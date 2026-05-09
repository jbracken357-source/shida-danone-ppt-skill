#!/usr/bin/env python
"""Create a Danone native PPTX deck from a short task/material brief."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = ROOT / "Danone Real Templates" / "Standard Danone Template.pptx"
DEFAULT_LAYOUT_MAP = ROOT / "templates" / "layout-map.json"


def load_native_builder():
    script = Path(__file__).with_name("build_native_pptx.py")
    spec = importlib.util.spec_from_file_location("build_native_pptx", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def brief_lines(brief: str) -> list[str]:
    lines = []
    for raw in re.split(r"[\n;]+", brief):
        line = clean_text(raw.strip(" -\t"))
        if line:
            lines.append(line)
    if not lines:
        return ["待补充：请添加材料要点、数据或任务目标。"]
    return lines


def find_labeled_value(lines: list[str], labels: tuple[str, ...]) -> str:
    for line in lines:
        lower = line.lower()
        for label in labels:
            if lower.startswith(label):
                return clean_text(re.sub(r"^[^:：]+[:：]\s*", "", line))
    return ""


def collect_metric_lines(lines: list[str]) -> list[str]:
    metrics = []
    for line in lines:
        if re.search(r"\d|%|倍|天|周|月|year|month|week|day", line, re.IGNORECASE):
            metrics.append(line)
    return metrics


def trim(value: str, limit: int = 220) -> str:
    value = clean_text(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def bullets(items: list[str], fallback: str, max_items: int = 4) -> str:
    chosen = [trim(item, 120) for item in items if item][:max_items]
    if not chosen:
        chosen = [fallback]
    return "\n".join(chosen)


def plan_from_brief(title: str, brief: str, slide_count: int = 6) -> list[dict]:
    """Convert user-provided material into a conservative native slide plan."""
    if slide_count < 3:
        raise ValueError("slide_count must be at least 3")

    title = clean_text(title) or "Danone corporate presentation"
    lines = brief_lines(brief)
    audience = find_labeled_value(lines, ("audience", "受众", "对象"))
    goal = find_labeled_value(lines, ("goal", "objective", "目的", "目标"))
    next_step = find_labeled_value(lines, ("next step", "ask", "行动", "下一步"))
    metrics = collect_metric_lines(lines)

    context_lines = [line for line in lines if line not in metrics]
    body_summary = bullets(context_lines, "待补充：核心背景、业务问题和约束。")
    metric_summary = bullets(metrics, "待补充：关键数据、指标或事实证据。")
    decision_ask = next_step or "待补充：最终决策请求或下一步行动。"
    strategic_goal = goal or context_lines[0]
    audience_note = f"Audience: {audience}" if audience else "Audience: 待补充"

    plan: list[dict] = [
        {
            "intent": "opening-cover",
            "content": {
                "title": title,
                "subtitle_or_date": audience_note,
            },
        }
    ]

    middle_slots = slide_count - 2
    middle_templates = [
        {
            "intent": "big-message",
            "content": {
                "headline": trim(strategic_goal, 120),
                "supporting_text": body_summary,
            },
        },
        {
            "intent": "two-column",
            "content": {
                "title": "Situation and implication",
                "left_content": body_summary,
                "right_content": metric_summary,
            },
        },
        {
            "intent": "chart-or-table",
            "content": {
                "title": "Evidence and quality gates",
                "chart_or_table": metric_summary,
                "insight": decision_ask,
            },
        },
        {
            "intent": "contents",
            "content": {
                "title": "Discussion flow",
                "agenda_items": ["Context", "Evidence", "Operating model", "Decision ask"],
            },
        },
        {
            "intent": "two-column",
            "content": {
                "title": "Operating model",
                "left_content": bullets(context_lines[:2], "待补充：工作流和职责边界。", 3),
                "right_content": decision_ask,
            },
        },
    ]
    plan.extend(middle_templates[:middle_slots])
    while len(plan) < slide_count - 1:
        plan.append(middle_templates[(len(plan) - 1) % len(middle_templates)])

    plan.append(
        {
            "intent": "closing",
            "content": {
                "title": decision_ask,
            },
        }
    )
    return plan[:slide_count]


def build_from_brief(
    title: str,
    brief: str,
    out_pptx: str | Path,
    out_plan: str | Path | None = None,
    slide_count: int = 6,
    template: str | Path = DEFAULT_TEMPLATE,
    layout_map: str | Path = DEFAULT_LAYOUT_MAP,
) -> list[dict]:
    plan = plan_from_brief(title, brief, slide_count=slide_count)
    out_pptx = Path(out_pptx)
    if out_plan is not None:
        out_plan = Path(out_plan)
        out_plan.parent.mkdir(parents=True, exist_ok=True)
        out_plan.write_text(json.dumps({"slides": plan}, ensure_ascii=False, indent=2), encoding="utf-8")

    builder = load_native_builder()
    builder.build_presentation(template, layout_map, plan, out_pptx)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a native editable Danone PPTX from a task/material brief.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--brief", help="Brief text. Use --brief-file for longer material.")
    parser.add_argument("--brief-file", help="UTF-8 text/markdown file containing the material brief.")
    parser.add_argument("--slides", type=int, default=6)
    parser.add_argument("--out", required=True, help="Output native .pptx path")
    parser.add_argument("--out-plan", help="Optional generated JSON plan path")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    parser.add_argument("--layout-map", default=str(DEFAULT_LAYOUT_MAP))
    args = parser.parse_args()

    if args.brief_file:
        brief = Path(args.brief_file).read_text(encoding="utf-8")
    elif args.brief:
        brief = args.brief
    else:
        raise SystemExit("Provide --brief or --brief-file")

    plan = build_from_brief(
        title=args.title,
        brief=brief,
        out_pptx=args.out,
        out_plan=args.out_plan,
        slide_count=args.slides,
        template=args.template,
        layout_map=args.layout_map,
    )
    print(f"Wrote {args.out} ({len(plan)} native slides) from brief")
    if args.out_plan:
        print(f"Wrote {args.out_plan}")


if __name__ == "__main__":
    main()
