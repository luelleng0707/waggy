# Waggy Core Forensic Architecture Map

**Phase:** 1 — forensic architecture audit  
**Date:** 2026-09-14  
**Workspace:** `c:\Users\Admin\Downloads\waggy`  
**Method:** Read source, tests, schemas, warehouse layout, and on-disk tree. No production code, tests, or scientific CSVs were modified. The full pytest suite was **not** executed (that is Phase 3).

**Classification of claims in this document:**

| Label | Meaning |
|---|---|
| VERIFIED | Observed in source, tests, or on-disk paths in this workspace |
| INFERRED | Reasonable from call graphs but not proven by a live run this session |
| UNCLEAR | Insufficient evidence in this audit |
| MISSING | Searched; not present or not wired |

Component **STATUS** values: `IMPLEMENTED` | `PARTIAL` | `BROKEN` | `MISSING` | `DUPLICATE` | `LEGACY` | `UNCLEAR`

If this file and runtime disagree later, **runtime wins**.

---

## 0. How to read this map

The desired “Waggy Core Brain” is a single callable pipeline:

```
dog profile → resolve → warehouse knowledge → health → nutrition → activity → grooming
          → product matching → packages → evidence → API
```

This audit records **what the repository actually does**, not what later phases should build.

**Headline (VERIFIED):** There is already one scientific/recommendation choke point:

`PPIEWellnessAgent.generate_reproducible_report` (`app/agent/engine.py`)

The HTTP workbench handler does **not** contain a second engine. Presentation, AI explain, tool gateway, and analysis-compare wrap that result or stored digests.

**Headline gaps vs the desired brain (VERIFIED):**

1. Activity and grooming are **not** first-class engines whose node outputs drive the public analyze JSON.
2. Product matching (`PRODUCT_MATCH_V2_1`) and package membership (`PACKAGE_OPTIMIZER_V2_1` / `run_package_search`) are **independent**.
3. Ω12 normalization is implemented and **not on** the HTTP/engine path.
4. `warehouse/manifest.yaml` points at `warehouse/science`, which **does not exist** at the warehouse root; the loader falls back to `warehouse/biology`.
5. Portable UI directory `waggy-frontend/` is **not on disk** in this workspace, though FastAPI and tests expect it.
6. Two HTTP profile adapters exist (fail-closed workbench vs silent-default analyze).

---

## 1. Documentation vs executable tree

| Claim | Source | Executable fact | Class |
|---|---|---|---|
| README §1 still says there is no Gemini / MCP / chatbot | `README.md` | `app/ai/` + `POST /api/v1/ai/explain` + Fake/Gemini providers exist; MCP does not | VERIFIED conflict |
| README §20 previously said tools were planned | `README.md` (updated Ω17.4) | `app/tools/` + `POST /api/v1/ai/tools/invoke` exist | VERIFIED |
| `docs/WAGGY_SYSTEM.md` is the authored system doc | docs | Code/tests win when they disagree | VERIFIED policy |
| `docs/omega17.1a-stabilization-report.md` | `docs/README.md` link | File **missing on disk** | VERIFIED |
| `docs/omega17-ai-architecture.md` | `docs/README.md` / `WAGGY_SYSTEM.md` | File **missing on disk** | VERIFIED |
| `waggy-frontend/` is the product UI | `app/api/main.py`, `tests/interface/frontend_paths.py`, `docs/omega17.4-fe-completion-report.md` | Directory **does not exist** (`Test-Path` false; `git ls-files waggy-frontend` empty) | VERIFIED |
| `warehouse/manifest.yaml` `root: warehouse/science` | manifest | No `warehouse/science/` at repo warehouse root; biology loader used instead | VERIFIED |

---

## 2. On-disk top level (VERIFIED)

Present: `app/`, `authoring/`, `config/`, `CSTC_1524/`, `curation/`, `debug/`, `docs/`, `legacy/`, `ontology/`, `repository/`, `science_pipeline/`, `scripts/`, `tests/`, `warehouse/`, `node_modules/`, FastAPI/Railway files.

**Absent:** `waggy-frontend/`, `legacy/workbench.js` (deleted; routes still point at the missing frontend).

`CSTC_1524/` exists on disk. No `app/` Python import of `CSTC_1524` or `PetCarePro` was found. STATUS: **LEGACY / UNKNOWN** (unrelated tree sitting in the repo).

---

## 3. Canonical runtime DAG (VERIFIED call chain)

```
HTTP POST /api/v1/presentation/workbench
        ↓
WorkbenchRequest  (app/api/http_models.py)
        ↓
profile_from_workbench_body  (app/api/payload_adapter.py)   FAIL-CLOSED
        ↓
optional constraints_from_dog + using_package_constraints   (if dog_id)
        ↓
PPIEWellnessAgent.generate_reproducible_report  (app/agent/engine.py)
        ↓
AssessmentAgent.assess  (app/agent/assessment_agent.py)
        ↓
FormulaGraph.execute  (18 nodes, app/agent/nodes/__init__.py default_nodes)
        ↓
ExportNode → assemble_frontend_response  (app/agent/response_assembler.py)
        ↓  (inside assembler)
build_optimized_packages → run_package_search
        ↓
raw analyze dict  (legacy JSON contract)
        ↓
build_clinical_assessment  (app/data/clinical_assessment.py)  NO RECOMPUTE
        ↓
build_workbench_presentations / build_canonical_result  (app/presentation/adapter.py)
        ↓
workbench_presentation.v1  { canonical_analysis.v1, roles.* }
        ↓
optional persist_workbench_run  (if dog_id)
```

**INFERRED (not live-run this session):** FormulaGraph node order is the `default_nodes()` list, scheduled by declared `dependencies`.

---

## 4. Application and API entrypoints

### 4.1 FastAPI

