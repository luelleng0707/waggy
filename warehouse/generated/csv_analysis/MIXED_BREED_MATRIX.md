# MIXED_BREED_MATRIX.csv

**Source path:** `data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv`

## Purpose

Cross-breed condition interaction multipliers

## Columns

| # | Column |
|---|--------|
| 1 | `breed_a` |
| 2 | `breed_b` |
| 3 | `condition` |
| 4 | `factor` |
| 5 | `source_name` |
| 6 | `source_quote` |
| 7 | `source_url` |

## Meaning

Rows: **5**. Column count: **7**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/stages/epidemiology.py`
- `app/agent/stages/health_risk.py`
- `app/agent/variable_map.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `apply_mixed_breed_matrix -> compute_risk`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
MIXED_BREED_MATRIX.csv
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

- Warehouse target: `science/mixed_trait_interactions.csv`
- Transform: scope=breed_pair

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/mixed_trait_interactions.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
