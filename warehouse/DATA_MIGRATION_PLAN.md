# DATA_MIGRATION_PLAN.md

**Phase 1 - plan only. Do not execute.**

Engine continues to read `data/`. Warehouse tables are schema stubs.

## Status legend

| Status | Meaning |
|--------|---------|
| Ready | Mapping known; safe to copy in a later phase |
| Blocked | Needs design decision |
| Skip | Unused / unmanifested; inventory only |

## Table plan

### BREED_ALIASES.csv

- **Rows:** 4
- **Old path:** `data/breed_analysis/1_biological_traits/BREED_ALIASES.csv`
- **New:** `runtime/aliases.csv`
- **Transformation:** alias_type=breed
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### BREEDS.csv

- **Rows:** 48
- **Old path:** `data/breed_analysis/1_biological_traits/BREEDS.csv`
- **New:** `reference/breeds.csv`
- **Transformation:** identity + FK to trait dims
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### MIXED_BREED_INTERACTIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv`
- **New:** `science/mixed_trait_interactions.csv`
- **Transformation:** optional; currently unused
- **Requirement today:** unused
- **Status:** Skip
- **Action:** Don't touch yet

### MIXED_BREED_MATRIX.csv

- **Rows:** 5
- **Old path:** `data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv`
- **New:** `science/mixed_trait_interactions.csv`
- **Transformation:** scope=breed_pair
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### ENVIRONMENTAL_MATRICES.csv

- **Rows:** 6
- **Old path:** `data/breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=environment
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### TRAIT_ATTRIBUTE_EXPLANATIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/2_evolutionary_profiles/TRAIT_ATTRIBUTE_EXPLANATIONS.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=trait_explain
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### TRAIT_PURPOSES.csv

- **Rows:** 5
- **Old path:** `data/breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=trait_purpose
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### BODYTYPE_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=body_type; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### BREED_CONDITIONS.csv

- **Rows:** 16
- **Old path:** `data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv`
- **New:** `science/breed_condition_risk.csv`
- **Transformation:** citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### CLIMATE_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/CLIMATE_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=climate; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### CLINICAL_RISK_TIMELINE.csv

- **Rows:** 6
- **Old path:** `data/breed_analysis/3_management_considerations/CLINICAL_RISK_TIMELINE.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=risk_timeline
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### COATTYPE_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=coat_type; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### ENERGY_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/ENERGY_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=energy; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### FUNCTIONGROUP_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/FUNCTIONGROUP_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=function_group; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### LIFESPAN_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/LIFESPAN_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=lifespan; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### SIZE_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/SIZE_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=size; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### SKULLTYPE_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/SKULLTYPE_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=skull_type; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### TRAIT_CONTRIBUTION_WEIGHTS.csv

- **Rows:** 7
- **Old path:** `data/breed_analysis/3_management_considerations/TRAIT_CONTRIBUTION_WEIGHTS.csv`
- **New:** `runtime/parameter_defaults.csv`
- **Transformation:** param_group=report_weights
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### TRAIT_INTERACTIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv`
- **New:** `science/mixed_trait_interactions.csv`
- **Transformation:** rename; keep multipliers
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### WEAKNESSGROUP_CONDITIONS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/3_management_considerations/WEAKNESSGROUP_CONDITIONS.csv`
- **New:** `science/trait_condition_risk.csv`
- **Transformation:** trait_category=weakness_group; citation -> paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### ACTIVITY_EVIDENCE.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv`
- **New:** `reference/papers.csv (+ prevention)`
- **Transformation:** unused today
- **Requirement today:** unused
- **Status:** Skip
- **Action:** Don't touch yet

### ACTIVITY_PRESCRIPTION_RULES.csv

- **Rows:** 4
- **Old path:** `data/breed_analysis/4_preventative_interventions/ACTIVITY_PRESCRIPTION_RULES.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=activity_rx
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### CONDITION_ACTIVITIES.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv`
- **New:** `science/prevention_effectiveness.csv`
- **Transformation:** prevention_type=activity
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### GROOMING_OBSERVATION_DEFS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/4_preventative_interventions/GROOMING_OBSERVATION_DEFS.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=grooming
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### TRAIT_BENEFITS.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv`
- **New:** `science/prevention_effectiveness.csv`
- **Transformation:** benefit rows; paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### CLINICAL_EVIDENCE_BASE.csv

- **Rows:** 7
- **Old path:** `data/breed_analysis/5_scientific_nutrition/CLINICAL_EVIDENCE_BASE.csv`
- **New:** `reference/papers.csv`
- **Transformation:** normalize into papers
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### CONDITION_INGREDIENTS.csv

- **Rows:** 12
- **Old path:** `data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv`
- **New:** `science/nutrient_targets.csv (+ ingredient_evidence)`
- **Transformation:** dose->canonical units; citation->paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### INGREDIENT_ALIASES.csv

- **Rows:** 6
- **Old path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_ALIASES.csv`
- **New:** `runtime/aliases.csv`
- **Transformation:** alias_type=ingredient
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### INGREDIENT_EVIDENCE.csv

- **Rows:** 10
- **Old path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv`
- **New:** `science/ingredient_evidence.csv`
- **Transformation:** citation->paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### INGREDIENT_MECHANISMS.csv

