# PPIE CSV Map

Loader: `DataRepository` in `app/agent/utils.py`. All CSVs load as strings (`dtype=str`, `keep_default_na=False`); column names are stripped. Cached by relative path key.

**Path aliases** (`resolve_path`): `2_evolutionary_traits` → `2_evolutionary_profiles`; `4_preventative_management` → `4_preventative_interventions`; `breed_analysis/product_portfolio` → `product_portfolio`.

**Shared normalization**

| Helper | Behavior |
|--------|----------|
| `parse_prevalence` | Strip `%`; if value > 1 treat as percent → divide by 100; else decimal |
| `normalize_breed_name` | `BREED_ALIASES`: lab/labrador → Labrador Retriever; golden → Golden Retriever |
| `canonical_key` / `condition_key` | Lowercase alphanumeric join (conditions) |
| `ingredient_key` | Lowercase with underscores (ingredients) |
| `condition_candidates` | Normalized condition + goal siblings from `GOAL_CONDITION_MAP` |
| `condition_matches` | Match on canonical key of `condition_key` or name column |

---

## `data/breed_analysis/1_biological_traits/BREEDS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `breed`, `size`, `body_type`, `coat_type`, `energy`, `weakness_group`, `skull_type`, `climate`, `lifespan`, `function_group` |
| **Loader** | `DataRepository.breeds()` → `load_csv` |
| **Subsystems** | Biology, health risk (`_breed_records`), epidemiology |
| **Normalization** | Breed name via `normalize_breed_name`; case-insensitive match, substring fallback |
| **Sorting** | CSV order preserved |
| **Filtering** | Rows where `breed` ∈ profile breed list |
| **Fallback** | Empty DataFrame → no resolved breeds; health risk uses raw input names |
| **Aliases** | Common nicknames in `BREED_ALIASES` |

---

## `data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `breed_a`, `breed_b`, `condition`, `factor`, optional `source_*` |
| **Loader** | `mixed_breed_matrix()` |
| **Subsystems** | Health risk (mixed-breed nudge), epidemiology (adjustment listing) |
| **Normalization** | Condition → `condition_key()`; breed pair order-insensitive match |
| **Sorting** | None |
| **Filtering** | Matching condition key and breed pair |
| **Fallback** | Empty or single breed → factor 1, no adjustment |
| **Aliases** | `variable_map` documents legacy names (`primary_breed`/`secondary_breed`) — runtime CSV uses `breed_a`/`breed_b` |

---

## `data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `trait_a`, `trait_b`, `condition`, `interaction`, `factor`, `reason`, `source` |
| **Loader** | `mixed_breed_interactions()` |
| **Subsystems** | **Not consumed** by Python pipeline (trace metadata only) |
| **Normalization** | None at load |
| **Sorting** | CSV order |
| **Filtering** | N/A in Python |
| **Fallback** | Empty DataFrame |
| **Aliases** | Listed in `variable_map` biology files |

---

## `data/breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | All columns exported to `biology.trait_purposes` records |
| **Loader** | `trait_purposes()` |
| **Subsystems** | Biology stage payload |
| **Normalization** | None |
| **Sorting** | CSV order |
| **Filtering** | None (full table attached) |
| **Fallback** | Empty list in biology payload |
| **Aliases** | Path alias from `2_evolutionary_traits` |

---

## `data/breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | Intended: trait values; code filters column `trait` (CSV header: `trait_category`, `trait_value`) |
| **Loader** | `environmental_matrices()` |
| **Subsystems** | Biology (`environmental_compatibility`) |
| **Normalization** | Match resolved breed trait strings |
| **Sorting** | None |
| **Filtering** | `environmental["trait"].isin(trait_values)` in `biological.py` |
| **Fallback** | Empty compatibility list if no column match |
| **Aliases** | Path alias from `2_evolutionary_traits` |

---

