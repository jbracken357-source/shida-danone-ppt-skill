---
name: shida-danone-ppt-skill
description: 达能企业风格 HTML 幻灯片生成——结合 huashu-design 的完整管线（架构选择 → 多页制作 → PDF/PPTX 导出）与 danone-design-system 的企业设计系统。支持浏览器播放 / PDF 导出 / 可编辑 PPTX / 图片铺底 PPTX 四种交付格式。触发词：达能风格 PPT、Danone slide deck、达能官网风格汇报、达能设计系统幻灯片、达能风格 deck、Danone presentation、Danone report deck。
version: 1.0.0
author: Shida Fu
tags: [presentation, slides, html, danone, corporate, design-system, pptx, pdf]
---

# Shida Danone PPT Skill

## 这个 Skill 做什么

生成**达能企业风格**的 HTML 幻灯片 deck，完整走通：
1. **需求澄清 → 叙事弧骨架 → 页数规划 → 节奏表**
2. **架构选择**（多文件 vs 单文件）
3. **Junior pass**（结构 + 占位，达能 token）→ 用户确认 → **Full pass**
4. **交付**：浏览器播放 / PDF / 可编辑 PPTX / 图片铺底 PPTX

设计系统来自 danone.com 全球官网，不是"商务 PPT 模板"。

## 何时使用

- 达能/企业风格的汇报、研究报告演示、产品发布
- 用户提到"达能风格 PPT"、"Danone slide deck"、"企业风格汇报"
- 需要同时交付 HTML + PDF + PPTX 的正式报告 deck

**不合适**：个人分享/演讲（用 guizang-ppt-skill）、创意设计/原型（用 huashu-design）、暗色仪表盘。

## Danone 设计系统（核心 Token）

> **来源验证**：以下 token 已对照 2026-05-08 的 danone.com 官网 CSS 验证（`theme/site.css` + `clientlib-base.min.css`）。标注 ✅ 为官网实际值，标注「品牌推断」为基于品牌体系的合理推断。

### 色板
| Token | 色值 | 用途 | 来源验证 |
|-------|------|------|---------|
| `--dn-blue` | `#005EB8` | 主品牌色、Hero 背景、激活状态、Bullet 点 | ✅ danone.com × 6 |
| `--dn-blue-mid` | `#0068CC` | Hover 状态 | 品牌推断 |
| `--dn-blue-dark` | `#002677` | 深色按钮 hover/active、深色文字 | ✅ danone.com × 3 |
| `--dn-blue-light` | `#0085EB` | Focus 状态、链接色 | 品牌推断 |
| `--dn-green` | `#207B3B` | 可持续/正向指标 accent | ✅ danone.com × 1 |
| `--dn-tint` | `#CCDFF1` | 日期标签背景、浅蓝底 | ✅ danone.com (原 `#CCEEFC` 已修正) |
| `--dn-text` | `#262627` | 正文/标题 | 品牌推断 |
| `--dn-text-secondary` | `rgba(0,0,0,0.6)` | 元数据、日期 | 品牌推断 |
| `--dn-border` | `rgba(0,0,0,0.15)` | 分隔线 | 品牌推断 |
| `--dn-white` | `#FFFFFF` | 默认画布 | ✅ |

### 字体
- **Hero/Display**: `Inter Tight`, `Inter`, sans-serif, weight 700
- **Heading**: `Inter`, weight 600
- **Body**: `Inter`, weight 400
- **中文 Body/Heading**: `Noto Sans SC`
- Google Fonts: `Inter:wght@400;500;600;700&Inter+Tight:wght@600;700&Noto+Sans+SC:wght@400;500;600;700`

### 组件签名特征
| 组件 | 规则 |
|------|------|
| **按钮** | `border-radius: 6.25rem`（pill 药丸形，官网实际值）|
| **卡片** | 扁平无阴影 |
| **表格** | 表头 `#CCDFF1` + `#005EB8` 底边 |
| **Hero** | 纯色 `#005EB8`，无渐变 |
| **图片** | 圆角 `border-radius: .75rem`（12px）|
| **Bullet 点** | 蓝色圆点 `#005EB8`，`border-radius: 50%`，`0.5rem` |
| **无渐变** | 任何场景不用 CSS gradient |
| **无 pill badge/tag** | 纯文本标签，不用彩色背景 badge |

### 间距尺度
`3, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96`（单位 px）

### 布局
- Max container: 1280px / Content: 1120px / Padding: 80px desktop
- Section vertical padding: 80-96px

## 工作流程

### Step 0 · 需求澄清（动手前必做）

**如果用户已经给了完整大纲 + 素材**，可以跳过直接进 Step 1。

**如果只给了主题或模糊想法**，用以下问题一次性对齐，**等用户批量答完再往下走**：

| # | 问题 | 作用 |
|---|------|------|
| 1 | **主题是什么？**（ESG 报告 / 产品发布 / 市场策略 / 年度汇报） | 决定叙事方向 |
| 2 | **受众是谁？分享场景？**（内部汇报 / 外部发布 / 投资人会议） | 语言风格和深度 |
| 3 | **分享时长？** | 换算页数：15 min ≈ 10 页, 30 min ≈ 20 页, 45 min ≈ 25-30 页 |
| 4 | **有没有原始素材？**（报告 / 旧 PPT / 数据 / 文案 / 图片） | 有就用，没有就帮搭 |
| 5 | **最终交付格式？** → 见下方交付格式决策 | 决定 HTML 约束 |

