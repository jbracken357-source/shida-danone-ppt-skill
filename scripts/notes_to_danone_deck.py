#!/usr/bin/env python
"""Build a Danone smoke deck from structured Markdown slide notes."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


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
    "water": {
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


def pick_theme(scenario_name: str) -> dict:
    """Map scenario name to theme colorway."""
    name = scenario_name.lower()
    if any(k in name for k in ("gut", "肠道", "digest", "microbiome")):
        return THEMES["gut"]
    if any(k in name for k in ("clinical", "tube", "medical", "nutrison", "管饲", "康复")):
        return THEMES["clinical"]
    if any(k in name for k in ("水", "hydration", "water", "汗液", "sport", "physical", "运动", "recovery")):
        return THEMES["water"]
    return DEFAULT_THEME


BASE_COMPONENT_CSS = """
:root {
  --dn-font: "Inter", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  --dn-font-display: "Playfair Display", "Noto Sans SC", "PingFang SC", serif;
  --dn-font-mono: "IBM Plex Mono", "SF Mono", "Consolas", monospace;
  font-feature-settings: "tnum";
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

.slide-dark {
  background: var(--dn-blue-dark);
  color: #fff;
}
.slide-dark .eyebrow { color: rgba(255,255,255,0.6); }
.slide-dark .title { color: #fff; }
.slide-dark .headline { color: #fff; }
.slide-dark li { color: rgba(255,255,255,0.85); }
.slide-dark li::marker { color: rgba(255,255,255,0.5); }
.slide-dark .footer { border-top-color: rgba(255,255,255,0.12); }
.slide-dark .footer p { color: rgba(255,255,255,0.5); }
.slide-dark .narrative-card {
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.1);
}
.slide-dark .narrative-card h3 { color: #fff; }
.slide-dark .narrative-card p { color: rgba(255,255,255,0.7); }

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
  letter-spacing: -0.01em;
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

/* ---- Opening Slide Title (Cover) ---- */
.opening-slide {
  background: var(--dn-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.opening-circle {
  width: 600px;
  height: 600px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 80px 100px;
  text-align: center;
}
.opening-subtitle {
  font-size: 18px;
  color: var(--dn-text);
  font-weight: 400;
  margin-bottom: 40px;
  letter-spacing: 0.5px;
}
.opening-title {
  font-family: var(--dn-font-display);
  font-size: 48px;
  font-weight: 700;
  color: var(--dn-blue);
  line-height: 1.2;
  letter-spacing: -0.01em;
}
.opening-logo {
  position: absolute;
  bottom: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.opening-logo-text {
  font-size: 28px;
  font-weight: 800;
  color: var(--dn-blue);
  letter-spacing: 4px;
}
.opening-logo-sub {
  font-size: 11px;
  color: var(--dn-teal);
  font-weight: 600;
  letter-spacing: 2px;
}

/* ---- Closing Slide Title (Thank You) ---- */
.closing-slide {
  background: var(--dn-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.closing-circle {
  width: 600px;
  height: 600px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 80px 100px;
  text-align: center;
}
.closing-title {
  font-family: var(--dn-font-display);
  font-size: 56px;
  font-weight: 700;
  color: var(--dn-blue);
  line-height: 1.15;
  letter-spacing: -0.01em;
}
.closing-subtitle {
  font-size: 20px;
  color: var(--dn-blue);
  font-weight: 500;
  margin-top: 16px;
  letter-spacing: 0.5px;
}
.closing-logo {
  position: absolute;
  bottom: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.closing-logo-text {
  font-size: 28px;
  font-weight: 800;
  color: var(--dn-blue);
  letter-spacing: 4px;
}
.closing-logo-sub {
  font-size: 11px;
  color: var(--dn-teal);
  font-weight: 600;
  letter-spacing: 2px;
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
  letter-spacing: -0.01em;
}
.headline {
  margin-top: 14px;
  font-family: var(--dn-font-display);
  font-size: 42px;
  line-height: 1.08;
  font-weight: 700;
  color: var(--dn-text);
  letter-spacing: -0.01em;
}

/* Metric big number */
.metric {
  font-family: var(--dn-font-display);
  font-size: 48px;
  line-height: 1;
  font-weight: 700;
  color: var(--dn-blue);
  letter-spacing: -0.02em;
  font-feature-settings: "tnum";
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

/* ---- Stat Grid (Big Number Poster) ---- */
.stat-grid {
  margin-top: 36px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
.stat-cell {
  position: relative;
  padding: 32px 28px;
  background: #fff;
  border: 1px solid var(--dn-border);
  border-radius: 12px;
  overflow: hidden;
}
.stat-cell .stat-number {
  font-family: var(--dn-font-display);
  font-size: 72px;
  font-weight: 800;
  line-height: 1;
  color: var(--accent, var(--dn-blue));
  letter-spacing: -0.03em;
  font-feature-settings: "tnum";
}
.stat-cell .stat-label {
  margin-top: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--dn-text);
  line-height: 1.3;
}
.stat-cell .stat-desc {
  margin-top: 6px;
  font-size: 13px;
  color: var(--dn-text-secondary);
  line-height: 1.35;
}

/* ---- Before / After Comparison ---- */
.compare-grid {
  margin-top: 36px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}
.compare-card {
  padding: 32px;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}
.compare-card.before {
  background: var(--dn-soft);
  border: 1px solid var(--dn-border);
}
.compare-card.after {
  background: var(--accent, var(--dn-blue));
  color: #fff;
}
.compare-card.after h3,
.compare-card.after li {
  color: #fff;
}
.compare-card.after li::marker {
  color: rgba(255,255,255,0.6);
}
.compare-label {
  font-family: var(--dn-font-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 16px;
  opacity: 0.6;
}

/* ---- Image + Text (Editorial) ---- */
.editorial-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  height: 100%;
  align-items: center;
}
.editorial-split.reverse {
  direction: rtl;
}
.editorial-split.reverse > * {
  direction: ltr;
}
.editorial-image {
  position: relative;
  height: 100%;
  min-height: 720px;
  overflow: hidden;
}
.editorial-image .frame-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border-radius: 0;
}
.editorial-text {
  padding: 72px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* ---- Big Quote Page ---- */
.big-quote-slide {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 72px 120px;
}
.big-quote-text {
  font-family: var(--dn-font-display);
  font-size: 42px;
  line-height: 1.2;
  font-weight: 500;
  color: var(--dn-text);
  font-style: italic;
}
.big-quote-source {
  margin-top: 32px;
  font-family: var(--dn-font-mono);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--dn-text-secondary);
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

/* ---- Editorial image placeholders ---- */
.frame-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  display: block;
}
.img-slot {
  border: 2px dashed var(--dn-border);
  border-radius: 8px;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 8px,
    rgba(0,0,0,0.03) 8px,
    rgba(0,0,0,0.03) 16px
  );
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--dn-font-mono);
  font-size: 11px;
  color: var(--dn-text-secondary);
  text-align: center;
  position: relative;
}
.img-slot::before {
  content: attr(data-ratio);
  position: absolute;
  top: 6px;
  right: 8px;
  font-size: 9px;
  color: rgba(0,0,0,0.35);
  background: rgba(255,255,255,0.7);
  padding: 2px 5px;
  border-radius: 3px;
}

/* ---- Visual depth ---- */
.card-shadow {
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04);
}
.card-shadow:hover {
  box-shadow: 0 2px 6px rgba(0,0,0,0.08), 0 8px 20px rgba(0,0,0,0.06);
}

.cover-gradient {
  background: radial-gradient(ellipse 80% 60% at 70% 40%, rgba(255,255,255,0.12) 0%, transparent 70%),
              linear-gradient(105deg, rgba(0,94,184,0.92) 0%, rgba(0,94,184,0.72) 45%, rgba(0,94,184,0.25) 100%);
}

.img-overlay {
  position: relative;
}
.img-overlay::after {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0,38,119,0.35);
  backdrop-filter: blur(2px);
  border-radius: inherit;
  pointer-events: none;
}

.ghost-number {
  position: absolute;
  font-family: var(--dn-font-display);
  font-size: 280px;
  font-weight: 800;
  line-height: 1;
  color: var(--accent, var(--dn-blue));
  opacity: 0.06;
  pointer-events: none;
  z-index: 0;
  user-select: none;
}

/* ---- Photo strip (Danone signature element) ---- */
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
class StrategicSlide:
    """A single slide from a strategic/VP review deck."""
    number: int
    title: str
    page_role: str = ""
    key_message: str = ""
    must_show: list[str] = field(default_factory=list)
    recommended_visual: str = ""  # maps to layout intent
    speaker_script: str = ""


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
    photo_hints: list[dict] = field(default_factory=list)


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


def collect_photo_hints(block: str) -> list[dict]:
    """Extract [img: xxx] / [photo: xxx] markers from scenario block."""
    return parse_image_hints(block)


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
        scenario.photo_hints = collect_photo_hints(block)
        scenario.shorthand = shorthands.get(name, "")
        if not scenario.shorthand:
            for key, value in shorthands.items():
                if key in name or name in key:
                    scenario.shorthand = value
                    break
        scenarios.append(scenario)

    # If scenarios have no photo hints, try global hints at top of file
    if all(not s.photo_hints for s in scenarios):
        global_hints = parse_image_hints(markdown)
        if global_hints:
            # Distribute: first hint to first scenario device, rest to products
            for i, scenario in enumerate(scenarios):
                start = i * 3
                scenario.photo_hints = global_hints[start:start + 3] or [{"path": "", "label": "Photo"}]

    summary_match = re.search(r"### 总结一句\s*\n>\s*(.+)", markdown)
    summary = clean_inline(summary_match.group(1)) if summary_match else "Danone 不只是提供营养，而是让营养被数据证明。"
    return title, scenarios, parse_showcase_flow(markdown), summary


def plan_from_notes(title: str, scenarios: list[Scenario], showcase_flow: list[str], summary: str) -> list[dict]:
    """Generate a layout plan based on content analysis, not hardcoded sequence.

    Each scenario is analyzed for richness and assigned the best layout:
    - 4+ data points → stat-grid
    - core_message present → scenario gets a big-quote divider after it
    - Default → three-column
    """
    if not scenarios:
        raise ValueError("No scenario sections found. Expected headings like '## 场景 1｜Gut Health'.")

    plan: list[dict] = []

    # 1. Cover
    plan.append({"intent": "cover", "theme": "hero"})

    # 2. Big message summary slide
    plan.append({
        "intent": "big-message",
        "theme": "light",
        "content": {
            "headline": "Three measurable nutrition journeys",
            "supporting_text": " / ".join(
                scenario.shorthand or scenario.name for scenario in scenarios[:3]
            ),
        },
    })

    # 3. Scenario slides with smart layout selection
    for scenario in scenarios:
        data_items = scenario.indicators or scenario.collected_data
        has_rich_data = len(data_items) >= 3
        has_core_msg = bool(scenario.core_message and "待补充" not in scenario.core_message)

        if has_rich_data and has_core_msg:
            # Rich scenario: full three-column + stats
            plan.append({
                "intent": "scenario",
                "theme": "light",
                "scenario": scenario,
            })
            # Insert big-quote divider if core message is strong
            plan.append({
                "intent": "big-quote",
                "theme": "dark",
                "content": {
                    "quote": scenario.core_message,
                    "source": scenario.shorthand or scenario.name,
                },
            })
        elif has_rich_data:
            plan.append({
                "intent": "stat-grid",
                "theme": "light",
                "content": {
                    "title": scenario.name,
                    "stats": [
                        {"number": "--", "label": item, "desc": ""}
                        for item in data_items[:6]
                    ],
                },
            })
        else:
            plan.append({
                "intent": "scenario",
                "theme": "light",
                "scenario": scenario,
            })

    # 4. Flow slide if showcase flow exists
    if showcase_flow:
        plan.append({"intent": "flow", "theme": "light"})

    # 5. Closing
    plan.append({"intent": "closing", "theme": "hero"})

    return plan


def parse_strategic_notes(markdown: str) -> tuple[str, list[StrategicSlide]]:
    """Parse strategic/VP review Markdown with `## Slide N — Title` format.

    Each slide may have sub-sections:
    - ### Page role
    - ### Key message
    - ### Must show on slide
    - ### Recommended visual
    - ### Speaker script
    """
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    title = clean_inline(title_match.group(1)) if title_match else "Strategic Deck"

    # Match ## Slide N — Title or ## Slide N：Title
    pattern = re.compile(r"^##\s+Slide\s+(\d+)\s*[—\-:：]\s*(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(markdown))
    slides: list[StrategicSlide] = []

    for i, match in enumerate(matches):
        number = int(match.group(1))
        slide_title = clean_inline(match.group(2))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        block = markdown[start:end]

        slide = StrategicSlide(number=number, title=slide_title)

        lines = block.splitlines()
        current_section = ""
        for raw in lines:
            line = raw.strip()
            if line.startswith("### "):
                current_section = clean_inline(line[4:]).lower()
                continue
            if not line:
                continue
            if current_section == "page role":
                slide.page_role = clean_inline(line)
            elif current_section == "key message":
                slide.key_message = clean_inline(line.lstrip("> "))
            elif current_section == "must show on slide":
                if line.startswith("- "):
                    slide.must_show.append(clean_inline(line[2:]))
                else:
                    slide.must_show.append(clean_inline(line))
            elif current_section == "recommended visual":
                slide.recommended_visual = clean_inline(line)
            elif current_section == "speaker script":
                slide.speaker_script += clean_inline(line) + " "

        slides.append(slide)

    return title, slides


# Map visual recommendations to layout intents
VISUAL_TO_INTENT = {
    "decision matrix": "decision-grid",
    "2×2": "decision-grid",
    "decision grid": "decision-grid",
    "before/after": "positioning",
    "before vs after": "positioning",
    "contrast": "positioning",
    "flow": "master-storyline",
    "pipeline": "master-storyline",
    "storyline": "master-storyline",
    "matrix": "service-architecture",
    "priority table": "service-architecture",
    "hero split": "hero-demo",
    "two-column": "hero-demo",
    "flywheel": "data-flywheel",
    "loop": "data-flywheel",
    "journey": "experience-space",
    "customer journey": "experience-space",
    "naming": "naming-direction",
    "recommendation": "naming-direction",
}


def classify_strategic_slide(slide: StrategicSlide) -> str:
    """Classify a strategic slide's layout intent from its visual recommendation."""
    visual = slide.recommended_visual.lower()
    for keyword, intent in VISUAL_TO_INTENT.items():
        if keyword in visual:
            return intent
    # Default: if it has bullets → decision-grid, if it has key message → positioning
    if slide.must_show:
        return "decision-grid"
    return "positioning"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render_bullets(items: list[str], fallback: str = "待补充", limit: int = 4) -> str:
    chosen = [item for item in items if item][:limit] or [fallback]
    return "\n".join(f"<li>{esc(trim(item, 120))}</li>" for item in chosen)


def parse_image_hints(text: str) -> list[dict]:
    """Extract [img: description] or [photo: description] markers from text.

    Users can place these anywhere in their outline to mark where images belong.
    """
    pattern = re.compile(r"\[(?:img|photo|image):\s*([^\]]+)\]", re.IGNORECASE)
    hints: list[dict] = []
    for match in pattern.finditer(text):
        raw = match.group(1).strip()
        # Check if it's a path:label format like "[img: assets/photo.jpg: Product Shot]"
        if ":" in raw and not raw.endswith(":"):
            parts = raw.split(":", 1)
            if Path(parts[0].strip()).suffix:  # looks like a file path
                hints.append({"path": parts[0].strip(), "label": parts[1].strip()})
                continue
        hints.append({"path": "", "label": raw})
    return hints


def render_image_slot(hint: dict, size: str = "64px", ratio: str = "1:1") -> str:
    """Render an image placeholder — with real image if path provided."""
    path = hint.get("path", "")
    label = hint.get("label", "Photo")
    if path:
        return f'<img class="frame-img" src="{esc(path)}" alt="{esc(label)}" style="width:{size};height:{size};border-radius:50%;object-fit:cover;">'
    return f'<div class="img-slot" style="width:{size};height:{size};border-radius:50%;" data-ratio="{ratio}"><span>{esc(label)}</span></div>'


def slide_shell(title: str, body: str, extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../shared/tokens.css">
<style>{extra_css}</style>
</head>
<body class="pptx-canvas">
{body}
</body>
</html>
"""


def render_cover(title: str, summary: str, scenarios: list[Scenario], total: int = 7, brand_line: str = "Danone Science Lab") -> str:
    body = f"""<main class="slide opening-slide" theme="hero">
  <div class="opening-circle">
    <p class="opening-subtitle">{esc(brand_line)}</p>
    <h1 class="opening-title">{esc(title)}</h1>
    <div class="opening-logo">
      <p class="opening-logo-text">DANONE</p>
      <p class="opening-logo-sub">ONE PLANET. ONE HEALTH</p>
    </div>
  </div>
</main>"""
    return slide_shell("01 Cover", body)


def render_summary(summary: str, scenarios: list[Scenario], total: int = 7) -> str:
    theme_classes = ["green", "orange", "pink"]
    card_imgs = ["Gut", "Sport", "Clinic"]
    metrics = ["--", "--", "--"]
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
        <div class="img-slot" style="--accent:var(--dn-{cls if cls else 'blue'});--soft:var(--dn-{cls if cls else 'blue'}-soft);width:64px;height:64px;border-radius:50%;" data-ratio="1:1"><span>{img_label}</span></div>
      </div>
      <h3>{esc(s.name)}</h3>
      <p>{esc(s.shorthand or s.core_message)}</p>
      <div class="viz-metric" style="margin-top:18px;">
        <span class="number" style="color:var(--dn-{cls if cls else 'blue'})">{metric}</span>
        <span class="unit">{metric_label}</span>
      </div>
    </div>"""

    body = f"""<main class="slide" theme="light">
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

    # Data viz bars — use neutral 50% width when no real values provided
    viz_bars = ""
    for idx, item in enumerate(data_items[:4]):
        viz_bars += f"""<div class="viz-bar">
        <div class="viz-bar-fill" style="width:50%;background:{accent}"></div>
        <span class="viz-bar-label">{esc(trim(item, 40))}</span>
      </div>"""

    # Ring chart placeholder
    ring_pct = "--"

    # Image slots from user-provided hints
    device_hint = scenario.photo_hints[0] if scenario.photo_hints else {"path": "", "label": "Device Photo"}
    prod_hints = scenario.photo_hints[1:] if len(scenario.photo_hints) > 1 else [
        {"path": "", "label": "Prod"},
        {"path": "", "label": "Pack"},
    ]

    device_img = render_image_slot(device_hint, size="120px", ratio="1:1")
    prod_imgs = "".join(render_image_slot(h, size="64px", ratio="1:1") for h in prod_hints[:2])

    body = f"""<main class="slide scenario" theme="light" style="--accent:{accent};--soft:{soft};--dark:{dark}">
  <div class="scenario-head">
    <div>
      <p class="eyebrow" style="color:{accent}">Scenario 0{scenario.number}</p>
      <h2 class="headline">{esc(scenario.name)}</h2>
    </div>
    <div style="display:flex;align-items:center;gap:18px;">
      {device_img}
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
        {prod_imgs}
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

    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">Showcase Structure</p>
  <h2 class="title">From Measurement to a Personalized Danone Journey</h2>
  <div class="flow-grid">{steps}</div>
  <p class="closing-quote">{esc(summary)}</p>
  <div class="footer"><p>Exhibition Flow &middot; One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("06 Showcase Flow", body)


def render_thankyou(summary: str, index: int = 7, total: int = 7, brand_line: str = "Danone Science Lab") -> str:
    body = f"""<main class="slide closing-slide" theme="hero">
  <div class="closing-circle">
    <h1 class="closing-title">THANK YOU</h1>
    <p class="closing-subtitle">{esc(summary)}</p>
    <div class="closing-logo">
      <p class="closing-logo-text">DANONE</p>
      <p class="closing-logo-sub">ONE PLANET. ONE HEALTH</p>
    </div>
  </div>
</main>"""
    return slide_shell("Thank You", body)


def render_big_message(headline: str, supporting: str = "", theme_class: str = "light",
                       accent_color: str = "var(--dn-blue)", index: int = 0, total: int = 1) -> str:
    """Single takeaway — oversized headline + optional support text."""
    ghost = '<div class="ghost-number">01</div>' if theme_class == "dark" else ""
    sub_color = "rgba(255,255,255,0.78)" if theme_class == "dark" else "var(--dn-text-secondary)"
    sub_html = f'<p style="margin-top:24px;font-size:22px;line-height:1.35;max-width:640px;color:{sub_color};">{esc(supporting)}</p>' if supporting else ""
    body = f"""<main class="slide {'slide-dark' if theme_class == 'dark' else ''}" theme="{theme_class}">
  {ghost}
  <p class="eyebrow" style="color:{'rgba(255,255,255,0.6)' if theme_class == 'dark' else 'var(--dn-blue)'}">Key Message</p>
  <h2 class="title" style="font-size:56px;line-height:1.0;margin-top:48px;">{esc(headline)}</h2>
  {sub_html}
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("Big Message", body)


def render_big_quote(quote: str, source: str = "", theme_class: str = "dark",
                     index: int = 0, total: int = 1) -> str:
    """Full-page centered quote for visual breathing."""
    body = f"""<main class="slide {'slide-dark' if theme_class == 'dark' else ''}" theme="{theme_class}">
  <div class="big-quote-slide">
    <p class="big-quote-text">&ldquo;{esc(quote)}&rdquo;</p>
    {f'<p class="big-quote-source">{esc(source)}</p>' if source else ''}
  </div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("Big Quote", body)


def render_stat_grid(stats: list[dict], theme_class: str = "light",
                     index: int = 0, total: int = 1) -> str:
    """Big number data highlights — stat grid with metric cells."""
    grid_items = ""
    for s in stats[:6]:
        grid_items += f"""<div class="stat-cell">
      <p class="stat-number" style="color:{s.get('color', 'var(--dn-blue)')}">{esc(s['number'])}</p>
      <p class="stat-label">{esc(s['label'])}</p>
      {f'<p class="stat-desc">{esc(s["desc"])}</p>' if s.get("desc") else ''}
    </div>"""
    cols = min(len(stats), 3)
    body = f"""<main class="slide {'slide-dark' if theme_class == 'dark' else ''}" theme="{theme_class}">
  <p class="eyebrow" style="color:{'rgba(255,255,255,0.6)' if theme_class == 'dark' else 'var(--dn-blue)'}">Data Highlights</p>
  <h2 class="title">Key Metrics</h2>
  <div class="stat-grid" style="grid-template-columns:repeat({cols},1fr);">{grid_items}</div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("Stat Grid", body)


def render_compare(before_title: str, before_items: list[str],
                   after_title: str, after_items: list[str],
                   theme_class: str = "light", accent_color: str = "var(--dn-blue)",
                   index: int = 0, total: int = 1) -> str:
    """Before/After two-column contrast."""
    body = f"""<main class="slide {'slide-dark' if theme_class == 'dark' else ''}" theme="{theme_class}">
  <p class="eyebrow" style="color:{'rgba(255,255,255,0.6)' if theme_class == 'dark' else 'var(--dn-blue)'}">Comparison</p>
  <h2 class="title">Before vs After</h2>
  <div class="compare-grid">
    <div class="compare-card before">
      <p class="compare-label">Before</p>
      <h3>{esc(before_title)}</h3>
      <ul>{"".join(f"<li>{esc(i)}</li>" for i in before_items[:5])}</ul>
    </div>
    <div class="compare-card after" style="background:{accent_color};">
      <p class="compare-label">After</p>
      <h3>{esc(after_title)}</h3>
      <ul>{"".join(f"<li>{esc(i)}</li>" for i in after_items[:5])}</ul>
    </div>
  </div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("Compare", body)


def render_editorial_split(headline: str, body_text: str, image_label: str = "Photo",
                           image_path: str = "", reverse: bool = False,
                           theme_class: str = "light", index: int = 0, total: int = 1) -> str:
    """Image + Text editorial split layout."""
    reverse_class = " reverse" if reverse else ""
    if image_path:
        img_content = f'<img class="frame-img" src="{esc(image_path)}" alt="{esc(image_label)}">'
    else:
        img_content = f'<div class="img-slot" style="width:100%;height:100%;" data-ratio="4:3"><span>{esc(image_label)}</span></div>'
    text_color = "rgba(255,255,255,0.78)" if theme_class == "dark" else "var(--dn-text-secondary)"
    eyebrow_color = "rgba(255,255,255,0.6)" if theme_class == "dark" else "var(--dn-blue)"
    body = f"""<main class="slide {'slide-dark' if theme_class == 'dark' else ''}" theme="{theme_class}">
  <div class="editorial-split{reverse_class}">
    <div class="editorial-image">{img_content}</div>
    <div class="editorial-text">
      <p class="eyebrow" style="color:{eyebrow_color};">Feature</p>
      <h2 class="headline">{esc(headline)}</h2>
      <p style="margin-top:18px;font-size:20px;line-height:1.4;color:{text_color};">{esc(body_text)}</p>
    </div>
  </div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell("Editorial Split", body)


# ---- Strategic / VP Review Render Functions ----

_STRATEGIC_CSS = """
.decision-grid { margin-top:32px; display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.decision-card { padding:24px; border-radius:12px; border:1px solid var(--dn-border); background:#fff; }
.decision-card.accent { background:var(--dn-soft); border-left:4px solid var(--dn-blue); }
.decision-card h3 { font-size:18px; font-weight:700; color:var(--dn-text); margin-bottom:10px; }
.decision-card ul { padding-left:18px; }
.decision-card li { font-size:15px; line-height:1.4; color:var(--dn-text-secondary); }
.positioning-row { margin-top:36px; display:grid; grid-template-columns:1fr 1fr; gap:32px; }
.positioning-col { padding:28px; border-radius:12px; }
.positioning-col.not { background:var(--dn-soft); border:1px solid var(--dn-border); }
.positioning-col.is { background:var(--dn-blue); color:#fff; }
.positioning-col.is h3, .positioning-col.is li { color:#fff; }
.positioning-col.is li::marker { color:rgba(255,255,255,0.6); }
.positioning-col h3 { font-size:16px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:14px; }
.storyline-flow { margin-top:36px; display:flex; gap:16px; flex-wrap:wrap; align-items:center; }
.storyline-step { flex:1; min-width:140px; padding:20px 16px; background:var(--dn-soft); border-radius:12px; border-top:4px solid var(--dn-blue); }
.storyline-step .step-num { font-family:var(--dn-font-display); font-size:32px; font-weight:700; color:var(--dn-blue); }
.storyline-step h4 { font-size:14px; font-weight:600; margin-top:8px; color:var(--dn-text); }
.service-matrix { margin-top:28px; width:100%; border-collapse:collapse; }
.service-matrix th, .service-matrix td { padding:10px 14px; border:1px solid var(--dn-border); text-align:left; font-size:14px; }
.service-matrix th { background:var(--dn-blue); color:#fff; font-weight:600; }
.priority-hero { color:var(--dn-blue); font-weight:700; }
.flywheel-container { margin-top:36px; display:flex; justify-content:center; align-items:center; flex-wrap:wrap; gap:12px; }
.flywheel-step { width:140px; height:140px; border-radius:50%; background:var(--dn-soft); border:3px solid var(--dn-blue); display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:12px; }
.flywheel-step .fw-num { font-family:var(--dn-font-display); font-size:28px; font-weight:700; color:var(--dn-blue); }
.flywheel-step h4 { font-size:12px; font-weight:600; color:var(--dn-text); margin-top:6px; }
.experience-journey { margin-top:36px; display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.journey-stage { padding:20px; border-radius:12px; background:var(--dn-soft); border-top:4px solid var(--dn-blue); }
.journey-stage h4 { font-size:14px; font-weight:700; margin-bottom:8px; color:var(--dn-text); }
.journey-stage p { font-size:13px; color:var(--dn-text-secondary); line-height:1.3; }
.naming-table { margin-top:28px; width:100%; }
.naming-table th, .naming-table td { padding:10px 14px; border:1px solid var(--dn-border); text-align:left; font-size:14px; }
.naming-table th { background:var(--dn-blue); color:#fff; }
.recommendation-box { margin-top:24px; padding:20px; background:var(--dn-soft); border-left:4px solid var(--dn-blue); border-radius:0 12px 12px 0; }
.recommendation-box h3 { font-size:16px; font-weight:700; color:var(--dn-text); margin-bottom:8px; }
"""


def render_strategic_slide(slide: StrategicSlide, index: int, total: int, intent: str = "") -> str:
    """Route a strategic slide to the appropriate render function."""
    # Respect explicit intent from plan first
    if intent == "strategic-cover":
        return _render_strategic_cover(slide, index, total)
    if intent == "strategic-closing":
        return _render_strategic_closing(slide, index, total)

    # Otherwise classify from slide content
    intent = classify_strategic_slide(slide)
    renderers = {
        "cover": _render_strategic_cover,
        "closing": _render_strategic_closing,
        "decision-grid": render_decision_grid,
        "positioning": render_positioning,
        "master-storyline": render_master_storyline,
        "service-architecture": render_service_architecture,
        "hero-demo": render_hero_demo,
        "data-flywheel": render_data_flywheel,
        "experience-space": render_experience_space,
        "naming-direction": render_naming_direction,
    }
    renderer = renderers.get(intent, render_decision_grid)
    return renderer(slide, index, total)


def _render_strategic_cover(slide: StrategicSlide, index: int, total: int) -> str:
    body = f"""<main class="slide opening-slide" theme="hero">
  <div class="opening-circle">
    <p class="opening-subtitle">Strategic Review</p>
    <h1 class="opening-title">{esc(slide.title)}</h1>
    <div class="opening-logo">
      <p class="opening-logo-text">DANONE</p>
      <p class="opening-logo-sub">ONE PLANET. ONE HEALTH</p>
    </div>
  </div>
</main>"""
    return slide_shell(f"{index:02d} Cover", body)


def _render_strategic_closing(slide: StrategicSlide, index: int, total: int) -> str:
    msg = slide.key_message or "Thank You"
    body = f"""<main class="slide closing-slide" theme="hero">
  <div class="closing-circle">
    <h1 class="closing-title">THANK YOU</h1>
    <p class="closing-subtitle">{esc(msg)}</p>
    <div class="closing-logo">
      <p class="closing-logo-text">DANONE</p>
      <p class="closing-logo-sub">ONE PLANET. ONE HEALTH</p>
    </div>
  </div>
</main>"""
    return slide_shell(f"{index:02d} Closing", body)


def render_decision_grid(slide: StrategicSlide, index: int, total: int) -> str:
    cards = ""
    items = slide.must_show or ["Key point to discuss"]
    # Split items into 2×2 grid pairs
    mid = (len(items) + 1) // 2
    for label, group in [("Key Considerations", items[:mid]), ("Action Items", items[mid:])]:
        cards += f"""<div class="decision-card accent">
      <h3>{esc(label)}</h3>
      <ul>{"".join(f"<li>{esc(i)}</li>" for i in group if i)}</ul>
    </div>"""
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <div class="decision-grid">{cards}</div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_positioning(slide: StrategicSlide, index: int, total: int) -> str:
    items = slide.must_show or ["Current state", "Future state"]
    mid = (len(items) + 1) // 2
    before = items[:mid]
    after = items[mid:]
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <div class="positioning-row">
    <div class="positioning-col not">
      <h3>What It Is Not</h3>
      <ul>{"".join(f"<li>{esc(i)}</li>" for i in before)}</ul>
    </div>
    <div class="positioning-col is">
      <h3>What It Is</h3>
      <ul>{"".join(f"<li>{esc(i)}</li>" for i in after)}</ul>
    </div>
  </div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_master_storyline(slide: StrategicSlide, index: int, total: int) -> str:
    items = slide.must_show or ["Vision", "Pillars", "Services", "Experience"]
    steps = ""
    for i, item in enumerate(items[:6], 1):
        steps += f"""<div class="storyline-step">
      <p class="step-num">{i}</p>
      <h4>{esc(item)}</h4>
    </div>"""
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <div class="storyline-flow">{steps}</div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_service_architecture(slide: StrategicSlide, index: int, total: int) -> str:
    items = slide.must_show or ["Service", "Priority", "Description"]
    rows = ""
    for item in items[:6]:
        rows += f"<tr><td>{esc(item)}</td><td>Core</td><td>Description TBD</td></tr>"
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <table class="service-matrix">
    <thead><tr><th>Service</th><th>Priority</th><th>Description</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_hero_demo(slide: StrategicSlide, index: int, total: int) -> str:
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <div class="editorial-split">
    <div class="editorial-image">
      <div class="img-slot" style="width:100%;height:100%;" data-ratio="4:3"><span>Hero Image</span></div>
    </div>
    <div class="editorial-text">
      <h2 class="headline">{esc(slide.key_message)}</h2>
      <ul style="margin-top:16px;">{"".join(f"<li>{esc(i)}</li>" for i in slide.must_show[:4])}</ul>
    </div>
  </div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_data_flywheel(slide: StrategicSlide, index: int, total: int) -> str:
    items = slide.must_show or ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5", "Step 6"]
    steps = ""
    for i, item in enumerate(items[:6], 1):
        steps += f"""<div class="flywheel-step">
      <p class="fw-num">{i}</p>
      <h4>{esc(item)}</h4>
    </div>"""
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <div class="flywheel-container">{steps}</div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_experience_space(slide: StrategicSlide, index: int, total: int) -> str:
    items = slide.must_show or ["Stage 1", "Stage 2", "Stage 3", "Stage 4"]
    stages = ""
    for item in items[:4]:
        stages += f"""<div class="journey-stage">
      <h4>{esc(item)}</h4>
      <p>Details to be defined</p>
    </div>"""
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <div class="experience-journey">{stages}</div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


def render_naming_direction(slide: StrategicSlide, index: int, total: int) -> str:
    items = slide.must_show or ["Option A", "Option B", "Option C"]
    rows = "".join(f"<tr><td>{esc(item)}</td><td>Evaluate</td></tr>" for item in items[:5])
    rec = slide.key_message or "Recommendation TBD"
    body = f"""<main class="slide" theme="light">
  <p class="eyebrow">{esc(slide.page_role)}</p>
  <h2 class="title">{esc(slide.title)}</h2>
  <table class="naming-table">
    <thead><tr><th>Option</th><th>Assessment</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="recommendation-box">
    <h3>Recommendation</h3>
    <p>{esc(rec)}</p>
  </div>
  <div class="footer"><p>One Planet. One Health</p><p>{index:02d} / {total:02d}</p></div>
</main>"""
    return slide_shell(slide.title, body)


# ---- End Strategic Render Functions ----


def plan_from_strategic(title: str, slides: list[StrategicSlide]) -> list[dict]:
    """Generate layout plan from strategic/VP review slides."""
    plan: list[dict] = []

    # 1. Cover
    plan.append({"intent": "strategic-cover", "slide": slides[0] if slides else StrategicSlide(number=0, title=title)})

    # 2. Each strategic slide with auto-classification
    for slide in slides:
        # Skip first slide if it's a cover
        is_cover = slide.number == 1 and (
            "cover" in slide.page_role.lower() or "opening" in slide.title.lower()
        )
        if is_cover:
            continue
        # Route closing slides by page role, number position, or content
        is_closing = (
            "closing" in slide.page_role.lower()
            or "thank" in slide.title.lower()
            or (slide.number == max(s.number for s in slides) and not slide.must_show)
        )
        if is_closing:
            plan.append({"intent": "strategic-closing", "slide": slide})
            continue

        intent = classify_strategic_slide(slide)
        plan.append({"intent": intent, "slide": slide})

    return plan


def native_plan_from_strategic(
    title: str,
    slides: list[StrategicSlide],
    brand_line: str = "Danone Science Lab",
) -> list[dict]:
    """Convert strategic HTML plan items into native PPTX content specs."""
    native_plan: list[dict] = []
    strategic_plan = plan_from_strategic(title, slides)

    for item in strategic_plan:
        intent = item["intent"]
        slide = item["slide"]
        bullets = [value for value in slide.must_show if value]
        bullet_block = bullet_text(bullets, slide.key_message or "Data TBD", 6)

        if intent == "strategic-cover":
            native_plan.append({
                "intent": "opening-cover",
                "content": {
                    "title": title,
                    "subtitle_or_date": brand_line,
                },
            })
        elif intent == "strategic-closing":
            native_plan.append({
                "intent": "closing",
                "content": {
                    "title": slide.key_message or "THANK YOU",
                },
            })
        elif intent == "positioning":
            native_plan.append({
                "intent": "positioning",
                "content": {
                    "title": slide.title,
                    "before_text": "What DHT is not\n" + "\n".join(bullets[:2] or [slide.page_role or "Data TBD"]),
                    "after_text": "What DHT is\n" + "\n".join(bullets[2:] or [slide.key_message or "Data TBD"]),
                },
            })
        elif intent == "service-architecture":
            midpoint = max(1, len(bullets) // 2)
            native_plan.append({
                "intent": "service-architecture",
                "content": {
                    "title": slide.title,
                    "left_content": "\n".join(bullets[:midpoint] or [slide.page_role or "Data TBD"]),
                    "right_content": "\n".join(bullets[midpoint:] or [slide.key_message or "Data TBD"]),
                },
            })
        elif intent == "data-flywheel":
            native_plan.append({
                "intent": "data-flywheel",
                "content": {
                    "title": slide.title,
                    "flywheel_steps": bullets or [slide.key_message or "Data TBD"],
                },
            })
        elif intent == "experience-space":
            native_plan.append({
                "intent": "experience-space",
                "content": {
                    "title": slide.title,
                    "column_1": "\n".join(bullets[0:2] or [slide.page_role or "Data TBD"]),
                    "column_2": "\n".join(bullets[2:4] or [slide.key_message or "Data TBD"]),
                    "column_3": "\n".join(bullets[4:6] or ["Data TBD"]),
                },
            })
        elif intent == "naming-direction":
            native_plan.append({
                "intent": "naming-direction",
                "content": {
                    "title": slide.title,
                    "naming_recommendation": slide.key_message or bullet_block,
                },
            })
        elif intent == "master-storyline":
            native_plan.append({
                "intent": "master-storyline",
                "content": {
                    "title": slide.title,
                    "headline": slide.key_message or bullet_block,
                },
            })
        elif intent == "decision-grid":
            native_plan.append({
                "intent": "decision-grid",
                "content": {
                    "title": slide.title,
                    "decision_items": bullets or [slide.key_message or "Data TBD"],
                },
            })
        elif intent == "big-quote":
            native_plan.append({
                "intent": "big-quote",
                "content": {
                    "title": slide.title,
                    "quote": slide.key_message or bullet_block,
                },
            })
        elif intent == "stat-grid":
            native_plan.append({
                "intent": "stat-grid",
                "content": {
                    "title": slide.title,
                    "stats": bullets or [slide.key_message or "Data TBD"],
                },
            })
        elif intent == "flow":
            native_plan.append({
                "intent": "flow",
                "content": {
                    "title": slide.title,
                    "flow_steps": bullets or [slide.key_message or "Data TBD"],
                },
            })
        elif intent == "hero-demo":
            native_plan.append({
                "intent": "two-column",
                "content": {
                    "title": slide.title,
                    "left_content": slide.key_message or slide.page_role or "Data TBD",
                    "right_content": bullet_block,
                },
            })

    return native_plan


def write_strategic_deck(out_dir: Path, title: str, slides: list[StrategicSlide]) -> None:
    """Generate HTML deck from strategic/VP review input."""
    slides_dir = out_dir / "slides"
    shared_dir = out_dir / "shared"
    slides_dir.mkdir(parents=True, exist_ok=True)
    shared_dir.mkdir(parents=True, exist_ok=True)
    token_css = DEFAULT_TOKENS.read_text(encoding="utf-8")
    (shared_dir / "tokens.css").write_text(token_css + "\n" + BASE_COMPONENT_CSS + "\n" + _STRATEGIC_CSS, encoding="utf-8")

    plan = plan_from_strategic(title, slides)
    total = len(plan)

    pages: list[tuple[str, str, str]] = []
    for i, item in enumerate(plan, start=1):
        slide = item["slide"]
        intent = item["intent"]
        html_content = render_strategic_slide(slide, index=i, total=total, intent=intent)
        label = slide.title or intent
        slug = slugify(label)
        filename = f"{i:02d}-{slug}.html"
        pages.append((filename, label, html_content))

    for filename, _label, content in pages:
        (slides_dir / filename).write_text(content, encoding="utf-8")

    manifest = [{"file": f"slides/{filename}", "label": label} for filename, label, _content in pages]
    (out_dir / "index.html").write_text(render_index(title, manifest), encoding="utf-8")
    logging.info("Wrote %d strategic slides to %s", total, out_dir)


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
    """Generate HTML deck using content-driven layout selection.

    Routes each plan item to the appropriate render function.
    Theme alternates light → dark → hero automatically.
    Slide count matches content, not hardcoded.
    """
    slides_dir = out_dir / "slides"
    shared_dir = out_dir / "shared"
    slides_dir.mkdir(parents=True, exist_ok=True)
    shared_dir.mkdir(parents=True, exist_ok=True)
    token_css = DEFAULT_TOKENS.read_text(encoding="utf-8")
    (shared_dir / "tokens.css").write_text(token_css + "\n" + BASE_COMPONENT_CSS, encoding="utf-8")

    plan = plan_from_notes(title, scenarios, showcase_flow, summary)
    total = len(plan)

    pages: list[tuple[str, str, str]] = []
    for i, slide in enumerate(plan, start=1):
        intent = slide["intent"]
        theme_class = slide.get("theme", "light")
        idx = i

        if intent == "cover":
            html_content = render_cover(title, summary, scenarios, total=total, brand_line=brand_line)
            label = "Cover"
        elif intent == "big-message":
            content = slide.get("content", {})
            html_content = render_big_message(
                headline=content.get("headline", ""),
                supporting=content.get("supporting_text", ""),
                theme_class=theme_class,
                index=idx, total=total,
            )
            label = "Key Message"
        elif intent == "scenario":
            scenario = slide["scenario"]
            html_content = render_scenario(idx, scenario, total=total)
            label = scenario.name
        elif intent == "big-quote":
            content = slide.get("content", {})
            html_content = render_big_quote(
                quote=content.get("quote", ""),
                source=content.get("source", ""),
                theme_class="dark",  # big-quote always dark
                index=idx, total=total,
            )
            label = "Quote"
        elif intent == "stat-grid":
            content = slide.get("content", {})
            theme = pick_theme(content.get("title", ""))
            accent = theme["accent"]
            stats = content.get("stats", [])
            for s in stats:
                if "color" not in s:
                    s["color"] = accent
            html_content = render_stat_grid(
                stats=stats,
                theme_class=theme_class,
                index=idx, total=total,
            )
            label = content.get("title", "Data")
        elif intent == "flow":
            html_content = render_flow(showcase_flow, summary, index=idx, total=total)
            label = "Flow"
        elif intent == "closing":
            html_content = render_thankyou(summary, index=idx, total=total, brand_line=brand_line)
            label = "Thank You"
        else:
            continue  # skip unknown intents gracefully

        slug = slugify(label)
        filename = f"{idx:02d}-{slug}.html"
        pages.append((filename, label, html_content))

    for filename, _label, content in pages:
        (slides_dir / filename).write_text(content, encoding="utf-8")

    manifest = [{"file": f"slides/{filename}", "label": label} for filename, label, _content in pages]
    (out_dir / "index.html").write_text(render_index(title, manifest), encoding="utf-8")
    logging.info("Wrote %d slides to %s", total, out_dir)


def build_deck(
    notes_file: str | Path,
    out_dir: str | Path,
    native_pptx: str | Path | None = None,
    out_plan: str | Path | None = None,
    template: str | Path = DEFAULT_TEMPLATE,
    layout_map: str | Path = DEFAULT_LAYOUT_MAP,
    brand_line: str = "Danone Science Lab",
    mode: str = "auto",
) -> dict:
    markdown = Path(notes_file).read_text(encoding="utf-8")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Auto-detect mode if not specified
    if mode == "auto":
        if re.search(r"^##\s+Slide\s+\d+", markdown, re.MULTILINE):
            mode = "strategic"
        else:
            mode = "scenario"

    if mode == "strategic":
        title, slides = parse_strategic_notes(markdown)
        write_strategic_deck(out_dir, title, slides)
        native_plan = native_plan_from_strategic(title, slides, brand_line=brand_line)
        if out_plan is not None:
            out_plan = Path(out_plan)
            out_plan.parent.mkdir(parents=True, exist_ok=True)
            out_plan.write_text(json.dumps({"slides": native_plan}, ensure_ascii=False, indent=2), encoding="utf-8")
        if native_pptx is not None and native_plan:
            builder = load_native_builder()
            builder.build_presentation(template, layout_map, native_plan, native_pptx)
        return {"title": title, "slide_count": len(native_plan), "mode": "strategic", "plan": native_plan}

    # Scenario mode (existing path)
    title, scenarios, showcase_flow, summary = parse_notes(markdown)
    plan = plan_from_notes(title, scenarios, showcase_flow, summary)
    write_html_deck(out_dir, title, scenarios, showcase_flow, summary, brand_line=brand_line)
    if out_plan is not None:
        out_plan = Path(out_plan)
        out_plan.parent.mkdir(parents=True, exist_ok=True)
        out_plan.write_text(json.dumps({"slides": plan}, ensure_ascii=False, indent=2), encoding="utf-8")
    if native_pptx is not None:
        # Filter plan to only include intents supported by native PPTX
        native_intents = {"opening-cover", "big-message", "two-column", "three-column", "closing", "contents"}
        native_plan = []
        for slide in plan:
            intent = slide["intent"]
            # Map HTML-only intents to closest native equivalents
            if intent == "cover":
                native_plan.append({"intent": "opening-cover", "content": {"title": title, "subtitle_or_date": brand_line}})
            elif intent == "scenario":
                scenario = slide["scenario"]
                native_plan.append({
                    "intent": "three-column",
                    "content": {
                        "title": f"{scenario.name} — {trim(scenario.hardware, 80)}",
                        "column_1": "User pain point\n" + bullet_text(scenario.pain_points, "待补充用户痛点", 4),
                        "column_2": "Invisible data made visible\n" + bullet_text(scenario.indicators or scenario.collected_data, "待补充数据指标", 4),
                        "column_3": "Danone product link\n" + bullet_text(scenario.products, "待补充 Danone 产品", 3),
                    },
                })
            elif intent == "closing":
                native_plan.append({
                    "intent": "closing",
                    "content": {"title": "Make nutrition measurable, actionable, and personal."},
                })
            elif intent in native_intents:
                native_plan.append({"intent": intent, "content": slide.get("content", {})})
            # Skip: stat-grid, big-quote, flow (no native equivalent)

        if native_plan:
            builder = load_native_builder()
            builder.build_presentation(template, layout_map, native_plan, native_pptx)
    return {"title": title, "scenario_count": len(scenarios), "slide_count": len(plan), "plan": plan}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Danone HTML and native PPTX assets from structured slide notes.")
    parser.add_argument("--notes", required=True, help="Structured Markdown notes file")
    parser.add_argument("--out-dir", required=True, help="Output deck directory containing index.html and slides/")
    parser.add_argument("--native-pptx", help="Optional native editable PPTX output path")
    parser.add_argument("--out-plan", help="Optional native JSON plan output path")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    parser.add_argument("--layout-map", default=str(DEFAULT_LAYOUT_MAP))
    parser.add_argument("--brand-line", default="Danone Science Lab", help="Footer brand line (e.g. 'Brand X · Danone')")
    parser.add_argument("--mode", choices=["auto", "scenario", "strategic"], default="auto",
                        help="Deck mode: scenario (science lab) or strategic (VP review). Auto-detects by default.")
    args = parser.parse_args()
    result = build_deck(
        notes_file=args.notes,
        out_dir=args.out_dir,
        native_pptx=args.native_pptx,
        out_plan=args.out_plan,
        template=args.template,
        layout_map=args.layout_map,
        brand_line=args.brand_line,
        mode=args.mode,
    )
    if result.get("mode") == "strategic":
        logging.info("Wrote %s (%d strategic slides)", args.out_dir, result["slide_count"])
    else:
        logging.info("Wrote %s (%d HTML slides, %d scenarios)", args.out_dir, result["slide_count"], result.get("scenario_count", 0))
    if args.native_pptx:
        logging.info("Wrote native %s (%d slides)", args.native_pptx, len(result.get("plan", [])))
    if args.out_plan:
        logging.info("Wrote plan %s", args.out_plan)


if __name__ == "__main__":
    main()
