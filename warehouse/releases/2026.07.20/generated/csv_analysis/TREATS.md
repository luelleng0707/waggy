# TREATS.csv

**Source path:** `data/product_portfolio/TREATS.csv`

## Purpose

Unmanifested treats table

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `treat_type` |
| 3 | `protein_source` |
| 4 | `texture` |
| 5 | `weight_g` |
| 6 | `feeding_recommendation` |
| 7 | `storage_method` |
| 8 | `shelf_life_days` |

## Meaning

Rows: **12**. Column count: **8**.

Status: **unused**.

## Who reads it

### Python files

- `app/agent/bundle_engine.py`
- `app/agent/package_detail.py`
- `app/agent/package_optimizer.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/data/clinical_report_builder.py`
- `app/data/repository.py`
- `app/ui/renderer/home.py`
- `app/ui/renderer/wellness.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
TREATS.csv
->
(loaded by repository if manifested)
->
(no engine formula)
->
Validation Console browser only
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `reference/foods.csv`
- Transform: unmanifested; inventory only

## Unused columns

- `feeding_recommendation` (all empty in source)

## Possible normalization

1. Map to `reference/foods.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
