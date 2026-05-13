---
name: shida-danone-ppt-skill
description: Use when creating Danone-branded presentations. Generates editable PPTX, HTML slide decks, or PDF. Photo-first or strategic layouts, multi-color themes, "One Planet. One Health" brand DNA.
version: 6.0.0
author: Shida Fu
tags: [presentation, slides, html, danone, corporate, design-system, pptx, pdf, strategic]
---

# Shida Danone PPT Skill

> Generate Danone-style corporate decks from any input (brief, outline, script, or structured notes). Output as editable PPTX, HTML deck, or PDF — chosen by the user.

## When to use

- Danone / corporate-style reports, ESG decks, product launches
- Deliverables needing editable PPTX or printable PDF
- VP review / strategic alignment / positioning decks
- Personal talks → use `guizang-ppt-skill` instead
- Dark dashboards → Danone is light-first
- Creative prototypes → use `huashu-design` instead

## Step 0: Detect deck type

Read the input. Determine which mode:

| Mode | Trigger | Format |
|------|---------|--------|
| **Strategic / VP Review** | Headings like `## Slide N — Title`, `## Slide N：Title`, or content about positioning, storyline, naming, decision | Outline with slide-by-slide structure |
| **Scenario / Science Lab** | Headings like `## 场景 N｜Name` | Scenario-based notes with target users, pain points, hardware, data, indicators, products |
| **Free-form** | Anything else | Brief, article, script, bullet list |

### Routing

- **Free-form** → normalize via `scripts/input_adapter.py` → detect type → proceed
- **Scenario / Science Lab** → parse via `notes_to_danone_deck.py` with `--mode scenario`
- **Strategic / VP Review** → parse via `notes_to_danone_deck.py` with `--mode strategic`

Each mode uses a different parser and layout registry. Do NOT force strategic content into scenario templates, or vice versa.

---

## Workflow

### Step 1: Clarify output format + accept input

Ask the user: **which format?**
- **Editable PPTX** — real Danone template, text editable in PowerPoint
- **HTML deck** — browser preview, full brand styling, interactive navigation
- **PDF** — vector export from HTML deck (printable, searchable)
- **All** — generate all three

Accept **any input format**:
- Free-form topics or bullet outline → normalize via `scripts/input_adapter.py`
- Long script or article → chunk into slides via `scripts/input_adapter.py`
- Structured notes → auto-detect deck type in Step 0

### Step 2: Parse and plan

Normalize input to structured Markdown (if free-form):
```bash
python scripts/input_adapter.py --input brief.md --out /tmp/normalized.md
```

Parse with the correct mode:
```bash
# Strategic / VP Review
python scripts/notes_to_danone_deck.py \
  --notes /tmp/normalized.md \
  --out-dir ./deck \
  --mode strategic \
  --brand-line "Brand X · Danone"

# Scenario / Science Lab
python scripts/notes_to_danone_deck.py \
  --notes /tmp/normalized.md \
  --out-dir ./deck \
  --mode scenario \
  --brand-line "Brand X · Danone"
```

Decide slide count, theme rhythm, and layout assignments. **Plan theme rhythm** before generating:
- Cover = hero, Closing = hero
- No 3+ consecutive same-theme pages
- 6+ page decks: at least 1 hero page per 3-4 content pages
- See `references/layouts.md` for rhythm planning table

### Step 3: Generate slides

Read the reference files for component and layout specs:
- `references/layouts.md` — layout skeletons and rhythm rules
- `references/themes.md` — color presets and font stack
- `references/components.md` — exact component specs

Generate the chosen format:

| Format | Command | Notes |
|--------|---------|-------|
| **HTML deck** | Already done in Step 2 | Opens via `./deck/index.html` |
| **Editable PPTX** | Add `--native-pptx ./deck/deck.pptx` to Step 2 command | Clones real Danone template |
| **PDF** | See Step 5 | Export from HTML deck |

### Step 4: Visual verification

Run through `references/visual-verification.md`:
1. **Cover**: solid `#005EB8` bg + white circle + centered title
2. **Theme rhythm**: grep theme classes, verify alternation
3. **Fonts**: headlines show serif (Playfair Display), body shows sans-serif (Inter)
4. **Components**: accent bars match theme, product cards are white + accent top
5. **Closing**: same format as cover with "THANK YOU"

### Step 5: Export (if PDF or image PPTX requested)

```bash
# HTML → PDF (vector, searchable)
node scripts/export_deck_pdf.mjs --slides ./deck/slides/ --out ./deck/deck.pdf --width 1280 --height 720

# HTML → Image PPTX (visual fidelity, not editable)
node scripts/export_deck_pptx.mjs --slides ./deck/slides/ --out ./deck/deck-image.pptx --width 1280 --height 720
```

