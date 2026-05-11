#!/usr/bin/env python
"""Build editable Danone PPTX decks by cloning real template sample slides.

This deliberately avoids HTML-to-PPTX conversion. It keeps the Danone template
package, clones real sample slide XML parts, and replaces editable text runs.
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import re
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
UNSUPPORTED_NATIVE_IMAGE_INTENTS = {"image-content", "section-photo"}
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
        if intent in UNSUPPORTED_NATIVE_IMAGE_INTENTS:
            raise NotImplementedError(
                f"Slide {index}: native image replacement is not implemented for "
                f"'{intent}'. Use the HTML fallback path for image-led pages."
            )

        content = spec.get("content", {})
        missing = [key for key in intents[intent].get("required_content", []) if key not in content]
        if missing:
            raise ValueError(
                f"Slide {index} ({intent}) missing required content: {', '.join(missing)}"
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
        put(pick("1", "21", "24"), "column_1")
        put(pick("2", "22", "25"), "column_2")
        put(pick("14", "3", "23", "26"), "column_3")
    elif intent == "scenario-detail":
        # Scenario pages: title + 3 columns (pain points, data, products)
        put(pick("13") if pick("13") is not None else title_shape, "title")
        put(pick("1", "21", "24"), "column_1")
        put(pick("2", "22", "25"), "column_2")
        put(pick("14", "3", "23", "26"), "column_3")
    elif intent == "big-message":
        put(by_idx.get("15") if "15" in by_idx else title_shape, "headline")
        put(by_idx.get("13"), "supporting_text")
    elif intent in {"image-content", "section-photo"}:
        put(by_idx.get("14") if "14" in by_idx else title_shape, "title")
        put(by_idx.get("1"), "body")
    elif intent == "contents":
        put(by_idx.get("13") if "13" in by_idx else title_shape, "title")
        put(by_idx.get("1") if "1" in by_idx else by_idx.get("2"), "agenda_items")

    if not mapped:
        for index, value in enumerate(content_values(intent, content)):
            if index < len(shapes):
                mapped[index] = value
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


def replace_text_runs(slide_xml: bytes, values: list[str], intent: str = "", content: dict | None = None) -> bytes:
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


def remove_slide_content_overrides(root: ET.Element) -> None:
    for override in list(root):
        if (
            override.tag.endswith("Override")
            and override.attrib.get("PartName", "").startswith("/ppt/slides/slide")
        ):
            root.remove(override)


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

            slide_part = f"ppt/slides/slide{index}.xml"
            slide_rels = f"ppt/slides/_rels/slide{index}.xml.rels"
            parts[slide_part] = replace_text_runs(
                zf.read(source.slide_part), values, intent=intent, content=spec.get("content", {})
            )
            parts[slide_rels] = zf.read(source.rels_part)

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
