# Python PPIE Agent

Canonical runtime for Wagtopia PPIE.

## Layout

```
app/
  main.py                 # FastAPI shim → app.api.main
  api/main.py             # Production HTTP API (port 8000)
  agent/                  # Deterministic pipeline + response assembly
  ui/                     # Streamlit demo
data/                     # CSV knowledge base
tools/parity_suite.py     # Golden regression suite
docs/                     # Algorithm, CSV map, response schema
```

## Run API

```bash
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Health: http://127.0.0.1:8000/health
- Analyze: `POST /api/v1/analyze` with header `x-api-key: wagtopia-demo-key`
- Evaluate: `POST /api/v2/wellness/evaluate`

## Run Streamlit UI

```bash
./run_demo.sh
# or
./run_demo.ps1
```

- API: http://localhost:8000
- UI: http://localhost:8501

## Example analyze body (Node-compatible)

```json
{
  "name": "Dolly",
  "pet_name": "Dolly",
  "breeds": ["Golden Retriever", "Labrador Retriever"],
  "birthday": "2021-03-15",
  "weight": 30,
  "sex": "Female",
  "activity_level": "High",
  "current_environment": "Shanghai Summer",
  "observed_conditions": []
}
```

JavaScript engine paths (`src/engine`, `server.js`) are retired. See `docs/PPIE_MIGRATION_REPORT.md`.
