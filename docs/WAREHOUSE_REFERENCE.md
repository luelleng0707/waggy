# Warehouse Reference

Generated: `2026-07-20T22:13:36.015168+00:00`

Live clinical engine reads `data/` via `DataPlatform`.
`warehouse/` holds schemas, materialized science, graph artifacts, and Phase 5 release pointers.

## Layout

- `reference/` (14 entries)
- `science/` (9 entries)
- `runtime/` (40 entries)
- `generated/` (65 entries)
- `graph/` (3 entries)
- `current/` (1 entries)
- `releases/` (138 entries)
- `draft/` (138 entries)
- `staging/` (138 entries)
- `production/` (139 entries)
- `snapshots/` (0 entries)

Never edit `production/` tables by hand — promote via `science_pipeline.release`.
