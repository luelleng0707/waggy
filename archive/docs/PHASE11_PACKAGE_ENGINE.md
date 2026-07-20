# Phase 11 — Data-Driven Clinical Package Engine + Standardized Reports

**Date:** 2026-07-20

## Pipeline

```
Canonical CSV (data/)
  → Data Repository
  → PPIE calculation engine (unchanged parity stages)
  → Package optimizer (app/agent/package_optimizer.py)
  → Standardized report objects (report_generator + report_models)
  → UI renderer (report-renderer.js)
```

## Package optimization

| Tier | Objective |
|------|-----------|
| Essential | Minimize yearly cost subject to required coverage / clinical function |
| Balanced | Maximize coverage, minimize surplus, reasonable cost (weighted score) |
| Optimal | Maximize clinical + functional + evidence; ignore cost |

Products come from **ACTIVE** `PRODUCT_CATALOG` joined to components, functions, feeding, pricing, and extension tables. Staple IDs come from `PACKAGE_TIERS.csv` only.

### Coverage math

```
coverage% = min(100, provided / target × 100)
Coverage Score = Σ min(provided_i / target_i, 1) / N
Overall = 0.35·Coverage + 0.25·Clinical + 0.20·Evidence
        + 0.15·CostEff + 0.05·Diversity − SurplusPenalty
```

When `active_ingredient` dose rows are absent, nutrient coverage is 0 and clinical function matching (from `PRODUCT_FUNCTIONS.csv`) drives selection — honest, not invented doses.

### 365-day plans

Yearly mass / packs computed first. **Monthly = yearly ÷ 12.**

## Report models

`app/data/report_models.py`: Breed, Risk, Nutrition, PackageComparison, PackageDetail, ProductAnalysis, ScientificEvidence, Activity, Grooming, AnnualPlan.

API `POST /api/v1/clinical-report` returns `report`, `reportModels`, `analyze`, `clinicalReport` (legacy).

## UI routes

- `#/packages/{tier}` — package detail report
- `#/products/{id}` — product detail report

## Success checks

- No hardcoded package product lists
- Adding an ACTIVE catalog row + joins makes it optimizer-eligible without Python edits
- Parity stages untouched
