# 1. Executive Summary

Ω11 was supposed to establish the canonical data language between customer/groomer/business input, the deterministic Waggy engine, derived results, and future agent tools — without implementing Gemini, MCP, a tool server, or a chat UI.

Implemented: a typed Pydantic contract package (`app/contracts/agent/`), adapters that map existing engine models without reasoning, a non-executing tool registry, contract tests, and design/inventory documentation.

The contract layer is ready for Ω12/Ω13 to implement a tool adapter/server on top of `PPIEWellnessAgent.generate_reproducible_report`. It is not itself a tool host.

**Ω11 STATUS: PASS WITH GAPS** — mandatory contracts, semantics, provenance, versioning, and scientific/product boundaries are in place and tested. Gaps are out-of-scope (no tool server / Gemini / HTTP wiring), documented host defaults on the existing application adapter, missing engine `analysis_id`, and 112 long interface optimizer tests not re-run this session.

# 2. Repository Architecture Inspected

Directories: `app/agent/`, `app/data/`, `app/api/`, `app/core/`, `app/presentation/`, `app/science/`, `warehouse/`, `tests/`, `docs/`, `repository/models/`.

Relevant files: `app/agent/state.py`, `version.py`, `engine.py`, `response_assembler.py`, `package_search.py`, `app/api/main.py`, `payload_adapter.py`, `app/data/scientific_care.py`, `scientific_requirements.py`, `repository.py`, `app/science/models.py`, `versioning.py`, `warehouse/repository/entities.py`, `repository/models/runtime.py`.

Existing engine path: `DogProfileInput` → `PPIEWellnessAgent.generate_reproducible_report` → warehouse → `resolve_care_model` → requirement profile → `PACKAGE_OPTIMIZER_V2_1` → analyze dict → presentation.

Existing API path: the same function behind `/api/v1/analyze`, `/api/v2/wellness/evaluate`, workbench, three-surfaces, clinical-report.

Existing warehouse path: `warehouse/biology`, `prevention`, `reference/papers.csv`, `commercial`.

# 3. Existing Contracts Reused

| Path | Model | Reason reused |
|---|---|---|
| `app/agent/state.py` | `DogProfileInput` | Canonical engine input; not duplicated |
| `app/agent/version.py` | `ALGORITHM_VERSION` (`2.1.0`), `ENGINE_NAME` (`PPIE`) | Sole engine version |
| `app/data/repository.py` | `version`, `csv_hash` | Warehouse identity |
| Warehouse CSV columns | `fact_id`, `paper_id`, `paper_name`, `paper_link`, `publication_year`, `scientific_quote`, `status` | Evidence/fact field names |
| Engine status strings | `NOT_AVAILABLE`, `NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE`, `NEEDS_VALIDATION`, `MISSING_PROVENANCE`, `WAREHOUSE_EVIDENCE`, `migrated`, `NOT_MODELED` | Do not invent parallel tokens |
| `repository/models/runtime.py` | `dog_id` convention | Documented, optional |
| Workbench | `correlation_id` | Optional invocation id |

# 4. New Contracts Added

| Path | Model | Purpose | Owner | Authority | Provenance | Mutability |
|---|---|---|---|---|---|---|
| `input.py` | `CanonicalDogInput`, `FieldValue` | Agent input + presence states | Customer | None | Optional | Authorized user fields later |
| `observations.py` | `Observation` | Individual observations | Groomer/customer | None | Observation fields | Authorized observations later |
| `evidence.py` | `ScientificEvidence`, `ScientificFact` | Evidence + facts | Science | Warehouse | Required | Agent NO |
| `inference.py` | `ScientificInference`, `PrevalenceValue` | Derived inference shape | Engine | Derived | Required | Agent NO |
| `products.py` | `ProductRecord`, `BusinessConfiguration` | Product vs commercial search space | Catalog/business | Not medical | Where applicable | Controlled |
| `health.py` | `HealthAnalysisResult` | Future analyze_health | Engine | Derived | Yes | Agent NO |
| `nutrition.py` | `NutritionAnalysisResult` | Future calculate_nutrition | Engine | Derived | Yes | Agent NO |
| `bundles.py` | `BundleSearchResult` | Future optimize_bundles | Optimizer | Derived | Yes | Agent NO |
| `analysis.py` | `CanonicalAnalysis` | One-run envelope | Engine | Derived | Yes | Agent NO |
| `report.py` | `ReportProjection` | Future generate_report | Presentation | None | Inherits analysis | Agent NO |
| `provenance.py` | `ProvenanceRecord` | Shared chain | Shared | — | Self | Agent NO |
| `versions.py` | `VersionStamp` | engine/warehouse/schema/tool | Shared | — | — | Agent NO |
| `errors.py` | `ToolError` | Boundary errors | Contract | — | — | — |
| `registry.py` | `ToolRegistryEntry` | Future registry | Contract | — | — | No execute |
| `context.py` | `AgentContext` | Bounded agent context | Auth (future) | None | — | Permissioned |
| `adapters.py` | mapping functions | Wrap existing dicts/models | Contract | None | Copied, not invented | — |

