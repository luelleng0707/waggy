# OMEGA9.7_INTERFACE_ARCHITECTURE_AUDIT

## Current HTTP entrypoint

- Canonical app: `app.main:app` (shim) -> `app.api.main:app`
- Production start command in repo:
  - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health endpoint: `/health`

## Current API routing

- Core:
  - `POST /api/v1/analyze`
  - `POST /api/v1/clinical-report`
  - `POST /api/v1/ppie/assess`
- Debug/developer:
  - `POST /api/v1/ppie/validation-console`
  - `GET /api/v1/ppie/validation-console/execution/{execution_id}`
  - `POST /api/v1/ppie/trace`
  - `GET /api/v1/ppie/debug/*`
- Store/science/research graph endpoints remain available under `/api/v1/*`.

## Current static/customer/developer interfaces

- Customer page: `GET /` -> `legacy/index.html`
- Developer page (legacy path): `GET /debug/calculation` -> `legacy/debug/calculation.html`
- New Ω9.7 routes added:
  - `GET /business` -> `legacy/business.html`
  - `GET /developer` -> `legacy/debug/calculation.html`

## Current CSTC/PySide6 interface

- Local native shell only (`python -m app.ui.cstc`)
- Acts as presentation adapter over the same FastAPI backend
- Not required for Railway/browser deployment

## Runtime ownership

All surfaces consume the same canonical backend runtime (`PPIEWellnessAgent`).
No separate scientific runtime is created for business/customer/developer.

## Environment and startup compatibility

- Existing:
  - `API_KEYS`
  - `PPIE_DEBUG` / `DEBUG_ENGINE`
  - `PORT`
- Added Ω9.7 access controls:
  - `WAGTOPIA_BUSINESS_ACCESS_KEY` (optional hard gate for `/business`)
  - `WAGTOPIA_DEVELOPER_ACCESS_KEY` (optional hard gate for `/developer` + debug APIs)

## Railway compatibility status

- Present: `Procfile`, `railway.json`, `nixpacks.toml`
- Single-service deployment model is compatible with one FastAPI backend + three browser routes.
- No claim of live/public deployment in this phase.

## Key Ω9.7 gaps addressed in this phase

- Added explicit business and developer browser routes.
- Added shared three-surface projection endpoint over one analysis run:
  - `POST /api/v1/presentation/three-surfaces`
- Added developer/business optional access-key gates.
- Added dedicated route-level interface tests for `/`, `/business`, `/developer`, `/health`.