## `data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `breed`, `condition`, `prevalence`, `sample_population`, `sample_size`, `source_name`, `source_quote`, `source_url`, `year`, `confidence_level` |
| **Loader** | `breed_conditions()` — applies `parse_prevalence` on `prevalence` |
| **Subsystems** | Health risk (observed prevalence), epidemiology, calculation trace |
| **Normalization** | Prevalence → decimal; breed lowercase match |
| **Sorting** | Health risk purebred: by groomer then risk; epidemiology: by prevalence desc |
| **Filtering** | Breeds in profile list |
| **Fallback** | Empty → purebred/mixed observed paths skip breed evidence |
| **Aliases** | `confidence_level` used as confidence in epidemiology groupby |

---

## Trait condition tables (9 files)

Paths under `data/breed_analysis/3_management_considerations/`:

- `SIZE_CONDITIONS.csv` — key column `size`
- `BODYTYPE_CONDITIONS.csv` — `body_type`
- `COATTYPE_CONDITIONS.csv` — `coat_type`
- `ENERGY_CONDITIONS.csv` — `energy`
- `SKULLTYPE_CONDITIONS.csv` — `skull_type`
- `CLIMATE_CONDITIONS.csv` — `climate`
- `LIFESPAN_CONDITIONS.csv` — `lifespan`
- `WEAKNESSGROUP_CONDITIONS.csv` — `weakness_group`
- `FUNCTIONGROUP_CONDITIONS.csv` — `function_group`

| Field | Detail |
|-------|--------|
| **Columns used** | Trait column, `condition`, `prevalence`, `sample_population`, `sample_size`, `source_name`, `source_quote`, `source_url`, `year`, `confidence_level`; loader adds `trait_category`, `trait_value` |
| **Loader** | `trait_condition_tables()` — concat all non-empty frames |
| **Subsystems** | Health risk (trait collection, overlap), epidemiology trait pool |
| **Normalization** | `parse_prevalence` on prevalence |
| **Sorting** | **Concat encounter order** preserved (matches JS store order for overlap) |
| **Filtering** | Row trait value equals resolved breed trait for category |
| **Fallback** | Skip empty files; empty concat → no trait risks |
| **Aliases** | Per-table trait column name mapped to unified `trait_value` |

---

## `data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `trait_a`, `trait_b`, `condition`, `interaction`, `factor`, `reason`, `source` |
| **Loader** | `trait_interactions()` — `factor` coerced numeric, NaN → 1.0 |
| **Subsystems** | Health risk overlap, epidemiology multipliers |
| **Normalization** | Condition matched by name or `condition_key`; skip `interaction == neutral` |
| **Sorting** | None |
| **Filtering** | Both traits in dog trait set |
| **Fallback** | factor 1.0; product clamped `[0.8, 1.2]` |
| **Aliases** | `trait_1`/`trait_2`/`target_condition`/`multiplier_effect` in `variable_map` |

---

## `data/breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `trait_a`, `trait_b`, `condition`, `reduction_factor`, `reason`, `source` |
| **Loader** | `trait_benefits()` — numeric `reduction_factor`, NaN → 1.0 |
| **Subsystems** | Health risk benefit reduction |
| **Normalization** | First matching row per condition |
| **Sorting** | None |
| **Filtering** | Traits in dog set + condition match |
| **Fallback** | `benefit_factor = 1` |
| **Aliases** | Path alias from `4_preventative_management` |

---

## `data/breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `condition`, `activity_name`, `frequency`, `duration_minutes`, `source_name`, `source_quote`, `source_url` |
| **Loader** | `condition_activities()` |
| **Subsystems** | Management stage, preventative nutrition, package activities, pipeline trace counts |
| **Normalization** | `condition_matches` with goal siblings; `duration_minutes` via `_js_number` |
| **Sorting** | CSV encounter order |
| **Filtering** | Top 10 priority conditions (management); per-priority condition (preventative) |
| **Fallback** | Empty lifestyle lists |
| **Aliases** | Legacy column `activity` supported in engine management filter |

