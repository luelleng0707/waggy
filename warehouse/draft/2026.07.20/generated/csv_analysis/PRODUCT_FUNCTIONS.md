# PRODUCT_FUNCTIONS.csv

**Source path:** `data/product_portfolio/PRODUCT_FUNCTIONS.csv`

## Purpose

Product functional tags

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `function` |
| 3 | `confidence` |

## Meaning

Rows: **10**. Column count: **3**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/package_optimizer.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `product tagging / package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PRODUCT_FUNCTIONS.csv
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

- Warehouse target: `runtime/lookup_maps.csv`
- Transform: map_type=product_function

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
