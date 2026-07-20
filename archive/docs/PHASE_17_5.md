# Phase 17.5 — ClinicalAssessment & report flow

**Status:** Complete  
**Goal:** Finish architectural separation (engine vs presentation) and redesign interaction for mobile-first progressive disclosure.

## Backend

- `app/data/clinical_assessment.py` — projects frozen `analyze` → modular `ClinicalAssessment` (no formula recompute)
- Modules: profile, breed, traits, behavior, environment, health, nutrition, activity, grooming, packages, products, evidence, validation, confidence
- `POST /api/v1/ppie/assess` — preferred contract; `?module=` for independent fetch/cache
- `POST /api/v1/clinical-report` — also returns `assessment` for the demo shell (single pipeline run)

## UI

- Home hierarchy always visible: snapshot → today’s plan → health → nutrition → package → breed → activity → expandable extras
- Packages / products = dedicated in-module detail pages
- Health detail = bottom sheet; technical reasoning only when expanded in the sheet
- No uniform “everything is a dropdown”

## Tests

- `tests/test_clinical_assessment.py`