---

## `data/breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `activity_name`, `source_name`, `source_quote`, `source_url`, `year` |
| **Loader** | `activity_evidence()` |
| **Subsystems** | **Not consumed** by Python pipeline |
| **Normalization** | None |
| **Sorting** | CSV order |
| **Filtering** | N/A |
| **Fallback** | Empty DataFrame |
| **Aliases** | Referenced in `variable_map` management stage |

---

## `data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `condition`, `ingredient_name`, `recommended_daily_dose`, `dose_unit`, `priority_rank`, `source_name`, `source_quote`, `source_url`, `evidence_type`; optional `dose_basis`, `condition_key`, `ingredient_key` |
| **Loader** | Part of `condition_ingredients()` merge |
| **Subsystems** | Nutrition stage, ingredient engine, preventative nutrition |
| **Normalization** | Dose columns: `recommended_daily_dose` or `target_daily_dose`; `canonical_key` / `ingredient_key` |
| **Sorting** | Nutrition: by `weighted_priority_score`, dose; ingredient map: by `-daily_dose` |
| **Filtering** | Inner join on exact `condition` (nutrition); fuzzy match (ingredient engine) |
| **Fallback** | Orphan conditions list; preventative falls back to nutrient priorities then targets |
| **Aliases** | Merged with preventative copy; dedupe on `(condition, ingredient_name)` keep first |

---

## `data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `ingredient_name`, `source_name`, `source_quote`, `source_url`, `year` |
| **Loader** | Part of `ingredient_evidence()` concat |
| **Subsystems** | Ingredient mapping, package detail evidence, scientific evidence collection |
| **Normalization** | Match by `ingredient_key` on name columns |
| **Sorting** | First hit wins |
| **Filtering** | By ingredient key/name |
| **Fallback** | Link row `source_*` fields |
| **Aliases** | Merged with `preventative_ingredients/INGREDIENT_EVIDENCE.csv` (no dedupe) |

---

## `data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `nutrient_name`, `ingredient_name`, `source_product_id`, `amount_per_serving`, `unit`, `mechanism_summary`, `evidence_level` |
| **Loader** | `ingredient_mechanisms()` |
| **Subsystems** | Ingredient engine, preventative nutrition (`mechanisms`, max 4) |
| **Normalization** | `ingredient_key` match on nutrient or ingredient name |
| **Sorting** | CSV order; break at 4 mechanisms |
| **Filtering** | Name/key equality |
| **Fallback** | Empty mechanisms array |
| **Aliases** | — |

---

## `data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `ingredient_name`, `food_source`, `amount_per_100g`, `unit`, `bioavailability_notes` |
| **Loader** | `natural_food_sources()` |
| **Subsystems** | Preventative whole-food equivalents |
| **Normalization** | Match nutrient by `ingredient_key` or lowercase name |
| **Sorting** | CSV order |
| **Filtering** | `amount_per_100g > 0` |
| **Fallback** | Empty `natural_food_alternatives` |
| **Aliases** | `food_item` alias in output |

---

## `data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `condition`, `nutrient_name`, `target_dose`, `target_unit`, `priority_rank`, `evidence_level`, `source_name`, `source_quote`, `source_url` |
| **Loader** | `nutrient_priorities()` |
| **Subsystems** | Preventative nutrition (preferred over condition ingredients) |
| **Normalization** | `_js_number` on doses/ranks |
| **Sorting** | Ascending `priority_rank` |
| **Filtering** | `condition_matches` per priority condition |
| **Fallback** | Falls through to `CONDITION_INGREDIENTS` then nutritional targets |
| **Aliases** | `variable_map` schema differs from on-disk columns (implementation uses condition-keyed rows) |

---

