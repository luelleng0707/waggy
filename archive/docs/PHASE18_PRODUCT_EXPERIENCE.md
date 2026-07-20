# Phase 18 — Premium Product Experience

**Status:** Complete (UI only)  
**Scope:** Presentation, information hierarchy, interaction design  
**Locked:** Clinical formulas, ClinicalAssessment schemas, API contracts, CSV, repository

## Product philosophy

Replace “generated report → cards → dropdowns” with:

**Dog profile → Clinical dashboard → Explore → Understand → Decide → Purchase → Maintain**

The module reads as an embedded Wagtopia clinical feature, not a standalone report app.

## Information hierarchy

| Level | Purpose | Pattern | Content |
|-------|---------|---------|---------|
| **1** | Immediate answers | Always visible | Snapshot, Today’s plan, Top 3 health priorities, Nutrition summary, Recommended package, Breed blurb, Activity |
| **2** | Understanding (“why?”) | Bottom sheets | Health / Nutrition / Activity / Environment / Behavior / Breed analysis |
| **3** | Decision support | Dedicated pages | Care package, Product detail |

Disclosure rules:

- Short → show inline  
- Medium → bottom sheet or light inline expand  
- Dense → sheet  
- Only **Package** and **Product** are full pages  

## UI architecture

| File | Role |
|------|------|
| `ppie-ui.js` | Reusable: section headers, stat cards, risk cards, package cards, product cards, evidence blocks, progress bars, coverage charts, plan rows, explore tiles |
| `ppie-shell.js` | Dashboard + package/product pages + Level-2 sheet content |
| `ppie-sheets.js` | Sheet host / stack (unchanged interaction chrome) |
| `styles.css` (`.px-*`) | Visual hierarchy: typography, spacing, elevation — not uniform white cards |

Lazy render: package/product HTML and sheet bodies are built only when opened.

## Data mapping (assessment → UI)

Uses existing ClinicalAssessment fields only:

- Snapshot ← `profile`, `health.summary_score`, `health.priorities[0]`, `confidence`, `meta.generated_at`
- Care plan ← recommended package `products` + `activity.daily_exercise`
- Priorities ← `health.priorities` + `validation.items` (benchmark when present)
- Nutrition bars ← `health.coverage.dimensions` (+ nutrient pills from `nutrition.targets`)
- Package page coverage bars ← same `health.coverage.dimensions` (dog-level preventative coverage)
- Breed lines ← `breed.descriptors` (energy, coat, function, weakness)
- Evidence ← `evidence.items`, matched to topics via `supports[]` or quote/title text overlap (presentation association only)

## Missing fields (not invented)

Documented gaps — **do not compute in JavaScript**:

| Desired UI | Missing / incomplete on ClinicalAssessment |
|------------|-----------------------------------------------|
| Dog photo | No `profile.photo_url` (or equivalent) |
| Risk **severity** label | Only `probability_pct` + optional `confidence` |
| Distinct morning vs evening meals | Only product servings; no `meal_guidance` schedule — UI shows a single meal row |
| Treat **allowance** (kcal/count) | Treat products exist; no allowance field |
| Water reminder (clinical) | Not in assessment — omitted from UI |
| Nutrition calories / protein goals | Not on `nutrition` module (`coverage_pct` often null) |
| Package-specific dimension matrix | `packages.*.detail.coverage` is nutrient rows (often zeroed); per-goal bars used from `health.coverage.dimensions` instead |
| Annual **savings** (clinical / vs market) | Only tier `yearly_cost` values; UI may compare two exposed costs, not invent savings |
| Package “Best for” tagline | Not a dedicated field (uses `summary` / recommended flag) |
| Evidence ↔ condition links | `evidence.supports` often empty; UI falls back to text overlap |
| Product “suitable dogs” / estimated active dose | Sparse on `products.by_id.analysis` |
| Published benchmarks | `validation.published_benchmark_pct` usually `null` / status `unavailable` |

When these are needed for a polished experience, extend **ClinicalAssessment** in a future contract phase — not the frontend.

## Verification

- [x] No clinical formulas / API / CSV / assessment schema changes  
- [x] Homepage Level-1 answers without opening expandables  
- [x] Package / product = dedicated pages; analysis = sheets  
- [x] Evidence embedded next to health priorities  
- [x] Engine IDs only under optional Technical reasoning  
- [x] No footer app navigation  
- [x] Existing Python tests still pass (presentation-only change)
