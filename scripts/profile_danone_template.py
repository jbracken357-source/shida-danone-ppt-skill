#!/usr/bin/env python
"""Profile a real Danone PowerPoint template into a reusable JSON manifest."""

from __future__ import annotations

import argparse
import json
import logging
import re
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
from xml.etree import ElementTree as ET


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

EMU_PER_IN = 914400


def natural_key(name: str) -> tuple[str, int]:
    match = re.search(r"(\d+)", name)
    return (re.sub(r"\d+", "", name), int(match.group(1)) if match else 0)


def pptx_parts(names: list[str], folder: str, stem: str) -> list[str]:
    pattern = re.compile(rf"ppt/{folder}/{stem}\d+\.xml$")
    return sorted((name for name in names if pattern.match(name)), key=natural_key)


def rgb_value(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    srgb = node.find(".//a:srgbClr", NS)
    if srgb is not None:
        return srgb.attrib.get("val")
    sys = node.find(".//a:sysClr", NS)
    if sys is not None:
        return sys.attrib.get("lastClr")
    scheme = node.find(".//a:schemeClr", NS)
    if scheme is not None:
        return scheme.attrib.get("val")
    return None


def theme_info(xml: bytes, theme_id: str) -> dict:
    root = ET.fromstring(xml)
    clr_scheme = root.find(".//a:clrScheme", NS)
    colors = {}
    if clr_scheme is not None:
      for child in list(clr_scheme):
          colors[child.tag.split("}")[-1]] = rgb_value(child)

    major = root.find(".//a:fontScheme/a:majorFont/a:latin", NS)
    minor = root.find(".//a:fontScheme/a:minorFont/a:latin", NS)
    return {
        "id": theme_id,
        "name": root.attrib.get("name", ""),
        "fonts": {
            "major_latin": major.attrib.get("typeface") if major is not None else "",
            "minor_latin": minor.attrib.get("typeface") if minor is not None else "",
        },
        "colors": colors,
    }


def placeholder_info(sp: ET.Element) -> dict | None:
    ph = sp.find("p:nvSpPr/p:nvPr/p:ph", NS)
    if ph is None:
        return None

    name_el = sp.find("p:nvSpPr/p:cNvPr", NS)
    off = sp.find(".//a:xfrm/a:off", NS)
    ext = sp.find(".//a:xfrm/a:ext", NS)
    position = None
    if off is not None and ext is not None:
        position = {
            "x_in": round(int(off.attrib.get("x", "0")) / EMU_PER_IN, 3),
            "y_in": round(int(off.attrib.get("y", "0")) / EMU_PER_IN, 3),
            "w_in": round(int(ext.attrib.get("cx", "0")) / EMU_PER_IN, 3),
            "h_in": round(int(ext.attrib.get("cy", "0")) / EMU_PER_IN, 3),
        }

    return {
        "name": name_el.attrib.get("name", "") if name_el is not None else "",
        "type": ph.attrib.get("type", "body"),
        "idx": ph.attrib.get("idx", ""),
        "position": position,
    }


def infer_layout_family(name: str, placeholders: list[dict]) -> str:
    lowered = name.lower()
    if "opening" in lowered:
        return "opening-cover"
    if "closing" in lowered:
        return "closing-cover"
    if "contents" in lowered or "agenda" in lowered:
        return "contents"
    if "three column" in lowered:
        return "three-column"
    if "two content" in lowered:
        return "two-content"
    if "four content" in lowered:
        return "four-content"
    if "full image" in lowered:
        return "full-image"
    if "large image" in lowered or "image land" in lowered or "image port" in lowered:
        return "image-content"
    if "chart" in lowered:
        return "chart"
    if "table" in lowered:
        return "table"
    if "big text" in lowered:
        return "big-message"
    if "title only" in lowered:
        return "title-only"
    if any(ph["type"] == "pic" for ph in placeholders):
        return "image-content"
    return "content"


def layout_info(xml: bytes, layout_id: str) -> dict:
    root = ET.fromstring(xml)
    c_sld = root.find("p:cSld", NS)
    name = c_sld.attrib.get("name", "") if c_sld is not None else ""
    placeholders = []
    for sp in root.findall(".//p:sp", NS):
        ph = placeholder_info(sp)
        if ph is not None:
            placeholders.append(ph)

    return {
        "id": layout_id,
        "name": name or layout_id,
        "family": infer_layout_family(name, placeholders),
        "placeholders": placeholders,
    }


def profile_template(pptx_path: str | Path) -> dict:
    pptx_path = Path(pptx_path)
    with zipfile.ZipFile(pptx_path) as zf:
        names = zf.namelist()
        slides = pptx_parts(names, "slides", "slide")
        layouts = pptx_parts(names, "slideLayouts", "slideLayout")
        masters = pptx_parts(names, "slideMasters", "slideMaster")
        themes = pptx_parts(names, "theme", "theme")
        media = sorted(name for name in names if name.startswith("ppt/media/"))

        presentation = ET.fromstring(zf.read("ppt/presentation.xml"))
        slide_size = presentation.find("p:sldSz", NS)
        width_emu = int(slide_size.attrib["cx"])
        height_emu = int(slide_size.attrib["cy"])

        theme_manifest = [
            theme_info(zf.read(theme), Path(theme).stem)
            for theme in themes
        ]
        layout_manifest = [
            layout_info(zf.read(layout), Path(layout).stem)
            for layout in layouts
        ]

    return {
        "source": {
            "file": pptx_path.name,
            "relative_path": str(pptx_path.as_posix()),
        },
        "slide_size": {
            "width_emu": width_emu,
            "height_emu": height_emu,
            "width_in": round(width_emu / EMU_PER_IN, 3),
            "height_in": round(height_emu / EMU_PER_IN, 3),
        },
        "counts": {
            "slides": len(slides),
            "layouts": len(layouts),
            "masters": len(masters),
            "themes": len(themes),
            "media": len(media),
        },
        "themes": theme_manifest,
        "layouts": layout_manifest,
        "media_extensions": sorted({Path(item).suffix.lower() for item in media}),
    }


def write_manifest(manifest: dict, out_path: str | Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a Danone PPTX template into JSON.")
    parser.add_argument("template", help="Path to a .pptx template/sample deck")
    parser.add_argument("--out", default="templates/danone-template-manifest.json", help="Output JSON path")
    args = parser.parse_args()

    manifest = profile_template(args.template)
    write_manifest(manifest, args.out)
    logging.info("Wrote %s (%d layouts, %d themes)", args.out, manifest["counts"]["layouts"], manifest["counts"]["themes"])


if __name__ == "__main__":
    main()
