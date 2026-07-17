# PPIE Data Layout (Canonical)

Runtime data is organized into deterministic subsystems.

## 1) `breed_analysis/` (architectural pivot applied)

### `breed_analysis/1_biological_traits/`
- `BREEDS.csv`
- `MIXED_BREED_MATRIX.csv`
- `MIXED_BREED_INTERACTIONS.csv`

### `breed_analysis/2_evolutionary_profiles/`
- `TRAIT_PURPOSES.csv`
- `ENVIRONMENTAL_MATRICES.csv`

### `breed_analysis/3_management_considerations/`
- `BREED_CONDITIONS.csv`
- `SIZE_CONDITIONS.csv`
- `BODYTYPE_CONDITIONS.csv`
- `COATTYPE_CONDITIONS.csv`
- `ENERGY_CONDITIONS.csv`
- `SKULLTYPE_CONDITIONS.csv`
- `CLIMATE_CONDITIONS.csv`
- `FUNCTIONGROUP_CONDITIONS.csv`
- `WEAKNESSGROUP_CONDITIONS.csv`
- `LIFESPAN_CONDITIONS.csv`
- `TRAIT_INTERACTIONS.csv`

### `breed_analysis/4_preventative_interventions/`
- `TRAIT_BENEFITS.csv`
- `CONDITION_ACTIVITIES.csv`
- `ACTIVITY_EVIDENCE.csv`

### `breed_analysis/5_scientific_nutrition/`
- `CONDITION_INGREDIENTS.csv`
- `INGREDIENT_EVIDENCE.csv`
- `INGREDIENT_MECHANISMS.csv`
- `NATURAL_FOOD_SOURCES.csv`
- `NUTRIENT_PRIORITIES.csv`
- `CLINICAL_EVIDENCE_BASE.csv`

### `breed_analysis/_legacy_misc/`
Archived non-canonical files kept for reference only.

## 2) `preventative_ingredients/`
- `CONDITION_INGREDIENTS.csv`
- `INGREDIENT_EVIDENCE.csv`
- `CONDITION_PROTOCOLS.csv`

## 3) `product_portfolio/`
## `product_portfolio/`

Canonical Wagtopia product registry (3NF):

- `PRODUCT_CATALOG.csv` — core product registry
- `PRODUCT_PRICING.csv` — `list_price_rmb`, float `package_units`, `unit_label`
- `PRODUCT_COMPONENTS.csv` — label macros, raw ingredients, active ingredients
- `EXT_TREATS_BAKERY.csv` — treat/bakery extension rows
- `EXT_SUPPLEMENTS.csv` — supplement extension rows
- `PRODUCT_FEEDING_RULES.csv` — weight-band serving rules
- `PRODUCT_FUNCTIONS.csv` — optional function tags (may be empty)
