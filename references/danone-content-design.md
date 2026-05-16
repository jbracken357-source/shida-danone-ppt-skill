# Danone Content Design System — Enterprise Content Pages

> Defines the design standard for **content pages** (cover and closing are defined separately in `danone-dna.md`).
> Integrates Huashu skill design principles with Danone brand DNA.

---

## 1. Huashu Design Principles Applied to Danone

### 1.1 位置四问 (Position Four Questions)

Before designing each content page, ask:

| Question | Danone Context |
|----------|---------------|
| **Narrative role** | Is this a hero statement, data detail, comparison, quote, or process flow? |
| **Audience distance** | 10cm phone → dense cards; 1m laptop → standard; 10m projector → big metrics, minimal text |
| **Visual temperature** | Calm (data), authoritative (decisions), excited (product reveals), gentle (testimonials) |
| **Capacity estimation** | Thumbnail test — can you understand the page at 10% scale? If not, simplify. |

### 1.2 Density Modes

| Mode | Use Case | Rules |
|------|----------|-------|
| **Restraint** (default) | Most content pages | 1 key message per page, breathing room, 72px+ padding |
| **High-density** | Data pages, comparison tables, decision grids | 3+ differentiated info elements, structured hierarchy, 48px padding |

### 1.3 Anti-AI Slop Checklist

