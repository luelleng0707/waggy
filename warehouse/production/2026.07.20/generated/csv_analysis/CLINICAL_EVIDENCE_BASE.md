# CLINICAL_EVIDENCE_BASE.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/CLINICAL_EVIDENCE_BASE.csv`

## Purpose

Clinical evidence base for reports

## Columns

| # | Column |
|---|--------|
| 1 | `evidence_id` |
| 2 | `domain` |
| 3 | `condition` |
| 4 | `nutrient_or_activity` |
| 5 | `mechanism` |
| 6 | `evidence_level` |
| 7 | `source_name` |
| 8 | `source_quote` |
| 9 | `source_url` |
| 10 | `year` |

## Meaning

Rows: **7**. Column count: **10**.

Status: **partially_required**.

## Who reads it

### Python files

- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
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
CLINICAL_EVIDENCE_BASE.csv
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

- Warehouse target: `reference/papers.csv`
- Transform: normalize into papers

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `reference/papers.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
