# SECURITY_PRESENTATION_AUDIT

## Authentication boundary

- Customer surface (`/`) is intentionally public.
- Business surface (`/business`) is optionally protected by `WAGTOPIA_BUSINESS_ACCESS_KEY`.
- Developer surface (`/developer`) is optionally protected by `WAGTOPIA_DEVELOPER_ACCESS_KEY`.
- Developer debug APIs additionally require debug mode (`PPIE_DEBUG=true` or `?debug=1`).

## Public routes

- `GET /`
- `GET /health`
- `GET /favicon.ico`
- Static assets required by customer/business/developer pages.

## Protected routes (when env keys are set)

- `GET /business`
- `GET /developer`
- `GET /debug/calculation` (compatibility endpoint)
- `POST /api/v1/presentation/three-surfaces` (business gate)
- `POST /api/v1/ppie/validation-console*` and `GET /api/v1/ppie/debug/*` (developer gate + debug gate)

## Secrets and environment variables

### Server-only configuration

- `API_KEYS` (optional API key enforcement)
- `WAGTOPIA_BUSINESS_ACCESS_KEY`
- `WAGTOPIA_DEVELOPER_ACCESS_KEY`
- `PPIE_DEBUG` / `DEBUG_ENGINE`

### Client-visible configuration

- Optional runtime-injected `window.WagtopiaAPI.API_KEY` / `window.WAGTOPIA_API_KEY` values.
- No hardcoded default key fallback is embedded in JS.

## Changes made in Ω9.7A

- Removed hardcoded fallback credentials from:
  - `legacy/app.js`
  - `legacy/business.js`
  - `legacy/catalog-service.js`
  - `legacy/ppie-validation-console.js`
- Removed backend default API key seed from `app/api/main.py`.
- Removed launcher defaults that embedded `wagtopia-demo-key` from:
  - `scripts/run_wagtopia_local.py`
  - `scripts/run_wagtopia_remote.py`
- Added cookie handoff for surface access keys on `/business`, `/developer`, and `/debug/calculation` to avoid exposing keys in page JavaScript.

## Remaining risks

- Surface access key can still be provided via query parameter (`?access_key=`) for compatibility; this is functional but lower security than headers/cookies.
- CORS remains permissive (`allow_origins=["*"]`) and should be tightened before true public production if cross-origin usage is not required.
- Optional API key mode means deployments without `API_KEYS` are intentionally open for same-origin public demo traffic.
