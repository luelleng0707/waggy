# PPIE documentation

Living docs for the current backend. No phase diaries here — history is in git and `archive/docs/`.

| Document | Owns |
|----------|------|
| [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) | Pipeline, stages, modules, ownership |
| [FORMULAS.md](FORMULAS.md) | Every formula ID, modifiers, scores, confidence |
| [DATA.md](DATA.md) | CSV layout, manifest, philosophy (current) |
| [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md) | Target normalized archive (planning) |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Column dictionary (current) |
| [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md) | Migration plan (not executed) |
| [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md) | Column-level audit ADR |
| [API.md](API.md) | Endpoints, auth, payloads, versioning |
| [DEBUGGING.md](DEBUGGING.md) | Validation Console, EngineTrace, debug gates |
| [ROADMAP.md](ROADMAP.md) | Future work only |
| [CHANGELOG.md](CHANGELOG.md) | Chronological record |

**Maintenance:** Update the matching living document when code changes. Do not add feature diary markdown. Prefer fewer docs. Exception: approved architecture decision records that will replace a living doc after migration (e.g. data redesign).

---

## What PPIE is

Portable Pet Intelligence Engine — deterministic clinical intelligence for Wagtopia.

```
DogProfile  →  PPIE Engine  →  ClinicalAssessment  →  Wagtopia UI
```

| Layer | Owner | Policy |
|-------|--------|--------|
| **A — Clinical engine** | PPIE | Versioned; golden/parity tested |
| **B — Clinical wording** | PPIE / content | Copy only; never numbers |
| **C — Experience** | Wagtopia | Fully replaceable |
| **Business data** | Wagtopia | Catalog, pricing, dog profiles |

Preferred contract: **`POST /api/v1/ppie/assess`**. Details in [API.md](API.md).

The frontend in this repo is a **demo**, not the product.

---

## Quick start

```bash
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/health | Readiness + versions + CSV hash |
| http://127.0.0.1:8000/ | Demo UI |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/debug/calculation?debug=1 | Validation Console |

Default API key: `wagtopia-demo-key` (header `x-api-key`). Override with `API_KEYS`.

Optional Streamlit: `.\run_demo.ps1` / `./run_demo.sh`.

Env: `API_KEYS`, `PORT`, `PPIE_DATA_DIR`, `PPIE_DEBUG`.

---

## Repository layout

```
app/agent/       Layer A — clinical stages + optimizer
app/inference/   Pure formula helpers + FORMULA_REGISTRY
app/data/        Repository, loaders, assessment, debug console
app/api/         FastAPI routes
data/            Scientific + catalog CSVs (manifest.yaml)
tests/           Golden + parity + console tests
docs/            These eight documents
archive/         Historical material (not required to run)
```

**Edit freely:** commercial CSVs under `data/product_portfolio/` (prices, SKUs) in your ops process.  
**Do not edit casually:** `app/agent/**` clinical math — requires algorithm bump + goldens.

---

## Data vs code

`data/` is a **scientific archive**, not a config dump. Algorithms, weights, and heuristics live in Python. See [DATA.md](DATA.md).
