#!/usr/bin/env python
"""Run the Danone deck golden-path smoke test.

This intentionally exercises the public scripts end-to-end instead of importing
their internals: strategic notes -> HTML -> PDF -> image PPTX -> native PPTX ->
verification and handoff verdict.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "smoke-tests" / "strategic-brief.md"
DEFAULT_OUT = ROOT / "smoke-tests" / "golden-output"

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


class SmokeSetupError(RuntimeError):
    """Raised when golden smoke cannot prepare its output directory."""


def rel_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def ensure_clean_dir(path: Path) -> None:
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved == root or root not in resolved.parents:
        raise ValueError(f"Refusing to clean output outside repo: {resolved}")
    if path.exists():
        try:
            shutil.rmtree(path)
        except PermissionError as exc:
            raise SmokeSetupError(
                "Could not clean the golden smoke output directory because a file is locked. "
                f"Close any open PPTX/PDF/preview files under '{resolved}', or rerun with "
                "`--out-dir` pointing to a new directory."
            ) from exc
        except OSError as exc:
            raise SmokeSetupError(
                f"Could not clean the golden smoke output directory '{resolved}': {exc}. "
                "Close any process using those files, or rerun with `--out-dir` pointing to a new directory."
            ) from exc
    path.mkdir(parents=True, exist_ok=True)


def run_command(label: str, command: list[str], cwd: Path = ROOT) -> dict:
    started = datetime.now().isoformat(timespec="seconds")
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    finished = datetime.now().isoformat(timespec="seconds")
    return {
        "label": label,
        "command": command,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "started": started,
        "finished": finished,
    }


def write_command_log(out_dir: Path, logs: list[dict]) -> None:
    (out_dir / "command-log.json").write_text(
        json.dumps(logs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_expected_terms(markdown_path: Path) -> list[str]:
    markdown = markdown_path.read_text(encoding="utf-8")
    terms: list[str] = []
    title = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if title:
        terms.append(title.group(1).strip())
    for match in re.finditer(r"^##\s+Slide\s+\d+\s+[—:-]\s+(.+)$", markdown, re.MULTILINE):
        value = match.group(1).strip()
        if value and value.lower() not in {"opening", "closing"}:
            terms.append(value)
    return terms


def normalize_part(base_dir: str, target: str) -> str:
    parts: list[str] = []
    for part in f"{base_dir}/{target}".split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        else:
            parts.append(part)
    return "/".join(parts)


def natural_slide_key(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def extract_slide_text(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    return [node.text or "" for node in root.findall(".//a:t", NS) if (node.text or "").strip()]


def inspect_native_pptx(pptx_path: Path, expected_terms: list[str]) -> dict:
    inspection = {
        "path": rel_path(pptx_path),
        "exists": pptx_path.exists(),
        "valid_zip": False,
        "slide_count": 0,
        "text_node_count": 0,
        "expected_terms": expected_terms,
        "missing_expected_terms": [],
        "sample_text_hits": [],
        "dangling_image_relationships": [],
        "unused_image_relationships": [],
        "risks": [],
    }
    if not pptx_path.exists():
        inspection["risks"].append("missing_pptx")
        return inspection

    sample_patterns = [
        "Lorem ipsum",
        "Click to add",
        "Insert text",
        "Presentation title",
        "Opening Slide Title",
        "Closing Slide Title",
        "Sample text",
        "Subtitle goes here",
    ]

    try:
        with zipfile.ZipFile(pptx_path) as zf:
            names = set(zf.namelist())
            slide_names = sorted(
                [name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name)],
                key=natural_slide_key,
            )
            all_text: list[str] = []
            for slide_name in slide_names:
                xml_bytes = zf.read(slide_name)
                slide_text = extract_slide_text(xml_bytes)
                all_text.extend(slide_text)
                rels_name = f"ppt/slides/_rels/{Path(slide_name).name}.rels"
                if rels_name not in names:
                    continue
                rels_root = ET.fromstring(zf.read(rels_name))
                rels = {
                    rel.attrib.get("Id", ""): rel.attrib.get("Target", "")
                    for rel in rels_root.findall("rel:Relationship", NS)
                    if rel.attrib.get("Type", "").endswith("/image")
                }
                root = ET.fromstring(xml_bytes)
                used_rids = {
                    node.attrib.get(f"{{{NS['r']}}}embed", "")
                    for node in root.findall(".//a:blip", NS)
                    if node.attrib.get(f"{{{NS['r']}}}embed")
                }
                for rid, target in rels.items():
                    target_part = normalize_part("ppt/slides", target)
                    if target_part not in names:
                        inspection["dangling_image_relationships"].append({
                            "slide": slide_name,
                            "rid": rid,
                            "target": target,
                        })
                    if rid not in used_rids:
                        inspection["unused_image_relationships"].append({
                            "slide": slide_name,
                            "rid": rid,
                            "target": target,
                        })
                for rid in used_rids:
                    if rid not in rels:
                        inspection["dangling_image_relationships"].append({
                            "slide": slide_name,
                            "rid": rid,
                            "target": None,
                        })

            joined_text = "\n".join(all_text)
            inspection["valid_zip"] = True
            inspection["slide_count"] = len(slide_names)
            inspection["text_node_count"] = len(all_text)
            inspection["missing_expected_terms"] = [
                term for term in expected_terms if term and term not in joined_text
            ]
            inspection["sample_text_hits"] = [
                pattern for pattern in sample_patterns if pattern.lower() in joined_text.lower()
            ]
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        inspection["risks"].append(f"bad_pptx:{exc}")
        return inspection

    if inspection["slide_count"] == 0:
        inspection["risks"].append("no_slides")
    if inspection["text_node_count"] == 0:
        inspection["risks"].append("no_editable_text")
    if inspection["missing_expected_terms"]:
        inspection["risks"].append("missing_expected_terms")
    if inspection["sample_text_hits"]:
        inspection["risks"].append("sample_text_leftover")
    if inspection["dangling_image_relationships"]:
        inspection["risks"].append("dangling_image_relationships")
    return inspection


def file_status(path: Path) -> dict:
    exists = path.exists()
    return {
        "path": rel_path(path),
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
    }


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def detect_doc_version_mismatch() -> dict:
    package_path = ROOT / "package.json"
    readme_path = ROOT / "README.md"
    changelog_path = ROOT / "CHANGELOG.md"
    package_version = ""
    readme_versions: list[str] = []
    changelog_top = ""
    if package_path.exists():
        package_version = json.loads(package_path.read_text(encoding="utf-8")).get("version", "")
    if readme_path.exists():
        readme_versions = re.findall(r"v?(\d+\.\d+\.\d+)", readme_path.read_text(encoding="utf-8"))[:3]
    if changelog_path.exists():
        match = re.search(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", changelog_path.read_text(encoding="utf-8"), re.MULTILINE)
        changelog_top = match.group(1) if match else ""
    versions = {value for value in [package_version, changelog_top, *readme_versions] if value}
    return {
        "package_version": package_version,
        "readme_versions": readme_versions,
        "changelog_top": changelog_top,
        "mismatch": len(versions) > 1,
    }


def choose_recommendation(
    statuses: dict,
    verify_report: dict,
    native_inspection: dict,
    doc_versions: dict,
    command_logs: list[dict],
) -> str:
    failed_commands = [log for log in command_logs if log["returncode"] != 0]
    if any(not statuses[key]["exists"] for key in ["html_index", "pdf", "image_pptx"]):
        return "fix-export"
    if not statuses["native_pptx"]["exists"] or native_inspection.get("risks"):
        return "fix-native-mapping"
    if failed_commands:
        failed_labels = {log["label"] for log in failed_commands}
        if failed_labels & {"generate"}:
            return "fix-native-mapping"
        if failed_labels - {"verify"}:
            return "fix-export"
    if verify_report and not verify_report.get("all_p0_pass", False):
        return "ready-for-sample-gallery"
    if doc_versions.get("mismatch"):
        return "fix-docs-dx"
    return "ready-for-sample-gallery"


def render_verdict(
    out_dir: Path,
    input_path: Path,
    command_logs: list[dict],
    statuses: dict,
    verify_report: dict,
    native_inspection: dict,
    doc_versions: dict,
    recommendation: str,
) -> str:
    lines = [
        "# Golden Smoke Handoff Verdict",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Input: `{rel_path(input_path)}`",
        f"- Output: `{rel_path(out_dir)}`",
        f"- Recommended next step: `{recommendation}`",
        "",
        "## Command Summary",
        "",
    ]
    for log in command_logs:
        command = " ".join(f'"{part}"' if " " in part else part for part in log["command"])
        lines.append(f"- `{log['label']}` exit `{log['returncode']}`: `{command}`")
    lines.extend(["", "## Output Files", "", "| Artifact | Exists | Size | Path |", "|---|---:|---:|---|"])
    for label, status in statuses.items():
        lines.append(
            f"| {label} | {'yes' if status['exists'] else 'no'} | {status['size_bytes']} | `{status['path']}` |"
        )
    lines.extend(["", "## Status Matrix", ""])
    html_ok = statuses["html_index"]["exists"] and statuses["slides_dir"]["exists"]
    pdf_ok = statuses["pdf"]["exists"] and statuses["pdf"]["size_bytes"] > 0
    image_ok = statuses["image_pptx"]["exists"] and statuses["image_pptx"]["size_bytes"] > 0
    native_ok = statuses["native_pptx"]["exists"] and not native_inspection.get("risks")
    verify_ok = verify_report.get("all_p0_pass") if verify_report else False
    lines.extend([
        f"- HTML deck: `{'pass' if html_ok else 'fail'}`",
        f"- PDF export: `{'pass' if pdf_ok else 'fail'}`",
        f"- Image PPTX export: `{'pass' if image_ok else 'fail'}`",
        f"- Native editable PPTX: `{'pass' if native_ok else 'risk'}`",
        f"- verify_deck P0: `{'pass' if verify_ok else 'fail'}`",
    ])
    lines.extend(["", "## Native PPTX Inspection", ""])
    lines.extend([
        f"- Slide count: `{native_inspection.get('slide_count', 0)}`",
        f"- Editable text nodes: `{native_inspection.get('text_node_count', 0)}`",
        f"- Missing expected terms: `{', '.join(native_inspection.get('missing_expected_terms', [])) or 'none'}`",
        f"- Sample text hits: `{', '.join(native_inspection.get('sample_text_hits', [])) or 'none'}`",
        f"- Dangling image rels: `{len(native_inspection.get('dangling_image_relationships', []))}`",
        f"- Risks: `{', '.join(native_inspection.get('risks', [])) or 'none'}`",
    ])
    lines.extend(["", "## Docs/DX Signal", ""])
    lines.append(
        f"- Version mismatch: `{'yes' if doc_versions.get('mismatch') else 'no'}` "
        f"(package `{doc_versions.get('package_version')}`, README `{', '.join(doc_versions.get('readme_versions', []))}`, CHANGELOG `{doc_versions.get('changelog_top')}`)"
    )
    lines.extend(["", "## Next Decision", ""])
    if recommendation == "fix-native-mapping":
        lines.append("Native PPTX is the limiting path. Next session should focus on placeholder/content mapping and native smoke tests.")
    elif recommendation == "fix-export":
        lines.append("The export chain is the limiting path. Next session should fix the first failed generation/export command.")
    elif recommendation == "fix-docs-dx":
        lines.append("The delivery chain works, but project metadata/docs disagree. Next session should sync README, package version, CHANGELOG, and ROADMAP.")
    else:
        lines.append("Core generation works. Next session can build a sample gallery and improve visual variation.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run golden-path Danone deck smoke test.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Strategic brief input")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Golden output directory")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    out_dir = Path(args.out_dir).resolve()
    slides_dir = out_dir / "slides"
    native_pptx = out_dir / "deck-editable.pptx"
    pdf_path = out_dir / "deck.pdf"
    image_pptx = out_dir / "deck-image.pptx"
    verify_json = out_dir / "verify-report.json"
    native_json = out_dir / "native-inspection.json"
    verdict_path = out_dir / "handoff-verdict.md"

    command_logs: list[dict] = []
    try:
        ensure_clean_dir(out_dir)
    except SmokeSetupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    commands = [
        (
            "generate",
            [
                sys.executable,
                "scripts/notes_to_danone_deck.py",
                "--notes",
                str(input_path),
                "--out-dir",
                str(out_dir),
                "--mode",
                "strategic",
                "--brand-line",
                "DHT Lab - Danone",
                "--native-pptx",
                str(native_pptx),
                "--out-plan",
                str(out_dir / "native-plan.json"),
            ],
        ),
        (
            "export-pdf",
            [
                "node",
                "scripts/export_deck_pdf.mjs",
                "--slides",
                str(slides_dir),
                "--out",
                str(pdf_path),
                "--width",
                "1280",
                "--height",
                "720",
            ],
        ),
        (
            "export-image-pptx",
            [
                "node",
                "scripts/export_deck_pptx.mjs",
                "--slides",
                str(slides_dir),
                "--out",
                str(image_pptx),
                "--width",
                "1280",
                "--height",
                "720",
            ],
        ),
        (
            "verify",
            [
                sys.executable,
                "scripts/verify_deck.py",
                str(slides_dir),
                "--pptx",
                str(native_pptx),
                "--json-out",
                str(verify_json),
            ],
        ),
    ]

    for label, command in commands:
        log = run_command(label, command)
        command_logs.append(log)
        write_command_log(out_dir, command_logs)
        if label == "verify":
            (out_dir / "verify-stdout.txt").write_text(log["stdout"] + log["stderr"], encoding="utf-8")
        if log["returncode"] != 0 and label != "verify":
            break

    expected_terms = parse_expected_terms(input_path)
    native_inspection = inspect_native_pptx(native_pptx, expected_terms)
    native_json.write_text(json.dumps(native_inspection, ensure_ascii=False, indent=2), encoding="utf-8")

    statuses = {
        "html_index": file_status(out_dir / "index.html"),
        "slides_dir": {
            "path": rel_path(slides_dir),
            "exists": slides_dir.exists(),
            "size_bytes": len(list(slides_dir.glob("*.html"))) if slides_dir.exists() else 0,
        },
        "native_pptx": file_status(native_pptx),
        "pdf": file_status(pdf_path),
        "image_pptx": file_status(image_pptx),
        "verify_report": file_status(verify_json),
        "native_inspection": file_status(native_json),
    }
    verify_report = load_json(verify_json)
    doc_versions = detect_doc_version_mismatch()
    recommendation = choose_recommendation(statuses, verify_report, native_inspection, doc_versions, command_logs)
    verdict = render_verdict(
        out_dir,
        input_path,
        command_logs,
        statuses,
        verify_report,
        native_inspection,
        doc_versions,
        recommendation,
    )
    verdict_path.write_text(verdict, encoding="utf-8")
    print(verdict)

    failed_generation = [log for log in command_logs if log["returncode"] != 0 and log["label"] != "verify"]
    sys.exit(1 if failed_generation else 0)


if __name__ == "__main__":
    main()
