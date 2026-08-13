# RAILWAY_PREFLIGHT

Pre-deployment checklist for Ω9.7A hardening. This is a preflight document only; no deployment is performed in this phase.

- [x] startup command
- [x] `$PORT` compatibility
- [x] dependency installation
- [x] static assets
- [x] API routes
- [x] customer route
- [x] business route
- [x] developer route
- [x] health route
- [x] environment variables
- [x] secret handling
- [x] no localhost references in served HTML
- [x] no hardcoded credentials
- [x] no scientific runtime changes

## Startup mechanism

- `Procfile`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `railway.json`: `deploy.startCommand` matches the same command.
- `nixpacks.toml`: `[start].cmd` matches the same command.

## Process model

- Single FastAPI service process.
- Three surfaces (`/`, `/business`, `/developer`) are routes on the same backend.
- No multi-service or multi-port deployment topology required.

## Environment keys

- Optional API key enforcement: `API_KEYS`
- Optional business gate: `WAGTOPIA_BUSINESS_ACCESS_KEY`
- Optional developer gate: `WAGTOPIA_DEVELOPER_ACCESS_KEY`
- Debug controls: `PPIE_DEBUG` / `DEBUG_ENGINE`

## Scope guardrails

- No changes made to `repository/mathematics`, `repository/formulas`, `repository/optimization`, or warehouse scientific datasets as part of Ω9.7A.
