# DEPENDENCY REPORT

## Scope
- Runtime foundation paths scanned: `repository/`, `config/`, `scripts/`, `tests/{warehouse,engine,api,pipeline}`.
- Legacy paths archived under `legacy/` were excluded from runtime dependency decisions.

## Python Imports Detected (Runtime Foundation)
- `__future__`
- `ast`
- `config`
- `dataclasses`
- `explainability`
- `functools`
- `interfaces`
- `models`
- `orchestrator`
- `os`
- `pandas`
- `pathlib`
- `repository`
- `runtime`
- `settings`
- `stage_order`
- `sys`
- `time`
- `trace`
- `typing`
- `uuid`
- `warehouse_interface`

## requirements.txt Changes
- Kept:
  - `pandas` (referenced by runtime foundation code or tests)
  - `pytest` (referenced by runtime foundation code or tests)
  - `pytest_asyncio` (referenced by runtime foundation code or tests)
- Removed (zero runtime usage in v2 foundation scan):
  - `fastapi`
  - `uvicorn`
  - `pydantic`
  - `httpx`
  - `streamlit`
  - `jinja2`
  - `PyYAML`
  - `watchdog`

## npm / package.json
- No external npm dependencies declared.
- Scripts updated to architecture-only actions (`validate:warehouse`, `test:architecture`).

## Obsolete Script Cleanup
- Removed parity/demo script wiring from `package.json` because those commands pointed to legacy runtime paths.

## Notes
- This report is static-analysis based for the v2 runtime foundation.
- If legacy modules are reactivated, dependency requirements must be re-evaluated before release.
