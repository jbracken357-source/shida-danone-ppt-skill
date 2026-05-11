# Shida Danone PPT Skill / Shida Danone PPT 技能

> **EN**: Danone-style corporate presentation generator. Photo-first layouts, multi-color category themes, "One Planet. One Health" brand DNA. v3.1.0.
> **CN**: Danone 风格企业演示文稿生成器。摄影优先布局、多色分类主题、"One Planet. One Health" 品牌基因。v3.1.0。

---

## Features / 功能特性

| Feature / 特性 | Description / 描述 |
|----------------|-------------------|
| **Photo-first / 摄影优先** | Every slide has photo placeholders; Danone is never text-only / 每页都有照片占位符；Danone 从不是纯文字 |
| **Multi-color themes / 多色主题** | 5 category colorways (Gut→Green, Sport→Orange, Clinical→Pink, Water→Teal, Corporate→Blue) / 5 种分类色域 |
| **Data visualization / 数据可视化** | Bar charts, ring charts, big metric numbers as CSS placeholders / 条形图、环形图、大数字指标 |
| **Circular images / 圆形图片** | Signature Danone circular photo elements across all slides / 贯穿所有页面的 Danone 标志性圆形图片元素 |
| **Brand DNA / 品牌基因** | "One Planet. One Health" on every footer + closing page / 每页页脚 + 结尾页都有 |
| **3 output paths / 3 种输出路径** | Native editable PPTX, HTML deck, PDF / 原生可编辑 PPTX、HTML 幻灯片、PDF |

---

## Output Paths / 输出路径

### 1. Native editable PPTX (preferred for editability / 优先可编辑性)
```bash
python scripts/brief_to_native_deck.py --title "X" --brief-file brief.md --slides 6 --out deck.pptx
```
Copies real template layouts from `Danone Real Templates/Standard Danone Template.pptx`.
从真实模板 `Danone Real Templates/Standard Danone Template.pptx` 复制布局。

### 2. HTML deck (preferred for visual fidelity / 优先视觉保真)
```bash
python scripts/notes_to_danone_deck.py --notes notes.md --out-dir ./deck --brand-line "Brand X · Danone"
```
Generates 1280×720px HTML slides with full brand system.
生成 1280×720px HTML 幻灯片，包含完整品牌系统。

### 3. PDF export / PDF 导出
```bash
node scripts/export_deck_pdf.mjs --slides slides/ --out deck.pdf --width 1280 --height 720
```

### 4. Image PPTX / 图片式 PPTX
```bash
node scripts/export_deck_pptx.mjs --slides slides/ --out deck.pptx --width 1280 --height 720
```

---

## Design System / 设计系统

### Brand DNA (non-negotiable / 不可协商)
- **Hero cover**: `#005EB8` with gradient overlay / 渐变叠加
- **Slogan**: "One Planet. One Health" on cover + footer / 封面 + 页脚
- **Photography-first**: photo placeholders on every page / 每页照片占位符
- **Multi-color themes / 多色主题**:
  - Gut/Natural → Green `#00A651`
  - Sport/Physical → Orange `#F26522`
  - Clinical/Baby → Pink `#E6007E`
  - Water/Hydration → Teal `#00B2A9`
  - Corporate/Default → Blue `#005EB8`

### Components / 组件
- **Cards / 卡片**: flat, rounded 12px, top accent bar (4px theme color) / 扁平圆角，顶部 4px 主题色条
- **Product link cards / 产品链接卡片**: white background + accent top bar / 白色背景 + 主题色顶条
- **Circular images / 圆形图片**: 120px/64px diameter, 3px/2px theme border / 直径 120px/64px，主题色边框
- **Data viz / 数据可视化**: bar charts (28px pill), ring charts (100px), big metrics (64px) / 条形图、环形图、大数字
- **Quote blocks / 引用块**: left accent border + decorative quote mark / 左侧强调边框 + 装饰引号
- **Flow steps / 流程步骤**: 5-column grid, circular arrow connectors / 五列网格，圆形箭头连接
- **Footer / 页脚**: chapter color bar (4px) + "One Planet. One Health" + page numbers / 章节色条 + 标语 + 页码

### Closing page / 结尾页
- Thank You slide with dark blue `#002677` background / 深蓝色背景
- Large condensed typography + centered slogan / 大字标语居中

---

## Install / 安装

```bash
npm install playwright pdf-lib pptxgenjs sharp
```

---

## Smoke Tests / 冒烟测试

`smoke-tests/` contains example inputs. Generated outputs are gitignored.
`smoke-tests/` 包含示例输入。生成产物已加入 gitignore。

```bash
# Native editable PPTX from brief / 从简报生成原生可编辑 PPTX
python scripts/brief_to_native_deck.py --title "X" --brief-file smoke-tests/brief-native/brief.md --slides 6 --out smoke-tests/brief-native/deck.pptx

# HTML deck + native PPTX from structured notes / 从结构化笔记生成
python scripts/notes_to_danone_deck.py --notes "smoke-tests/dht-lab-notes/Slide notes.md" --out-dir smoke-tests/dht-lab-notes --native-pptx smoke-tests/dht-lab-notes/deck.pptx --brand-line "DHT Lab · Danone Science Lab"

# PDF export from HTML slides / 从 HTML 导出 PDF
node scripts/export_deck_pdf.mjs --slides smoke-tests/dht-lab-notes/slides --out smoke-tests/dht-lab-notes/deck.pdf --width 1280 --height 720
```

---

## License / 许可证

MIT
