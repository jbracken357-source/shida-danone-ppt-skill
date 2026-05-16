# Visual Verification — Danone PPT Skill

After generating any deck, perform these checks before delivery.

## 1. Cover Verification

Open the deck and verify the cover slide:

- **Background**: solid `#005EB8` — no gradients, no overlays, no wrong colors
- **White circle**: 600px diameter, centered, `border-radius: 50%`
- **Title**: Playfair Display, 48px, 700 weight, `#005EB8`, centered inside circle
- **Subtitle**: above title, 18px, `var(--dn-text)` / `#262627`
- **Logo**: "DANONE" at bottom of circle, 28px, 800 weight, letter-spacing 4px
- **Slogan**: "ONE PLANET. ONE HEALTH" below logo, 11px, teal

**Grep check** (for HTML decks):
```bash
grep 'opening-slide\|closing-slide' slides/01-cover.html
grep '#005EB8\|var(--dn-blue)' slides/01-cover.html
```

**Quick check**: If the cover background is anything other than solid `#005EB8`, stop and fix.

## 2. Theme Rhythm Verification

List all slide theme classes:
```bash
grep -o 'theme="[a-z]*"' slides/*.html | sort | uniq -c
```

Check:
- No 3+ consecutive slides with the same `theme` value
- At least 1 `theme="hero"` slide per 3-4 content pages
- Cover and closing are `theme="hero"`

## 3. Font Verification

Open the deck in a browser (for HTML) or PowerPoint (for PPTX):

- **Headlines** show serif font (Playfair Display). If sans-serif appears, font failed to load
- **Body** shows clean sans-serif (Inter). If Arial/system font appears, check Google Fonts CDN connectivity
- **Data** shows monospace (IBM Plex Mono) for metrics and page numbers

**Grep check** (for HTML decks):
```bash
grep 'fonts.googleapis.com' slides/*.html  # Should match every slide
```

## 4. Component Spot-Check

Open the first scenario/content slide and verify:

- **Accent bar** at top of cards matches the scenario's theme color (green/orange/pink/teal/blue)
- **Product cards** are white background with colored top bar (never solid color blocks)
- **Quote block** has large decorative " mark at top-left (Georgia serif, semi-transparent)
- **Bullet markers** match the theme color
- **Footer** has 4px color bar at bottom edge + "One Planet. One Health" + page numbering

## 5. Closing Verification

Same checks as cover, but:
- Title is "THANK YOU" (56px, Playfair Display)
- Optional subtitle below title
- "One Planet. One Health" appears at bottom of circle

## 6. Export Verification

### PDF (from HTML)
- Open in PDF viewer
- Text should be **searchable** (vector PDF, not bitmap)
- All slides render at 1280x720 resolution
- Fonts are embedded or rendered correctly

### Image PPTX (from HTML)
- Open in PowerPoint
- Each slide is a full-bleed image (not editable text)
- Resolution matches 1280x720
- Visual fidelity: colors and fonts match the HTML source

### Native Editable PPTX
- Open in PowerPoint
- Text is **editable** (native text, not images)
- File size is reasonable (< 5MB)
- Layout matches the template masters
- Slide numbers are correct

## 7. Screenshot Contact Sheet

For visual validation, generate a contact sheet:
```bash
# After running the HTML deck generation
node scripts/export_deck_pptx.mjs --slides ./deck/slides/ --out ./deck/contact.pptx --width 1280 --height 720
```

Open the resulting PPTX in PowerPoint and scan through slides to verify:
- Cover color is correct
- Theme rhythm alternates properly
- No blank or broken slides
- All component styles render as expected
