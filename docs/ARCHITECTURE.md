# Waggy v2 Architecture

## Structure

The v2 architecture is layered to keep responsibilities explicit:

1. `warehouse/` — immutable fact storage only
2. `repository/warehouse/` — warehouse loading, validation, ID resolution
3. `repository/engine/` — reasoning service boundaries (skeletons in Ω1)
4. `repository/api/` — API contracts and orchestration layer
5. `repository/frontend/` — presentation layer
6. `scripts/` — operational tooling (validation and migration helpers)
7. `tests/` — layer-specific test suites
8. `docs/` — architecture and contributor guidance

## Layer Responsibilities

### Warehouse
- Stores only factual datasets.
- No scores, recommendations, cached outputs, or business logic.
- No Python modules inside warehouse directories.

### Warehouse Interface
- Implemented in `repository/warehouse/warehouse_interface.py`.
- Loads canonical datasets into immutable DataFrames.
- Runs structural + relational validation.
- Resolves IDs for engine consumers.

### Engine
- Contains domain services only.
- Must never read CSVs directly.
- Must consume warehouse data through interface contracts.

### API
- Converts external requests into engine calls.
- Must not contain inference math or direct warehouse access.

### Frontend
- Reads API responses only.
- Must not reference warehouse paths or datasets.

## Dependency Direction

Allowed:

`Warehouse -> Engine -> API -> Frontend`

Forbidden:

- `Frontend -> Warehouse`
- `Warehouse -> Engine`
- any circular dependency

## Future Reasoning Pipeline

1. Load and validate warehouse facts.
2. Build biology context.
3. Build epidemiology context.
4. Build estimation and prevention contexts.
5. Build nutrition and product contexts.
6. Run optimization.
7. Render explainability output.

Ω1 intentionally ships only the architecture skeleton and validation foundation.