#### 交付格式决策（最硬 checkpoint）

> **这个决策比架构选择更先。** 要可编辑 PPTX 就必须从第一行 HTML 按硬约束写，事后补救 = 2-3 小时返工。

| 格式 | HTML 约束 | 说明 |
|------|----------|------|
| **浏览器 + PDF** | 无特殊约束 | 视觉最自由 |
| **PPTX 图片铺底** | 无特殊约束 | 视觉 100% 保真，文字不可编辑 |
| **PPTX 可编辑** | 4 条硬约束（见下方） | 同事能改文字，视觉稍受限 |

**如果用户说"都需要"**——按 **PPTX 可编辑** 的约束写 HTML。它同时覆盖浏览器、PDF、PPTX 三种场景，是超集。

#### PPTX 可编辑的 4 条硬约束（从第一行 HTML 就遵守）

1. **body 固定 `960pt × 540pt`**（不是 1920×1080px）
2. **所有文字必须在 `<p>` 或 `<h1>`-`<h6>` 里**（禁止 div 直接写文字，禁止 `<span>` 承载主文字）
3. **`<p>`/`<h*>` 不能有 background/border/shadow**（放外层 div）
4. **不用 CSS 渐变，div 不用 background-image**（用 `<img>` 标签）

### Step 1 · 叙事弧搭骨架 + 页数规划

用"叙事弧"模板搭骨架，再填内容：

```
钩子(Hook)       → 1 页   : 抛反差/问题/硬数据让人停下来
定调(Context)    → 1-2 页 : 背景/你是谁/为什么讲这个
主体(Core)       → 3-5 页 : 核心内容
转折(Shift)      → 1 页   : 打破预期/新观点
收束(Takeaway)   → 1-2 页 : 金句/悬念/行动建议
```

**产出物**：一份"节奏规划表"，列出每一页的主题角色 + 布局类型 + 达能主题变体（light/dark/hero）：

| 页号 | 主题角色 | 布局类型 | 背景变体 |
|------|----------|---------|---------|
| 1 | 封面 | Hero Cover | `hero-blue` |
| 2 | 执行摘要 | KPI 卡片网格 | `white` |
| 3 | 核心观点 | 左文右图 | `white` |
| ... | ... | ... | ... |

**节奏规则**：
- 每 3-4 页插入一个 Hero 页（封面/幕封/问题/大引用）
- 不要连续 3 页以上相同主题
- Hero 页与正文页 2-3:1 交错

🛑 **检查点**：把节奏规划表发给用户，等确认后再动手。

### Step 2 · 架构选择

| 维度 | 单文件（≤10 页） | **多文件（≥10 页，默认推荐）** |
|------|-----------------|-------------------------------|
| 结构 | 一个 HTML，所有 slide 是 `<section>` | 每页独立 HTML，index.html 用 iframe 拼接 |
| CSS | ❌ 全局作用域 | ✅ 天然隔离 |
| 验证 | ❌ 要 JS 切换 | ✅ 双击单文件就能看 |
| 并行 | ❌ 冲突 | ✅ 可拆分给多 agent |

**默认走多文件**。决策后进入实现。

### Step 3 · 生成 shared/tokens.css（达能设计系统）

```css
:root {
  --dn-blue: #005EB8;
  --dn-blue-mid: #0068CC;
  --dn-blue-dark: #002677;
  --dn-blue-light: #0085EB;
  --dn-green: #207B3B;
  --dn-tint: #CCDFF1;
  --dn-text: #262627;
  --dn-text-secondary: rgba(0,0,0,0.6);
  --dn-border: rgba(0,0,0,0.15);
  --dn-white: #FFFFFF;
  --dn-font: "Inter", "Noto Sans SC", system-ui, sans-serif;
  --dn-font-display: "Inter Tight", "Inter", "Noto Sans SC", sans-serif;
  --dn-radius-btn: 6.25rem;
  --dn-radius-img: .75rem;
  --dn-radius-bullet: 50%;
}
body {
  font-family: var(--dn-font);
  color: var(--dn-text);
  background: var(--dn-white);
  margin: 0;
  line-height: 1.15;
  -webkit-font-smoothing: antialiased;
}
/* 多文件架构画布锁定 */
body.slide-canvas { width: 1920px; height: 1080px; overflow: hidden; }
/* PPTX 可编辑模式画布锁定 */
body.pptx-canvas { width: 960pt; height: 540pt; overflow: hidden; }
```

### Step 4 · Junior pass（结构 + 占位）

- 先出 2-3 页（封面 + 核心内容页 + 数据页）的骨架
- 用诚实 placeholder（灰块 + 文字标签），不编造内容
- 用达能 token 写好 `tokens.css` 和目录结构
- 🛑 **尽早 show 给用户，等反馈再 Full pass**

### Step 5 · Full pass