| Field | Value |
|---|---|
| FILE | `app/api/main.py` |
| SYMBOL | `app` (`FastAPI`); shim `app/main.py` re-exports it |
| PURPOSE | HTTP boundary: analysis, persistence, catalog, debug, static UI |
| INPUT | HTTP |
| OUTPUT | JSON / static files |
| DEPENDENCIES | `PPIEWellnessAgent`, presentation, state, AI, tools |
| TESTS | `tests/api/*`, `tests/interface/test_canonical_routes.py`, `tests/api/test_omega16_openapi.py` |
| STATUS | **IMPLEMENTED** |

Launcher: `scripts/run_dev.py` (sets `WAGTOPIA_DEMO_MODE=true`, `PPIE_DEBUG=true` by default). Also `scripts/run_wagtopia_local.py` / `run_wagtopia_remote.py`.

### 4.2 Canonical workbench route

| Field | Value |
|---|---|
| FILE | `app/api/main.py` |
| SYMBOL | `presentation_workbench` → `_run_workbench_analysis` |
| PURPOSE | One engine call + four role projections |
| INPUT | `WorkbenchRequest` (fail-closed: breed, age or birthday, weight, activity, environment) |
| OUTPUT | `workbench_presentation.v1` |
| DEPENDENCIES | `profile_from_workbench_body`, `generate_reproducible_report`, `build_clinical_assessment`, `build_workbench_presentations` |
| TESTS | `tests/api/test_omega16_api_contract.py`, `tests/api/test_omega16_1_hardening.py`, `tests/interface/test_unified_workbench.py` |
| STATUS | **IMPLEMENTED** (API). UI consumer **MISSING** on disk. |

Does **not** duplicate scientific math in the handler (VERIFIED: handler calls agent then projects).

### 4.3 Other analysis HTTP (same engine, different adapters)

| Route | Handler pattern | Engine? | Validation | STATUS |
|---|---|---|---|---|
| `POST /api/v1/analyze` | `profile_from_analyze_body` | Yes | Silent defaults (age 5, weight 20, Moderate, Temperate Indoor) | **IMPLEMENTED / LEGACY contract** |
| `POST /api/v2/wellness/evaluate` | typed `DogProfileInput` | Yes | Pydantic model | **IMPLEMENTED** |
| `POST /api/v1/dogs/{id}/analyze` | `effective_profile` → workbench path | Yes | Fail-closed projection | **IMPLEMENTED** |
| `POST /api/v1/dogs/{id}/recompute` | preference change + one engine run | Yes | Ω17.2 body | **IMPLEMENTED** |
| `POST /api/v1/presentation/three-surfaces` | analyze + project | Yes | Business key optional | **IMPLEMENTED** |
| `POST /api/v1/clinical-report` | analyze + report projection | Yes | Legacy analyze body | **IMPLEMENTED / LEGACY-adjacent** |
| `POST /api/v1/ppie/assess` | clinical assessment modules | Yes | — | **IMPLEMENTED** |
| `GET /api/v1/dogs/{id}/analyses/compare` | `explain_from_digests` | **No** | Stored rows | **IMPLEMENTED** |
| `POST /api/v1/ai/explain` | `WaggyExplanationAgent` | **No** | Canonical payload | **IMPLEMENTED** |
| `POST /api/v1/ai/tools/invoke` | `WaggyToolGateway` | **No** | Allowlist | **IMPLEMENTED** |
| `GET /api/v1/evidence/{condition}` | `app/api/evidence.py` | No | Catalog/warehouse lookup | **IMPLEMENTED** (parallel matcher helper, not package composer) |
| `GET /api/v1/products/{condition}` | same | No | — | **IMPLEMENTED** |

**CONFLICT (VERIFIED):** Workbench vs `/api/v1/analyze` validation. Same `generate_reproducible_report`, different input semantics.

**CONFLICT (VERIFIED):** `POST /api/v2/wellness/evaluate` is unauthenticated raw engine access; workbench is also not `API_KEYS`-gated. Graph/authoring routes are gated when `API_KEYS` is set.

### 4.4 Streamlit / in-process UI

| Field | Value |
|---|---|
| FILE | `app/ui/renderer/navigation.py` |
| SYMBOL | `get_agent`, `default_profile`, `run_engine` path |
| PURPOSE | Streamlit journey; calls `generate_reproducible_report` **in-process** |
| INPUT | Different Dolly defaults than HTTP example |
| OUTPUT | Templates |
| TESTS | `tests/test_ui_templates.py` (partial) |
| STATUS | **LEGACY / DUPLICATE consumer** — bypasses workbench HTTP contract |

---

## 5. Core engine modules

### 5.1 PPIEWellnessAgent

| Field | Value |
|---|---|
| FILE | `app/agent/engine.py` |
| SYMBOL | `PPIEWellnessAgent.generate_reproducible_report` |
| PURPOSE | Sole production analysis entry |
| INPUT | `DogProfileInput` |
| OUTPUT | `dict` = `AssessmentResult.to_analyze_dict()` = ExportNode `legacy_json` |
| DEPENDENCIES | `AssessmentAgent`, `DataRepository` via `bootstrap` + `clinical_root_str()` |
| TESTS | `tests/test_agent_pipeline.py`, `tests/test_formula_graph.py`, `tests/test_engine_trace.py` |
| STATUS | **IMPLEMENTED** |

Docstring omits GroomingNode / Confidence / Evidence (INFERRED as stale comment, not a second pipeline).

### 5.2 AssessmentAgent + FormulaGraph

| Field | Value |
|---|---|
| FILE | `app/agent/assessment_agent.py`, `app/agent/formula_graph.py`, `app/agent/nodes/__init__.py` |
| SYMBOL | `AssessmentAgent.assess`, `FormulaGraph`, `default_nodes()` |
| PURPOSE | Schedule 18 nodes; attach science-graph explainability after execute |
| INPUT | `DogProfileInput` + `DataRepository` |
| OUTPUT | `AssessmentResult` (typed) + `legacy_json` |
| DEPENDENCIES | Nodes wrap `app/formulas/stages/*` and engines |
| TESTS | `tests/test_formula_graph.py`, `tests/pipeline/test_pipeline_architecture.py` |
| STATUS | **IMPLEMENTED** |

