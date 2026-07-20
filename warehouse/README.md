# Scientific Data Warehouse

Phase 1: schema + audits. Phase 2: **adapter layer** (zero formula change).

## Hard rules

- Production `data/` remains the default engine source (`backend=legacy`).
- Formulas (`health_risk`, `ingredient_engine`, `package_optimizer`, …) are **unchanged**.
- Warehouse adapters rebuild the **exact same DataFrames** formulas already consume.
- Cutover only after parity stays at 100%.

## Phase 2 components (`app/data/warehouse/`)

| Component | Role |
|-----------|------|
| `WarehouseDataPlatform` | DataPlatform-compatible; materialize → adapt → same `_tables` |
| `WarehouseRepository` | DataRepository pinned to warehouse platform |
| `TraitConditionAdapter` | 9 `*_CONDITIONS` ↔ `science/trait_condition_risk.csv` |
| `PaperAdapter` | citations ↔ `reference/papers.csv` + `paper_id` |
| `IngredientRepository` | joined evidence/foods/mechanisms view (opt-in API) |
| `UnitNormalizer` | canonical units (attached as extras; legacy cols untouched) |
| `ParameterRepository` | mirrors current constants (not wired into formulas yet) |
| `LegacyCompatibilityLayer` | warehouse → legacy objects |

## Opt-in engine backend

```python
PPIEWellnessAgent(data_dir="data", backend="legacy")     # default
PPIEWellnessAgent(data_dir="data", backend="warehouse")  # adapter path
```

## Materialize warehouse tables from `data/`

```bash
py -3 warehouse/tools/materialize.py
```

Writes `reference/papers.csv`, `science/trait_condition_risk.csv`,
`science/breed_condition_risk.csv`, `runtime/parameter_defaults.csv`,
`runtime/legacy_mirror/*.csv`, and `generated/phase2_parity_report.json`.

## Parity tests

```bash
py -3 -m pytest tests/test_warehouse_parity.py -m "not slow" -v
# Full 100-dog suite:
py -3 -m pytest tests/test_warehouse_parity.py -m slow -v
```

Table round-trip and golden-dog clinical hashes must match.

## Phase 3 — FormulaGraph

`AssessmentAgent` → `FormulaGraph` → nodes wrapping locked engines.
See `app/agent/assessment_agent.py`. Math unchanged.

## Phase 4 — Knowledge graph & explainability

Deterministic only (no AI in the clinical path):

```
warehouse/graph/       # nodes.json, edges.json, summary.json
warehouse/reasoning/   # templates / notes
warehouse/generated/   # SCIENTIFIC_AUDIT.md, knowledge_coverage.json
app/science/           # KnowledgeGraphBuilder, GraphRepository, EvidenceObject, …
```

```bash
py -3 warehouse/tools/build_science_graph.py
py -3 -m pytest tests/test_science_graph.py -q
```

APIs: `GET /api/v1/graph/{condition|paper|ingredient|product|explanation}/…`,
`GET /api/v1/graph/why?q=…`, `GET /api/v1/science/{audit|coverage|versions}`.

## Phase 5 — Versioned releases (governance OS)

Live engine still reads `data/`. Warehouse adds release pointers:

```
warehouse/
  reference|science|runtime|generated|graph/   # working science tree
  current/release.json                         # active version pointer
  draft|staging|production/<YYYY.MM.DD>/
  releases/<YYYY.MM.DD>/release.json
  snapshots/
```

```bash
py -3 -m science_pipeline.release
```

See `docs/governance/PHASE5.md` and `governance/README.md`.
