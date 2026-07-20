# Frontend Data Integration Report

**Date:** 2026-07-18  
**Scope:** Frontend + store API only (PPIE calculation logic untouched)

## Principle

`data/` is the single source of truth. The UI is a pure renderer of:

- `GET /api/v1/store` — joined catalog/pricing/components/feeding/extensions  
- `POST /api/v1/analyze` — package/plan IDs and costs  

Every product card resolves `product_id` → `CatalogService.get(id)`.

## Architecture

```
CSV (PRODUCT_*, EXT_*)
  ↓
DataPlatform / DataRepository
  ↓
GET /api/v1/store (+ /api/v1/catalog subset)
POST /api/v1/analyze
  ↓
catalog-service.js (CatalogService)
  ↓
app.js screens (Shop, Packages, Plans, Grooming products, Recommendations, Modal)
```

## New / updated files

| File | Role |
|------|------|
| `catalog-service.js` | Load/cache/lookup/search/format from `/api/v1/store` |
| `app.js` | Pure renderer; no mock product arrays |
| `app/api/main.py` | `/api/v1/store`, `/api/v1/store/{id}`, serves `catalog-service.js` |
| `app/data/repository.py` | `store_api_rows()` joins all product tables |
| `index.html` | `#packages-root`, `#plans-root`, product modal |
| `styles.css` | Modal + package product rows |

## Screen migration

| Screen | Data source |
|--------|-------------|
| Shop | `CatalogService` ← `/api/v1/store` |
| Care packages | `analyze.wellnessPackages` + `packageDetails` IDs → catalog lookup |
| Monthly / yearly plans | `analyze.monthly_plan` / `yearly_plan` → resolve name/id → catalog + feeding |
| Grooming “products used” | Session holds **only** `productIds[]`; names/prices/images from catalog |
| Recommended for Dolly | Analysis product IDs grouped by catalog `category` |
| Product detail modal | Full store record: components, feeding rules, supplement/bakery, price, image |

## Acceptance checklist

| Criterion | Status |
|-----------|--------|
| No mock product arrays | **Pass** (`recCategories` / `productsUsed` objects removed) |
| No hardcoded product names | **Pass** |
| No hardcoded prices | **Pass** (¥ from `PRODUCT_PRICING`) |
| No hardcoded product images | **Pass** (`image_url` or placeholder) |
| Cards resolve from `product_id` | **Pass** |
| Bundles = analysis + catalog | **Pass** |
| Feeding from `PRODUCT_FEEDING_RULES` | **Pass** (e.g. FF002_BEEF → `340g/day` at 30 kg) |
| Ingredients from `PRODUCT_COMPONENTS` | **Pass** (modal lists components) |
| CSV edit + refresh updates UI | **Pass** (store + visibility reload) |

## Remaining non-product demo content

Intentionally kept (not product catalog data):

- Grooming session narrative (dates, groomer notes, problem/result copy)
- Unsplash dog photo pools for before/after grooming photos
- Static wellness copy in `index.html` (trait text not tied to packages)
- Favorite treats blurb in profile (narrative; not shop SKUs)

Grooming sessions reference catalog IDs only (`SP014`, `TR003`, …) — display always comes from the store.

## `/api/v1/store` payload (per product)

Includes: catalog fields, `list_price_rmb`, `components[]`, `feeding_rules[]`, `feeding_for_weight`, `supplement`, `bakery`, `functions[]`.

Example verified: `FF002_BEEF` → 5 components, feeding `340g/day` for 20–35 kg.

## How to run

```bash
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` — packages, plans, shop, recommendations, and modal all bind live.
