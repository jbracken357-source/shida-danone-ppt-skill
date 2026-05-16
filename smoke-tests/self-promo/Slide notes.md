# Shida Danone PPT Skill — Self-Promo Deck

---

## Slide 1｜Opening Cover

### Title
Shida Danone PPT Skill

### Subtitle
Turn rough notes into polished corporate decks

### Tagline
One Planet. One Health

---

## Slide 2｜What Is It?

### Headline
A Claude Code skill for Danone-style presentations

### Key Points
- Photo-first layouts with multi-color category themes
- Dual-path architecture: native editable PPTX + HTML deck pipeline
- Built on the real Standard Danone Template

### Visual
Architecture diagram: Input → Native PPTX (editable) or HTML → PDF / Image PPTX

---

## Slide 3｜Why It Matters

### Headline
Three values that save hours

### Value 1 — Template Consistency
Clones real Danone master slides. Every deck follows brand DNA.

### Value 2 — Editable Text
Native PPTX path keeps all text editable in PowerPoint. No raster traps.

### Value 3 — Multi-Format Output
One source → editable PPTX, vector PDF, or image PPTX. Your choice.

---

## Slide 4｜Install in 30 Seconds

### Headline
Two commands. Done.

### Step 1
mkdir -p ~/.claude/skills/shida-danone-ppt-skill

### Step 2
cp SKILL.md ~/.claude/skills/shida-danone-ppt-skill/SKILL.md

### Extra
npm install  # for PDF/PPTX export engines

---

## Slide 5｜How to Use

### Headline
Four output paths. Pick yours.

### Path 1 — Native Editable PPTX
python scripts/brief_to_native_deck.py --title "X" --brief-file brief.md --slides 6 --out deck.pptx

### Path 2 — HTML Deck
python scripts/notes_to_danone_deck.py --notes notes.md --out-dir ./deck --brand-line "Brand X · Danone"

### Path 3 — PDF Export
node scripts/export_deck_pdf.mjs --slides ./deck/slides/ --out deck.pdf

### Path 4 — Image PPTX
node scripts/export_deck_pptx.mjs --slides ./deck/slides/ --out deck.pptx

---

## Slide 6｜Closing

### Headline
THANK YOU

### Subtitle
Ready to build your next Danone deck?

### Contact
Copy SKILL.md → ~/.claude/skills/shida-danone-ppt-skill/
