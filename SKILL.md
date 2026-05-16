---
name: shida-danone-ppt-skill
description: Generate Danone-branded presentation decks from outlines, briefs, or scripts. Parses content, assigns layouts/themes, outputs editable PPTX, HTML, or PDF. Use when the user asks to create slides, presentations, decks, PPTX, PDF reports, corporate decks, ESG presentations, product launches, VP review decks, or mentions "达能PPT"、"演示文稿"、"汇报"、"路演"、"品牌演示"、"Danone presentation"、"slide deck"、"powerpoint". Always use this skill for any Danone-branded or corporate presentation task — even if the user just says "帮我做个PPT" or "做几页slides".
when_to_use: 用户提供PPT大纲/笔记/脚本需要转成幻灯片；需要做达能品牌风格的演示文稿；需要做可编辑PPTX、HTML翻页幻灯片或可打印PDF；需要做VP评审/战略对齐/产品发布/ESG报告等 corporate deck；用户提到 "达能PPT"、"做个PPT"、"帮我做几页slides"、"Danone deck"、"corporate presentation"、"brand deck"、"ESG report deck"。个人talk/发布会风格网页PPT → 用 guizang-ppt-skill；深色dashboard → 用 huashu-design。
---

# Shida Danone PPT Skill

> 从大纲/笔记/脚本生成达能品牌 PPT。三选一路径：可编辑 PPTX / HTML 翻页幻灯片 / 可打印 PDF。

## Step 0: 路由决策

读输入，判断 deck 类型，选择对应脚本。完整命令参考见 `AGENTS.md`。

| 输入类型 | 识别特征 | 脚本 |
|---------|---------|------|
| **自由形式** | 话题列表、文章、大纲、bullet points | `scripts/input_adapter.py` 标准化 → `brief_to_native_deck.py` |
| **结构化笔记（VP 评审/战略对齐）** | 标题含 `## Slide N — Title` 或 `## Slide N：Title` | `scripts/notes_to_danone_deck.py --mode strategic` |
| **场景笔记（Science Lab）** | 标题含 `## 场景 N｜Name` | `scripts/notes_to_danone_deck.py --mode scenario` |

**不确定用哪个？** 先跑 `input_adapter.py` 标准化输入，再用 `notes_to_danone_deck.py --mode auto` 自动检测。

**输出格式**：在 Step 1 询问用户选择 PPTX / HTML / PDF / All。

---

## Workflow

### Step 1: 确认输出格式

- **PPTX** — 真实达能模板，PowerPoint 内可编辑文字
- **HTML** — 浏览器预览，品牌样式 + 交互导航
- **PDF** — 从 HTML 导出的矢量 PDF（可打印、可搜索）
- **All** — 三种格式同时生成

### Step 2: 解析与规划

```bash
# 自由形式：先标准化
python scripts/input_adapter.py --input brief.md --out /tmp/normalized.md
```

```bash
# 战略 / VP 评审
python scripts/notes_to_danone_deck.py \
  --notes /tmp/normalized.md --out-dir ./deck --mode strategic \
  --brand-line "Brand X · Danone" [--native-pptx ./deck/deck.pptx]
```

```bash
# 场景 / Science Lab
python scripts/notes_to_danone_deck.py \
  --notes /tmp/normalized.md --out-dir ./deck --mode scenario \
  --brand-line "Brand X · Danone" [--native-pptx ./deck/deck.pptx]
```

**规划 theme rhythm**（生成前必须做）：
- 封面 = hero，封底 = hero
- 不允许 3+ 页连续同主题（light/dark/hero）
- 6+ 页 deck 每 3-4 页至少 1 页 hero
- 节奏规则详见 `references/layouts.md`

### Step 3: 生成幻灯片

布局注册表见 `references/layouts.md`（战略布局 8 种 + 场景布局 7 种）。
主题配色见 `references/themes.md`。
组件规格见 `references/components.md`。

