# CONDITION_ACTIVITIES.csv

**Source path:** `data/breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv`

## Purpose

Condition -> activity recommendations

## Columns

| # | Column |
|---|--------|
| 1 | `condition` |
| 2 | `activity_name` |
| 3 | `frequency` |
| 4 | `duration_minutes` |
| 5 | `source_name` |
| 6 | `source_quote` |
| 7 | `source_url` |

## Meaning

Rows: **10**. Column count: **7**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/engine.py`
- `app/agent/package_detail.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/variable_map.py`
- `app/data/engine_trace.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `management / assembler`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
CONDITION_ACTIVITIES.csv
->
repository / report_generator
->
clinical_report_builder (if report path)
->
response_assembler (if wired)
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/prevention_effectiveness.csv`
- Transform: prevention_type=activity

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/prevention_effectiveness.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
