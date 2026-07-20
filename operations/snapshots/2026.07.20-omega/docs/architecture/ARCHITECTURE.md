# Architecture (generated)

Generated: `2026-07-20T22:13:35.722959+00:00`
Omega platform: `omega.1.0.0`
Algorithm: `2.1.0`
Core frozen: **True**

## Clinical execution path

`Warehouse → Repository → ExecutionContext → FormulaGraph → AssessmentResult`

New work should extend via datasets, formula nodes, plugins, dashboards, and reports — not redesign the engine.

## Layers

- `data/` + `warehouse/` — science & products
- `app/agent` — FormulaGraph (frozen math wrappers)
- `app/science` — knowledge graph / explainability
- `governance/` + `science_pipeline/` — Phase 5 release OS
- `platform/` + `quality/` + `operations/` + `meta/` — Phase Ω
