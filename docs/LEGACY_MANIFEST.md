# LEGACY MANIFEST

Repository-wide file classification for Omega 1.1 cutover.

| file path | category | reason | dependencies | replacement | safe to archive? | notes |
|---|---|---|---|---|---|---|
| .env.example | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| .gitignore | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| .python-version | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| .streamlit/config.toml | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| CANONICAL_SCIENTIFIC_FACT_WAREHOUSE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| PROJECT_ARCHITECTURE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| Procfile | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| README.md | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| SCIENTIFIC_DISCOVERY_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| app.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| app/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/assessment_agent.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/assessment_result.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/bundle_engine.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/calculation_trace.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/condition_lookup.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/engine.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/execution_context.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/formula_graph.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/formula_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/formula_registry.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/formula_trace.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/ingredient_engine.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/legacy_compat.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/activity_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/assessment_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/biology_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/breed_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/confidence_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/epidemiology_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/evidence_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/export_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/grooming_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/ingredient_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/nutrition_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/package_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/product_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/profile_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/report_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/risk_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/trace_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/nodes/validation_node.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/package_detail.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/package_optimizer.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/pipeline_trace.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/response_assembler.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/stages/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/stages/biological.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/stages/epidemiology.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/stages/health_risk.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/stages/nutrition.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/stages/optimization.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/state.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/utils.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/variable_map.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/version.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/agent/wellness_map.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/api/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/api/evidence.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/api/main.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/api/payload_adapter.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/core/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/core/paths.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/assessment_diff.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/cache.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/clinical_assessment.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/clinical_report_builder.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/console_inspectors.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/debug_boot.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/debug_presets.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/debug_repository_browser.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/engine_trace.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/loader.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/native_loader.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/report_generator.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/report_models.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/report_schema.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/repository.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/runtime.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/schemas.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/validation_console.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/validators.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/ingredients.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/legacy.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/materialize.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/papers.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/parameters.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/parity.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/platform.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/repository.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/traits.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/warehouse/units.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/data/watcher.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/debug/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/debug/clinical_execution_debug.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/stages/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/stages/biological.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/stages/epidemiology.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/stages/health_risk.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/stages/nutrition.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/formulas/stages/optimization.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/breed.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/confidence.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/config.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/explanation.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/formula_registry.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/ingredient.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/models.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/nutrition.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/resolver.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/risk.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/inference/score.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/main.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/attach.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/audit.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/builder.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/confidence.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/coverage.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/diff_engine.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/explanations.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/graph.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/models.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/repository.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/validator.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/science/versioning.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/demo_app.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/__init__.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/diary.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/formatters.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/home.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/journey.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/navigation.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/template_engine.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/view_models.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/renderer/wellness.py | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/static/css/.gitkeep | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/static/icons/.gitkeep | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/static/images/.gitkeep | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/static/js/.gitkeep | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/base/app_styles.css | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/diary_section.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/dog_profile_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/evidence_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/feeding_option.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/ingredient_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/macros.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/nutrition_priority_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/nutrition_row.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/package_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/product_row.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/trait_benefit_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/trait_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/trait_weakness_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/components/wellness_recommendation_card.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/diary/page.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/home/journey.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/wellness/nutrition_report.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/wellness/package_detail.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| app/ui/templates/wellness/product_analysis.html | TRANSITIONAL | legacy runtime still referenced in historical tests/docs | legacy path references | repository/* target layers | No | Needs staged migration; not archived yet |
| archive/README.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/css/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv.zip | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/ACTIVITY_EVIDENCE.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/BODYTYPE_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/BREEDS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/BREED_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/CLIMATE_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/CONDITION_ACTIVITIES.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/CONDITION_INGREDIENTS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/ENERGY_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/FUNCTIONGROUP_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/HOMESTYLE_BAKERY.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/INGREDIENT_EVIDENCE.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/LIFESPAN_CONDITIONS(1).csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/LIFESPAN_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/MIXED_BREED_INTERACTIONS(1)(1).csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/MIXED_BREED_INTERACTIONS(1).csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/MIXED_BREED_INTERACTIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/MIXED_BREED_MATRIX.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/PRODUCTS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/PRODUCT_ACTIVE_INGREDIENTS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/PRODUCT_FEEDING_RULES.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/PRODUCT_FUNCTIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/PRODUCT_PRICING.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/SIZE_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/SKULLTYPE_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/STAPLE_FOOD.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/SUPPLEMENTS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/TRAIT_BENEFITS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/TREATS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/data/legacy-parity-csv/WEAKNESSGROUP_CONDITIONS.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/CLINICAL_REPORT_V3.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/CLINICAL_REPORT_V4.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/FINAL_UI_POLISH_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/FRONTEND_ARCHITECTURE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/FRONTEND_DATA_INTEGRATION_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/FRONTEND_LAYOUT_SPEC.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/LEGACY_NODE_REFERENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE11_PACKAGE_ENGINE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE12_VALIDATION_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE13_UX.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE14_EMBEDDED_SHEETS.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE15_PRESENTATION.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE18_PRODUCT_EXPERIENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PHASE_17_5.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_ALGORITHM.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_ALGORITHM_VERSIONING.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_CSV_MAP.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_DATA_PLATFORM.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_FINAL_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_FRONTEND_QA_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_IMPORT_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_MIGRATION_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PPIE_RESPONSE_SCHEMA.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/PYTHON_AGENT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/RELEASE_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/SHOP_STOREFRONT_BINDING_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/SHOP_UI_REMOVAL_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/docs/UI_STANDARDIZATION_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/activity_card.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/base.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/condition_card.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/detail_block.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/evidence_trace.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/metric_card.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/nav_status.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/page_title.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/section_divider.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/section_title.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/html/jinja-orphans/sidebar_header.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/javascript/care-recommendation.js | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/javascript/clinical-report.js | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/border_collie/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/chihuahua/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/dolly_golden_x_labrador/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/french_bulldog/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/german_shepherd_dog/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/great_pyrenees_giant/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/mixed_chow_x_rural/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/overweight_labrador/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/puppy_golden/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/js_responses/senior_labrador/js_response.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/legacy-parity/prisma/schema.prisma | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/python/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/python/tools/import_audit_scan.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| archive/tests/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| authoring/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/__main__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/builder.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-0140bb7711.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-0dae669195.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-1028ed62b8.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-1094c418bd.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-129bd9c068.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-1b25c581a2.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-1f7cbdc5c9.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-24d0388dff.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-29ab489b53.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-2f2735093a.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-3a65ff44bb.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-41f737765e.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-5ab71769bd.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-5ff1fea851.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-63a2f44caf.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-7436284cb8.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-823e66ef7f.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-8640919d10.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-9eb5049221.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-a630246c9b.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-b2a2364c5a.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-c872f02df6.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-d559816c1e.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-dc6f6260da.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-ea89aed9d4.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-f6c5feaf0c.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/drafts/draft-f95c717002.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/explorer.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/ml_sandbox.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/models.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/pipeline.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/portal.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-0dae669195.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-1028ed62b8.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-1b25c581a2.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-1f7cbdc5c9.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-2f2735093a.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-41f737765e.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-5ab71769bd.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-5ff1fea851.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-823e66ef7f.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-8640919d10.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-9eb5049221.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-d559816c1e.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-dc6f6260da.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/published/draft-f95c717002.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/research.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/studio/explorer.html | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/studio/explorer_data.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/studio/ml_sandbox/README.md | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/studio/ml_sandbox/SUGGESTIONS.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| authoring/templates/evidence_entry.template.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| catalog-service.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| config/__init__.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| config/settings.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| curation/conflict_resolution.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| curation/duplicate_detection.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| curation/evidence_ranking.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| curation/reports/CONFLICTS.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| curation/reports/DUPLICATES.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| curation/reports/EVIDENCE_RANKING.md | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/README.md | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/1_biological_traits/BREEDS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/1_biological_traits/BREED_ALIASES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/2_evolutionary_profiles/TRAIT_ATTRIBUTE_EXPLANATIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/CLIMATE_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/CLINICAL_RISK_TIMELINE.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/ENERGY_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/FUNCTIONGROUP_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/LIFESPAN_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/SIZE_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/SKULLTYPE_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/TRAIT_CONTRIBUTION_WEIGHTS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/3_management_considerations/WEAKNESSGROUP_CONDITIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/4_preventative_interventions/ACTIVITY_PRESCRIPTION_RULES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/4_preventative_interventions/GROOMING_OBSERVATION_DEFS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/CLINICAL_EVIDENCE_BASE.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/INGREDIENT_ALIASES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/INGREDIENT_NUTRIENT_ESTIMATES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/manifest.yaml | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/preventative_ingredients/CONDITION_INGREDIENTS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/preventative_ingredients/CONDITION_PROTOCOLS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/preventative_ingredients/INGREDIENT_EVIDENCE.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/EXT_SUPPLEMENTS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/EXT_TREATS_BAKERY.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PACKAGE_TIERS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PRODUCT_CATALOG.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PRODUCT_COMPONENTS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PRODUCT_DEFAULTS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PRODUCT_FEEDING_RULES.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PRODUCT_FUNCTIONS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/PRODUCT_PRICING.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/STAPLE_FOOD.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| data/product_portfolio/TREATS.csv | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| debug/calculation.html | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| developer_tools/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/benchmarking/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/benchmarking/suite.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/dashboards/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/dashboards/generators.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/dashboards/html_dashboard.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/dashboards/index.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/diagnostics/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/profiling/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/research/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| developer_tools/research/queries.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| docs/API.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/API_REFERENCE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/ARCHITECTURE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/BACKEND_ARCHITECTURE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/CHANGELOG.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/CONTRIBUTING.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_ARCHITECTURE_REVIEW.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_ARCHITECTURE_V2.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_CONSUMERS.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_DICTIONARY.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_DUPLICATION_REPORT.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_MIGRATION_V2.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_NORMALIZATION.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_PIPELINE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DATA_RELATIONSHIPS.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DEBUGGING.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/DEVELOPER_GUIDE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FILES_DELETED.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FILES_MERGED.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FINAL_DOCUMENTATION.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FINAL_RUNTIME.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FOLDER_USAGE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FORMULAS.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/FORMULA_REFERENCE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/GRAPH_REFERENCE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/MINIMAL_PROJECT_TREE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/PROJECT_SIZE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/PROJECT_STATUS.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/PROJECT_STRUCTURE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/RAILWAY_DEPLOYMENT.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/README.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/ROADMAP.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/RUNTIME_DEPENDENCIES.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/RUNTIME_PIPELINE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/SCIENCE_MODEL.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/SCIENCE_REFERENCE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/SYSTEM_ARCHITECTURE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/WAREHOUSE_GUIDE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/WAREHOUSE_REFERENCE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/architecture/OMEGA_COMPLETE.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/architecture/PHASE5.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/architecture/PHASE_OMEGA.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/governance/PHASE5.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/onboarding/PHASE5.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/science/PHASE5.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| docs/validation_report.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| governance/README.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/changelogs/CHANGELOG.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/releases/2026.07.20.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/releases/TAG_2026.07.20.txt | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/BENCHMARK_REPORT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/BENCHMARK_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/DATA_HEALTH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/FORMULA_STABILITY_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/PERFORMANCE_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/RELEASE_SUMMARY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/RELEASE_SUMMARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/SCIENTIFIC_IMPACT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/SCIENTIFIC_IMPACT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/data_health.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/formula_stability.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/reports/performance_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/review/CHECKLIST.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/validation/SCIENCE_VALIDATION_REPORT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| governance/validation/SCIENCE_VALIDATION_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| index.html | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| legacy/README.md | ACTIVE | already archived material | none | n/a | n/a |  |
| meta/architecture/API_REFERENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/API_STABILITY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/API_STABILITY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/ARCHITECTURE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/DATA_DICTIONARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/DEPENDENCY_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/FORMULA_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/KNOWLEDGE_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/OMEGA_SUMMARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/PERFORMANCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/QUALITY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/RELEASE_HISTORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/SCIENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/SECURITY_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/architecture/WAREHOUSE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/dependency_graph/DEPENDENCY_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/dependency_graph/DEPENDENCY_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/inventories/formulas.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/FORMULA_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/FORMULA_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/OMEGA_SUMMARY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/PERFORMANCE_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/PERFORMANCE_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/SCIENCE_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/SCIENCE_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/SYSTEM_RUNTIME.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| meta/metrics/SYSTEM_RUNTIME.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| nixpacks.toml | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| ontology/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ontology/anatomy/anatomy_index.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ontology/condition_graph/CONDITION_ONTOLOGY.md | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ontology/condition_graph/conditions.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ontology/ingredient_graph/ingredients.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ontology/physiology/physiology_index.json | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| operations/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/lifecycle.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/migration/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/SNAPSHOT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/API_REFERENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/API_STABILITY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/API_STABILITY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/ARCHITECTURE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/DATA_DICTIONARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/DEPENDENCY_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/FORMULA_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/KNOWLEDGE_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/PERFORMANCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/QUALITY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/RELEASE_HISTORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/SCIENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/SECURITY_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/architecture/WAREHOUSE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/BENCHMARK_REPORT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/BENCHMARK_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/DATA_HEALTH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/FORMULA_STABILITY_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/PERFORMANCE_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/RELEASE_SUMMARY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/RELEASE_SUMMARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/SCIENTIFIC_IMPACT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/SCIENTIFIC_IMPACT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/data_health.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/formula_stability.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/docs/reports/performance_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/formula_registry.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/SCIENTIFIC_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/coverage_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/data_validation.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/duplicate_detection.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/activity_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/assembler.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/ingredient_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/nutrition_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/package_optimizer.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/formula_trace/risk_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/knowledge_coverage.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/migration_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/phase2_parity_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/scientific_audit.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/unused_columns.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/generated/warehouse_mapping.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/graph/edges.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/graph/nodes.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/graph/summary.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/activities.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/body_sizes.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/body_types.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/breeds.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/climates.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/coat_types.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/conditions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/foods.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/ingredients.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/nutrients.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/papers.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/prevention_methods.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/skull_types.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/reference/traits.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/aliases.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/activity_evidence.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/activity_prescription_rules.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/breed_aliases.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/breeds.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/clinical_evidence_base.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/clinical_risk_timeline.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_activities.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_ingredients_prev.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_ingredients_sci.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/condition_protocols.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/environmental_matrices.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ext_supplements.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ext_treats_bakery.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/grooming_observation_defs.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_aliases.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_evidence_prev.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_evidence_sci.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_mechanisms.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/mixed_breed_interactions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/mixed_breed_matrix.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/natural_food_sources.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/nutrient_priorities.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/package_tiers.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_components.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_defaults.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_feeding_rules.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_functions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/product_pricing.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/products.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_attribute_explanations.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_benefits.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_contribution_weights.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_interactions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/legacy_mirror/trait_purposes.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/lookup_maps.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/parameter_defaults.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/runtime/unit_conversion.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/breed_condition_risk.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/food_nutrients.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/ingredient_evidence.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/ingredient_food_sources.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/mixed_trait_interactions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/nutrient_targets.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/prevention_effectiveness.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/product_composition.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-omega/warehouse/science/trait_condition_risk.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/SNAPSHOT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/API_REFERENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/API_STABILITY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/API_STABILITY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/ARCHITECTURE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/DATA_DICTIONARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/DEPENDENCY_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/FORMULA_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/KNOWLEDGE_GRAPH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/OMEGA_SUMMARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/PERFORMANCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/QUALITY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/RELEASE_HISTORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/SCIENCE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/SECURITY_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/architecture/WAREHOUSE.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/BENCHMARK_REPORT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/BENCHMARK_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/DATA_HEALTH.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/FORMULA_STABILITY_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/PERFORMANCE_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/RELEASE_SUMMARY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/RELEASE_SUMMARY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/SCIENTIFIC_IMPACT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/SCIENTIFIC_IMPACT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/data_health.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/formula_stability.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/docs/reports/performance_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/formula_registry.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/SCIENTIFIC_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/coverage_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/data_validation.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/duplicate_detection.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/formula_trace/activity_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/formula_trace/assembler.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/formula_trace/ingredient_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/formula_trace/nutrition_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/formula_trace/package_optimizer.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/formula_trace/risk_engine.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/knowledge_coverage.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/migration_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/phase2_parity_report.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/scientific_audit.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/unused_columns.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/generated/warehouse_mapping.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/graph/edges.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/graph/nodes.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/graph/summary.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/activities.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/body_sizes.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/body_types.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/breeds.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/climates.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/coat_types.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/conditions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/foods.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/ingredients.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/nutrients.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/papers.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/prevention_methods.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/skull_types.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/reference/traits.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/aliases.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/activity_evidence.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/activity_prescription_rules.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/breed_aliases.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/breeds.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/clinical_evidence_base.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/clinical_risk_timeline.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/condition_activities.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/condition_ingredients_prev.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/condition_ingredients_sci.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/condition_protocols.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/environmental_matrices.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ext_supplements.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ext_treats_bakery.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/grooming_observation_defs.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ingredient_aliases.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ingredient_evidence_prev.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ingredient_evidence_sci.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ingredient_mechanisms.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/mixed_breed_interactions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/mixed_breed_matrix.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/natural_food_sources.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/nutrient_priorities.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/package_tiers.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/product_components.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/product_defaults.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/product_feeding_rules.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/product_functions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/product_pricing.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/products.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/trait_attribute_explanations.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/trait_benefits.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/trait_contribution_weights.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/trait_interactions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/legacy_mirror/trait_purposes.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/lookup_maps.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/parameter_defaults.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/runtime/unit_conversion.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/breed_condition_risk.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/food_nutrients.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/ingredient_evidence.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/ingredient_food_sources.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/mixed_trait_interactions.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/nutrient_targets.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/prevention_effectiveness.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/product_composition.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| operations/snapshots/2026.07.20-test-omega/warehouse/science/trait_condition_risk.csv | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| package.json | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| platform/README.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie-dev-menu.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie-sheets.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie-shell.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie-trace.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie-ui.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie-validation-console.css | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie-validation-console.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| ppie_platform/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/__main__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/dashboard/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/dashboard/build.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/dashboard/index.html | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/deployment/ARTIFACT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/lifecycle/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/lifecycle/docs.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/common.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/observatories.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/DEPENDENCY_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/DEPENDENCY_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/FORMULA_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/FORMULA_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/PERFORMANCE_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/PERFORMANCE_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/SCIENCE_OBSERVATORY.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/SCIENCE_OBSERVATORY.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/SYSTEM_RUNTIME.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/observability/reports/SYSTEM_RUNTIME.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/omega.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/plugins/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/plugins/sdk.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/sdk/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/sdk/generate.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/sdk/generated/client.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/sdk/generated/openapi.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/sdk/generated/ppie.d.ts | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/sdk/generated/schemas.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/security/SECURITY_AUDIT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/security/SECURITY_AUDIT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/security/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/security/audit.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/status.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| ppie_platform/telemetry/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| pytest.ini | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| quality/__init__.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/regression/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/FAILURE_SIMULATION.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/FAILURE_SIMULATION.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/FUZZ_REPORT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/FUZZ_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/MUTATION_REPORT.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/MUTATION_REPORT.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/SYNTHETIC_POPULATION.json | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/reports/SYNTHETIC_POPULATION.md | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/stress/.gitkeep | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| quality/suites.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| railway.json | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| report-renderer.js | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| repository/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/api/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/docs/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/__init__.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/biology/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/biology/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/biology/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/biology/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/epidemiology/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/epidemiology/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/epidemiology/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/epidemiology/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/estimation/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/estimation/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/estimation/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/estimation/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/explainability/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/explainability/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/explainability/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/explainability/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/nutrition/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/nutrition/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/nutrition/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/nutrition/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/optimization/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/optimization/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/optimization/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/optimization/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/prevention/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/prevention/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/prevention/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/prevention/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/products/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/products/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/products/models.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/engine/products/service.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/frontend/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/models/__init__.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/models/explainability.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/models/runtime.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/models/trace.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/pipeline/__init__.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/pipeline/interfaces.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/pipeline/orchestrator.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/pipeline/stage_order.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/scripts/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/tests/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/warehouse/__init__.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/warehouse/commercial/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/warehouse/reference/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/warehouse/science/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| repository/warehouse/warehouse_interface.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| requirements.txt | TRANSITIONAL | project root config/doc entrypoint | various | v2 docs/scripts | No |  |
| run_demo.ps1 | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| run_demo.sh | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| science_pipeline/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/__main__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/ingestion/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/ingestion/provenance.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/normalization/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/provenance.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/publishing/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/publishing/release_ops.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/release.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/release_ops.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/snapshots/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/validation/__init__.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/validation/extended.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/validation/impact.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| science_pipeline/validation_extended.py | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| scripts/validate_warehouse.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| styles.css | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| tests/api/test_api_architecture_placeholder.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/engine/test_engine_layer_boundaries.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/README.md | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/border_collie.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/chihuahua.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/dolly.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/french_bulldog.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/german_shepherd.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/great_pyrenees.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/mixed_chow.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/overweight_labrador.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/puppy_golden.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/senior_labrador.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/golden/suite_summary.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/border_collie/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/border_collie/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/border_collie/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/chihuahua/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/chihuahua/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/chihuahua/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/dolly_golden_x_labrador/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/dolly_golden_x_labrador/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/dolly_golden_x_labrador/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/french_bulldog/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/french_bulldog/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/french_bulldog/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/german_shepherd_dog/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/german_shepherd_dog/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/german_shepherd_dog/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/great_pyrenees_giant/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/great_pyrenees_giant/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/great_pyrenees_giant/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/mixed_chow_x_rural/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/mixed_chow_x_rural/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/mixed_chow_x_rural/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/overweight_labrador/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/overweight_labrador/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/overweight_labrador/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/puppy_golden/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/puppy_golden/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/puppy_golden/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/senior_labrador/golden_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/senior_labrador/parity_diff.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/senior_labrador/py_response.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/summary.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/summary_run_1.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/summary_run_2.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/parity/summary_run_3.json | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_agent_pipeline.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_clinical_assessment.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_clinical_report.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_engine_trace.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_formula_graph.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_inference_layer.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_inference_parity.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_package_optimizer.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_phase5_governance.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_phase6_authoring.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_phase_omega.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_science_graph.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_standard_report.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_ui_templates.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_validation_console.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_validation_console_live.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/test_warehouse_parity.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| tests/warehouse/test_warehouse_interface.py | TRANSITIONAL | supporting tests/docs/scripts for cutover | various | repository/* | No |  |
| theme.css | LEGACY | prototype/experimental or superseded by v2 layers | none in v2 path | repository/* or warehouse/* | Yes | Archive in Omega 1.1 |
| tools/clean_clone_smoke.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| tools/gen_data_dictionary_tables.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| tools/parity_harness.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| tools/parity_suite.py | UNKNOWN | manual review required | unknown | unknown | Maybe |  |
| warehouse/CANONICAL_MANIFEST.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/DATA_MIGRATION_PLAN.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/DOMAIN_REGISTRY.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/MIGRATION_REPORT.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/MIGRATION_SUMMARY.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/VALIDATION_SUMMARY.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/WAREHOUSE_GUIDE.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/breed_traits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/environment_facts.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/life_stage_health_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/observed_breed_conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/size_risk_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/biology/trait_condition_associations.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_declared_nutrition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_feeding_guide.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_functions_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_master.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_pricing_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_recipe.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/commercial/product_recipe_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/current/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/current/release.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/SCIENTIFIC_AUDIT.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/coverage_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/ACTIVITY_EVIDENCE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/ACTIVITY_PRESCRIPTION_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/BODYTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/BREEDS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/BREED_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/BREED_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CLIMATE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CLINICAL_EVIDENCE_BASE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CLINICAL_RISK_TIMELINE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/COATTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CONDITION_ACTIVITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/CONDITION_PROTOCOLS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/ENERGY_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/ENVIRONMENTAL_MATRICES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/EXT_SUPPLEMENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/EXT_TREATS_BAKERY.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/FUNCTIONGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/GROOMING_OBSERVATION_DEFS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/INGREDIENT_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/INGREDIENT_MECHANISMS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/INGREDIENT_NUTRIENT_ESTIMATES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/LIFESPAN_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/MIXED_BREED_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/MIXED_BREED_MATRIX.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/NATURAL_FOOD_SOURCES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/NUTRIENT_PRIORITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PACKAGE_TIERS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PRODUCT_CATALOG.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PRODUCT_COMPONENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PRODUCT_DEFAULTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PRODUCT_FEEDING_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PRODUCT_FUNCTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/PRODUCT_PRICING.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/SIZE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/SKULLTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/STAPLE_FOOD.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/TRAIT_ATTRIBUTE_EXPLANATIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/TRAIT_BENEFITS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/TRAIT_CONTRIBUTION_WEIGHTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/TRAIT_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/TRAIT_PURPOSES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/TREATS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/csv_analysis/WEAKNESSGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/data_validation.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/duplicate_detection.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/formula_trace/activity_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/formula_trace/assembler.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/formula_trace/ingredient_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/formula_trace/nutrition_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/formula_trace/package_optimizer.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/formula_trace/risk_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/knowledge_coverage.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/migration_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/phase2_parity_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/scientific_audit.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/unused_columns.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/generated/warehouse_mapping.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/graph/edges.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/graph/nodes.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/graph/summary.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/body_sizes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/body_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/climates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/coat_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/foods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/papers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/prevention_methods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/skull_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/reference/traits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/release.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/activity_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/activity_prescription_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/breed_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/clinical_evidence_base.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/clinical_risk_timeline.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/condition_activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/condition_ingredients_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/condition_ingredients_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/condition_protocols.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/environmental_matrices.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ext_supplements.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ext_treats_bakery.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/grooming_observation_defs.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ingredient_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ingredient_evidence_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ingredient_evidence_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ingredient_mechanisms.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/mixed_breed_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/mixed_breed_matrix.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/natural_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/nutrient_priorities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/package_tiers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/product_components.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/product_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/product_feeding_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/product_functions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/product_pricing.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/products.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/trait_attribute_explanations.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/trait_benefits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/trait_contribution_weights.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/legacy_mirror/trait_purposes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/lookup_maps.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/parameter_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/runtime/unit_conversion.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/breed_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/food_nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/ingredient_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/ingredient_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/mixed_trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/nutrient_targets.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/prevention_effectiveness.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/product_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/draft/2026.07.20/science/trait_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/SCIENTIFIC_AUDIT.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/coverage_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/ACTIVITY_EVIDENCE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/ACTIVITY_PRESCRIPTION_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/BODYTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/BREEDS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/BREED_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/BREED_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CLIMATE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CLINICAL_EVIDENCE_BASE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CLINICAL_RISK_TIMELINE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/COATTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CONDITION_ACTIVITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CONDITION_INGREDIENTS__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CONDITION_INGREDIENTS__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/CONDITION_PROTOCOLS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/ENERGY_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/ENVIRONMENTAL_MATRICES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/EXT_SUPPLEMENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/EXT_TREATS_BAKERY.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/FUNCTIONGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/GROOMING_OBSERVATION_DEFS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/INGREDIENT_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/INGREDIENT_EVIDENCE__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/INGREDIENT_EVIDENCE__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/INGREDIENT_MECHANISMS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/INGREDIENT_NUTRIENT_ESTIMATES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/LIFESPAN_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/MIXED_BREED_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/MIXED_BREED_MATRIX.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/NATURAL_FOOD_SOURCES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/NUTRIENT_PRIORITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PACKAGE_TIERS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PRODUCT_CATALOG.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PRODUCT_COMPONENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PRODUCT_DEFAULTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PRODUCT_FEEDING_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PRODUCT_FUNCTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/PRODUCT_PRICING.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/SIZE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/SKULLTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/STAPLE_FOOD.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/TRAIT_ATTRIBUTE_EXPLANATIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/TRAIT_BENEFITS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/TRAIT_CONTRIBUTION_WEIGHTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/TRAIT_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/TRAIT_PURPOSES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/TREATS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/csv_analysis/WEAKNESSGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/data_validation.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/duplicate_detection.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/formula_trace/activity_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/formula_trace/assembler.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/formula_trace/ingredient_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/formula_trace/nutrition_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/formula_trace/package_optimizer.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/formula_trace/risk_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/knowledge_coverage.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/migration_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/phase2_parity_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/scientific_audit.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/unused_columns.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/generated/warehouse_mapping.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/graph/edges.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/graph/nodes.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/graph/summary.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/manifest.yaml | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/nutrition/food_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/nutrition/ingredient_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/nutrition/ingredient_composition_NEEDS_VALIDATION.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/nutrition/ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/nutrition/units.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/prevention/condition_activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/prevention/condition_ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/SCIENTIFIC_AUDIT.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/coverage_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/ACTIVITY_EVIDENCE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/ACTIVITY_PRESCRIPTION_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/BODYTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/BREEDS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/BREED_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/BREED_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CLIMATE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CLINICAL_EVIDENCE_BASE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CLINICAL_RISK_TIMELINE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/COATTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CONDITION_ACTIVITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/CONDITION_PROTOCOLS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/ENERGY_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/ENVIRONMENTAL_MATRICES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/EXT_SUPPLEMENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/EXT_TREATS_BAKERY.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/FUNCTIONGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/GROOMING_OBSERVATION_DEFS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/INGREDIENT_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/INGREDIENT_MECHANISMS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/INGREDIENT_NUTRIENT_ESTIMATES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/LIFESPAN_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/MIXED_BREED_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/MIXED_BREED_MATRIX.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/NATURAL_FOOD_SOURCES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/NUTRIENT_PRIORITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PACKAGE_TIERS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PRODUCT_CATALOG.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PRODUCT_COMPONENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PRODUCT_DEFAULTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PRODUCT_FEEDING_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PRODUCT_FUNCTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/PRODUCT_PRICING.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/SIZE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/SKULLTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/STAPLE_FOOD.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/TRAIT_ATTRIBUTE_EXPLANATIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/TRAIT_BENEFITS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/TRAIT_CONTRIBUTION_WEIGHTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/TRAIT_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/TRAIT_PURPOSES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/TREATS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/csv_analysis/WEAKNESSGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/data_validation.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/duplicate_detection.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/formula_trace/activity_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/formula_trace/assembler.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/formula_trace/ingredient_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/formula_trace/nutrition_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/formula_trace/package_optimizer.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/formula_trace/risk_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/knowledge_coverage.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/migration_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/phase2_parity_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/scientific_audit.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/unused_columns.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/generated/warehouse_mapping.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/graph/edges.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/graph/nodes.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/graph/summary.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/body_sizes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/body_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/climates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/coat_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/foods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/papers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/prevention_methods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/skull_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/reference/traits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/release.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/activity_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/activity_prescription_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/breed_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/clinical_evidence_base.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/clinical_risk_timeline.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/condition_activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/condition_ingredients_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/condition_ingredients_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/condition_protocols.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/environmental_matrices.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ext_supplements.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ext_treats_bakery.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/grooming_observation_defs.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ingredient_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ingredient_evidence_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ingredient_evidence_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ingredient_mechanisms.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/mixed_breed_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/mixed_breed_matrix.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/natural_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/nutrient_priorities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/package_tiers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/product_components.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/product_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/product_feeding_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/product_functions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/product_pricing.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/products.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/trait_attribute_explanations.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/trait_benefits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/trait_contribution_weights.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/legacy_mirror/trait_purposes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/lookup_maps.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/parameter_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/runtime/unit_conversion.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/breed_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/food_nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/ingredient_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/ingredient_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/mixed_trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/nutrient_targets.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/prevention_effectiveness.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/product_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/2026.07.20/science/trait_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/production/release.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reasoning/README.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/body_sizes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/body_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/climates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/coat_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/foods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/papers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/prevention_methods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/skull_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/reference/traits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/SCIENTIFIC_AUDIT.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/coverage_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/ACTIVITY_EVIDENCE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/ACTIVITY_PRESCRIPTION_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/BODYTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/BREEDS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/BREED_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/BREED_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CLIMATE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CLINICAL_EVIDENCE_BASE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CLINICAL_RISK_TIMELINE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/COATTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CONDITION_ACTIVITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/CONDITION_PROTOCOLS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/ENERGY_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/ENVIRONMENTAL_MATRICES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/EXT_SUPPLEMENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/EXT_TREATS_BAKERY.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/FUNCTIONGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/GROOMING_OBSERVATION_DEFS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/INGREDIENT_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/INGREDIENT_MECHANISMS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/INGREDIENT_NUTRIENT_ESTIMATES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/LIFESPAN_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/MIXED_BREED_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/MIXED_BREED_MATRIX.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/NATURAL_FOOD_SOURCES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/NUTRIENT_PRIORITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PACKAGE_TIERS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PRODUCT_CATALOG.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PRODUCT_COMPONENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PRODUCT_DEFAULTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PRODUCT_FEEDING_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PRODUCT_FUNCTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/PRODUCT_PRICING.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/SIZE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/SKULLTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/STAPLE_FOOD.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/TRAIT_ATTRIBUTE_EXPLANATIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/TRAIT_BENEFITS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/TRAIT_CONTRIBUTION_WEIGHTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/TRAIT_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/TRAIT_PURPOSES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/TREATS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/csv_analysis/WEAKNESSGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/data_validation.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/duplicate_detection.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/formula_trace/activity_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/formula_trace/assembler.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/formula_trace/ingredient_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/formula_trace/nutrition_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/formula_trace/package_optimizer.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/formula_trace/risk_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/knowledge_coverage.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/migration_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/phase2_parity_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/scientific_audit.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/unused_columns.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/generated/warehouse_mapping.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/graph/edges.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/graph/nodes.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/graph/summary.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/body_sizes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/body_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/climates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/coat_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/foods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/papers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/prevention_methods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/skull_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/reference/traits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/release.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/activity_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/activity_prescription_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/breed_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/clinical_evidence_base.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/clinical_risk_timeline.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/condition_activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/condition_ingredients_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/condition_ingredients_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/condition_protocols.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/environmental_matrices.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ext_supplements.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ext_treats_bakery.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/grooming_observation_defs.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ingredient_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ingredient_evidence_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ingredient_evidence_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ingredient_mechanisms.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/mixed_breed_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/mixed_breed_matrix.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/natural_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/nutrient_priorities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/package_tiers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/product_components.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/product_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/product_feeding_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/product_functions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/product_pricing.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/products.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/trait_attribute_explanations.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/trait_benefits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/trait_contribution_weights.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/legacy_mirror/trait_purposes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/lookup_maps.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/parameter_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/runtime/unit_conversion.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/breed_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/food_nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/ingredient_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/ingredient_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/mixed_trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/nutrient_targets.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/prevention_effectiveness.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/product_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/releases/2026.07.20/science/trait_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/repository/__init__.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/repository/domains.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/repository/entities.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/repository/scientific.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/activity_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/activity_prescription_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/breed_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/clinical_evidence_base.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/clinical_risk_timeline.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/condition_activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/condition_ingredients_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/condition_ingredients_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/condition_protocols.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/environmental_matrices.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ext_supplements.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ext_treats_bakery.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/grooming_observation_defs.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ingredient_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ingredient_evidence_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ingredient_evidence_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ingredient_mechanisms.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/mixed_breed_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/mixed_breed_matrix.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/natural_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/nutrient_priorities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/package_tiers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/product_components.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/product_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/product_feeding_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/product_functions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/product_pricing.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/products.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/trait_attribute_explanations.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/trait_benefits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/trait_contribution_weights.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/legacy_mirror/trait_purposes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/lookup_maps.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/parameter_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/runtime/unit_conversion.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/breed_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/food_nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/ingredient_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/ingredient_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/mixed_trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/nutrient_targets.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/prevention_effectiveness.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/product_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/science/trait_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/SCIENTIFIC_AUDIT.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/coverage_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/ACTIVITY_EVIDENCE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/ACTIVITY_PRESCRIPTION_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/BODYTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/BREEDS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/BREED_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/BREED_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CLIMATE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CLINICAL_EVIDENCE_BASE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CLINICAL_RISK_TIMELINE.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/COATTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CONDITION_ACTIVITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CONDITION_INGREDIENTS__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/CONDITION_PROTOCOLS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/ENERGY_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/ENVIRONMENTAL_MATRICES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/EXT_SUPPLEMENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/EXT_TREATS_BAKERY.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/FUNCTIONGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/GROOMING_OBSERVATION_DEFS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/INGREDIENT_ALIASES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__5_scientific_nutrition.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/INGREDIENT_EVIDENCE__preventative_ingredients.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/INGREDIENT_MECHANISMS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/INGREDIENT_NUTRIENT_ESTIMATES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/LIFESPAN_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/MIXED_BREED_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/MIXED_BREED_MATRIX.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/NATURAL_FOOD_SOURCES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/NUTRIENT_PRIORITIES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PACKAGE_TIERS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PRODUCT_CATALOG.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PRODUCT_COMPONENTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PRODUCT_DEFAULTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PRODUCT_FEEDING_RULES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PRODUCT_FUNCTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/PRODUCT_PRICING.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/SIZE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/SKULLTYPE_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/STAPLE_FOOD.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/TRAIT_ATTRIBUTE_EXPLANATIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/TRAIT_BENEFITS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/TRAIT_CONTRIBUTION_WEIGHTS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/TRAIT_INTERACTIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/TRAIT_PURPOSES.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/TREATS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/csv_analysis/WEAKNESSGROUP_CONDITIONS.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/data_validation.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/duplicate_detection.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/formula_trace/activity_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/formula_trace/assembler.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/formula_trace/ingredient_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/formula_trace/nutrition_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/formula_trace/package_optimizer.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/formula_trace/risk_engine.md | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/knowledge_coverage.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/migration_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/phase2_parity_report.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/scientific_audit.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/unused_columns.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/generated/warehouse_mapping.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/graph/edges.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/graph/nodes.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/graph/summary.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/body_sizes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/body_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/climates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/coat_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/conditions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/foods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/ingredients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/papers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/prevention_methods.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/skull_types.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/reference/traits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/release.json | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/activity_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/activity_prescription_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/breed_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/breeds.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/clinical_evidence_base.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/clinical_risk_timeline.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/condition_activities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/condition_ingredients_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/condition_ingredients_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/condition_protocols.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/environmental_matrices.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ext_supplements.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ext_treats_bakery.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/grooming_observation_defs.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ingredient_aliases.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ingredient_evidence_prev.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ingredient_evidence_sci.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ingredient_mechanisms.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/ingredient_nutrient_estimates.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/mixed_breed_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/mixed_breed_matrix.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/natural_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/nutrient_priorities.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/package_tiers.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/product_components.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/product_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/product_feeding_rules.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/product_functions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/product_pricing.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/products.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/trait_attribute_explanations.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/trait_benefits.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/trait_contribution_weights.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/legacy_mirror/trait_purposes.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/lookup_maps.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/parameter_defaults.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/runtime/unit_conversion.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/breed_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/food_nutrients.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/ingredient_evidence.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/ingredient_food_sources.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/mixed_trait_interactions.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/nutrient_targets.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/prevention_effectiveness.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/product_composition.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/staging/2026.07.20/science/trait_condition_risk.csv | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/tools/build_phase1.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/tools/build_science_graph.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
| warehouse/tools/materialize.py | ACTIVE | v2 architecture foundation asset | v2 layer files | n/a | No |  |