**Blacklisted patterns** (DO NOT use):
- Purple gradients
- Emoji icons
- Rounded cards with left border accent (the #1 AI tell)
- 3-column equal-width feature grid (the #2 AI tell)
- Centered everything
- Uniform border-radius across all components
- Decorative blobs / SVG dividers
- Colored left-border cards
- Generic hero copy ("Transform your workflow")
- Cookie-cutter section rhythm
- Cyber neon / GitHub dark mode aesthetic

**Positive rules** (DO use):
- `text-wrap: pretty` for editorial typography
- CSS Grid for layout (not flexbox for structural grids)
- Different border-radius per component type (anti-convergence)
- `oklch()` color space for perceptually uniform colors
- Chinese quotes using 「」
- Editorial split: image full-height + text vertically centered
- Varied section rhythm — no two consecutive pages share same layout

### 1.4 Anti-Convergence

Same intent → different HTML structures across a deck. Example:
- Slide 3: `two-column` as `.editorial-split` (image left, text right)
- Slide 6: `two-column` as `.narrative-grid` (two equal columns with accent bars)
- Slide 9: `two-column` as `.compare-grid` (before/after comparison)

The intent classification stays the same, but the visual expression varies.

---

## 2. Component Specifications

### 2.1 Narrative Cards

```
┌─────────────────────────┐
│ ▓▓▓▓ 4px accent bar     │
│                         │
│  Title (18px, 600w)     │
│  Body text (14px)       │
│  ▸ Bullet list          │
│                         │
│  Metric: 87%            │
└─────────────────────────┘
```

| Property | Value |
|----------|-------|
| Border-radius | 12px |
| Shadow | None (flat design) |
| Top accent bar | 4px height, theme accent color |
| Background | White |
| Padding | 24px |
| Title | 18px, 600 weight, `var(--dn-text)` |
| Body | 14px, normal weight, `var(--dn-text-secondary)` |
| Metric | Playfair Display, 52px, 700 weight, theme accent color |
| Bullet markers | Theme-colored dot (`li::marker { color: var(--accent) }`) |

**Color variants**: `.green`, `.orange`, `.pink`, `.teal` (override accent color)

### 2.2 Product Link Cards

```
┌─────────────────────────┐
│ ▓▓▓▓ 4px accent bar     │
│                         │
│  Product Name           │
│  Category tag (pill)    │
│  Description (13px)     │
│                         │
└─────────────────────────┘
```

| Property | Value |
|----------|-------|
| Border-radius | 12px |
| Top accent bar | 4px, theme accent color |
| Background | White (NEVER solid color blocks) |
| Border | 1px `var(--dn-border)` |
| Padding | 20px |
| Category pill | `border-radius: 6.25rem`, padding `4px 10px`, theme bg + white text |

### 2.3 Quote Blocks

```
  ┃ "The quote text flows
  ┃  here in italic serif
  ┃  with generous leading"
  ┃
     — Attribution, Source
```

| Property | Value |
|----------|-------|
| Left accent border | 4px, theme accent color |
| Decorative quote mark | Georgia serif, 48px, 25% opacity, top-left corner |
| Quote text | Italic, 24px, 600 weight, `var(--dn-font-display)` |
| Attribution | Normal, 15px, `var(--dn-text-secondary)` |
| Padding | 32px |

### 2.4 Big Quote Page (Full-Page)

| Property | Value |
|----------|-------|
| Layout | Centered, full-page |
| Quote | Playfair Display, 42px, 500 weight, italic |
| Source | IBM Plex Mono, 13px, uppercase, `var(--dn-text-secondary)` |
| Background | White or soft tint |

### 2.5 Data Visualization Components

#### Big Metric

| Property | Value |
|----------|-------|
| Number | Playfair Display, 72px, 800 weight, theme accent color |
| Unit label | 20px, `var(--dn-text-secondary)` |
| Label | 16px, 600 weight, `var(--dn-text)` |

#### Bar Chart

| Property | Value |
|----------|-------|
| Container height | 28px |
| Border-radius | 14px |
| Background | Soft theme tint |
| Fill | Theme accent color, 85% opacity |
| Label | 13px, 600 weight |

#### Ring Chart

| Property | Value |
|----------|-------|
| Diameter | 100px |
| Style | `conic-gradient(theme color)` |
| Center hole | 72px white circle |
| Percentage text | 26px, theme accent color, centered |

#### Stat Grid

| Property | Value |
|----------|-------|
| Columns | 3 |
| Gap | 24px |
| Cell padding | 32px |
| Cell background | White |
| Cell border | 1px `var(--dn-border)`, 12px border-radius |
| Number | Playfair Display, 72px, 800 weight, theme accent color |
| Label | 14px, 600 weight |

### 2.6 Flow Steps

```
  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
  │ ▓▓▓▓│  │ ▓▓▓▓│  │ ▓▓▓▓│  │ ▓▓▓▓│  │ ▓▓▓▓│
  │  01 │→ │  02 │→ │  03 │→ │  04 │→ │  05 │
  │     │  │     │  │     │  │     │  │     │
  │Text │  │Text │  │Text │  │Text │  │Text │
  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘
```

| Property | Value |
|----------|-------|
| Grid | 5-column (or 6-column) |
| Gap | 14px |
| Min-height | 200px per step |
| Top accent bar | 5px, theme accent color |
| Background | Soft theme tint |
| Step number | Playfair Display, 42px, 700 weight, theme accent color |
| Arrow connector | 28px circle + triangle between steps |

### 2.7 Before/After Comparison

| Property | Before | After |
|----------|--------|-------|
| Background | Soft tint | Solid theme color |
| Border | 1px `var(--dn-border)` | None |
| Text | `var(--dn-text-secondary)` | White |
| Label | Uppercase 10px, bold, `#cc0000` | White |
| Items | Italic 11px, secondary | White, normal |

### 2.8 Editorial Split

| Property | Value |
|----------|-------|
| Grid | 2-column, equal width |
| Image side | Full-height, `object-fit: cover` |
| Text side | 72px padding, vertically centered |
| Reverse variant | `.editorial-split.reverse` (image right, text left) |

### 2.9 Decision Cards (Strategic Mode)

| Property | Value |
|----------|-------|
| Border-radius | 12px |
| Border | 1px `var(--dn-border)` |
| Padding | 18px |
| Left accent bar | 4px, theme accent color (optional) |
| Label | Uppercase 11px, bold, letter-spacing 0.08em |
| Body | 14px, line-height 1.4 |

### 2.10 Journey Map Cards

| Property | Value |
|----------|-------|
| Background | `rgba(255,255,255,0.08)` on dark blue page |
| Top accent bar | 5px, theme accent color |
| Arrow connectors | 28px circle + triangle |
| Space name | Playfair Display, 18px, 700 weight, theme accent color |
| Space role | Uppercase 12px, 600 weight, muted |

### 2.11 Flywheel Guardrail

| Property | Value |
|----------|-------|
| Background | `var(--dn-yellow-soft)` |
| Left border | 4px, `var(--dn-yellow-dark)` |
| Warning label | 700 weight, `var(--dn-yellow-dark)` |
| Body text | 12-13px, `var(--dn-text-secondary)` |

### 2.12 Service Priority Tags

| Tag | Style |
|-----|-------|
| Hero | Green pill, `border-radius: 6.25rem`, white text |
| Core | Blue pill, same shape |
| Future | Yellow pill, same shape |

All pills: padding `4px 10px`

---

## 3. Layout Variants by Intent

| Intent | Variant A | Variant B | Variant C |
|--------|-----------|-----------|-----------|
| `big-message` | Centered big text | Left-aligned with accent bar | Full-bleed hero text |
| `two-column` | Editorial split (img+text) | Two narrative cards | Compare (before/after) |
| `three-column` | Stat grid (3-col) | Three product cards | Three-column w/image |
| `data` | Big metric + label | Bar chart row | Ring chart + stat |
| `flow` | 5-step horizontal | Vertical timeline | Numbered narrative |

**Rule**: In a single deck, never use the same variant twice consecutively for the same intent.

---

## 4. Spacing System

| Scale | Value | Usage |
|-------|-------|-------|
| xs | 8px | Micro spacing, icon gaps |
| sm | 16px | Between list items, internal card padding |
| md | 24px | Card gaps, section spacing |
| lg | 48px | Major section breaks |
| xl | 72px | Page-level padding, editorial split padding |
| 2xl | 100px | Page horizontal padding (standard) |

---

## 5. Typography Scale

| Level | Size | Weight | Line-height | Usage |
|-------|------|--------|-------------|-------|
| H1 | 48px | 700 | 1.1 | Cover/closing title |
| H2 | 36px | 700 | 1.15 | Slide title |
| H3 | 28px | 600 | 1.2 | Section headers |
| H4 | 22px | 600 | 1.25 | Card titles |
| Body | 16px | 400 | 1.5 | Body text |
| Small | 14px | 400 | 1.4 | Secondary text |
| Caption | 13px | 600 | 1.3 | Labels, pills |
| Micro | 11px | 700 | 1.2 | Tags, warnings |

**Data numbers**: Playfair Display, 2x the corresponding body size (e.g., 72px for stat grid numbers)

---

## 6. Motion / Interaction (HTML Preview Only)

- Card hover: `transform: translateY(-2px)`, subtle shadow
- Page transition: fade (200ms)
- Data bars: animate width on scroll into view (300ms, ease-out)
- Ring charts: animate from 0 to target (500ms, ease-out)

---

## 7. Canvas Dimensions

| Context | Width | Height |
|---------|-------|--------|
| Browser preview (slide canvas) | 1920px | 1080px |
| PPTX export canvas | 1280px | 720px |
| PDF export | 1280px | 720px per page |