# 5. Canonical Domain Model

- **User data** — `CanonicalDogInput` / `DomainKind.USER_INPUT`. Not evidence.
- **Observation** — `Observation`. Not a fact, not a diagnosis.
- **Evidence** — `ScientificEvidence` (paper/quote/status).
- **Fact** — `ScientificFact` (subject–relationship–object + warehouse status).
- **Inference** — `ScientificInference` / `ConditionFinding` (engine-derived).
- **Product** — `ProductRecord` (identity/commercial/nutrition/eligibility separated).
- **Commercial configuration** — `BusinessConfiguration` (search space only).
- **Analysis** — `CanonicalAnalysis` and capability slices.
- **Recommendation** — `BundleOption.domain = RECOMMENDATION` (optimizer output).
- **Analytics** — domain enum only; no individual-customer analytics models.

# 6. Canonical Input Contract

`CanonicalDogInput` (`app/contracts/agent/input.py`).

Each scalar is `FieldValue` with `state` + `value`.

| Field | Type | Required for tools | Meaning | Unknown state | Source |
|---|---|---|---|---|---|
| `dog_id` | `str \| None` | No | Optional identity | omitted | Convention / future |
| `name` | `FieldValue[str]` | No (required only to convert to engine) | Pet name | UNKNOWN / NOT_PROVIDED | User |
| `primary_breed` | `FieldValue[str]` | Yes | Stated breed | UNKNOWN / NOT_PROVIDED | User |
| `secondary_breed` | `FieldValue[str]` | No | Stated second breed | NOT_PROVIDED | User |
| `breed_split_pct` | `FieldValue[float]` | If secondary present (engine conversion) | Mix percent | NOT_PROVIDED | User |
| `age_years` | `FieldValue[float]` | Yes | Age | UNKNOWN / NOT_PROVIDED | User |
| `birthday` | `FieldValue[str]` | No | ISO date; not used to invent age via `now()` | NOT_PROVIDED | User |
| `weight_kg` | `FieldValue[float]` | Yes | Weight | UNKNOWN / NOT_PROVIDED | User |
| `sex` | `FieldValue[str]` | No | Sex | NOT_PROVIDED | User |
| `activity_level` | `FieldValue[str]` | No for tools; yes for engine conversion | Activity | NOT_PROVIDED | User |
| `environment` | `FieldValue[str]` | No for tools; yes for engine conversion | Environment | NOT_PROVIDED | User |
| `height_cm` / `bcs` | `FieldValue[float]` | No | Optional body measures | NOT_PROVIDED | User |
| `monthly_budget` | `FieldValue[float]` | No | Budget; NOT_PROVIDED ≠ 0 | NOT_PROVIDED | User |
| `observations` | `list[Observation]` | No | Typed observations | empty list | User/groomer |

`validate_for_tools()` returns `MISSING_REQUIRED_INPUT` or `INVALID_INPUT`. It does not set age=5 or weight=20.

# 7. Observation Contract

`Observation`: `domain=OBSERVATION`, `observation_id`, `dog_id`, `observer_role` (customer/groomer/system), `observation_type`, `value`, `unit`, `confidence`, `timestamp`, `source_session_id`, `confirmation_status`.

No diagnosis field. Mapping observation → warehouse trait remains an engine concern, not automatic promotion.

# 8. Scientific Evidence Contract

`ScientificEvidence`: `paper_id`, `paper_name`, `paper_link`, `publication_year`, `study_type`, `species`, `scientific_quote`, `status`, `warehouse_version`, `source_table`, `relationship_ref` (fact_id).

Multiple evidence records per fact are allowed. Status uses warehouse tokens.

