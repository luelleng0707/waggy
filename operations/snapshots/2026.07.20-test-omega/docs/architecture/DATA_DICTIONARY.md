# Data Dictionary

Generated: `2026-07-20T22:10:22.060756+00:00`

## `activity_evidence`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `activity_name` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `activity_prescription_rules`

Rows: 4

| Column | Dtype | Non-null |
|---|---|---:|
| `energy` | str | 4 |
| `size` | str | 4 |
| `body_type` | str | 4 |
| `age_stage` | str | 4 |
| `daily_km` | str | 4 |
| `walk_morning_min` | str | 4 |
| `walk_evening_min` | str | 4 |
| `weekly_km` | str | 4 |
| `mental_enrichment` | str | 4 |
| `swimming` | str | 4 |
| `fetch` | str | 4 |
| `training` | str | 4 |
| `recovery_note` | str | 4 |
| `source_name` | str | 4 |
| `source_url` | str | 4 |
| `_csv_row` | int64 | 4 |
| `_csv_file` | str | 4 |

## `bodytype_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `body_type` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `breed_aliases`

Rows: 4

| Column | Dtype | Non-null |
|---|---|---:|
| `alias` | str | 4 |
| `canonical_breed` | str | 4 |
| `_csv_row` | int64 | 4 |
| `_csv_file` | str | 4 |

## `breed_conditions`

Rows: 16

| Column | Dtype | Non-null |
|---|---|---:|
| `breed` | str | 16 |
| `condition` | str | 16 |
| `prevalence` | str | 16 |
| `sample_population` | str | 16 |
| `sample_size` | str | 16 |
| `source_name` | str | 16 |
| `source_quote` | str | 16 |
| `source_url` | str | 16 |
| `year` | str | 16 |
| `confidence_level` | str | 16 |
| `_csv_row` | int64 | 16 |
| `_csv_file` | str | 16 |

## `breeds`

Rows: 48

| Column | Dtype | Non-null |
|---|---|---:|
| `breed` | str | 48 |
| `size` | str | 48 |
| `body_type` | str | 48 |
| `coat_type` | str | 48 |
| `energy` | str | 48 |
| `weakness_group` | str | 48 |
| `skull_type` | str | 48 |
| `climate` | str | 48 |
| `lifespan` | str | 48 |
| `function_group` | str | 48 |
| `_csv_row` | int64 | 48 |
| `_csv_file` | str | 48 |

## `climate_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `climate` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `clinical_evidence_base`

Rows: 7

| Column | Dtype | Non-null |
|---|---|---:|
| `evidence_id` | str | 7 |
| `domain` | str | 7 |
| `condition` | str | 7 |
| `nutrient_or_activity` | str | 7 |
| `mechanism` | str | 7 |
| `evidence_level` | str | 7 |
| `source_name` | str | 7 |
| `source_quote` | str | 7 |
| `source_url` | str | 7 |
| `year` | str | 7 |
| `_csv_row` | int64 | 7 |
| `_csv_file` | str | 7 |

## `clinical_risk_timeline`

Rows: 6

| Column | Dtype | Non-null |
|---|---|---:|
| `age_stage` | str | 6 |
| `trait_or_breed` | str | 6 |
| `condition` | str | 6 |
| `risk_level` | str | 6 |
| `monitoring` | str | 6 |
| `prevention` | str | 6 |
| `evidence_id` | str | 6 |
| `_csv_row` | int64 | 6 |
| `_csv_file` | str | 6 |

## `coattype_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `coat_type` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `condition_activities`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `condition` | str | 10 |
| `activity_name` | str | 10 |
| `frequency` | str | 10 |
| `duration_minutes` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `condition_ingredients_prev`

Rows: 12

| Column | Dtype | Non-null |
|---|---|---:|
| `condition` | str | 12 |
| `ingredient_name` | str | 12 |
| `recommended_daily_dose` | str | 12 |
| `dose_unit` | str | 12 |
| `source_name` | str | 12 |
| `source_quote` | str | 12 |
| `source_url` | str | 12 |
| `priority_rank` | str | 12 |
| `_csv_row` | int64 | 12 |
| `_csv_file` | str | 12 |

## `condition_ingredients_sci`

Rows: 12

| Column | Dtype | Non-null |
|---|---|---:|
| `condition` | str | 12 |
| `ingredient_name` | str | 12 |
| `recommended_daily_dose` | str | 12 |
| `dose_unit` | str | 12 |
| `source_name` | str | 12 |
| `source_quote` | str | 12 |
| `source_url` | str | 12 |
| `priority_rank` | str | 12 |
| `evidence_type` | str | 12 |
| `_csv_row` | int64 | 12 |
| `_csv_file` | str | 12 |

## `condition_protocols`

Rows: 12

