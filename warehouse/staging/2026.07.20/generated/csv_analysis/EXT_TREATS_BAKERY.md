# EXT_TREATS_BAKERY.csv

**Source path:** `data/product_portfolio/EXT_TREATS_BAKERY.csv`

## Purpose

External treat/bakery SKUs

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `treat_type` |
| 3 | `bakery_type` |
| 4 | `protein_source` |
| 5 | `texture` |
| 6 | `weight_g` |
| 7 | `feeding_recommendation` |
| 8 | `storage_method` |
| 9 | `shelf_life_days` |

## Meaning

Rows: **12**. Column count: **9**.

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
EXT_TREATS_BAKERY.csv
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
- Transform: source=ext_treats

## Unused columns

- `feeding_recommendation` (all empty in source)

## Possible normalization

1. Map to `science/product_composition.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
