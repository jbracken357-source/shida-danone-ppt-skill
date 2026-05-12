# AGENTS.md — Shida Danone PPT Skill

> Source of truth for project commands, architecture, and development workflow.
> 项目命令、架构和开发流程的单一真相源。

---

## Project Overview / 项目概述

Danone-style corporate presentation generator. Dual-path architecture:
- **Native PPTX path**: clones real Danone template XML, swaps text → editable in PowerPoint
- **HTML deck path**: renders CSS slides → export to vector PDF or image PPTX

Version: 4.0.0

---

## Quick Commands / 命令速查

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
├── SKILL.md                  # Claude skill definition (source of truth)
├── AGENTS.md                 # This file — commands & architecture
├── CHANGELOG.md              # Version history
├── package.json              # Node dependencies
├── requirements.txt          # Python deps (stdlib only, documented)
├── .gitignore
│
├── scripts/                  # Build & export scripts
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
    │   └── brief.md
    └── dht-lab-notes/
        ├── Slide notes.md
        └── test-notes.md
```

---

## Architecture / 架构

### Dual-Path Design

```
Input (brief / notes)
        │
        ├─→ brief_to_native_deck.py ──→ build_native_pptx.py ──→ *.pptx (editable)
        │
        └─→ notes_to_danone_deck.py ──→ HTML slides + index.html
                                              │
                                              ├─→ export_deck_pdf.mjs ──→ *.pdf
                                              └─→ export_deck_pptx.mjs ──→ *.pptx (image)
```

### Native PPTX Path
- **Strengths**: Real template masters/layouts, editable text, small file size
- **Limitations**: Image replacement not yet implemented (falls back to HTML path)
- **Core engine**: `build_native_pptx.py` clones slide XML from the real template and replaces text runs

### HTML Deck Path
- **Strengths**: Full CSS styling, photo placeholders, data viz, any layout possible
- **Limitations**: PDF text is vector but not editable; image PPTX is not editable
- **Canvas size**: 1280×720px (pptx-canvas) for export; 1920×1080px (slide-canvas) for browser preview

---

## Known Issues / 已知问题

> 详见 `ROADMAP.md` 的完整分析和优化计划。

### P1 — HTML Deck 待完善
- 9 种新布局中部分尚未在 `plan_from_notes` 中自动生成（当前仍使用原有 5 种布局）
- Dark 主题页面样式已定义但尚未在生成逻辑中强制插入（需 6 页以上 deck）
- `.img-slot` 占位符尚未支持直接传入真实图片路径

### P1 — Native PPTX 待完善
- `image-content` / `section-photo` intents 仍标记为 `native_supported: false`（图片替换需手动处理）
- 资源清理可能过于激进，某些边缘 case 的字体文件可能被误删（已保留核心文件）
- 未对清理后的文件数做下限验证（当前 ~87 文件，目标 < 100）

---

## Development Workflow / 开发流程

### 每日开工 checklist（明天开始用）

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
   # Step 1: 生成测试 deck
   python scripts/notes_to_danone_deck.py \
     --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
     --out-dir /tmp/test-html --brand-line "DHT Lab · Danone"

   python scripts/brief_to_native_deck.py \
     --title "Test" --brief-file smoke-tests/brief-native/brief.md \
     --slides 6 --out /tmp/test-native.pptx

   # Step 2: HTML 视觉验证（打开浏览器）
   # 检查：字体加载、主题节奏、图片占位符、视觉深度

   # Step 3: Native PPTX 功能验证
   ls -lh /tmp/test-native.pptx        # 期望 < 5MB
   python -c "import zipfile; z=zipfile.ZipFile('/tmp/test-native.pptx'); print(len(z.namelist()), 'files')"  # 期望 < 100

   # Step 4: Export 验证
   node scripts/export_deck_pdf.mjs --slides /tmp/test-html/slides --out /tmp/test.pdf --width 1280 --height 720
   node scripts/export_deck_pptx.mjs --slides /tmp/test-html/slides --out /tmp/test-image.pptx --width 1280 --height 720

   # Step 5: 文档同步检查
   # - SKILL.md 的 design rules 与代码一致
   # - AGENTS.md 的命令速查与代码一致
   # - CHANGELOG.md 已记录变更
   ```

### Modifying the Skill
1. Edit `SKILL.md` (root directory — this is the source of truth)
2. Test by copying to `~/.claude/skills/shida-danone-ppt-skill/SKILL.md`
3. Run the smoke test workflow above

### Adding a New Script
1. Place in `scripts/`, follow existing naming convention
2. Add command to AGENTS.md Quick Commands section
3. Update README.md if user-facing

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

For full design rules, see `SKILL.md`.