Post-graph: `app/science/attach.py` `build_reasoning_payload` / `attach_science_to_analyze`. Failures are swallowed; clinical JSON preserved (VERIFIED try/except).

### 5.3 FormulaGraph nodes (membership VERIFIED)

| Node | FILE | Wraps | Feeds public analyze? | STATUS |
|---|---|---|---|---|
| ProfileNode | `app/agent/nodes/profile_node.py` | profile dump | Indirect | **IMPLEMENTED** |
| BreedNode | `app/agent/nodes/breed_node.py` | ad-hoc breed table match | **BiologyNode does not read this output** | **PARTIAL / DUPLICATE** |
| BiologyNode | `app/agent/nodes/biology_node.py` | `run_biological_stage` | Yes (`biology`) | **IMPLEMENTED** |
| RiskNode | `app/agent/nodes/risk_node.py` | `compute_risks` | Yes (`healthInsights` via assembler) | **IMPLEMENTED** |
| EpidemiologyNode | `app/agent/nodes/epidemiology_node.py` | epidemiology stage | Yes | **IMPLEMENTED** |
| ActivityNode | `app/agent/nodes/activity_node.py` | `condition_activities` lookup | Passed as `management` into assembler; **parameter unused** | **PARTIAL** |
| GroomingNode | `app/agent/nodes/grooming_node.py` | load `grooming_observation_defs` | **Not a dependency of ExportNode** | **PARTIAL** (runs; not in analyze JSON) |
| NutritionNode | `app/agent/nodes/nutrition_node.py` | `run_nutrition_stage` | Yes (clinical targets) | **IMPLEMENTED** |
| IngredientNode | `app/agent/nodes/ingredient_node.py` | `map_ingredients` | Assembler also calls `map_ingredients` again | **DUPLICATE path** (INFERRED overlap) |
| ProductNode | `app/agent/nodes/product_node.py` | `run_optimization_stage` | Yes (`productRecommendations`) | **IMPLEMENTED** |
| PackageNode | `app/agent/nodes/package_node.py` | marker only `deferred_to: export` | Packages built in assembler | **IMPLEMENTED** (stub) |
| Assessment / Report / Confidence / Evidence / Validation / Trace | `app/agent/nodes/*` | graph bookkeeping | Mostly debug | **IMPLEMENTED** |
| ExportNode | `app/agent/nodes/export_node.py` | `assemble_frontend_response` | **Yes — public contract** | **IMPLEMENTED** |

`AssessmentResult.to_analyze_dict()` returns **only** `legacy_json`. Typed `activities` / `grooming` on `AssessmentResult` are **not** the HTTP body (VERIFIED).

### 5.4 Parallel / non-hot-path “engines”

| FILE | SYMBOL | On analyze path? | STATUS |
|---|---|---|---|
| `repository/engine/*` | `BiologyEngineService`, etc. | **No** (`app/` does not import it) | **LEGACY** (skeletal; `tests/engine/test_engine_layer_boundaries.py`) |
| `app/inference/*` | wrappers / formula registry | Not the analyze orchestrator | **PARTIAL** |
| `app/science/diff_engine.py` | ScientificDiffEngine | Not on analyze path | **UNCLEAR / offline** |
| Greedy `_optimize_essential/_balanced/_optimal` | `app/agent/package_optimizer.py` | **Not called** (only defined) | **LEGACY / dead** |
| `AgentHealthEngine` | — | Not in tree | **MISSING** (tests assert absence) |

---

## 6. Canonical dog input vs persistent dog state

### 6.1 Engine DTO — DogProfileInput

| Field | Value |
|---|---|
| FILE | `app/agent/state.py` |
| SYMBOL | `DogProfileInput` |
| PURPOSE | Normalized invocation input for the graph |
| INPUT | Built by HTTP adapters or `project_to_dog_profile_input` |
| OUTPUT | Fields consumed by stages |
| DEPENDENCIES | Pydantic |
| TESTS | `tests/architecture/test_dog_profile_contract.py` |
| STATUS | **IMPLEMENTED** |

Fields (VERIFIED): `name`, `primary_breed`, `secondary_breed`, `breed_split_pct`, `age_years`, `weight_kg`, `current_environment`, `activity_level`, `sex`/`gender`, `birthday`, `height_cm`, `bcs`, `observed_conditions`, `monthly_budget`.

This **is** the closest thing to “canonical dog state” for a single analysis. There is **not** a separate in-engine CanonicalDog object.

### 6.2 Persistent application state

| Field | Value |
|---|---|
| FILE | `app/state/` (`store.py`, `models.py`, `projection.py`, `db.py`) |
| SYMBOL | `PersistentDog`, `PreferenceRecord`, `AnalysisRecord` |
| PURPOSE | Cross-session identity, events, preferences, analysis **digests** |
| INPUT | HTTP dog APIs |
| OUTPUT | SQLite (`WAGGY_STATE_PATH`, default `var/waggy_state.sqlite`) |
| DEPENDENCIES | Must not write warehouse |
| TESTS | `tests/state/test_omega17_*_contracts.py`, `tests/api/test_omega17_1_dogs.py` |
| STATUS | **IMPLEMENTED** |

**CONFLICT (VERIFIED, not silent-chosen):** Two representations exist **by design**:

- `DogProfileInput` = engine input  
- `PersistentDog` = application store  

Projection: `PersistentDog` → `dog_to_workbench_body` → `profile_from_workbench_body` → `DogProfileInput`.

Ω11 `CanonicalDogInput` (`app/contracts/agent/input.py`) is a **typed contract**, not the runtime DTO (VERIFIED: engine uses `DogProfileInput`).

### 6.3 Profile adapters

