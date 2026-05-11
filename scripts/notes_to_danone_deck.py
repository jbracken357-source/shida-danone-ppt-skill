#!/usr/bin/env python
"""Build a Danone smoke deck from structured Markdown slide notes."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "Danone Real Templates" / "Standard Danone Template.pptx"
DEFAULT_LAYOUT_MAP = ROOT / "templates" / "layout-map.json"
DEFAULT_TOKENS = ROOT / "templates" / "tokens.css"

# Theme colors per scenario category (matched to real Danone template colorways)
THEMES = {
    "gut": {
        "accent": "var(--dn-green)",
        "soft": "var(--dn-green-soft)",
        "dark": "var(--dn-green-dark)",
    },
    "physical": {
        "accent": "var(--dn-orange)",
        "soft": "var(--dn-orange-soft)",
        "dark": "var(--dn-orange-dark)",
    },
    "clinical": {
        "accent": "var(--dn-pink)",
        "soft": "var(--dn-pink-soft)",
        "dark": "var(--dn-pink-dark)",
    },
}

DEFAULT_THEME = {
    "accent": "var(--dn-blue)",
    "soft": "var(--dn-soft)",
    "dark": "var(--dn-blue-dark)",
}


def pick_theme(scenario_name: str) -> dict:
    """Map scenario name to theme colorway."""
    name = scenario_name.lower()
    if any(k in name for k in ("gut", "肠道", "digest", "microbiome")):
        return THEMES["gut"]
    if any(k in name for k in ("physical", "sport", "运动", "recovery", "hydrat", "汗液")):
        return THEMES["physical"]
    if any(k in name for k in ("clinical", "tube", "medical", "nutrison", "管饲", "康复")):
        return THEMES["clinical"]
    return DEFAULT_THEME


BASE_COMPONENT_CSS = """
:root {
  --dn-font: "Danone One Light", "Arial Narrow", "Arial", "Microsoft YaHei", sans-serif;
  --dn-font-display: "Danone One Condensed", "Arial Narrow", "Arial", "Microsoft YaHei", sans-serif;
}

h1, h2, h3, h4, p, ul, li {
  margin: 0;
  padding: 0;
}

ul {
  padding-left: 22px;
}

li {
  margin-bottom: 10px;
  font-size: 20px;
  line-height: 1.32;
  color: var(--dn-text);
}

li::marker {
  color: var(--dn-blue);
}

.slide {
  position: relative;
  width: 1280px;
  height: 720px;
  padding: 54px 72px 50px;
  overflow: hidden;
  background: #fff;
}

.slide-blue {
  background: var(--dn-blue);
  color: #fff;
}

/* ---- Cover ---- */
.cover-bg {
  position: absolute;
  inset: 0;
  background: var(--dn-blue);
  z-index: 0;
}
.cover-photo {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, rgba(0,94,184,0.92) 0%, rgba(0,94,184,0.72) 45%, rgba(0,94,184,0.25) 100%);
  z-index: 1;
}
.cover-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: grid;
  grid-template-columns: 1.15fr .85fr;
  gap: 56px;
  align-items: center;
}
.cover-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 24px;
}
.cover-slogan {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.65);
}
.cover-title {
  font-family: var(--dn-font-display);
  font-size: 56px;
  line-height: 1.04;
  font-weight: 700;
  color: #fff;
}
.cover-copy {
  font-size: 26px;
  line-height: 1.3;
  color: rgba(255,255,255,0.88);
  max-width: 520px;
}
.cover-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.chip {
  border: 1px solid rgba(255,255,255,.32);
  border-radius: 12px;
  padding: 20px 22px;
  background: rgba(255,255,255,.08);
  backdrop-filter: blur(4px);
}
.chip-label {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.6);
  margin-bottom: 6px;
}
.chip-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}
.chip-desc {
  margin-top: 6px;
  font-size: 16px;
  line-height: 1.35;
  color: rgba(255,255,255,.78);
}

/* ---- Narrative Frame ---- */
.narrative-grid {
  margin-top: 42px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.narrative-card {
  border-radius: 12px;
  padding: 28px 24px;
  background: #fff;
  border: 1px solid var(--dn-border);
  position: relative;
  overflow: hidden;
}
.narrative-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--dn-blue);
}
.narrative-card.green::before { background: var(--dn-green); }
.narrative-card.orange::before { background: var(--dn-orange); }
.narrative-card.pink::before { background: var(--dn-pink); }

