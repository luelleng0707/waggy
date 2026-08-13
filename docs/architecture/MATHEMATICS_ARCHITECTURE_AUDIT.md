# MATHEMATICS_ARCHITECTURE_AUDIT

## CURRENT_IMPLEMENTATION
- Runtime formulas: `repository/mathematics/` (MAT-1001..MAT-1008).
- Formula-as-data loading/versioning: `repository/formulas/` with warehouse tables in `warehouse/formulas/`.
- Condition-level orchestration: `repository/mathematics/runtime.py`.

## AUDIT
- Debugger, replay, provenance, sensitivity tooling: `repository/math_debugger/`.
- Audit artifacts: `docs/mathematics/*` including O9.4/O9.5 documents and CSV manifests.

## PROPOSED_MODEL
- O9.5 replacement/revision recommendations live in:
  - `docs/mathematics/PROPOSED_ESTIMATION_MODEL.md`
  - `docs/mathematics/PROPOSED_FORMULA_REGISTRY.md`
- Current MAT formulas remain audited legacy/current implementations and are not final scientific architecture.

## DEVELOPER_TOOLING
- Deterministic replay and independent replay: `repository/math_debugger/replay.py`, `repository/math_debugger/independent_replay.py`.
- Constant and provenance audit: `repository/math_debugger/formula_validator.py`, `repository/math_debugger/numerical_inventory.py`.

## Provenance artifact preservation (canonical)
- `docs/mathematics/OMEGA9_CURRENT_MODEL.md`
- `docs/mathematics/MATHEMATICAL_DEPENDENCY_GRAPH.md`
- `docs/mathematics/MAT1002_PARAMETER_AUDIT.csv`
- `docs/mathematics/PROPOSED_ESTIMATION_MODEL.md`
- `docs/mathematics/ENVIRONMENT_MODEL_AUDIT.md`
- `docs/mathematics/MAT1007_DEPENDENCY_AUDIT.csv`
- `docs/mathematics/SCIENTIFIC_ENGINEERING_BOUNDARY.md`
- `docs/mathematics/WAREHOUSE_BLOCKERS.md`
- `docs/mathematics/PROPOSED_FORMULA_REGISTRY.md`
- `docs/mathematics/FORMULA_REGISTRY.csv`
- `docs/mathematics/FORMULA_DEPENDENCIES.csv`
- `docs/mathematics/FORMULA_REPLAY.csv`
- `docs/mathematics/MATHEMATICAL_AUDIT.md`

## Structural recommendation (audit only)
- Keep `mathematics`, `formulas`, and `math_debugger` as separate responsibilities but document them as one Mathematics domain family.
- Prevent accidental coupling of proposed-model docs with production runtime paths.
- Preserve O9.5 dispositions explicitly in architecture manifests.
