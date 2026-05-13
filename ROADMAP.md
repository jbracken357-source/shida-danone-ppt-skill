# Danone PPT Skill — Roadmap & Next Steps

> 本文档记录当前已知问题、优化计划和下一步行动。
> 最后更新：2026-05-13

---

## 当前状态（v6.0.0）

### v6.0 已完成（2026-05-13）

#### Content-driven layout selection
- [x] `plan_from_notes()` replaces hardcoded 7-slide sequence
- [x] Theme rhythm: hero→light→dark alternation between scenario slides
- [x] Rich data scenarios get scenario + dark big-quote pairs
- [x] 9 new HTML layouts: hero-cover, big-message, three-column, stat-grid, big-quote, before-after, pipeline, image-text, flow, closing
- [x] `_STRATEGIC_CSS` with 10+ strategic layout classes

#### Strategic / VP Review mode
- [x] `## Slide N — Title` parser with `StrategicSlide` dataclass
- [x] `VISUAL_TO_INTENT` mapping (cover/closing/positioning/flywheel/journey/matrix/hero-demo)
- [x] 8 strategic renderers: cover, closing, decision-grid, positioning, master-storyline, service-architecture, hero-demo, data-flywheel, experience-space, naming-direction
- [x] `--mode strategic` CLI flag with auto-detect fallback
- [x] Smoke test: 6-slide strategic brief with varied layouts

#### Image placeholder protocol
- [x] `[img: path:label]` / `[photo: path:label]` marker extraction
- [x] `parse_image_hints()` / `render_image_slot()` helpers
- [x] Input adapter preserves image hints across all formats
- [x] HTML deck renders real `<img>` tags when paths exist

#### Native PPTX fixes (v4.0)
- [x] Resource cleanup: 15-20MB → ~700KB
- [x] Content mapping: contents/three-column/scenario-detail fixed
- [x] Slide number: output sequence instead of template page numbers
- [x] Dangling image refs cleaned from slide rels

#### Editorial typography
- [x] Playfair Display (serif headlines) + Inter (body) + IBM Plex Mono (data)
- [x] Visual depth: card shadows, radial gradients, backdrop-filter blur, ghost numbers

### 已知的待完善项（P1-P2）

#### P1 — Native PPTX 图片替换
- `image-content` / `section-photo` intents 在 HTML 路径已渲染，在 native PPTX 路径尚未实现图片替换到 `<p:pic>`
- 需要：复制图片到 `ppt/media/`，更新 `a:blip` 引用

#### P1 — Native PPTX 布局扩展
- 当前 native PPTX 仅支持 5 种基础布局映射（cover, contents, three-column, scenario-detail, closing）
- Strategic 布局（decision-grid, flywheel, journey 等）尚未映射到 native PPTX
- 当前策略：strategic 模式默认输出 HTML 路径

#### P2 — Export 交互性
- PDF 输出为矢量但不可编辑
- Image PPTX 不可编辑
- 真正可编辑的路径仅 native PPTX

#### P2 — Input adapter 智能度
- Script 格式拆分基于段落分块，Claude 填充细节的逻辑尚未完全自动化
- 部分 `待补充` 字段仍需要手动完善

---

## 优化计划

### Phase 1: Native PPTX 图片替换 + 布局扩展
| 顺序 | 任务 | 优先级 |
|------|------|--------|
| 1.1 | 实现 native PPTX 图片替换（`ppt/media/` + `a:blip`） | P1 |
| 1.2 | 扩展 layout-map.json 覆盖 strategic 布局 | P1 |
| 1.3 | `build_native_pptx.py` 支持 strategic render functions | P1 |

### Phase 2: Input adapter 增强
| 顺序 | 任务 | 优先级 |
|------|------|--------|
| 2.1 | Claude 辅助填充 `待补充` 字段的自动化流程 | P2 |
| 2.2 | 更多输入格式支持（JSON, CSV, keynote export） | P3 |

---

## 开发验证流程

每次修改后按以下顺序验证：

### Step 1: 生成测试 Deck
```bash
# Scenario mode
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
  --out-dir /tmp/test-html --brand-line "DHT Lab · Danone"

# Strategic mode
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/strategic-brief.md \
  --out-dir /tmp/test-strategic --mode strategic

# Auto-detect
python scripts/notes_to_danone_deck.py \
  --notes /tmp/normalized.md \
  --out-dir /tmp/test-auto
```

### Step 2: HTML 视觉自检
```bash
start /tmp/test-html/index.html  # Windows
```
检查清单：
- [ ] 字体正确加载（Playfair Display + Inter）
- [ ] 主题节奏合理（light/dark/hero 交替）
- [ ] 图片占位符渲染正确
- [ ] 布局多样化（非单一卡片网格）
- [ ] Strategic 模式布局正确

### Step 3: Export 验证
```bash
node scripts/export_deck_pdf.mjs --slides /tmp/test-html/slides --out /tmp/test.pdf --width 1280 --height 720
node scripts/export_deck_pptx.mjs --slides /tmp/test-html/slides --out /tmp/test-image.pptx --width 1280 --height 720
```

### Step 4: 文档同步检查
- [ ] SKILL.md 的 design rules 与代码一致
- [ ] AGENTS.md 的命令速查与代码一致
- [ ] CHANGELOG.md 已记录本次变更
- [ ] ROADMAP.md 更新当前状态

---

## 依赖检查清单

```bash
# Python（stdlib only，无需安装）
python --version  # 3.10+

# Node.js
node --version    # 18+

# 依赖包
npm list playwright pdf-lib pptxgenjs sharp 2>/dev/null || npm install
```

---

## 参考资源

- `templates/layout-map.json` — intent → PPTX layout 映射
- `scripts/build_native_pptx.py` — native PPTX 核心逻辑
- `scripts/notes_to_danone_deck.py` — HTML deck + strategic mode 核心逻辑
- `scripts/input_adapter.py` — 输入格式规范化