## `data/breed_analysis/5_scientific_nutrition/CLINICAL_EVIDENCE_BASE.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `evidence_id`, `domain`, `condition`, `nutrient_or_activity`, `mechanism`, `evidence_level`, `source_name`, `source_quote`, `source_url`, `year` |
| **Loader** | **No Python loader** (JS `csvLoader` only) |
| **Subsystems** | Not used by Python PPIE |
| **Normalization** | — |
| **Sorting** | — |
| **Filtering** | — |
| **Fallback** | — |
| **Aliases** | — |

---

## `data/preventative_ingredients/CONDITION_INGREDIENTS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | Same as scientific copy: `condition`, `ingredient_name`, `recommended_daily_dose`, `dose_unit`, `priority_rank`, `source_*` |
| **Loader** | Merged in `condition_ingredients()` after scientific rows |
| **Subsystems** | Nutrition, ingredient engine, preventative |
| **Normalization** | Dedupe: scientific rows win on `(condition, ingredient_name)` |
| **Sorting** | Concat order: scientific first |
| **Filtering** | Same as scientific |
| **Fallback** | If scientific empty, use preventative alone |
| **Aliases** | — |

---

## `data/preventative_ingredients/CONDITION_PROTOCOLS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | Quoted CSV: `condition`, `ingredient_name`, `recommended_daily_dose`, `dose_unit`, `priority_rank`, `source_*`, `year`, `evidence_type` |
| **Loader** | **No Python loader** |
| **Subsystems** | Not used by Python PPIE |
| **Normalization** | — |
| **Sorting** | — |
| **Filtering** | — |
| **Fallback** | — |
| **Aliases** | — |

---

## `data/preventative_ingredients/INGREDIENT_EVIDENCE.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `ingredient_name`, `source_name`, `source_quote`, `source_url`, `year` |
| **Loader** | Appended in `ingredient_evidence()` if scientific non-empty |
| **Subsystems** | Ingredient evidence lookup |
| **Normalization** | Same as scientific evidence |
| **Sorting** | Scientific rows searched first |
| **Filtering** | By ingredient key |
| **Fallback** | Scientific-only or preventative-only if one side empty |
| **Aliases** | — |

---

## `data/product_portfolio/PRODUCT_CATALOG.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `brand`, `category`, `subcategory`, `product_name`, `status`, `image_url`, `purchase_url` |
| **Loader** | `product_catalog()` |
| **Subsystems** | Product matching, packages, bundle plans, package detail |
| **Normalization** | `product_type` derived from category/subcategory |
| **Sorting** | Staples: iteration order; recs by `coverage_percent` desc |
| **Filtering** | `status == active`; exclude legacy mock IDs |
| **Fallback** | Empty catalog → no product matches |
| **Aliases** | — |

---

## `data/product_portfolio/PRODUCT_COMPONENTS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `component_type`, `component_name`, `value`, `unit`, `evidence_level`, `notes` |
| **Loader** | `product_components()` |
| **Subsystems** | Optimization (active ingredients), package detail (macros, actives) |
| **Normalization** | `component_type == active_ingredient`; ingredient key aliases (`EPA+DHA` → `omega_3`, etc.) |
| **Sorting** | Best coverage product first per target |
| **Filtering** | Unit compatibility with target dose |
| **Fallback** | No match → empty fulfillment |
| **Aliases** | Component display names in package detail |

---

## `data/product_portfolio/PRODUCT_PRICING.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `list_price_rmb`, `package_units`, `unit_label` |
| **Loader** | `product_pricing()` — numeric coercion on price/units |
| **Subsystems** | Unit economics, package pricing, bundle plans |
| **Normalization** | `unit_cost_per_bag = round((price/units)×100)/100` |
| **Sorting** | — |
| **Filtering** | By `product_id` |
| **Fallback** | Price 0, units 1 if missing |
| **Aliases** | — |

---

