# FORMULA_EXECUTION_ARCHITECTURE

## Scope

This architecture links:

- `repository/formulas/`
- `repository/mathematics/`
- `repository/math_debugger/`
- `docs/mathematics/*`

without changing scientific formulas in this phase.

## Canonical formula lifecycle

1. **Formula definition**: ID, version, metadata (`warehouse/formulas/*.csv`, `repository/formulas/*`)
2. **Parameter/coefficient loading**: deterministic resolver and registry (`repository/formulas/runtime.py`)
3. **Runtime execution**:
   - Parallel mathematical runtime: `repository/mathematics/runtime.py`
   - Production app runtime currently uses app formula execution path (`app/agent/*`)
4. **Intermediate values / output**:
   - Typed traces in repository math models and debugger models
   - App debug output in validation console
5. **Replay**: `repository/math_debugger/replay.py`, `independent_replay.py`
6. **Sensitivity**: `repository/math_debugger/sensitivity.py`
7. **Publication/methodology status**: `docs/architecture/FORMULA_STATUS.csv`, `docs/mathematics/*`

## MAT formula status (preserved from Ω9.5)

- `MAT-1001 = REVISE`
- `MAT-1002 = REPLACE`
- `MAT-1003 = REPLACE`
- `MAT-1004 = KEEP`
- `MAT-1005 = REVISE`
- `MAT-1006 = REPLACE`
- `MAT-1007 = REPLACE`
- `MAT-1008 = REPLACE`

These statuses are **not** changed here.

## Runtime boundary

- Repository formula/mathematics runtime is presently parallel/test/audit infrastructure.
- Production request path uses app-layer formula execution and exposes debug provenance through `app.debug.clinical_execution_debug`.

## Trace contract requirements

Each formula execution should retain (where available):

- formula ID + version
- source location
- equation / substituted equation status
- inputs/parameters/intermediate values/output
- warehouse/evidence references
- replay and sensitivity status
- publication risk classification
