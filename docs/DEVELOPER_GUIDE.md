# Developer Guide (Waggy v2 Foundation)

## Core Rules

1. Treat `warehouse/` as the single source of truth for facts.
2. Do not implement inference logic in warehouse interfaces.
3. Add reasoning only in `repository/engine/*`.
4. Access facts through `WarehouseInterface`, never direct CSV paths.
5. Keep dependency direction:
   - Warehouse -> Engine -> API -> Frontend

## Adding Data

1. Add or update canonical CSV rows under `warehouse/`.
2. If mapping is uncertain, add rows to a domain `*_NEEDS_VALIDATION.csv`.
3. Preserve source evidence fields.
4. Run validation:
   - `py -3 scripts/validate_warehouse.py`
5. Check generated report:
   - `docs/validation_report.md`

## Adding Engine Capabilities

1. Pick domain package under `repository/engine/`.
2. Expand `interfaces.py` contract first.
3. Add immutable models in `models.py`.
4. Implement deterministic behavior in `service.py`.
5. Add tests under `tests/engine/`.

## Adding API Endpoints

1. Keep endpoints in API layer only.
2. No direct warehouse imports in route handlers.
3. Call engine services and return explicit schemas.
4. Add tests under `tests/api/`.

## Validation Expectations

Validation should detect:
- duplicate IDs
- missing required IDs
- broken references
- missing evidence links
- invalid URLs
- orphan product references