## `data/product_portfolio/PRODUCT_FEEDING_RULES.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `min_weight_kg`/`weight_min_kg`, `max_weight_kg`/`weight_max_kg`, `daily_amount`, `daily_unit` |
| **Loader** | `product_feeding_rules()` — normalizes weight column names |
| **Subsystems** | Product matching, packages, package detail, bundle engine |
| **Normalization** | Numeric weight bounds and daily amount |
| **Sorting** | First matching weight band (`iloc[0]`) |
| **Filtering** | `weight_min ≤ weight_kg ≤ weight_max` |
| **Fallback** | `"1 serving/day"` or `weight_kg × 20 g` for staples |
| **Aliases** | `min_weight_kg` → `weight_min_kg` at load |

---

## `data/product_portfolio/PRODUCT_FUNCTIONS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `function`, `confidence` |
| **Loader** | **No Python loader** |
| **Subsystems** | Not used by Python PPIE |
| **Normalization** | — |
| **Sorting** | — |
| **Filtering** | — |
| **Fallback** | — |
| **Aliases** | — |

---

## `data/product_portfolio/EXT_SUPPLEMENTS.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `supplement_type`, `serving_size_g`, `servings_per_pack`, `storage_method`, `shelf_life_days` |
| **Loader** | `load_csv` direct from `package_detail.py`, `bundle_engine.py` |
| **Subsystems** | Shelf life / storage enrichment when absent from catalog |
| **Normalization** | `shelf_life_days` → int, default 365 |
| **Sorting** | — |
| **Filtering** | By `product_id` |
| **Fallback** | Default shelf 365 days, storage null → `"Cool, dry place"` in analysis |
| **Aliases** | — |

---

## `data/product_portfolio/EXT_TREATS_BAKERY.csv`

| Field | Detail |
|-------|--------|
| **Columns used** | `product_id`, `treat_type`, `bakery_type`, `protein_source`, `texture`, `weight_g`, `feeding_recommendation`, `storage_method`, `shelf_life_days` |
| **Loader** | `load_csv` direct (same as EXT_SUPPLEMENTS pattern) |
| **Subsystems** | Shelf life / storage for treats; bundle fresh warnings |
| **Normalization** | Same as supplements extension |
| **Sorting** | — |
| **Filtering** | By `product_id` |
| **Fallback** | shelf 365; fresh_warning null if shelf > 30 |
| **Aliases** | — |

---

## Quick reference: loader method → path

| Method | Path |
|--------|------|
| `breeds()` | `breed_analysis/1_biological_traits/BREEDS.csv` |
| `mixed_breed_matrix()` | `breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv` |
| `mixed_breed_interactions()` | `breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv` |
| `trait_purposes()` | `breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv` |
| `environmental_matrices()` | `breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv` |
| `breed_conditions()` | `breed_analysis/3_management_considerations/BREED_CONDITIONS.csv` |
| `trait_condition_tables()` | Nine `*_CONDITIONS.csv` under `3_management_considerations/` |
| `trait_interactions()` | `breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv` |
| `trait_benefits()` | `breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv` |
| `condition_activities()` | `breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv` |
| `activity_evidence()` | `breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv` |
| `condition_ingredients()` | Scientific + `preventative_ingredients/CONDITION_INGREDIENTS.csv` |
| `ingredient_evidence()` | Scientific + `preventative_ingredients/INGREDIENT_EVIDENCE.csv` |
| `ingredient_mechanisms()` | `breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv` |
| `natural_food_sources()` | `breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv` |
| `nutrient_priorities()` | `breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv` |
| `product_catalog()` | `product_portfolio/PRODUCT_CATALOG.csv` |
| `product_components()` | `product_portfolio/PRODUCT_COMPONENTS.csv` |
| `product_pricing()` | `product_portfolio/PRODUCT_PRICING.csv` |
| `product_feeding_rules()` | `product_portfolio/PRODUCT_FEEDING_RULES.csv` |

Missing file → warning log + empty `DataFrame` (downstream stages generally no-op).
