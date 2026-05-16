# Shida Danone PPT Skill / Shida Danone PPT 技能

> **EN**: Danone-style corporate presentation generator. Photo-first layouts, multi-color category themes, "One Planet. One Health" brand DNA. v6.0.0.
> **CN**: Danone 风格企业演示文稿生成器。摄影优先布局、多色分类主题、"One Planet. One Health" 品牌基因。v6.0.0。

---

## Features / 功能特性

| Feature / 特性 | Description / 描述 |
|----------------|-------------------|
| **Editorial typography / 杂志级排版** | Playfair Display + Inter + IBM Plex Mono font stack / 衬线标题 + 非衬线正文 + 等宽数据 |
| **Photo-first / 摄影优先** | Editorial image placeholders with ratio labels / 编辑风格图片占位符，标注比例 |
| **Multi-color themes / 多色主题** | 5 category colorways mapped to real Danone template palettes / 5 种分类色域 |
| **Theme rhythm / 主题节奏** | Light / dark / hero page alternation for visual breathing / 明暗交替制造视觉呼吸 |
| **Native editable PPTX / 原生可编辑 PPTX** | Clones real template XML, keeps text editable in PowerPoint / 克隆真实模板 XML，文字可编辑 |
| **HTML deck / HTML 幻灯片** | Full CSS styling, data viz placeholders, any layout possible / 完整 CSS 样式、数据可视化占位 |
| **PDF export / PDF 导出** | Vector text, searchable, 1:1 visual fidelity / 矢量文字、可搜索、视觉保真 |
| **Image PPTX / 图片式 PPTX** | Screenshot-based, 100% visual fidelity / 截图模式，100% 视觉还原 |

---

## File Structure / 文件结构

```
.
├── README.md              # This file
├── SKILL.md               # Claude skill definition (source of truth)
├── AGENTS.md              # Commands & architecture reference
├── CHANGELOG.md           # Version history
├── ROADMAP.md             # Known issues, optimization plans, next steps
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies (stdlib only)
│
├── scripts/               # Build & export scripts
│   ├── input_adapter.py           # Normalize free-form input
│   ├── brief_to_native_deck.py    # Brief → native PPTX
│   ├── notes_to_danone_deck.py    # Notes → HTML deck (+ optional native)
│   ├── build_native_pptx.py       # Core engine (XML clone + text swap)
│   ├── export_deck_pdf.mjs        # HTML → vector PDF
│   ├── export_deck_pptx.mjs       # HTML → image PPTX
│   └── profile_danone_template.py # Template analyzer
│
├── templates/             # Design system
│   ├── tokens.css         # CSS design tokens
│   ├── layout-map.json    # Intent → layout mapping
│   └── danone-template-manifest.json
│
├── references/            # Skill reference files
│   ├── checklist.md       # P0-P3 quality gates
│   ├── components.md      # Component catalog
│   ├── layouts.md         # Layout skeletons + theme rhythm
│   ├── themes.md          # Color presets + brand colors
│   └── visual-verification.md
│
├── assets/
│   └── deck_index.html    # Reusable deck shell
│
├── Danone Real Templates/
│   └── Standard Danone Template.pptx
│
├── backlog/               # Decision records
└── smoke-tests/           # Test inputs & outputs
```

For detailed command reference and architecture, see [**AGENTS.md**](AGENTS.md).

---

## Install / 安装

**Node.js dependencies:**
```bash
npm install
# or: pnpm install / yarn install
```

**Python:** Standard library only — no `pip install` needed.

---

## Quick Start / 快速开始

### 0. Normalize free-form input
```bash
python scripts/input_adapter.py \
  --input brief.md \
  --out /tmp/normalized.md \
  --format auto
```

### 1. Native editable PPTX (from brief)
```bash
python scripts/brief_to_native_deck.py \
  --title "Strategy Deck" \
  --brief-file smoke-tests/brief-native/brief.md \
  --slides 6 \
  --out deck.pptx
```

### 2. HTML deck + PDF (from structured notes)
```bash
# Generate HTML slides (scenario mode)
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
  --out-dir ./deck \
  --brand-line "DHT Lab · Danone"

# Strategic / VP Review mode
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/strategic-brief.md \
  --out-dir ./deck \
  --mode strategic \
  --brand-line "Brand X · Danone"

# Export to PDF
node scripts/export_deck_pdf.mjs \
  --slides ./deck/slides/ \
  --out deck.pdf \
  --width 1280 --height 720
```