# 9. Scientific Fact Contract

`ScientificFact`: `fact_id`, `subject`, `relationship`, `object`, `value`, `unit`, `status`, `evidence[]`, `provenance[]`, `warehouse_version`.

`is_scientifically_usable` is true only for `APPROVED` or `WAREHOUSE_EVIDENCE`.

`NEEDS_VALIDATION`, `MISSING_PROVENANCE`, and `migrated` are **not** APPROVED. The warehouse does not currently label rows APPROVED; that state is reserved.

# 10. Scientific Inference Contract

`ScientificInference` / `ConditionFinding`: input fact refs, observed vs estimated `PrevalenceValue`, contributing traits, preventative targets, diagnosis_claim default false.

`PrevalenceValue`: `AVAILABLE` with percent/ratio, or `NOT_AVAILABLE` with nulls — never 0-as-missing.

# 11. Product Contract

`ProductRecord` separates `ProductIdentity`, `ProductCommercialData`, `ProductNutrientAmount`, `ProductEvidence`, `ProductEligibility`.

Advertising ≠ inventory ≠ scientific approval ≠ efficacy. `product_from_catalog_row` does not invent price or functions.

# 12. Business Configuration Contract

`BusinessConfiguration`: allowed products/brands, category eligibility, advertising/in-store/online/fulfillment lists, optional budget, package policy.

This changes candidate catalog later. It does not change prevalence, requirements, or evidence.

# 13. Health Contract

`HealthAnalysisResult` (`capability=analyze_health`): findings, trait_associations (separate), preventative_targets, evidence_status, prevalence_available, diagnosis_claim=false, evidence, provenance, versions.

Adapter: `health_from_care_model`. Does not call `resolve_care_model`.

# 14. Nutrition Contract

`NutritionAnalysisResult` (`capability=calculate_nutrition`): nutrients with min/max/unit/basis/`breed_recommended`/source; `daily_requirement` may be `NOT_AVAILABLE` when only density exists; `senior_specific_minima` can be `NOT_AVAILABLE`; `not_modeled` list; `complete_diet_claim=false`.

Adapter: `nutrition_from_requirement_profile`. Does not call `build_requirement_profile`.

# 15. Bundle Contract

`BundleSearchResult` (`capability=optimize_bundles`): essential/balanced/optimal `BundleOption`s (ids, names, prices, ledger, constraints, care pathways), `OptimizerProvenance` with `PACKAGE_OPTIMIZER_V2_1`, `filter_funnel`, `llm_used=false`.

Empty options → `status=NO_VALID_BUNDLES`.

Adapter: `bundles_from_search_envelope`. Does not run the search.

# 16. Provenance Contract

`ProvenanceRecord`: source_type, source_id, evidence_id, fact_id, paper_id, source_name, source_link, publication_year, quote, study_type, species, status, warehouse_version, csv_hash, engine_version (`ALGORITHM_VERSION`), capability_id, source_table, source_row.

Chain: package → product → eligibility → care/nutrient constraint → fact → paper. Ω11 defines the record; live chain assembly is Ω13.

# 17. Versioning Contract

| Field | Source |
|---|---|
| `engine_version` | `ALGORITHM_VERSION` = `2.1.0` |
| `engine_name` | `PPIE` |
| `warehouse_version` | `DataRepository.version` when known |
| `csv_hash` | `DataRepository.csv_hash` when known |
| `schema_version` | `AGENT_CONTRACT_SCHEMA_VERSION` = `1.0.0` |
| `tool_version` | reserved; registry entries `1.0.0` |
| `analysis_version` | equals engine_version when from analyze |

No second engine-version system.

# 18. Error Contract

| Code | Use |
|---|---|
| `MISSING_REQUIRED_INPUT` | Missing breed / age / weight (or engine-conversion name/env/activity) |
| `INVALID_INPUT` | `InputState.INVALID` |
| `NOT_AVAILABLE` | No usable scientific value (`NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE` is the engine equivalent) |
| `MISSING_EVIDENCE` | Evidence required but absent |
| `NEEDS_VALIDATION` / `MISSING_PROVENANCE` | Reused warehouse tokens |
| `NO_VALID_PRODUCTS` | No eligible products |
| `NO_VALID_BUNDLES` | Optimizer returned no tier options |
| `WAREHOUSE_ERROR` | Warehouse/system failure |

