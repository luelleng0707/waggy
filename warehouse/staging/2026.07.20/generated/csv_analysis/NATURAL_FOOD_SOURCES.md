# NATURAL_FOOD_SOURCES.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv`

## Purpose

Natural food sources for nutrients

## Columns

| # | Column |
|---|--------|
| 1 | `ingredient_name` |
| 2 | `food_source` |
| 3 | `amount_per_100g` |
| 4 | `unit` |
| 5 | `bioavailability_notes` |

## Meaning

Rows: **15**. Column count: **5**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/variable_map.py`
- `app/data/repository.py`

## Formula

- `response_assembler`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
NATURAL_FOOD_SOURCES.csv
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

- Warehouse target: `science/ingredient_food_sources.csv`
- Transform: identity

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/ingredient_food_sources.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
