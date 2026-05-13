# Layout Catalog — Danone PPT Skill

## Layout Skeletons

| Intent | Layout Class | Use Case |
|--------|-------------|----------|
| `opening-cover` | `.opening-slide` | Cover slide — title + brand + slogan |
| `closing` | `.closing-slide` | Thank you slide — same format as cover |
| `big-message` | `.slide` with `.title` + `.headline` | Single key takeaway, no columns |
| `three-column` | `.scenario-body` (3-col grid) | Scenario detail: pain points / data / products |
| `two-column` | `.editorial-split` | Image left + text right (or reversed) |
| `flow` | `.flow-grid` (5-col or 6-col) | Process steps with arrow connectors |
| `big-quote` | `.big-quote-slide` | Full-page centered quote |
| `stat-grid` | `.stat-grid` (3-col) | Data highlights with big numbers |
| `compare` | `.compare-grid` (2-col) | Before/after comparison |
| `contents` | `.slide` with `.narrative-grid` | Table of contents / narrative frame |

## Strategic Layouts (VP Review Mode)

| Intent | Layout Class | Use Case |
|--------|-------------|----------|
| `decision-grid` | `.decision-grid` | VP decision cards (2×2 or 1×4): positioning, storyline, hero demo, naming |
| `positioning` | `.positioning-slide` | Two-column contrast: "What DHT Is Not" vs "What DHT Is" |
| `master-storyline` | `.storyline-flow` | Horizontal spine: Vision → Pillars → Services → Demos → Flywheel → Experience |
| `service-architecture` | `.service-matrix` | Lifecycle matrix table with colored priority tags (Hero/Core/Future) |
| `hero-demo` | `.hero-split` | Two-column hero blocks comparing two flagship demos |
| `data-flywheel` | `.flywheel-grid` | Circular data-learning loop (6 steps) with guardrail bar |
| `experience-space` | `.journey-map` | 4-column physical experience journey with arrow connectors |
| `naming-direction` | `.naming-slide` | Table of naming territories + recommendation blocks + VP decision bar |

## PPTX Layout Mapping

See `templates/layout-map.json` for the full mapping. Key intents:

### Scenario Mode
| Intent | PPTX Layout | Fallback |
|--------|-------------|----------|
| `opening-cover` | Title Slide | — |
| `contents` | Contents | Title Slide |
| `big-message` | Blue: Full White - Big Text / No Caps | Title Slide |
| `three-column` | Aqua: Three Column w/Image | Blue: Two Content Box |
| `two-column` | Blue: Two Content Box | — |
| `flow` | Blue: Two Content Box (split) | Title Slide |
| `closing` | Closing Slide | Title Slide |

### Strategic / VP Review Mode
| Intent | PPTX Layout | Fallback |
|--------|-------------|----------|
| `cover` | Title Slide | — |
| `decision-grid` | Blue: Full White + Custom 4-box | Title Slide |
| `positioning` | Blue: Two Content Box | — |
| `master-storyline` | Blue: Full White - Big Text | Title Slide |
| `service-architecture` | Aqua: Three Column w/Image | Blue: Two Content Box |
| `hero-demo` | Blue: Two Content Box | — |
| `data-flywheel` | Blue: Full White - Big Text | Title Slide |
| `experience-space` | Aqua: Three Column w/Image (4-col custom) | Blue: Two Content Box |
| `naming-direction` | Blue: Full White + Custom table | Title Slide |
| `closing` | Closing Slide | Title Slide |

## Theme Rhythm Planning

### Hard Rules

1. **No 3+ consecutive pages** of the same theme (light/dark/hero)
2. **6+ page decks** must include at least 1 hero page every 3-4 content pages
3. **Cover = hero**, **Closing = hero**
4. **Mix theme colors** per scenario (Gut=Green, Sport=Orange, Clinical=Pink, Water=Teal, Corporate=Blue)

### Theme Assignment

Every slide gets:
- A **theme class**: `light` (white bg), `dark` (dark blue bg), `hero` (full-bleed photo bg)
- A **theme color**: the accent color for that slide's scenario/category

### Rhythm Template: Scenario Mode (8-page deck)

| Page | Type | Theme Class | Theme Color |
|------|------|-------------|-------------|
| 1 | Cover | hero | Blue `#005EB8` |
| 2 | Narrative Frame | light | Green `#00A651` |
| 3 | Scenario 1 (Gut) | light | Green `#00A651` |
| 4 | Scenario 2 (Sport) | dark | Orange `#F26522` |
| 5 | Scenario 3 (Clinical) | light | Pink `#E6007E` |
| 6 | Showcase Flow | light | Blue `#005EB8` |
| 7 | Big Quote | hero | Blue `#005EB8` |
| 8 | Closing | hero | Blue `#005EB8` |

This rhythm alternates: hero → light → light → dark → light → light → hero → hero.
No 3+ consecutive same-theme pages. Hero pages at positions 1, 7, 8.

### Rhythm Template: Strategic / VP Review Mode (10-page deck)

| Page | Type | Theme Class | Theme Color |
|------|------|-------------|-------------|
| 1 | Cover | hero | Blue `#005EB8` |
| 2 | Executive Ask (decision-grid) | light | Blue `#005EB8` |
| 3 | Positioning | light/dark | Green `#00A651` |
| 4 | Master Storyline (flow) | dark | Blue `#005EB8` |
| 5 | Service Architecture (matrix) | light | Blue `#005EB8` |
| 6 | Hero Demo (split) | light | Green `#00A651` |
| 7 | Data Flywheel | light | Yellow `#FFD700` |
| 8 | Experience Space (journey) | dark | Blue `#005EB8` |
| 9 | Naming Direction | light | Blue `#005EB8` |
| 10 | Closing | hero | Blue `#005EB8` |

Strategic decks use dark blue backgrounds for storyline/journey pages (creating visual "chapters"), white backgrounds for data-heavy pages, and hero for bookends.
