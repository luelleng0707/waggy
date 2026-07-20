# PPIE Clinical Report V3 (legacy)

> **Superseded for new UI by [CLINICAL_REPORT_V4.md](./CLINICAL_REPORT_V4.md)** (schema `4.0.0` standard sections/widgets). V3 remains available as `clinicalReport` on the same endpoint for transitional clients.

**Date:** 2026-07-20  
**Principle:** Transparent explanation layer — no PPIE math changes, no fabricated citations.

## Architecture

```
CSV explanation tables
        ↓
DataRepository (load/join)
        ↓
ClinicalReportBuilder ← frozen POST /api/v1/analyze output
        ↓
POST /api/v1/clinical-report  →  { analyze, clinicalReport }
        ↓
clinical-report.js (14 section renderers)
```

PPIE still calculates. The builder **only explains** deterministic outputs using CSV-backed text, citations, and trace nodes.

## New CSV tables

| File | Sections |
|------|----------|
| `TRAIT_ATTRIBUTE_EXPLANATIONS.csv` | S1 Biological profile cards |
| `TRAIT_PURPOSES.csv` (populated) | S2 Advantages |
| `TRAIT_CONTRIBUTION_WEIGHTS.csv` | S5 Contribution tree |
| `CLINICAL_RISK_TIMELINE.csv` | S6 Age progression |
| `ACTIVITY_PRESCRIPTION_RULES.csv` | S10 Activity prescription |
| `GROOMING_OBSERVATION_DEFS.csv` | S12 Grooming intelligence |
| `ENVIRONMENTAL_MATRICES.csv` (populated) | S4 Environment |
| `CLINICAL_EVIDENCE_BASE.csv` (populated) | S7, S13 citations |
| `NUTRIENT_PRIORITIES.csv` (populated) | S8 context |

Existing tables also used: `BREEDS.csv`, `BREED_CONDITIONS.csv`, `TRAIT_INTERACTIONS.csv`, `PRODUCT_COMPONENTS.csv`, PPIE `calculationTrace`, `wellnessPackages`, `nutritionalTargets`.

## API

```http
POST /api/v1/clinical-report
x-api-key: wagtopia-demo-key
Content-Type: application/json

{ same body as /api/v1/analyze }
```

Response:

```json
{
  "analyze": { "...existing PPIE envelope..." },
  "clinicalReport": {
    "version": "3.0.0",
    "sections": [ { "id": "s1", "title": "...", ... }, ... s14 ]
  }
}
```

## Frontend

- `clinical-report.js` — renders all 14 sections
- `app.js` — boot calls `/api/v1/clinical-report` once (analyze + explain)
- `#wellness-insights-root` — clinical report container

## Citation rules

- Published rows require `source_url` in CSV
- Missing URL → **"Awaiting evidence entry"** (never fabricated DOI)
- `EVD-GEN-001` in `CLINICAL_EVIDENCE_BASE.csv` is an explicit placeholder row

## Editing content without code

Update any explanation CSV → hot reload → refresh browser. No Python/JS changes required for copy, evidence links, or trait descriptions.

## Tests

```bash
py -3 -m pytest tests/test_clinical_report.py -q
```

## Not changed

- PPIE engine stages (risk ranking, nutrition dosing, optimization)
- `/api/v1/analyze` response schema (unchanged; clinical-report wraps it)
- Product selection algorithms
