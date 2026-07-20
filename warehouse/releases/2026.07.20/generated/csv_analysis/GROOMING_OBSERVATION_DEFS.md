# GROOMING_OBSERVATION_DEFS.csv

**Source path:** `data/breed_analysis/4_preventative_interventions/GROOMING_OBSERVATION_DEFS.csv`

## Purpose

Grooming observation definitions (reports)

## Columns

| # | Column |
|---|--------|
| 1 | `observation_key` |
| 2 | `label` |
| 3 | `normal_criteria` |
| 4 | `monitor_criteria` |
| 5 | `attention_criteria` |
| 6 | `severity_scale` |
| 7 | `recommendation_template` |
| 8 | `source_csv` |

## Meaning

Rows: **10**. Column count: **8**.

Status: **partially_required**.

## Who reads it

### Python files

- `app/data/clinical_report_builder.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
GROOMING_OBSERVATION_DEFS.csv
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

- Warehouse target: `runtime/lookup_maps.csv`
- Transform: map_type=grooming

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
