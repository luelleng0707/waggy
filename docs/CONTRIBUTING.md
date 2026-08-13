# CONTRIBUTING.md

## Clinical safety

1. Do not change formula math without an algorithm version bump + golden/parity tests.  
2. Warehouse edits go through validation (`science_pipeline`) when possible.  
3. Prefer Repository accessors over ad-hoc CSV reads.

## Day-to-day

```bash
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
py -3 -m pytest -q
```

## Docs to read

`SYSTEM_ARCHITECTURE.md` → `RUNTIME_PIPELINE.md` → `DATA_PIPELINE.md` → `SCIENCE_MODEL.md` → `API_REFERENCE.md`

## Scientific authoring

```bash
py -3 -m authoring.pipeline
py -3 -m science_pipeline.release --skip-parity
```

Staging only — never auto-write live clinical tables.
