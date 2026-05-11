# Danone PPT Skill — Roadmap & Next Steps

> 本文档记录当前已知问题、优化计划和下一步行动。
> 最后更新：2026-05-11

---

## 当前状态（v3.1.0）

### 已完成的改进（2026-05-11）
- [x] 文档边界重新划分：README（人类）/ SKILL.md（Claude AI）
- [x] 修复 README ↔ SKILL.md 设计规范不一致（closing 颜色、cover gradient）
- [x] 添加 `.gitignore` 忽略根目录生成产物
- [x] 所有 Python 脚本添加 `logging` 替代 `print()`
- [x] 移除 `notes_to_danone_deck.py` 硬编码假数据
- [x] 统一画布尺寸为 1280×720
- [x] Node export 脚本添加 `--help`、目录验证、进度输出
- [x] 新建 `AGENTS.md`、`CHANGELOG.md`、`package.json`、`requirements.txt`

### 已知的致命问题（P0）

#### 1. HTML Deck 视觉效果完全烂了
**原因分析：**
- 字体使用 Arial Narrow fallback，廉价且无品牌感
- 布局只有 5 种对称卡片/网格模式，单调重复
- 图片占位符是圆形 wireframe + 文字标签，不像 editorial layout
- Flat 纯色背景，无 gradient/shadow/视觉深度
- 所有页都是 light 主题，没有 dark 页制造呼吸节奏
- 每页内联 791 行 CSS，无法全局调整

**参考标准：**
- `guizang-ppt-skill` 的杂志级排版（衬线标题 + 非衬线正文 + 等宽元数据）
- `frontend-design` 的 anti-AI-slop 原则（不用 overused fonts、不用 identical card grids）

#### 2. Native 可编辑 PPTX 全烂了
**原因分析：**
- 输出文件 15-20MB：复制了整个模板（649 文件），未清理未使用资源
- `contents` intent 内容映射 broken：查找 idx=1/2，实际 layout 用 idx=16,22-25
- `three-column` / `scenario-detail` intent 映射 broken：查找 idx=1,2,14，实际用 idx=21-26
- slide number 显示原始模板页码（如 "35"）而非输出页码
- 移除 `<p:pic>` 后未清理 slide rels，产生悬空引用
- `image-content` / `section-photo` intents 直接抛 NotImplementedError

---

## 优化计划（v4.0）

### Phase 1: HTML Deck 视觉重构（最高优先级）

#### 1.1 锁定字体策略
- **Display/Headline**: `Playfair Display` (Google Fonts) — 衬线杂志感
- **Body**: `Inter` (Google Fonts) — 清晰现代
- **Chinese**: `Noto Sans SC`
- **Mono/Labels**: `IBM Plex Mono` — 数据、页码、metadata
- 删除 `"Danone One Light"` / `"Danone One Condensed"` 引用（用户大概率没有）
- 添加 `font-feature-settings: "tnum"`

#### 1.2 重构布局系统（新增 9 种布局）
| 布局 | 用途 |
|------|------|
| Hero Cover | 第 1 页 |
| Big Message | 超大 headline |
| Three-Column Editorial | 不对称分栏 |
| Stat Grid | 数据大字报 |
| Quote / Big Quote | 衬线引用 + 署名 |
| Before/After | 并列对比 |
| Pipeline / Steps | 流程步骤 |
| Image + Text | 左图右文/右图左文 |
| Closing | 感谢页 |

**强制规则：** 每 3-4 页插入 1 个 hero 页，连续不超过 3 页同主题。

#### 1.3 图片占位符系统升级
- 移除 `.img-circle` wireframe
- 新增 `.frame-img` — `object-fit: cover`，支持真实图片
- 新增 `.img-slot` — 编辑风格虚线边框占位符
- 所有占位符标注尺寸比例（16:9, 4:3, 3:2, 1:1）

#### 1.4 CSS 架构统一
- 共享 CSS 提取到 `shared/tokens.css`，每页只保留 layout-specific 少量样式
- 建立可组合类名系统：`.h-hero`、`.h-xl`、`.lead`、`.grid-2-1`、`.card`、`.stat`

#### 1.5 添加视觉深度
- 卡片极 subtle shadow
- Cover/closing 添加 radial gradient
- 图片 overlay 使用 `backdrop-filter: blur(2px)`
- 数据页使用 ghost number（超大半透明背景数字）

#### 1.6 主题节奏系统
- 每页标记 `theme="light"` / `theme="dark"` / `theme="hero"`
- 6 页以上 deck 必须有 ≥1 dark 页
- 生成后 `grep 'theme-'` 自检

### Phase 2: Native PPTX 修复

#### 2.1 清理未使用资源
- trace 实际引用的 media/layouts/masters/themes
- 删除未引用资源（预计 20MB → ~2MB）

