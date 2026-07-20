# PRODUCT_PRICING.csv

**Source path:** `data/product_portfolio/PRODUCT_PRICING.csv`

## Purpose

Product pricing

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `list_price_rmb` |
| 3 | `package_units` |
| 4 | `unit_label` |

## Meaning

Rows: **16**. Column count: **4**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/bundle_engine.py`
- `app/agent/package_detail.py`
- `app/agent/package_optimizer.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/stages/optimization.py`
- `app/agent/variable_map.py`
- `app/api/evidence.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`
- `app/ui/renderer/wellness.py`

## Formula

- `package_optimizer cost`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PRODUCT_PRICING.csv
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
- Transform: param_group=pricing

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/parameter_defaults.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
