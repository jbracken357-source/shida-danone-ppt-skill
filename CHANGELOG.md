# Changelog

All notable changes to this project are documented in this file.

## [6.0.1] — 2026-05-16

### Changed
- **Documentation sync**: updated `.gitignore`, `AGENTS.md`, `README.md`, `ROADMAP.md` to reflect actual project state
- **`.gitignore` overhaul**: added `dht-deck/`, `Testdocs/`, `slides-preview/`, smoke-test generated artifacts (`.pptx`, `.pdf`, `.png`), consolidated patterns
- **`README.md`**: version bump to v6.0.0 → v6.0.1, added `references/` to file structure, added `input_adapter.py` and strategic mode to Quick Start, updated Known Issues to reflect v6.0 fixed state
- **`AGENTS.md`**: cleaned up "NEW:" tags, added `self-promo/` to smoke-tests directory listing

## [6.0.0] — 2026-05-13

### Added
- **Content-driven layout selection**: `plan_from_notes()` replaces hardcoded 7-slide sequence; layout assigned by content richness (data density, core message, showcase flow)
- **Theme rhythm system**: automatic hero→light→dark alternation between scenario slides; 6+ page decks get dark big-quote dividers
- **Strategic / VP Review mode**: `## Slide N — Title` parser, `StrategicSlide` dataclass, intent classification, 8 strategic renderers (cover, closing, decision-grid, positioning, master-storyline, service-architecture, hero-demo, data-flywheel, experience-space, naming-direction)
- **Image placeholder protocol**: `[img: path:label]` / `[photo: path:label]` markers extracted, distributed across scenarios, rendered as real `<img>` tags in HTML
- **Input adapter image hint preservation**: all formats (outline/topics/script) preserve `[img: xxx]` markers through normalization
- **CLI `--mode` flag**: `auto` (default), `scenario`, `strategic` with auto-detect fallback

### Changed
- `write_html_deck()` reads from `plan_from_notes()` instead of fixed 7-slide sequence
- `build_deck()` auto-detects strategic vs scenario mode from input format
- Strategic content filtered from native PPTX intent mapping (HTML-only until native layout mapping added)

### Verified
- Scenario mode: 10 slides with proper theme alternation (hero/light/light/dark/light/dark/light/dark/light/hero)
- Strategic mode: 6 slides with varied layouts (cover→positioning→service-matrix→flywheel→journey→closing)
- Auto-detect correctly routes between modes
- Image hints render as real `<img>` tags when paths provided

## [5.0.0] — 2026-05-13

### Added
- **Workflow-first SKILL.md**: 6-step workflow (Clarify → Plan → Generate → Verify → Export → Self-check) replacing dense rule dump
- **Reference files** (`references/`): checklist.md (P0-P3 quality gates), components.md (component catalog), layouts.md (layout skeletons + theme rhythm), themes.md (color presets + brand colors), visual-verification.md (screenshot + grep verification procedure)
- **Input adapter** (`scripts/input_adapter.py`): normalizes free-form topics, outlines, scripts, and structured notes into `## 场景 N｜Name` Markdown
- **Auto format detection**: input adapter auto-detects input format (structured/outline/topics/script)
- **Visual verification procedure**: structured checks for cover, theme rhythm, fonts, components, closing, and export fidelity

### Changed
- SKILL.md reduced from 165 lines to ~100 lines, delegating detail to `references/` files
- SKILL.md now documents input flexibility: accepts briefs, outlines, scripts, or structured notes
- Output format selection (PPTX/HTML/PDF) is Step 1 of the workflow
- AGENTS.md updated with input_adapter.py command, new file structure, 6-step workflow

### Verified
- Brand color `#005EB8` consistent across tokens.css, HTML deck CSS, and PPTX template

## [4.0.0] — 2026-05-12

### Added
- **Editorial font stack**: Playfair Display (serif headlines) + Inter (body) + IBM Plex Mono (data/labels)
- **Visual depth system**: subtle card shadows, radial gradients on cover/closing, backdrop-filter blur, ghost numbers
- **New image placeholder system**: `.frame-img` (object-fit:cover) + `.img-slot` (editorial dashed border with ratio labels)
- **Theme rhythm**: slides mark `theme="light"` / `theme="dark"` / `theme="hero"` for visual pacing
- **New layout CSS**: Stat Grid, Before/After comparison, Image+Text editorial split, Big Quote
- **Runtime mapping validation**: warns when content keys fail to map to shapes
- **Unused resource cleanup**: traces referenced media/layouts/masters and removes unreferenced files
- **Slide number fix**: updates `sldNum` placeholder to output sequence (1, 2, 3...)
- **Dangling reference cleanup**: removes unused image relationships from slide rels when pics are removed

### Changed
- Replaced Arial Narrow fallback with editorial magazine font stack
- Updated `tokens.css` with new font variables and `font-feature-settings: "tnum"`
- Replaced `.img-circle` wireframe placeholders with `.img-slot` editorial placeholders
- Enhanced cover/closing with radial gradient overlays

### Fixed
- **Native PPTX file size**: 15-20MB → ~700KB (removed 562 unreferenced files)
- **Content mapping**: `contents` intent now maps to idx=16,22-25; `three-column` / `scenario-detail` map to idx=21-26
- **Slide numbers**: now show correct output page numbers instead of original template page numbers
- **Dangling image refs**: removing `<p:pic>` now cleans up slide rels files

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

### Known Issues (v3.1.0)
- **HTML Deck visual quality**: Arial Narrow fallback looks cheap; layouts are monotonous; no visual depth (gradients/shadows); no dark-page rhythm
- **Native PPTX bloat**: Output files are 15-20MB because unused media/layouts/masters are not pruned
- **Native PPTX content mapping broken**: `contents` and `three-column` intents map to wrong placeholder indices
- **Native PPTX slide numbers**: Show original template slide numbers instead of output sequence (1, 2, 3...)
- **Native PPTX dangling refs**: Removing `<p:pic>` elements does not clean up slide rels files
- **Unsupported intents**: `image-content` and `section-photo` raise `NotImplementedError`

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
