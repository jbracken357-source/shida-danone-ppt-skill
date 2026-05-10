# Shida Danone PPT Skill

Danone-style corporate presentation generator. Prioritizes real template-native editable PPTX; uses HTML pipeline for PDF and image PPTX exports.

## Install

```bash
npm install playwright pdf-lib pptxgenjs sharp
```

## Smoke tests

`smoke-tests/` contains example inputs and outputs for all three paths. Run manually:

```bash
# Native editable PPTX from brief
python scripts/brief_to_native_deck.py --title "X" --brief-file smoke-tests/brief-native/brief.md --slides 6 --out smoke-tests/brief-native/deck.pptx

# HTML deck + native PPTX from structured notes
python scripts/notes_to_danone_deck.py --notes "smoke-tests/dht-lab-notes/Slide notes.md" --out-dir smoke-tests/dht-lab-notes --native-pptx smoke-tests/dht-lab-notes/deck.pptx

# PDF export from HTML slides
node scripts/export_deck_pdf.mjs --slides smoke-tests/dht-lab-notes/slides --out smoke-tests/dht-lab-notes/deck.pdf --width 1280 --height 720
```

## License

MIT