| SYMBOL | FILE | Behavior | STATUS |
|---|---|---|---|
| `profile_from_workbench_body` | `app/api/payload_adapter.py` | Fail-closed; optional `as_of_date` for birthday age | **IMPLEMENTED / CANONICAL HTTP** |
| `profile_from_analyze_body` | same | Silent defaults | **IMPLEMENTED / LEGACY HTTP** |
| `age_years_from_birthday` | same | Uses `datetime.now` if `as_of` omitted | **IMPLEMENTED** (documented nondeterminism) |

---

## 7. Scientific warehouse

### 7.1 Loader

| Field | Value |
|---|---|
| FILE | `app/data/loader.py`, `app/data/warehouse_biology.py`, `app/data/repository.py` |
| SYMBOL | `load_all_tables`, `is_biology_warehouse`, `DataPlatform` / `DataRepository` |
| PURPOSE | Load CSVs into in-memory tables; no scoring in the repository itself |
| INPUT | `resolve_clinical_root()` → `warehouse/` unless `PPIE_DATA_DIR` |
| OUTPUT | DataFrames, `version`, `csv_hash` |
| DEPENDENCIES | `config.settings.warehouse_root` |
| TESTS | `tests/warehouse/test_warehouse_interface.py`, `tests/interface/test_omega10_warehouse_health.py` |
| STATUS | **IMPLEMENTED** with config drift |

**VERIFIED load order** (`load_all_tables`):

1. If `warehouse/science` native warehouse → native loader, optionally merge biology  
2. Else if `warehouse/biology/breeds.csv` exists → **`load_biology_warehouse`**  
3. Else historical `breed_analysis` / manifest files  

This workspace: **no** `warehouse/science/` at warehouse root → path 2.

`warehouse/manifest.yaml` still says `root: warehouse/science` and `version: "5.0.0-science"` — **not** the biology fallback path. STATUS of manifest: **PARTIAL / stale**.

### 7.2 Canonical science CSVs used by health (VERIFIED comments + files)

`warehouse/biology/`: `breeds.csv`, `breed_traits.csv`, `observed_breed_conditions.csv`, `trait_condition_associations.csv`, `conditions.csv`, `environment_facts.csv`, plus `*_NEEDS_VALIDATION.csv`.

`warehouse/prevention/`: `condition_ingredients.csv`, `condition_activities.csv`.

`warehouse/commercial/`: product master/recipe/feeding/pricing (several `*_NEEDS_VALIDATION`).

`warehouse/recovery_original/`: historical snapshots. **LEGACY / READ-ONLY archive.** Must not be treated as the runtime store.

`warehouse/current/`: historical pointer; `app/core/paths.py` says **not used for loading**.

`warehouse/validation/actual_clinical_cases.csv` has a `dog_id` column (INFERRED from prior audits / naming). That is validation cases, not runtime per-dog scores. **UNCLEAR** without opening the CSV this session; do not treat as personalized warehouse knowledge.

Dog-specific risk scores, package rankings, and recommendations are **not** stored as warehouse science; they are engine outputs / SQLite digests (VERIFIED architecture).

### 7.3 Demo overlay

| Field | Value |
|---|---|
| FILE | `app/data/demo_catalog.py` |
| SYMBOL | `demo_mode_enabled`, overlay of product-domain tables |
| PURPOSE | Synthetic commercial catalog when `WAGTOPIA_DEMO_MODE` is true |
| INPUT | env |
| OUTPUT | In-memory product tables |
| TESTS | `tests/interface/test_demo_catalog.py`, many interface tests force demo on |
| STATUS | **IMPLEMENTED** |

`app/data/demo_breed_care.py` **raises** on use. STATUS: **LEGACY / retired**.

Local `scripts/run_dev.py` turns demo catalog **on** by default (VERIFIED). Production-like tests autouse-delete that env (`tests/conftest.py`).

---

## 8. Breed and trait / observation resolution

### 8.1 Breed

| Layer | FILE | SYMBOL | STATUS |
|---|---|---|---|
| Alias normalize | `app/data/repository.py` + `app/agent/utils.py` | `normalize_breed_name` | **IMPLEMENTED** |
| Row match (biology) | `app/formulas/stages/biological.py` | `run_biological_stage` → `resolve_breed_rows` | **IMPLEMENTED** (this is what Export sees) |
| Graph BreedNode | `app/agent/nodes/breed_node.py` | contains-match after normalize | **DUPLICATE**; output unused by BiologyNode |
| Hardcoded display aliases | `app/data/warehouse_biology.py` `_BREED_ALIASES` | Lab/Golden/GSD | **IMPLEMENTED** (loader projection) |
| Ω12 | `app/normalization/` | `resolve` / mapping catalog | **IMPLEMENTED but isolated** — not called from `payload_adapter`, `engine.py`, or `main.py` analysis path |
| Unknown breed | empty resolved rows / empty care model | fail-closed, no invented pathways | **IMPLEMENTED** (per `scientific_care` / biology empty path) |
| Mixed breed | epidemiology union; mixed_breed flags; no combined fake prevalence | **PARTIAL** (flagged / union, not a blended estimator) |

**CONFLICT (VERIFIED):** BreedNode vs `run_biological_stage`. Downstream health uses biology stage, not BreedNode rows.

### 8.2 Traits / observations

| Mechanism | FILE | STATUS |
|---|---|---|
| Trait → condition risks | `app/formulas/stages/health_risk.py` `compute_risks` | **IMPLEMENTED** |
| Groomer observation boosts | `resolve_groomer_boosts` in `health_risk.py` | **IMPLEMENTED** (sort/priority flags, not invented %) |
| `DogProfileInput.observed_conditions` | input list | **IMPLEMENTED** |
| `resolve_care_model(..., observations)` | `scientific_care.py` **`del observations`** | **IMPLEMENTED** — observations **do not** create care-model conditions |
| Hidden groomer merge | `observations_for_legacy_analyze` on `/analyze` and clinical-report | **IMPLEMENTED / LEGACY path only**; workbench docs say no hidden session merge |

