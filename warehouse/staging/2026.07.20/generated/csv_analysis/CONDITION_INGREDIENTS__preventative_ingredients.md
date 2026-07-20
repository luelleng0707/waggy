# CONDITION_INGREDIENTS.csv

**Source path:** `data/preventative_ingredients/CONDITION_INGREDIENTS.csv`

## Purpose

Condition -> nutrient targets / ingredients (dual home)

## Columns

| # | Column |
|---|--------|
| 1 | `condition` |
| 2 | `ingredient_name` |
| 3 | `recommended_daily_dose` |
| 4 | `dose_unit` |
| 5 | `source_name` |
| 6 | `source_quote` |
| 7 | `source_url` |
| 8 | `priority_rank` |

## Meaning

Rows: **12**. Column count: **8**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/calculation_trace.py`
- `app/agent/ingredient_engine.py`
- `app/agent/package_detail.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/stages/nutrition.py`
- `app/agent/variable_map.py`
- `app/api/evidence.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `map_ingredients`
- `nutrition stage`
- `package_optimizer`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
CONDITION_INGREDIENTS.csv
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

- Warehouse target: `science/nutrient_targets.csv (+ ingredient_evidence)`
- Transform: dose->canonical units; citation->paper_id

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/nutrient_targets.csv (+ ingredient_evidence)`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