- 填充所有页内容（根据用户提供的素材或确认后的假设）
- 逐页完成后在浏览器打开验证
- 检查：字体加载、图片路径、布局不溢出、达能风格一致性

### Step 6 · 导出

根据 Step 0 确认的交付格式执行：

| 导出目标 | 命令 |
|---------|------|
| **浏览器播放** | 直接打开 `index.html`（拼接器内置键盘导航/计数器/打印） |
| **PDF（矢量文字可搜索）** | `node scripts/export_deck_pdf.mjs --slides slides/ --out deck.pdf` |
| **PPTX 图片铺底** | `node scripts/export_deck_pptx.mjs --slides slides/ --out deck.pptx --mode image` |
| **PPTX 可编辑** | `node scripts/export_deck_pptx.mjs --slides slides/ --out deck.pptx --mode editable` |

> 以上脚本路径指向 huashu-design skill 的 `scripts/` 目录。如果没有这些脚本，手动安装依赖：`npm install playwright pdf-lib pptxgenjs`。

## 页面布局库

参考 `danone-report-deck` 和 `guizang-ppt-skill` 的布局模式，适配达能风格：

| 布局 | 用途 | 达能特征 |
|------|------|---------|
| **1. Hero 封面** | 第 1 页 | `#005EB8` 纯色背景 + 白字大标题 |
| **2. 章节幕封** | 每幕开场 | 大留白 + 章节标题 |
| **3. KPI 卡片网格** | 执行摘要 | 3×2 或 2×3 卡片，无阴影，蓝色 bullet 点 `#005EB8` |
| **4. 左文右图** | 观点+实证 | 7:5 网格，图片 `border-radius: .75rem` |
| **5. 图片网格** | 多图对比 | 固定 `height:26vh`，不用 aspect-ratio |
| **6. 流水线** | 工作流程 | 编号步骤，按 → 逐步点亮 |
| **7. 数据表格** | 硬数据 | 表头 `#CCDFF1` + `#005EB8` 底边 |
| **8. 对比页** | Before/After | 左右分半，旧 `opacity:.55` |
| **9. 大引用** | 金句/takeaway | 大留白 + Inter Tight 700 |
| **10. 收束/致谢** | 最后一页 | Hero 蓝色背景 + 关键行动/联系方式 |

## 按钮 & CTA 规范

达能官网的按钮是 **pill 药丸形**（`border-radius: 6.25rem`），不是尖角：

```css
/* Primary CTA */
.btn-primary {
  background: var(--dn-blue);
  color: #fff;
  border-radius: 6.25rem;
  padding: .75rem 2rem;
  font-weight: 600;
  border: none;
}
.btn-primary:hover {
  background: var(--dn-blue-dark);
}

/* Secondary CTA */
.btn-secondary {
  background: transparent;
  color: var(--dn-text);
  border: 1px solid var(--dn-text);
  border-radius: 6.25rem;
  padding: .75rem 2rem;
  font-weight: 600;
}
.btn-secondary:hover {
  background: var(--dn-blue-dark);
  border-color: var(--dn-blue-dark);
  color: #fff;
}
```

## 图片规范

- 统一圆角 `border-radius: .75rem`（12px）
- `object-fit: cover`，顶部对齐
- 官网图片比例以 16:9 和 1:1 为主

## 目录结构模板

```
达能Deck/
├── index.html              # 拼接器（从 huashu-design assets/deck_index.html 复制）
├── shared/
│   └── tokens.css          # 达能设计 token
└── slides/
    ├── 01-cover.html
    ├── 02-agenda.html
    ├── 03-executive-summary.html
    └── ...
```

## 自检清单（交付前）

- [ ] `<title>` 没有残留占位符
- [ ] Google Fonts 加载正常（Inter / Inter Tight / Noto Sans SC）
- [ ] 所有按钮 `border-radius: 6.25rem`（pill 药丸形）
- [ ] 卡片无 `box-shadow`
- [ ] Hero 背景是纯色 `#005EB8`（无渐变）
- [ ] 图片 `border-radius: .75rem`
- [ ] 表头 `#CCDFF1` + 底边 `#005EB8`
- [ ] Bullet 点是蓝色圆点 `#005EB8`，`border-radius: 50%`
- [ ] 按 → 键翻每一页无空白/无错位
- [ ] PPTX 可编辑模式：body 是 `960pt×540pt`，文字全在 `<p>`/`<h*>` 里
- [ ] 无 TODO / placeholder 残留

## 反模式

- ❌ 深色主题（达能是 light-first，white canvas）
- ❌ 尖角按钮（达能实际用 `border-radius: 6.25rem` pill 药丸形）
- ❌ 卡片阴影（达能是扁平设计）
- ❌ 渐变背景（Hero 用纯色 `#005EB8`）
- ❌ 彩色背景 badge/tag（纯文本标签，日期标签用 `#CCDFF1` 浅蓝底）
- ❌ 超过 2 个 accent 色（blue + green only）
- ❌ 装饰性插图/图标（达能是摄影驱动）
- ❌ 图片不用圆角（官网图片统一 `.5rem`-`.75rem` 圆角）