HTML 生成在 Step 2 命令中自动完成（`./deck/index.html`）。
PPTX 需要加 `--native-pptx` 参数。

### Step 4: 视觉验证

按 `references/visual-verification.md` 逐项检查：
1. 封面：实色 `#005EB8` + 白圆 + 居中标题
2. Theme rhythm：grep theme classes，确认交替
3. 字体：headline 显示 serif（Playfair Display），body 显示 sans-serif（Inter）
4. 组件：accent bar 匹配主题色，product card 白底 + 顶栏
5. 封底：同封面格式，标题为 "THANK YOU"

### Step 5: 导出（如需 PDF 或图片 PPTX）

```bash
# HTML → PDF
node scripts/export_deck_pdf.mjs --slides ./deck/slides/ --out ./deck/deck.pdf --width 1280 --height 720

# HTML → 图片 PPTX（不可编辑）
node scripts/export_deck_pptx.mjs --slides ./deck/slides/ --out ./deck/deck-image.pptx --width 1280 --height 720
```

### Step 6: 自检

跑 `references/checklist.md`（P0/P1/P2/P3 分级）。P0 全部通过才能交付。

---

## Resource Files

| 文件 | 何时读 |
|------|--------|
| `references/layouts.md` | Step 2 规划布局 + theme rhythm |
| `references/themes.md` | Step 2 选主题色 + 品牌色 |
| `references/components.md` | Step 3 生成组件（封面/卡片/表格/引用块等） |
| `references/visual-verification.md` | Step 4 验证输出 |
| `references/checklist.md` | Step 6 自检 |

---

## Core Principles

1. **内容匹配布局**：战略 deck 用决策矩阵 + storyline flow；科学 lab deck 用场景卡片 + 数据可视化
2. **摄影优先**：每页需要照片占位符或数据可视化——纯文字页不符合达能品牌（摄影和数据是品牌语言的核心）
3. **多色主题**：内容匹配颜色（Gut=绿 `#00A651` / Sport=橙 `#F26522` / Clinical=粉 `#E6007E` / Water=青 `#00B2A9` / Corporate=蓝 `#005EB8`），场景 deck 如果全蓝会显得单调
4. **不使用假数据**：达能高管评审时对未经证实的数据提出质疑，用 "Data TBD" / "数据待补充" 占位符
5. **One Planet. One Health**：品牌 DNA，出现在封面、每页 footer、封底
6. **封面/封底格式**：实色 `#005EB8` 背景 + 白色圆 + 居中标题，详见 `references/components.md`
7. **不使用装饰插画**：达能是摄影/数据可视化驱动的品牌——图标和 clipart 会削弱专业感

---

## Common Mistakes

| 错误 | 为什么容易发生 | 怎么避免 |
|------|--------------|---------|
| **全蓝 PPT** | 默认 corporate blue 容易一路用到所有页 | 用 `references/themes.md` category themes 按内容匹配颜色 |
| **实心 product card** | 直接用主题色做卡片背景很直观 | product card 必须白底 + 顶栏 accent（设计系统的硬性约定） |
| **假数据** | 编百分比让 deck 看起来更完整 | 达能高管会质疑数据来源——用 "Data TBD" 占位 |
| **封面格式错误** | 用了渐变 hero 而非达能官方格式 | 必须是实色 `#005EB8` + 白圆 + 居中标题 |
| **缺少 "One Planet. One Health"** | 容易被遗忘 | 品牌 DNA 三处必须有：封面、每页 footer、封底 |
| **单调主题** | 每页默认 light blue 最安全 | 每页必须有 theme class（light/dark/hero），按 `references/layouts.md` 节奏交替 |
| **战略布局塞进场景模板** | 内容判断不清 | VP 评审用 decision grid，科学 lab 用三栏场景卡片——不要混用 |
| **所有页同一布局** | 用同一个 render_XXX 最省事 | 战略 deck 需要 varied layouts（grid/table/flow/comparison），见 `references/layouts.md` |
