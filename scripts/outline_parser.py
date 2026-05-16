#!/usr/bin/env python
"""Intelligent outline parser: free-form Markdown → structured slide plan.

Parses arbitrary Markdown outlines, classifies each block into an intent type,
assigns theme colors based on content semantics, and applies theme rhythm rules.

Usage:
    python scripts/outline_parser.py input.md [--out plan.json]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ── Intent Classification Keywords ──────────────────────────────────────────

INTENT_KEYWORDS = {
    "cover": ["封面", "cover", "opening", "标题页", "开场"],
    "closing": ["感谢", "thank", "closing", "结束", "尾页", "thank you", "thanks"],
    "big-message": ["核心", "key message", "核心信息", "takeaway", "重点", "关键"],
    "big-quote": ["quote", "引用", "名言", "客户说", "testimonial"],
    "decision-grid": ["决策", "decision", "vp review", "review", "approve", "审批", "service", "architecture", "priority", "tier"],
    "positioning": ["对比", "comparison", "vs", "before", "after", "定位", "差异", "positioning", "position"],
    "flow": ["流程", "process", "step", "步骤", "pipeline", "workflow", "journey", "experience", "user journey", "体验", "旅程"],
    "stat-grid": ["数据", "data", "metric", "kpi", "指标", "统计", "dashboard", "flywheel", "循环", "loop"],
    "chart-or-table": ["图表", "chart", "table", "数据表", "趋势", "trend"],
    "contents": ["目录", "contents", "agenda", "大纲", "overview", "总览"],
}

# ── Theme Classification Keywords ───────────────────────────────────────────

THEME_KEYWORDS = {
    "gut": {
        "keywords": ["gut", "肠道", "digest", "microbiome", "probiotic", "probiotics", "益", "消化"],
        "accent": "var(--dn-green)",
        "soft": "var(--dn-green-soft)",
        "dark": "var(--dn-green-dark)",
    },
    "physical": {
        "keywords": ["sport", "physical", "运动", "recovery", "hydration", "fitness", "锻炼", "体能"],
        "accent": "var(--dn-orange)",
        "soft": "var(--dn-orange-soft)",
        "dark": "var(--dn-orange-dark)",
    },
    "clinical": {
        "keywords": ["clinical", "tube", "medical", "nutrison", "管饲", "康复", "baby", "婴儿", "临床"],
        "accent": "var(--dn-pink)",
        "soft": "var(--dn-pink-soft)",
        "dark": "var(--dn-pink-dark)",
    },
    "water": {
        "keywords": ["water", "hydration", "水", "汗液", "补水", "电解质"],
        "accent": "var(--dn-teal)",
        "soft": "var(--dn-teal-soft)",
        "dark": "var(--dn-teal-dark)",
    },
}

DEFAULT_THEME = {
    "accent": "var(--dn-blue)",
    "soft": "var(--dn-soft)",
    "dark": "var(--dn-blue-dark)",
}

# ── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class SlideBlock:
    """A parsed slide block from the outline."""
    title: str
    body_lines: list[str] = field(default_factory=list)
    bullet_items: list[str] = field(default_factory=list)
    image_hint: str | None = None
    section: str = ""  # parent section name for theme inference


@dataclass
class ClassifiedSlide:
    """A slide with intent classification and theme assignment."""
    intent: str
    title: str
    content: dict
    theme: dict
    theme_name: str


# ── Parser ───────────────────────────────────────────────────────────────────


def parse_outline(text: str) -> list[SlideBlock]:
    """Parse free-form Markdown into structured slide blocks.

    Supports:
    - `## Slide N -- Title` or `## Slide N:Title` (structured format)
    - `## 场景 N|Name` (scenario format)
    - `## Title` (free-form: title as heading, body as text/bullets below)
    """
    lines = text.split("\n")
    blocks: list[SlideBlock] = []
    current: SlideBlock | None = None
    current_section = ""

    for line in lines:
        stripped = line.strip()

        # Detect slide boundaries (## level headings)
        if stripped.startswith("## ") and not stripped.startswith("### "):
            if current is not None:
                blocks.append(current)

            # Parse title
            header = stripped[3:].strip()
            # Remove "Slide N --" or "Slide N:" prefix
            title = re.sub(r"^Slide\s+\d+\s*[:\-\—]\s*", "", header, flags=re.IGNORECASE).strip()
            # Remove "场景 N|" prefix
            title = re.sub(r"^场景\s+\d+\|", "", title).strip()

            # Detect section boundaries (# level headings)
            if stripped.startswith("# ") and not stripped.startswith("## "):
                current_section = stripped[2:].strip()

            # Check if the header itself indicates a section break
            is_section = (
                re.match(r"^(场景|section|chapter|part|阶段|篇章)\s*\d*", title, re.IGNORECASE)
                or len(title) < 20 and "场景" in header
            )
            if is_section:
                current_section = title

            # Extract image hint from title
            image_hint = _extract_image_hint(title)
            title = re.sub(r"\[img:\s*[^\]]*\]|\[photo:\s*[^\]]*\]", "", title).strip()

            current = SlideBlock(
                title=title,
                section=current_section,
                image_hint=image_hint,
            )
            continue

        if current is None:
            continue

        # Extract image hints from body
        img_match = re.search(r"\[img:\s*([^\]]+)\]|\[photo:\s*([^\]]+)\]", stripped)
        if img_match:
            current.image_hint = (img_match.group(1) or img_match.group(2)).strip()
            stripped = re.sub(r"\[img:\s*[^\]]*\]|\[photo:\s*[^\]]*\]", "", stripped).strip()

        # Skip ### subheading markers (metadata labels, not content)
        if stripped.startswith("### "):
            continue

        if not stripped:
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            current.bullet_items.append(stripped[2:].strip())
        else:
            current.body_lines.append(stripped)

    if current is not None:
        blocks.append(current)

    return blocks


def _extract_image_hint(text: str) -> str | None:
    """Extract [img: path] or [photo: path] marker from text."""
    m = re.search(r"\[img:\s*([^\]]+)\]|\[photo:\s*([^\]]+)\]", text)
    return m.group(1) or m.group(2) if m else None


# ── Intent Classifier ────────────────────────────────────────────────────────


def classify_intent(block: SlideBlock, position: int, total: int) -> str:
    """Classify a slide block into an intent type based on content analysis."""
    text = f"{block.title} {' '.join(block.body_lines)} {' '.join(block.bullet_items)}"
    text_lower = text.lower()

    # Position-based classification
    if position == 1:
        # Check if title suggests cover
        if _match_keywords(text_lower, INTENT_KEYWORDS["cover"]):
            return "opening-cover"
        # If title is short and no specific content, assume cover
        if len(block.title) < 30 and not block.bullet_items and not block.body_lines:
            return "opening-cover"

    if position == total:
        if _match_keywords(text_lower, INTENT_KEYWORDS["closing"]):
            return "closing"
        # Last slide with short title = likely closing
        if len(block.title) < 30 and not block.bullet_items and not block.body_lines:
            return "closing"

    # Keyword-based classification
    for intent, keywords in INTENT_KEYWORDS.items():
        if _match_keywords(text_lower, keywords):
            return intent

    # Structure-based classification
    n_items = len(block.bullet_items)
    n_lines = len(block.body_lines)

    if n_items >= 4:
        return "decision-grid"
    if n_items == 3:
        return "three-column"
    if n_items == 2:
        return "two-column"
    if n_lines <= 1 and len(block.title) > 30:
        return "big-message"
    if block.image_hint:
        return "image-content"

    # Default fallback
    if n_items >= 3:
        return "three-column"
    if n_items == 2:
        return "two-column"
    return "big-message"


def _match_keywords(text: str, keywords: list[str]) -> bool:
    """Check if any keyword appears in the text using word-boundary matching."""
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
            return True
    return False


# ── Theme Assignment ─────────────────────────────────────────────────────────


def classify_theme(block: SlideBlock) -> tuple[str, dict]:
    """Assign a theme color based on content semantics."""
    text = f"{block.title} {block.section} {' '.join(block.body_lines)}".lower()

    for name, theme_info in THEME_KEYWORDS.items():
        if any(kw.lower() in text for kw in theme_info["keywords"]):
            return name, {
                "accent": theme_info["accent"],
                "soft": theme_info["soft"],
                "dark": theme_info["dark"],
            }

    return "corporate", DEFAULT_THEME


def apply_theme_rhythm(
    slides: list[ClassifiedSlide],
) -> list[ClassifiedSlide]:
    """Enforce theme rhythm: no 3+ consecutive same theme pages."""
    if len(slides) <= 2:
        return slides

    themes_used = set()
    alternate_themes = [
        ("light", "dark", "light", "hero", "light", "dark", "light", "hero"),
    ]

    for i, slide in enumerate(slides):
        # Assign theme class (light/dark/hero)
        if i == 0 or i == len(slides) - 1:
            slide.content["theme_class"] = "hero"
        else:
            cycle = alternate_themes[0]
            slide.content["theme_class"] = cycle[i % len(cycle)]

        # Check for 3+ consecutive same color theme
        if i >= 2:
            prev_two = [slides[i - 2].theme_name, slides[i - 1].theme_name]
            if prev_two[0] == prev_two[1] == slide.theme_name:
                # Force a different theme color
                for alt_name, alt_theme in THEME_KEYWORDS.items():
                    if alt_name != slide.theme_name:
                        slide.theme_name = alt_name
                        slide.theme = {
                            "accent": alt_theme["accent"],
                            "soft": alt_theme["soft"],
                            "dark": alt_theme["dark"],
                        }
                        break

    return slides


# ── Content Builder ──────────────────────────────────────────────────────────


def build_content(intent: str, block: SlideBlock) -> dict:
    """Build the content dict for a given intent from a SlideBlock."""
    content: dict = {}

    if intent == "opening-cover":
        content["title"] = block.title
        content["subtitle_or_date"] = " ".join(block.body_lines) if block.body_lines else ""
    elif intent == "closing":
        content["title"] = "THANK YOU"
    elif intent == "big-message":
        content["headline"] = block.title
        content["supporting_text"] = " ".join(block.body_lines) if block.body_lines else ""
    elif intent == "two-column":
        content["title"] = block.title
        mid = len(block.bullet_items) // 2
        content["left_content"] = block.bullet_items[:mid] or block.body_lines[:2]
        content["right_content"] = block.bullet_items[mid:] or block.body_lines[2:]
    elif intent == "three-column":
        content["title"] = block.title
        items = block.bullet_items or block.body_lines
        chunk = max(1, len(items) // 3)
        content["column_1"] = items[:chunk]
        content["column_2"] = items[chunk:chunk * 2]
        content["column_3"] = items[chunk * 2:]
    elif intent == "image-content":
        content["title"] = block.title
        content["body"] = " ".join(block.body_lines)
        if block.image_hint:
            content["image"] = block.image_hint
    elif intent == "section-photo":
        content["title"] = block.title
        if block.image_hint:
            content["image"] = block.image_hint
    elif intent == "big-quote":
        content["title"] = block.title
        content["quote"] = " ".join(block.body_lines)
    elif intent == "decision-grid":
        content["title"] = block.title
        content["decision_items"] = block.bullet_items or block.body_lines
    elif intent == "positioning":
        content["title"] = block.title
        mid = len(block.bullet_items) // 2
        content["before_text"] = block.bullet_items[:mid] or [""]
        content["after_text"] = block.bullet_items[mid:] or [""]
    elif intent == "flow":
        content["title"] = block.title
        content["flow_steps"] = block.bullet_items or block.body_lines
    elif intent == "stat-grid":
        content["title"] = block.title
        content["stats"] = block.bullet_items or block.body_lines
    elif intent == "contents":
        content["title"] = block.title
        content["agenda_items"] = block.bullet_items or block.body_lines
    elif intent == "chart-or-table":
        content["title"] = block.title
        content["chart_or_table"] = "Data TBD"
        content["insight"] = " ".join(block.body_lines)
    else:
        # Generic fallback
        content["title"] = block.title
        if block.bullet_items:
            content["body"] = block.bullet_items
        elif block.body_lines:
            content["body"] = " ".join(block.body_lines)

    if block.image_hint and "image" not in content:
        content["image"] = block.image_hint

    return content


# ── Main Pipeline ────────────────────────────────────────────────────────────


def parse_and_classify(text: str, mode: str = "auto") -> list[ClassifiedSlide]:
    """Full pipeline: parse → classify → theme → rhythm."""
    blocks = parse_outline(text)
    if not blocks:
        return []

    total = len(blocks)
    slides: list[ClassifiedSlide] = []

    for i, block in enumerate(blocks, start=1):
        intent = classify_intent(block, i, total)
        theme_name, theme = classify_theme(block)
        content = build_content(intent, block)
        content["theme_name"] = theme_name

        slides.append(ClassifiedSlide(
            intent=intent,
            title=block.title,
            content=content,
            theme=theme,
            theme_name=theme_name,
        ))

    slides = apply_theme_rhythm(slides)
    return slides


def to_plan(slides: list[ClassifiedSlide]) -> list[dict]:
    """Convert classified slides to the JSON plan format expected by build_native_pptx.py."""
    plan = []
    for slide in slides:
        plan.append({
            "intent": slide.intent,
            "content": slide.content,
        })
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse free-form Markdown outline → structured JSON slide plan."
    )
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("--out", default="plan.json", help="Output JSON plan file")
    parser.add_argument("--mode", choices=["auto", "strategic", "scenario"], default="auto")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    slides = parse_and_classify(text, mode=args.mode)
    plan = to_plan(slides)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("Parsed %d slides → %s", len(plan), args.out)

    # Print summary
    for i, slide in enumerate(slides, start=1):
        print(f"  Slide {i:2d}: intent={slide.intent:<18s} theme={slide.theme_name:<12s} title={slide.title}")


if __name__ == "__main__":
    main()
