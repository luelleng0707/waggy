# CLINICAL_RISK_TIMELINE.csv

**Source path:** `data/breed_analysis/3_management_considerations/CLINICAL_RISK_TIMELINE.csv`

## Purpose

Age/timeline risk narrative for reports

## Columns

| # | Column |
|---|--------|
| 1 | `age_stage` |
| 2 | `trait_or_breed` |
| 3 | `condition` |
| 4 | `risk_level` |
| 5 | `monitoring` |
| 6 | `prevention` |
| 7 | `evidence_id` |

## Meaning

Rows: **6**. Column count: **7**.

Status: **partially_required**.

## Who reads it

### Python files

- `app/data/clinical_report_builder.py`
- `app/data/report_generator.py`
- `app/data/repository.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
CLINICAL_RISK_TIMELINE.csv
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
- Transform: map_type=risk_timeline

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