### 3. Native + HTML + PDF (full pipeline)
```bash
python scripts/notes_to_danone_deck.py \
  --notes notes.md \
  --out-dir ./deck \
  --native-pptx ./deck/deck-editable.pptx \
  --brand-line "Brand X · Danone"

node scripts/export_deck_pdf.mjs \
  --slides ./deck/slides/ --out ./deck/deck.pdf \
  --width 1280 --height 720

node scripts/export_deck_pptx.mjs \
  --slides ./deck/slides/ --out ./deck/deck-image.pptx \
  --width 1280 --height 720
```

---

## Design System / 设计系统

### Brand DNA (non-negotiable)
- **Hero cover**: solid `#005EB8` background, white circle, centered title — "Opening Slide Title" format
- **Slogan**: "One Planet. One Health" on cover + every footer
- **Photography-first**: photo placeholders on every page
- **Multi-color themes**:
  - Gut/Natural → Green `#00A651`
  - Sport/Physical → Orange `#F26522`
  - Clinical/Baby → Pink `#E6007E`
  - Water/Hydration → Teal `#00B2A9`
  - Corporate/Default → Blue `#005EB8`

### Closing Page
- "Closing Slide Title" format — same blue background + white circle + "THANK YOU"
- DANONE logo + "One Planet. One Health" at bottom

For full component specifications (cards, buttons, images, data viz, quote blocks, flow steps, footer), see [**SKILL.md**](SKILL.md).

---

## Development / 开发

### Modifying the Skill
1. Edit `SKILL.md` in the project root — this is the **source of truth**
2. Copy to your Claude skills directory to test:
   ```bash
   mkdir -p ~/.claude/skills/shida-danone-ppt-skill
   cp SKILL.md ~/.claude/skills/shida-danone-ppt-skill/SKILL.md
   ```

### Adding Scripts
1. Add to `scripts/`, follow `kebab_case.py` or `camelCase.mjs` naming
2. Document in `AGENTS.md`

---

## Known Issues / 已知问题

> 详见 [**ROADMAP.md**](ROADMAP.md) 的完整分析和优化计划。

### P1 — Native PPTX 图片替换
- `image-content` / `section-photo` intents 在 HTML 路径已渲染，在 native PPTX 路径尚未实现图片替换到 `<p:pic>`

### P1 — Strategic 布局 native PPTX 映射
- Strategic 布局（decision-grid, flywheel, journey 等）尚未映射到 native PPTX
- 当前策略：strategic 模式默认输出 HTML 路径

### P2 — Export 交互性
- PDF 输出为矢量但不可编辑；Image PPTX 不可编辑
- 真正可编辑的路径仅 native PPTX

### P2 — Input adapter 智能度
- Script 格式拆分基于段落分块，部分 `待补充` 字段仍需要手动完善

---

## Roadmap / 路线图

See [**ROADMAP.md**](ROADMAP.md) for the full v6.0 status and next-phase plans, including:
- Phase 1: Native PPTX 图片替换 + 布局扩展
- Phase 2: Input adapter 增强
- 每日开发验证流程

### Running Smoke Tests
```bash
# Native path
python scripts/brief_to_native_deck.py --title "Smoke" --brief-file smoke-tests/brief-native/brief.md --slides 6 --out /tmp/smoke.pptx

# HTML path
python scripts/notes_to_danone_deck.py --notes smoke-tests/dht-lab-notes/Slide\ notes.md --out-dir /tmp/smoke --brand-line "Smoke Test"
node scripts/export_deck_pdf.mjs --slides /tmp/smoke/slides --out /tmp/smoke/deck.pdf --width 1280 --height 720
```

---

## Documentation Index / 文档索引

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Project overview, install, quick start | Humans |
| `SKILL.md` | Design rules, self-check, output paths | Claude AI |
| `AGENTS.md` | Commands, architecture, file structure | Developers |
| `CHANGELOG.md` | Version history | Everyone |
| `backlog/` | Decision records (e.g., abandoned paths) | Developers |

---

## License / 许可证

MIT
