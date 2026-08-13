# ACTIVE_RUNTIME_PATH

## Deployment and startup evidence
- `Procfile`: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `railway.json`: `startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `app/main.py`: backward-compatible shim exporting `app` from `app.api.main`
- `app/api/main.py`: active FastAPI app and endpoint definitions

## Current runtime path (proven)
1. HTTP request enters FastAPI app at `app.api.main:app`.
2. API handlers call `PPIEWellnessAgent` and app data/repository modules.
3. App debug/reporting paths consume app trace/evidence utilities.

## Repository runtime role
- `repository/pipeline` + `repository/mathematics` are active in tests, benchmarks, debugger tooling, and audit layers.
- They are not currently the deployment start command entrypoint.

## Canonical runtime ownership today
- Production web entrypoint owner: `app/`
- Scientific/mathematical audit and redesign owner: `repository/`

## Cutover implication
- Any app-to-repository runtime migration must preserve API contracts and replay hashes before changing start commands.