| Column | Dtype | Non-null |
|---|---|---:|
| `condition` | str | 12 |
| `ingredient_name` | str | 12 |
| `recommended_daily_dose` | str | 12 |
| `dose_unit` | str | 12 |
| `priority_rank` | str | 12 |
| `source_name` | str | 12 |
| `source_quote` | str | 12 |
| `source_url` | str | 12 |
| `year` | str | 12 |
| `evidence_type` | str | 12 |
| `_csv_row` | int64 | 12 |
| `_csv_file` | str | 12 |

## `energy_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `energy` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `environmental_matrices`

Rows: 6

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_category` | str | 6 |
| `trait_value` | str | 6 |
| `trait` | str | 6 |
| `climate_context` | str | 6 |
| `dimension` | str | 6 |
| `compatibility_score` | str | 6 |
| `management_note` | str | 6 |
| `source_name` | str | 6 |
| `source_quote` | str | 6 |
| `source_url` | str | 6 |
| `_csv_row` | int64 | 6 |
| `_csv_file` | str | 6 |

## `ext_supplements`

Rows: 0

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 0 |
| `supplement_type` | str | 0 |
| `serving_size_g` | str | 0 |
| `servings_per_pack` | str | 0 |
| `storage_method` | str | 0 |
| `shelf_life_days` | str | 0 |

## `ext_treats_bakery`

Rows: 12

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 12 |
| `treat_type` | str | 12 |
| `bakery_type` | str | 12 |
| `protein_source` | str | 12 |
| `texture` | str | 12 |
| `weight_g` | str | 12 |
| `feeding_recommendation` | str | 12 |
| `storage_method` | str | 12 |
| `shelf_life_days` | str | 12 |
| `_csv_row` | int64 | 12 |
| `_csv_file` | str | 12 |

## `functiongroup_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `function_group` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `grooming_observation_defs`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `observation_key` | str | 10 |
| `label` | str | 10 |
| `normal_criteria` | str | 10 |
| `monitor_criteria` | str | 10 |
| `attention_criteria` | str | 10 |
| `severity_scale` | str | 10 |
| `recommendation_template` | str | 10 |
| `source_csv` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `ingredient_aliases`

Rows: 6

| Column | Dtype | Non-null |
|---|---|---:|
| `canonical_key` | str | 6 |
| `alias_key` | str | 6 |
| `category` | str | 6 |
| `parent_key` | str | 6 |
| `_csv_row` | int64 | 6 |
| `_csv_file` | str | 6 |

## `ingredient_evidence_prev`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `ingredient_name` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `ingredient_evidence_sci`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `ingredient_name` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `supports_joint` | str | 10 |
| `supports_skin` | str | 10 |
| `supports_gut` | str | 10 |
| `anti_inflammatory` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `ingredient_mechanisms`

Rows: 8

| Column | Dtype | Non-null |
|---|---|---:|
| `nutrient_name` | str | 8 |
| `ingredient_name` | str | 8 |
| `source_product_id` | str | 8 |
| `amount_per_serving` | str | 8 |
| `unit` | str | 8 |
| `mechanism_summary` | str | 8 |
| `evidence_level` | str | 8 |
| `_csv_row` | int64 | 8 |
| `_csv_file` | str | 8 |

## `ingredient_nutrient_estimates`

Rows: 8

| Column | Dtype | Non-null |
|---|---|---:|
| `ingredient` | str | 8 |
| `canonical_ingredient` | str | 8 |
| `nutrient` | str | 8 |
| `amount_per_100g` | str | 8 |
| `unit` | str | 8 |
| `confidence` | str | 8 |
| `source` | str | 8 |
| `is_estimated` | str | 8 |
| `category` | str | 8 |
| `parent` | str | 8 |
| `property_tags` | str | 8 |
| `notes` | str | 8 |
| `_csv_row` | int64 | 8 |
| `_csv_file` | str | 8 |

## `lifespan_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `lifespan` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `mixed_breed_interactions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_a` | str | 10 |
| `trait_b` | str | 10 |
| `condition` | str | 10 |
| `interaction` | str | 10 |
| `factor` | str | 10 |
| `reason` | str | 10 |
| `source` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `mixed_breed_matrix`

Rows: 5

| Column | Dtype | Non-null |
|---|---|---:|
| `breed_a` | str | 5 |
| `breed_b` | str | 5 |
| `condition` | str | 5 |
| `factor` | str | 5 |
| `source_name` | str | 5 |
| `source_quote` | str | 5 |
| `source_url` | str | 5 |
| `_csv_row` | int64 | 5 |
| `_csv_file` | str | 5 |

## `natural_food_sources`

Rows: 15

| Column | Dtype | Non-null |
|---|---|---:|
| `ingredient_name` | str | 15 |
| `food_source` | str | 15 |
| `amount_per_100g` | str | 15 |
| `unit` | str | 15 |
| `bioavailability_notes` | str | 15 |
| `_csv_row` | int64 | 15 |
| `_csv_file` | str | 15 |

## `nutrient_priorities`

Rows: 5

