# NUTRIENT_PRIORITIES.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv`

## Purpose

Nutrient priority ordering for assembly

## Columns

| # | Column |
|---|--------|
| 1 | `condition` |
| 2 | `nutrient_name` |
| 3 | `target_dose` |
| 4 | `target_unit` |
| 5 | `priority_rank` |
| 6 | `evidence_level` |
| 7 | `source_name` |
| 8 | `source_quote` |
| 9 | `source_url` |

## Meaning

Rows: **5**. Column count: **9**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/variable_map.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/repository.py`

## Formula

- `response_assembler`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
NUTRIENT_PRIORITIES.csv
->
repository condition_ingredients / evidence
->
ingredient_engine / nutrition stage
->
package_optimizer coverage
->
response_assembler
->
Clinical Assessment
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `runtime/parameter_defaults.csv`
- Transform: param_group=nutrient_priority

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/parameter_defaults.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