---

## 9. Health analysis

| Field | Value |
|---|---|
| FILE | `app/formulas/stages/health_risk.py` (RiskNode); `app/data/scientific_care.py` (package care scoring) |
| SYMBOL | `compute_risks`; `resolve_care_model` |
| PURPOSE | Preventative considerations from warehouse breed/trait/condition rows |
| INPUT | `DataRepository` + `DogProfileInput` |
| OUTPUT | `health_risk.risks` → assembler `healthInsights`; careModel for optimizer |
| DEPENDENCIES | biology warehouse tables |
| TESTS | `tests/interface/test_omega10_warehouse_health.py` |
| STATUS | **IMPLEMENTED** as preventative analysis, **not** a diagnosis engine |

**CONFLICT (VERIFIED):** Two health-related builders:

1. **RISK_V2_1** `compute_risks` — FormulaGraph health insights on the public analyze payload.  
2. **`resolve_care_model`** — called from `run_package_search` for package care scoring. Explicitly ignores observations.

They share warehouse tables but are not the same function.

Empty warehouse hits → `NOT_AVAILABLE` / empty model (VERIFIED in `resolve_care_model`). No Labrador/Golden invention via retired demo_breed_care.

---

## 10. Nutrition

Three builders exist (VERIFIED). Do not collapse them.

| Builder | FILE | Consumes | Used for | STATUS |
|---|---|---|---|---|
| Clinical condition → ingredient/nutrient targets | `app/formulas/stages/nutrition.py` `run_nutrition_stage` | epidemiology priorities + `condition_ingredients` | NutritionNode / matcher inputs | **IMPLEMENTED** |
| Ingredient dose mapping | `app/agent/ingredient_engine.py` `map_ingredients` | risks + weight | assembler `rawIngredients` / nutritionalTargets | **IMPLEMENTED** |
| AAFCO-style requirement profile | `app/data/scientific_requirements.py` `build_requirement_profile` | **weight + age only** (not breed); **not warehouse CSV** | `run_package_search` when demo mode | **IMPLEMENTED** (secondary source); **PARTIAL** off-demo (`insufficient_product_nutrient_data` stub in package_search — INFERRED from prior code comments, confirmed by `package_search` demo branch in audit) |

`scientific_requirements.py` docstring states values are **not** warehouse-authoritative AAFCO tables (VERIFIED).

Public workbench nutrition slice: `canonical.scientific_analysis.nutrient_targets` ← `analyze.nutritionalTargets` (VERIFIED `http_models.DEVELOPER_JSON_PATHS` + `build_canonical_result`).

---

## 11. Activity analysis

**Desired:** a domain engine from canonical dog + evidence.  
**Actual:**

| Piece | FILE | In HTTP analyze JSON? | STATUS |
|---|---|---|---|
| Profile field `activity_level` | `DogProfileInput` | Echoed on profile | **IMPLEMENTED** (input, not analysis) |
| ActivityNode | `activity_node.py` | `management` passed to assembler; **`management` never referenced in assembler body** | **PARTIAL** |
| Heuristic activity plan | `response_assembler.build_activity_recommendations` | Yes — `activityRecommendations` (minutes from breed energy/age; hardcoded activity lists) | **IMPLEMENTED** (not warehouse condition_activities) |
| Lifestyle rows | `build_preventative_nutrition_system` re-queries `repo.condition_activities()` | Yes — nested preventative system | **IMPLEMENTED** / **DUPLICATE** of ActivityNode intent |
| Clinical assessment activity module | `clinical_assessment._activity_module` | Projection of `activityRecommendations` | **IMPLEMENTED** (projection) |

**MISSING:** a single activity engine whose node output is the public activity result.

Hardcoded minute bands (75/60/45) and activity name lists in `build_activity_recommendations` are **not** warehouse rows (VERIFIED).

---

## 12. Grooming analysis

| Piece | FILE | In HTTP analyze JSON? | STATUS |
|---|---|---|---|
| GroomingNode | `grooming_node.py` | No (not ExportNode dependency) | **PARTIAL** |
| `groomer[]` checklist | `response_assembler.py` | Yes — maps `observed_conditions` to fixed fields | **IMPLEMENTED** (observation flags, not a grooming engine) |
| Report `_grooming` | `app/data/report_generator.py`, `clinical_report_builder.py` | Clinical report path | **IMPLEMENTED** (separate projection; loads defs again) |
| Assessment grooming module | `clinical_assessment._grooming_module` | From `analyze.groomer` | **IMPLEMENTED** (projection) |
| Durable groomer events | `app/state/groomer.py` | Application state | **IMPLEMENTED** |

**MISSING:** a grooming reasoning engine that turns coat/skin warehouse facts + dog state into structured grooming analysis on the canonical envelope.

`GroomingNode` currently dumps **all** `grooming_observation_defs` rows (VERIFIED) — not dog-specific.

---

## 13. Product catalog and matching

### 13.1 Catalog

Runtime catalog = `DataRepository` product tables, optionally **demo overlay**. Commercial CSVs under `warehouse/commercial/`.

### 13.2 PRODUCT_MATCH_V2_1

| Field | Value |
|---|---|
| FILE | `app/formulas/stages/optimization.py` |
| SYMBOL | `run_optimization_stage`, `_match_products_for_target` |
| PURPOSE | Per-nutrient-target catalog knapsack / fulfillment |
| INPUT | NutritionNode targets + catalog |
| OUTPUT | reports / feeding_plan → `productRecommendations` |
| TESTS | interface optimizer / package tests (indirect) |
| STATUS | **IMPLEMENTED** |

Presentation explicitly records that **packages do not consume** `productRecommendations` (`app/presentation/adapter.py` `does_not_consume`).

