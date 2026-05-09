---
name: shida-danone-ppt-skill
description: Use when creating Danone-inspired corporate presentation decks, ESG reports, product launch decks, Danone-style HTML slides, PDF exports, image PPTX exports, or editable PPTX exports.
version: 2.1.0
author: Shida Fu
tags: [presentation, slides, html, danone, corporate, design-system, pptx, pdf]
---

# Shida Danone PPT Skill

> TL;DR：真实 Danone 企业 PPT 模板优先。正式可编辑 PPTX 先复用 `Danone Real Templates/Standard Danone Template.pptx` 的 master/layout/placeholders；HTML 多文件管线用于预览、PDF、图片铺底和无法映射到真实模板的兜底页面。要走 HTML→editable PPTX 时才从第一行遵守4条硬约束；默认不要在 editable 上再铺截图覆盖层。

## Danone 品牌资产协议（动手前必做）

> 达能是 "摄影驱动" 品牌，禁止装饰性插图。涉及真实 Danone 项目时，必须采集真实品牌资产。

### Step A · 采集 Danone Logo
- 从 danone.com 首页或 /brand 页面提取 inline SVG 或 PNG
- 保存为 `assets/danone-logo.svg`
- 至少准备两个版本：深底白色版 + 浅底蓝色版
- **必须验证文件真的是图片/SVG**：PNG 文件头应为 `89 50 4E 47`，SVG 应包含 `<svg`。如果 `.png` 实际是 HTML（常见于下载失败/权限页），不要使用，改用文字品牌占位并向用户说明。

### Step B · 采集官方产品图/摄影
- 从 danone.com 产品页或 press kit 下载高清产品图
- 优先真实摄影（达能摄影驱动），不用 AI 生成或 CSS 剪影
- 如果找不到合适的图，用诚实 placeholder（灰块+文字标签）

### Step C · 验证设计系统
- 色值/字体 token 已在下方 Danone 设计系统 中固化，无需每次重新采集
- 如需新增 accent 色，先对照官网验证再使用

---

## 何时使用

- ✅ 达能/企业风格汇报、研究报告演示、ESG报告、产品发布
- ✅ 需要同时交付 HTML + PDF + PPTX 的正式报告 deck
- ❌ 个人分享/演讲 → 用 guizang-ppt-skill
- ❌ 创意设计/原型 → 用 huashu-design
- ❌ 暗色仪表盘 → 达能是 light-first

---

## 真实模板保真协议（优先级最高）

> 当仓库中存在 `Danone Real Templates/*.pptx` 时，它们是真实 Danone 企业模板，比官网 token 和手写 CSS 规则优先。

### Step 0 · Profile 真实模板

在开始正式 PPTX 生成前，先确认 manifest 是最新的：

```bash
python scripts/profile_danone_template.py "Danone Real Templates/Standard Danone Template.pptx" --out templates/danone-template-manifest.json
python -m unittest tests.test_profile_danone_template tests.test_layout_map tests.test_build_native_pptx -v
```

manifest 必须记录：
- slide size: 13.333 × 7.5 inch
- fonts: `Danone One Condensed` / `Danone One Light`
- 真实 themes、layouts、placeholders
- layout families，例如 `two-content`、`three-column`、`full-image`、`big-message`

### Step 0.5 · 从描述生成 native PPTX slide plan

正式可编辑 PPTX 不从 HTML 导出。用户只给材料描述或任务描述时，先用 brief 入口生成可审阅的 JSON plan 和 template-native PPTX：

```bash
python scripts/brief_to_native_deck.py --title "Deck title" --brief-file brief.md --slides 6 --out deck-native.pptx --out-plan plan.json
```

这个入口只重组用户提供的信息；材料缺口必须保留“待补充”占位，不编造业务事实。它默认只选当前真实模板样张能稳定复制的 native intent。已有完整页级规划时，再手写或编辑 JSON plan：