- **Rows:** 8
- **Old path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv`
- **New:** `science/ingredient_evidence.csv`
- **Transformation:** mechanism narrative cols
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### INGREDIENT_NUTRIENT_ESTIMATES.csv

- **Rows:** 8
- **Old path:** `data/breed_analysis/5_scientific_nutrition/INGREDIENT_NUTRIENT_ESTIMATES.csv`
- **New:** `science/food_nutrients.csv`
- **Transformation:** units->canonical
- **Requirement today:** partially_required
- **Status:** Ready
- **Action:** Don't touch yet

### NATURAL_FOOD_SOURCES.csv

- **Rows:** 15
- **Old path:** `data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv`
- **New:** `science/ingredient_food_sources.csv`
- **Transformation:** identity
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### NUTRIENT_PRIORITIES.csv

- **Rows:** 5
- **Old path:** `data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv`
- **New:** `runtime/parameter_defaults.csv`
- **Transformation:** param_group=nutrient_priority
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### CONDITION_INGREDIENTS.csv

- **Rows:** 12
- **Old path:** `data/preventative_ingredients/CONDITION_INGREDIENTS.csv`
- **New:** `science/nutrient_targets.csv (+ ingredient_evidence)`
- **Transformation:** dose->canonical units; citation->paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### CONDITION_PROTOCOLS.csv

- **Rows:** 12
- **Old path:** `data/preventative_ingredients/CONDITION_PROTOCOLS.csv`
- **New:** `science/prevention_effectiveness.csv`
- **Transformation:** unused today
- **Requirement today:** unused
- **Status:** Skip
- **Action:** Don't touch yet

### INGREDIENT_EVIDENCE.csv

- **Rows:** 10
- **Old path:** `data/preventative_ingredients/INGREDIENT_EVIDENCE.csv`
- **New:** `science/ingredient_evidence.csv`
- **Transformation:** citation->paper_id
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### EXT_SUPPLEMENTS.csv

- **Rows:** 0
- **Old path:** `data/product_portfolio/EXT_SUPPLEMENTS.csv`
- **New:** `science/product_composition.csv`
- **Transformation:** source=ext_supplements
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### EXT_TREATS_BAKERY.csv

- **Rows:** 12
- **Old path:** `data/product_portfolio/EXT_TREATS_BAKERY.csv`
- **New:** `science/product_composition.csv`
- **Transformation:** source=ext_treats
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### PACKAGE_TIERS.csv

- **Rows:** 3
- **Old path:** `data/product_portfolio/PACKAGE_TIERS.csv`
- **New:** `runtime/parameter_defaults.csv`
- **Transformation:** param_group=package_tier
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### PRODUCT_CATALOG.csv

- **Rows:** 16
- **Old path:** `data/product_portfolio/PRODUCT_CATALOG.csv`
- **New:** `science/product_composition.csv (catalog half)`
- **Transformation:** split identity vs composition
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### PRODUCT_COMPONENTS.csv

- **Rows:** 59
- **Old path:** `data/product_portfolio/PRODUCT_COMPONENTS.csv`
- **New:** `science/product_composition.csv`
- **Transformation:** composition rows
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### PRODUCT_DEFAULTS.csv

- **Rows:** 5
- **Old path:** `data/product_portfolio/PRODUCT_DEFAULTS.csv`
- **New:** `runtime/parameter_defaults.csv`
- **Transformation:** unused today
- **Requirement today:** unused
- **Status:** Skip
- **Action:** Don't touch yet

### PRODUCT_FEEDING_RULES.csv

- **Rows:** 23
- **Old path:** `data/product_portfolio/PRODUCT_FEEDING_RULES.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=feeding
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### PRODUCT_FUNCTIONS.csv

- **Rows:** 10
- **Old path:** `data/product_portfolio/PRODUCT_FUNCTIONS.csv`
- **New:** `runtime/lookup_maps.csv`
- **Transformation:** map_type=product_function
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### PRODUCT_PRICING.csv

- **Rows:** 16
- **Old path:** `data/product_portfolio/PRODUCT_PRICING.csv`
- **New:** `runtime/parameter_defaults.csv`
- **Transformation:** param_group=pricing
- **Requirement today:** required
- **Status:** Ready
- **Action:** Don't touch yet

### STAPLE_FOOD.csv

- **Rows:** 4
- **Old path:** `data/product_portfolio/STAPLE_FOOD.csv`
- **New:** `reference/foods.csv`
- **Transformation:** unmanifested; inventory only
- **Requirement today:** unused
- **Status:** Skip
- **Action:** Don't touch yet

### TREATS.csv

- **Rows:** 12
- **Old path:** `data/product_portfolio/TREATS.csv`
- **New:** `reference/foods.csv`
- **Transformation:** unmanifested; inventory only
- **Requirement today:** unused
- **Status:** Skip
- **Action:** Don't touch yet

## Collapses (important)

### Trait prevalence (9 -> 1)

```
SIZE_CONDITIONS.csv           -+
BODYTYPE_CONDITIONS.csv       -+
COATTYPE_CONDITIONS.csv       -+
ENERGY_CONDITIONS.csv         -+
SKULLTYPE_CONDITIONS.csv      -+-> science/trait_condition_risk.csv
FUNCTIONGROUP_CONDITIONS.csv  -+     trait_category + trait_value
WEAKNESSGROUP_CONDITIONS.csv  -+
CLIMATE_CONDITIONS.csv        -+
LIFESPAN_CONDITIONS.csv       -+
```

### Evidence normalization

```
inline journal/author/year/url/quote across many CSVs
        ->
reference/papers.csv  (paper_id)
        ->
science/*.csv rows keep paper_id only
```

## Cutover rule

No cutover in Phase 1. Later phases add adapters and parity tests before switching paths.
