# Standardized Clinical Report Architecture (Schema v4)

**Date:** 2026-07-20  
**Principle:** Backend emits structured JSON only. Frontend is a pure widget renderer. No HTML from the API. No clinical business logic in the browser.

## Data flow

```
CSV
 ↓
Repository (app/data/repository.py)
 ↓
PPIE Calculation Engine (app/agent/** — frozen math)
 ↓
Report Generator (app/data/report_generator.py)
 ↓
Standard JSON (schema 4.0.0)
 ↓
Frontend Renderer (report-renderer.js)
```

Nothing bypasses this path for clinical report pages.

## Report envelope

Every report includes:

| Field | Purpose |
|-------|---------|
| `schema_version` | Widget/section contract (`4.0.0`) |
| `algorithm_version` | PPIE algorithm label |
| `data_version` | Manifest / platform version |
| `csv_hash` | Reproducibility fingerprint of loaded CSVs |
| `generated_at` | UTC ISO timestamp |
| `navigation` | Section ids + titles for sticky nav |
| `sections[]` | Ordered clinical chapters |
| `package_reports{}` | Nested reports keyed by tier (`essential` / `balanced` / `optimal`) |
| `product_reports{}` | Nested reports keyed by product id |

## Section contract

Every section:

```json
{
  "id": "breed_analysis",
  "title": "Breed Analysis",
  "priority": 20,
  "summary": "...",
  "score": { "value": 82, "label": "...", "unit": "%" },
  "widgets": [],
  "references": []
}
```

Canonical section ids:

1. `summary`
2. `breed_analysis`
3. `trait_analysis`
4. `environment_analysis`
5. `risk_analysis`
6. `nutrition_analysis`
7. `activity_analysis`
8. `package_analysis`
9. `grooming_analysis`
10. `scientific_references`

## Widget types

Frontend understands only these types (see `app/data/report_schema.py`):

`text` · `metric` · `metrics` · `accordion` · `progress` · `timeline` · `comparison` · `chart` · `warning` · `package` · `product` · `risk` · `activity` · `trait` · `list` · `chips` · `ledger` · `evidence` · `trace` · `nav`

The renderer switches on `type` only — no page-specific layouts.

## API

```http
POST /api/v1/clinical-report
x-api-key: wagtopia-demo-key
```

Response:

```json
{
  "analyze": { "... frozen PPIE envelope ..." },
  "report": { "... schema v4 standard report ..." },
  "clinicalReport": { "... legacy V3 for transitional clients ..." }
}
```

Use **`report`** for all new UI. `clinicalReport` remains until V3 consumers are removed.

## Frontend

| File | Role |
|------|------|
| `report-renderer.js` | Pure widget loop + package/product overlays |
| `app.js` | Boots `/api/v1/clinical-report`, mounts `StandardReportRenderer` |
| `clinical-report.js` | Legacy V3 renderer (fallback only) |
| `care-recommendation.js` | Legacy care pages (fallback only) |

Routes:

- `#/care/{tier}` → `report.package_reports[tier]`
- `#/product/{id}` → `report.product_reports[id]`

## Citation rules

- Published rows require `source_url` from CSV
- Missing URL → `status: "placeholder"` with label **Placeholder — No paper linked yet.**
- Never invent DOIs, PubMed IDs, or quotes

## Editing content without UI code

Update CSV under `data/` → repository hot-reload → refresh browser. Titles, summaries, products, package names, evidence, and traces all come from the generator.

## Tests

```bash
py -3 -m pytest tests/test_standard_report.py tests/test_clinical_report.py -q
```
