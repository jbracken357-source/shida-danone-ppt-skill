# AGENTS.md — Shida Danone PPT Skill

> Source of truth for project commands, architecture, and development workflow.
> 项目命令、架构和开发流程的单一真相源。

---

## Project Overview / 项目概述

Danone-style corporate presentation generator. Triple-output architecture:
- **Native PPTX path**: clones real Danone template XML, swaps text → editable in PowerPoint
- **HTML deck path**: renders CSS slides → export to vector PDF or image PPTX
- **Input adapter**: normalizes free-form input (topics, outlines, scripts) → structured Markdown

Version: 6.0.0

---

## Quick Commands / 命令速查

### 0. Normalize free-form input (topics, outlines, scripts)
```bash
python scripts/input_adapter.py \
  --input brief.md \
  --out /tmp/normalized.md \
  --format auto
```

### 1. Native editable PPTX (from brief)
```bash
python scripts/brief_to_native_deck.py \
  --title "Deck Title" \
  --brief-file smoke-tests/brief-native/brief.md \
  --slides 6 \
  --out output.pptx
```

### 2. Native editable PPTX (from structured notes)
```bash
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
  --out-dir ./deck \
  --native-pptx ./deck/deck-editable.pptx \
  --brand-line "Brand X · Danone" \
  --mode auto
```

### 2b. Strategic / VP Review deck (HTML only)
```bash
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/strategic-brief.md \
  --out-dir ./deck \
  --mode strategic \
  --brand-line "Brand X · Danone"
```

### 3. HTML deck only (no PPTX)
```bash
python scripts/notes_to_danone_deck.py \
  --notes notes.md \
  --out-dir ./deck \
  --brand-line "Brand X · Danone"
```

### 4. HTML → PDF
```bash
node scripts/export_deck_pdf.mjs \
  --slides ./deck/slides/ \
  --out deck.pdf \
  --width 1280 --height 720
```

### 5. HTML → Image PPTX
```bash
node scripts/export_deck_pptx.mjs \
  --slides ./deck/slides/ \
  --out deck.pptx \
  --width 1280 --height 720
```

### 6. Profile a new template
```bash
python scripts/profile_danone_template.py \
  "Danone Real Templates/Standard Danone Template.pptx" \
  --out templates/danone-template-manifest.json
```

---

## File Structure / 文件结构

```
.
├── README.md                 # Human-facing project docs
├── SKILL.md                  # Claude skill definition (workflow-first, ~100 lines)
├── AGENTS.md                 # This file — commands & architecture
├── CHANGELOG.md              # Version history
├── package.json              # Node dependencies
├── requirements.txt          # Python deps (stdlib only, documented)
├── .gitignore
│
├── scripts/                  # Build & export scripts
│   ├── input_adapter.py             # NEW: normalize free-form input
│   ├── brief_to_native_deck.py      # Entry: brief → native PPTX
│   ├── build_native_pptx.py         # Core: XML clone + text swap
│   ├── notes_to_danone_deck.py      # Entry: notes → HTML deck (+ opt. native)
│   ├── export_deck_pdf.mjs          # HTML slides → vector PDF
│   ├── export_deck_pptx.mjs         # HTML slides → image PPTX
│   └── profile_danone_template.py   # Template analyzer
│
├── templates/                # Design system & mapping
│   ├── tokens.css            # CSS design tokens (colors, fonts)
│   ├── layout-map.json       # Intent → PPTX layout mapping
│   └── danone-template-manifest.json  # Full template profile (344KB)
│
├── references/               # NEW: Skill reference files
│   ├── checklist.md          # P0-P3 quality gates
│   ├── components.md         # Component catalog with exact CSS specs
│   ├── layouts.md            # Layout skeletons + theme rhythm planning
│   ├── themes.md             # Theme presets + brand colors
│   └── visual-verification.md # Screenshot + grep verification procedure
│
├── assets/
│   └── deck_index.html       # Reusable multi-file deck shell
│
├── Danone Real Templates/
│   └── Standard Danone Template.pptx  # Source template (do not modify)
│
├── backlog/
│   └── node-js-html-to-pptx.md      # Decision record: abandoned path
│
└── smoke-tests/              # Test inputs & outputs
    ├── brief-native/
    ├── dht-lab-notes/
    ├── native-minimal/
    ├── ai-ppt-skill-value/
    ├── strategic-brief.md     # Strategic mode test (6 slides)
    └── test-image-hints.md    # Image placeholder protocol test
```

---

## Architecture / 架构

### Triple-Output Design

```
Input (brief / notes / topics / outline / script)
    │
    ├─→ input_adapter.py (if free-form) ──→ normalized.md
    │                                             │
    ├─→ mode detection ──────────────────────────┘
    │        │
    │        ├─→ strategic mode ──→ HTML only (decision grids, flywheels, journeys)
    │        │        notes_to_danone_deck.py --mode strategic
    │        │
    │        └─→ scenario mode ──→ HTML slides + index.html
    │                 notes_to_danone_deck.py --mode scenario
    │                                      │
    │                                      ├─→ export_deck_pdf.mjs ──→ *.pdf (vector)
    │                                      └─→ export_deck_pptx.mjs ──→ *.pptx (image)
    │
    └─→ brief_to_native_deck.py ──→ build_native_pptx.py ──→ *.pptx (editable)
```

### Mode Routing
- **Strategic**: Detected by `## Slide N — Title` format or `--mode strategic`. Uses intent-based renderers (cover, positioning, flywheel, journey, etc.). HTML-only until native layout mapping added.
- **Scenario**: Detected by `## 场景 N｜Name` format or `--mode scenario`. Uses scenario card layouts with theme rhythm.
- **Auto**: Default. Format-detected from input structure.

