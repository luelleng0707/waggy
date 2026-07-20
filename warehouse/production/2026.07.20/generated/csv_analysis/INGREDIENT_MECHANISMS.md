# INGREDIENT_MECHANISMS.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv`

## Purpose

Ingredient mechanism narratives

## Columns

| # | Column |
|---|--------|
| 1 | `nutrient_name` |
| 2 | `ingredient_name` |
| 3 | `source_product_id` |
| 4 | `amount_per_serving` |
| 5 | `unit` |
| 6 | `mechanism_summary` |
| 7 | `evidence_level` |

## Meaning

Rows: **8**. Column count: **7**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/ingredient_engine.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/variable_map.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/repository.py`

## Formula

- `response_assembler`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
INGREDIENT_MECHANISMS.csv
->
repository condition_ingredients / evidence
->
ingredient_engine / nutrition stage
->
package_optimizer coverage
->
response_assembler
->
Clinical Assessment
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/ingredient_evidence.csv`
- Transform: mechanism narrative cols

## Unused columns

- `evidence_level` (all empty in source)

## Possible normalization

1. Map to `science/ingredient_evidence.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
