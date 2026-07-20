# PACKAGE_TIERS.csv

**Source path:** `data/product_portfolio/PACKAGE_TIERS.csv`

## Purpose

Package tier definitions & staple rules

## Columns

| # | Column |
|---|--------|
| 1 | `tier_id` |
| 2 | `title` |
| 3 | `yearly_discount_factor` |
| 4 | `staple_product_id` |
| 5 | `sort_order` |

## Meaning

Rows: **3**. Column count: **5**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/package_optimizer.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `staple selection / package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PACKAGE_TIERS.csv
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
- Transform: param_group=package_tier

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/parameter_defaults.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
