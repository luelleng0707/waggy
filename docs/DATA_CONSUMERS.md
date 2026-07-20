# Data Consumers

**Status:** Blast-radius reference for the **current** runtime  
**Rule:** Changing a table affects every checked consumer. Prefer adapters over silent path changes.

Legend: **R** = reads · **—** = does not use · **U** = loaded but unused accessor · **I** = opt-in / tests only

---

## Engine / stage matrix

| Table (manifest) | Bio | Risk | Epi | Mgmt | Nutr | Optim | Assembler | Reports | API | Console |
|------------------|-----|------|-----|------|------|-------|-----------|---------|-----|---------|
| `breeds` | R | R | — | — | — | — | R | R | R | R |
| `breed_aliases` | R | R | — | — | — | — | — | — | — | R |
| `breed_conditions` | — | R | R | — | — | — | R | R | R | R |
| `size_conditions` … `lifespan_conditions` (×9) | — | R | R | — | — | — | — | — | — | R |
| `trait_interactions` | — | R | R | — | — | — | — | R | — | R |
| `trait_benefits` | — | R | — | — | — | — | — | — | — | R |
| `mixed_breed_matrix` | — | R | R | — | — | — | — | — | — | R |
| `mixed_breed_interactions` | U | U | U | U | U | U | U | U | U | R |
| `trait_purposes` | R | — | — | — | — | — | — | R | — | R |
| `environmental_matrices` | R | — | — | — | — | — | — | R | — | R |
| `trait_attribute_explanations` | — | — | — | — | — | — | — | R | — | R |
| `trait_contribution_weights` | — | — | — | — | — | — | — | R | — | R |
| `clinical_risk_timeline` | — | — | — | — | — | — | — | R | — | R |
| `clinical_evidence_base` | — | — | — | — | — | — | — | R | — | R |
| `condition_activities` | — | — | — | R | — | — | R | — | — | R |
| `activity_prescription_rules` | — | — | — | — | — | — | — | R | — | R |
| `activity_evidence` | U | U | U | U | U | U | U | U | U | R |
| `grooming_observation_defs` | — | — | — | — | — | — | — | R | — | R |
| `condition_ingredients_sci` | — | — | — | — | R | R | R | — | R | R |
| `condition_ingredients_prev` | — | — | — | — | R | R | R | — | R | R |
| `nutrient_priorities` | — | — | — | — | — | — | R | — | — | R |
| `condition_protocols` | U | U | U | U | U | U | U | mention | U | R |
| `ingredient_evidence_sci` | — | — | — | — | — | — | R | — | R | R |
| `ingredient_evidence_prev` | — | — | — | — | — | — | R | — | R | R |
| `ingredient_mechanisms` | — | — | — | — | — | — | R | — | — | R |
| `natural_food_sources` | — | — | — | — | — | — | R | — | — | R |
| `ingredient_aliases` | — | — | — | — | — | R | — | — | — | R |
| `ingredient_nutrient_estimates` | I | I | I | I | I | I | I | I | I | R |
| `products` | — | — | — | — | — | R | R | R | R | R |
| `product_pricing` | — | — | — | — | — | R | R | — | R | R |
| `product_components` | — | — | — | — | — | R | R | — | R | R |
| `product_feeding_rules` | — | — | — | — | — | R | R | — | R | R |
| `product_functions` | — | — | — | — | — | R | — | — | R | R |
| `ext_supplements` | — | — | — | — | — | R | R | — | R | R |
| `ext_treats_bakery` | — | — | — | — | — | R | R | — | R | R |
| `package_tiers` | — | — | — | — | — | R | R | — | — | R |
| `product_defaults` | U | U | U | U | U | U | U | U | U | R |
| `STAPLE_FOOD` / `TREATS` (unmanifested) | — | — | — | — | — | — | — | — | — | — |

Column abbreviations: Bio=`biological` · Risk=`health_risk` · Epi=`epidemiology` · Mgmt=management · Nutr=`nutrition` · Optim=`optimization`/`package_optimizer` · Reports=`report_generator`/`clinical_report_builder` · API=store/catalog/evidence routes · Console=Validation Console / repository browser

---

## Module → tables (detail)

### `app/agent/stages/biological.py`
`breeds`, `breed_aliases` (via normalize), `trait_purposes`, `environmental_matrices`

### `app/agent/stages/health_risk.py`
`breeds`, trait `*_conditions` (×9), `breed_conditions`, `trait_interactions`, `trait_benefits`, `mixed_breed_matrix`

### `app/agent/stages/epidemiology.py`
`breed_conditions`, trait conditions, `trait_interactions`, `mixed_breed_matrix`

### `app/agent/stages/nutrition.py` + `ingredient_engine`
Merged `condition_ingredients_*`, evidence tables, mechanisms (indirect)

### `app/agent/package_optimizer.py` + `stages/optimization.py`
`products`, `product_pricing`, `product_components`, `product_feeding_rules`, `product_functions`, `ext_*`, `package_tiers`, `ingredient_aliases`

### `app/agent/response_assembler.py`
Insights/packages/targets/evidence assembly; reads nutrition priorities, natural foods, mechanisms, activities

### `app/data/report_generator.py` / `clinical_report_builder.py`
Trait narratives, contribution weights, timeline, evidence base, grooming, activity prescriptions

### Frontend
**Does not load CSVs.** Consumes analyze / assess / store JSON only. Demo may mention missing feeding/component fields in copy.

### Validation Console
Reads all manifested tables via repository browser; projects analyze.debug / pipeline_trace for lookups.

---

## Change blast radius (examples)

| If you change… | Highest risk consumers |
|----------------|------------------------|
| `BREED_CONDITIONS.prevalence` | Risk ranking, evidence API, reports, goldens |
| Any trait `*_CONDITIONS` | Risk + epidemiology + parity |
| `CONDITION_INGREDIENTS` (sci **or** prev) | Nutrition targets, packages, coverage |
| `PRODUCT_COMPONENTS` | Optimizer, coverage, store API |
| `PACKAGE_TIERS` | Staple selection, costs |
| `INGREDIENT_ALIASES` | Coverage matching (silent miss if wrong) |
| `CLINICAL_EVIDENCE_BASE` | Reports only (not risk math) |

---

## Related

[DATA_DICTIONARY.md](DATA_DICTIONARY.md) · [DATA_RELATIONSHIPS.md](DATA_RELATIONSHIPS.md) · [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md)

