# OMEGA9.6G_REPORT

## Scope

Execution provenance and formula parity hardening for developer debugger only.

No scientific runtime migration, no app->repository cutover, no customer-surface debug exposure.

## Implemented

- Added canonical execution-record projection fields in `app.debug.clinical_execution_debug`:
  - `execution_id`
  - `source_location` + `source_validation`
  - `documentation_status`
  - `warehouse_status`
  - `evidence_status`
  - `execution_status` matrix
  - `scientific_support_status`
  - `publication_status`
- Added explicit non-synthetic missing states:
  - `FORMULA DOCUMENTATION MISSING`
  - `SOURCE_NOT_AVAILABLE`
  - `WAREHOUSE ROW: NOT AVAILABLE`
  - `EVIDENCE: NOT AVAILABLE FOR THIS EXECUTION`
  - `REPLAY: NOT IMPLEMENTED FOR THIS FORMULA`
  - `SENSITIVITY: NOT IMPLEMENTED FOR THIS FORMULA`
- Added read-only execution detail endpoint:
  - `GET /api/v1/ppie/validation-console/execution/{execution_id}?debug=1`
  - serves cached provenance from latest validation-console run
  - does not recalculate formulas
- Updated developer UI `legacy/ppie-validation-console.js`:
  - execution status section
  - source location + bounded code excerpt
  - explicit warehouse/evidence/replay/sensitivity/publication state presentation
- Added docs:
  - `docs/architecture/FORMULA_EXECUTION_PARITY.csv`
  - `docs/architecture/EXECUTION_PROVENANCE_ARCHITECTURE.md`
  - `docs/mathematics/EXECUTION_FORMULA_MAP.md`

## Current honest runtime state (Dolly)

- Formula cards shown: runtime execution projections only (`formula_executions` + stage-derived execution records)
- Replay on V2 app runtime formulas: not implemented
- Sensitivity on V2 app runtime formulas: not implemented
- Row-level warehouse IDs: only when emitted by runtime lookups; otherwise explicitly unavailable
- Scientific evidence links: execution-dependent; unavailable states explicitly shown

## Production safety

- No production formula logic changed.
- Developer projection/read-only endpoints only.

## Files changed in Ω9.6G

- `app/debug/clinical_execution_debug.py`
- `app/api/main.py`
- `legacy/ppie-validation-console.js`
- `tests/interface/test_debug_calculation_runtime.py`
- `docs/architecture/FORMULA_EXECUTION_PARITY.csv`
- `docs/architecture/EXECUTION_PROVENANCE_ARCHITECTURE.md`
- `docs/mathematics/EXECUTION_FORMULA_MAP.md`

## Remaining gaps (explicit)

- Formal equations for many V2 app formulas are not documented in runtime payload.
- V2 replay capability contract exists as status fields but not implemented with deterministic re-executor.
- V2 sensitivity capability remains not implemented.
- Warehouse row-level IDs depend on runtime lookup emission.
- Evidence links/quotes depend on actual serialized evidence for each execution path.
