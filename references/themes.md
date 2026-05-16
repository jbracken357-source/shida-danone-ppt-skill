# Theme Presets — Danone PPT Skill

> **Source of truth**: All color values are defined in `../templates/tokens.css`.
> This file references tokens.css — do NOT hardcode values here that differ from it.

## Brand Core

| Token | Value | Variable |
|-------|-------|----------|
| Brand primary | `#005EB8` | `--dn-blue` |
| Brand mid | `#0068CC` | `--dn-blue-mid` |
| Brand dark | `#002677` | `--dn-blue-dark` |
| Brand light | `#CCDFF1` | `--dn-tint` |
| Soft bg | `#F4F8FC` | `--dn-soft` |
| Text primary | `#262627` | `--dn-text` |
| Text secondary | `rgba(0,0,0,0.6)` | `--dn-text-secondary` |
| Border | `rgba(0,0,0,0.15)` | `--dn-border` |

## Category Themes

| Category | Accent | Soft | Dark | Trigger Keywords |
|----------|--------|------|------|-----------------|
| **Corporate** (default) | `#005EB8` | `#F4F8FC` | `#002677` | corporate, default |
| **Gut/Natural** | `#00A651` | `#E6F7EF` | `#007A3D` | gut, 肠道, digest, microbiome, natural |
| **Sport/Physical** | `#F26522` | `#FEF0E8` | `#C44A14` | sport, physical, 运动, recovery, hydration |
| **Clinical/Baby** | `#E6007E` | `#FCE6F2` | `#B30063` | clinical, tube, medical, 管饲, 康复, baby |
| **Water/Hydration** | `#00B2A9` | `#E6F8F7` | `#008A82` | water, hydration, 水, 汗液 |

## Font Stack

| Role | Font | Fallback | Variable |
|------|------|----------|----------|
| Display / Headlines | Playfair Display | Georgia, serif | `--dn-font-display` |
| Body | Inter | Noto Sans SC, Microsoft YaHei, sans-serif | `--dn-font` |
| Mono / Data | IBM Plex Mono | SF Mono, Consolas, monospace | `--dn-font-mono` |
| Chinese | Noto Sans SC | PingFang SC, Microsoft YaHei | included in `--dn-font` |

Load via Google Fonts CDN:
```
https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap
```

## Cover / Closing Format

### Opening Slide
```
solid #005EB8 background
  └── large white circle (600px, centered)
        ├── subtitle (18px, var(--dn-text), above title)
        ├── title (48px, Playfair Display, #005EB8, inside circle)
        └── logo area (bottom of circle)
              ├── "DANONE" (28px, 800 weight, letter-spacing 4px)
              └── "ONE PLANET. ONE HEALTH" (11px, teal, letter-spacing 2px)
```

### Closing Slide
```
solid #005EB8 background
  └── large white circle (600px, centered)
        ├── "THANK YOU" (56px, Playfair Display, #005EB8, inside circle)
        ├── optional subtitle (20px, #005EB8, below title)
        └── logo area (same as cover)
```

## Anti-Patterns

- **All-blue decks**: Different scenarios must use different theme colors
- **Solid product cards**: Always white bg + accent top bar, never solid color blocks
- **Decorative illustrations**: Danone is photography-driven, no icons/clipart as decoration
- **Fake data**: Never hardcode percentages — use real input or "Data TBD"
- **Wrong cover format**: Must use Opening Slide Title format, not generic gradient hero
- **Gradient overlays on cover/closing**: Solid `#005EB8` only
