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

## Phase 3 (later)

Formula graph / AssessmentAgent rewrite — **only after** adapter parity stays green.
