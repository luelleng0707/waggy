# Warehouse Guide

Canonical warehouse root: `warehouse/`

## Dataset Groups

### Biology
- `biology/breeds.csv`: canonical breed entities
- `biology/conditions.csv`: canonical condition entities
- `biology/breed_traits.csv`: breed trait facts
- `biology/observed_breed_conditions.csv`: epidemiologic breed-condition observations
- `biology/trait_condition_associations.csv`: trait-condition association facts
- `biology/environment_facts.csv`: environment-linked observations

### Prevention
- `prevention/condition_activities.csv`: condition-activity evidence
- `prevention/condition_ingredients.csv`: condition-ingredient evidence

### Nutrition
- `nutrition/ingredients.csv`: ingredient entities
- `nutrition/ingredient_composition.csv`: composition facts per ingredient
- `nutrition/food_composition.csv`: food composition facts
- `nutrition/units.csv`: unit dictionary

### Commercial
- `commercial/product_master.csv`: product entities + declaration metadata
- `commercial/product_recipe.csv`: product recipe declarations
- `commercial/product_declared_nutrition.csv`: declared nutrient values
- `commercial/product_feeding_guide.csv`: declared feeding guidance

### Validation datasets
- `*_NEEDS_VALIDATION.csv` files keep unresolved facts without deletion.

## Required Evidence Columns

For factual rows (especially `fact_id` rows), keep:
- `scientific_quote`
- `paper_name`
- `paper_link`
- `publication_year` (if available)
- `study_type` (if available)
- `species` (if available)
- `status`

## Relationships

Expected key relationships:
- `observed_breed_conditions.breed_id -> breeds.breed_id`
- `observed_breed_conditions.condition_id -> conditions.condition_id`
- `trait_condition_associations.condition_id -> conditions.condition_id`
- `condition_activities.condition_id -> conditions.condition_id`
- `condition_ingredients.condition_id -> conditions.condition_id`
- `condition_ingredients.ingredient_id -> ingredients.ingredient_id`
- product declaration files `.product_id -> product_master.product_id`

## Editing Rules

- Never fabricate evidence.
- Never overwrite rows without preserving provenance.
- Do not store computed predictions in warehouse CSVs.
- Use `status=needs_validation` when auto-mapping is uncertain.
- Run `py -3 scripts/validate_warehouse.py` after edits.
