# Danone Design DNA — Fixed Anchor Points

> Extracted from `Danone Real Templates/Standard Danone Template.pptx` (profiled via `scripts/profile_danone_template.py`).
> These are the **invariant brand elements** that MUST appear on every output, regardless of layout or theme.
> All values are defined in `../templates/tokens.css`.

---

## 1. Cover Slide (Opening)

**Structure** (ASCII):
```
┌─────────────────────────────────────────┐
│                                         │
│           solid #005EB8 bg              │
│                                         │
│              ╭─────────╮                │
│              │         │                │
│              │  white  │                │
│              │  600px  │                │
│              │ circle  │                │
│              │         │                │
│              ╰─────────╯                │
│                                         │
└─────────────────────────────────────────┘
```

**Elements inside circle** (top to bottom):
| Element | Spec |
|---------|------|
| Subtitle | 18px, `var(--dn-text)`, normal weight |
| Title | 48px, `var(--dn-font-display)`, 700 weight, `var(--dn-blue)`, centered |
| Logo text | "DANONE", 28px, 800 weight, letter-spacing 4px |
| Slogan | "ONE PLANET. ONE HEALTH", 11px, letter-spacing 2px |

**Hard rules**:
- Background MUST be solid `#005EB8` — NO gradients, NO overlays
- Circle is 600px diameter, white (`#FFFFFF`), centered horizontally and vertically
- No decorative illustrations, no photos on cover
- No gradient overlays on cover

---

## 2. Closing Slide

Same structure as cover, but:
- Title text: "THANK YOU" (56px, `var(--dn-font-display)`, `var(--dn-blue)`)
- Optional subtitle below title (20px, `var(--dn-blue)`)
- Logo and slogan area same as cover

---

## 3. Footer (Every Body Page)

```
┌─────────────────────────────────────────┐
│                                         │
│            slide content                  │
│                                         │
├─────────────────────────────────────────┤
│ ┃ 4px theme color bar (bottom edge)     │
│ [Logo]  One Planet. One Health    03/07 │
└─────────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Color bar | 4px height, bottom edge, theme accent color |
| Logo | Danone logo (left-aligned) |
| Slogan | "One Planet. One Health" (center area) |
| Page number | `NN / TT` format (right-aligned, e.g. `03 / 07`) |
| Padding | 16px vertical, 72px horizontal |

---

## 4. Font Stack

| Role | Primary Font | Fallback Chain | CSS Variable |
|------|-------------|----------------|-------------|
| Headlines / Display | Playfair Display | Noto Sans SC, PingFang SC, serif | `--dn-font-display` |
| Body | Inter | Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif | `--dn-font` |
| Data / Mono | IBM Plex Mono | SF Mono, Consolas, monospace | `--dn-font-mono` |

**Font loading**: Google Fonts CDN
```
https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap
```

**Blacklist**: Papyrus, Comic Sans, Lobster, Impact, Jokerman
**Avoid for headlines**: Inter, Roboto, Arial, Helvetica, Open Sans, Lato, Montserrat, Poppins, Space Grotesk

---

## 5. Color System

### Brand Core
| Token | Value | Usage |
|-------|-------|-------|
| `--dn-blue` | `#005EB8` | Cover/closing bg, corporate accent |
| `--dn-blue-mid` | `#0068CC` | Mid-level accent |
| `--dn-blue-dark` | `#002677` | Dark theme bg, dark page backgrounds |
| `--dn-blue-light` | `#00ACED` | Light accent, links |
| `--dn-tint` | `#CCDFF1` | Table headers, light tint |
| `--dn-soft` | `#F4F8FC` | Soft backgrounds, before/after comparison |
| `--dn-text` | `#262627` | Primary text color |
| `--dn-text-secondary` | `rgba(0,0,0,0.6)` | Secondary text |
| `--dn-border` | `rgba(0,0,0,0.15)` | Borders, dividers |

### Category Accent Themes
| Category | Accent | Soft bg | Dark | Trigger Keywords |
|----------|--------|---------|------|-----------------|
| Corporate | `#005EB8` | `#F4F8FC` | `#002677` | corporate, default |
| Gut/Natural | `#00A651` | `#E6F7EF` | `#007A3D` | gut, 肠道, digest, microbiome |
| Sport/Physical | `#F26522` | `#FEF0E8` | `#C44A14` | sport, physical, 运动, recovery |
| Clinical/Baby | `#E6007E` | `#FCE6F2` | `#B30063` | clinical, tube, medical, 管饲 |
| Water/Hydration | `#00B2A9` | `#E6F8F7` | `#008A82` | water, hydration, 水, 汗液 |

### Data Accents
| Token | Value | Usage |
|-------|-------|-------|
| `--dn-yellow` | `#FFC72C` | Warnings, attention, future tags |
| `--dn-yellow-soft` | `#FFF8E1` | Warning background (flywheel guardrail) |
| `--dn-yellow-dark` | `#CC9E1F` | Warning text |

---

## 6. Content Page Skeleton

Every body page follows this structure:
```
┌─────────────────────────────────────────┐
│ [Eyebrow] (optional)                    │
│ Title (24-32px, display font)           │
│ ─────────────────────────────────────   │
│                                         │
│           Content Area                  │
│    (cards / columns / data / images)    │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│ ┃ 4px theme color bar                   │
│ [Logo]  One Planet. One Health    03/07 │
└─────────────────────────────────────────┘
```

**Key principles**:
- Every page has a photo placeholder OR data visualization — NO pure-text pages
- Theme rhythm: no 3+ consecutive pages of same theme (light/dark/hero)
- Each scenario/category uses a distinct theme color (not all blue)
- Eyebrow text (optional): uppercase 14px, 600 weight, letter-spacing 0.12em, theme color

---

## 7. Theme Rhythm Hard Rules

1. Cover = hero theme, Closing = hero theme
2. No 3+ consecutive pages of the same theme (light/dark/hero)
3. 6+ page decks MUST include at least 1 hero page every 3-4 content pages
4. Mix theme colors per scenario (Gut=Green, Sport=Orange, Clinical=Pink, Water=Teal, Corporate=Blue)

---

## 8. Anti-Patterns (Brand DNA Violations)

- All-blue decks (every scenario same accent color)
- Solid color product cards (must be white bg + accent top bar)
- Decorative illustrations (Danone is photography-driven)
- Fake data / hardcoded percentages (use "Data TBD" placeholders)
- Wrong cover format (must be solid `#005EB8` + white circle, not gradient hero)
- Gradient overlays on cover/closing
- Arial Narrow or generic system sans-serif for headlines
- Monotonous theme (every slide same theme class)
