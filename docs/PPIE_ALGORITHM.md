# PPIE Algorithm Reference (Python)

Canonical implementation: `app/agent/`. The JavaScript engine under `src/engine/` is retired; parity tests validate Python output against historical JS fixtures.

**Orchestrator:** `PPIEWellnessAgent.generate_reproducible_report()` in `app/agent/engine.py`

**Pipeline order:** biology → health_risk → epidemiology (legacy union) → management → nutrition → optimization → response assembly

---

## Biology

| | |
|---|---|
| **Purpose** | Resolve breed rows into biological trait descriptors and attach evolutionary context (trait purposes, environmental matrices). |
| **Inputs** | `DogProfileInput`: `primary_breed`, optional `secondary_breed`, `activity_level`, `current_environment`, `breed_split_pct`. |
| **Outputs** | `biology.resolved_breeds[]` (per-breed traits), `trait_purposes`, `environmental_compatibility`, metadata for trace. Frontend block: `biology` via `build_biology_block()`. |
| **CSV files** | `BREEDS.csv`, `TRAIT_PURPOSES.csv`, `ENVIRONMENTAL_MATRICES.csv` |
| **Formula** | Row lookup: `resolve_breed_rows(breeds_df, normalize_breed_name(names))`. Environmental rows filtered where `trait` ∈ all string trait values from resolved breeds (see CSV map for column notes). |
| **Dependencies** | `normalize_breed_name`, `resolve_breed_rows` (`app/agent/utils.py`) |
| **Files** | `app/agent/stages/biological.py`, `app/agent/response_assembler.py` (`build_biology_block`) |

---

## Epidemiology

| | |
|---|---|
| **Purpose** | Legacy additive union of breed-specific and trait-derived condition prevalence, with interaction multipliers. Ranked list feeds nutrition stage when health-risk output is absent; otherwise **overridden** by health-risk priorities in `engine.py`. |
| **Inputs** | Profile breeds; `biology.resolved_breeds` trait values. |
| **Outputs** | `epidemiology.breed_risks`, `trait_risks`, `priority_conditions[]` (with `weighted_priority_score`), `mixed_breed_adjustments`, `breed_evidence_detail`. |
| **CSV files** | `BREED_CONDITIONS.csv`, trait tables via `trait_condition_tables()` (9 `*_CONDITIONS.csv`), `TRAIT_INTERACTIONS.csv`, `MIXED_BREED_MATRIX.csv` |
| **Formula** | Breed pool: `sum(prevalence)` per condition across matched breeds, clipped to 1.0. Trait pool: same over matching trait values. Union: `breed + trait` per condition. Interactions: `weighted_priority = prevalence × ∏ factor`, factor clamped `[0.8, 1.2]`. |
| **Dependencies** | Biology stage output; `parse_prevalence` |
| **Files** | `app/agent/stages/epidemiology.py` |

---

## Mixed Breed Logic

| | |
|---|---|
| **Purpose** | Adjust trait-derived risk for cross-breed pairs and merge observed breed epidemiology with trait estimates. |
| **Inputs** | Two breed names; per-condition trait risk decimal; `MIXED_BREED_MATRIX` rows. |
| **Outputs** | `mixed_breed_factor` (clamped `[0.8, 1.2]`), `mixed_breed_adjustment_percent`, `mixed_breed_sources`, logic tags: `mixed_trait_estimate`, `mixed_breed_union`. Purebred path uses `purebred_observed` only. |
| **CSV files** | `MIXED_BREED_MATRIX.csv` (`breed_a`, `breed_b`, `condition`, `factor`), `BREED_CONDITIONS.csv` |
| **Formula** | For each matching breed pair and condition: `factor = ∏ clamp(f_i, 0.8, 1.2)`; `risk = clamp(trait_risk × factor)`. Union with breed rows: `risk = max(trait_nudged, observed_prevalence)`. Filter: keep rows where `risk ≥ min(positive trait risks)` or `groomer_boosted`. |
| **Dependencies** | Trait overlap pipeline; significance logic |
| **Files** | `app/agent/stages/health_risk.py` (`apply_mixed_breed_nudge`, `apply_significance_logic`) |

Note: `mixed_breed_interactions()` exists on `DataRepository` but is **not** consumed by the Python pipeline (listed in `variable_map` for trace metadata only).

---

## Trait Overlap

