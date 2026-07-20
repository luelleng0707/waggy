# Ingredient engine formula trace

**Source:** `app/agent/ingredient_engine.py` (+ `stages/nutrition.py`)

## Call chain

```
map_ingredients(risks, weight_kg, repo)
->
_condition_ingredient_rows() <- repository.condition_ingredients()
  merges CONDITION_INGREDIENTS.csv (scientific + preventative homes)
->
calculate_dose(link, weight_kg) - dose/unit math per link
->
_ingredient_evidence() <- INGREDIENT_EVIDENCE.csv
->
_ingredient_mechanisms() <- INGREDIENT_MECHANISMS.csv
->
returns nutrition targets / ingredient map
```

## Modifiers / side inputs

- `NUTRIENT_PRIORITIES.csv` (ordering; assembler-heavy)
- `INGREDIENT_MECHANISMS.csv`, `NATURAL_FOOD_SOURCES.csv` (narrative)
- `INGREDIENT_NUTRIENT_ESTIMATES.csv` (opt-in estimates)

## Warehouse target

- `science/nutrient_targets.csv`
- `science/ingredient_evidence.csv`
- `science/ingredient_food_sources.csv`
- `science/food_nutrients.csv`
- units via `runtime/unit_conversion.csv`

## Do not change

No edits to `ingredient_engine.py` in Phase 1.
