# INGREDIENT_EVIDENCE.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv`

## Purpose

Ingredient evidence citations (dual home)

## Columns

| # | Column |
|---|--------|
| 1 | `ingredient_name` |
| 2 | `source_name` |
| 3 | `source_quote` |
| 4 | `source_url` |
| 5 | `year` |
| 6 | `supports_joint` |
| 7 | `supports_skin` |
| 8 | `supports_gut` |
| 9 | `anti_inflammatory` |

## Meaning

Rows: **10**. Column count: **9**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/calculation_trace.py`
- `app/agent/ingredient_engine.py`
- `app/agent/package_detail.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/variable_map.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`
- `app/ui/renderer/wellness.py`

## Formula

- `response_assembler evidence`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
INGREDIENT_EVIDENCE.csv
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
- Transform: citation->paper_id

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/ingredient_evidence.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
