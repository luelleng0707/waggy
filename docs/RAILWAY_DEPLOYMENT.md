# Railway Deployment — Wagtopia PPIE

Production FastAPI runtime for this repository. **No Node server.** Clinical engine, formulas, and API contracts are unchanged by this guide.

---

## 1. Repository layout (deployment-relevant)

```
waggy/
├── app/
│   ├── main.py              # uvicorn entry shim → exports `app`
│   ├── api/main.py          # FastAPI() application + routes + static demo UI
│   ├── agent/               # clinical engines (do not change for deploy)
│   ├── data/                # CSV repository / platform
│   └── …
├── data/                    # Scientific + product CSVs (required at runtime)
├── index.html, *.js, *.css  # Demo frontend (served by FastAPI)
├── debug/calculation.html   # Validation Console page
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway/Heroku-style process type
├── railway.json             # Railway start + healthcheck
└── .python-version          # Prefer Python 3.12 on Nixpacks
```

---

## 2. Entry point

| Item | Value |
|------|--------|
| Module | `app.main` |
| Object | `app` |
| Source | `app/main.py` re-exports `from app.api.main import app` |
| Definition | `app = FastAPI(...)` in `app/api/main.py` |

Verified by repo docs (`README.md`, `package.json` script `start`) and import:

```python
from app.main import app
```

---

## 3. Exact Railway Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Why this command is correct**

- `app.main:app` is the documented production ASGI target (`README.md`, `package.json`).
- `--host 0.0.0.0` binds all interfaces (required on Railway).
- `--port $PORT` uses Railway’s injected `PORT` (do not hard-code 8000).

Also declared in:

- `Procfile` → `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `railway.json` → `deploy.startCommand` (same)
- `nixpacks.toml` → `[start] cmd` (same) and **`providers = ["python"]`** so Nixpacks does not treat `package.json` as a Node app

---

## 4. Required environment variables

| Variable | Required on Railway? | Default in code | Purpose |
|----------|----------------------|-----------------|---------|
| `PORT` | **Yes** (set by Railway) | `8000` only if unset | HTTP listen port |
| `API_KEYS` | Recommended | `wagtopia-demo-key,ppie-dev-key` | Comma-separated keys for `x-api-key` |
| `PPIE_DATA_DIR` | No | `data` | CSV root; resolved against repo root if relative |
| `PPIE_DEBUG` | No | unset/false | Enables developer/debug routes |
| `DEBUG_ENGINE` | No | unset/false | Alias for engine debug |
| `PPIE_DEV_BOOT` | No | unset/false | Local banner / console soft-enable |
| `PPIE_OPEN_BROWSER` | No | `true` (local only) | Opens browser when local-dev boot; leave unset or `false` on Railway |

**Not used by the Python FastAPI app** (appear only in `.env.example` / legacy notes — do not treat as required):

- `DATABASE_URL`
- `ENGINE_LICENSE_KEY` / `ENGINE_LICENSE_EXPECTED`
- `CLIENT_SECRET` / `JWT_SECRET` / `ENCRYPTION_KEY`

---

## 5. Required files for a successful deploy

Must be present in the deployed tree:

- `requirements.txt`
- `app/main.py`, `app/api/main.py`
- `data/` including `data/manifest.yaml` and CSV files referenced by the manifest
- Demo static assets at repo root: `index.html`, `app.js`, `styles.css`, `theme.css`, etc. (mounted only if `index.html` exists)
- `Procfile` and/or `railway.json` (both provided)

---

## 6. Deployment steps

1. Push this repository to GitHub/GitLab (include `data/`, `Procfile`, `railway.json`).
2. In Railway: **New Project → Deploy from GitHub** → select this repo.
3. Confirm Start Command is:

   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

   (Railway should pick this up from `railway.json` / `Procfile`.)
4. Optional Variables:

   - `API_KEYS=wagtopia-demo-key,your-production-key`
   - `PPIE_OPEN_BROWSER=false` (recommended)
5. Deploy and wait for healthcheck on `/health`.
6. Open the public URL:

   - Frontend: `https://<service>.up.railway.app/`
   - Health: `https://<service>.up.railway.app/health`
   - API docs: `https://<service>.up.railway.app/docs`

---

## 7. Common deployment failures

| Symptom | Cause | Fix |
|---------|--------|-----|
| **No start command detected** | Missing Procfile / railway startCommand, or Nixpacks picked **Node** because of `package.json` | Ensure `nixpacks.toml` has `providers = ["python"]`; set Start Command manually if needed |
| App crashes on boot | `data/` missing from deploy | Ensure CSVs + `manifest.yaml` are committed / not ignored |
| 401 on API | Wrong/missing `x-api-key` | Send a key from `API_KEYS` |
| Wrong Python | Unsupported runtime | `.python-version` / `NIXPACKS_PYTHON_VERSION` pin `3.12` |
| Port bind errors | Hard-coded port | Always use `$PORT` |
| Static 404 | `index.html` not at repo root | Keep demo assets at repository root |
| `npm start` / `py -3` failures | Node provider selected | Force Python provider via `nixpacks.toml` |

---

## 8. Health endpoint

```
GET /health
```

Returns engine/data status (algorithm version, CSV hash when loaded). Used by `railway.json` `healthcheckPath`.

---

## 9. API endpoint (preferred)

```
POST /api/v1/ppie/assess
Header: x-api-key: <key from API_KEYS>
```

Also available: `POST /api/v1/analyze`, OpenAPI at `/docs`.

---

## 10. Frontend URL

```
GET /
```

Serves `index.html` from the repository root via FastAPI `FileResponse` routes (not a separate Node static server).

---

## Local parity check

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
curl http://127.0.0.1:8000/health
```
