---
name: shida-danone-ppt-skill
description: 生成达能企业风格 HTML 幻灯片 deck，完整走通需求澄清→叙事弧→架构选择→Junior/Full pass→交付（浏览器/PDF/可编辑PPTX/图片铺底PPTX）。设计系统来自 danone.com 官网验证。触发词：达能风格 PPT、Danone slide deck、达能官网风格汇报、达能设计系统幻灯片、达能风格 deck、Danone presentation、Danone report deck、ESG 报告 PPT、产品发布 deck。
version: 2.0.0
author: Shida Fu
tags: [presentation, slides, html, danone, corporate, design-system, pptx, pdf]
---

# Shida Danone PPT Skill

> TL;DR：达能官网(light-first)风格幻灯片。走需求澄清→叙事弧→多文件架构→Junior pass(确认)→Full pass→交付。要可编辑PPTX就从第一行遵守4条硬约束。

## 何时使用

- ✅ 达能/企业风格汇报、研究报告演示、ESG报告、产品发布
- ✅ 需要同时交付 HTML + PDF + PPTX 的正式报告 deck
- ❌ 个人分享/演讲 → 用 guizang-ppt-skill
- ❌ 创意设计/原型 → 用 huashu-design
- ❌ 暗色仪表盘 → 达能是 light-first

---

## Danone 设计系统

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
  ├─ 是 → PPTX可编辑 → 从第一行遵守4条硬约束（见下方）
  └─ 否 → 要PDF吗？
           ├─ 是 → 浏览器+PDF → 无特殊约束
           └─ 否 → 浏览器播放 或 PPTX图片铺底 → 无特殊约束
```

**用户说"都需要"** → 按 **PPTX可编辑** 约束写（超集，覆盖所有场景）。

#### PPTX可编辑的 4 条硬约束

1. body 固定 `960pt × 540pt`（不是 1920×1080px）
2. 所有文字在 `<p>` 或 `<h1>`-`<h6>` 里（禁止 div/span 直接承载文字）
3. `<p>`/`<h*>` 无 background/border/shadow（放外层 div）
4. 无 CSS 渐变，div 无 background-image（用 `<img>` 标签）

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

### Step 2 · 架构选择

| 页数 | 架构 | 理由 |
|------|------|------|
| ≤10 页 | 单文件（`<section>` 切换） | 简单 |
| ≥10 页 | **多文件**（每页独立 HTML，index.html iframe 拼接） | 天然隔离、可并行、双击可看 |

**默认多文件**。生成目录结构：
```
达能Deck/
├── index.html              # 拼接器（从 huashu-design assets/deck_index.html 复制）
├── shared/
│   └── tokens.css          # 见下方
└── slides/
    ├── 01-cover.html
    ├── 02-...
    └── ...
