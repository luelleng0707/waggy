# Formula Reference

Generated: `2026-07-20T22:13:36.005040+00:00`

## `PROFILE_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.profile_node`
- Tables: —

## `BREED_RESOLVE_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.breed_node`
- Tables: breeds, breed_aliases

## `BIOLOGY_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.biology_node`
- Tables: breeds, trait_purposes, environmental_matrices

## `RISK_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.risk_node`
- Wraps: `app.agent.stages.health_risk.compute_risks`
- Tables: breed_conditions, size_conditions, bodytype_conditions, coattype_conditions, energy_conditions, skulltype_conditions, climate_conditions, lifespan_conditions, functiongroup_conditions, weaknessgroup_conditions, trait_interactions, trait_benefits, mixed_breed_matrix

## `EPIDEMIOLOGY_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.epidemiology_node`
- Wraps: `app.agent.stages.epidemiology.run_epidemiology_stage`
- Tables: breed_conditions, trait_condition tables

## `ACTIVITY_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.activity_node`
- Tables: condition_activities

## `GROOMING_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.grooming_node`
- Tables: grooming_observation_defs

## `NUTRITION_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.nutrition_node`
- Wraps: `app.agent.stages.nutrition.run_nutrition_stage`
- Tables: condition_ingredients

## `NUTRIENT_TARGET_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.ingredient_node`
- Wraps: `app.agent.ingredient_engine.map_ingredients`
- Tables: condition_ingredients, ingredient_evidence, ingredient_mechanisms

## `PRODUCT_MATCH_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.product_node`
- Wraps: `app.agent.stages.optimization.run_optimization_stage`
- Tables: products, product_components, product_pricing, product_feeding_rules

## `PACKAGE_OPTIMIZER_V2_1`

- Version: 2.1.0
- Module: `app.agent.nodes.package_node`
- Tables: package_tiers

## `ASSESSMENT_PROJECT_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.assessment_node`
- Tables: —

## `REPORT_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.report_node`
- Tables: —

## `CONFIDENCE_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.confidence_node`
- Tables: —

## `EVIDENCE_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.evidence_node`
- Tables: ingredient_evidence, clinical_evidence_base

## `VALIDATION_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.validation_node`
- Tables: —

## `TRACE_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.trace_node`
- Tables: —

## `EXPORT_LEGACY_V1`

- Version: 2.1.0
- Module: `app.agent.nodes.export_node`
- Wraps: `app.agent.response_assembler.assemble_frontend_response`
- Tables: —