### Native PPTX Path
- **Strengths**: Real template masters/layouts, editable text, small file size
- **Limitations**: Image replacement not yet implemented (falls back to HTML path)
- **Core engine**: `build_native_pptx.py` clones slide XML from the real template and replaces text runs

### HTML Deck Path
- **Strengths**: Full CSS styling, photo placeholders, data viz, any layout possible
- **Limitations**: PDF text is vector but not editable; image PPTX is not editable
- **Canvas size**: 1280×720px (pptx-canvas) for export; 1920×1080px (slide-canvas) for browser preview

### Input Adapter
- **Purpose**: Accept any input format, normalize to `## 场景 N｜Name` Markdown
- **Detection**: auto-detects structured/outline/topics/script formats
- **Output**: compatible with existing `notes_to_danone_deck.py` parser

---

## Known Issues / 已知问题

> 详见 `ROADMAP.md` 的完整分析和优化计划。

### P1 — Native PPTX 图片替换
- `image-content` / `section-photo` intents 在 HTML 路径已渲染，在 native PPTX 路径尚未实现图片替换到 `<p:pic>`
- 需要：复制图片到 `ppt/media/`，更新 `a:blip` 引用

### P1 — Strategic 布局 native PPTX 映射
- Strategic 布局（decision-grid, flywheel, journey 等）尚未映射到 native PPTX
- 当前策略：strategic 模式默认输出 HTML 路径

### P2 — Input adapter 智能度
- Script 格式拆分基于段落分块，部分 `待补充` 字段仍需要手动完善

---

## Development Workflow / 开发流程

### 每日开工 checklist

1. **依赖检查**
   ```bash
   node --version  # 18+
   python --version  # 3.10+
   npm list playwright pdf-lib pptxgenjs sharp 2>/dev/null || npm install
   ```

2. **读取 Roadmap**
   ```bash
   cat ROADMAP.md  # 确认当天要修的问题
   ```

3. **修改 → 生成 → 验证**
   ```bash
   # Step 1: Normalize input (if free-form)
   python scripts/input_adapter.py --input brief.md --out /tmp/normalized.md --format auto

   # Step 2: Generate test deck
   python scripts/notes_to_danone_deck.py \
     --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
     --out-dir /tmp/test-html --brand-line "DHT Lab · Danone"

   python scripts/brief_to_native_deck.py \
     --title "Test" --brief-file smoke-tests/brief-native/brief.md \
     --slides 6 --out /tmp/test-native.pptx

   # Step 3: HTML visual verification (open browser)
   # Check: font loading, theme rhythm, image placeholders, visual depth

   # Step 4: Native PPTX functional verification
   ls -lh /tmp/test-native.pptx        # Expected < 5MB
   python -c "import zipfile; z=zipfile.ZipFile('/tmp/test-native.pptx'); print(len(z.namelist()), 'files')"  # Expected < 100

   # Step 5: Export verification
   node scripts/export_deck_pdf.mjs --slides /tmp/test-html/slides --out /tmp/test.pdf --width 1280 --height 720
   node scripts/export_deck_pptx.mjs --slides /tmp/test-html/slides --out /tmp/test-image.pptx --width 1280 --height 720

   # Step 6: Documentation sync
   # - SKILL.md workflow matches actual script behavior
   # - references/ files are up to date
   # - CHANGELOG.md records changes
   ```

### Modifying the Skill
1. Edit `SKILL.md` (workflow) or `references/` (detail) — this is the source of truth
2. Test by copying to `~/.claude/skills/shida-danone-ppt-skill/SKILL.md`
3. Run the smoke test workflow above

### Adding a New Script
1. Place in `scripts/`, follow existing naming convention
2. Add command to AGENTS.md Quick Commands section
3. Update SKILL.md workflow step if the script is user-facing

### Template Changes
1. If the Danone template file changes, re-run `profile_danone_template.py`
2. Update `layout-map.json` if new layouts are added/removed
3. Verify `tokens.css` color values match the template

---

## Skill Installation / Skill 安装

To use this skill in Claude Code, copy the skill file to your Claude skills directory:

```bash
mkdir -p ~/.claude/skills/shida-danone-ppt-skill
cp SKILL.md ~/.claude/skills/shida-danone-ppt-skill/SKILL.md
```

Or use your skill manager (e.g., cc-switch) to install from this repo.

---

## Dependencies / 依赖

**Python**: Standard library only (no pip install needed).

**Node.js**:
```bash
npm install
# or
pnpm install
```

Packages: `playwright`, `pdf-lib`, `pptxgenjs`, `sharp`

---

## Design System Reference / 设计系统速查

| Element | Specification |
|---------|--------------|
| Brand primary | `#005EB8` |
| Brand dark | `#002677` |
| Slogan | "One Planet. One Health" |
| Cover format | Opening Slide Title — solid blue bg, white circle, centered title |
| Closing format | Closing Slide Title — same as cover, "THANK YOU" text |
| Gut theme | Green `#00A651` |
| Sport theme | Orange `#F26522` |
| Clinical theme | Pink `#E6007E` |
| Water theme | Teal `#00B2A9` |
| Corporate | Blue `#005EB8` |
| Font stack | Playfair Display (headlines), Inter (body), IBM Plex Mono (data) |

For full design rules, see `references/` directory. For layout registry and mode routing, see `SKILL.md`.
