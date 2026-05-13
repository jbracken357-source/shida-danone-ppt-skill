#!/usr/bin/env python
"""Detect input format and normalize to structured Danone deck Markdown.

Accepts free-form topics, bullet outlines, scripts, or existing structured notes.
Outputs normalized Markdown in the `## 场景 N｜Name` format for the deck builder.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def detect_format(content: str) -> str:
    """Detect the input format. Returns one of: structured, outline, topics, script."""
    # Structured: has ## 场景 N| pattern
    if re.search(r"^##\s*场景\s*\d+[｜|]", content, re.MULTILINE):
        return "structured"
    # Outline: has numbered headings or bullet list with clear hierarchy
    if re.search(r"^(?:#{1,3}\s*\d+[\.\s]|[一1-9]+\.\s|\-\s+[A-Z])", content, re.MULTILINE):
        return "outline"
    # Script: long paragraphs, >500 chars, prose-style
    if len(content.strip()) > 500 and content.count("\n\n") > 3:
        return "script"
    # Topics: short phrases, bullet list
    return "topics"


def normalize_structured(content: str) -> str:
    """Pass through already-structured content unchanged."""
    return content


def normalize_outline(content: str) -> str:
    """Convert a bullet/numbered outline to structured Danone format.

    This does NOT use regex to parse the outline. Instead, it outputs a
    structured skeleton that Claude fills in. The script handles format detection;
    Claude handles content mapping.
    """
    lines = content.strip().splitlines()

    # Extract title (first # heading or first line)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else lines[0].strip("# - ")

    # Find scenario sections (## headings or numbered items)
    scenarios: list[tuple[str, str]] = []
    current_name = ""
    current_lines: list[str] = []

    for line in lines:
        heading_match = re.match(r"^#{1,3}\s*(\d+[\.\s]+)?(.+)$", line)
        if heading_match:
            if current_name:
                scenarios.append((current_name, "\n".join(current_lines)))
            current_name = heading_match.group(2).strip()
            current_lines = []
        elif line.strip().startswith("- "):
            current_lines.append(line.strip())

    if current_name:
        scenarios.append((current_name, "\n".join(current_lines)))

    if not scenarios:
        # Fall back: treat each top-level bullet as a scenario
        for i, line in enumerate(lines, 1):
            text = re.sub(r"^[-*\d.\s]+", "", line).strip()
            if text:
                scenarios.append((f"Topic {i}", text))

    # Build normalized output
    output = f"# {title}\n\n"
    for idx, (name, body) in enumerate(scenarios, 1):
        output += f"## 场景 {idx}｜{name}\n\n"
        output += f"### Target User\n- {body}\n\n"
        output += f"### Pain Points\n- 待补充\n\n"
        output += f"### Hardware\n待补充\n\n"
        output += f"### Objective\n- 待补充\n\n"
        output += f"### Collected Data\n- 待补充\n\n"
        output += f"### Interpreted Indicators\n- 待补充\n\n"
        output += f"### Link to Danone Products\n- 待补充\n\n"
        output += f"### Core Message\n> 待补充\n\n"

    return inject_image_hints(output, extract_image_hints(content))


def extract_image_hints(content: str) -> list[str]:
    """Extract [img: xxx] / [photo: xxx] markers from raw input."""
    pattern = re.compile(r"\[(?:img|photo|image):\s*([^\]]+)\]", re.IGNORECASE)
    return [m.group(1).strip() for m in pattern.finditer(content)]


def inject_image_hints(output: str, hints: list[str]) -> str:
    """Inject image hints into the structured Markdown as ### Photo sections."""
    if not hints:
        return output
    # Insert after the first scenario's first sub-section
    lines = output.splitlines()
    insert_idx = None
    scenario_count = 0
    for i, line in enumerate(lines):
        if line.startswith("### "):
            if scenario_count == 1:
                insert_idx = i
                break
        if line.startswith("## 场景"):
            scenario_count += 1
    if insert_idx is not None:
        hint_lines = [f"[img: {h}]" for h in hints]
        lines.insert(insert_idx, "### Photo")
        for j, hint_line in enumerate(hint_lines):
            lines.insert(insert_idx + 1 + j, hint_line)
        lines.insert(insert_idx + 1 + len(hints), "")
    return "\n".join(lines)


