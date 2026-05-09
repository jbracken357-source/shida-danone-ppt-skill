# Shida Danone PPT Skill

达能企业风格幻灯片生成 Skill —— 优先复用真实 Danone 企业 PPT 模板的 master/layout/placeholders，再用 HTML 管线处理预览、PDF 和无法映射到真实版式的兜底页面。

## 真实模板优先

仓库支持从 `Danone Real Templates/Standard Danone Template.pptx` 抽取模板 manifest：

```bash
python scripts/profile_danone_template.py "Danone Real Templates/Standard Danone Template.pptx" --out templates/danone-template-manifest.json
```

正式可编辑 PPTX 用 native builder 生成：

如果用户只给材料描述或任务描述，先用 brief 入口生成 plan 和可编辑 PPTX：

```bash
python scripts/brief_to_native_deck.py --title "Deck title" --brief-file brief.md --slides 6 --out deck-native.pptx --out-plan plan.json
```

这个入口会保守重组用户提供的信息，缺内容时使用明确的“待补充”占位，不编造业务事实。

已有完整页级规划时，也可以直接用 native builder：

```bash
python scripts/build_native_pptx.py --plan plan.json --out deck-native.pptx
```

`plan.json` 可以是 slide 数组，或 `{ "slides": [...] }`：

```json
{
  "slides": [
    {
      "intent": "opening-cover",
      "content": {
        "title": "Deck title",
        "subtitle_or_date": "May 2026"
      }
    }
  ]
}
```

已生成的文件：

- `templates/danone-template-manifest.json` — 真实模板的 slide size、theme、字体、layout、placeholder inventory
- `templates/layout-map.json` — 将语义意图映射到真实 Danone layouts，例如封面、目录、两栏、大图、三栏、收尾页
- `scripts/brief_to_native_deck.py` — 从材料描述或任务描述生成 native slide plan，并直接产出真实模板可编辑 PPTX
- `scripts/build_native_pptx.py` — 复制真实 sample slide XML 并替换可编辑文本的 native PPTX builder

生成正式可编辑 PPTX 时，默认策略是选取 `layout-map.json` 中的真实 layout，复制真实模板的 layout 或 sample slide，并填充原生 placeholders。只有在内容无法稳定映射到真实模板时，才退回 HTML → editable PPTX；PDF、浏览器播放和图片铺底 PPTX 可以继续使用 HTML 管线。

## 支持四种交付格式

- **浏览器播放** — 直接打开 HTML，键盘导航翻页
- **PDF 导出** — 矢量文字可搜索
- **PPTX 图片铺底** — 视觉 100% 保真，文字不可编辑
- **PPTX 可编辑** — 同事能直接改文字

## 设计系统

真实模板 manifest 是优先级最高的设计系统来源。当前模板显示：

- 字体: `Danone One Condensed` / `Danone One Light`
- 尺寸: 16:9 wide, 13.333 × 7.5 inch
- 模板规模: 55 sample slides, 252 layouts, 12 masters, 14 themes

`templates/tokens.css` 仍保留为 HTML 预览和 fallback 生成用，基于 danone.com 全球官网 CSS 提取：

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
2. 架构选择：正式可编辑 PPTX 走真实模板 native；浏览器/PDF/图片铺底走 HTML；无真实 layout 的特殊页才用 HTML fallback
3. Junior pass：template-native PPTX 需列出每页真实 layout；HTML 分支才生成 `shared/tokens.css` 和 `slides/*.html`
4. Full pass → 导出/渲染抽查：确认 master、字体、页码、图片裁切和 placeholder 没有被 HTML 重建风格替换

完整流程、布局库、组件规范、自检清单和反模式见 [SKILL.md](./SKILL.md)。

## License

MIT
