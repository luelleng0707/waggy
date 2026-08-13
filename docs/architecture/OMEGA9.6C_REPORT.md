# OMEGA9.6C_REPORT

## 1) Concepts audited
- DogProfile
- EvidenceGraph
- FormulaRegistry
- WarehouseInterface
- Validation
- Trace

## 2) Canonical candidates
- DogProfile -> `repository/models/runtime.py` (domain) with app DTO boundary retained.
- EvidenceGraph -> `repository/models/runtime.py` + `repository/pipeline/biological_runtime.py`.
- FormulaRegistry -> `repository/formulas/`.
- WarehouseInterface -> `repository/warehouse/warehouse_interface.py`.
- Validation -> separated by purpose; no single collapse target.
- Trace -> layered typed contracts (runtime/formula/execution/optimization + app debug adapters).

## 3) Confirmed contracts
- `DOGPROFILE_CONTRACT.md`
- `EVIDENCEGRAPH_CONTRACT.md`
- `FORMULA_REGISTRY_CANONICAL_CONTRACT.md`
- `WAREHOUSE_INTERFACE_CANONICAL_CONTRACT.md`
- `VALIDATION_CANONICAL_BOUNDARY.md`
- `TRACE_CANONICAL_CONTRACT.md`

## 4) Unresolved differences
- DogProfile: app has `breed_split_pct`, `gender`, `height_cm`, `bcs` not present in repository domain model.
- EvidenceGraph: app evidence bundle summaries differ from repository provenance graph shape.
- FormulaRegistry: app metadata registries and repository runtime registry use different identity spaces and scopes.
- Warehouse access: app-side direct CSV readers still active.
- Trace: app narrative traces and repository deterministic traces differ in granularity.

## 5) Adapters required
- See `ADAPTER_REQUIREMENTS.csv`.
- Required for DogProfile, EvidenceGraph, FormulaRegistry, WarehouseInterface, Trace.

## 6) Migration readiness
- See `MIGRATION_READINESS_9.6C.csv`.
- READY_FOR_MIGRATION: FormulaRegistry.
- READY_WITH_ADAPTER: DogProfile, EvidenceGraph, Trace.
- NOT_READY: WarehouseInterface, Validation.

## 7) High-risk dependencies
- Warehouse access coupling in app data loaders.
- Trace schema divergence across app and repository domains.
- Formula metadata namespace mismatch between app registries and repository runtime configuration.

## 8) Traceability findings
- Repository already supports deterministic formula and execution traces with provenance rows/citations.
- App debug traces remain useful but not equivalent to full provenance traces.

## 9) Validation boundary findings
- Validation systems are semantically distinct and should not be collapsed by name.
- Warehouse QA, formula validation, and runtime graph validation serve different guarantees.

## 10) Warehouse access findings
- Canonical warehouse interface is active in repository runtime.
- Known direct-read exceptions remain in app data loaders and `repository/validation/runtime.py`.

## 11) Formula registry findings
- Repository formula runtime resolution is deterministic and explicit-error on missing formula/version.
- No MAT formula behavior changes were introduced in O9.6C.

## 12) Regression results
- `pytest tests/architecture -q` -> 28 passed
- `pytest tests/mathematics -q` -> 13 passed
- `pytest tests/formulas -q` -> 3 passed
- `pytest tests/math_debugger -q` -> 20 passed
- `pytest tests/optimization -q` -> 6 passed
- `pytest tests/science_graph -q` -> 6 passed
- `pytest tests/warehouse_qa -q` -> 6 passed

## 13) Known warehouse blockers
- `py -3 scripts/validate_warehouse.py` remains FAIL with known 8 broken references in `mechanisms.condition_mechanisms` and `mechanisms.food_mechanisms`.
- No repair attempted in this phase.

## 14) Recommended next phase
- O9.6D should be limited to adapter implementation planning/prototyping and non-cutover compatibility harnesses.
- Do not execute runtime cutover until DogProfile/EvidenceGraph/Trace/WarehouseInterface adapter proofs are complete.

## Evidence status markers
- **AUDITED**: implementation inventory and dependency mapping in `OMEGA9.6C_VERIFICATION.csv`.
- **PROVEN**: contract tests under `tests/architecture/` passing.
- **INFERRED**: migration risk/readiness classification based on static + runtime contract evidence.
- **RECOMMENDED**: canonical ownership and adapter strategy for future phases.
