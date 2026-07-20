# TRAIT_CONTRIBUTION_WEIGHTS.csv

**Source path:** `data/breed_analysis/3_management_considerations/TRAIT_CONTRIBUTION_WEIGHTS.csv`

## Purpose

Report contribution weight metadata

## Columns

| # | Column |
|---|--------|
| 1 | `trait_category` |
| 2 | `trait_value` |
| 3 | `condition` |
| 4 | `risk_delta` |
| 5 | `unit` |
| 6 | `source_csv` |
| 7 | `evidence_id` |
| 8 | `mechanism_note` |

## Meaning

Rows: **7**. Column count: **8**.

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
TRAIT_CONTRIBUTION_WEIGHTS.csv
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

- Warehouse target: `runtime/parameter_defaults.csv`
- Transform: param_group=report_weights

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/parameter_defaults.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