Empty matcher is treated as commercial-input limitation, not invented products (VERIFIED warning strings in `build_canonical_result`).

### 13.3 HTTP evidence helper (not the optimizer)

| FILE | `app/api/evidence.py` |
|---|---|
| SYMBOL | `match_products_for_ingredients`, `get_products_for_condition` |
| STATUS | **IMPLEMENTED** / **DUPLICATE matcher family** for research routes |

---

## 14. Package optimization

| Field | Value |
|---|---|
| FILE | `app/agent/package_optimizer.py`, `app/agent/package_search.py` |
| SYMBOL | `build_optimized_packages` → **`run_package_search`** |
| PURPOSE | Exhaustive/bounded combination search; Essential / Balanced / Optimal |
| INPUT | Candidate products, profile (budget), repo, care model, requirement profile |
| OUTPUT | `wellnessPackages` / `packageOptions` + `optimizerProvenance` (`llm_used: false` expected by architecture tests) |
| DEPENDENCIES | `catalog_eligibility.apply_active_constraints` (Ω17.2) |
| TESTS | `tests/test_package_optimizer.py`, `tests/interface/test_package_combinatorial_optimizer.py`, `tests/optimization/test_exhaustive_bundle_ranking.py` |
| STATUS | **IMPLEMENTED** |

Invariant **one ranked package per tier** is stated in `build_optimized_packages` docstring (“Compatibility: one package per tier”) (VERIFIED).

Greedy `_optimize_*` functions remain in the same file and are **uncalled** (VERIFIED grep: definitions only).

`PackageNode` does **not** run the optimizer (VERIFIED).

---

## 15. Evidence and provenance

| Source | FILE | Payload | STATUS |
|---|---|---|---|
| Per-risk ledgers | `health_risk.py` | `debug.formula_executions` | **IMPLEMENTED** |
| Package search ledger | `package_search.py` | `optimizerProvenance`, package `formula_execution` | **IMPLEMENTED** |
| Quote list | `response_assembler.collect_evidence` | `scientificEvidence` | **IMPLEMENTED** |
| Science graph attach | `app/science/attach.py` | `debug.science`, evidence objects | **IMPLEMENTED** (best-effort) |
| Canonical view | `build_canonical_result` | `scientific_analysis.evidence`, package provenance | **IMPLEMENTED** (projection) |
| Recalculation | `app/state/recalculation.py` | `waggy_recalculation_explanation.v1` | **IMPLEMENTED** |
| Analysis signature | `presentation/adapter.py` `analysis_signature` | envelope + persist | **IMPLEMENTED** |
| Versions | engine `2.1.0`, warehouse `DataRepository.version`, HTTP `v1` | headers + body | **IMPLEMENTED** |
| Ω11 ProvenanceRecord | `app/contracts/agent/provenance.py` | types | **PARTIAL** (not the live envelope schema) |

Persisted SQLite `result_digest` stores finding titles, package product ids, `recommendation_snapshot` — **not** full evidence quotes (VERIFIED Ω17.4 adapters / `app/state/projection.py`). Tool health slices therefore report `NOT_AVAILABLE` for evidence.

---

## 16. Recalculation, comparison, preferences

| FILE | SYMBOL | Engine? | STATUS |
|---|---|---|---|
| `app/state/recompute.py` | `apply_preference_change`, `effective_profile` | Prepares then HTTP runs engine | **IMPLEMENTED** |
| `app/state/package_constraints.py` | `validate_preference_value`, `constraints_from_dog` | Eligibility only | **IMPLEMENTED** |
| `app/agent/catalog_eligibility.py` | `apply_active_constraints` | Before `run_package_search` | **IMPLEMENTED** |
| `app/state/recalculation.py` | `explain_from_digests` | **No** | **IMPLEMENTED** |
| `app/api/main.py` compare route | stored digest diff | **No** | **IMPLEMENTED** |

No AI mutation tool for preferences (VERIFIED Ω17.4 `propose_preference` only).

---

## 17. Versioning (do not conflate)

| Constant | FILE | Value / role | STATUS |
|---|---|---|---|
| `ALGORITHM_VERSION` | `app/agent/version.py` | `"2.1.0"` engine | **IMPLEMENTED** |
| `HTTP_API_VERSION` | `app/api/http_models.py` | `"v1"` OpenAPI | **IMPLEMENTED** |
| `ALGORITHM_VERSION` | `app/data/report_schema.py` | `"PPIE"` **different meaning** | **DUPLICATE name** |
| Dog-state schemas | `app/state/version.py` | `waggy_dog_state.v1` etc. | **IMPLEMENTED** |
| Tool contract | `app/tools/version.py` | `1.0` / `waggy_tool_result.v1` | **IMPLEMENTED** |
| Warehouse | loader meta / manifest | e.g. `5.0.0-science` label | **PARTIAL** (manifest root stale) |
| Ω11 | `app/contracts/agent/versions.py` | reuses engine ALGORITHM_VERSION | **IMPLEMENTED** (types) |

---

## 18. Configuration and security (audit only)

| Item | FILE | Fact | STATUS |
|---|---|---|---|
| Warehouse root | `config/settings.py`, `app/core/paths.py` | `WAGGY_WAREHOUSE_ROOT` or `warehouse/`; `PPIE_DATA_DIR` overrides | **IMPLEMENTED** |
| CORS | `app/api/main.py` | `allow_origins=["*"]` | **IMPLEMENTED** (open) |
| `API_KEYS` | `app/api/main.py` | Optional; workbench not gated | **PARTIAL** prototype |
| Surface keys | business/developer env | Optional | **PARTIAL** |
| Secrets in frontend | tests | Forbid hardcoded keys | tests exist; **frontend tree missing** |
| SQLite | `WAGGY_STATE_PATH` | Prototype; no production auth | **PARTIAL** |
| `.env.example` | root | Placeholders including unused JWT-style names | **UNCLEAR** whether those vars are wired to FastAPI |

