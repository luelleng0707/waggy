# UI Standardization Report

**Date:** 2026-07-18  
**Scope:** Frontend visual consistency only. No PPIE engine, API contracts, or calculation changes.

## Design system

New file: `theme.css`

| Token | Value |
|-------|--------|
| `--bg-1` → `--bg-3` | `#F7F2F5` → `#F2E9EF` → `#EFE5EB` |
| `--accent` | `#B3266A` (single accent) |
| `--surface` | `#FFFFFF` |
| `--radius` | `24px` |
| `--radius-media` | `18px` |
| `--shadow` | `0 10px 35px rgba(0,0,0,.08)` |
| `--page-max` / `--page-pad` | `430px` / `20px` |
| `--space-1`…`--space-5` | `8 / 16 / 24 / 32 / 40` |
| `--media-h` | `140px` |
| `--duration` / `--ease` | `200ms` / `ease-out` |

Legacy aliases (`--primary`, `--brown`, `--cream`, …) map to the new tokens so older class names keep working.

## CSS files modified

| File | Change |
|------|--------|
| `theme.css` | **Created** — global design tokens |
| `styles.css` | Rewritten against tokens — unified cards, type, spacing, calendar, products, buttons |
| `app/ui/templates/base/app_styles.css` | Streamlit journey tokens/surfaces aligned |
| `app/api/main.py` | Static serve for `/theme.css` only (no API contract change) |

## Components / markup updated

| File | Change |
|------|--------|
| `index.html` | Loads `theme.css` + `styles.css`; calendar wrapped in `.calendar-card`; soft header; image `onerror` fallbacks |
| `app.js` | Unified `productCardHTML` (image, title, category, price, reason, CTA); `safeImg` for report photos |
| `catalog-service.js` | Empty/`onerror` → letter placeholder (no broken-image icons) |

## Screenshot checklist

Verified live at `http://127.0.0.1:8000/`:

| Check | Status |
|-------|--------|
| Consistent subtle background (`#F7F2F5`…`#EFE5EB`) | Pass |
| Consistent 8pt spacing + 20px page padding | Pass |
| White cards, 24px radius, shared shadow | Pass (`13` card surfaces) |
| Typography: heading 700 / section 600 / body 400 / caption 500 | Pass |
| No broken images | Pass (`brokenImgs: 0`) |
| Unified accent `#B3266A` (buttons, calendar active, highlights) | Pass |
| Calendar in card, accent session days | Pass |
| Product cards share one layout | Pass |
| Mobile shell max-width 430px, no Shop chrome | Pass |

Computed tokens sampled: `--accent: #b3266a`, `--radius: 24px`, `--shadow: 0 10px 35px rgba(0,0,0,.08)`.

## Unchanged (by design)

- PPIE engine / CSV formulas / analysis math  
- `/api/v1/catalog`, `/api/v1/analyze`, `/api/v1/store` payloads  
- Navigation / journey workflow  
- Catalog-backed product resolution  

## How to review

Hard-refresh `http://127.0.0.1:8000/` (cache-busted `?v=ui-1` on CSS/JS).
