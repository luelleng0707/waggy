# APP_REPOSITORY_CUTOVER

## Current runtime

Production startup path is currently app-centric:

frontend/static clients
    ->
`uvicorn app.main:app`
    ->
`app.main` (shim)
    ->
`app.api.main`
    ->
`app.agent.engine.PPIEWellnessAgent`
    ->
`app.data.repository` / app data loaders

Repository runtime path exists in parallel:

`repository.pipeline.orchestrator` + `repository.mathematics.runtime`

but is primarily exercised via tests/debugger/benchmarks and not the deployment start command.

## app responsibilities
- FastAPI runtime entrypoints and API contract (`app/api/main.py`).
- PPIE agent orchestration and response assembly (`app/agent/*`).
- App-level formula metadata registries (`app/agent/formula_registry.py`, `app/inference/formula_registry.py`).
- Legacy-compatible trace/report presentation models.
- App data platform access wrappers.

## repository responsibilities
- Canonical domain runtime models (`repository/models/*`).
- Biological pipeline orchestration (`repository/pipeline/*`).
- Omega 9 mathematics (`repository/mathematics/*`).
- Formula-as-data runtime (`repository/formulas/*`).
- Math debugger/replay/provenance (`repository/math_debugger/*`).
- Warehouse interface and QA (`repository/warehouse/*`, `repository/warehouse_qa/*`).

## overlap

| concept | app implementation | repository implementation | app consumers | repository consumers | behavioral differences | data differences | canonical candidate | migration requirement | risk |
|---|---|---|---|---|---|---|---|---|---|
| DogProfile | `app/agent/state.py::DogProfileInput` | `repository/models/runtime.py::DogProfile` | `app.api.main`, agent nodes | pipeline, mathematics tests | app model is API-facing Pydantic payload, repository model is immutable runtime dataclass | field names and optionality differ | `repository/models/runtime.py` for internal domain, `app/agent/state.py` for API DTO | add explicit adapter boundary; avoid dual-domain logic | MEDIUM |
| EvidenceGraph | app evidence/trace nodes (`app/agent/nodes/evidence_node.py`) | `repository/models/runtime.py::EvidenceGraph` | app trace/validation flows | pipeline/mathematics/runtime/debugger | app treats evidence as report payload fragments; repository uses structured graph contract | schema divergence | `repository/models/runtime.py` | map app evidence outputs to repository graph contract if cutover | HIGH |
| FormulaRegistry | `app/agent/formula_registry.py`, `app/inference/formula_registry.py` | `repository/mathematics/formulas.py`, `repository/formulas/*` | app debug/trace/formula graph | mathematics runtime, tests, debugger | app registries are metadata-rich and mixed historical scope; repository registries are runtime-formula and formula-as-data separated | ID namespaces differ (`PROFILE_*` vs `MAT-*`) | KEEP_BOTH_TEMPORARILY with canonical production math registry in repository | explicit namespace policy and de-dup docs | HIGH |
| WarehouseInterface | app uses app-native loaders/repository wrappers | `repository/warehouse/warehouse_interface.py` | app runtime and debug panels | pipeline, formulas, benchmarks, QA | app path can bypass canonical WarehouseInterface | app path includes transitional CSV platform layer | `repository/warehouse/warehouse_interface.py` | enforce adapter usage in future cutover phase | HIGH |
| Validation | app validation node/debug console | repository validation + warehouse QA + tests | app API debug tooling | data QA, formula QA, test suites | app validation focuses clinical/debug payloads; repository validation focuses data/integrity/formula | differing severity and scope | keep both with explicit taxonomy | classify systems by responsibility before merges | MEDIUM |
| Trace | `app/agent/calculation_trace.py` and debug traces | `repository/models/trace.py` + `repository/math_debugger/*` | app debug/reporting | orchestrator/mathematics debugger/tests | app trace is clinical narrative/legacy parity; repository trace is deterministic runtime+formula provenance | structure and granularity differ | keep both temporarily, consolidate contracts not classes | define trace hierarchy contract first | HIGH |
