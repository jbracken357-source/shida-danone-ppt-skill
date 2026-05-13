# Component Catalog — Danone PPT Skill

Every component below appears in generated decks. Use exact specs.

## Cards

### Narrative Cards
- Flat, no shadows, rounded 12px
- Top accent bar: 4px height, theme color
- CSS class: `.narrative-card` with optional color modifier (`.green`, `.orange`, `.pink`)
- Metric inside card: `font-family: var(--dn-font-display)`, 52px, 700 weight, theme color

### Product Link Cards
- White background + top accent bar (4px theme color)
- **Never** solid color blocks
- CSS class: `.scenario-col.accent-bar`

## Buttons / Pills
- Pill shape: `border-radius: 6.25rem`

## Images

### Circular Placeholders
- Large: 120px diameter, 3px theme border
- Small: 64px diameter, 2px theme border
- Background: soft tint (`var(--soft)`)
- CSS class: `.img-circle`, `.img-circle-sm`

### Photo Strip
- Row of 80px circular images
- CSS class: `.photo-strip`

### Rectangular Placeholders
- `.frame-img`: full-bleed, `object-fit: cover`, 8px border-radius
- `.img-slot`: dashed border, striped background, `data-ratio` label

## Bullets
- Colored dot matching theme accent (`li::marker { color: var(--accent) }`)

## Table Header
- Background: `#CCDFF1`
- Bottom border: 1px solid `#005EB8`

## Quote Blocks
- Left accent border: 4px theme color
- Large decorative quote mark: Georgia serif, 48px, 25% opacity, top-left
- Quote text: italic, 24px, 600 weight
- Attribution: normal text, 15px, secondary color

## Data Visualization

### Big Metrics
- Font: `var(--dn-font-display)`, 64px, 700 weight, theme color
- With unit label in secondary color, 20px

### Bar Charts
- Container: 28px height, 14px border-radius, soft background
- Fill: theme color, 85% opacity
- Label: 13px, 600 weight

### Ring Charts
- 100px diameter, `conic-gradient` theme color
- White center hole: 72px
- Percentage text centered, 26px, theme color

### Stat Grid
- 3-column grid, 24px gap
- Cell: 32px padding, white bg, 1px border, 12px border-radius
- Number: 72px, 800 weight, theme color

## Flow Steps
- 5-column grid, 14px gap
- Min-height: 200px
- Top accent bar: 5px theme color
- Background: soft tint
- Step number: 42px, display font, theme color
- Circular arrow connector between steps: 28px circle + triangle

## Before/After Comparison
- 2-column grid, 32px gap
- Before: soft bg + border
- After: solid theme bg, white text

## Editorial Split
- 2-column grid, equal width
- Image: full-height, `object-fit: cover`
- Text: 72px padding, centered vertically
- Reverse variant: `.editorial-split.reverse`

## Footer
- Chapter color bar: 4px at bottom edge
- "One Planet. One Health" on every page
- Page numbering: `NN / TT` (e.g., `03 / 07`)
- Flex layout: space-between, 16px vertical padding, 72px horizontal padding

## Big Quote Page
- Centered, full-page layout
- Quote: Playfair Display, 42px, 500 weight, italic
- Source: IBM Plex Mono, 13px, uppercase, secondary color

## Cover / Closing Format

### Opening Slide
- Background: solid `#005EB8`
- White circle: 600px, centered, `border-radius: 50%`
- Title: Playfair Display, 48px, 700 weight, `#005EB8` (inside circle)
- Subtitle: 18px, `#1a1a1a`, above title
- Logo: "DANONE" 28px, 800 weight, letter-spacing 4px, at bottom of circle
- Slogan: "ONE PLANET. ONE HEALTH" 11px, teal color, below logo

### Closing Slide
- Same structure as cover
- Title: "THANK YOU", 56px, Playfair Display, 700 weight, `#005EB8`
- Subtitle: optional, 20px, `#005EB8`
- Logo + slogan: same as cover

## Strategic Components (VP Review Mode)

### Decision Cards
- `.decision-card`: rounded 12px, border 1px var(--dn-border), 18px padding
- Optional accent: left border 4px theme color for highlighted items
- Label: uppercase 11px, bold, letter-spacing 0.08em
- Body: 14px, 1.4 line-height
- Hover: subtle shadow or bg tint

### Positioning Comparison
- Before: soft bg (`var(--dn-soft)`), border, muted text
- After: solid theme bg, white text, checkmark indicators
- X marks for "not": `×` or red circle
- Check marks for "is": `✓` or green circle

### Service Priority Tags
- Hero tag: green pill (`background: var(--dn-green-soft)`, `color: var(--dn-green-dark)`)
- Core tag: blue pill (`background: var(--dn-soft)`, `color: var(--dn-blue-dark)`)
- Future tag: yellow pill (`background: var(--dn-yellow-soft)`, `color: var(--dn-yellow-dark)`)
- Pill shape: `border-radius: 6.25rem`, padding `4px 10px`

### Flywheel Guardrail
- Warning bar: yellow bg (`var(--dn-yellow-soft)`), left border 4px yellow-dark
- Bold warning label: `font-weight: 700`, dark yellow color
- Body text: 12-13px, secondary color

### Journey Map Cards
- Dark bg cards: `background: rgba(255,255,255,0.08)` on dark blue page
- Top accent bar: 5px theme color
- Arrow connectors: 28px circle + triangle between cards
- Space name: Playfair Display, 18px, 700 weight, theme color
- Space role: uppercase 12px, 600 weight, muted

### Naming Recommendation Blocks
- `.rec-block`: rounded 12px, border 1px var(--dn-border), 18px padding
- Recommended variant: solid theme border, bg tint, name in theme color
- Secondary variant: white bg, muted border
- Name: Playfair Display, 22px, 700 weight
- Description: 13px, secondary color

### Avoid List
- Label: uppercase 10px, bold, red (`#cc0000`)
- Items: italic 11px, secondary color, horizontal flex with gap

### VP Decision Bar
- Solid theme bg bar, white text, centered
- Pill buttons: white bg + theme text, or transparent + white border
- Font: 14px, 600 weight

### Eyebrow
- Uppercase 14px, 600 weight, letter-spacing 0.12em
- Theme color (not black)
- Always above slide title