def normalize_topics(content: str) -> str:
    """Convert a list of topics/keywords to a minimal structured deck."""
    lines = [re.sub(r"^[-*\d.\s]+", "", line).strip() for line in content.strip().splitlines()]
    lines = [l for l in lines if l]

    if not lines:
        raise ValueError("Empty input: provide at least one topic or brief.")

    title = lines[0]
    topics = lines[1:] if len(lines) > 1 else ["Overview"]

    output = f"# {title}\n\n"
    for idx, topic in enumerate(topics, 1):
        output += f"## 场景 {idx}｜{topic}\n\n"
        output += f"### Target User\n- 待补充\n\n"
        output += f"### Pain Points\n- 待补充\n\n"
        output += f"### Hardware\n待补充\n\n"
        output += f"### Objective\n- 待补充\n\n"
        output += f"### Collected Data\n- 待补充\n\n"
        output += f"### Interpreted Indicators\n- 待补充\n\n"
        output += f"### Link to Danone Products\n- 待补充\n\n"
        output += f"### Core Message\n> 待补充\n\n"

    return inject_image_hints(output, extract_image_hints(content))


def normalize_script(content: str) -> str:
    """Convert a long-form script/article to structured deck chunks.

    Splits content by major sections (headings, numbered items, or paragraph
    breaks) and creates one scenario per section. Claude fills in the details.
    """
    # Find natural section breaks
    breaks = [m.start() for m in re.finditer(r"^(?:#{1,3}\s|PART\s+\w+|Chapter\s+\d+|\d+\.\s+[A-Z])", content, re.MULTILINE)]
    if not breaks:
        # Split by double newlines, group into chunks of ~3 paragraphs
        paragraphs = content.strip().split("\n\n")
        breaks = []
        for i in range(0, len(paragraphs), 3):
            offset = sum(len(p) + 2 for p in paragraphs[:i])
            breaks.append(offset)

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else content.split("\n")[0][:80]

    sections: list[str] = []
    for i, start in enumerate(breaks):
        end = breaks[i + 1] if i + 1 < len(breaks) else len(content)
        sections.append(content[start:end].strip())

    if not sections:
        sections = [content.strip()]

    output = f"# {title}\n\n"
    for idx, section in enumerate(sections, 1):
        # Extract a heading if present
        heading_match = re.match(r"^(?:#{1,3}\s*|\d+\.\s*)(.+)", section)
        name = heading_match.group(1) if heading_match else f"Section {idx}"
        name = name.strip()[:80]

        output += f"## 场景 {idx}｜{name}\n\n"
        output += f"### Target User\n- 待补充\n\n"
        output += f"### Pain Points\n- 待补充\n\n"
        output += f"### Hardware\n待补充\n\n"
        output += f"### Objective\n- 待补充\n\n"
        output += f"### Collected Data\n- 待补充\n\n"
        output += f"### Interpreted Indicators\n- 待补充\n\n"
        output += f"### Link to Danone Products\n- 待补充\n\n"
        output += f"### Core Message\n> 待补充\n\n"

    return inject_image_hints(output, extract_image_hints(content))


FORMAT_NORMALIZERS = {
    "structured": normalize_structured,
    "outline": normalize_outline,
    "topics": normalize_topics,
    "script": normalize_script,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize free-form input to structured Danone deck Markdown.")
    parser.add_argument("--input", required=True, help="Input file (brief, outline, topics, or script)")
    parser.add_argument("--out", required=True, help="Output normalized Markdown file")
    parser.add_argument("--format", choices=["auto", "structured", "outline", "topics", "script"], default="auto", help="Input format (auto-detect by default)")
    args = parser.parse_args()

    content = Path(args.input).read_text(encoding="utf-8")

    if args.format == "auto":
        fmt = detect_format(content)
    else:
        fmt = args.format

    normalizer = FORMAT_NORMALIZERS[fmt]
    normalized = normalizer(content)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(normalized, encoding="utf-8")

    print(f"Detected format: {fmt}")
    print(f"Wrote normalized Markdown to {args.out}")


if __name__ == "__main__":
    main()
