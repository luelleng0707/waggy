# EXT_SUPPLEMENTS.csv

**Source path:** `data/product_portfolio/EXT_SUPPLEMENTS.csv`

## Purpose

External supplement SKUs

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `supplement_type` |
| 3 | `serving_size_g` |
| 4 | `servings_per_pack` |
| 5 | `storage_method` |
| 6 | `shelf_life_days` |

## Meaning

Rows: **0**. Column count: **6**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/bundle_engine.py`
- `app/agent/package_detail.py`
- `app/agent/package_optimizer.py`
- `app/data/repository.py`

## Formula

- `package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
EXT_SUPPLEMENTS.csv
->
repository product accessors
->
package_optimizer
->
stages/optimization
->
response_assembler
->
store/catalog APIs
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/product_composition.csv`
- Transform: source=ext_supplements

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/product_composition.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