.narrative-card .metric {
  font-family: var(--dn-font-display);
  font-size: 52px;
  line-height: 1;
  font-weight: 700;
  color: var(--dn-blue);
  margin-bottom: 14px;
}
.narrative-card.green .metric { color: var(--dn-green); }
.narrative-card.orange .metric { color: var(--dn-orange); }
.narrative-card.pink .metric { color: var(--dn-pink); }

.narrative-card h3 {
  font-size: 23px;
  line-height: 1.18;
  color: var(--dn-text);
  font-weight: 700;
  margin-bottom: 10px;
}
.narrative-card p {
  font-size: 17px;
  line-height: 1.35;
  color: var(--dn-text-secondary);
}

/* ---- Scenario ---- */
.scenario-head {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 40px;
  align-items: end;
}
.hardware-box {
  border-left: 5px solid var(--accent, var(--dn-blue));
  padding: 14px 0 14px 20px;
}
.hardware-box p {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--dn-text-secondary);
}
.hardware-box h3 {
  margin-top: 6px;
  font-size: 21px;
  line-height: 1.2;
  color: var(--dn-text);
  font-weight: 700;
}

.scenario-body {
  margin-top: 30px;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 18px;
}

.scenario-col {
  border-radius: 12px;
  padding: 24px 22px;
  position: relative;
}
.scenario-col h3 {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 16px;
  line-height: 1.2;
}
.scenario-col.tint {
  background: var(--soft, var(--dn-soft));
  border: 1px solid rgba(0,0,0,0.08);
}
.scenario-col.tint h3 {
  color: var(--dark, var(--dn-blue-dark));
}
.scenario-col.white {
  background: #fff;
  border: 1px solid var(--dn-border);
}
.scenario-col.white h3 {
  color: var(--dark, var(--dn-blue-dark));
}
.scenario-col.accent {
  background: var(--accent, var(--dn-blue));
  color: #fff;
}
.scenario-col.accent h3 {
  color: #fff;
}
.scenario-col.accent li {
  color: #fff;
}
.scenario-col.accent li::marker {
  color: rgba(255,255,255,0.7);
}

/* Accent-bar variant: white card with colored top bar */
.scenario-col.accent-bar {
  background: #fff;
  border: 1px solid var(--dn-border);
  overflow: hidden;
}
.scenario-col.accent-bar::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent, var(--dn-blue));
}
.scenario-col.accent-bar h3 {
  color: var(--accent, var(--dn-blue));
}
.scenario-col.accent-bar li {
  color: var(--dn-text);
}
.scenario-col.accent-bar li::marker {
  color: var(--accent, var(--dn-blue));
}

.scenario-col li {
  font-size: 16px;
  line-height: 1.32;
  margin-bottom: 8px;
}

/* Circular image placeholder (Danone template signature) */
.img-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--soft, var(--dn-soft));
  border: 3px solid var(--accent, var(--dn-blue));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--dn-text-secondary);
  text-align: center;
  overflow: hidden;
}
.img-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Quote / Core message block */
.quote-block {
  position: absolute;
  left: 72px;
  right: 72px;
  bottom: 56px;
  padding: 18px 0 18px 24px;
  border-left: 4px solid var(--accent, var(--dn-blue));
}
.quote-block::before {
  content: "\201C";
  position: absolute;
  left: -2px;
  top: -8px;
  font-family: Georgia, serif;
  font-size: 48px;
  line-height: 1;
  color: var(--accent, var(--dn-blue));
  opacity: 0.25;
}
.quote-block p {
  font-size: 24px;
  line-height: 1.3;
  font-weight: 600;
  color: var(--dn-text);
  font-style: italic;
}
.quote-block .quote-source {
  margin-top: 10px;
  font-size: 15px;
  font-weight: 500;
  color: var(--dn-text-secondary);
  font-style: normal;
}

/* ---- Showcase Flow ---- */
.flow-grid {
  margin-top: 36px;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}
.flow-step {
  min-height: 200px;
  border-top: 5px solid var(--dn-blue);
  background: var(--dn-soft);
  border-radius: 0 0 12px 12px;
  padding: 20px 16px;
  position: relative;
}
.flow-step .step-num {
  font-family: var(--dn-font-display);
  font-size: 42px;
  line-height: 1;
  font-weight: 700;
  color: var(--dn-blue);
}
.flow-step h3 {
  margin-top: 16px;
  font-size: 18px;
  line-height: 1.2;
  color: var(--dn-text);
  font-weight: 700;
}
.flow-step p {
  margin-top: 6px;
  font-size: 14px;
  line-height: 1.3;
  color: var(--dn-text-secondary);
}
.flow-arrow {
  position: absolute;
  right: -14px;
  top: 20px;
  width: 28px;
  height: 28px;
  z-index: 2;
}
.flow-arrow::before {
  content: "";
  position: absolute;
  inset: 0;
  background: var(--dn-blue);
  opacity: 0.15;
  border-radius: 50%;
}
.flow-arrow::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-40%, -50%);
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-left: 9px solid var(--dn-blue);
}