Debug routes under `/api/v1/ppie/*` and `/debug/calculation` expose execution internals when debug flags allow (VERIFIED route list).

---

## 19. AI / agent boundary

| Field | Value |
|---|---|
| FILE | `app/ai/agent.py`, `app/tools/gateway.py` |
| SYMBOL | `WaggyExplanationAgent.explain`; `WaggyToolGateway.invoke` |
| PURPOSE | Explain / allowlisted reads; **not** scientific authority |
| INPUT | Canonical envelope or tool arguments |
| OUTPUT | `waggy_ai_response.v1` / `waggy_tool_result.v1` |
| DEPENDENCIES | FakeProvider default; Gemini optional |
| TESTS | `tests/ai/*`, `tests/tools/*`, `tests/api/test_omega17_ai.py`, `tests/api/test_omega17_4_tools.py` |
| STATUS | **IMPLEMENTED** (bounded). Chat UI **MISSING**. MCP **MISSING**. |

Tools do not import engine/warehouse/SQLite (isolation tests exist). They read stored digests; they do **not** run the core brain.

Ω11 `FUTURE_TOOL_REGISTRY` remains **non-executing** (`app/contracts/agent/registry.py`). Name overlap with executable `analyze_health` / `calculate_nutrition` in `app/tools/` is **DUPLICATE naming**, different modules.

---

## 20. Presentation vs frontend

| Layer | FILE | Computes science? | STATUS |
|---|---|---|---|
| Presentation adapter | `app/presentation/adapter.py` | **No** | **IMPLEMENTED** |
| Clinical assessment split | `app/data/clinical_assessment.py` | **No** (frozen analyze) | **IMPLEMENTED** |
| `waggy-frontend/` | expected by `app/api/main.py` `_frontend_root` | Intended HTTP-only | **MISSING on disk** |
| `legacy/archive/frontend/` | archive | No | **LEGACY** |
| `legacy/debug/calculation.html` | debug explorer | Consumes debug API | **IMPLEMENTED** debug UI |
| Streamlit `app/ui/` | in-process engine | Yes (calls agent) | **LEGACY / DUPLICATE** |

**CONFLICT (VERIFIED):** Product HTTP API can return `workbench_presentation.v1` without any frontend. Serving `GET /` depends on missing `waggy-frontend/index.html`.

---

## 21. Canonical dog fixture (Dolly) — CONFLICT

Do not invent a new dog. Existing fixtures disagree:

| Location | Breed order / age / weight / environment | Class |
|---|---|---|
| `WORKBENCH_EXAMPLE_REQUEST` in `http_models.py` | Labrador × Golden, birthday 2021-04-15, `as_of_date` 2026-09-09, weight 30, Temperate Outdoor, Moderate, joint_stiffness + itching | VERIFIED HTTP example |
| `app/ui/renderer/navigation.py` `default_profile()` | Golden × Labrador, age 3.0, 28 kg, Shanghai Summer, High | VERIFIED Streamlit |
| `tests/golden/dolly.json` | Golden snapshot for parity | VERIFIED file exists (content not fully re-read) |
| Widespread test `_dolly()` / `_profile()` helpers | Usually Labrador, 5.4 years, 30 kg, Temperate Outdoor | VERIFIED in Ω17 tests |

Treat **HTTP workbench example** as the canonical *API* fixture for later phases unless tests freeze `tests/golden/dolly.json`.

---

## 22. End-to-end trace (conceptual Dolly on workbench)

Using `WORKBENCH_EXAMPLE_REQUEST` as the existing canonical HTTP fixture.

| Step | Desired brain | Actual code | STATUS |
|---|---|---|---|
| 1 raw input | JSON body | `WorkbenchRequest` | **IMPLEMENTED** |
| 2 dog profile | canonical state | `profile_from_workbench_body` → `DogProfileInput` | **IMPLEMENTED** |
| 3 breed resolution | Ω12 + warehouse IDs | `run_biological_stage` + alias normalize; **Ω12 not used** | **PARTIAL** |
| 4 trait/observation | canonical concepts | `compute_risks` + `observed_conditions`; care model ignores observations | **PARTIAL** |
| 5 canonical dog state | one internal object | `DogProfileInput` only for the run; SQLite if `dog_id` | **PARTIAL** (two layers) |
| 6 health | warehouse + rules | `compute_risks` → `healthInsights`; plus `resolve_care_model` inside package search | **IMPLEMENTED** (split) |
| 7 nutrition | from health | `run_nutrition_stage` + `map_ingredients` + optional requirement profile | **IMPLEMENTED** (split) |
| 8 activity | evidence-backed | heuristic `activityRecommendations` + unused ActivityNode | **PARTIAL** |
| 9 grooming | evidence-backed | observation checklist; unused GroomingNode | **PARTIAL** |
| 10 product matching | after needs | `PRODUCT_MATCH_V2_1` **independent of packages** | **IMPLEMENTED** (by design split) |
| 11 packages | optimizer | `run_package_search` in assembler | **IMPLEMENTED** |
| 12 evidence | machine-readable why | scientificEvidence + debug + optimizerProvenance | **IMPLEMENTED** (rich debug; digest persistence lossy) |
| 13 provenance | versions + signature | engine/warehouse/signature on envelope | **IMPLEMENTED** |
| 14 API | stable workbench | `POST /api/v1/presentation/workbench` | **IMPLEMENTED** |
| 15 external client without importing core | frontend HTTP | **frontend directory missing**; API itself is callable | **PARTIAL** |

---

## 23. Tests (inventory only — not executed this phase)

Representative suites mapped to components:

| Area | Paths |
|---|---|
| Workbench / Ω16 | `tests/api/test_omega16_*.py`, `tests/interface/test_unified_workbench.py` |
| Pipeline / graph | `tests/test_agent_pipeline.py`, `tests/test_formula_graph.py`, `tests/pipeline/test_pipeline_architecture.py` |
| Warehouse health | `tests/interface/test_omega10_warehouse_health.py`, `tests/warehouse/` |
| Packages | `tests/test_package_optimizer.py`, `tests/interface/test_package_combinatorial_optimizer.py`, `tests/optimization/` |
| Dog state / recompute | `tests/state/test_omega17_*.py`, `tests/api/test_omega17_1_*.py`, `test_omega17_2_recompute.py`, `test_omega17_3_recompute.py` |
| AI / tools | `tests/ai/`, `tests/tools/`, `tests/api/test_omega17_ai.py`, `tests/api/test_omega17_4_tools.py` |
| Frontend isolation | `tests/interface/test_frontend_consolidation.py`, `test_omega17_4_frontend_isolation.py` — **would require missing tree** |
| Ω11 / Ω12 | `tests/contracts/`, `tests/normalization/`, `tests/architecture/test_omega12_boundaries.py` |
| Golden | `tests/golden/*.json` |
| Isolation | `tests/architecture/test_omega17_1a_scientific_isolation.py`, `test_omega17_4_tool_isolation.py` |

`tests/conftest.py` skips a frozen set of DataPlatform tests when `warehouse/current/product_portfolio` is empty (VERIFIED).

---

## 24. Legacy / duplicate / extra trees

| Path | Role | STATUS |
|---|---|---|
| `legacy/` | Archived UIs + debug explorer | **LEGACY** |
| `app/ui/` Streamlit + CSTC | Alternate consumers | **LEGACY / DUPLICATE** |
| `repository/engine/` | Skeletal services for MAT tests | **LEGACY** (not PACKAGE_OPTIMIZER) |
| `repository/` mathematics/optimization | MAT stack; not package composer | **IMPLEMENTED** off hot path |
| `app/contracts/agent/` | Ω11 types | **IMPLEMENTED** types only |
| `app/normalization/` | Ω12 | **IMPLEMENTED** isolated |
| `CSTC_1524/` | Unrelated PetCarePro tree on disk | **UNKNOWN / LEGACY** |
| `authoring/`, `curation/`, `ontology/`, `science_pipeline/` | Staging / research | **PARTIAL / UNCLEAR** vs hot path |
| Dead `_optimize_*` in `package_optimizer.py` | Old greedy composer | **LEGACY** |
| `demo_breed_care.py` | Retired | **LEGACY** |

Do not delete these in later phases without an explicit migration instruction.

---

## 25. Gaps vs “complete Waggy Core Brain”

These are **not** implementation tasks for this phase. They are the forensic punch list.

| ID | Gap | Evidence class |
|---|---|---|
| G1 | ActivityNode unused by assembler; public activity is heuristic | VERIFIED |
| G2 | GroomingNode unused by ExportNode; public grooming is observation flags | VERIFIED |
| G3 | Two health builders (`compute_risks` vs `resolve_care_model`) | VERIFIED |
| G4 | Three nutrition builders | VERIFIED |
| G5 | Matcher vs optimizer independence | VERIFIED |
| G6 | Ω12 not on HTTP/engine path | VERIFIED |
| G7 | Dual HTTP input contracts | VERIFIED |
| G8 | Manifest `warehouse/science` missing; biology fallback | VERIFIED |
| G9 | `waggy-frontend/` missing on disk | VERIFIED |
| G10 | Streamlit bypasses workbench validation | VERIFIED |
| G11 | Multiple Dolly fixtures | VERIFIED |
| G12 | Analysis persistence is digest-lossy vs full envelope | VERIFIED |
| G13 | Prototype auth / open CORS / ungated workbench | VERIFIED |
| G14 | README still contradicts AI implementation in places | VERIFIED |
| G15 | `report_schema.ALGORITHM_VERSION = "PPIE"` name clash | VERIFIED |
| G16 | Birthday age without `as_of_date` uses `datetime.now` | VERIFIED |
| G17 | Whether non-demo catalog has enough nutrient data for optimizer | UNCLEAR without a live run (Phase 3/11) |
| G18 | Whether golden `dolly.json` still matches ALGORITHM_VERSION 2.1.0 output | UNCLEAR without running parity |

**MISSING EVIDENCE (do not guess in later phases):**

- Live workbench JSON for Dolly in this workspace (engine not executed this session).  
- Whether `waggy-frontend` was never committed or was deleted after Ω17.4-FE docs were written.  
- Whether `CSTC_1524` is intentional reference or accidental copy.  
- Exact row counts / NEEDS_VALIDATION tallies in current CSVs (not recounted here).

---

## 26. What later phases must not do (from this map)

- Do not add a second `generate_reproducible_report`.  
- Do not put health math in `app/api/main.py` or `app/presentation/adapter.py`.  
- Do not wire Ω12 by inventing mappings.  
- Do not invent warehouse science to fill empty health.  
- Do not treat `repository/engine` or Streamlit as the canonical API.  
- Do not expose SQLite or CSV paths through AI tools.  
- Do not “fix” activity/grooming by copying generic pet-care advice into the assembler.

---

## 27. Suggested phase alignment (for humans; not auto-advanced)

| Recommended phase | This map’s primary evidence |
|---|---|
| 2 Canonical data-flow | §3, §22 |
| 3 Baseline tests | §23 (must run) |
| 4 Warehouse integrity | §7, G8 |
| 5 Breed + trait | §8, G6 |
| 6 Canonical dog state | §6, G11 |
| 7 Health | §9, G3 |
| 8 Nutrition | §10, G4 |
| 9 Activity + grooming | §11–12, G1–G2 |
| 10 Product matching | §13, G5 |
| 11 Packages | §14 |
| 12 Evidence | §15, G12 |
| 13 Determinism | G16, golden suite |
| 14–16 Workbench/API/tests | §4, G7, G9 |
| 17 Security | §18 |
| 18 AI gateway | §19 |
| 19 Black-box client | G9 |

STOP. Wait for the next explicit phase instruction.