```

### Step 3 · 生成 tokens.css

写入 `shared/tokens.css`（见下方代码块）。所有 slide 引用此文件。

```css
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
body.pptx-canvas { width: 960pt; height: 540pt; overflow: hidden; }
```

### Step 4 · Junior pass（结构 + 占位）

**做什么**：出 2-3 页骨架（封面 + 核心内容页 + 数据页），写好 tokens.css 和目录结构。

**输出规格**：
- 每页一个独立 HTML 文件（多文件模式）或 `<section>`（单文件）
- 布局结构完整（网格/分栏/留白比例正确）
- 内容用灰块 + 文字标签占位（如 `[此处放ESG数据图表]`），**不编造内容**
- 达能 token（色值/字体/圆角）已就位

**展示方式**：列出文件路径，让用户在浏览器打开对应文件查看效果。

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

#### 前置：复制脚本 + 安装依赖

```bash
cp <huashu-design>/scripts/export_deck_pdf.mjs ./
cp <huashu-design>/scripts/export_deck_pptx.mjs ./
cp <huashu-design>/scripts/html2pptx.js ./
cp <huashu-design>/assets/deck_index.html ./index.html
npm install playwright pdf-lib pptxgenjs
```

**Playwright Chromium 通道适配**：`npx playwright install` 在 WSL/Ubuntu 常因 headless-shell 下载超时失败。先 `which chromium-browser` 确认系统 chromium 存在，然后把两个脚本里的 `chromium.launch()` 改为 `chromium.launch({ channel: 'chromium' })`。

#### 导出执行

根据 Step 0 确认的交付格式，**实际运行**对应导出命令并检查输出：

| 目标 | 命令 | 成功标志 |
|------|------|---------|
| PDF | `node export_deck_pdf.mjs --slides slides/ --out deck.pdf --width 1920 --height 1080` | 输出 `✓ Wrote ...pdf (X KB, N pages, vector)` |
| PPTX 图片铺底 | `node export_deck_pptx.mjs --slides slides/ --out deck.pptx --mode image` | 输出 `✓ Wrote ...pptx (N slides, image mode)` |
| PPTX 可编辑 | `node export_deck_pptx.mjs --slides slides/ --out deck.pptx --mode editable` | 输出 `✓ Wrote ...pptx (N/N slides, editable mode)` |

**⚠️ PPTX 可编辑模式前置检查（导出前必须过）**：

editable 模式用 `html2pptx.js` 把 DOM 逐元素翻译为 PowerPoint 对象，HTML 不符合 4 条硬约束会全量失败。导出前先跑这个检查：

```bash
# 检查1: body 尺寸
grep -rl 'class="pptx-canvas"' slides/  | wc -l   # 应 = 总 slide 数
# 检查2: 文字包裹
grep -rP '<(div|span)[^>]*>[^<]{20,}<' slides/    # 有输出 = 有 div/span 直接承载文字
# 检查3: 渐变
grep -rl 'gradient' slides/                         # 有输出 = 有渐变
# 检查4: <p>/<h*> 上无样式
grep -rP '<(p|h[1-6])[^>]*(background|border|box-shadow)' slides/  # 有输出 = 违规
```

如果检查不通过，**不跑 editable 模式**，退回图片铺底模式（image mode），并向用户说明原因。

**PPTX 可编辑模式的 4 条硬约束（回顾）**：
1. body 固定 `960pt × 540pt`（用 `class="pptx-canvas"`）
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
| PDF 导出后字体显示为方块 | Google Fonts 未加载，检查网络或改用系统字体 fallback |
| 用户拒绝回答问题清单 | 按 best judgment 做 1 个主方案，交付时标注 assumption |
| huashu-design 脚本不存在 | 降级方案：`npm install playwright pdf-lib pptxgenjs` 后自写导出脚本（playwright 截图 + pdf-lib 合并） |

---

## 页面布局库

| 布局 | 用途 | 达能特征 |
|------|------|---------|
| 1. Hero 封面 | 第1页 | `#005EB8` 纯色 + 白字大标题 |
| 2. 章节幕封 | 每幕开场 | 大留白 + 章节标题 |
| 3. KPI 卡片网格 | 执行摘要 | 3×2 或 2×3 卡片，无阴影，蓝色 bullet |
| 4. 左文右图 | 观点+实证 | 7:5 网格，图片圆角 .75rem |
| 5. 图片网格 | 多图对比 | 固定 height:26vh |
| 6. 流水线 | 工作流程 | 编号步骤 → 逐步点亮 |
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
- [ ] PPTX 可编辑：body `960pt×540pt`，文字全在 `<p>`/`<h*>` 里
- [ ] 无 TODO / placeholder 残留

## 反模式

- ❌ 深色主题（达能 light-first，white canvas）
- ❌ 尖角按钮 / CSS 渐变 / 卡片阴影 / 彩色 badge
- ❌ 超过 2 个 accent 色（blue + green only）
- ❌ 装饰性插图/图标（达能摄影驱动）
