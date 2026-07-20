# PPIE Response Schema

Produced by `assemble_frontend_response()` in `app/agent/response_assembler.py`. Reference fixture: `tests/parity/dolly_golden_x_labrador/py_response.json`.

**Contract rules**

- Monetary fields are raw numbers (RMB yuan); UI applies formatting.
- Rounding uses `js_round` (half away from zero) for parity with legacy JS.
- Optional object fields are **omitted** when undefined in legacy paths (e.g. `source_name` on `risks[]` only if present).
- `null` appears for unset profile fields (`bcs`, `height_cm`) and nullable prevalence fields.

---

## Top-level key order

Keys are emitted in this order (Python 3.7+ dict insertion order):

1. `engine` · 2. `version` · 3. `pipeline_flow` · 4. `variable_map` · 5. `profile` · 6. `biology` · 7. `wellness_summary` · 8. `wellness_coverage` · 9. `healthInsights` · 10. `nutritionalTargets` · 11. `ingredientRequirements` · 12. `productRecommendations` · 13. `wellnessPackages` · 14. `packageDetails` · 15. `productAnalyses` · 16. `activityRecommendations` · 17. `scientificEvidence` · 18. `researchSection` · 19. `calculationTrace` · 20. `groomer` · 21. `preventativeNutritionSystem` · 22. `monthly_plan` · 23. `yearly_plan` · 24. `wellness_score` · 25. `pipeline_trace` · **Legacy:** 26. `pet` · 27. `risks` · 28. `ingredients` · 29. `products` · 30. `activities` · 31. `evidence`

---

## Metadata

### `engine`
- **Type:** string
- **Value:** `"PPIE"`

### `version`
- **Type:** string
- **Value:** `"2.1.0"` (`ENGINE_VERSION`)

### `pipeline_flow`
- **Type:** string[]
- **Value:** `["biology", "health_risk", "management", "nutrition", "products", "feeding_plan"]`

### `variable_map`
- **Type:** object
- **Contents:** Stage labels, CSV schemas, path aliases — mirror of `app/agent/variable_map.py` `VARIABLE_MAP` plus `pipeline_flow` and `profile_inputs` keys at top level in fixture.

### `wellness_score`
- **Type:** integer
- **Value:** Duplicate of `wellness_coverage.overall_score`

---

## Profile

### `profile` (canonical)
| Field | Type | Notes |
|-------|------|-------|
| `pet_name` | string | From `DogProfileInput.name` |
| `breeds` | string[] | Resolved names from health_risk meta when available, else primary + secondary |
| `birthday` | string \| null | ISO date optional |
| `gender`, `sex` | string \| null | `sex` or `gender` from input |
| `bcs` | number \| null | Body condition score |
| `activity_level` | string | e.g. `"High"` |
| `current_environment` | string | |
| `weight_kg` | number | float |
| `height_cm` | number \| null | |
| `age_years` | number | One decimal |
| `age_stage` | string | `"puppy"` \| `"adult"` \| `"senior"` |

### Legacy alias: `pet`
- Identical object to `profile`.

---

## Biology

### `biology`
| Field | Type | Notes |
|-------|------|-------|
| `breeds` | string[] | Input breed names (not necessarily normalized) |
| `breed_count` | integer | `len(resolved_breeds)` |
| `age_years`, `age_stage` | | From profile |
| `trait_summary` | string[] | Deduped trait values across breeds (insertion order) |
| `descriptors` | object[] | Per breed: `breed`, `size`, `body_type`, `coat_type`, `energy`, `weakness_group`, `function_group` |

---

## Wellness narrative

### `wellness_summary`
| Field | Type |
|-------|------|
| `greeting` | string — time-of-day |
| `intro`, `closing` | string |
| `wellness_score` | integer |
| `score_label` | `"Estimated Wellness Score"` |
| `primary_priorities` | string[] — up to 4 display labels |
| `traits_analysed` | string[] — copy of biology trait summary |
| `analysis_detail` | object[] — up to 6 items: `goal_id`, `title`, `biological_estimate_percent`, `observed_prevalence_percent` (nullable), `difference_percent` (nullable), `supporting_traits[]`, `explanation` |

### `wellness_coverage`
| Field | Type |
|-------|------|
| `overall_score` | integer |
| `max_score` | 100 |
| `label`, `subtitle` | string |
| `dimensions` | object[] — `goal_id`, `title`, `coverage_percent` |

### `healthInsights`
- **Type:** object[] — max **8** items, sorted by groomer priority then priority score.
- **Fields:** `goal_id`, `title`, `priority_score`, `biological_risk_percent`, `observed_prevalence_percent` (nullable), `confidence_percent`, `evidence_count`, `supporting_conditions[]`, `supporting_traits[]`, `evidence_sources[]`, `groomer_priority`, `estimated_biological_risk_percent`, `observed_breed_prevalence_percent`, `estimate_vs_observed_difference`, `explanation`, `why_this_matters`, `peer_reviewed_study_count`.

