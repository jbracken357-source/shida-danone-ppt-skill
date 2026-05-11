---
name: shida-danone-ppt-skill
description: Use when creating Danone-inspired corporate presentation decks, ESG reports, product launch decks, Danone-style HTML slides, PDF exports, image PPTX exports, or editable PPTX exports.
version: 3.1.0
author: Shida Fu
tags: [presentation, slides, html, danone, corporate, design-system, pptx, pdf]
---

# Shida Danone PPT Skill

> Generate Danone-style corporate decks. Photo-first layouts, multi-color category themes, "One Planet. One Health" brand DNA. Prefer real template-native PPTX when editability matters; use HTML pipeline for PDF, image PPTX, and fallback pages.

## When to use

- Danone / corporate-style reports, ESG decks, product launches
- Deliverables needing PDF + PPTX
- Personal talks -> use guizang-ppt-skill
- Creative prototypes -> use huashu-design
- Dark dashboards -> Danone is light-first

## Output paths

### 1. Native editable PPTX (preferred for editability)
```bash
python scripts/brief_to_native_deck.py --title "X" --brief-file brief.md --slides 6 --out deck.pptx
```
Copies real template layouts from `Danone Real Templates/Standard Danone Template.pptx`, fills native placeholders. For structured notes, use `scripts/notes_to_danone_deck.py`.

### 2. HTML deck (preferred for visual fidelity)
```bash
python scripts/notes_to_danone_deck.py --notes notes.md --out-dir ./deck --brand-line "Brand X · Danone"
```
Generates 1280x720px HTML slides with full brand system (photo placeholders, data viz, multi-color themes).

### 3. PDF
```bash
node scripts/export_deck_pdf.mjs --slides slides/ --out deck.pdf --width 1280 --height 720
```

### 4. Image PPTX
```bash
node scripts/export_deck_pptx.mjs --slides slides/ --out deck.pptx --width 1280 --height 720
```

## Design rules

### Brand DNA (non-negotiable)
- **Hero cover**: Opening Slide Title format — solid `#005EB8` background, large centered white circle (`border-radius: 50%`), title in blue `#005EB8` centered inside circle, subtitle above title, DANONE logo + "One Planet. One Health" at bottom of circle
- **Slogan**: "One Planet. One Health" must appear on cover + footer
- **Photography-first**: every page should have photo placeholders; Danone is not text-only
- **Multi-color themes**: match category to colorway
  - Gut/Natural -> Green `#00A651`
  - Sport/Physical -> Orange `#F26522`
  - Clinical/Baby -> Pink `#E6007E`
  - Water/Hydration -> Teal `#00B2A9`
  - Corporate/Default -> Blue `#005EB8`

### Typography
- Display: Danone One Condensed (fallback: Arial Narrow -> Arial)
- Body: Danone One Light (fallback: Arial Narrow -> Arial)
- Chinese: Microsoft YaHei / Noto Sans SC

### Components

#### Cards
- Flat, no shadows, rounded 12px
- **Narrative cards**: top accent bar (4px theme color)
- **Product link cards**: white background + top accent bar (4px theme color), not solid color blocks

#### Buttons
- Pill shape (`border-radius: 6.25rem`)

#### Images
- `border-radius: .75rem` or circular (`50%`)
- **Circular placeholders**: 120px/64px diameter, 3px/2px theme color border, soft tint background
- **Photo strip**: row of 80px circular images for product showcases

#### Bullets
- Colored dot matching theme accent

#### Table header
- `#CCDFF1` with `#005EB8` bottom border

#### Quote blocks
- Left accent border (4px theme color)
- **Large decorative quote mark** (Georgia serif, 48px, 25% opacity) at top-left
- Italic text for the quote
- Normal text for attribution below

#### Data visualization placeholders
- **Bar charts**: 28px height, pill-shaped, theme color fill on soft background
- **Ring charts**: 100px diameter, conic-gradient, white center hole, percentage text
- **Big metrics**: 64px display font, theme color, with unit label
- **No fake data**: if the user has not provided real numbers, use gray empty placeholders labeled "数据待补充" / "Data TBD" — never hardcode percentages like 87%, 92%

#### Flow steps
- 5-column grid, soft background
- **Top accent bar** (5px theme color)
- **Circular arrow connectors** between steps (28px circle + triangle)
- Step number in display font

#### Footer
- Chapter color bar (4px) at bottom edge
- "One Planet. One Health" on every page
- Page numbering `NN / TT`

### Closing page
- Closing Slide Title format — solid `#005EB8` background, large centered white circle (`border-radius: 50%`), "THANK YOU" in blue `#005EB8` centered inside circle, optional subtitle below, DANONE logo + "One Planet. One Health" at bottom of circle

## Self-check

### Structure (before generating)
- [ ] Content organized as Opening → Body → Closing
- [ ] Every page has a photo placeholder or data viz — no pure-text pages
- [ ] Each scenario/category uses a distinct theme color (not all blue)

### Cover
- [ ] Cover uses Opening Slide Title format (solid blue bg + white circle + centered blue title + DANONE logo)
- [ ] "One Planet. One Health" appears on cover
- [ ] Subtitle/date positioned above the main title

### Body pages
- [ ] Cards have top accent bar matching theme color
- [ ] Product link cards are white with accent top bar (not solid color blocks)
- [ ] Data visualization uses real numbers from input, or gray "Data TBD" placeholders (no fake percentages)
- [ ] Quote blocks have decorative quote mark (Georgia serif, 48px, 25% opacity)
- [ ] Flow steps have circular arrow connectors between them
- [ ] Circular images have theme-colored borders (3px for large, 2px for small)

### Closing
- [ ] Thank You page uses Closing Slide Title format (blue bg + white circle + THANK YOU + DANONE logo)
- [ ] "One Planet. One Health" appears on closing page

### Global
- [ ] Footer has chapter color bar (4px) on every page
- [ ] No decorative illustrations — Danone is photography-driven
- [ ] No gradient overlays on cover or closing — solid `#005EB8` only

## Common mistakes to avoid

- **All-blue decks**: Don't give every page the corporate blue. Different scenarios must use different theme colors.
- **Solid product cards**: Product link cards must be white background + colored top bar. Never use solid color blocks.
- **Decorative illustrations**: Danone is photography-driven. Do not add icons, illustrations, or clipart as decorative elements.
- **Fake data**: Never hardcode percentages (87%, 92%, etc.) or bar widths. Use real input data or gray "Data TBD" placeholders.
- **Wrong cover format**: Cover must use Opening Slide Title format (white circle on blue), not a generic gradient hero.
- **Missing slogan**: "One Planet. One Health" must appear on cover, footer of every page, and closing page.
- **Text-only pages**: Every slide needs either a photo placeholder or a data visualization element.
