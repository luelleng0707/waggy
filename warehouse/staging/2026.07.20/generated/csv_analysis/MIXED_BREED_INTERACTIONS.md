# MIXED_BREED_INTERACTIONS.csv

**Source path:** `data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv`

## Purpose

Mixed-breed interaction notes (unused by engine)

## Columns

| # | Column |
|---|--------|
| 1 | `trait_a` |
| 2 | `trait_b` |
| 3 | `condition` |
| 4 | `interaction` |
| 5 | `factor` |
| 6 | `reason` |
| 7 | `source` |

## Meaning

Rows: **10**. Column count: **7**.

Status: **unused**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/variable_map.py`
- `app/data/engine_trace.py`
- `app/data/repository.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
MIXED_BREED_INTERACTIONS.csv
->
(loaded by repository if manifested)
->
(no engine formula)
->
Validation Console browser only
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/mixed_trait_interactions.csv`
- Transform: optional; currently unused

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/mixed_trait_interactions.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
