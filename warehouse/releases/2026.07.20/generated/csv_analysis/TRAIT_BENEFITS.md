# TRAIT_BENEFITS.csv

**Source path:** `data/breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv`

## Purpose

Subtractive trait benefit modifiers (risk)

## Columns

| # | Column |
|---|--------|
| 1 | `trait_a` |
| 2 | `trait_b` |
| 3 | `condition` |
| 4 | `reduction_factor` |
| 5 | `reason` |
| 6 | `source` |

## Meaning

Rows: **10**. Column count: **6**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/stages/health_risk.py`
- `app/agent/variable_map.py`
- `app/data/console_inspectors.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`
- `app/ui/renderer/journey.py`

## Formula

- `apply_trait_benefits -> compute_risk`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
TRAIT_BENEFITS.csv
->
health_risk modifiers
->
compute_risk
->
downstream nutrition + packages
->
response_assembler
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/prevention_effectiveness.csv`
- Transform: benefit rows; paper_id

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/prevention_effectiveness.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
