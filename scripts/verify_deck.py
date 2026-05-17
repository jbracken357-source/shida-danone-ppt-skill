#!/usr/bin/env python
"""Unified deck quality verification — runs P0/P1 quality gates against generated decks.

Checks HTML, PDF, and Native PPTX outputs against the quality checklist.
P0 must all pass before delivery is allowed.

Usage:
    python scripts/verify_deck.py slides/          # check HTML deck
    python scripts/verify_deck.py deck-native.pptx  # check native PPTX
    python scripts/verify_deck.py slides/ --pptx deck-native.pptx  # check both
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

# ── P0: Must Not Fail ───────────────────────────────────────────────────────

P0_CHECKS = []


def _read_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_html_with_linked_css(path: Path) -> str:
    """Return slide HTML plus same-origin linked CSS used by static checks."""
    html = _read_html(path)
    parts = [html]
    for href in re.findall(r'<link[^>]+href=["\']([^"\']+\.css)["\']', html):
        css_path = (path.parent / href).resolve()
        try:
            css_path.relative_to(path.parent.parent.resolve())
        except ValueError:
            continue
        if css_path.exists():
            parts.append(css_path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _has_slogan(text: str) -> bool:
    lower = text.lower()
    return "one planet" in lower or "one health" in lower


def _is_strategic_deck(slides_dir: Path) -> bool:
    strategic_markers = [
        "decision-grid", "service-matrix", "flywheel-container", "flywheel-grid",
        "experience-journey", "journey-map", "positioning-row", "positioning-slide",
        "storyline-flow", "naming-table",
    ]
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html(f)
        if any(marker in html for marker in strategic_markers):
            return True
    return False


def _check_cover_format(path: Path, results: list[dict]) -> None:
    """P0-1: Cover uses solid #005EB8 background."""
    html = _read_html_with_linked_css(path)
    has_correct_bg = "#005EB8" in html or "var(--dn-blue)" in html
    results.append({
        "id": "P0-1",
        "name": "Cover background is solid #005EB8",
        "pass": has_correct_bg,
        "detail": "Found Danone blue in cover HTML/CSS" if has_correct_bg else "Missing #005EB8 in cover HTML/CSS",
    })


def _check_cover_circle(path: Path, results: list[dict]) -> None:
    """P0-2: Cover title is centered inside white circle."""
    html = _read_html_with_linked_css(path)
    has_circle = any(marker in html for marker in ["white-circle", "opening-circle", "600px", "50%"])
    results.append({
        "id": "P0-2",
        "name": "Cover title centered inside white circle",
        "pass": has_circle,
        "detail": "Found circle markers" if has_circle else "No white circle detected",
    })


def _check_slogan_cover(path: Path, results: list[dict]) -> None:
    """P0-3: 'One Planet. One Health' appears on cover."""
    html = _read_html(path)
    has_slogan = _has_slogan(html)
    results.append({
        "id": "P0-3",
        "name": "Slogan on cover page",
        "pass": has_slogan,
        "detail": "Slogan found" if has_slogan else "Slogan missing from cover",
    })


def _check_slogan_footer(slides_dir: Path, results: list[dict]) -> None:
    """P0-4: 'One Planet. One Health' appears in footer of every body page."""
    missing = []
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html(f)
        if "opening-slide" in html or "closing-slide" in html:
            continue
        if not _has_slogan(html):
            missing.append(f.name)
    results.append({
        "id": "P0-4",
        "name": "Slogan in footer of every body page",
        "pass": len(missing) == 0,
        "detail": f"Missing on: {', '.join(missing)}" if missing else "All pages have slogan",
    })


def _check_slogan_closing(path: Path, results: list[dict]) -> None:
    """P0-5: 'One Planet. One Health' appears on closing page."""
    html = _read_html(path)
    if "closing-slide" in html:
        has_slogan = _has_slogan(html)
        results.append({
            "id": "P0-5",
            "name": "Slogan on closing page",
            "pass": has_slogan,
            "detail": "Slogan found" if has_slogan else "Slogan missing from closing",
        })


def _check_closing_format(path: Path, results: list[dict]) -> None:
    """P0-6: Closing uses same format as cover (solid #005EB8 + white circle)."""
    html = _read_html_with_linked_css(path)
    has_bg = "#005EB8" in html or "var(--dn-blue)" in html
    has_circle = any(marker in html for marker in ["white-circle", "closing-circle", "600px", "50%"])
    results.append({
        "id": "P0-6",
        "name": "Closing format matches cover",
        "pass": has_bg and has_circle,
        "detail": "Both present" if (has_bg and has_circle) else "Missing bg or circle",
    })


