# Shida Danone PPT Skill

达能企业风格 HTML 幻灯片生成 Skill —— 结合 huashu-design 的完整管线（架构选择 → 多页制作 → PDF/PPTX 导出）与 Danone 企业设计系统。

## 支持四种交付格式

- **浏览器播放** — 直接打开 HTML，键盘导航翻页
- **PDF 导出** — 矢量文字可搜索
- **PPTX 图片铺底** — 视觉 100% 保真，文字不可编辑
- **PPTX 可编辑** — 同事能直接改文字

## 设计系统

基于 danone.com 全球官网 CSS 提取的设计 token：

| Token | 色值 | 用途 |
|-------|------|------|
| `--dn-blue` | `#005EB8` | 主品牌色 |
| `--dn-green` | `#207B3B` | 可持续 accent |
| `--dn-tint` | `#CCDFF1` | 浅蓝底标签 |
| `--dn-text` | `#262627` | 正文 |

- **字体**: Inter / Inter Tight / Noto Sans SC (Google Fonts)
- **按钮**: Pill 药丸形 `border-radius: 6.25rem`
- **卡片**: 扁平无阴影
- **Hero**: 纯色 `#005EB8`，无渐变

## 工作流程

1. 需求澄清 → 叙事弧骨架 → 页数规划 → 节奏表
2. 架构选择（多文件 vs 单文件）
3. Junior pass（结构 + 占位，达能 token）→ 确认 → Full pass
4. 交付：浏览器 / PDF / PPTX

完整流程、布局库、组件规范、自检清单和反模式见 [SKILL.md](./SKILL.md)。

## License

MIT