| | |
|---|---|
| **Purpose** | Aggregate per-trait condition prevalence into a single biological risk per condition, then apply synergistic interaction multipliers. |
| **Inputs** | All trait–condition rows matching resolved breed trait values (9 categories). |
| **Outputs** | Per condition: `base_risk`, `interaction_factor`, `risk_after_interaction`, `trait_evidence[]`, `supporting_traits[]`. |
| **CSV files** | `SIZE`, `BODYTYPE`, `COATTYPE`, `ENERGY`, `SKULLTYPE`, `CLIMATE`, `LIFESPAN`, `WEAKNESSGROUP`, `FUNCTIONGROUP` `_CONDITIONS.csv`; `TRAIT_INTERACTIONS.csv` |
| **Formula** | Per category, keep **max** prevalence. `base_risk = clamp(Σ prevalence)` (additive sum, not OR). `confidence = round10(evidence_count / 9 × 100)`. Interaction: multiply matching `factor` values where both `trait_a` and `trait_b` ∈ dog trait set and condition matches; clamp product to `[0.8, 1.2]`. Skip rows with `interaction == neutral`. |
| **Dependencies** | `CATEGORY_WEIGHTS` (used in evidence scoring metadata; sum uses raw prevalence) |
| **Files** | `app/agent/stages/health_risk.py` (`collect_trait_risks`, `compute_evidence_scores`) |

---

## Risk Scoring

| | |
|---|---|
| **Purpose** | Produce ranked condition-level risks that drive wellness goals, ingredients, and packages. |
| **Inputs** | Profile; resolved breeds; groomer `observed_conditions`; age. |
| **Outputs** | `health_risk.risks[]`: `condition_name`, `condition_key`, `risk_percent`, `risk_decimal`, `trait_risk_percent`, `breed_prevalence_percent`, adjustments, `logic`, `groomer_boosted`, `source`, `trait_explanation`. |
| **CSV files** | All trait condition tables, `BREED_CONDITIONS`, `TRAIT_INTERACTIONS`, `TRAIT_BENEFITS`, `MIXED_BREED_MATRIX` |
| **Formula** | Pipeline: trait collection → overlap/interaction → benefit reduction → significance (purebred vs mixed) → optional senior bump: `risk × 1.05` if `age_years ≥ 7`. Sort: `(-groomer_boosted, -risk_percent)`. |
| **Dependencies** | Overlap, mixed breed, benefit, significance modules |
| **Files** | `app/agent/stages/health_risk.py` (`compute_risks`), `app/agent/engine.py` (maps risks → `priority_conditions`) |

---

## Confidence

| | |
|---|---|
| **Purpose** | Express how many independent trait categories support each condition estimate. |
| **Inputs** | Count of trait categories with evidence per condition (max 9). |
| **Outputs** | `confidence_percent` on each risk row; rolled into `healthInsights` and wellness coverage. |
| **CSV files** | Same trait condition tables as overlap |
| **Formula** | `confidence_percent = js_round(evidence_count / 9 × 1000) / 10` |
| **Dependencies** | `TOTAL_TRAIT_CATEGORIES = 9` |
| **Files** | `app/agent/stages/health_risk.py` |

Groomer boosts (`GROOMER_MAP`) flag conditions for sort priority; they do not change confidence math.

---

## Ingredient Mapping

| | |
|---|---|
| **Purpose** | Map ranked conditions to daily nutrient targets with evidence and mechanisms. |
| **Inputs** | `health_risk.risks[]`; `weight_kg`. |
| **Outputs** | `raw_ingredients[]` (internal), `nutritionalTargets` / `ingredientRequirements` (frontend). Deduped by `ingredient_key`; doses merged with `max` daily dose across conditions. |
| **CSV files** | `CONDITION_INGREDIENTS.csv` (scientific + preventative merge), `INGREDIENT_EVIDENCE.csv`, `INGREDIENT_MECHANISMS.csv` |
| **Formula** | For each risk condition: `_condition_ingredient_rows()` via `condition_candidates` / `condition_matches`. Attach evidence and first mechanism row. Sort by `-daily_dose`. Stage 5 nutrition path additionally joins epidemiology priorities on exact `condition` string. |
| **Dependencies** | `condition_lookup`, `calculate_dose`, `map_ingredients` |
| **Files** | `app/agent/ingredient_engine.py`, `app/agent/stages/nutrition.py`, `app/agent/response_assembler.py` |

---

## Dosage

| | |
|---|---|
| **Purpose** | Convert CSV dose fields to daily/monthly/yearly amounts scaled by body weight when applicable. |
| **Inputs** | Condition–ingredient link row; `weight_kg`. |
| **Outputs** | `{ daily, monthly, yearly, unit }` |
| **CSV files** | `CONDITION_INGREDIENTS.csv` columns: `recommended_daily_dose`, `dose_unit`, optional `dose_basis` |
| **Formula** | If `dose_basis == "mg_per_kg"`: `daily = js_round(weight_kg × dose)`. Else: `daily = js_round(dose)`. `monthly = daily × 30`, `yearly = daily × 365`. |
| **Dependencies** | `js_round` |
| **Files** | `app/agent/ingredient_engine.py` (`calculate_dose`) |

