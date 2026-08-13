# Waggy v2 Foundation

Canonical direction:

`warehouse -> repository/engine -> repository/api -> repository/frontend`

## What exists in Ω1

- Immutable canonical warehouse at `warehouse/`
- Warehouse interface and validation in `repository/warehouse/`
- Engine skeleton packages in `repository/engine/`
- v2 architecture docs in `docs/`
- Validation script at `scripts/validate_warehouse.py`

## Validate Warehouse

```bash
py -3 scripts/validate_warehouse.py
```

Validation output:

- `docs/validation_report.md`

## Read first

1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. [docs/WAREHOUSE_GUIDE.md](docs/WAREHOUSE_GUIDE.md)
3. [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)

## Note on legacy code

Pre-v2 runtime and UI assets have been archived under `legacy/` during Ω1.1 cutover. Any remaining non-`repository/` runtime modules should be treated as transitional until migrated.