| Column | Dtype | Non-null |
|---|---|---:|
| `condition` | str | 5 |
| `nutrient_name` | str | 5 |
| `target_dose` | str | 5 |
| `target_unit` | str | 5 |
| `priority_rank` | str | 5 |
| `evidence_level` | str | 5 |
| `source_name` | str | 5 |
| `source_quote` | str | 5 |
| `source_url` | str | 5 |
| `_csv_row` | int64 | 5 |
| `_csv_file` | str | 5 |

## `package_tiers`

Rows: 3

| Column | Dtype | Non-null |
|---|---|---:|
| `tier_id` | str | 3 |
| `title` | str | 3 |
| `yearly_discount_factor` | str | 3 |
| `staple_product_id` | str | 3 |
| `sort_order` | str | 3 |
| `_csv_row` | int64 | 3 |
| `_csv_file` | str | 3 |

## `product_components`

Rows: 59

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 59 |
| `component_type` | str | 59 |
| `component_name` | str | 59 |
| `value` | str | 59 |
| `unit` | str | 59 |
| `evidence_level` | str | 59 |
| `notes` | str | 59 |
| `_csv_row` | int64 | 59 |
| `_csv_file` | str | 59 |

## `product_defaults`

Rows: 5

| Column | Dtype | Non-null |
|---|---|---:|
| `key` | str | 5 |
| `product_id` | str | 5 |
| `_csv_row` | int64 | 5 |
| `_csv_file` | str | 5 |

## `product_feeding_rules`

Rows: 23

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 23 |
| `min_weight_kg` | str | 23 |
| `max_weight_kg` | str | 23 |
| `daily_amount` | str | 23 |
| `daily_unit` | str | 23 |
| `_csv_row` | int64 | 23 |
| `_csv_file` | str | 23 |

## `product_functions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 10 |
| `function` | str | 10 |
| `confidence` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `product_pricing`

Rows: 16

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 16 |
| `list_price_rmb` | str | 16 |
| `package_units` | str | 16 |
| `unit_label` | str | 16 |
| `_csv_row` | int64 | 16 |
| `_csv_file` | str | 16 |

## `products`

Rows: 16

| Column | Dtype | Non-null |
|---|---|---:|
| `product_id` | str | 16 |
| `brand` | str | 16 |
| `category` | str | 16 |
| `subcategory` | str | 16 |
| `product_name` | str | 16 |
| `status` | str | 16 |
| `image_url` | str | 16 |
| `purchase_url` | str | 16 |
| `description` | str | 16 |
| `short_description` | str | 16 |
| `featured` | str | 16 |
| `tags` | str | 16 |
| `display_order` | str | 16 |
| `inventory_status` | str | 16 |
| `rating` | str | 16 |
| `review_count` | str | 16 |
| `_csv_row` | int64 | 16 |
| `_csv_file` | str | 16 |

## `size_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `size` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `skulltype_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `skull_type` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `trait_attribute_explanations`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_category` | str | 10 |
| `trait_value` | str | 10 |
| `card_title` | str | 10 |
| `explanation` | str | 10 |
| `related_conditions` | str | 10 |
| `evidence_level` | str | 10 |
| `evidence_id` | str | 10 |
| `source_csv` | str | 10 |
| `source_name` | str | 10 |
| `source_url` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `trait_benefits`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_a` | str | 10 |
| `trait_b` | str | 10 |
| `condition` | str | 10 |
| `reduction_factor` | str | 10 |
| `reason` | str | 10 |
| `source` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `trait_contribution_weights`

Rows: 7

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_category` | str | 7 |
| `trait_value` | str | 7 |
| `condition` | str | 7 |
| `risk_delta` | str | 7 |
| `unit` | str | 7 |
| `source_csv` | str | 7 |
| `evidence_id` | str | 7 |
| `mechanism_note` | str | 7 |
| `_csv_row` | int64 | 7 |
| `_csv_file` | str | 7 |

## `trait_interactions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_a` | str | 10 |
| `trait_b` | str | 10 |
| `condition` | str | 10 |
| `interaction` | str | 10 |
| `factor` | str | 10 |
| `reason` | str | 10 |
| `source` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |

## `trait_purposes`

Rows: 5

| Column | Dtype | Non-null |
|---|---|---:|
| `trait_category` | str | 5 |
| `trait_value` | str | 5 |
| `biological_purpose` | str | 5 |
| `advantage_summary` | str | 5 |
| `source_name` | str | 5 |
| `source_quote` | str | 5 |
| `source_url` | str | 5 |
| `_csv_row` | int64 | 5 |
| `_csv_file` | str | 5 |

## `weaknessgroup_conditions`

Rows: 10

| Column | Dtype | Non-null |
|---|---|---:|
| `weakness_group` | str | 10 |
| `condition` | str | 10 |
| `prevalence` | str | 10 |
| `sample_population` | str | 10 |
| `sample_size` | str | 10 |
| `source_name` | str | 10 |
| `source_quote` | str | 10 |
| `source_url` | str | 10 |
| `year` | str | 10 |
| `confidence_level` | str | 10 |
| `_csv_row` | int64 | 10 |
| `_csv_file` | str | 10 |