```json
{
  "slides": [
    {
      "intent": "opening-cover",
      "content": {
        "title": "Deck title",
        "subtitle_or_date": "May 2026"
      }
    },
    {
      "intent": "two-column",
      "content": {
        "title": "Two operating shifts",
        "left_content": "Left column",
        "right_content": "Right column"
      }
    }
  ]
}
```

`intent` 必须来自 `templates/layout-map.json`。builder 会优先找 preferred layout 对应的真实 sample slide；如果 preferred layout 没有 sample slide，则按 fallback layout 找可复制的真实 sample slide。

### Step 1 · 用 layout-map 选真实版式

`templates/layout-map.json` 是内容意图到真实模板 layout 的桥：

| 意图 | 用途 | 生成要求 |
|------|------|----------|
| `opening-cover` | 封面 | 使用真实 Title Slide layout，不重画圆形/图片结构 |
| `contents` | 目录 | 保留模板编号和图片结构 |
| `section-photo` | 章节/摄影页 | 当前 native builder 不替换图片；走 HTML fallback，或等实现原生图片替换后再纳入 native |
| `big-message` | 核心观点 | 使用模板 highlighter/underline 语言 |
| `two-column` | 对比/论证 | 填充真实左右 placeholders |
| `three-column` | 三支柱/框架 | 填充真实三栏 placeholders |
| `image-content` | 图文页 | 当前 native builder 不替换图片；走 HTML fallback，避免误用模板样张图片 |
| `chart-or-table` | 数据页 | 优先原生 PPT 图表/表格 |
| `closing` | 结束页 | 使用真实 Closing Slide layout |

### Step 2 · 生成策略

1. **正式可编辑 PPTX**：复制真实模板中的 layout 或 sample slide，填充已有 placeholders。不要用 HTML 坐标重建模板几何。
2. **浏览器/PDF/图片 PPTX**：可继续用多文件 HTML 管线，因为 Chromium 渲染对视觉最稳定。
3. **HTML→editable PPTX**：仅用于没有对应真实 layout 的自定义页，并严格遵守下方 4 条硬约束。
4. **质量门**：生成后用 LibreOffice/PowerPoint 渲染抽查，确认字体、色带、页码、图片裁切、placeholder 溢出都与模板一致。

### Step 3 · 不要做的事

- 不要把真实模板截图当背景再覆盖文本作为默认方案；这会牺牲编辑体验。
- 不要用官网 token 替代模板内嵌 theme/font，除非目标是 HTML 预览或模板缺失。
- 不要混用其他企业模板或手写新 master。
- 不要手写 logo、页码、边栏色条；这些应从 master/layout 继承。

## Danone 设计系统

> 以下 token 只用于 HTML 预览和 fallback 页面。正式 PPTX 以 `templates/danone-template-manifest.json` 和真实 `.pptx` 模板为准。

> 以下 token 对照 2026-05-08 danone.com 官网 CSS 验证。

### 色板
| Token | 色值 | 用途 |
|-------|------|------|
| `--dn-blue` | `#005EB8` | 主品牌色、Hero背景、激活态、Bullet |
| `--dn-blue-dark` | `#002677` | 深色按钮、深色文字 |
| `--dn-blue-mid` | `#0068CC` | Hover |
| `--dn-blue-light` | `#0085EB` | Focus、链接 |
| `--dn-green` | `#207B3B` | 可持续/正向指标 accent |
| `--dn-tint` | `#CCDFF1` | 浅蓝底（表格header、日期标签） |
| `--dn-text` | `#262627` | 正文/标题 |
| `--dn-text-secondary` | `rgba(0,0,0,0.6)` | 元数据 |
| `--dn-border` | `rgba(0,0,0,0.15)` | 分隔线 |

### 字体
- Display: `Inter Tight`, wght 700
- Heading: `Inter`, wght 600
- Body: `Inter` / `Noto Sans SC`(中文), wght 400
- Google Fonts: `Inter:wght@400;500;600;700&Inter+Tight:wght@600;700&Noto+Sans+SC:wght@400;500;600;700`

