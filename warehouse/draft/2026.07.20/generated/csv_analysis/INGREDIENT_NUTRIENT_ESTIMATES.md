# INGREDIENT_NUTRIENT_ESTIMATES.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_NUTRIENT_ESTIMATES.csv`

## Purpose

Ingredient nutrient estimates (opt-in)

## Columns

| # | Column |
|---|--------|
| 1 | `ingredient` |
| 2 | `canonical_ingredient` |
| 3 | `nutrient` |
| 4 | `amount_per_100g` |
| 5 | `unit` |
| 6 | `confidence` |
| 7 | `source` |
| 8 | `is_estimated` |
| 9 | `category` |
| 10 | `parent` |
| 11 | `property_tags` |
| 12 | `notes` |

## Meaning

Rows: **8**. Column count: **12**.

Status: **partially_required**.

## Who reads it

### Python files

- `app/inference/formula_registry.py`
- `app/inference/ingredient.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
INGREDIENT_NUTRIENT_ESTIMATES.csv
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

- Warehouse target: `science/food_nutrients.csv`
- Transform: units->canonical

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/food_nutrients.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
