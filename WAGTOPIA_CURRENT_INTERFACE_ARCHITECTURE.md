# WAGTOPIA_CURRENT_INTERFACE_ARCHITECTURE

## Current entrypoint proof
- Deploy/start commands:
  - `Procfile`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - `railway.json`: same `startCommand`
- `app/main.py` re-exports `app` from `app.api.main`.

## Current runtime path (verified)
frontend/static or API client
-> `app.main`
-> `app.api.main` (FastAPI app)
-> `PPIEWellnessAgent` global singleton
-> `AssessmentAgent` + `FormulaGraph`
-> `app.agent.nodes.*`
-> `app.formulas.stages.*` + `app.data.repository`
-> warehouse-backed CSV views/loaders

## Current UI
- API-served static legacy assets conditionally from repo root (`app/api/main.py` routes)
- Streamlit UI path (`app/ui/demo_app.py`) runs agent in-process

## Current API
- Primary analysis routes:
  - `/api/v1/analyze`
  - `/api/v1/clinical-report`
  - `/api/v1/ppie/assess`
  - `/api/v2/wellness/evaluate`
- Product/store/evidence/graph/debug routes also present.

## Current agent
- Public callable boundary: `PPIEWellnessAgent.generate_reproducible_report(profile)`.
- Input model: `DogProfileInput` (`app/agent/state.py`) + payload adapter from legacy request formats.

## Current state model
- Request-scoped execution context in agent graph.
- Process-global API agent singleton.
- Lightweight in-memory groomer sessions in API module.

## Current domain models
- App transport/input models: `app/agent/state.py`.
- Parallel repository domain models: `repository/models/runtime.py`.

## Current scientific pipeline
- Production path: app formula graph + stage functions under `app/formulas/stages/*`.
- Repository scientific pipeline exists in parallel (`repository/pipeline`, `repository/reasoning`, `repository/mathematics`) mainly test/tooling-facing.

## Current optimization pipeline
- Production optimization lives in `app/formulas/stages/optimization.py` and app package assembly modules.
- Repository optimization runtime exists (`repository/optimization/runtime.py`) but is not current production owner.

## Current trace pipeline
- App runtime traces: `execution_trace`, `lookup_trace`, pipeline/calculation traces, debug engine trace payload.
- Repository typed trace stack exists in parallel (`repository/models/trace.py`, `repository/math_debugger/*`, optimization trace models).

## Current data access
- App data access facade: `app/data/repository.py` (+ loader/native loader).
- Canonical repository warehouse interface also exists: `repository/warehouse/warehouse_interface.py`.

## Current frontend->backend path
- API clients call FastAPI endpoints; Streamlit path can invoke agent directly in process.