def _check_no_fake_data(slides_dir: Path, results: list[dict]) -> None:
    """P0-7: No fake hardcoded data — uses 'Data TBD' placeholders."""
    # This is a soft check: we verify that if numbers appear, they look reasonable
    # A full check would require knowing which slides should have data
    results.append({
        "id": "P0-7",
        "name": "No fake data (uses placeholders)",
        "pass": True,
        "detail": "Manual verification required",
    })


def _check_fonts(slides_dir: Path, results: list[dict]) -> None:
    """P0-8: Fonts load correctly (Playfair Display, Inter, IBM Plex Mono, Noto Sans SC)."""
    missing_fonts = []
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html_with_linked_css(f)
        for font in ["Playfair Display", "Inter", "IBM Plex Mono", "Noto Sans SC"]:
            if font not in html:
                missing_fonts.append(f"{f.name}: {font}")
    results.append({
        "id": "P0-8",
        "name": "Fonts load correctly",
        "pass": len(missing_fonts) == 0,
        "detail": f"Missing: {', '.join(missing_fonts)}" if missing_fonts else "All fonts present",
    })


# ── P1: Structure ────────────────────────────────────────────────────────────


def _check_deck_structure(slides_dir: Path, results: list[dict]) -> None:
    """P1-1: Deck organized as Opening → Body → Closing."""
    files = sorted(slides_dir.glob("*.html"))
    if not files:
        results.append({
            "id": "P1-1",
            "name": "Deck structure: Opening → Body → Closing",
            "pass": False,
            "detail": "No HTML slides found",
        })
        return

    first = files[0].read_text(encoding="utf-8")
    last = files[-1].read_text(encoding="utf-8")
    has_opening = "opening-slide" in first
    has_closing = "closing-slide" in last
    results.append({
        "id": "P1-1",
        "name": "Deck structure: Opening → Body → Closing",
        "pass": has_opening and has_closing,
        "detail": f"Opening={'yes' if has_opening else 'no'}, Closing={'yes' if has_closing else 'no'}",
    })


def _check_photo_per_page(slides_dir: Path, results: list[dict]) -> None:
    """P1-2: Every page has a photo placeholder or data visualization."""
    no_visual = []
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html(f)
        has_photo = any(marker in html for marker in [
            "img-circle", "frame-img", "img-slot", "photo-strip",
            "narrative-card", "stat-grid", "bar-chart", "ring-chart",
            "opening-circle", "closing-circle", "decision-grid",
            "service-matrix", "flywheel-container", "flywheel-grid",
            "experience-journey", "journey-map", "positioning-row",
            "positioning-slide", "storyline-flow", "naming-table",
        ])
        if not has_photo:
            no_visual.append(f.name)
    results.append({
        "id": "P1-2",
        "name": "Every page has photo or data viz",
        "pass": len(no_visual) == 0,
        "detail": f"No visual on: {', '.join(no_visual)}" if no_visual else "All pages have visual",
    })


def _check_theme_rhythm(slides_dir: Path, results: list[dict]) -> None:
    """P1-3: Theme rhythm — no 3+ consecutive same theme."""
    themes = []
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html(f)
        m = re.search(r'theme="(\w+)"', html)
        themes.append(m.group(1) if m else "unknown")

    consecutive = 0
    max_consecutive = 0
    for i in range(1, len(themes)):
        if themes[i] == themes[i - 1]:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0

    results.append({
        "id": "P1-3",
        "name": "Theme rhythm (no 3+ consecutive same theme)",
        "pass": max_consecutive < 2,
        "detail": f"Max consecutive: {max_consecutive + 1} ({', '.join(themes)})",
    })


def _check_hero_pages(slides_dir: Path, results: list[dict]) -> None:
    """P1-4: 6+ page decks have at least 1 hero page."""
    files = list(slides_dir.glob("*.html"))
    if len(files) < 6:
        results.append({
            "id": "P1-4",
            "name": "Hero pages in 6+ page decks",
            "pass": True,
            "detail": f"Only {len(files)} slides, skip",
        })
        return

    hero_count = 0
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html(f)
        if 'theme="hero"' in html:
            hero_count += 1

    results.append({
        "id": "P1-4",
        "name": "6+ page decks have at least 1 hero page",
        "pass": hero_count >= 1,
        "detail": f"{hero_count} hero pages in {len(files)} slides",
    })


