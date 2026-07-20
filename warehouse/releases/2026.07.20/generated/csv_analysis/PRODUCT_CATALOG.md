# PRODUCT_CATALOG.csv

**Source path:** `data/product_portfolio/PRODUCT_CATALOG.csv`

## Purpose

Product identity catalog

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `brand` |
| 3 | `category` |
| 4 | `subcategory` |
| 5 | `product_name` |
| 6 | `status` |
| 7 | `image_url` |
| 8 | `purchase_url` |
| 9 | `description` |
| 10 | `short_description` |
| 11 | `featured` |
| 12 | `tags` |
| 13 | `display_order` |
| 14 | `inventory_status` |
| 15 | `rating` |
| 16 | `review_count` |

## Meaning

Rows: **16**. Column count: **16**.

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
- `app/api/main.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`

## Formula

- `build_packages / package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PRODUCT_CATALOG.csv
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

- Warehouse target: `science/product_composition.csv (catalog half)`
- Transform: split identity vs composition

## Unused columns

- `image_url` (all empty in source)
- `purchase_url` (all empty in source)
- `description` (all empty in source)
- `rating` (all empty in source)
- `review_count` (all empty in source)

## Possible normalization

1. Map to `science/product_composition.csv (catalog half)`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
