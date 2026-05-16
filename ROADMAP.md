# Danone PPT Skill — Roadmap & Next Steps

> 本文档记录当前已知问题、优化计划和下一步行动。
> 最后更新：2026-05-16

---

## 当前状态（v7.0.0-dev）

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

### v7.0.0 新增加（2026-05-16）

#### 设计系统统一
- [x] 统一 tokens.css 与 themes.md 的 5 个冲突值
- [x] 新建 `references/danone-dna.md`：品牌固定锚点文档
- [x] 新建 `references/danone-content-design.md`：内容页企业级设计标准 + 反 AI slop 清单
- [x] 修复 visual-verification.md、components.md、notes_to_danone_deck.py 中的硬编码颜色值

#### Native PPTX 图片替换
- [x] `build_native_pptx.py` 新增图片替换引擎：复制图片到 `ppt/media/` + 更新 `a:blip` 引用
- [x] 移除 `UNSUPPORTED_NATIVE_IMAGE_INTENTS` 限制
- [x] `image-content` / `section-photo` intents 现在 native PPTX 路径可用

#### 布局扩展（17 种 intent）
- [x] 新增 8 种 strategic intent 映射到 layout-map.json
- [x] 新增 `stat-grid`、`flow`、`big-quote` intent 映射
- [x] 从硬编码 placeholder idx 改为动态类型匹配（进行中）

#### 智能大纲解析
- [x] 新建 `scripts/outline_parser.py`：自由格式大纲 → JSON plan
- [x] 意图分类器：基于关键词 + 结构分析自动分类 intent
- [x] 主题色自动分配 + theme rhythm 规则应用
- [x] 词边界匹配避免 substring 误匹配（如 "discovers" 匹配 "cover"）

#### 统一质量检查
- [x] 新建 `scripts/verify_deck.py`：HTML + PPTX 统一 P0/P1 检查
- [x] SKILL.md 更新：反映新增能力、路由表、资源文件

### 已知的待完善项

#### P1 — 动态 placeholder 映射
- `map_content_to_shapes()` 仍使用部分硬编码 placeholder idx
- 需要：运行时解析 layout XML 中每个 placeholder 的 type/idx/name

#### P2 — Export 交互性
- PDF 输出为矢量但不可编辑
- Image PPTX 不可编辑
- 真正可编辑的路径仅 native PPTX

#### P2 — Input adapter 智能度
- Script 格式拆分基于段落分块，Claude 填充细节的逻辑尚未完全自动化
- 部分 `待补充` 字段仍需要手动完善

#### P2 — 布局变体多样性
- 同一 intent 总是渲染相同 HTML 结构
- 需要：anti-convergence 规则，同 deck 内同 intent 使用不同变体

---

## 优化计划

### Phase 1: 已完成 ✓
| 顺序 | 任务 | 状态 |
|------|------|------|
| 1.1 | 设计 Token 统一 | ✓ 完成 |
| 1.2 | Danone DNA 文档 | ✓ 完成 |
| 1.3 | 内容页设计规范 | ✓ 完成 |
| 1.4 | Native PPTX 图片替换 | ✓ 完成 |
| 1.5 | 布局扩展（17 种 intent） | ✓ 完成 |
| 1.6 | 智能大纲解析 | ✓ 完成 |
| 1.7 | 统一质量检查 | ✓ 完成 |

### Phase 2: 动态 placeholder 映射
| 顺序 | 任务 | 优先级 |
|------|------|--------|
| 2.1 | `build_placeholder_map()` 运行时解析 layout XML | P1 |
| 2.2 | 替换 `map_content_to_shapes()` 的 magic number | P1 |

### Phase 3: 布局变体 + Anti-convergence
| 顺序 | 任务 | 优先级 |
|------|------|--------|
| 3.1 | 同 intent 多 HTML 变体切换 | P2 |
| 3.2 | Theme rhythm 自动优化 | P2 |

---

## 开发验证流程

每次修改后按以下顺序验证：

### Step 1: 生成测试 Deck
```bash
# 智能大纲解析 → Native PPTX
python scripts/outline_parser.py input.md --out plan.json
python scripts/build_native_pptx.py --plan plan.json --out deck-native.pptx

# Scenario mode
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
  --out-dir /tmp/test-html --brand-line "DHT Lab · Danone"

# Strategic mode
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/strategic-brief.md \
  --out-dir /tmp/test-strategic --mode strategic
```

### Step 2: 统一质量检查
```bash
python scripts/verify_deck.py ./deck/slides/ --pptx ./deck-native.pptx
```

### Step 3: HTML 视觉自检
```bash
start /tmp/test-html/index.html  # Windows
```
检查清单：
- [ ] 字体正确加载（Playfair Display + Inter）
- [ ] 主题节奏合理（light/dark/hero 交替）
- [ ] 图片占位符渲染正确
- [ ] 布局多样化（非单一卡片网格）
- [ ] Strategic 模式布局正确

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

| 文件 | 用途 |
|------|------|
| `references/danone-dna.md` | 品牌固定锚点（封面/末页/字体/页码/Footer） |
| `references/danone-content-design.md` | 内容页企业级设计标准 + 反 AI slop |
| `references/layouts.md` | 布局注册表 + theme rhythm |
| `references/themes.md` | 主题色 + 品牌色（引用 tokens.css） |
| `references/components.md` | 组件规格 |
| `references/visual-verification.md` | 验证流程 |
| `references/checklist.md` | P0/P1/P2/P3 自检清单 |
| `templates/tokens.css` | 设计 Token 唯一事实源 |
| `templates/layout-map.json` | Intent → PPTX layout 映射 |
| `scripts/build_native_pptx.py` | Native PPTX 核心（含图片替换） |
| `scripts/outline_parser.py` | 智能大纲解析 |
| `scripts/verify_deck.py` | 统一质量检查 |
| `scripts/notes_to_danone_deck.py` | HTML deck + strategic mode |