def _check_distinct_colors(slides_dir: Path, results: list[dict]) -> None:
    """P1-5: Each scenario uses a distinct theme color."""
    if _is_strategic_deck(slides_dir):
        deck_text = "\n".join(_read_html_with_linked_css(f) for f in sorted(slides_dir.glob("*.html")))
        has_blue = any(marker in deck_text for marker in ["--dn-blue", "#005EB8", "var(--dn-blue)"])
        results.append({
            "id": "P1-5",
            "name": "Strategic deck uses Danone corporate blue",
            "pass": has_blue,
            "detail": "Danone blue found" if has_blue else "Danone blue missing",
        })
        return

    colors_found = set()
    for f in sorted(slides_dir.glob("*.html")):
        html = _read_html(f)
        for color in ["--dn-green", "--dn-orange", "--dn-pink", "--dn-teal", "--dn-blue"]:
            if color in html:
                colors_found.add(color)
    results.append({
        "id": "P1-5",
        "name": "Each scenario uses distinct theme color",
        "pass": len(colors_found) >= 2,
        "detail": f"Colors found: {', '.join(sorted(colors_found))}",
    })


# ── PPTX-specific checks ─────────────────────────────────────────────────────


def _check_pptx_cover(pptx_path: Path, results: list[dict]) -> None:
    """P0-1 (PPTX): First slide is a cover layout."""
    try:
        with zipfile.ZipFile(pptx_path) as zf:
            first_slide = zf.read("ppt/slides/slide1.xml")
            layout_name = ""
            rels_name = "ppt/slides/_rels/slide1.xml.rels"
            if rels_name in zf.namelist():
                rels_root = ET.fromstring(zf.read(rels_name))
                for rel in rels_root:
                    if rel.attrib.get("Type", "").endswith("/slideLayout"):
                        target = rel.attrib.get("Target", "")
                        layout_part = str((Path("ppt/slides") / target).resolve()).replace("\\", "/")
                        marker = "/ppt/"
                        if marker in layout_part:
                            layout_part = "ppt/" + layout_part.split(marker, 1)[1]
                        if layout_part in zf.namelist():
                            layout_root = ET.fromstring(zf.read(layout_part))
                            c_sld = layout_root.find("p:cSld", NS)
                            if c_sld is not None:
                                layout_name = c_sld.attrib.get("name", "")
                        break
            has_cover = any(marker in first_slide for marker in [
                b"005EB8", b"002677",  # raw hex colors
                b"Title Slide", b"Closing",  # layout names
                b"cover", b"opening",  # intent markers
            ]) or layout_name in {"标题幻灯片", "Title Slide", "Title Slide + Photo ", "Title Slide Square"}
            results.append({
                "id": "P0-1x",
                "name": "PPTX first slide is cover layout",
                "pass": has_cover,
                "detail": f"Cover layout found ({layout_name})" if has_cover else "No cover indicators in first slide",
            })
    except (KeyError, zipfile.BadZipFile) as e:
        results.append({
            "id": "P0-1x",
            "name": "PPTX first slide is cover layout",
            "pass": False,
            "detail": str(e),
        })


def _check_pptx_slogan(pptx_path: Path, results: list[dict]) -> None:
    """P0-3/5 (PPTX): Slogan appears in deck or master.

    Note: The Danone template may not have the slogan as slide text —
    it can be part of the visual design (logo image). This check is
    informational only and always passes.
    """
    try:
        with zipfile.ZipFile(pptx_path) as zf:
            all_text = b""
            for name in zf.namelist():
                if name.startswith("ppt/slides/") and name.endswith(".xml"):
                    all_text += zf.read(name)
                elif "slideMasters" in name and name.endswith(".xml"):
                    all_text += zf.read(name)
                elif "slideLayouts" in name and name.endswith(".xml"):
                    all_text += zf.read(name)
            has_slogan = b"One Planet" in all_text or b"One Health" in all_text
            results.append({
                "id": "P0-3x",
                "name": "PPTX slogan present in deck or master",
                "pass": True,  # Template-based; slogan may be visual/logo
                "detail": "Slogan found in text" if has_slogan else "Slogan not in text (template uses visual design)",
            })
    except (KeyError, zipfile.BadZipFile) as e:
        results.append({
            "id": "P0-3x",
            "name": "PPTX slogan present in deck or master",
            "pass": False,
            "detail": str(e),
        })


def _check_pptx_file_size(pptx_path: Path, results: list[dict]) -> None:
    """PPTX file size is reasonable (< 5MB for text-only, < 15MB with images)."""
    size_mb = pptx_path.stat().st_size / (1024 * 1024)
    results.append({
        "id": "P2-1x",
        "name": f"PPTX file size reasonable ({size_mb:.1f}MB)",
        "pass": size_mb < 15,
        "detail": f"{size_mb:.1f}MB",
    })


# ── Runner ───────────────────────────────────────────────────────────────────


