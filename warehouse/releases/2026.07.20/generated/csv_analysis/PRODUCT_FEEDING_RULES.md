# PRODUCT_FEEDING_RULES.csv

**Source path:** `data/product_portfolio/PRODUCT_FEEDING_RULES.csv`

## Purpose

Feeding amount rules by size/weight

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `min_weight_kg` |
| 3 | `max_weight_kg` |
| 4 | `daily_amount` |
| 5 | `daily_unit` |

## Meaning

Rows: **23**. Column count: **5**.

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
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/ui/renderer/wellness.py`

## Formula

- `feeding amount / package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PRODUCT_FEEDING_RULES.csv
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
- Transform: map_type=feeding

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
