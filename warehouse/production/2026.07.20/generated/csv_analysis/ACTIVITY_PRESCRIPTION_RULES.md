# ACTIVITY_PRESCRIPTION_RULES.csv

**Source path:** `data/breed_analysis/4_preventative_interventions/ACTIVITY_PRESCRIPTION_RULES.csv`

## Purpose

Activity prescription rules (reports)

## Columns

| # | Column |
|---|--------|
| 1 | `energy` |
| 2 | `size` |
| 3 | `body_type` |
| 4 | `age_stage` |
| 5 | `daily_km` |
| 6 | `walk_morning_min` |
| 7 | `walk_evening_min` |
| 8 | `weekly_km` |
| 9 | `mental_enrichment` |
| 10 | `swimming` |
| 11 | `fetch` |
| 12 | `training` |
| 13 | `recovery_note` |
| 14 | `source_name` |
| 15 | `source_url` |

## Meaning

Rows: **4**. Column count: **15**.

Status: **partially_required**.

## Who reads it

### Python files

- `app/data/clinical_report_builder.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
ACTIVITY_PRESCRIPTION_RULES.csv
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
- Transform: map_type=activity_rx

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