#### 2.2 修复内容映射
- `contents` → idx=16,22,23,24,25
- `three-column` / `scenario-detail` → idx=21,22,23,24,25,26
- `image-content` / `section-photo` → title=idx=14, body=idx=1
- 添加运行时验证：映射找不到时报错

#### 2.3 修复 slide number
- 更新 `sldNum` placeholder 为输出页码

#### 2.4 修复悬空图片引用
- 移除 `<p:pic>` 时同步清理 slide rels

#### 2.5 实现图片替换（P2）
- 支持 `image` content key
- 复制图片到 `ppt/media/`，更新 `a:blip`

### Phase 3: 文档同步
- 更新 SKILL.md：字体栈、布局类型、主题节奏、图片占位符规范
- 更新 README.md：Quick Start 示例
- 更新 AGENTS.md：Visual Quality Checklist
- 更新 CHANGELOG.md：v4.0 变更记录

---

## 执行顺序建议

| 顺序 | 任务 | 预计时间 | ROI |
|------|------|---------|-----|
| 1 | Phase 1.1 字体 + Phase 1.5 视觉深度 | 1-2h | 最高 |
| 2 | Phase 1.2 布局重构 + Phase 1.3 图片占位符 | 2-3h | 高 |
| 3 | Phase 1.4 CSS 架构 + Phase 1.6 主题节奏 | 1-2h | 中 |
| 4 | Phase 2.1 资源清理 + Phase 2.2 映射修复 | 2h | 高 |
| 5 | Phase 2.3 slide number + Phase 2.4 悬空引用 | 1h | 中 |
| 6 | Phase 3 文档更新 | 1h | 中 |

---

## 开发验证流程（明天开始用）

每次修改后按以下顺序验证：

### Step 1: 生成测试 Deck
```bash
# HTML path
python scripts/notes_to_danone_deck.py \
  --notes smoke-tests/dht-lab-notes/Slide\ notes.md \
  --out-dir /tmp/test-html \
  --brand-line "DHT Lab · Danone"

# Native path
python scripts/brief_to_native_deck.py \
  --title "Test" \
  --brief-file smoke-tests/brief-native/brief.md \
  --slides 6 \
  --out /tmp/test-native.pptx
```

### Step 2: HTML 视觉自检
```bash
# 打开浏览器验证
open /tmp/test-html/index.html  # macOS
start /tmp/test-html/index.html  # Windows
```
检查清单：
- [ ] 字体正确加载（Playfair Display + Inter）
- [ ] 主题节奏合理（light/dark/hero 交替）
- [ ] 图片占位符有 `.frame-img` / `.img-slot`
- [ ] 视觉深度存在（gradient、shadow、backdrop-blur）
- [ ] 无纯 flat 页面

### Step 3: Native PPTX 功能自检
```bash
# 检查文件大小
ls -lh /tmp/test-native.pptx
# 期望：< 5MB

# 检查内部结构
python -c "import zipfile; z=zipfile.ZipFile('/tmp/test-native.pptx'); print(len(z.namelist()), 'files')"
# 期望：< 100 个文件

# 检查 slide number
python -c "
import zipfile, re
z = zipfile.ZipFile('/tmp/test-native.pptx')
for name in sorted(z.namelist()):
    if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
        xml = z.read(name).decode('utf-8')
        nums = re.findall(r'<a:t>(\d+)</a:t>', xml)
        print(name, 'numbers found:', nums[:3])
"
# 期望：显示 1, 2, 3... 而非原始模板页码
```

### Step 4: Export 验证
```bash
# PDF
node scripts/export_deck_pdf.mjs \
  --slides /tmp/test-html/slides \
  --out /tmp/test.pdf \
  --width 1280 --height 720

# Image PPTX
node scripts/export_deck_pptx.mjs \
  --slides /tmp/test-html/slides \
  --out /tmp/test-image.pptx \
  --width 1280 --height 720
```

### Step 5: 文档同步检查
- [ ] SKILL.md 的 design rules 与代码一致
- [ ] AGENTS.md 的命令速查与代码一致
- [ ] CHANGELOG.md 已记录本次变更

---

## 依赖检查清单（明天开始前）

```bash
# Python（stdlib only，无需安装）
python --version  # 3.10+

# Node.js
node --version    # 18+
npm --version

# 依赖包
npm list playwright pdf-lib pptxgenjs sharp 2>/dev/null || npm install
```

---

## 参考资源

- `guizang-ppt-skill` 的杂志排版理念（衬线标题 + 非衬线正文 + 等宽元数据）
- `frontend-design` 的 anti-AI-slop 原则（不用 overused fonts、不用 identical card grids）
- `templates/layout-map.json` — intent → PPTX layout 映射
- `scripts/build_native_pptx.py` — native PPTX 核心逻辑
- `scripts/notes_to_danone_deck.py` — HTML deck 核心逻辑
