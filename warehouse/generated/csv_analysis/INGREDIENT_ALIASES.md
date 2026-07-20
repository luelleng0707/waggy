# INGREDIENT_ALIASES.csv

**Source path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_ALIASES.csv`

## Purpose

Ingredient name aliases for coverage matching

## Columns

| # | Column |
|---|--------|
| 1 | `canonical_key` |
| 2 | `alias_key` |
| 3 | `category` |
| 4 | `parent_key` |

## Meaning

Rows: **6**. Column count: **4**.

Status: **required**.

## Who reads it

### Python files

- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `coverage matching`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
INGREDIENT_ALIASES.csv
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

- Warehouse target: `runtime/aliases.csv`
- Transform: alias_type=ingredient

## Unused columns

- `parent_key` (all empty in source)

## Possible normalization

1. Map to `runtime/aliases.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
