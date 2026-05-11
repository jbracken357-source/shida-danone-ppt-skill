# Changelog

All notable changes to this project are documented in this file.

## [3.1.0] — 2026-05-11

### Added
- Photo-first deck system — every slide includes photo placeholders
- Multi-color category themes (Gut→Green, Sport→Orange, Clinical→Pink, Water→Teal, Corporate→Blue)
- `templates/tokens.css` — centralized design system tokens
- `templates/layout-map.json` — semantic intent-to-layout mapping
- `scripts/profile_danone_template.py` — template profiler generating JSON manifest
- `assets/deck_index.html` — reusable multi-file slide deck shell
- Bilingual README (EN+CN)

### Changed
- Cover and closing pages aligned with official Danone "Opening Slide Title" / "Closing Slide Title" format
- `notes_to_danone_deck.py` now generates structured HTML slides with full brand system
- Smoke test outputs gitignored to reduce repo noise

### Fixed
- Correct caps handling in native builder
- Three-column layout mapping accuracy
- Layout cleanup for consistent spacing

---

## [3.0.0] — 2026-05 (earlier)

### Added
- Native editable PPTX builder (`scripts/build_native_pptx.py`)
- Template XML cloning approach — copies real sample slides instead of synthesizing layouts
- `scripts/brief_to_native_deck.py` — converts text briefs into native PPTX plans
- `scripts/notes_to_danone_deck.py` — converts structured Markdown notes into decks
- Dual-path architecture: Native PPTX (editability) + HTML deck (visual fidelity)

### Changed
- Replaced HTML-to-editable-PPTX approach with template-native XML cloning
- Significantly faster build times (no browser launch per slide)

---

## [2.1.0] — 2026-04 (earlier)

### Added
- Full HTML → PDF / PPTX export pipeline
- `scripts/export_deck_pdf.mjs` — vector PDF export via Playwright
- `scripts/export_deck_pptx.mjs` — image-based PPTX export via Playwright + pptxgenjs
- Support for 1280×720 and 1920×1080 canvas sizes

---

## [2.0.0] — 2026-04 (earlier)

### Changed
- Major skill optimization based on evaluation rubric (score improved from 68→87)
- Refined design system alignment with real Danone template

---

## [1.0.0] — 2026-04 (earlier)

### Added
- Initial Shida Danone PPT Skill
- Basic HTML slide generation
- Danone brand color system (blue primary)

---

## Removed / Backlogged

- **Node.js HTML-to-editable-PPTX path** (`scripts/html2pptx.js`): Removed in v3.0.
  - Reason: heavy dependencies, fragile DOM-to-PPTX mapping, not truly editable
  - Decision record: `backlog/node-js-html-to-pptx.md`
  - Will only be revived if native builder cannot support a required layout
