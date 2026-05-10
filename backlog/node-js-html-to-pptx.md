# Backlog: Node.js HTML-to-PPTX Conversion Path

## Status
On hold. Native PPTX builder (`scripts/build_native_pptx.py`) is the current production path.

## What It Was
A Node.js-based pipeline that converted HTML/CSS slide renders into editable PPTX using:
- **Playwright** to render HTML slides in a headless browser
- **pptxgenjs** to generate PPTX from measured DOM bounding boxes and text content
- Targeted the same JSON slide plan consumed by the native builder

## Why It Was Removed
The approach was discarded during the "Musk-ify" refactor (commit bd3b38b) because:
1. **Heavy dependency chain** — required Node.js, Playwright browser binaries, and a pptxgenjs wrapper
2. **Fragile text measurement** — DOM-to-PPTX coordinate mapping broke whenever template CSS changed
3. **Not truly editable** — pptxgenjs created shapes from scratch; they looked correct but didn't inherit Danone template masters, layouts, or theme colors
4. **Slower** — launching a browser per slide plan was orders of magnitude slower than cloning XML parts

## When to Revive It
Consider reviving this path ONLY if:
- The native builder cannot support a required layout that has no sample slide in the template
- Complex image placement/positioning becomes a hard requirement and the native builder's image replacement remains unimplemented
- A future stakeholder explicitly requests HTML-first design fidelity over native editability

## Reference Implementation
The last known working version was in `scripts/html2pptx.js` before commit bd3b38b. If needed, recover it from git:

```bash
git show bd3b38b^:scripts/html2pptx.js > backlog/html2pptx-recovered.js
```

## Trade-off Summary
| Concern | Native Builder (current) | Node.js HTML Path (backlog) |
|---------|--------------------------|----------------------------|
| Editability | High — real template masters/layouts | Low — synthetic shapes |
| Fidelity to HTML design | Medium — limited by template geometry | High — pixel-perfect from browser |
| Speed | Fast — XML clone + text swap | Slow — browser launch + measurement |
| Dependencies | Python stdlib only | Node.js + Playwright + pptxgenjs |
| Maintenance | Low — template-driven | High — CSS drift breaks mapping |