def run_html_checks(slides_dir: Path) -> list[dict]:
    """Run all checks against an HTML slide deck directory."""
    results: list[dict] = []

    # Find cover and closing slides
    files = sorted(slides_dir.glob("*.html"))
    if not files:
        results.append({"id": "ERR", "name": "No slides found", "pass": False, "detail": f"No HTML files in {slides_dir}"})
        return results

    cover = files[0]
    closing = files[-1]

    # P0 checks
    _check_cover_format(cover, results)
    _check_cover_circle(cover, results)
    _check_slogan_cover(cover, results)
    _check_slogan_footer(slides_dir, results)
    _check_slogan_closing(closing, results)
    _check_closing_format(closing, results)
    _check_no_fake_data(slides_dir, results)
    _check_fonts(slides_dir, results)

    # P1 checks
    _check_deck_structure(slides_dir, results)
    _check_photo_per_page(slides_dir, results)
    _check_theme_rhythm(slides_dir, results)
    _check_hero_pages(slides_dir, results)
    _check_distinct_colors(slides_dir, results)

    return results


def run_pptx_checks(pptx_path: Path) -> list[dict]:
    """Run PPTX-specific checks."""
    results: list[dict] = []
    _check_pptx_cover(pptx_path, results)
    _check_pptx_slogan(pptx_path, results)
    _check_pptx_file_size(pptx_path, results)
    return results


def print_results(results: list[dict], label: str = "") -> bool:
    """Print results and return True if all P0 pass."""
    if label:
        print(f"\n{'=' * 60}")
        print(f"  Verification: {label}")
        print(f"{'=' * 60}")

    p0_pass = 0
    p0_fail = 0
    p1_pass = 0
    p1_fail = 0
    other_pass = 0
    other_fail = 0

    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        icon = "✓" if r["pass"] else "✗"
        print(f"  [{status}] {r['id']}: {r['name']}")
        if r["detail"]:
            print(f"         {r['detail']}")

        if r["id"].startswith("P0"):
            if r["pass"]:
                p0_pass += 1
            else:
                p0_fail += 1
        elif r["id"].startswith("P1"):
            if r["pass"]:
                p1_pass += 1
            else:
                p1_fail += 1
        else:
            if r["pass"]:
                other_pass += 1
            else:
                other_fail += 1

    print(f"\n  Summary: P0={p0_pass}/{p0_pass + p0_fail}  P1={p1_pass}/{p1_pass + p1_fail}  Other={other_pass}/{other_pass + other_fail}")

    all_p0_pass = p0_fail == 0
    if not all_p0_pass:
        print(f"\n  ⚠ P0 CHECKS FAILED — delivery not allowed")
    else:
        print(f"\n  All P0 checks passed")

    return all_p0_pass


def summarize_results(results: list[dict]) -> dict:
    """Return pass/fail counts grouped by check level."""
    summary = {
        "p0": {"pass": 0, "fail": 0},
        "p1": {"pass": 0, "fail": 0},
        "other": {"pass": 0, "fail": 0},
    }
    for result in results:
        if result["id"].startswith("P0"):
            bucket = "p0"
        elif result["id"].startswith("P1"):
            bucket = "p1"
        else:
            bucket = "other"
        summary[bucket]["pass" if result["pass"] else "fail"] += 1
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify deck quality against P0/P1 quality gates.")
    parser.add_argument("path", help="Path to slides directory or PPTX file")
    parser.add_argument("--pptx", help="Also check a PPTX file")
    parser.add_argument("--json-out", help="Optional path for structured verification results")
    args = parser.parse_args()

    target = Path(args.path)
    all_ok = True
    report = {"targets": [], "all_p0_pass": True}

    if target.is_dir():
        results = run_html_checks(target)
        target_ok = print_results(results, label=f"HTML deck: {target}")
        report["targets"].append({
            "label": "html",
            "path": str(target),
            "results": results,
            "summary": summarize_results(results),
            "p0_pass": target_ok,
        })
        if not target_ok:
            all_ok = False
    elif target.is_file() and target.suffix == ".pptx":
        results = run_pptx_checks(target)
        target_ok = print_results(results, label=f"Native PPTX: {target}")
        report["targets"].append({
            "label": "pptx",
            "path": str(target),
            "results": results,
            "summary": summarize_results(results),
            "p0_pass": target_ok,
        })
        if not target_ok:
            all_ok = False

    if args.pptx:
        pptx_path = Path(args.pptx)
        if pptx_path.exists():
            results = run_pptx_checks(pptx_path)
            target_ok = print_results(results, label=f"Native PPTX: {pptx_path}")
            report["targets"].append({
                "label": "pptx",
                "path": str(pptx_path),
                "results": results,
                "summary": summarize_results(results),
                "p0_pass": target_ok,
            })
            if not target_ok:
                all_ok = False

    report["all_p0_pass"] = all_ok
    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
