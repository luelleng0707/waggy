# PRODUCT_COMPONENTS.csv

**Source path:** `data/product_portfolio/PRODUCT_COMPONENTS.csv`

## Purpose

Product composition / active ingredients

## Columns

| # | Column |
|---|--------|
| 1 | `product_id` |
| 2 | `component_type` |
| 3 | `component_name` |
| 4 | `value` |
| 5 | `unit` |
| 6 | `evidence_level` |
| 7 | `notes` |

## Meaning

Rows: **59**. Column count: **7**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/package_detail.py`
- `app/agent/package_optimizer.py`
- `app/agent/pipeline_trace.py`
- `app/agent/stages/optimization.py`
- `app/agent/variable_map.py`
- `app/api/evidence.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`
- `app/ui/renderer/wellness.py`

## Formula

- `coverage matching / package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
PRODUCT_COMPONENTS.csv
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
- Transform: composition rows

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/product_composition.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
