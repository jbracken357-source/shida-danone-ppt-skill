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

BASE_COMPONENT_CSS = """
:root {
  --dn-font: "Microsoft YaHei", "Arial", sans-serif;
  --dn-font-display: "Microsoft YaHei", "Arial", sans-serif;
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
  font-size: 22px;
  line-height: 1.32;
  color: var(--dn-text);
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

.eyebrow {
  font-size: 17px;
  line-height: 1.2;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--dn-blue);
}

.slide-blue .eyebrow,
.slide-blue .footer p {
  color: rgba(255,255,255,0.78);
}

.title {
  margin-top: 18px;
  font-family: var(--dn-font-display);
  font-size: 54px;
  line-height: 1.04;
  font-weight: 700;
  color: var(--dn-text);
}

.headline {
  margin-top: 16px;
  font-family: var(--dn-font-display);
  font-size: 46px;
  line-height: 1.05;
  font-weight: 700;
  color: var(--dn-text);
}

.footer {
  position: absolute;
  left: 72px;
  right: 72px;
  bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer p {
  font-size: 13px;
  line-height: 1;
  color: var(--dn-text-secondary);
}

.card,
.tint-card,
.blue-card {
  border-radius: 8px;
  padding: 24px;
}

.card {
  background: #fff;
  border: 1px solid var(--dn-border);
}

.tint-card {
  background: #F4F8FC;
  border: 1px solid #D6E6F5;
}

.blue-card {
  background: var(--dn-blue);
}

.blue-card h3,
.blue-card p,
.blue-card li {
  color: #fff;
}

.metric {
  font-family: var(--dn-font-display);
  font-size: 46px;
  line-height: 1;
  font-weight: 700;
  color: var(--dn-blue);
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
                "intent": "two-column",
                "content": {
                    "title": f"{scenario.name}: {scenario.shorthand or scenario.core_message}",
                    "left_content": "\n".join(
                        [
                            f"Hardware: {scenario.hardware}",
                            compact_lines(scenario.pain_points, "待补充用户痛点", 2),
                        ]
                    ),
                    "right_content": "\n".join(
                        [
                            compact_lines(scenario.indicators or scenario.collected_data, "待补充数据指标", 3),
                            f"Product: {compact_lines(scenario.products, '待补充 Danone 产品', 1)}",
                        ]
                    ),
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


def render_cover(title: str, summary: str, scenarios: list[Scenario]) -> str:
    chips = "".join(
        f"<div class=\"chip\"><p>{esc(s.name)}</p><p>{esc(s.shorthand or s.core_message)}</p></div>"
        for s in scenarios[:3]
    )
    body = f"""<main class="slide slide-blue cover-grid">
  <section>
    <p class="eyebrow">Danone Science Lab</p>
    <h1 class="cover-title">{esc(title)}</h1>
    <p class="cover-copy">{esc(summary)}</p>
  </section>
  <aside class="signal-panel">{chips}</aside>
  <div class="footer"><p>DHT Lab smoke</p><p>01 / 06</p></div>
