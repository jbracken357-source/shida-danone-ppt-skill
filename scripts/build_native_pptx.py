#!/usr/bin/env python
"""Build editable Danone PPTX decks by cloning real template sample slides.

This deliberately avoids HTML-to-PPTX conversion. It keeps the Danone template
package, clones real sample slide XML parts, and replaces editable text runs.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import logging
import mimetypes
import re
import shutil
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
from typing import NamedTuple
from xml.etree import ElementTree as ET


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}

SLIDE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
SLIDE_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
TEMPLATE_CHROME_PLACEHOLDER_TYPES = {"sldNum", "dt", "ftr"}

for prefix, uri in NS.items():
    if prefix not in {"rel", "ct"}:
        ET.register_namespace(prefix, uri)
ET.register_namespace("", NS["ct"])


class SampleSlide(NamedTuple):
    slide_number: int
    slide_part: str
    rels_part: str
    layout_name: str


def natural_key(value: str) -> tuple[str, int]:
    match = re.search(r"(\d+)", value)
    return (re.sub(r"\d+", "", value), int(match.group(1)) if match else 0)


def normalize_part(base_dir: str, target: str) -> str:
    parts: list[str] = []
    for part in f"{base_dir}/{target}".split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def relationship_map(root: ET.Element) -> dict[str, str]:
    return {rel.attrib["Id"]: rel.attrib["Target"] for rel in root}


def layout_name_for_slide(zf: zipfile.ZipFile, slide_part: str) -> str:
    slide_name = Path(slide_part).name
    rels_part = f"ppt/slides/_rels/{slide_name}.rels"
    rels = ET.fromstring(zf.read(rels_part))
    layout_target = None
    for rel in rels:
        if rel.attrib["Type"].endswith("/slideLayout"):
            layout_target = rel.attrib["Target"]
            break
    if layout_target is None:
        return ""

    layout_part = normalize_part("ppt/slides", layout_target)
    layout = ET.fromstring(zf.read(layout_part))
    c_sld = layout.find("p:cSld", NS)
    return c_sld.attrib.get("name", "") if c_sld is not None else ""


def discover_sample_slides(template_path: str | Path) -> list[SampleSlide]:
    template_path = Path(template_path)
    with zipfile.ZipFile(template_path) as zf:
        presentation = ET.fromstring(zf.read("ppt/presentation.xml"))
        presentation_rels = ET.fromstring(zf.read("ppt/_rels/presentation.xml.rels"))
        rels = relationship_map(presentation_rels)
        samples = []
        for index, sld_id in enumerate(presentation.find("p:sldIdLst", NS), start=1):
            rid = sld_id.attrib[f"{{{NS['r']}}}id"]
            slide_part = normalize_part("ppt", rels[rid])
            samples.append(
                SampleSlide(
                    slide_number=index,
                    slide_part=slide_part,
                    rels_part=f"ppt/slides/_rels/{Path(slide_part).name}.rels",
                    layout_name=layout_name_for_slide(zf, slide_part),
                )
            )
    return samples


def resolve_source_slide(intent: str, layout_map: dict, samples: list[SampleSlide]) -> SampleSlide:
    intents = layout_map.get("intents", {})
    if intent not in intents:
        raise ValueError(f"Unknown intent: {intent}")

    candidates = [
        intents[intent]["preferred_layout"],
        *intents[intent].get("fallback_layouts", []),
    ]
    by_layout = {}
    for sample in samples:
        by_layout.setdefault(sample.layout_name, sample)

    for layout in candidates:
        if layout in by_layout:
            return by_layout[layout]
    raise ValueError(f"No sample slide found for intent {intent}; tried: {', '.join(candidates)}")


def validate_plan(layout_map: dict, plan: list[dict]) -> None:
    intents = layout_map.get("intents", {})
    for index, spec in enumerate(plan, start=1):
        intent = spec.get("intent")
        if intent not in intents:
            raise ValueError(f"Slide {index}: unknown intent: {intent}")

        content = spec.get("content", {})
        missing = [key for key in intents[intent].get("required_content", []) if key not in content]
        if missing:
            raise ValueError(
                f"Slide {index} ({intent}) missing required content: {', '.join(missing)}"
            )

        # Validate image paths for image-led intents
        if intent in {"image-content", "section-photo"}:
            image = content.get("image")
            if image and not Path(image).exists():
                raise FileNotFoundError(
                    f"Slide {index} ({intent}): image file not found: {image}"
                )


def content_values(intent: str, content: dict) -> list[str]:
    orders = {
        "opening-cover": ["title", "subtitle_or_date", "subtitle", "date"],
        "contents": ["title", "agenda_items"],
        "section-photo": ["title", "body"],
        "big-message": ["headline", "supporting_text"],
        "two-column": ["title", "left_content", "right_content"],
        "three-column": ["title", "column_1", "column_2", "column_3"],
        "scenario-detail": ["title", "column_1", "column_2", "column_3"],
        "image-content": ["title", "body"],
        "chart-or-table": ["title", "chart_or_table", "insight"],
        "closing": ["title"],
    }
    values = []
    seen = set()
    for key in orders.get(intent, []):
        if key in content:
            value = content[key]
            if isinstance(value, list):
                value = "\n".join(str(item) for item in value)
            values.append(str(value))
            seen.add(key)
    for key, value in content.items():
        if key in seen or key == "image":
            continue
        if isinstance(value, list):
            value = "\n".join(str(item) for item in value)
        values.append(str(value))
    return values


def shape_key(sp: ET.Element) -> tuple[str, str]:
    ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
    if ph is None:
        return ("", "")
    return (ph.attrib.get("type", ""), ph.attrib.get("idx", ""))


# ─── Image Replacement Engine ───────────────────────────────────────────────

def _mime_type_for(path: Path) -> str:
    """Guess MIME type from file extension."""
    mime, _ = mimetypes.guess_type(str(path))
    if mime:
        return mime
    ext = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }.get(ext, "image/png")


def _media_ext_for(mime: str) -> str:
    """Map MIME type to file extension for ppt/media/ naming."""
    return {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/svg+xml": ".svg",
        "image/webp": ".webp",
    }.get(mime, ".png")


def _content_type_for(mime: str) -> str:
    """Map MIME type to [Content_Types].xml ContentType."""
    return {
        "image/png": "image/png",
        "image/jpeg": "image/jpeg",
        "image/gif": "image/gif",
        "image/svg+xml": "image/svg+xml",
        "image/webp": "image/webp",
    }.get(mime, "image/png")


def _next_image_rid(rels_root: ET.Element) -> str:
    """Generate next available rId for image relationships."""
    existing = set()
    for rel in rels_root:
        rid = rel.attrib.get("Id", "")
        if rid.startswith("rId"):
            try:
                existing.add(int(rid[3:]))
            except ValueError:
                pass
    next_num = max(existing, default=0) + 1
    return f"rId{next_num}"


def _next_media_name(parts: dict[str, bytes], mime: str) -> str:
    """Generate unique media filename in ppt/media/."""
    ext = _media_ext_for(mime)
    existing = {
        Path(n).name
        for n in parts
        if n.startswith("ppt/media/")
    }
    for i in range(1, 200):
        name = f"image{i}{ext}"
        if name not in existing:
            return name
    # Fallback: use hash
    h = hashlib.md5(str(len(parts)).encode()).hexdigest()[:8]
    return f"image_{h}{ext}"


def copy_image_to_media(
    image_path: Path,
    parts: dict[str, bytes],
    content_types: ET.Element,
    slide_rels: ET.Element,
) -> str:
    """Copy an image into the PPTX package and create a relationship.

    Returns the rId that can be used to reference this image in slide XML.
    """
    mime = _mime_type_for(image_path)
    media_name = _next_media_name(parts, mime)
    media_part = f"ppt/media/{media_name}"

    # Read and store image data
    image_data = image_path.read_bytes()
    parts[media_part] = image_data

    # Register content type override
    ct = _content_type_for(mime)
    # Check if this extension is already registered
    registered = False
    for default in content_types.findall("ct:Default", NS):
        if default.attrib.get("Extension") == media_name.lstrip(".").split(".")[0]:
            registered = True
            break
    if not registered:
        ET.SubElement(
            content_types,
            f"{{{NS['ct']}}}Default",
            {"Extension": media_name.lstrip("."), "ContentType": ct},
        )

    # Create relationship in slide rels
    rid = _next_image_rid(slide_rels)
    ET.SubElement(
        slide_rels,
        f"{{{NS['rel']}}}Relationship",
        {"Id": rid, "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", "Target": f"../media/{media_name}"},
    )

    return rid


def replace_placeholder_image(
    slide_xml: ET.Element,
    image_path: Path,
    parts: dict[str, bytes],
    content_types: ET.Element,
    slide_rels: ET.Element,
) -> bool:
    """Replace the first <p:pic> placeholder in the slide with a custom image.

    Returns True if a placeholder was found and replaced, False otherwise.
    """
    # Find picture placeholders in the slide
    for pic in slide_xml.findall(".//p:pic", NS):
        nv_pic = pic.find("p:nvPicPr", NS)
        if nv_pic is None:
            continue
        ph = nv_pic.find("p:nvPr/p:ph", NS)
        if ph is None:
            continue
        # This is a template picture placeholder
        blip_fill = pic.find("p:blipFill", NS)
        if blip_fill is None:
            continue
        blip = blip_fill.find("a:blip", NS)
        if blip is None:
            continue

        # Copy image and get new rId
        rid = copy_image_to_media(image_path, parts, content_types, slide_rels)

        # Update the blip to point to the new image
        blip.attrib[f"{{{NS['r']}}}embed"] = rid

        logging.info("Replaced image placeholder with %s (rid=%s)", image_path.name, rid)
        return True

    return False


def set_shape_text(sp: ET.Element, value: str) -> None:
    """Replace text in a shape, splitting newlines into separate paragraphs."""
    tx_body = sp.find(".//p:txBody", NS)
    if tx_body is None:
        return

    paragraphs = list(tx_body.findall("a:p", NS))
    if not paragraphs:
        return

    # Use the first paragraph as a template for properties
    template_p = paragraphs[0]
    pPr = template_p.find("a:pPr", NS)

    # Remove all existing paragraphs
    for p in paragraphs:
        tx_body.remove(p)

    lines = value.split("\n") if value else [""]

    for line in lines:
        new_p = ET.SubElement(tx_body, f"{{{NS['a']}}}p")
        if pPr is not None:
            new_p.append(copy.deepcopy(pPr))
        if line:
            r = ET.SubElement(new_p, f"{{{NS['a']}}}r")
            # Always add explicit rPr with cap="none" to override layout/master-level cap="all"
            template_r = template_p.find("a:r", NS)
            if template_r is not None:
                template_rPr = template_r.find("a:rPr", NS)
                if template_rPr is not None:
                    rPr = copy.deepcopy(template_rPr)
                    rPr.attrib["cap"] = "none"
                    r.append(rPr)
                else:
                    rPr = ET.SubElement(r, f"{{{NS['a']}}}rPr")
                    rPr.attrib["cap"] = "none"
            else:
                rPr = ET.SubElement(r, f"{{{NS['a']}}}rPr")
                rPr.attrib["cap"] = "none"
            t = ET.SubElement(r, f"{{{NS['a']}}}t")
            t.text = line


def cleanup_unmapped_sample_content(root: ET.Element, mapped: dict[int, str], content: dict, intent: str) -> None:
    sp_tree = root.find("p:cSld/p:spTree", NS)
    if sp_tree is None:
        return

    text_shapes = [sp for sp in root.findall(".//p:sp", NS) if sp.findall(".//a:t", NS)]
    for index, sp in enumerate(text_shapes):
        if index in mapped:
            continue
        ph_type, ph_idx = shape_key(sp)
        if ph_type in TEMPLATE_CHROME_PLACEHOLDER_TYPES:
            continue
        if ph_type == "body" and ph_idx:
            # Remove unmapped body placeholders so they don't leak sample text
            if sp in list(sp_tree):
                sp_tree.remove(sp)
            continue
        if ph_idx:
            continue
        if sp in list(sp_tree):
            sp_tree.remove(sp)

    if "image" not in content:
        for pic in list(sp_tree.findall("p:pic", NS)):
            sp_tree.remove(pic)

    for connector in list(sp_tree.findall("p:cxnSp", NS)):
        sp_tree.remove(connector)

    if intent not in {"opening-cover", "closing", "scenario-detail"}:
        for sp in list(sp_tree.findall("p:sp", NS)):
            ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
            texts = [node for node in sp.findall(".//a:t", NS) if node.text and node.text.strip()]
            if ph is None and not texts:
                sp_tree.remove(sp)


def map_content_to_shapes(intent: str, content: dict, shapes: list[ET.Element]) -> dict[int, str]:
    by_idx: dict[str, int] = {}
    title_shape = None
    for index, sp in enumerate(shapes):
        ph_type, ph_idx = shape_key(sp)
        if ph_type == "sldNum":
            continue
        if ph_idx:
            by_idx.setdefault(ph_idx, index)
        if ph_type == "title":
            title_shape = index

    mapped: dict[int, str] = {}

    def put(index: int | None, key: str) -> None:
        if index is not None and key in content:
            value = content[key]
            if isinstance(value, list):
                value = "\n".join(str(item) for item in value)
            mapped[index] = str(value)

    def pick(*keys: str) -> int | None:
        for k in keys:
            if k in by_idx:
                return by_idx[k]
        return None

    if intent == "opening-cover":
        put(title_shape, "title")
        put(by_idx.get("10"), "subtitle_or_date")
    elif intent == "closing":
        put(title_shape, "title")
    elif intent == "two-column":
        put(by_idx.get("13") if "13" in by_idx else title_shape, "title")
        put(by_idx.get("1"), "left_content")
        put(by_idx.get("2") if "2" in by_idx else by_idx.get("14"), "right_content")
    elif intent == "chart-or-table":
        put(by_idx.get("13") if "13" in by_idx else title_shape, "title")
        put(by_idx.get("1"), "chart_or_table")
        put(by_idx.get("2") if "2" in by_idx else by_idx.get("14"), "insight")
    elif intent == "three-column":
        put(pick("13") if pick("13") is not None else title_shape, "title")
        put(pick("21", "24", "1"), "column_1")
        put(pick("22", "25", "2"), "column_2")
        put(pick("23", "26", "14", "3"), "column_3")
    elif intent == "scenario-detail":
        # Scenario pages: title + 3 columns (pain points, data, products)
        put(pick("13") if pick("13") is not None else title_shape, "title")
        put(pick("21", "24", "1"), "column_1")
        put(pick("22", "25", "2"), "column_2")
        put(pick("23", "26", "14", "3"), "column_3")
    elif intent == "big-message":
        put(by_idx.get("15") if "15" in by_idx else title_shape, "headline")
        put(by_idx.get("13"), "supporting_text")
    elif intent in {"image-content", "section-photo"}:
        put(pick("14", "13") if pick("14", "13") is not None else title_shape, "title")
        put(pick("1"), "body")
    elif intent == "contents":
        put(pick("13") if pick("13") is not None else title_shape, "title")
        # Agenda items: distribute across available body placeholders
        agenda_idx = [k for k in ("16", "22", "23", "24", "25") if k in by_idx]
        if not agenda_idx:
            agenda_idx = [k for k in ("1", "2") if k in by_idx]
        if "agenda_items" in content and agenda_idx:
            items = content["agenda_items"]
            if isinstance(items, list):
                items = [str(i) for i in items]
            else:
                items = str(items).split("\n")
            for i, idx_key in enumerate(agenda_idx):
                if i < len(items):
                    mapped[by_idx[idx_key]] = items[i]

    if not mapped:
        for index, value in enumerate(content_values(intent, content)):
            if index < len(shapes):
                mapped[index] = value

    # Runtime validation: warn if expected mappings are missing
    expected_keys = {
        "opening-cover": ["title"],
        "closing": ["title"],
        "big-message": ["headline"],
        "contents": ["title"],
        "three-column": ["title", "column_1", "column_2", "column_3"],
        "scenario-detail": ["title", "column_1", "column_2", "column_3"],
        "image-content": ["title", "body"],
        "section-photo": ["title", "body"],
    }
    for key in expected_keys.get(intent, []):
        if key not in content:
            continue
        found = any(v == str(content[key]) for v in mapped.values())
        if not found:
            logging.warning("Intent '%s': content key '%s' was not mapped to any shape", intent, key)

    return mapped


def strip_text_transforms(root: ET.Element) -> None:
    """Remove forced ALL CAPS text transforms from a slide."""
    for elem in root.iter():
        if elem.attrib.get("cap") == "all":
            del elem.attrib["cap"]


def strip_caps_from_layouts(parts: dict[str, bytes]) -> None:
    """Neutralise cap='all' in all slide layout XML so it never forces uppercase."""
    for name in list(parts.keys()):
        if name.startswith("ppt/slideLayouts/slideLayout") and name.endswith(".xml"):
            root = ET.fromstring(parts[name])
            for elem in root.iter():
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag in {"defRPr", "rPr"} and elem.attrib.get("cap") == "all":
                    elem.attrib["cap"] = "none"
            parts[name] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_slide_number(root: ET.Element, slide_index: int) -> None:
    """Update sldNum placeholder to show output slide number."""
    for sp in root.findall(".//p:sp", NS):
        ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
        if ph is not None and ph.attrib.get("type") == "sldNum":
            tx_body = sp.find(".//p:txBody", NS)
            if tx_body is not None:
                for t in tx_body.findall(".//a:t", NS):
                    t.text = str(slide_index)


def replace_text_runs(slide_xml: bytes, values: list[str], intent: str = "", content: dict | None = None, slide_index: int = 0) -> bytes:
    root = ET.fromstring(slide_xml)
    shapes = [sp for sp in root.findall(".//p:sp", NS) if sp.findall(".//a:t", NS)]
    mapped = map_content_to_shapes(intent, content or {}, shapes) if content is not None else {}
    if mapped:
        for index, sp in enumerate(shapes):
            ph_type, _ = shape_key(sp)
            if ph_type in TEMPLATE_CHROME_PLACEHOLDER_TYPES:
                continue
            set_shape_text(sp, mapped.get(index, ""))
        cleanup_unmapped_sample_content(root, mapped, content or {}, intent)
    else:
        text_nodes = [node for node in root.findall(".//a:t", NS) if node.text and node.text.strip()]
        for node, value in zip(text_nodes, values):
            node.text = value
    update_slide_number(root, slide_index)
    strip_text_transforms(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def is_slide_part(name: str) -> bool:
    return bool(re.match(r"ppt/slides/slide\d+\.xml$", name))


def is_slide_rels_part(name: str) -> bool:
    return bool(re.match(r"ppt/slides/_rels/slide\d+\.xml\.rels$", name))


def remove_slide_relationships(root: ET.Element) -> None:
    for rel in list(root):
        if rel.attrib.get("Type") == SLIDE_REL_TYPE:
            root.remove(rel)


def cleanup_unused_image_rels(slide_xml: bytes, rels_xml: bytes) -> bytes:
    """Remove image relationships from slide rels that are no longer referenced in slide XML."""
    root = ET.fromstring(rels_xml)
    # Find all referenced image rIds in slide XML
    slide_root = ET.fromstring(slide_xml)
    used_rids = set()
    for blip in slide_root.findall(".//a:blip", NS):
        embed = blip.attrib.get(f"{{{NS['r']}}}embed")
        if embed:
            used_rids.add(embed)
    # Also check for video/audio references
    for elem in slide_root.iter():
        for attr in elem.attrib:
            if attr.endswith("}embed") or attr.endswith("}link"):
                used_rids.add(elem.attrib[attr])
    # Remove unused image relationships
    IMAGE_REL_TYPES = {
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/video",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio",
    }
    for rel in list(root):
        if rel.attrib.get("Type") in IMAGE_REL_TYPES and rel.attrib.get("Id") not in used_rids:
            root.remove(rel)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def remove_slide_content_overrides(root: ET.Element) -> None:
    for override in list(root):
        if (
            override.tag.endswith("Override")
            and override.attrib.get("PartName", "").startswith("/ppt/slides/slide")
        ):
            root.remove(override)


def collect_used_resources(parts: dict[str, bytes]) -> set[str]:
    """Trace all referenced media, layouts, masters, and themes from slide rels."""
    used: set[str] = set()

    # Collect from slide rels
    for name, data in parts.items():
        if not name.startswith("ppt/slides/_rels/") or not name.endswith(".rels"):
            continue
        root = ET.fromstring(data)
        for rel in root:
            target = rel.attrib.get("Target", "")
            rel_type = rel.attrib.get("Type", "")
            # Normalize target path
            base = name.rsplit("/_rels/", 1)[0]
            resolved = normalize_part(base, target)
            used.add(resolved)

    # Collect from layout rels (follow used layouts)
    layout_rels = {}
    for name, data in parts.items():
        if name.startswith("ppt/slideLayouts/_rels/") and name.endswith(".rels"):
            layout_name = name.replace("ppt/slideLayouts/_rels/", "").replace(".rels", "")
            layout_rels[layout_name] = data

    for resolved in list(used):
        if resolved.startswith("ppt/slideLayouts/") and resolved.endswith(".xml"):
            layout_name = Path(resolved).name
            rels_name = f"ppt/slideLayouts/_rels/{layout_name}.rels"
            if rels_name in parts:
                used.add(rels_name)
                root = ET.fromstring(parts[rels_name])
                for rel in root:
                    target = rel.attrib.get("Target", "")
                    resolved2 = normalize_part("ppt/slideLayouts", target)
                    used.add(resolved2)

    # Collect from master rels (follow used masters)
    for resolved in list(used):
        if resolved.startswith("ppt/slideMasters/") and resolved.endswith(".xml"):
            master_name = Path(resolved).name
            rels_name = f"ppt/slideMasters/_rels/{master_name}.rels"
            if rels_name in parts:
                used.add(rels_name)
                root = ET.fromstring(parts[rels_name])
                for rel in root:
                    target = rel.attrib.get("Target", "")
                    resolved2 = normalize_part("ppt/slideMasters", target)
                    used.add(resolved2)

    return used


def cleanup_unused_resources(parts: dict[str, bytes]) -> dict[str, bytes]:
    """Remove unreferenced media, layouts, masters, and themes to reduce file size."""
    used = collect_used_resources(parts)

    # Always keep core files
    core_files = {
        "ppt/presentation.xml",
        "ppt/_rels/presentation.xml.rels",
        "[Content_Types].xml",
        "_rels/.rels",
    }
    used.update(core_files)

    cleaned: dict[str, bytes] = {}
    removed_count = 0
    for name, data in parts.items():
        if name in used or name.startswith("ppt/slides/") or name.startswith("ppt/slides/_rels/"):
            cleaned[name] = data
        elif any(name.startswith(prefix) for prefix in [
            "ppt/media/", "ppt/slideLayouts/", "ppt/slideMasters/",
            "ppt/theme/", "ppt/notesSlides/", "ppt/notesMasters/",
            "ppt/handoutMasters/", "ppt/presProps.xml", "ppt/tableStyles.xml",
            "ppt/viewProps.xml", "docProps/"
        ]):
            removed_count += 1
            continue
        else:
            cleaned[name] = data

    if removed_count > 0:
        logging.info("Removed %d unreferenced resource files", removed_count)
    return cleaned


def build_presentation(
    template_path: str | Path,
    layout_map_path: str | Path,
    plan: list[dict],
    out_path: str | Path,
) -> None:
    template_path = Path(template_path)
    layout_map_path = Path(layout_map_path)
    out_path = Path(out_path)
    layout_map = json.loads(layout_map_path.read_text(encoding="utf-8"))
    validate_plan(layout_map, plan)
    samples = discover_sample_slides(template_path)

    with zipfile.ZipFile(template_path) as zf:
        parts = {
            info.filename: zf.read(info.filename)
            for info in zf.infolist()
            if not is_slide_part(info.filename) and not is_slide_rels_part(info.filename)
        }
        strip_caps_from_layouts(parts)

        presentation = ET.fromstring(parts["ppt/presentation.xml"])
        presentation_rels = ET.fromstring(parts["ppt/_rels/presentation.xml.rels"])
        content_types = ET.fromstring(parts["[Content_Types].xml"])

        sld_id_list = presentation.find("p:sldIdLst", NS)
        if sld_id_list is None:
            sld_id_list = ET.SubElement(presentation, f"{{{NS['p']}}}sldIdLst")
        for child in list(sld_id_list):
            sld_id_list.remove(child)
        remove_slide_relationships(presentation_rels)
        remove_slide_content_overrides(content_types)

        for index, spec in enumerate(plan, start=1):
            intent = spec["intent"]
            source = resolve_source_slide(intent, layout_map, samples)
            values = content_values(intent, spec.get("content", {}))
            content = spec.get("content", {})

            slide_part = f"ppt/slides/slide{index}.xml"
            slide_rels_name = f"ppt/slides/_rels/slide{index}.xml.rels"

            # Replace text content
            parts[slide_part] = replace_text_runs(
                zf.read(source.slide_part), values, intent=intent, content=content, slide_index=index
            )

            # Parse slide rels for image replacement
            raw_rels = zf.read(source.rels_part)
            slide_rels_root = ET.fromstring(raw_rels)
            slide_xml_root = ET.fromstring(parts[slide_part])

            # Handle image replacement for image-led intents
            image_path = content.get("image")
            if image_path and intent in {"image-content", "section-photo"}:
                img = Path(image_path)
                if img.exists():
                    replaced = replace_placeholder_image(
                        slide_xml_root, img, parts, content_types, slide_rels_root
                    )
                    if not replaced:
                        logging.warning(
                            "Slide %d (%s): no picture placeholder found for image %s",
                            index, intent, image_path,
                        )
                else:
                    logging.warning("Slide %d (%s): image file not found: %s", index, intent, image_path)

            # Serialize updated XML
            parts[slide_part] = ET.tostring(slide_xml_root, encoding="utf-8", xml_declaration=True)
            parts[slide_rels_name] = cleanup_unused_image_rels(parts[slide_part],
                ET.tostring(slide_rels_root, encoding="utf-8", xml_declaration=True)
            )

            rid = f"rIdNative{index}"
            ET.SubElement(
                sld_id_list,
                f"{{{NS['p']}}}sldId",
                {"id": str(255 + index), f"{{{NS['r']}}}id": rid},
            )
            ET.SubElement(
                presentation_rels,
                f"{{{NS['rel']}}}Relationship",
                {"Id": rid, "Type": SLIDE_REL_TYPE, "Target": f"slides/slide{index}.xml"},
            )
            ET.SubElement(
                content_types,
                f"{{{NS['ct']}}}Override",
                {"PartName": f"/ppt/slides/slide{index}.xml", "ContentType": SLIDE_CONTENT_TYPE},
            )

        parts["ppt/presentation.xml"] = ET.tostring(
            presentation, encoding="utf-8", xml_declaration=True
        )
        parts["ppt/_rels/presentation.xml.rels"] = ET.tostring(
            presentation_rels, encoding="utf-8", xml_declaration=True
        )
        parts["[Content_Types].xml"] = ET.tostring(
            content_types, encoding="utf-8", xml_declaration=True
        )

    # Cleanup unreferenced resources to reduce file size
    parts = cleanup_unused_resources(parts)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as out:
        for name in sorted(parts.keys(), key=natural_key):
            out.writestr(name, parts[name])


def load_plan(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("slides", [])
    if not isinstance(data, list):
        raise ValueError("Plan must be a list or an object with a 'slides' list")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a native editable Danone PPTX from a JSON slide plan.")
    parser.add_argument("--template", default="Danone Real Templates/Standard Danone Template.pptx")
    parser.add_argument("--layout-map", default="templates/layout-map.json")
    parser.add_argument("--plan", required=True, help="JSON file: list of slides or { slides: [...] }")
    parser.add_argument("--out", required=True, help="Output .pptx path")
    args = parser.parse_args()

    plan = load_plan(args.plan)
    build_presentation(args.template, args.layout_map, plan, args.out)
    logging.info("Wrote %s (%d native slides)", args.out, len(plan))


if __name__ == "__main__":
    main()
