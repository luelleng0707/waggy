# Release Audit — Phase 18

**Date:** 2026-07-20  
**Scope:** Release cleanup & CTO handoff  
**Constraint:** No deterministic formula changes · No intentional API contract changes · No runtime behavior changes beyond removing unused static assets

---

## Summary

The repository was cleaned for Wagtopia engineering handoff: obsolete development docs and dead frontend assets were archived, the README was rewritten as an SDK-style entry point, and CTO documentation was reduced to the Phase 17 integration set plus deployment/release notes.

---

## Files removed / archived

### Documentation → `archive/docs/`

Phase diaries, migration/parity journey notes, frontend/shop/UI audits, formula reference (`PPIE_ALGORITHM.md`), CSV map / data platform internals, response schema draft, clinical report V3/V4 transition notes, root `FRONTEND_LAYOUT_SPEC.md`, `PYTHON_AGENT.md`.

### Frontend → `archive/frontend/`

| Item | Reason |
|------|--------|
| `clinical-report.js` | Not loaded by live demo shell |
| `care-recommendation.js` | Not loaded by live demo shell |
| Unused Jinja components | Not referenced by Streamlit journey |

### Other → `archive/`

| Item | Reason |
|------|--------|
| `data_csv/`, `data_csv.zip` | Duplicate scratch of `data/` |
| `prisma/` | Unreferenced schema sketch |
| `tools/import_audit_scan.py` | One-off migration audit |
| `tests/parity/**/js_response.json` | Legacy Node parity artifacts |

### API static routes removed

- `GET /clinical-report.js`
- `GET /care-recommendation.js`

### Demo JS cleanup (`app.js`)

Removed unused `renderWellnessInsights`, `renderPackages`, `renderPlans` (DOM roots no longer exist). Boot path unchanged: catalog load → clinical-report → `PpieShell.mount`.

---

## Dead code removed (runtime-safe)

- Orphan static JS routes and files (above)
- Dead demo render helpers (above)
- Orphan Jinja components archived

**Not removed (still wired):**

- `app/data/clinical_report_builder.py` (still returned on clinical-report)
- Streamlit `app/ui/**` journey path + tests
- Optional API surfaces (groomer, evidence, recommendations, breeds)

---

## Remaining documentation (ship)

| Path | Role |
|------|------|
| `README.md` | Overview, quick start, layout, integration |
| `docs/INDEX.md` | Doc index |
| `docs/PPIE_ENGINE_SPEC.md` | Architecture |
| `docs/PPIE_API_CONTRACT.md` | DogProfile / ClinicalAssessment |
| `docs/PPIE_LAYER_OWNERSHIP.md` | Ownership boundaries |
| `docs/PPIE_DATA_PROVIDER_SPEC.md` | Data providers |
| `docs/PPIE_VERSIONING_POLICY.md` | Version axes |
| `docs/PPIE_VALIDATION_SPEC.md` | Evidence / validation |
| `docs/DEPLOYMENT.md` | Env & run |
| `docs/RELEASE_AUDIT.md` | This file |
| `data/README.md` | CSV provider layout (business data) |
| `archive/` | Historical only |

Public docs describe **capabilities and contracts**, not proprietary equations. Detailed formula notes live under `archive/docs/PPIE_ALGORITHM.md` for internal algorithm owners only.

---

## Remaining runtime modules

| Area | Path |
|------|------|
| API | `app/api/main.py`, `payload_adapter.py`, `evidence.py` |
| Engine | `app/agent/**` |
| Data | `app/data/**`, `data/**` |
| Demo UI | `index.html`, `app.js`, `ppie-shell.js`, `ppie-sheets.js`, `report-renderer.js`, `catalog-service.js`, `theme.css`, `styles.css` |
| Optional Streamlit | `app/ui/**`, `run_demo.*` |
| Regression | `tests/`, `tools/parity_suite.py` |

---

## Confirmations

| Check | Status |
|-------|--------|
| No Layer A formula edits | Confirmed |
| No intentional API contract changes | Confirmed (only unused static routes removed) |
| Demo boot still uses `/api/v1/clinical-report` + store | Confirmed |
| CTO docs only in `docs/` (plus README / data README) | Confirmed |
| Historical material under `archive/` | Confirmed |

---

## Suggested next engineering steps (out of Phase 18 scope)

1. Typed `ClinicalAssessment` model + single assess endpoint  
2. Deprecate dual analyze/clinical-report megadicts  
3. Optional: drop Streamlit if FastAPI demo is the sole UI  
4. Commit currently untracked demo assets (`ppie-*.js`, `theme.css`, etc.) if not yet on remote