# 19. Permission Boundary

| Role | May |
|---|---|
| Customer | Own dog profile, preferences, analysis |
| Groomer | Authorized observations |
| Business | Commercial configuration, aggregate analytics (future) |
| Science team | Evidence, papers, mappings, authoring WRITE |
| Developer | Technical provenance, versions, traces |
| AI agent | Only authorized tools; not a human role |

Authoring `POST /api/v1/authoring/evidence` and `.../materialize` remain off the agent surface (`EXCLUDED_FROM_AGENT_SURFACE`).

# 20. Read/Calculate/Write Boundary

| Tool | Operation |
|---|---|
| analyze_health | READ + CALCULATE |
| calculate_nutrition | READ + CALCULATE |
| optimize_bundles | READ + CALCULATE |
| generate_report | PROJECTION |

Ω11 implements **no WRITE** and **no tool execution**.

# 21. Future Tool Registry Contract

`ToolRegistryEntry`: name, description, tool_version, schema_version, operation, permission, input_schema_name, output_schema_name.

Names: `analyze_health`, `calculate_nutrition`, `optimize_bundles`, `generate_report`.

No `execute`. No `POST /tools/call`. No MCP.

# 22. Future AI Boundary

Gemini may eventually: understand language, identify intent, select authorized tools, construct structured requests, explain results, summarize provenance, request missing inputs.

Gemini may NOT: access the warehouse or raw tables, create/modify scientific facts or evidence, invent prevalence/nutrients/products/prices, choose products outside the optimizer, override hard constraints or ranking, modify mappings, or bypass permissions.

Not implemented in Ω11.

# 23. Determinism Contract

Same dog input + authorized observations + warehouse version + catalog + commercial configuration + preferences + engine version → same deterministic analysis.

Canonical contracts exclude: `demo_mode` as scientific input, hidden groomer session merge, `datetime.now()` as age, silent numeric defaults.

Application HTTP still has those host behaviors. That is a documented gap, not hidden by Ω11.

# 24. Backward Compatibility

Unchanged: engine, optimizer, warehouse CSVs, `DogProfileInput`, payload adapter, all `/api/v1` and `/api/v2` routes, presentation adapters, workbench UI.

Ω11 is additive (`app/contracts/` + tests + docs).

# 25. Tests Added

`tests/contracts/test_omega11_serialization.py`

- `test_canonical_dog_input_roundtrip`
- `test_observation_roundtrip`
- `test_scientific_evidence_and_fact_roundtrip`
- `test_inference_product_business_roundtrip`
- `test_health_nutrition_bundle_provenance_version_error_roundtrip`

`tests/contracts/test_omega11_semantics.py`

- `test_unknown_is_not_zero`
- `test_not_available_prevalence_is_not_zero`
- `test_needs_validation_is_not_approved`
- `test_missing_provenance_is_not_approved`
- `test_migrated_is_not_approved`
- `test_observation_is_not_scientific_fact`
- `test_scientific_fact_is_not_inference`
- `test_product_fact_is_not_scientific_evidence`
- `test_commercial_configuration_is_not_scientific_evidence`
- `test_recommendation_and_report_projection_domains`
- `test_canonical_input_rejects_demo_mode_and_hidden_session`
- `test_budget_not_provided_is_not_zero`

`tests/contracts/test_omega11_provenance_versions.py`

- `test_provenance_retains_warehouse_evidence_fields`
- `test_unavailable_provenance_is_explicit_not_fabricated`
- `test_fact_adapter_preserves_row_provenance_without_inventing`
- `test_version_stamp_reuses_algorithm_version`
- `test_registry_has_tool_version_place`

`tests/contracts/test_omega11_errors_defaults.py`

- `test_missing_required_input_codes`
- `test_invalid_input_code`
- `test_not_available_and_evidence_codes`
- `test_product_and_bundle_and_warehouse_error_codes`
- `test_incomplete_dog_does_not_default_age_or_weight`
- `test_unknown_age_is_missing_required_not_five`
- `test_invalid_field_is_invalid_input`
- `test_engine_adapter_refuses_silent_defaults`
- `test_engine_adapter_succeeds_only_with_explicit_fields`

`tests/architecture/test_omega11_boundaries.py`

