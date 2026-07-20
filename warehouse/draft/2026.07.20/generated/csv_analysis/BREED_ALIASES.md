# BREED_ALIASES.csv

**Source path:** `data/breed_analysis/1_biological_traits/BREED_ALIASES.csv`

## Purpose

Breed name normalization aliases

## Columns

| # | Column |
|---|--------|
| 1 | `alias` |
| 2 | `canonical_breed` |

## Meaning

Rows: **4**. Column count: **2**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/utils.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `normalize_breed`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
BREED_ALIASES.csv
->
run_biological_stage
->
traits on dog profile
->
compute_risk
->
ingredient_engine
->
package_optimizer
->
response_assembler
->
Clinical Assessment
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `runtime/aliases.csv`
- Transform: alias_type=breed

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/aliases.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