---

## Product Matching

| | |
|---|---|
| **Purpose** | Match nutrient targets to catalog products by active-ingredient components; compute coverage and unit economics. |
| **Inputs** | `nutrition.nutrient_targets[]`; `weight_kg`; product catalog/components/pricing/rules. |
| **Outputs** | `WellnessReportPayload[]` with best `ProductFulfillment` per target; `productRecommendations` in response. |
| **CSV files** | `PRODUCT_CATALOG.csv`, `PRODUCT_COMPONENTS.csv`, `PRODUCT_PRICING.csv`, `PRODUCT_FEEDING_RULES.csv` |
| **Formula** | `coverage_pct = min(100, round(amount_per_unit / target_daily_dose × 100, 1))`. Requires `units_compatible(target_unit, component_unit)`. Ingredient keys normalized via aliases (`omega_3` ↔ `epa_dha`, etc.). Legacy mock IDs (`SF00*`, `SP00[1-8]`, `TR00[1-2]`) excluded. |
| **Dependencies** | `optimization` stage; `_match_products_for_target` |
| **Files** | `app/agent/stages/optimization.py`, `app/agent/response_assembler.py` (`build_product_recommendations`) |

---

## Package Generation

| | |
|---|---|
| **Purpose** | Build three tiered wellness packages (essential / balanced / optimal) with staples, supplements, treats, dental, pricing, and coverage scores. |
| **Inputs** | `productRecommendations`, `healthInsights`, `wellness_coverage`, profile, repo. |
| **Outputs** | `wellnessPackages[]`: tier metadata, `products_included`, `nutrition_coverage`, costs, `activities_included`. |
| **CSV files** | `PRODUCT_CATALOG`, `PRODUCT_PRICING`, `PRODUCT_FEEDING_RULES`, `CONDITION_ACTIVITIES` (activity names for top goals) |
| **Formula** | Staple: essential → `fresh_single` last in list; balanced/optimal → Wagtopia `fresh_combo`. Monthly staple cost: `js_round(unit_cost_per_bag × 7.5)`. Tier multiplier on total: essential 0.72, balanced 1.0, optimal 1.08. Coverage: `min(100, dimension × tier_mult)` with floors 72/88/97. Yearly discount: 0.95 / 0.92 / 0.88. |
| **Dependencies** | `build_wellness_packages`, verified staple IDs in `response_assembler` |
| **Files** | `app/agent/response_assembler.py` |

---

## Package Details

| | |
|---|---|
| **Purpose** | Enrich each package with serving cards, daily nutrient intake, full nutrition report, feeding strategies A–D, cost breakdown, research notes; build per-product analysis pages. |
| **Inputs** | Package object; `raw_ingredients`; `product_recommendations`; `weight_kg`; repo. |
| **Outputs** | Enriched packages (`product_cards`, `daily_nutrition_intake`, `full_nutrition_report`, `feeding_strategies`, `cost_breakdown`); `packageDetails` map by tier; `productAnalyses` keyed by `product_id`. |
| **CSV files** | Catalog, components, pricing, feeding rules, ingredient evidence, `EXT_SUPPLEMENTS.csv`, `EXT_TREATS_BAKERY.csv` (shelf life / storage) |
| **Formula** | Nutrient coverage: `min(150, round(provided/target × 100))`. Staple macros from feeding rule grams × component macro %. Whole-food grams: `round(target_dose / amount_per_100g × 100)`. |
| **Dependencies** | `enrich_package_for_detail`, `build_product_analysis`, `NUTRIENT_CATALOG` |
| **Files** | `app/agent/package_detail.py`, `app/agent/response_assembler.py` |

---

## Activity Recommendations

| | |
|---|---|
| **Purpose** | Breed-energy-based exercise plan (not condition-specific in current Python path). |
| **Inputs** | `biology.resolved_breeds` energy/function_group; `meta.ageStage`; pet name. |
| **Outputs** | `activityRecommendations`: daily minutes range, physical/mental lists, `lifestyle_tip`, empty `condition_specific`. |
| **CSV files** | None for the heuristic plan. Condition-linked rows come from `CONDITION_ACTIVITIES.csv` in management / preventative sections. |
| **Formula** | High drive → 75 min base; Low → 45; else 60. Senior × 0.75; puppy × 0.85. Range: `{base}–{base+15} minutes`. |
| **Dependencies** | `build_activity_recommendations` |
| **Files** | `app/agent/response_assembler.py`, `app/agent/engine.py` (`_run_management_stage`), `app/agent/package_detail.py` (`activities_for_condition`) |