.closing-quote {
  position: absolute;
  left: 72px;
  right: 72px;
  bottom: 64px;
  font-size: 26px;
  line-height: 1.25;
  font-weight: 700;
  color: var(--dn-blue-dark);
}

/* ---- Thank You / Closing ---- */
.thankyou-slide {
  background: var(--dn-blue-dark);
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 28px;
}
.thankyou-slide .eyebrow {
  color: rgba(255,255,255,0.6);
}
.thankyou-slide h1 {
  font-family: var(--dn-font-display);
  font-size: 72px;
  line-height: 1.05;
  font-weight: 700;
  color: #fff;
}
.thankyou-slide .slogan {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.7);
}
.thankyou-slide .closing-msg {
  font-size: 22px;
  line-height: 1.4;
  color: rgba(255,255,255,0.8);
  max-width: 640px;
}

/* ---- Footer ---- */
.footer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 72px;
  border-top: 1px solid var(--dn-border);
}
.slide-blue .footer,
.thankyou-slide .footer {
  border-top: 1px solid rgba(255,255,255,0.15);
}
.footer-bar {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 4px;
  background: var(--accent, var(--dn-blue));
}
.footer p {
  font-size: 13px;
  line-height: 1;
  color: var(--dn-text-secondary);
}
.slide-blue .footer p,
.thankyou-slide .footer p {
  color: rgba(255,255,255,0.6);
}

/* Eyebrow */
.eyebrow {
  font-size: 14px;
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--dn-blue);
}

/* Title / Headline */
.title {
  margin-top: 16px;
  font-family: var(--dn-font-display);
  font-size: 48px;
  line-height: 1.06;
  font-weight: 700;
  color: var(--dn-text);
}
.headline {
  margin-top: 14px;
  font-family: var(--dn-font-display);
  font-size: 42px;
  line-height: 1.08;
  font-weight: 700;
  color: var(--dn-text);
}

/* Metric big number */
.metric {
  font-family: var(--dn-font-display);
  font-size: 48px;
  line-height: 1;
  font-weight: 700;
  color: var(--dn-blue);
}

/* ---- Photography Placeholder (Danone signature) ---- */
.photo-placeholder {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(105deg, rgba(0,94,184,0.90) 0%, rgba(0,94,184,0.65) 40%, rgba(0,94,184,0.20) 100%),
    linear-gradient(135deg, #003d7a 0%, #005EB8 40%, #0078d4 70%, #4aa3df 100%);
  z-index: 1;
}
.photo-placeholder::after {
  content: "";
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1280' height='720'%3E%3Crect fill='%23005EB8' width='1280' height='720'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='18' fill='rgba(255,255,255,0.25)'%3E[Photo: family / nature / health scene]%3C/text%3E%3C/svg%3E") center/cover no-repeat;
  opacity: 0.35;
}

/* ---- Circular Images (Danone signature) ---- */
.img-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--soft, var(--dn-soft));
  border: 3px solid var(--accent, var(--dn-blue));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--dn-text-secondary);
  text-align: center;
  overflow: hidden;
  flex-shrink: 0;
}
.img-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.img-circle-sm {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--soft, var(--dn-soft));
  border: 2px solid var(--accent, var(--dn-blue));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: var(--dn-text-secondary);
  text-align: center;
  overflow: hidden;
  flex-shrink: 0;
}