- `test_contract_layer_does_not_import_reasoning_engines`
- `test_contract_layer_does_not_instantiate_ppie_engine`
- `test_allowed_engine_imports_are_version_and_state_only`
- `test_health_adapter_does_not_invent_prevalence`
- `test_nutrition_adapter_does_not_invent_requirements`
- `test_bundle_adapter_does_not_choose_or_invent_products`
- `test_product_adapter_does_not_invent_price_or_efficacy`
- `test_authoring_routes_are_excluded_from_registry`

Contract + boundary: **39 passed, 0 failed** (`py -3 -m pytest tests/contracts tests/architecture/test_omega11_boundaries.py -q`).

# 26. Regression Tests

Commands and exact results (2026-09-08):

```
py -3 -m pytest tests/contracts tests/architecture/test_omega11_boundaries.py -q
```

**39 passed** in 1.09s. 0 failed.

```
py -3 -m pytest tests/architecture tests/mathematics tests/formulas tests/science_graph tests/warehouse_qa tests/contracts tests/optimization/test_optimization_runtime.py -q --tb=line
```

**109 passed** in 44.06s. 0 failed.

```
py -3 -m pytest tests/engine tests/pipeline tests/warehouse tests/api tests/reasoning tests/mechanisms tests/objectives tests/math_debugger tests/test_package_optimizer.py tests/optimization -q --tb=line
```

**54 passed, 2 skipped** in 109.41s. 0 failed.

```
py -3 -m pytest tests/test_agent_pipeline.py tests/test_clinical_assessment.py tests/test_clinical_report.py tests/test_engine_trace.py tests/test_formula_graph.py tests/test_inference_layer.py tests/test_inference_parity.py tests/test_phase6_authoring.py tests/test_science_graph.py tests/test_standard_report.py tests/test_ui_templates.py tests/test_validation_console.py tests/test_validation_console_live.py tests/test_warehouse_parity.py tests/benchmarks -q --tb=line
```

**49 passed, 30 skipped** in 111.16s. 0 failed. Skips are the existing `warehouse/current` clinical-CSV projection tests in `tests/conftest.py`.

```
py -3 -m pytest tests/interface -q --tb=line
  --ignore=tests/interface/test_bundle_comparison.py
  --ignore=tests/interface/test_bundle_display_options.py
  --ignore=tests/interface/test_bundle_nutrition_ledger.py
  --ignore=tests/interface/test_bundle_tier_semantics.py
  --ignore=tests/interface/test_exhaustive_nutrient_optimizer.py
  --ignore=tests/interface/test_package_combinatorial_optimizer.py
  --ignore=tests/interface/test_omega910_bundle_reasoning.py
  --ignore=tests/interface/test_demo_package_composition.py
  --ignore=tests/interface/test_package_generation_provenance.py
  --ignore=tests/interface/test_unified_workbench.py
  --ignore=tests/interface/test_omega10_warehouse_health.py
  --ignore=tests/interface/test_three_surface_contract.py
  --ignore=tests/interface/test_three_surface_runtime_identity.py
  --ignore=tests/interface/test_customer_package_render_contract.py
  --ignore=tests/interface/test_cstc_adapter.py
```

**81 passed** in 136.93s. 0 failed.

Interface folder total: 193 collected. **112 tests not re-run** this session because they invoke `PACKAGE_OPTIMIZER_V2_1` / workbench POST (`2^N−1`) and exceed practical wall-clock (prior full `tests/interface` run stalled for tens of minutes on a single search). Those files were not modified by Ω11. Status: **NOT VERIFIED** this session.

Unique executed (accounting for `tests/optimization/test_optimization_runtime.py` overlap of 6 tests): **287 passed, 32 skipped, 0 failed**.

A full uninterrupted `pytest tests` including all 112 exhaustive interface tests: **NOT VERIFIED**.

# 27. Files Changed

| Path | Reason |
|---|---|
| `app/contracts/**` | New typed contract package |
| `tests/contracts/**` | Contract tests |
| `tests/architecture/test_omega11_boundaries.py` | Engine-identity / scientific / product boundary |
| `docs/omega11-agent-data-contract-design.md` | Design report |
| `docs/omega11-agent-contract-inventory.md` | Inventory |
| `docs/omega11-agent-data-contract-report.md` | This report |
| `docs/WAGGY_SYSTEM.md` | Pointer + correct leftover “Ω11 = validate flags” line |
| `docs/README.md` | Links |

# 28. Files Not Changed