### 组件签名
| 组件 | 规则 |
|------|------|
| 按钮 | `border-radius: 6.25rem`（pill 药丸形）|
| 卡片 | 扁平无阴影 |
| 表格 | 表头 `#CCDFF1` + `#005EB8` 底边 |
| Hero | 纯色 `#005EB8`，**无渐变** |
| 图片 | `border-radius: .75rem`（12px）|
| Bullet | 蓝色圆点 `#005EB8`，`border-radius: 50%` |
| **禁止** | CSS gradient、彩色badge/tag、装饰性插图 |

### 间距
`3, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96` (px)

### 布局
Max 1280px / Content 1120px / Padding 80px / Section vertical 80-96px

---

## 工作流程

### Step 0 · 需求澄清（动手前必做）

**用户已给完整大纲+素材** → 跳过，进 Step 1。
**只给主题或模糊想法** → 用下表一次性对齐，**等用户批量答完再往下走**：

| # | 问题 | 决定什么 |
|---|------|---------|
| 1 | 主题？（ESG/产品发布/市场策略/年度汇报） | 叙事方向 |
| 2 | 受众+场景？（内部/外部/投资人） | 语言风格和深度 |
| 3 | 分享时长？ | 页数：15min≈10页, 30min≈20页, 45min≈25-30页 |
| 4 | 有素材吗？（报告/旧PPT/数据/图片） | 有就用，没有帮搭 |
| 5 | 交付格式？ | 见下方决策树 |

#### 交付格式决策树