---

## Nutrition & products

### `nutritionalTargets`
- **Type:** object[]
- **Fields:** `ingredient`, `ingredient_key`, `daily_target`, `monthly_target` (formatted strings with unit), `supports_goals[]`, `evidence_quote`, `source_name`, `source_url`

### `ingredientRequirements`
- **Type:** object[]
- **Value:** **Identical** to `nutritionalTargets` (duplicate key for legacy UI).

### `productRecommendations`
- **Type:** object[] — sorted by `coverage_percent` desc
- **Fields:** `product_id`, `product_name`, `brand`, `product_type` (`fresh_food` \| `supplement` \| `treat`), `price` (int RMB), `serving_size`, `suggested_usage`, `coverage_percent`, `monthly_cost_estimate`, `active_ingredients[]` (`name`, `amount`), `why_selected`, `combined_coverage_note`, `advantages[]`
- **Empty array** when no verified products match (Dolly fixture: `[]`).

### `wellnessPackages`
- **Type:** object[] — length **3** (essential, balanced, optimal)
- **Core fields:** `tier`, `title`, `recommended` (bool), `best_for` (string \| null), `tagline`, `description`, `coverage_score`, `monthly_cost`, `yearly_cost`, `includes_summary[]`, `products_included[]`, `nutrition_coverage[]`, `overview`, `activities_included[]`, `why_fits`, `subscribe_cta`
- **Enrichment fields** (post `enrich_package_for_detail`): `package_summary`, `estimated_monthly_supply`, `product_cards[]`, `daily_nutrition_intake[]`, `full_nutrition_report[]`, `feeding_strategies[]`, `cost_breakdown`, `research_notes[]`

#### `products_included[]` item
`type`, `name`, `product_id`, `brand`, `category`, `monthly_cost`, `price`, `serving_size`, `daily_amount`, `monthly_quantity`, `coverage_percent`, `why_selected`, `combined_coverage_note`, `advantages[]`, `active_ingredients[]`, `nutrition_contribution[]`

#### `product_cards[]` item
`product_id`, `product_name`, `brand`, `category`, `image_url` (null if missing), `daily_serving`, `monthly_amount`, `monthly_cost`

#### `daily_nutrition_intake[]` item
`nutrient`, `nutrient_key`, `provided`, `target_daily`, `unit`, `coverage_percent`, `status` (`"Meets target"` \| `"Below target"` \| `"Informational"`), `evidence` (object \| null)

#### `feeding_strategies[]`
Four strategies `id` A–D with `title`, `description`, `items[]`, `calories_estimate`, `highlights[]`

#### `cost_breakdown`
`rows[]`, `monthly_total`, `yearly_total`, `annual_discount_percent`, `savings_vs_monthly`

### `packageDetails`
- **Type:** object map `{ essential, balanced, optimal }`
- **Value:** Same enriched package objects as `wellnessPackages` keyed by tier.

### `productAnalyses`
- **Type:** object map keyed by **`product_id`**
- **Built from:** each package's `product_cards`; later tiers overwrite same id.
- **Shape:**

```json
{
  "product_id": "FF001",
  "product_name": "...",
  "brand": "...",
  "category": "...",
  "package_tier": "essential",
  "overview": "...",
  "serving": { "daily", "monthly_requirement", "calories_kcal", "weight_g", "container_lasts_days" },
  "active_ingredients": [],
  "scientific_evidence": [],
  "why_included": [],
  "alternatives": [],
  "cost": { "unit_price", "yearly_cost", "monthly_cost?" },
  "specifications": { "brand", "package_units", "shelf_life_days", "storage", "category" }
}
```

`monthly_cost` on `cost` only included when not null.

---

## Activities & evidence

### `activityRecommendations`
| Field | Type |
|-------|------|
| `recommended_daily_exercise` | string — e.g. `"75–90 minutes"` |
| `suggested_physical`, `suggested_mental` | string[] |
| `lifestyle_tip` | string |
| `condition_specific` | array — **always empty** in Python |
| `future_personalization_note` | string |

### `scientificEvidence`
- **Type:** object[]
- **Fields:** `type` (`"breed"` \| `"ingredient"`), `condition`, `breed` (nullable), `source_name`, `quote`, `url`
- Deduped by url+quote key.

### `researchSection`
| Field | Type |
|-------|------|
| `title` | string |
| `biological_traits` | string[] |
| `health_priorities` | object[] — up to 6 |
| `ingredient_evidence` | object[] — up to 6 |
| `literature` | array — slice of `scientificEvidence` (max 8) |