- Scientific warehouse (`warehouse/**`, including `recovery_original/`)
- Optimizer (`app/agent/package_optimizer.py`, `package_search.py`)
- Formulas (`app/formulas/**`)
- Health reasoning (`app/data/scientific_care.py`)
- Nutrition mathematics (`app/data/scientific_requirements.py`)
- Product ranking / engine (`app/agent/engine.py`, `response_assembler.py`)
- Presentation routes and `app/presentation/adapter.py`
- `app/api/main.py`, `app/api/payload_adapter.py`
- Legacy workbench UI

# 29. Known Limitations

- Tool server / MCP / Gemini / agent UI: **NOT IMPLEMENTED** (out of scope).
- Adapters are not wired to HTTP: **NOT IMPLEMENTED**.
- `analysis_id` is not produced by the current engine: **GAP**.
- Application `profile_from_analyze_body` still defaults age=5 / weight=20: **UNCHANGED** (agent contract does not).
- Groomer session merge and process-wide demo mode remain on the application host: **UNCHANGED**.
- Live provenance chain from a real analyze run through all slices: **NOT VERIFIED** (adapters tested with example/engine-shaped dicts only).
- Exhaustive interface optimizer / workbench POST suite (112 tests): **NOT VERIFIED** this session (duration). Ω11 did not modify those test files or the optimizer.
- `APPROVED` is a reserved status; no warehouse row currently uses it.
- `dog_id` remains an unstable name-derived convention.
- `generate_report` is a typed projection stub, not a call to existing report builders.
- `match_products` is intentionally not a public tool.

# 30. Ω11 Acceptance Matrix

| Requirement | PASS/FAIL | Evidence |
|-------------|-----------|----------|
| Canonical dog input | PASS | `app/contracts/agent/input.py` `CanonicalDogInput`; `test_canonical_dog_input_roundtrip` |
| Observation contract | PASS | `observations.py` `Observation`; `test_observation_roundtrip` |
| Scientific evidence | PASS | `evidence.py` `ScientificEvidence`; `test_scientific_evidence_and_fact_roundtrip` |
| Scientific fact | PASS | `ScientificFact`; `test_needs_validation_is_not_approved` |
| Scientific inference | PASS | `inference.py`; `test_scientific_fact_is_not_inference` |
| Product contract | PASS | `products.py` `ProductRecord`; `test_product_adapter_does_not_invent_price_or_efficacy` |
| Business config | PASS | `BusinessConfiguration`; `test_commercial_configuration_is_not_scientific_evidence` |
| Health contract | PASS | `health.py` `HealthAnalysisResult`; `test_health_adapter_does_not_invent_prevalence` |
| Nutrition contract | PASS | `nutrition.py`; `test_nutrition_adapter_does_not_invent_requirements` |
| Bundle contract | PASS | `bundles.py`; `test_bundle_adapter_does_not_choose_or_invent_products` |
| Provenance | PASS | `provenance.py`; `test_provenance_retains_warehouse_evidence_fields` |
| Versioning | PASS | `versions.py` uses `ALGORITHM_VERSION`; `test_version_stamp_reuses_algorithm_version` |
| Typed errors | PASS | `errors.py`; `test_missing_required_input_codes` et al. |
| No silent defaults | PASS | `test_incomplete_dog_does_not_default_age_or_weight`; `test_engine_adapter_refuses_silent_defaults` |
| Scientific boundary | PASS | `test_contract_layer_does_not_import_reasoning_engines`; `test_health_adapter_does_not_invent_prevalence` |
| Product boundary | PASS | `test_product_adapter_does_not_invent_price_or_efficacy`; `test_bundle_adapter_does_not_choose_or_invent_products` |
| Permission boundary | PASS | `context.py` `ActorRole`; `test_authoring_routes_are_excluded_from_registry` |
| Determinism | PASS | No demo_mode/session fields on canonical input; `test_canonical_input_rejects_demo_mode_and_hidden_session` |
| Backward compatibility | PASS | Ω11 added `app/contracts/` + tests + docs only. Did not edit engine/optimizer/warehouse/API/UI in this phase |
| Regression tests | PASS WITH GAPS | 287 passed, 32 skipped, 0 failed on executed suite. 112 exhaustive interface tests NOT VERIFIED (duration) |

# 31. Final Verdict

Ω11 STATUS: PASS WITH GAPS
