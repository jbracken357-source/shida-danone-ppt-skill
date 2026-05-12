# Shida Danone PPT Skill / Shida Danone PPT 技能

> **EN**: Danone-style corporate presentation generator. Photo-first layouts, multi-color category themes, "One Planet. One Health" brand DNA. v4.0.0.
> **CN**: Danone 风格企业演示文稿生成器。摄影优先布局、多色分类主题、"One Planet. One Health" 品牌基因。v4.0.0。

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
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies (stdlib only)
│
├── scripts/               # Build & export scripts
│   ├── brief_to_native_deck.py     # Brief → native PPTX
│   ├── notes_to_danone_deck.py     # Notes → HTML deck (+ optional native)
│   ├── build_native_pptx.py        # Core engine (XML clone + text swap)
│   ├── export_deck_pdf.mjs         # HTML → vector PDF
│   ├── export_deck_pptx.mjs        # HTML → image PPTX
│   └── profile_danone_template.py  # Template analyzer
│
├── templates/             # Design system
│   ├── tokens.css         # CSS design tokens
│   ├── layout-map.json    # Intent → layout mapping
│   └── danone-template-manifest.json
│
├── assets/
│   └── deck_index.html    # Reusable deck shell
│
├── Danone Real Templates/
│   └── Standard Danone Template.pptx
│
├── backlog/               # Decision records
└── smoke-tests/           # Test inputs
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
# Generate HTML slides
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
  --out-dir ./deck \
  --brand-line "DHT Lab · Danone"

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

### P0 — HTML Deck 视觉效果
- 字体使用 Arial Narrow fallback，廉价且无品牌感（计划改用 Playfair Display + Inter）
- 布局单调，只有 5 种对称卡片模式
- 图片占位符像 wireframe，不像 editorial layout
- Flat 纯色，无 gradient/shadow/视觉深度
- 所有页都是 light 主题，没有 dark 页制造呼吸

### P0 — Native PPTX 功能
- 输出文件 15-20MB：复制了整个模板（649 文件），未清理未使用资源
- `contents` / `three-column` intent 内容映射 broken
- slide number 显示原始模板页码而非输出页码
- `image-content` / `section-photo` intents 未实现

---

## Roadmap / 路线图

See [**ROADMAP.md**](ROADMAP.md) for the full v4.0 optimization plan, including:
- Phase 1: HTML Deck visual重构（字体、布局、图片占位符、CSS 架构、视觉深度、主题节奏）
- Phase 2: Native PPTX 修复（资源清理、映射修复、slide number、悬空引用）
- Phase 3: 文档同步
- 每日开发验证流程（明天开工直接用）
3. Update this README if user-facing

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