### `calculationTrace`
- **Type:** object[] — up to 6 (one per top health insight)
- **Fields:** `condition`, `observed_inputs` (profile snapshot), `published_evidence[]`, `trait_contributions[]`, `nutrient_targets[]`, `product_contributions[]`, `decision_log[]`

---

## Groomer & preventative

### `groomer`
- **Type:** object[] — fixed 7 entries
- **Fields:** `key`, `label`, `match[]`, `status` (`"clear"` \| `"flagged"`), `live` (bool)
- Derived from `profile.observed_conditions` normalized to snake_case.

### `preventativeNutritionSystem`
| Key | Type | Description |
|-----|------|-------------|
| `pipeline_flow` | string[] | Human-readable stage names |
| `dog_profile` | object | Same fields as `profile` |
| `biological_traits` | object[] | Extended trait rows incl. `climate`, `skull_type`, `lifespan` |
| `management_considerations` | object[] | Top 8 risks as priorities |
| `lifestyle_interventions` | object[] | From CONDITION_ACTIVITIES |
| `nutritional_synthesis` | object[] | Nutrient priorities with mechanisms |
| `whole_food_feeding_equivalents` | object[] | Whole-food contracts |
| `trait_analysis`, `preventative_health_priorities` | | Duplicate of priorities list |
| `standardized_outputs` | object | `disease_risk_modifiers`, `environmental_compatibility_matrix`, nested copies |
| `output_contracts` | | Same as whole_food_feeding_equivalents |
| `narrative_synthesis` | string | Long-form paragraph |

#### `whole_food_feeding_equivalents[]` / contract item
`condition`, `priority_rank`, `targeted_intervention`: `{ active_ingredient, required_dosage, scientific_validation, natural_food_alternatives[], lifestyle_requirement | null }`

---

## Feeding plans

### `monthly_plan`
| Field | Type |
|-------|------|
| `title` | `"Monthly Wellness Plan"` |
| `duration_days` | 30 |
| `items` | object[] — staple + optional supps/treats |
| `total_cost` | number |
| `product_count` | integer |

**Item fields:** `product_name`, `product_type`, `daily`, `monthly`, `depletion`, `quantity`, `cost`, `unit_cost_per_bag` (staple), `fresh_warning` (null or string)

### `yearly_plan`
Extends monthly items with `duration: "365 days"`, adjusted `quantity`/`cost`, plus `monthly_equivalent`, `savings`, `savings_percent`, `kibble_upgrade`, `staple_upgrade` (same object or null), `bulk_notes`.

---

## Pipeline trace

### `pipeline_trace`
- **Type:** object[] — length 6
- **Fields:** `stage`, `label`, `source_files[]`, `record_counts` (integer)
- **Optional:** `orphan_conditions[]` (nutrition stage), `unmapped_ingredients[]` (products stage)

Distinct from internal `AgentPipelineState.trace` (not exported).

---

## Legacy aliases

| Key | Maps to | Notes |
|-----|---------|-------|
| `pet` | `profile` | Identical |
| `risks` | Derived from `healthInsights` | Wellness-goal shape: `condition`, `condition_key`, `risk_percent`, `estimated_risk_percent`, `trait_risk_percent`, `breed_prevalence_percent`, `confidence_percent`, `evidence_count`, `supporting_traits`, `logic: "wellness_insight"`, `groomer_boosted`, `why`; optional `source_name`, `source_quote`, `source_url` |
| `ingredients` | Remap of `nutritionalTargets` | Fields: `ingredient`, `ingredient_key`, `daily_dose`, `monthly_dose`, `for_conditions`, `evidence_quote`, `source_name`, `source_url` |
| `ingredientRequirements` | `nutritionalTargets` | Same array reference content |
| `products` | `productRecommendations` | Same data (Dolly: empty) |
| `activities` | `activityRecommendations.condition_specific` | Always `[]` |
| `evidence` | `scientificEvidence` | Same entries |

---

## Null & empty conventions (Dolly fixture)

| Field | Typical value when absent |
|-------|---------------------------|
| `profile.bcs`, `height_cm` | `null` |
| `healthInsights[].observed_prevalence_percent` | `null` (mixed-breed trait-only goals) |
| `product_cards[].image_url` | `null` |
| `daily_nutrition_intake[].evidence` | `null` for macro rows |
| `productRecommendations` | `[]` if no inventory match |
| `activities` / `condition_specific` | `[]` |
| `groomer[].live` | `false` when status `"clear"` |

---

## Input model

Request profile: `DogProfileInput` in `app/agent/state.py` — required `name`, `primary_breed`, `age_years`, `weight_kg`, `current_environment`; optional `secondary_breed`, `breed_split_pct`, `observed_conditions`, demographics.

Entry: `PPIEWellnessAgent.generate_reproducible_report(profile)` → this schema.
