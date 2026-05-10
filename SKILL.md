---
name: shida-danone-ppt-skill
description: Use when creating Danone-inspired corporate presentation decks, ESG reports, product launch decks, Danone-style HTML slides, PDF exports, image PPTX exports, or editable PPTX exports.
version: 2.2.0
author: Shida Fu
tags: [presentation, slides, html, danone, corporate, design-system, pptx, pdf]
---

# Shida Danone PPT Skill

> Generate Danone-style corporate decks. Prefer real template-native PPTX when editability matters; use HTML pipeline for PDF, image PPTX, and fallback pages.

## When to use

- ✅ Danone / corporate-style reports, ESG decks, product launches
- ✅ Deliverables needing PDF + PPTX
- ❌ Personal talks → use guizang-ppt-skill
- ❌ Creative prototypes → use huashu-design
- ❌ Dark dashboards → Danone is light-first

## Output paths

### 1. Native editable PPTX (preferred for editability)
```bash
python scripts/brief_to_native_deck.py --title "X" --brief-file brief.md --slides 6 --out deck.pptx
```
Copies real template layouts from `Danone Real Templates/Standard Danone Template.pptx`, fills native placeholders. For DHT Lab structured notes, use `scripts/notes_to_danone_deck.py`.

### 2. PDF
```bash
node scripts/export_deck_pdf.mjs --slides slides/ --out deck.pdf --width 1280 --height 720
```

### 3. Image PPTX
```bash
node scripts/export_deck_pptx.mjs --slides slides/ --out deck.pptx --width 1280 --height 720
```

## Design rules

- Hero: solid `#005EB8`, no gradients
- Buttons: pill shape (`border-radius: 6.25rem`)
- Cards: flat, no shadows
- Images: `border-radius: .75rem`
- Bullets: blue dot `#005EB8`
- Table header: `#CCDFF1` with `#005EB8` bottom border
- No decorative illustrations (Danone is photography-driven)

## Self-check

- [ ] Title has no placeholders
- [ ] Hero is solid `#005EB8` (no gradient)
- [ ] Cards have no `box-shadow`
- [ ] Buttons are pill-shaped
- [ ] Images have `border-radius: .75rem`
