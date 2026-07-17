# Wagtopia PPIE

Portable Pet Intelligence Engine — **Python is the sole production runtime**.

## Quick start

```bash
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Demo UI: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (static `index.html`)

Streamlit demo: `.\run_demo.ps1` or `./run_demo.sh`

## Production API

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| GET | `/health` | none | Engine status |
| POST | `/api/v1/analyze` | `x-api-key` | Full wellness envelope (canonical) |
| POST | `/api/v2/wellness/evaluate` | none | Same pipeline; Python profile schema |
| POST | `/api/recommendations` | `x-api-key` | Legacy mapped response |
| GET | `/api/v1/evidence/{condition}` | `x-api-key` | Condition evidence |
| GET | `/api/v1/products/{condition}` | `x-api-key` | Product matches |
| GET | `/api/breeds` | none | Breed name search |
| POST | `/api/v1/groomer/update` | `x-api-key` | Session observations |
| GET | `/api/v1/groomer/session/{petId}` | `x-api-key` | Session read |

Default API keys: `wagtopia-demo-key`, `ppie-dev-key` (override with `API_KEYS`).

## Regression

Golden fixtures live under `tests/parity/<profile>/golden_response.json`.

```bash
py -3 tools/parity_suite.py --repeat 3
```

Refresh goldens only for intentional algorithm changes:

```bash
py -3 tools/parity_suite.py --freeze
```

## Documentation

- [docs/PPIE_ALGORITHM.md](docs/PPIE_ALGORITHM.md)
- [docs/PPIE_CSV_MAP.md](docs/PPIE_CSV_MAP.md)
- [docs/PPIE_RESPONSE_SCHEMA.md](docs/PPIE_RESPONSE_SCHEMA.md)
- [docs/PPIE_IMPORT_AUDIT.md](docs/PPIE_IMPORT_AUDIT.md)
- [docs/PPIE_MIGRATION_REPORT.md](docs/PPIE_MIGRATION_REPORT.md)

## Data

CSV matrices under `data/` — see `docs/PPIE_CSV_MAP.md`.