```
需要同事改文字？
  ├─ 是 → 真实模板 PPTX → 复制 `Danone Real Templates/*.pptx` 的 layout/sample slide 并填充 placeholders
  └─ 否 → 要PDF吗？
           ├─ 是 → 浏览器+PDF → 无特殊约束
           └─ 否 → 浏览器播放 或 PPTX图片铺底 → 无特殊约束
```

**用户说"都需要"** → 正式可编辑 PPTX 仍以真实模板为主；HTML 只作为 PDF/浏览器预览或无法映射到真实 layout 的 fallback。

#### PPTX可编辑的 4 条硬约束

1. body 固定 `1280px × 720px`（960pt × 540pt 等效，用 px 而非 pt —— Chromium 对 pt 单位有渲染偏差）
2. 所有文字在 `<p>` 或 `<h1>`-`<h6>` 里（禁止 div/span 直接承载主文字）
3. `<p>`/`<h*>` 无 background/border/shadow（放外层 div）
4. 无 CSS 渐变，div 无 background-image（用 `<img>` 标签）

#### PPTX 可编辑默认策略

- 默认生成**template-native editable PPTX**：复用真实 Danone 模板的 master/layout/placeholders，文字和形状可直接编辑。
- 只有当某页无法稳定映射到 `templates/layout-map.json` 的真实 layout 时，才走 HTML→editable PPTX fallback（`--mode editable`）并遵守下方 4 条硬约束。
- 不要默认在 editable 上铺一层全页截图。这样虽然视觉完全保真，但会挡住底层可编辑对象，用户编辑体验差。
- 只有当用户明确要求“打开效果必须和 PDF 逐像素一致，编辑性次要”时，才做“底层 editable + 顶层截图”的 hybrid 方案，并明确告知编辑前要移开/删除顶层截图。
- editable 与 PDF 允许有轻微字体度量、圆角、边框渲染差异；只要整体布局、层级、颜色和可读性一致，优先保留纯 editable。

🛑 **检查点 1**：确认交付格式后再进 Step 1。

### Step 1 · 叙事弧 + 节奏规划表

叙事弧模板：
```
钩子(Hook)  → 1页  : 反差/问题/硬数据
定调(Context)→ 1-2页: 背景/为什么讲这个
主体(Core)   → 3-5页: 核心内容
转折(Shift)  → 1页  : 打破预期
收束(Takeaway)→ 1-2页: 金句/行动建议
```

**产出物**：节奏规划表

| 页号 | 主题角色 | 布局类型 | 背景变体 |
|------|----------|---------|---------|
| 1 | 封面 | Hero Cover | hero-blue |
| 2 | 执行摘要 | KPI卡片网格 | white |
| ... | ... | ... | ... |

**节奏规则**：每 3-4 页插一个 Hero 页；Hero 与正文 2-3:1 交错；不连续 3 页同主题。

🛑 **检查点 2**：节奏规划表发给用户确认，**等回复**再继续。

### Step 2 · 生成架构选择

先按交付目标选择架构，不要无条件进入 HTML 多文件管线：

| 目标 | 主架构 | 规则 |
|------|--------|------|
| 正式可编辑 PPTX | **真实模板 native PPTX** | 从 `Danone Real Templates/Standard Danone Template.pptx` 复制匹配的 layout 或 sample slide，填充原生 placeholders。不要用 HTML 坐标重建模板几何。 |
| 浏览器播放 / PDF / PPTX 图片铺底 | HTML 多文件 | 用下方多文件架构；它是预览和视觉保真的渲染管线，不是正式 editable PPTX 的默认来源。 |
| 无真实 layout 的特殊页 | HTML→editable fallback | 只有 layout-map 无法覆盖时使用；从第一行遵守 4 条硬约束。 |

HTML 分支不采用 guizang-ppt-skill 的单文件方案，原因：

| 维度 | guizang 单文件（`<section>` 切换） | huashu 多文件（iframe 拼接） |
|------|------------------------------------|---------------------------|
| CSS 作用域 | ❌ 全局，一页样式影响所有页 | ✅ iframe 天然隔离 |
| 单页验证 | ❌ 必须打开整个 deck | ✅ 双击 slide HTML 直接看 |
| 并行开发 | ❌ 一个文件多 agent 改会冲突 | ✅ 多 agent 并行零冲突 |
| PDF/PPTX 导出 | ❌ 无内置脚本 | ✅ 完整导出管线 |
| 调试 | ❌ 一处 CSS 出错全 deck 翻车 | ✅ 一页出错只影响自己 |
| 内嵌交互 | ✅ 跨页共享状态简单 | 🟡 需 postMessage |

**结论**：正式可编辑 PPTX 走真实模板 native 路径；只有 HTML 分支使用多文件架构。guizang 单文件的「WebGL 背景」「横向翻页」在企业场景是负担不是能力。

HTML 分支目录结构：
```
达能Deck/
├── index.html              # 拼接器（本 skill assets/deck_index.html）
├── shared/
│   └── tokens.css          # 见下方
└── slides/
    ├── 01-cover.html
    ├── 02-...
    └── ...
```

### Step 3 · 生成 tokens.css（仅 HTML 分支）

只有在 Step 2 选择浏览器/PDF/图片铺底/HTML fallback 时才生成 `tokens.css`。正式 template-native PPTX 不使用这里的 CSS token，必须继承真实模板 theme/font/layout。

**HTML 分支可直接复制 `templates/tokens.css`** 到项目 `shared/tokens.css`，或按下方代码块手写。所有 slide 引用此文件。

```css
*, *::before, *::after { box-sizing: border-box; }
:root {
  --dn-blue: #005EB8; --dn-blue-mid: #0068CC;
  --dn-blue-dark: #002677; --dn-blue-light: #0085EB;
  --dn-green: #207B3B; --dn-tint: #CCDFF1;
  --dn-text: #262627; --dn-text-secondary: rgba(0,0,0,0.6);
  --dn-border: rgba(0,0,0,0.15);
  --dn-font: "Inter","Noto Sans SC",system-ui,sans-serif;
  --dn-font-display: "Inter Tight","Inter","Noto Sans SC",sans-serif;
}
body { font-family: var(--dn-font); color: var(--dn-text); background: #fff; margin: 0; line-height: 1.15; -webkit-font-smoothing: antialiased; }
body.slide-canvas { width: 1920px; height: 1080px; overflow: hidden; }
body.pptx-canvas { width: 1280px; height: 720px; overflow: hidden; }
```

> ⚠️ **`box-sizing: border-box` 不可省**。2026-05-09 实测：不加这行，所有带 padding 的 content slide（KPI grid、表格、流水线等）在 editable 模式导出时会报 "HTML content overflows body by 83.3pt horizontally and 59.3pt vertically"，全量失败。

### Step 4 · Junior pass（结构 + 占位）

**做什么**：出 2-3 页骨架（封面 + 核心内容页 + 数据页），先证明选定架构能保留 Danone 真实模板语言。

**template-native PPTX 输出规格**：
- 从 `templates/layout-map.json` 为每页选择真实 layout intent（例如 `opening-cover`、`two-column`、`chart-or-table`）。
- 复制真实模板 layout 或 sample slide，不重画 logo、页码、色带、圆形、图片裁切结构。
- 只填充已有 placeholders；缺素材时保留诚实 placeholder，不编造内容。
- Junior pass 交付一个可打开的 `.pptx` 骨架，并说明每页使用的 layout 名称。

**HTML 分支输出规格**：
- 每页一个独立 HTML 文件（多文件模式）或 `<section>`（单文件）
- 布局结构完整（网格/分栏/留白比例正确）
- 内容用灰块 + 文字标签占位（如 `[此处放ESG数据图表]`），**不编造内容**
- 达能 token（色值/字体/圆角）已就位

**展示方式**：template-native PPTX 列出 PPTX 路径和每页 layout；HTML 分支列出文件路径，让用户在浏览器打开对应文件查看效果。

🛑 **检查点 3**：用户确认 Junior pass 后再进 Full pass。
- 用户说 OK → 继续 Step 5
- 用户要改布局/风格 → 按反馈调整，重新展示
- 用户说"方向不对，换主题" → 回 Step 1 重做叙事弧

### Step 5 · Full pass

- 填充所有页内容（用用户素材或确认后的假设）
- 逐页完成后在浏览器打开验证
- 检查：字体加载、图片路径、布局不溢出、达能风格一致性

### Step 6 · 导出（最终交付物）

**HTML 是中间产物，用户最终拿到的是 PDF 或 PPTX。导出步骤必须实际执行并验证成功，不能只列命令。**

#### 前置：安装依赖

脚本已内置在本 skill 的 `scripts/` 目录下，不需要从外部拷贝。只需安装 npm 依赖：

```bash
npm install playwright pdf-lib pptxgenjs sharp
```

#### 视觉验证（可选但推荐）

在正式导出前，用 `scripts/verify.py` 对 index.html 做逐页截图验证，确认翻页、字体加载和控制台状态：

```bash
python scripts/verify.py index.html --slides 10 --output ./screenshots/
```

截图会输出到 `screenshots/` 目录，文件名 `index-slide-01.png` ~ `index-slide-10.png`。肉眼确认后再跑导出。

**注意**：`index.html` 截图会包含外层舞台/counter，适合验证翻页链路，不适合最终视觉验收。最终视觉验收应直接打开 `slides/*.html` 截图，或把 PDF/PPTX 导出后再渲染成图片对比。

#### Playwright Chromium 通道适配

WSL/Ubuntu 环境下 `npx playwright install` 常因 headless-shell 下载超时失败。本 skill 的导出脚本已预设为 `chromium.launch({ channel: 'chromium' })`，使用系统 `chromium-browser`。如果目标环境是 macOS，脚本会自动切换为 `chrome` 通道。

#### 导出执行

根据 Step 0 确认的交付格式，**实际运行**对应导出命令并检查输出：

| 目标 | 命令 | 成功标志 |
|------|------|---------|
| 正式可编辑 PPTX | `python scripts/build_native_pptx.py --plan plan.json --out deck-native.pptx` | 输出 `Wrote ... (N native slides)`；PPTX 打开后仍继承 Danone master/layout，文字可编辑，未出现 HTML 重建痕迹 |
| PDF | `node scripts/export_deck_pdf.mjs --slides slides/ --out deck.pdf --width 1280 --height 720` | 输出 `✓ Wrote ...pdf (X KB, N pages, vector)` |
| PPTX 图片铺底 | `node scripts/export_deck_pptx.mjs --slides slides/ --out deck-image.pptx --mode image --width 1280 --height 720` | 输出 `✓ Wrote ...pptx (N slides, image mode)` |
| HTML→editable fallback | `node scripts/export_deck_pptx.mjs --slides slides/ --out deck-editable.pptx --mode editable` | 输出 `✓ Wrote ...pptx (N/N slides, editable mode)` |

**默认按用户要的格式导出**。用户要正式可编辑 PPTX 时，不要默认用 `scripts/export_deck_pptx.mjs --mode editable` 替代真实模板 native 生成；该脚本只属于 HTML fallback。

**重要**：当 HTML 使用 `body.pptx-canvas { width:1280px; height:720px; }` 时，PDF 和 image PPTX 也默认用 `--width 1280 --height 720`，这样三种产物尺寸一致。只有用户明确要求高清 PDF 时才生成额外 1920×1080 版本。

**⚠️ PPTX 可编辑模式前置检查（导出前必须过）**：

editable 模式用 `scripts/html2pptx.js` 把 DOM 逐元素翻译为 PowerPoint 对象，HTML 不符合 4 条硬约束会全量失败。导出前先跑这个检查：

```bash
# 检查1: body 尺寸（应 = 总 slide 数）
grep -rl 'class="pptx-canvas"' slides/  | wc -l
# 检查2: 文字包裹
grep -rP '<(div|span)[^>]*>[^<]{20,}<' slides/    # 有输出 = 有 div/span 直接承载文字
# 检查3: 渐变
grep -rl 'gradient' slides/                         # 有输出 = 有渐变
# 检查4: <p>/<h*> 上无样式
grep -rP '<(p|h[1-6])[^>]*(background|border|box-shadow)' slides/  # 有输出 = 违规
# 检查5: body 用 px 不用 pt
grep -rP 'width:\s*\d+pt' slides/                   # 有输出 = 用了 pt 单位
```

如果检查不通过，**不跑 editable 模式**，退回图片铺底模式（image mode），并向用户说明原因。

**PPTX 可编辑模式的 4 条硬约束（回顾）**：
1. body 固定 `1280px × 720px`（960pt × 540pt 等效，用 px 而非 pt —— Chromium 对 pt 单位有渲染偏差）
2. 所有文字在 `<p>` 或 `<h1>`-`<h6>` 里（禁止 div/span 直接承载主文字）
3. `<p>`/`<h*>` 无 background/border/shadow（放外层 div）
4. 无 CSS 渐变，div 无 background-image（用 `<img>` 标签）

🛑 **检查点 4（交付前质量门）**：PDF 和 PPTX 导出都执行成功后，按自检清单逐项确认，最终交付物发给用户。

---

## 异常处理

| 场景 | 处理 |
|------|------|
| Playwright headless-shell 下载超时 | 改 `chromium.launch({ channel: 'chromium' })`，用系统 chromium-browser |
| PPTX editable 全部失败 | 回退到 image mode（图片铺底），告知用户文字不可编辑但视觉 100% 保真 |
| PPTX image 导出后内容缩在左上角 | 脚本必须用显式 `slideW = width / 96`、`slideH = height / 96` 铺图，不能依赖 `pres.width/pres.height` |
| 项目 `package.json` 有 `"type":"module"` 导致 `html2pptx.js` require 失败 | 当前脚本会自动复制临时 `.cjs` 再加载；如果旧脚本失败，删除 `"type":"module"` 或把 `html2pptx.js` 改为 `.cjs` |
| editable 与 PDF 有轻微字体/圆角差异 | 接受纯 editable；不要为了像素一致默认加截图覆盖层 |
| PDF 导出后字体显示为方块 | Google Fonts 未加载，检查网络或改用系统字体 fallback |
| LibreOffice 转 PDF 前输出目录不存在 | 先创建输出目录；否则 Windows 上可能只返回非零状态且没有清晰错误文本 |
| 用户拒绝回答问题清单 | 按 best judgment 做 1 个主方案，交付时标注 assumption |
| 导出脚本异常 | 降级方案：`npm install playwright pdf-lib pptxgenjs sharp` 后自写导出脚本（playwright 截图 + pdf-lib 合并） |

---

## 页面布局库

| 布局 | 用途 | 达能特征 |
|------|------|---------|
| 1. Hero 封面 | 第1页 | `#005EB8` 纯色 + 白字大标题 |
| 2. 章节幕封 | 每幕开场 | 大留白 + 章节标题 |
| 3. KPI 卡片网格 | 执行摘要 | 3×2 或 2×3 卡片，无阴影，蓝色 bullet |
| 4. 左文右图 | 观点+实证 | 7:5 网格，图片圆角 .75rem |
| 5. 图片网格 | 多图对比 | 固定 height:26vh |
| 6. 流水线 | 工作流程 | 编号步骤 → 逐步点亮。**⚠️ 步骤数字必须包在 `<p>` 里：`<div class="step-num"><p>1</p></div>`** |
| 7. 数据表格 | 硬数据 | 表头 `#CCDFF1` + 底边 `#005EB8` |
| 8. 对比页 | Before/After | 左右分半，旧侧 opacity:.55 |
| 9. 大引用 | 金句/takeaway | 大留白 + Inter Tight 700 |
| 10. 收束/致谢 | 最后一页 | Hero 蓝底 + 关键行动 |

## 按钮 & CTA

```css
.btn-primary { background: var(--dn-blue); color: #fff; border-radius: 6.25rem; padding: .75rem 2rem; font-weight: 600; border: none; }
.btn-primary:hover { background: var(--dn-blue-dark); }
.btn-secondary { background: transparent; color: var(--dn-text); border: 1px solid var(--dn-text); border-radius: 6.25rem; padding: .75rem 2rem; font-weight: 600; }
.btn-secondary:hover { background: var(--dn-blue-dark); border-color: var(--dn-blue-dark); color: #fff; }
```

## 自检清单

- [ ] `<title>` 无占位符
- [ ] Google Fonts 正常加载
- [ ] 按钮 `border-radius: 6.25rem`
- [ ] 卡片无 `box-shadow`
- [ ] Hero 纯色 `#005EB8`（无渐变）
- [ ] 图片 `border-radius: .75rem`
- [ ] 表格 header `#CCDFF1` + 底边 `#005EB8`
- [ ] Bullet 蓝色圆点 `#005EB8`
- [ ] → 键翻页无空白/错位
- [ ] PPTX 可编辑：body `1280px×720px`（不是 960pt×540pt），文字全在 `<p>`/`<h*>` 里
- [ ] PPTX 图片铺底：导出后打开/渲染检查，截图必须铺满整页，不能缩在左上角
- [ ] PPTX 可编辑：优先纯 editable，无顶层全页截图覆盖
- [ ] 无 TODO / placeholder 残留
- [ ] **Playwright 截图验证**：导出前用 Playwright 截取关键页面（封面、摘要页、数据页、收束页），肉眼确认布局不溢出、字体加载正常
- [ ] **交付物对比验证**：至少抽查 PDF、image PPTX、editable PPTX 各 2-3 页，确认展示效果一致

## 反模式

- ❌ 深色主题（达能 light-first，white canvas）
- ❌ 尖角按钮 / CSS 渐变 / 卡片阴影 / 彩色 badge
- ❌ 超过 2 个 accent 色（blue + green only）
- ❌ 装饰性插图/图标（达能摄影驱动）
- ❌ **可编辑 PPTX 额外反模式**（editable 模式导出前必查）：
  - ❌ `<div>`/`<span>` 直接承载文字（必须包在 `<p>` 或 `<h1>`-`<h6>` 里）
  - ❌ `<div>` 里放裸数字/文字（如 `<div class="pipeline-num">1</div>` → 改为 `<div class="pipeline-num"><p>1</p></div>`）
  - ❌ 手动 bullet 符号 `•` `●` `✓`（用 `<ul><li>` 列表代替）
  - ❌ `<p>`/`<h*>` 上带 background/border/box-shadow 样式
  - ❌ 用 `• 文本<br>• 文本` 做多行列表（用 `<ul><li>` 代替）
  - ❌ 为了视觉保真，在 editable 顶层默认铺全页截图（这会挡住可编辑内容）

## PPTX editable 模式额外陷阱（html2pptx.js 特定）

> 这些不是 4 条硬约束的一部分，而是 html2pptx.js 运行时会额外拒绝的模式。**即使过了 4 条硬约束检查，仍可能在这几步翻车。**

| 陷阱 | 错误写法 | 正确写法 |
|------|---------|---------|
| **div 内裸数字/文字** | `<div class="pipeline-num">1</div>` | `<div class="pipeline-num"><p>1</p></div>` |
| **手动 bullet 字符** | `<p>• 渠道下沉...</p>` `<p>● 推进中 85%</p>` | `<ul><li>渠道下沉...</li></ul>` |
| **`<p>` 上带 border/background** | `<p class="btn-secondary" style="border:1px solid #fff;">下载</p>` | `<div style="border:1px solid #fff;"><p>下载</p></div>` |
| **`<span>` 承载文字** | `<span class="slide-footer">01 / 10</span>` | `<p class="slide-footer">01 / 10</p>` |
| **数字裸放在 div 里** | `<div class="step-num">1</div>` | `<div class="step-num"><p>1</p></div>` |
| **tokens.css 缺 box-sizing** | 只有 `:root` 和 body 样式 | 第一行加 `*, *::before, *::after { box-sizing: border-box; }` |
| **用 pt 而非 px 单位** | `body.pptx-canvas { width: 960pt; height: 540pt; }` | `body.pptx-canvas { width: 1280px; height: 720px; }` |

---

#### Body Class 策略（当用户要"HTML + PDF + PPTX 都导出"时）

Step 0 确认"都需要"时，按 **PPTX 可编辑** 约束写 HTML：
- body 使用 `class="pptx-canvas"`（1280px × 720px，等效 960pt × 540pt）
- 所有文字在 `<p>` / `<h*>` 里，无 div/span 裸文字
- 无渐变，tokens.css 必须包含 `box-sizing: border-box`

**⚠️ 用 px 不用 pt**：`960pt × 540pt` 在 Chromium 中有渲染偏差，导致 html2pptx 报 "overflows body by 83.3pt"。等效的 `1280px × 720px` 完全通过。

**PDF 导出分辨率取舍**：pptx-canvas 的 body 只有 1280px 宽，PDF 导出时 `--width 1920 --height 1080` 设的是视口大小，但 Playwright 截的是 body 实际尺寸（1280px）。PDF 文字保持矢量可搜，但图片 placeholder 分辨率只有 720p。这在企业报告场景是可接受的——PDF 核心是文字内容，不是图片质量。

**如果用户明确要高清 PDF（1920px）**：需要生成两套 HTML——一套 `slide-canvas`（1920×1080）用于 PDF/image 导出，一套 `pptx-canvas`（1280×720）用于 editable PPTX。**默认只生成一套 pptx-canvas**，除非用户明确要求高清 PDF。

**经验教训**：导出前先跑 `node export_deck_pptx.mjs --mode editable` 试一次——比 grep 检查更准。失败了就根据错误信息逐页修，修完重跑。

#### 交付物视觉对齐经验（2026-05-09 实测）

- `deck-image.pptx` 应与 PDF 展示一致；如果不一致，优先怀疑图片铺底尺寸，而不是 HTML。
- `deck-editable.pptx` 原生对象和 PDF 可能有轻微差异，主要来自 PowerPoint/LibreOffice 字体度量、圆角和边框渲染；只要用户接受，应保留纯 editable。
- 如需量化对比，可把 PPTX 用 LibreOffice 转 PDF，再用 PyMuPDF 渲染成 PNG，与 `deck.pdf` 渲染图做抽查。平均像素差在低个位数通常是抗锯齿级差异。