/* ---- Data Visualization Placeholders ---- */
.viz-metric {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 16px 0;
}
.viz-metric .number {
  font-family: var(--dn-font-display);
  font-size: 64px;
  line-height: 1;
  font-weight: 700;
  color: var(--accent, var(--dn-blue));
}
.viz-metric .unit {
  font-size: 20px;
  font-weight: 600;
  color: var(--dn-text-secondary);
}
.viz-bar {
  height: 28px;
  border-radius: 14px;
  background: var(--soft, var(--dn-soft));
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  margin: 8px 0;
  position: relative;
}
.viz-bar-fill {
  height: 100%;
  border-radius: 14px;
  background: var(--accent, var(--dn-blue));
  opacity: 0.85;
}
.viz-bar-label {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  font-weight: 600;
  color: var(--dn-text);
  mix-blend-mode: multiply;
}
.viz-ring {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(var(--accent, var(--dn-blue)) 0% 75%, var(--soft, var(--dn-soft)) 75% 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.viz-ring::before {
  content: "";
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fff;
}
.viz-ring-text {
  position: absolute;
  font-family: var(--dn-font-display);
  font-size: 26px;
  font-weight: 700;
  color: var(--accent, var(--dn-blue));
}

/* Photo strip (Danone signature element) */
.photo-strip {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}
.photo-strip .img-circle {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}
"""


@dataclass
class Scenario:
    number: str
    name: str
    target_users: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    hardware: str = ""
    objective: list[str] = field(default_factory=list)
    collected_data: list[str] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    core_message: str = ""
    shorthand: str = ""


def load_native_builder():
    script = Path(__file__).with_name("build_native_pptx.py")
    spec = importlib.util.spec_from_file_location("build_native_pptx", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_inline(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"[`*_]+", "", value)
    value = value.replace("insites", "insights")
    value = value.replace("Daone", "Danone")
    value = value.replace("coustomized", "customized")
    value = re.sub(r"\s+-\s*", " - ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_heading(value: str) -> str:
    value = clean_inline(value)
    value = re.sub(r"（.*?）", "", value)
    value = re.sub(r"\(.*?\)", "", value)
    return value.strip()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "slide"


def trim(value: str, limit: int = 170) -> str:
    value = clean_inline(value)
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def bullet_text(items: list[str], fallback: str = "待补充", max_items: int = 4) -> str:
    chosen = [trim(item, 120) for item in items if item][:max_items]
    return "\n".join(chosen or [fallback])


def compact_lines(items: list[str], fallback: str, max_items: int = 3, limit: int = 72) -> str:
    chosen = [trim(item, limit) for item in items if item][:max_items]
    return "\n".join(chosen or [fallback])


def split_scenario_blocks(markdown: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(r"^##\s*场景\s*(\d+)[｜|]\s*(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))
    blocks: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        blocks.append((match.group(1), normalize_heading(match.group(2)), markdown[start:end]))
    return blocks


def collect_list_after(block: str, heading_patterns: tuple[str, ...]) -> list[str]:
    lines = block.splitlines()
    items: list[str] = []
    collecting = False
    for raw in lines:
        line = raw.strip()
        if line.startswith("### "):
            heading = clean_inline(line[4:])
            collecting = any(re.search(pattern, heading, re.IGNORECASE) for pattern in heading_patterns)
            continue
        if collecting and line.startswith("- "):
            item = clean_inline(line[2:])
            if item in {"数据用于解释：", "根据："} or item.endswith("用于解释："):
                continue
            items.append(item)
    return items


def collect_hardware(block: str) -> str:
    lines = block.splitlines()
    for index, raw in enumerate(lines):
        if raw.strip().startswith("### Hardware"):
            for follow in lines[index + 1 : index + 6]:
                line = follow.strip()
                if line.startswith("### "):
                    break
                if line.startswith("**") and line.endswith("**"):
                    return clean_inline(line)
                if line and not line.startswith("- "):
                    return clean_inline(line)
    return "待补充硬件对象"


def collect_core_message(block: str) -> str:
    lines = block.splitlines()
    for index, raw in enumerate(lines):
        if raw.strip().startswith("### Core Message"):
            for follow in lines[index + 1 : index + 6]:
                line = follow.strip()
                if line.startswith(">"):
                    return clean_inline(line.lstrip("> "))
                if line.startswith("### "):
                    break
    return "待补充核心信息"


def parse_shorthands(markdown: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in markdown.splitlines():
        line = raw.strip("- \t")
        if "：" in line and "**" in line:
            left, right = line.split("：", 1)
            result[normalize_heading(left)] = clean_inline(right)
    return result


def parse_showcase_flow(markdown: str) -> list[str]:
    marker = "### Show Case"
    if marker not in markdown:
        return []
    tail = markdown.split(marker, 1)[1]
    items: list[str] = []
    for raw in tail.splitlines():
        match = re.match(r"\s*\d+[.\t ]+(.*)", raw)
        if match:
            items.append(clean_inline(match.group(1)))
    return items


def parse_notes(markdown: str) -> tuple[str, list[Scenario], list[str], str]:
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    title = clean_inline(title_match.group(1)) if title_match else "Danone Science Lab"
    shorthands = parse_shorthands(markdown)
    scenarios: list[Scenario] = []
    for number, name, block in split_scenario_blocks(markdown):
        scenario = Scenario(number=number, name=name)
        scenario.target_users = collect_list_after(block, ("target user", "目标用户"))
        scenario.pain_points = collect_list_after(block, ("pain points", "痛点"))
        scenario.hardware = collect_hardware(block)
        scenario.objective = collect_list_after(block, ("objective", "目的"))
        scenario.collected_data = collect_list_after(block, ("collected data", "采集"))
        scenario.indicators = collect_list_after(block, ("interpreted indicators", "指标"))
        scenario.products = collect_list_after(block, ("link to danone products", "产品"))
        scenario.core_message = collect_core_message(block)
        scenario.shorthand = shorthands.get(name, "")
        if not scenario.shorthand:
            for key, value in shorthands.items():
                if key in name or name in key:
                    scenario.shorthand = value
                    break
        scenarios.append(scenario)

    summary_match = re.search(r"### 总结一句\s*\n>\s*(.+)", markdown)
    summary = clean_inline(summary_match.group(1)) if summary_match else "Danone 不只是提供营养，而是让营养被数据证明。"
    return title, scenarios, parse_showcase_flow(markdown), summary


def plan_from_notes(title: str, scenarios: list[Scenario], showcase_flow: list[str], summary: str) -> list[dict]:
    if not scenarios:
        raise ValueError("No scenario sections found. Expected headings like '## 场景 1｜Gut Health'.")

    plan: list[dict] = [
        {
            "intent": "opening-cover",
            "content": {"title": "Danone Science Lab", "subtitle_or_date": "DHT Lab smoke deck"},
        },
        {
            "intent": "big-message",
            "content": {
                "headline": "Three measurable nutrition journeys",
                "supporting_text": " / ".join(
                    scenario.shorthand or scenario.name for scenario in scenarios[:3]
                ),
            },
        },
    ]
    for scenario in scenarios[:3]:
        plan.append(
            {
                "intent": "three-column",
                "content": {
                    "title": f"{scenario.name} — {trim(scenario.hardware, 80)}",
                    "column_1": "User pain point\n" + bullet_text(scenario.pain_points, "待补充用户痛点", 4),
                    "column_2": "Invisible data made visible\n" + bullet_text(scenario.indicators or scenario.collected_data, "待补充数据指标", 4),
                    "column_3": "Danone product link\n" + bullet_text(scenario.products, "待补充 Danone 产品", 3),
                },
            }
        )
    plan.append(
        {
            "intent": "closing",
            "content": {
                "title": "Make nutrition measurable, actionable, and personal.",
            },
        }
    )
    return plan


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render_bullets(items: list[str], fallback: str = "待补充", limit: int = 4) -> str:
    chosen = [item for item in items if item][:limit] or [fallback]
    return "\n".join(f"<li>{esc(trim(item, 120))}</li>" for item in chosen)


def slide_shell(title: str, body: str, extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Inter+Tight:wght@600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../shared/tokens.css">
<style>{extra_css}</style>
</head>
<body class="pptx-canvas">
{body}
</body>
</html>
"""


def render_cover(title: str, summary: str, scenarios: list[Scenario], total: int = 7, brand_line: str = "Danone Science Lab") -> str:
    chips = ""
    theme_classes = ["green", "orange", "pink"]
    chip_imgs = ["Family", "Sport", "Medical"]
    for i, s in enumerate(scenarios[:3]):
        cls = theme_classes[i] if i < len(theme_classes) else ""
        img_label = chip_imgs[i] if i < len(chip_imgs) else "Photo"
        chips += f"""<div class="chip">
      <div style="display:flex;align-items:center;gap:16px;">
        <div class="img-circle-sm" style="--accent:var(--dn-{cls if cls else 'blue'});--soft:var(--dn-{cls if cls else 'blue'}-soft)">
          <span>{img_label}</span>
        </div>
        <div>
          <p class="chip-label">Scenario 0{s.number}</p>
          <p class="chip-title">{esc(s.name)}</p>
        </div>
      </div>
      <p class="chip-desc">{esc(s.shorthand or s.core_message)}</p>
    </div>"""

    body = f"""<main class="slide slide-blue">
  <div class="cover-bg"></div>
  <div class="photo-placeholder"></div>
  <div class="cover-content">
    <div class="cover-left">
      <p class="cover-slogan">One Planet. One Health</p>
      <h1 class="cover-title">{esc(title)}</h1>
      <p class="cover-copy">{esc(summary)}</p>
    </div>
    <div class="cover-right">{chips}</div>
  </div>
  <div class="footer"><p>{esc(brand_line)}</p><p>01 / {total:02d}</p></div>
</main>"""
    return slide_shell("01 Cover", body)


def render_summary(summary: str, scenarios: list[Scenario], total: int = 7) -> str:
    theme_classes = ["green", "orange", "pink"]
    card_imgs = ["Gut", "Sport", "Clinic"]
    metrics = ["87%", "92%", "78%"]
    metric_labels = ["Gut Health Score", "Hydration Match", "Recovery Rate"]
    cards = ""
    for i, s in enumerate(scenarios[:3]):
        cls = theme_classes[i] if i < len(theme_classes) else ""
        img_label = card_imgs[i] if i < len(card_imgs) else "Icon"
        metric = metrics[i] if i < len(metrics) else "--"
        metric_label = metric_labels[i] if i < len(metric_labels) else "Metric"
        cards += f"""<div class="narrative-card {cls}">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <p class="metric">0{s.number}</p>
        <div class="img-circle-sm" style="--accent:var(--dn-{cls if cls else 'blue'});--soft:var(--dn-{cls if cls else 'blue'}-soft)"><span>{img_label}</span></div>
      </div>
      <h3>{esc(s.name)}</h3>
      <p>{esc(s.shorthand or s.core_message)}</p>
      <div class="viz-metric" style="margin-top:18px;">
        <span class="number" style="color:var(--dn-{cls if cls else 'blue'})">{metric}</span>
        <span class="unit">{metric_label}</span>
      </div>
    </div>"""

    body = f"""<main class="slide">
  <p class="eyebrow">Narrative Frame</p>
  <h2 class="title">{esc(summary)}</h2>
  <div class="narrative-grid">{cards}</div>
  <div class="footer"><p>Unified Story &middot; One Planet. One Health</p><p>02 / {total:02d}</p></div>
</main>"""
    return slide_shell("02 Narrative Frame", body)


def render_scenario(index: int, scenario: Scenario, total: int = 7) -> str:
    theme = pick_theme(scenario.name)
    accent = theme["accent"]
    soft = theme["soft"]
    dark = theme["dark"]

    # Use indicators if available, otherwise collected_data
    data_items = scenario.indicators if scenario.indicators else scenario.collected_data

    # Data viz bars (one per data item, deterministic widths based on index)
    viz_bars = ""
    bar_widths = [75, 60, 85, 50]
    for idx, item in enumerate(data_items[:4]):
        width = bar_widths[idx % len(bar_widths)]
        viz_bars += f"""<div class="viz-bar">
        <div class="viz-bar-fill" style="width:{width}%;background:{accent}"></div>
        <span class="viz-bar-label">{esc(trim(item, 40))}</span>
      </div>"""

    # Ring chart placeholder
    ring_pct = 75 + (index * 7) % 20

    body = f"""<main class="slide scenario" style="--accent:{accent};--soft:{soft};--dark:{dark}">
  <div class="scenario-head">
    <div>
      <p class="eyebrow" style="color:{accent}">Scenario 0{scenario.number}</p>
      <h2 class="headline">{esc(scenario.name)}</h2>
    </div>
    <div style="display:flex;align-items:center;gap:18px;">
      <div class="img-circle" style="--accent:{accent};--soft:{soft}"><span>Device<br>Photo</span></div>
      <div class="hardware-box">
        <p>Hardware Object</p>
        <h3>{esc(scenario.hardware)}</h3>
      </div>
    </div>
  </div>
  <div class="scenario-body">
    <section class="scenario-col tint">
      <h3>User Pain Point</h3>
      <ul>{render_bullets(scenario.pain_points, "待补充用户痛点", 4)}</ul>
      <div style="margin-top:18px;display:flex;gap:10px;align-items:center;">
        <div class="viz-ring" style="--accent:{accent};--soft:{soft}">
          <span class="viz-ring-text" style="color:{accent}">{ring_pct}%</span>
        </div>
        <p style="font-size:13px;color:var(--dn-text-secondary);line-height:1.3;">Patient-reported concern match rate</p>
      </div>
    </section>
    <section class="scenario-col white">
      <h3>Invisible Data Made Visible</h3>
      {viz_bars}
    </section>
    <section class="scenario-col white accent-bar">
      <h3>Danone Product Link</h3>
      <ul>{render_bullets(scenario.products, "待补充 Danone 产品", 3)}</ul>
      <div class="photo-strip" style="margin-top:14px;">
        <div class="img-circle-sm" style="--accent:{accent};--soft:{soft}"><span>Prod</span></div>
        <div class="img-circle-sm" style="--accent:{accent};--soft:{soft}"><span>Pack</span></div>
      </div>
    </section>
  </div>
  <div class="quote-block">
    <p>&ldquo;{esc(scenario.core_message)}&rdquo;</p>
    <p class="quote-source">{esc(scenario.shorthand or scenario.name)}</p>
  </div>
  <div class="footer-bar" style="background:{accent}"></div>
  <div class="footer"><p>{esc(scenario.shorthand or scenario.name)}</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(f"{index:02d} {scenario.name}", body)


def render_flow(showcase_flow: list[str], summary: str, index: int = 6, total: int = 7) -> str:
    items = showcase_flow[:5] or [
        "Why we measure",
        "How we see the invisible",
        "What the body is telling you",
        "What you can do next",
        "What you take home",
    ]
    steps = ""
    for i, item in enumerate(items, start=1):
        arrow = '<div class="flow-arrow"></div>' if i < len(items) else ""
        steps += f"""<div class="flow-step">
      {arrow}
      <p class="step-num">{i:02d}</p>
      <h3>{esc(item)}</h3>
    </div>"""

    body = f"""<main class="slide">
  <p class="eyebrow">Showcase Structure</p>
  <h2 class="title">From Measurement to a Personalized Danone Journey</h2>
  <div class="flow-grid">{steps}</div>
  <p class="closing-quote">{esc(summary)}</p>
  <div class="footer"><p>Exhibition Flow &middot; One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("06 Showcase Flow", body)


def render_thankyou(summary: str, index: int = 7, total: int = 7, brand_line: str = "Danone Science Lab") -> str:
    body = f"""<main class="slide thankyou-slide">
  <p class="eyebrow">Danone Science Lab</p>
  <h1>Thank You</h1>
  <p class="slogan">One Planet. One Health</p>
  <p class="closing-msg">{esc(summary)}</p>
  <div class="footer"><p>{esc(brand_line)}</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("07 Thank You", body)


def render_index(title: str, manifest: list[dict]) -> str:
    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{esc(title)}</title>
<script>
  window.DECK_MANIFEST = {manifest_json};
  window.DECK_WIDTH = 1280;
  window.DECK_HEIGHT = 720;
</script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ height: 100%; background: #0a1628; overflow: hidden; font-family: -apple-system, "PingFang SC", sans-serif; }}
  #stage {{ position: fixed; top: 0; left: 0; transform-origin: top left; background: #fff; box-shadow: 0 4px 24px rgba(0,0,0,0.25); border-radius: 4px; }}
  iframe {{ width: 100%; height: 100%; border: 0; display: block; background: #fff; }}
  .counter {{ position: fixed; bottom: 18px; right: 18px; background: rgba(0,0,0,0.55); color: #fff; padding: 6px 14px; border-radius: 999px; font-size: 13px; z-index: 100; }}
  .counter .label {{ color: rgba(255,255,255,0.72); margin-left: 8px; }}
  .nav-zone {{ position: fixed; top: 0; bottom: 0; width: 15%; cursor: pointer; z-index: 50; }}
  .nav-zone.left {{ left: 0; }}
  .nav-zone.right {{ right: 0; }}
</style>
</head>
<body>
<div id="stage"><iframe id="frame" src="about:blank"></iframe></div>
<div class="nav-zone left" id="navL"></div>
<div class="nav-zone right" id="navR"></div>
<div class="counter" id="counter">1 / {len(manifest)}</div>
<script>
(function () {{
  const W = window.DECK_WIDTH;
  const H = window.DECK_HEIGHT;
  const deck = window.DECK_MANIFEST;
  const stage = document.getElementById('stage');
  const frame = document.getElementById('frame');
  const counter = document.getElementById('counter');
  let current = 0;
  stage.style.width = W + 'px';
  stage.style.height = H + 'px';
  function fit() {{
    const s = Math.min(window.innerWidth / W, window.innerHeight / H);
    const x = (window.innerWidth - W * s) / 2;
    const y = (window.innerHeight - H * s) / 2;
    stage.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(' + s + ')';
  }}
  function show(idx) {{
    if (idx < 0 || idx >= deck.length) return;
    current = idx;
    frame.src = deck[idx].file;
    counter.innerHTML = (idx + 1) + ' / ' + deck.length + '<span class="label">' + deck[idx].label + '</span>';
    history.replaceState(null, '', '#' + (idx + 1));
  }}
  function next() {{ show(Math.min(current + 1, deck.length - 1)); }}
  function prev() {{ show(Math.max(current - 1, 0)); }}
  document.addEventListener('keydown', function (e) {{
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{ e.preventDefault(); next(); }}
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); prev(); }}
    if (e.key === 'Home') {{ e.preventDefault(); show(0); }}
    if (e.key === 'End') {{ e.preventDefault(); show(deck.length - 1); }}
  }});
  document.getElementById('navL').addEventListener('click', prev);
  document.getElementById('navR').addEventListener('click', next);
  window.addEventListener('resize', fit);
  fit();
  const hash = location.hash.match(/^#(\\d+)$/);
  show(hash ? Math.max(0, Math.min(deck.length - 1, parseInt(hash[1], 10) - 1)) : 0);
}})();
</script>
</body>
</html>
"""


def write_html_deck(out_dir: Path, title: str, scenarios: list[Scenario], showcase_flow: list[str], summary: str, brand_line: str = "Danone Science Lab") -> None:
    slides_dir = out_dir / "slides"
    shared_dir = out_dir / "shared"
    slides_dir.mkdir(parents=True, exist_ok=True)
    shared_dir.mkdir(parents=True, exist_ok=True)
    token_css = DEFAULT_TOKENS.read_text(encoding="utf-8")
    (shared_dir / "tokens.css").write_text(token_css + "\n" + BASE_COMPONENT_CSS, encoding="utf-8")

    total_slides = 2 + min(len(scenarios), 3) + 2  # cover + narrative + scenarios + flow + thankyou

    pages = [
        ("01-cover.html", "Cover", render_cover(title, summary, scenarios, total=total_slides, brand_line=brand_line)),
        ("02-narrative-frame.html", "Narrative", render_summary(summary, scenarios, total=total_slides)),
    ]
    for offset, scenario in enumerate(scenarios[:3], start=3):
        pages.append((f"{offset:02d}-{slugify(scenario.name)}.html", scenario.name, render_scenario(offset, scenario, total=total_slides)))
    pages.append(("06-showcase-flow.html", "Showcase Flow", render_flow(showcase_flow, summary, index=6, total=total_slides)))
    pages.append(("07-thank-you.html", "Thank You", render_thankyou(summary, index=7, total=total_slides, brand_line=brand_line)))

    for filename, _label, content in pages:
        (slides_dir / filename).write_text(content, encoding="utf-8")
    manifest = [{"file": f"slides/{filename}", "label": label} for filename, label, _content in pages]
    (out_dir / "index.html").write_text(render_index(title, manifest), encoding="utf-8")


def build_deck(
    notes_file: str | Path,
    out_dir: str | Path,
    native_pptx: str | Path | None = None,
    out_plan: str | Path | None = None,
    template: str | Path = DEFAULT_TEMPLATE,
    layout_map: str | Path = DEFAULT_LAYOUT_MAP,
    brand_line: str = "Danone Science Lab",
) -> dict:
    markdown = Path(notes_file).read_text(encoding="utf-8")
    title, scenarios, showcase_flow, summary = parse_notes(markdown)
    plan = plan_from_notes(title, scenarios, showcase_flow, summary)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_html_deck(out_dir, title, scenarios, showcase_flow, summary, brand_line=brand_line)
    if out_plan is not None:
        out_plan = Path(out_plan)
        out_plan.parent.mkdir(parents=True, exist_ok=True)
        out_plan.write_text(json.dumps({"slides": plan}, ensure_ascii=False, indent=2), encoding="utf-8")
    if native_pptx is not None:
        builder = load_native_builder()
        builder.build_presentation(template, layout_map, plan, native_pptx)
    return {"title": title, "scenario_count": len(scenarios), "slide_count": 7, "plan": plan}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Danone HTML and native PPTX assets from structured slide notes.")
    parser.add_argument("--notes", required=True, help="Structured Markdown notes file")
    parser.add_argument("--out-dir", required=True, help="Output deck directory containing index.html and slides/")
    parser.add_argument("--native-pptx", help="Optional native editable PPTX output path")
    parser.add_argument("--out-plan", help="Optional native JSON plan output path")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    parser.add_argument("--layout-map", default=str(DEFAULT_LAYOUT_MAP))
    parser.add_argument("--brand-line", default="Danone Science Lab", help="Footer brand line (e.g. 'Brand X · Danone')")
    args = parser.parse_args()
    result = build_deck(
        notes_file=args.notes,
        out_dir=args.out_dir,
        native_pptx=args.native_pptx,
        out_plan=args.out_plan,
        template=args.template,
        layout_map=args.layout_map,
        brand_line=args.brand_line,
    )
    print(f"Wrote {args.out_dir} ({result['slide_count']} HTML slides, {result['scenario_count']} scenarios)")
    if args.native_pptx:
        print(f"Wrote {args.native_pptx} ({len(result['plan'])} native slides)")
    if args.out_plan:
        print(f"Wrote {args.out_plan}")


if __name__ == "__main__":
    main()
