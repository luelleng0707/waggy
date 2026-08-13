# RAILWAY_INTERFACE_GUIDE

## Purpose

Deploy one Wagtopia backend service with three browser presentation surfaces.

## Routes

- Customer URL: `https://<deployment>/`
- Business URL: `https://<deployment>/business`
- Developer URL: `https://<deployment>/developer`
- API URL: `https://<deployment>/api/v1/analyze`
- Health URL: `https://<deployment>/health`

Replace `<deployment>` with your Railway domain.

## Start command

`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Local start commands

- API-only dev: `py -3 scripts/run_dev.py`
- Local multi-interface suite: `py -3 scripts/run_wagtopia_local.py`

## Authentication controls

Optional environment-key gates:

- `WAGTOPIA_BUSINESS_ACCESS_KEY`
- `WAGTOPIA_DEVELOPER_ACCESS_KEY`

When set, supply value via:

- HTTP header: `x-wagtopia-access-key`
- or query parameter: `?access_key=<value>`

Developer debug APIs also enforce `PPIE_DEBUG`/`?debug=1` semantics plus optional developer access key.

## Demo profile

Default demo input:

- `Dolly`
- mixed breed (`Golden Retriever` x `Labrador Retriever`)

Synthetic profiles are demo inputs only and must not be treated as scientific evidence.

## Surface purpose

- Customer (`/`): personalized wellness recommendations and package view
- Business (`/business`): portfolio/opportunity/economics view (runtime-backed metrics only)
- Developer (`/developer`): full execution provenance/audit explorer

## Safety and honesty rules

- No synthetic scientific citations
- No synthetic warehouse row provenance
- No synthetic replay/sensitivity outputs
- Missing runtime fields must display `NOT AVAILABLE` / `NOT DOCUMENTED` / `NOT IMPLEMENTED`

## Deployment verification checklist

Verify after deploy:

1. `GET /` returns customer UI
2. `GET /business` returns business UI
3. `GET /developer` returns developer UI
4. `GET /health` returns service status
5. `POST /api/v1/analyze` succeeds with demo profile