</main>"""
    css = """
  .cover-grid { display: grid; grid-template-columns: 1.12fr .88fr; gap: 56px; align-items: center; }
  .cover-title { margin-top: 22px; font-family: var(--dn-font-display); font-size: 58px; line-height: 1.03; font-weight: 700; color: #fff; }
  .cover-copy { margin-top: 28px; font-size: 28px; line-height: 1.28; color: #fff; }
  .signal-panel { display: grid; gap: 16px; }
  .chip { border: 1px solid rgba(255,255,255,.36); border-radius: 8px; padding: 20px; background: rgba(255,255,255,.08); }
  .chip p:first-child { font-size: 21px; font-weight: 700; color: #fff; }
  .chip p:last-child { margin-top: 8px; font-size: 17px; line-height: 1.3; color: rgba(255,255,255,.82); }
"""
    return slide_shell("01 Cover", body, css)


def render_summary(summary: str, scenarios: list[Scenario]) -> str:
    cards = "".join(
        f"""<div class="card">
      <p class="metric">0{s.number}</p>
      <h3>{esc(s.name)}</h3>
      <p>{esc(s.shorthand or s.core_message)}</p>
    </div>"""
        for s in scenarios[:3]
    )
    body = f"""<main class="slide">
  <p class="eyebrow">Narrative frame</p>
  <h2 class="title">{esc(summary)}</h2>
  <div class="summary-grid">{cards}</div>
  <div class="footer"><p>Unified story</p><p>02 / 06</p></div>
</main>"""
    css = """
  .summary-grid { margin-top: 48px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  .card h3 { margin-top: 18px; font-size: 24px; line-height: 1.18; color: var(--dn-blue-dark); }
  .card p:last-child { margin-top: 14px; font-size: 18px; line-height: 1.35; color: var(--dn-text-secondary); }
"""
    return slide_shell("02 Narrative Frame", body, css)


def render_scenario(index: int, scenario: Scenario, total: int = 6) -> str:
    body = f"""<main class="slide scenario">
  <div class="scenario-head">
    <div>
      <p class="eyebrow">Scenario 0{scenario.number}</p>
      <h2 class="headline">{esc(scenario.name)}</h2>
    </div>
    <div class="hardware-box">
      <p>Hardware object</p>
      <h3>{esc(scenario.hardware)}</h3>
    </div>
  </div>
  <div class="scenario-grid">
    <section class="tint-card">
      <h3>User pain point</h3>
      <ul>{render_bullets(scenario.pain_points, "待补充用户痛点", 4)}</ul>
    </section>
    <section class="card">
      <h3>Invisible data made visible</h3>
      <ul>{render_bullets(scenario.collected_data, "待补充采集数据", 4)}</ul>
    </section>
    <section class="blue-card">
      <h3>Danone product link</h3>
      <ul>{render_bullets(scenario.products, "待补充 Danone 产品", 3)}</ul>
    </section>
  </div>
  <p class="core-message">{esc(scenario.core_message)}</p>
  <div class="footer"><p>{esc(scenario.shorthand or scenario.name)}</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    css = """
  .scenario-head { display: grid; grid-template-columns: 1fr 360px; gap: 32px; align-items: end; }
  .hardware-box { border-left: 5px solid var(--dn-blue); padding: 16px 0 16px 22px; }
  .hardware-box p { font-size: 15px; color: var(--dn-text-secondary); }
  .hardware-box h3 { margin-top: 8px; font-size: 23px; line-height: 1.18; color: var(--dn-blue-dark); }
  .scenario-grid { margin-top: 34px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  .scenario-grid h3 { font-size: 22px; line-height: 1.2; margin-bottom: 18px; color: var(--dn-blue-dark); }
  .blue-card h3 { color: #fff; }
  .scenario-grid li { font-size: 17px; line-height: 1.32; margin-bottom: 9px; }
  .core-message { position: absolute; left: 72px; right: 72px; bottom: 60px; font-size: 25px; line-height: 1.25; font-weight: 600; color: var(--dn-blue-dark); }
"""
    return slide_shell(f"{index:02d} {scenario.name}", body, css)


def render_flow(showcase_flow: list[str], summary: str) -> str:
    items = showcase_flow[:5] or [
        "Why we measure",
        "How we see the invisible",
        "What the body is telling you",
        "What you can do next",
        "What you take home",
    ]
    steps = "".join(
        f"""<div class="flow-step">
      <p class="metric">{i:02d}</p>
      <h3>{esc(item)}</h3>
    </div>"""
        for i, item in enumerate(items, start=1)
    )
    body = f"""<main class="slide">
  <p class="eyebrow">Showcase structure</p>
  <h2 class="title">From measurement to a personalized Danone journey</h2>
  <div class="flow">{steps}</div>
  <p class="closing-line">{esc(summary)}</p>
  <div class="footer"><p>Exhibition flow</p><p>06 / 06</p></div>
</main>"""
    css = """
  .flow { margin-top: 40px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
  .flow-step { min-height: 210px; border-top: 5px solid var(--dn-blue); background: var(--dn-soft); padding: 22px 18px; }
  .flow-step h3 { margin-top: 24px; font-size: 20px; line-height: 1.18; color: var(--dn-blue-dark); }
  .closing-line { position: absolute; left: 72px; right: 72px; bottom: 72px; font-size: 28px; line-height: 1.22; font-weight: 700; color: var(--dn-blue-dark); }
"""
    return slide_shell("06 Showcase Flow", body, css)


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
  html, body {{ height: 100%; background: #f5f7fa; overflow: hidden; font-family: -apple-system, "PingFang SC", sans-serif; }}
  #stage {{ position: fixed; top: 0; left: 0; transform-origin: top left; background: #fff; box-shadow: 0 4px 24px rgba(0,0,0,0.1); border-radius: 4px; }}
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


def write_html_deck(out_dir: Path, title: str, scenarios: list[Scenario], showcase_flow: list[str], summary: str) -> None:
    slides_dir = out_dir / "slides"
    shared_dir = out_dir / "shared"
    slides_dir.mkdir(parents=True, exist_ok=True)
    shared_dir.mkdir(parents=True, exist_ok=True)
    token_css = DEFAULT_TOKENS.read_text(encoding="utf-8")
    (shared_dir / "tokens.css").write_text(token_css + "\n" + BASE_COMPONENT_CSS, encoding="utf-8")

    pages = [
        ("01-cover.html", "Cover", render_cover(title, summary, scenarios)),
        ("02-narrative-frame.html", "Narrative", render_summary(summary, scenarios)),
    ]
    for offset, scenario in enumerate(scenarios[:3], start=3):
        pages.append((f"{offset:02d}-{slugify(scenario.name)}.html", scenario.name, render_scenario(offset, scenario)))
    pages.append(("06-showcase-flow.html", "Showcase Flow", render_flow(showcase_flow, summary)))

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
) -> dict:
    markdown = Path(notes_file).read_text(encoding="utf-8")
    title, scenarios, showcase_flow, summary = parse_notes(markdown)
    plan = plan_from_notes(title, scenarios, showcase_flow, summary)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_html_deck(out_dir, title, scenarios, showcase_flow, summary)
    if out_plan is not None:
        out_plan = Path(out_plan)
        out_plan.parent.mkdir(parents=True, exist_ok=True)
        out_plan.write_text(json.dumps({"slides": plan}, ensure_ascii=False, indent=2), encoding="utf-8")
    if native_pptx is not None:
        builder = load_native_builder()
        builder.build_presentation(template, layout_map, plan, native_pptx)
    return {"title": title, "scenario_count": len(scenarios), "slide_count": 6, "plan": plan}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Danone HTML and native PPTX assets from structured slide notes.")
    parser.add_argument("--notes", required=True, help="Structured Markdown notes file")
    parser.add_argument("--out-dir", required=True, help="Output deck directory containing index.html and slides/")
    parser.add_argument("--native-pptx", help="Optional native editable PPTX output path")
    parser.add_argument("--out-plan", help="Optional native JSON plan output path")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    parser.add_argument("--layout-map", default=str(DEFAULT_LAYOUT_MAP))
    args = parser.parse_args()
    result = build_deck(
        notes_file=args.notes,
        out_dir=args.out_dir,
        native_pptx=args.native_pptx,
        out_plan=args.out_plan,
        template=args.template,
        layout_map=args.layout_map,
    )
    print(f"Wrote {args.out_dir} ({result['slide_count']} HTML slides, {result['scenario_count']} scenarios)")
    if args.native_pptx:
        print(f"Wrote {args.native_pptx} ({len(result['plan'])} native slides)")
    if args.out_plan:
        print(f"Wrote {args.out_plan}")


if __name__ == "__main__":
    main()
