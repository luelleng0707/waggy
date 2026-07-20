# STAPLE_FOOD.csv

**Source path:** `data/product_portfolio/STAPLE_FOOD.csv`

## Purpose

Unmanifested staple food table

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `food_type` |
| 3 | `life_stage` |
| 4 | `size_support` |
| 5 | `protein_source` |
| 6 | `package_weight_g` |
| 7 | `daily_feeding_chart` |
| 8 | `energy_kcal_per_kg` |
| 9 | `protein_pct` |
| 10 | `fat_pct` |
| 11 | `fiber_pct` |
| 12 | `ash_pct` |
| 13 | `calcium_pct` |
| 14 | `phosphorus_pct` |
| 15 | `ingredient_list` |
| 16 | `storage_method` |
| 17 | `shelf_life_days` |

## Meaning

Rows: **4**. Column count: **17**.

Status: **unused**.

## Who reads it

### Python files

- `app/agent/bundle_engine.py`
- `app/agent/package_detail.py`
- `app/agent/package_optimizer.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/api/evidence.py`
- `app/ui/renderer/wellness.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
STAPLE_FOOD.csv
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

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `reference/foods.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
