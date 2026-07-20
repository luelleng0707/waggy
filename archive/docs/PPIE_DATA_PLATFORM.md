# PPIE Data Platform

Filesystem under `data/` is the canonical production database.

## Design rule

- The **algorithm** knows *how* to calculate.
- The **CSVs** define *what* it calculates.
- Adding breeds, products, ingredients, conditions, feeding rules, or evidence is a **data** operation.

## Package layout

| Module | Role |
|--------|------|
| `app/data/schemas.py` | Load `data/manifest.yaml` |
| `app/data/loader.py` | Read every declared CSV |
| `app/data/validators.py` | Required columns, PKs, FKs, empty checks |
| `app/data/cache.py` | `version`, `csv_hash`, `loaded_at`, `file_count` |
| `app/data/repository.py` | `DataPlatform` + engine-facing `DataRepository` |
| `app/data/runtime.py` | Process singleton + `reload_platform()` |
| `app/data/watcher.py` | Watchdog hot reload (no server restart) |

`app.agent.utils.DataRepository` re-exports the platform facade so existing engine imports keep working.

## Hot reload

On FastAPI startup, `start_data_watcher(DATA_DIR)` monitors `data/**/*.csv` and `manifest.yaml`.  
Edits trigger validate → rebuild indexes → swap the live platform.  
Refresh the browser to see Shop / analyze results from the new dataset.

## Health

`GET /health` includes:

```json
{
  "data_version": "2.1.0",
  "csv_hash": "...",
  "loaded_files": 39,
  "loaded_at": "..."
}
```

## Catalog API

`GET /api/v1/catalog` (requires `x-api-key`) returns active products joined with pricing — used by the static Shop UI. No frontend product arrays.