### Step 6: Self-check

Run through `references/checklist.md` (P0/P1/P2/P3 graded). All P0 items must pass before delivery.

---

## Strategic Deck Layouts (VP Review Mode)

When the parser detects `## Slide N — Title` format, it routes to the **strategic layout registry**. Each slide type gets a named `render_XXX()` function:

| Layout Intent | Render Function | Visual Pattern |
|---------------|-----------------|----------------|
| `cover` | `_render_strategic_cover` | Blue bg + white circle + centered title |
| `closing` | `_render_strategic_closing` | Same as cover, "THANK YOU" |
| `decision-grid` | `render_decision_grid` | 2x2 or 1x4 decision cards (positioning/storyline/hero/naming) |
| `positioning` | `render_positioning` | Before/After two-column contrast ("What DHT Is Not" vs "What DHT Is") |
| `master-storyline` | `render_master_storyline` | Horizontal flow: Vision → Pillars → Services → Demos → Flywheel → Experience |
| `service-architecture` | `render_service_architecture` | Matrix table with colored priority tags (Hero/Core/Future) |
| `hero-demo` | `render_hero_demo` | Two-column split hero (invisible vs visible, or compare two options) |
| `data-flywheel` | `render_data_flywheel` | 6-step circular loop with guardrail warning bar |
| `experience-space` | `render_experience_space` | 4-column journey map with arrow connectors |
| `naming-direction` | `render_naming_direction` | Table + recommendation blocks + avoid list + VP decision bar |

### Strategic slide anatomy

Each strategic slide in the input Markdown has this structure:

```markdown
## Slide N — Title

### Page role
One sentence: why this slide exists.

### Key message
The single takeaway the VP should remember.

### Must show on slide
Bullets, tables, or structured data that MUST appear.

### Recommended visual
One line describing the layout pattern (maps to a layout intent above).

### Speaker script
(Optional) What the presenter says.
```

The parser extracts these sections and maps `Recommended visual` → layout intent → `render_XXX()`.

---

## Scenario Deck Layouts (Science Lab Mode)

When the parser detects `## 场景 N｜Name` format, it routes to the **scenario layout registry**:

| Layout Intent | Render Function | Visual Pattern |
|---------------|-----------------|----------------|
| `opening-cover` | `render_cover` | Blue bg + white circle |
| `narrative-frame` | `render_narrative_frame` | 3-column narrative cards |
| `three-column` | `render_scenario` | Pain points / data / products |
| `flow` | `render_flow` | 5-step process with arrows |
| `big-quote` | `render_big_quote` | Large serif quote on dark background |
| `stat-grid` | `render_stat_grid` | Data大字报 with 2-3 big numbers |
| `closing` | `render_closing` | Same as cover, "THANK YOU" |

---

## Resource Files

| File | Read when... |
|------|-------------|
| `references/checklist.md` | Step 6 self-check; verifying deck quality before delivery |
| `references/components.md` | Step 3 generating slides; need exact component CSS specs |
| `references/layouts.md` | Step 2 planning; deciding slide layouts and theme rhythm |
| `references/themes.md` | Step 2 planning; choosing color presets and verifying brand colors |
| `references/visual-verification.md` | Step 4; verifying generated deck looks correct |

---

## Core Principles

1. **Content-appropriate layout**: strategic decks use decision matrices and storyline flows; science lab decks use scenario cards and data viz
2. **Photography-first**: every page needs a photo placeholder or data viz (strategic decks may use icon/data-heavy layouts instead)
3. **Multi-color themes**: match content to color (Gut=Green, Sport=Orange, Clinical=Pink, Water=Teal, Corporate=Blue)
4. **No fake data**: use "Data TBD" placeholders, never hardcode percentages
5. **One Planet. One Health**: on cover, every footer, and closing page
6. **Cover/Closing format**: solid `#005EB8` bg + white circle + centered title + DANONE logo
7. **No decorative illustrations**: Danone is photography / data-viz driven

---

## Common mistakes

- All-blue decks (scenarios must use different theme colors)
- Solid product cards (must be white + accent top bar)
- Fake data (hardcoded percentages without user input)
- Wrong cover format (must use Opening Slide Title, not gradient hero)
- Missing "One Planet. One Health" slogan
- Monotonous theme (every slide needs light/dark/hero class)
- **Forcing strategic content into scenario templates** (VP review decks need decision grids, not 3-column scenario cards)
- **All pages using the same layout** (strategic decks need varied layouts: grids, tables, flows, comparisons)
