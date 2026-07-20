# Formula Stability Report

Generated: `2026-07-20T21:58:06.300268+00:00`

| Formula | Version | Tables | Consumers | Module |
|---|---|---|---|---|
| `PROFILE_V1` | 2.1.0 | — | breed, biology, risk | `app.agent.nodes.profile_node` |
| `BREED_RESOLVE_V1` | 2.1.0 | breeds, breed_aliases | biology, risk | `app.agent.nodes.breed_node` |
| `BIOLOGY_V2_1` | 2.1.0 | breeds, trait_purposes, environmental_matrices | risk, epidemiology, assessment | `app.agent.nodes.biology_node` |
| `RISK_V2_1` | 2.1.0 | breed_conditions, size_conditions, bodytype_conditions, coattype_conditions, energy_conditions, skulltype_conditions, climate_conditions, lifespan_conditions, functiongroup_conditions, weaknessgroup_conditions, trait_interactions, trait_benefits, mixed_breed_matrix | epidemiology, nutrition, ingredient, packages, assessment, validation | `app.agent.nodes.risk_node` |
| `EPIDEMIOLOGY_V2_1` | 2.1.0 | breed_conditions, trait_condition tables | activity, nutrition | `app.agent.nodes.epidemiology_node` |
| `ACTIVITY_V2_1` | 2.1.0 | condition_activities | assessment, export | `app.agent.nodes.activity_node` |
| `GROOMING_V1` | 2.1.0 | grooming_observation_defs | assessment, report | `app.agent.nodes.grooming_node` |
| `NUTRITION_V2_1` | 2.1.0 | condition_ingredients | ingredient, product, export | `app.agent.nodes.nutrition_node` |
| `NUTRIENT_TARGET_V2_1` | 2.1.0 | condition_ingredients, ingredient_evidence, ingredient_mechanisms | product, package, export, evidence | `app.agent.nodes.ingredient_node` |
| `PRODUCT_MATCH_V2_1` | 2.1.0 | products, product_components, product_pricing, product_feeding_rules | package, report, export | `app.agent.nodes.product_node` |
| `PACKAGE_OPTIMIZER_V2_1` | 2.1.0 | package_tiers | export, assessment | `app.agent.nodes.package_node` |
| `ASSESSMENT_PROJECT_V1` | 2.1.0 | — | export, validation | `app.agent.nodes.assessment_node` |
| `REPORT_V1` | 2.1.0 | — | export | `app.agent.nodes.report_node` |
| `CONFIDENCE_V1` | 2.1.0 | — | validation, trace | `app.agent.nodes.confidence_node` |
| `EVIDENCE_V1` | 2.1.0 | ingredient_evidence, clinical_evidence_base | validation, trace | `app.agent.nodes.evidence_node` |
| `VALIDATION_V1` | 2.1.0 | — | export, trace | `app.agent.nodes.validation_node` |
| `TRACE_V1` | 2.1.0 | — | export | `app.agent.nodes.trace_node` |
| `EXPORT_LEGACY_V1` | 2.1.0 | — | api, frontend, validation_console | `app.agent.nodes.export_node` |

## Execution Order

1. `profile`
2. `breed`
3. `biology`
4. `grooming`
5. `risk`
6. `confidence`
7. `epidemiology`
8. `activity`
9. `nutrition`
10. `ingredient`
11. `evidence`
12. `product`
13. `package`
14. `assessment`
15. `report`
16. `validation`
17. `trace`
18. `export`
