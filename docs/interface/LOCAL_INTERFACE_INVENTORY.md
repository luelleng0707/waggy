# LOCAL_INTERFACE_INVENTORY

## Interface table

| Interface | Type | Purpose | URL / Launch | Runtime Owner | Exposure |
|---|---|---|---|---|---|
| Customer UI | Browser (static shell + API proxy) | Primary interview/demo flow for dog profile, analysis, evidence, package, and economics | `http://127.0.0.1:8080/` via `py -3 scripts/run_wagtopia_local.py` or `py -3 scripts/run_wagtopia_remote.py` | `legacy/*` presentation + `app.api.main` backend | PUBLIC/REMOTE (through remote tunnel), LOCAL when no tunnel |
| Business UI | Browser executive dashboard | Portfolio/opportunity/economics view from runtime-backed payloads | `http://127.0.0.1:8080/business` | `legacy/business.html` + `app.presentation.adapter` | LOCAL by default; optionally access-key protected |
| Developer UI (Calculation Explorer) | Browser debug UI | Full formula/evidence/trace inspection | `http://127.0.0.1:8080/developer` | `legacy/debug/calculation.html` + `/api/v1/ppie/*` | LOCAL by default; optionally access-key protected |
| CSTC Desktop Shell | Native desktop (PySide6) | Operator/business-facing navigation and presentation | `py -3 -m app.ui.cstc` | `app/ui/cstc/*` + `app.api.main` | LOCAL ONLY |
| API Service | FastAPI | Application transport layer for all interfaces | `http://127.0.0.1:8000/` (`uvicorn app.api.main:app`) | `app.main -> app.api.main -> app.agent.engine.PPIEWellnessAgent` | LOCAL ONLY |
| Health endpoint | HTTP endpoint | Runtime health and launch readiness checks | `http://127.0.0.1:8000/health` and proxied `http://127.0.0.1:8080/health` | `app.api.main` | LOCAL ONLY |
| Remote customer tunnel | HTTPS tunnel to gateway | Remote tester access to customer presentation surface only | Runtime-generated `https://*.ngrok-free.app/` from `py -3 scripts/run_wagtopia_remote.py` | `scripts/run_wagtopia_remote.py` customer gateway | PUBLIC/REMOTE |

## Runtime ownership notes

- Production/deployed runtime path remains app-owned:
  - `frontend/static -> gateway -> app.main/app.api.main -> app.agent.engine.PPIEWellnessAgent`
- Repository v2 remains parallel/test-focused in this phase.
- Remote launcher keeps API port `8000` local-only and exposes only gateway `8080`.
- Developer execution-provenance endpoint: `/api/v1/ppie/validation-console/execution/{execution_id}?debug=1` (read-only, local debug only).
- Shared three-surface projection endpoint: `/api/v1/presentation/three-surfaces` (single analysis -> customer/business/developer projections).
