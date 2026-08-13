# EXECUTION_PROVENANCE_ARCHITECTURE

## Purpose

Define the developer-only provenance projection for `Ω9.6G` without changing scientific runtime behavior.

The projection must answer:

1. What exact computation executed
2. Where it executed in code
3. Which inputs/parameters/outputs were used
4. Which warehouse/evidence links are available
5. Whether replay/sensitivity/scientific/publication states are available

## Pipeline

`USER INPUT -> APPLICATION EXECUTION -> EXECUTION TRACE -> FORMULA PROVENANCE -> CODE PROVENANCE -> WAREHOUSE PROVENANCE -> EVIDENCE PROVENANCE -> REPLAY/SENSITIVITY -> PRESENTATION`

## Canonical Distinctions

- Execution `!=` Documentation
- Execution `!=` Replay
- Execution `!=` Scientific validation
- Execution `!=` Publication readiness

Each execution record carries independent statuses for:

- `executed`
- `source_located`
- `formula_documented`
- `parameterized`
- `warehouse_traced`
- `evidence_traced`
- `replayable`
- `sensitivity_analyzable`
- `scientifically_validated`
- `publication_status`

## Runtime Components

- Producer: `app.api.main` (`/api/v1/ppie/validation-console`)
- Projection owner: `app.debug.clinical_execution_debug`
- Developer UI: `legacy/ppie-validation-console.js`
- Execution detail endpoint (read-only projection):
  - `GET /api/v1/ppie/validation-console/execution/{execution_id}?debug=1`

No second calculation engine is introduced. Provenance endpoint serves records already produced by the most recent validation-console run.

## Missing-data policy

When runtime does not provide data, projection must emit explicit unavailable states:

- `FORMULA DOCUMENTATION MISSING`
- `SOURCE_NOT_AVAILABLE`
- `WAREHOUSE ROW: NOT AVAILABLE`
- `EVIDENCE: NOT AVAILABLE FOR THIS EXECUTION`
- `REPLAY: NOT IMPLEMENTED FOR THIS FORMULA`
- `SENSITIVITY: NOT IMPLEMENTED FOR THIS FORMULA`
- `PUBLICATION: NOT ASSESSED`

No synthetic citations, row IDs, equations, replay outputs, or sensitivity outputs are allowed.