---

## Preventative Nutrition System

| | |
|---|---|
| **Purpose** | Structured clinical narrative block: priorities, lifestyle, nutrient synthesis, whole-food equivalents, environmental compatibility. |
| **Inputs** | Profile, biology, risks, nutritional targets, repo. |
| **Outputs** | `preventativeNutritionSystem` with nested `standardized_outputs`, `whole_food_feeding_equivalents`, `narrative_synthesis`. |
| **CSV files** | `CONDITION_ACTIVITIES`, `NUTRIENT_PRIORITIES`, `CONDITION_INGREDIENTS`, `INGREDIENT_MECHANISMS`, `NATURAL_FOOD_SOURCES`, `BREED_CONDITIONS` (via risk sources) |
| **Formula** | Priorities from top 8 risks. Nutrition: prefer `NUTRIENT_PRIORITIES` sorted by `priority_rank`; else condition ingredients; else nutritional target fallback. Whole food: `grams = round(target_dose / amount_per_100g × 100)`. Climate score heuristic in `_infer_climate_compatibility`. |
| **Dependencies** | `build_preventative_nutrition_system`, `condition_matches` |
| **Files** | `app/agent/response_assembler.py` |

---

## Pipeline Trace

| | |
|---|---|
| **Purpose** | Frontend-facing audit trail of stage record counts and data lineage (not internal `AgentPipelineState.trace`). |
| **Inputs** | Biology, risks, mapped ingredients, repo. |
| **Outputs** | `pipeline_trace[]`: `stage`, `label`, `source_files`, `record_counts`; nutrition adds `orphan_conditions`; products adds `unmapped_ingredients`. |
| **CSV files** | Referenced symbolically via `VARIABLE_MAP` / `PIPELINE_STAGES` |
| **Formula** | Counts: breeds resolved, risk rows, activity rows per risk, ingredient count, feeding-plan item estimate. |
| **Dependencies** | `build_pipeline_trace`, `variable_map.PIPELINE_STAGES` |
| **Files** | `app/agent/pipeline_trace.py`, `app/agent/variable_map.py` |

---

## Wellness Score

| | |
|---|---|
| **Purpose** | Single 0–100 score summarizing nutritional coverage across wellness dimensions. |
| **Inputs** | `healthInsights`, optional `productRecommendations`, `raw_ingredients`. |
| **Outputs** | `wellness_coverage.overall_score`, `wellness_summary.wellness_score`, top-level `wellness_score` (duplicate). |
| **CSV files** | None (derived from insight scores and product coverage) |
| **Formula** | Default dimensions at 72%. Per insight: `min(98, 60 + priority_score×0.8 + confidence×0.2 + product_boost)`. Digestive boost from ingredient count. `overall = round(mean(dimension scores))`. Package tier applies separate multiplier to dimension coverage. |
| **Dependencies** | `build_wellness_coverage`, `WELLNESS_GOALS` |
| **Files** | `app/agent/response_assembler.py`, `app/agent/wellness_map.py` |

Health insights grouped by `goal_for_condition()` → max scores per goal; capped at 8 insights, sorted by groomer then priority.

---

## Feeding Plans

| | |
|---|---|
| **Purpose** | Two plan views: optimization-stage minimal plan (internal state) and bundle monthly/yearly plans in the API response. |
| **Inputs** | Selected products, `weight_kg`, `age_stage`, repo staples catalog. |
| **Outputs** | `feeding_plan` (optimization), `monthly_plan`, `yearly_plan` in response. |
| **CSV files** | `PRODUCT_CATALOG`, `PRODUCT_PRICING`, `PRODUCT_FEEDING_RULES`, `EXT_*` for shelf life |
| **Formula** | Optimization: sum `unit_cost_per_bag` of unique matched products. Monthly: best Wagtopia combo staple; `bags = ceil(daily×30 / 200g)`; supplements 1 jar; treats by pack depletion. Yearly: supplement qty `ceil(365/60)`; `savings = monthly×12 - yearly_total`. Fallback staple feeding: `weight_kg × 20 g/day`. |
| **Dependencies** | `bundle_engine`, `run_optimization_stage` |
| **Files** | `app/agent/bundle_engine.py`, `app/agent/stages/optimization.py`, `app/agent/response_assembler.py` |

---

## Response assembly entrypoint

`assemble_frontend_response()` in `app/agent/response_assembler.py` merges pipeline outputs with `map_ingredients`, wellness blocks, packages, trace, groomer flags, and legacy aliases. See `docs/PPIE_RESPONSE_SCHEMA.md` for field-level contract.

**Engine version:** `2.1.0` (`ENGINE_VERSION`).
