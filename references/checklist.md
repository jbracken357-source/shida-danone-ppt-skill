# Quality Checklist — Danone PPT Skill

Run this checklist after generating any deck. Issues are graded by severity.

## P0 — Must Not Fail

- [ ] Cover uses solid `#005EB8` background (not gradient, not wrong color)
- [ ] Cover title is centered inside white circle
- [ ] "One Planet. One Health" appears on cover
- [ ] "One Planet. One Health" appears in footer of every body page
- [ ] "One Planet. One Health" appears on closing page
- [ ] Closing uses same format as cover (solid `#005EB8` bg + white circle + centered text)
- [ ] No fake data: use "Data TBD" / "数据待补充" placeholders (no hardcoded percentages like 87%, 92%)
- [ ] Fonts load correctly: Playfair Display (headlines), Inter (body), IBM Plex Mono (data), Noto Sans SC (Chinese)

## P1 — Structure

- [ ] Deck organized as Opening → Body → Closing
- [ ] Every page has a photo placeholder or data visualization — no pure-text pages
- [ ] Theme rhythm: no 3+ consecutive pages of the same theme (light/dark/hero)
- [ ] 6+ page decks have at least 1 hero page (cover, chapter divider, or big quote)
- [ ] Each scenario/category uses a distinct theme color (not all blue)
- [ ] Slide count matches the plan/manifest

## P2 — Component Fidelity

- [ ] Narrative cards have top accent bar (4px) matching their theme color
- [ ] Product link cards are white background + accent top bar (never solid color blocks)
- [ ] Quote blocks have decorative quote mark (Georgia serif, 48px, 25% opacity)
- [ ] Flow steps have circular arrow connectors between them
- [ ] Circular image placeholders have theme-colored borders (3px large, 2px small)
- [ ] Data visualization uses real input numbers or gray "Data TBD" placeholders
- [ ] Table headers use `#CCDFF1` background with `#005EB8` bottom border

## P3 — Polish

- [ ] No decorative illustrations — Danone is photography-driven
- [ ] No gradient overlays on cover or closing — solid `#005EB8` only
- [ ] Visual depth exists: subtle shadows, gradients, or backdrop-blur on overlays
- [ ] No wireframe image placeholders (`.img-slot` with dashed borders is OK for placeholders; colored circles are not)
- [ ] No monotonous theme: every slide has a theme class (`light`/`dark`/`hero`)
- [ ] No Arial Narrow or generic system sans-serif for headlines
