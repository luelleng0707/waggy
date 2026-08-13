# WAGTOPIA_DESKTOP_STARTUP

## Purpose
Launch the CSTC-style native desktop presentation shell that calls the existing Wagtopia API/agent.

## Prerequisites
- Python 3.10+ environment
- Wagtopia API dependencies available (FastAPI stack for `app.api.main`)
- Desktop dependency for this shell:
  - `py -3 -m pip install PySide6`

## Start Wagtopia API
From repository root:

```bash
py -3 -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

## Start CSTC-style desktop shell
In a second terminal from repository root:

```bash
py -3 -m app.ui.cstc
```

## Connection defaults
- Base URL: `http://127.0.0.1:8000`
- API key: `wagtopia-demo-key`

Override with env vars if desired:
- `WAGTOPIA_API_BASE_URL`
- `WAGTOPIA_API_KEY`

## Runtime boundary
- Transport: HTTP API calls
- Computation owner: existing Wagtopia API + `PPIEWellnessAgent`
- UI role: presentation only (no scientific/math/package recomputation)

## One-click local suite
Run all local demo surfaces (API + customer web UI + developer web UI + CSTC desktop):

```bash
py -3 scripts/run_wagtopia_local.py
```
