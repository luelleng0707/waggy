# PRODUCT_DEFAULTS.csv

**Source path:** `data/product_portfolio/PRODUCT_DEFAULTS.csv`

## Purpose

Product defaults (unused by engine)

## Columns

| # | Column |
|---|--------|
| 1 | `key` |
| 2 | `product_id` |

## Meaning

Rows: **5**. Column count: **2**.

Status: **unused**.

## Who reads it

### Python files

- `app/data/engine_trace.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PRODUCT_DEFAULTS.csv
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

- Warehouse target: `runtime/parameter_defaults.csv`
- Transform: unused today

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/parameter_defaults.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
