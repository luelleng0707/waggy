# Shop Storefront Binding Report

**Date:** 2026-07-18  
**Scope:** Frontend + catalog API data binding only (PPIE engine untouched)

---

## Verdict

Shop is now a CSV-driven storefront.

```
PRODUCT_CATALOG.csv ⨝ PRODUCT_PRICING.csv
        ↓
GET /api/v1/catalog
        ↓
fetch(cache: 'no-store') + x-api-key
        ↓
shopProducts[] (in-memory state)
        ↓
category / subcategory filter (dynamic)
        ↓
search (name, brand, category, subcategory, tags, …)
        ↓
#product-grid cards
```

Browser verification at `http://127.0.0.1:8000/`: **18 cards** rendered matching **18 active CSV rows**.

---

## Step results

| Step | Result |
|------|--------|
| 1 Catalog API | **200**, count **18** = active `PRODUCT_CATALOG.csv` rows |
| 2 Hardcoded shop arrays | **None** in Shop path (`shopProducts` starts `[]`, filled by API) |
| 3 Pipeline | Documented above — all stages use live API data |
| 4 Card fields | From CSV/API: `product_id`, `brand`, `category`, `subcategory`, `product_name`, `status`, `image_url`, `purchase_url` |
| 5 Prices | From `PRODUCT_PRICING.csv` → `list_price_rmb` / `price_rmb` |
| 6 Images | Empty → letter placeholder; set `image_url` → `<img>` |
| 7 Categories | Dynamic from live `category` (+ human-readable `subcategory`) |
| 8 Search | Matches `product_name`, `brand`, `category`, `subcategory`, tags/descriptions |
| 9 Rename hot reload | API returned `Fresh Dog Food Single TEST` without server restart |
| 10 Add `SP999` | Appeared in catalog (count 19) without code changes |
| 11 Delete row | Product removed from catalog after hot reload |
| 12 Price edit | `FF001` showed `777` after `PRODUCT_PRICING.csv` change |
| 13 Image URL | Returned `https://example.com/ff001.jpg` after CSV edit |
| 14 Subcategory filter | `Functional Foods` present in API; UI adds filter chip when subcategory is not snake_case |

---

## Counts

| Metric | Value |
|--------|-------|
| Active CSV products | 18 |
| API products returned | 18 |
| Shop cards rendered | 18 |
| Dynamic category filters | All, All-Natural Treats, Fresh Food, Homestyle Bakery, Nutritional Supplements |

---

## Files involved

### Frontend
- `index.html` — Shop shell, `#product-grid`, `#shop-categories`, `#shop-search`
- `app.js` — `loadCatalog()` / `renderShop()` / filters / search
- `styles.css` — card + placeholder + brand styles

### API / data platform (no PPIE formulas)
- `app/api/main.py` — `GET /api/v1/catalog`
- `app/data/repository.py` — `catalog_api_rows()` (pass-through catalog columns + pricing join)
- `app/data/validators.py` — FK orphans → **warnings** (so catalog add/delete can hot-reload)
- `app/data/watcher.py` — CSV hot reload
- `data/product_portfolio/PRODUCT_CATALOG.csv` — expanded optional storefront columns
- `data/product_portfolio/PRODUCT_PRICING.csv` — prices

### Streamlit (also catalog-driven)
- `app/ui/renderer/shop.py` — builds shop VMs from catalog DF
- `app/ui/templates/components/shop_section.html`

---

## Hardcoded values remaining (non-Shop)

| Location | What | Shop impact |
|----------|------|-------------|
| `app.js` grooming `sessions[].productsUsed` | Demo grooming narrative products | **None** — not Shop |
| `app.js` `recCategories` | “Recommended for Dolly” mock carousels | **None** — not Shop |
| `app.js` Unsplash pools | Grooming before/after photos | **None** — not Shop |

Shop itself has **no** hardcoded product names, prices, categories, or image URLs.

---

## Missing / empty fields (expected)

Most catalog rows have empty `image_url` / `purchase_url` → placeholders until CSV filled.  
Optional columns now present for progressive enrichment:

`description`, `short_description`, `featured`, `tags`, `display_order`, `inventory_status`, `rating`, `review_count`

These pass through `/api/v1/catalog` automatically when populated.

---

## Hot reload

| Check | Status |
|-------|--------|
| Watcher running | Yes (FastAPI startup) |
| Edit name → API updates | Yes (~1s debounce) |
| Browser refresh / tab focus → UI updates | Yes (`visibilitychange` re-fetches) |
| FK orphan no longer blocks reload | Yes (warn-only) |

---

## How to verify locally

1. `py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
2. Open `http://127.0.0.1:8000/` → scroll to **Wagtopia Shop**
3. DevTools → Network → `GET /api/v1/catalog` → 200, 18 products
4. Edit `PRODUCT_CATALOG.csv` → save → wait 1s → refresh (or refocus tab)

---

*PPIE calculations / recommendation logic were not modified.*
