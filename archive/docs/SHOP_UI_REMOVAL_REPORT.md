# Shop UI Removal Report

**Date:** 2026-07-18  
**Scope:** Frontend Shop surfaces only. Catalog APIs, data platform, and PPIE engine unchanged.

## Decision

Standalone storefront removed from the product experience.  
Catalog + `/api/v1/catalog` + `/api/v1/store` + `CatalogService` remain so packages, plans, recommendations, and product detail modals keep resolving live CSV data. An e-commerce UI can be reattached later without rebuilding the data layer.

## Files deleted

| File | Role removed |
|------|----------------|
| `app/ui/renderer/shop.py` | Streamlit Shop view-model builder |
| `app/ui/templates/components/shop_section.html` | Journey Shop section |
| `app/ui/templates/shop/page.html` | Orphan Shop page template |

## Files modified

| File | Change |
|------|--------|
| `index.html` | Removed Wagtopia Shop section (sidebar, search, product grid) |
| `app.js` | Removed `renderShop`, category nav, search handlers; boot still loads catalog + analyze |
| `styles.css` | Removed Shop-only layout/grid/filter CSS; kept product placeholder as `.product-media-placeholder` for packages/modal |
| `catalog-service.js` | Placeholder class rename only (`product-media-placeholder`) |
| `app/ui/renderer/journey.py` | Dropped `ShopRenderer` / `shop_items` |
| `app/ui/renderer/__init__.py` | Stopped exporting `ShopRenderer` |
| `app/ui/templates/home/journey.html` | Removed shop section include |
| `app/ui/templates/components/macros.html` | Removed `shop_item` macro |
| `tests/test_ui_templates.py` | Dropped Shop template test; assert journey has no “Wagtopia Shop” |

## Routes / UI removed

- Static Shop section on `#page-home` (no separate Shop route existed)
- Streamlit journey Shop block
- Shop category sidebar, search, product browsing grid
- Shop-only CSS (`.shop-layout`, `.shop-sidebar`, `.cat-btn`, `.product-grid`, `.shop-product*`)

No Shop nav tab/button existed in the current shell (bottom nav already hidden).

## Components removed

- `ShopRenderer` / `ShopItemVM` / `ShopPageVM`
- `shop_section.html`
- `shop/page.html`
- `shop_item` Jinja macro
- `renderShop()` / shop filter/search JS

## CSS removed

Shop storefront rules listed above. Retained product-media styles used by package rows and the product detail modal.

## Remaining product-related UI

| Surface | Still uses catalog |
|---------|--------------------|
| Care packages | analyze IDs → `CatalogService` |
| Monthly / yearly plans | analyze + catalog + feeding rules |
| Grooming report product cards | session `productIds` → catalog |
| Recommended products | analysis IDs → catalog |
| Product detail modal | `/api/v1/store/{id}` |
| `CatalogService` | loads `/api/v1/store` for all of the above |

## Backend intact (verified)

| Endpoint | Result |
|----------|--------|
| `GET /health` | 200 |
| `GET /api/v1/catalog` | 200 (18 products) |
| `POST /api/v1/analyze` | 200 (3 wellness packages) |

Also unchanged: `data/`, data repository, CSV hot reload, `/api/v1/store`, PPIE agent stages, package/recommendation generation.

## Tests

`tests/test_ui_templates.py` — 6 passed.

## PPIE calculations

**Unchanged.** No edits under `app/agent/**`, no CSV formula changes, no analyze schema changes.
