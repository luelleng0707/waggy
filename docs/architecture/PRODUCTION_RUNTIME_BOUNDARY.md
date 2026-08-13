# PRODUCTION_RUNTIME_BOUNDARY

## What runs in production today

### Request path: `POST /api/v1/analyze`

1. `app.main:app` re-exports `app.api.main:app`.
2. `app.api.main.analyze_v1` receives request.
3. `require_api_key` gate is applied (optional depending on `API_KEYS` configuration).
4. `profile_from_analyze_body(...)` converts request body into `DogProfileInput`.
5. `PPIEWellnessAgent.generate_reproducible_report(...)` executes:
   - `AssessmentAgent.assess(...)`
   - `FormulaGraph.execute(...)`
   - app agent nodes (`profile`, `breed`, `biology`, `risk`, `nutrition`, `ingredient`, `product`, `package`, `assessment`, `report`, `validation`, `trace`, `export`)
6. `AssessmentResult.to_analyze_dict()` returns analyze payload.
7. API returns JSON to caller.

### Request path: `POST /api/v1/presentation/three-surfaces`

1. `app.api.main.presentation_three_surfaces` receives request.
2. Optional business access gate (`WAGTOPIA_BUSINESS_ACCESS_KEY`).
3. Same profile normalization + `PPIEWellnessAgent.generate_reproducible_report(...)`.
4. `build_clinical_assessment(...)` projects assessment modules.
5. If `?debug=1`, debug gate + `build_validation_console(...)`.
6. `build_three_surface_presentations(...)` creates customer/business/developer payloads with:
   - `analysis_signature`
   - `presentation_correlation_id`

## What is production-active vs parallel

### Production-active runtime

- `app/api/*`
- `app/agent/*`
- `app/data/*`
- `app/presentation/*`
- `legacy/*` (browser assets served by FastAPI routes)

### Parallel / test / debug infrastructure

- `repository/pipeline/*`
- `repository/reasoning/*`
- `repository/mathematics/*`
- `repository/formulas/*`
- `repository/mechanisms/*`
- `repository/objectives/*`
- `repository/sources/*`
- `repository/optimization/*`
- `repository/science_graph/*`
- `repository/math_debugger/*` (used by debug/audit features, not core customer runtime path)
- `repository/benchmarks/*`
- `repository/warehouse_qa/*`
- `repository/validation/*`

## Which repository components are actually executed in production requests

- Core customer runtime: **none of the repository Ω4-Ω9 engines are direct owners** for `/api/v1/analyze`.
- Debug/audit route enrichment may call `repository/math_debugger/*` through `app/debug/clinical_execution_debug.py` when debug is enabled.
- `scripts/validate_warehouse.py` executes `repository/warehouse.WarehouseInterface` outside production request handling.

## Components that exist but are not connected to production request path

- `repository/engine/*` (skeleton/planned)
- `repository/pipeline/*` orchestrator path
- repository formula runtime and mathematical runtime chain
- repository optimization runtime chain

## Conclusion

Production currently runs on **app runtime path** with one FastAPI process and one analysis execution path.
Repository runtime remains parallel and validated by tests and audit tooling, pending explicit cutover work.
