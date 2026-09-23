# Waggy Canonical Data-Flow and Gap Analysis

**Phase:** 2 — analysis only  
**Date:** 2026-09-18  
**Workspace:** `c:\Users\Admin\Downloads\waggy`  
**Starting evidence:** `docs/WAGGY_CORE_FORENSIC_MAP.md` (Phase 1)  
**Method:** Source, tests, schemas, imports, and existing docs. No production code, tests, scientific CSVs, API schemas, configuration, or legacy code were modified. The pytest suite was **not** executed (that is Phase 3). FormulaGraph order in §3 is **VERIFIED** by applying `FormulaGraph.order()` (Kahn; alphabetical ready-set) in `app/agent/formula_graph.py` to the `dependencies` lists declared on the 18 node classes. Tests freeze only a subset of that order.

**Claim labels**

| Label | Meaning |
|---|---|
| VERIFIED | Observed in source, tests, or on-disk paths |
| INFERRED | Follows from the call graph; not proven by a live run this session |
| UNCLEAR | Insufficient evidence |
| MISSING | Searched; not present or not wired |

If this file and runtime disagree later, **runtime wins**.

---

## 1. Executive summary

**Primary question:** Can the existing pipeline be represented as

```
Dog input → canonical resolution → canonical dog state → health → nutrition
→ activity → grooming → product matching → package optimization
→ evidence/provenance → canonical result → API
```

**Answer: NO.** The repository already has **one** scientific/recommendation choke point (`PPIEWellnessAgent.generate_reproducible_report`). It does **not** execute as that linear “Core Brain.” The actual hot path is a FormulaGraph whose public JSON is assembled **after** most nodes, and several named stages are either unused, duplicated, or independently recomputed. **VERIFIED.**

What **is** already true:

- HTTP workbench does not contain a second engine. **VERIFIED**
- Presentation, clinical assessment, AI explain, and tools wrap `legacy_json` or a **lossy digest**, they do not recompute formulas. **VERIFIED**
- Product matching and package membership are **intentionally independent** (code `del product_recs`; tests freeze `independent_of_product_match is True`). **VERIFIED**
- Ω12 exists and tests **forbid** engine/optimizer imports of it. **VERIFIED**

Exact breakpoints vs the desired linear brain:

| Desired arrow | Actual | Status |
|---|---|---|
| Dog input → canonical resolution | HTTP adapters produce `DogProfileInput` as **free-text names**. Ω12 / BreedNode IDs are not that resolution. | **PARTIAL** |
| Canonical dog state | Engine consumes `DogProfileInput`. Persistence uses `PersistentDog`. Ω11 `CanonicalDogInput` is unused on the hot path. | **DUPLICATE** representations |
| Health | `compute_risks` drives public `healthInsights`. `resolve_care_model` scores packages. | **DUPLICATE** |
| Nutrition | `run_nutrition_stage` → matcher; `map_ingredients` → public targets (recomputed in assembler); `build_requirement_profile` → demo package minima only. | **DUPLICATE** / **PARTIAL** |
| Activity | `ActivityNode` runs; assembler **ignores** `management`; public activity is a breed-energy heuristic. | **MISSING** (node→API) |
| Grooming | `GroomingNode` loads all observation defs; **not** an ExportNode dependency; public `groomer` is a hardcoded checklist vs `observed_conditions`. | **MISSING** (node→API) |
| Product matching → packages | Matcher output is **discarded** by `build_optimized_packages`. | **MISSING** (and test-frozen) |
| Evidence → API | Assembler `scientificEvidence` + debug ledgers are public. `EvidenceNode` bundle is not. Persistence keeps a digest only. | **PARTIAL** |
| Canonical result → API | `ExportNode` `legacy_json` → workbench projection. Presentation `CANONICAL_PIPELINE_STAGES` is a **label list**, not executed code. | **PARTIAL** / **CONFLICT** |

**Do not redesign.** The minimum architectural move is to treat the existing graph + assembler as the engine, then decide **which existing output is authoritative** at each breakpoint — not to add a second pipeline.

---

## 2. Actual runtime call graph

Start: `POST /api/v1/presentation/workbench`.

```
WorkbenchRequest                          app/api/http_models.py
        ↓  extra=allow; fail-closed fields documented on the model
profile_from_workbench_body               app/api/payload_adapter.py
        ↓
DogProfileInput                           app/agent/state.py
        ↓  optional using_package_constraints(constraints_from_dog) if dog_id
PPIEWellnessAgent.generate_reproducible_report
                                          app/agent/engine.py
        ↓
AssessmentAgent.assess                    app/agent/assessment_agent.py
        ↓
FormulaGraph.execute                      18 nodes, Kahn + alphabetical ready-set
        ↓
ExportNode.assemble_frontend_response     app/agent/response_assembler.py
        ↓  inside assembler
map_ingredients (again)
build_optimized_packages → run_package_search
build_activity_recommendations (heuristic)
hardcoded groomer checklist
        ↓
legacy_json  (public analyze dict)
        ↓  AssessmentAgent try/except attach_science_to_analyze (additive)
to_analyze_dict() == legacy_json only
        ↓
build_clinical_assessment                 app/data/clinical_assessment.py  NO RECOMPUTE
        ↓
build_workbench_presentations             app/presentation/adapter.py
        ↓
workbench_presentation.v1
        ↓  if dog_id
persist_workbench_run → result_digest     app/state/service.py
```

**VERIFIED** from `app/api/main.py` `presentation_workbench` → `_run_workbench_analysis`.

### 2.1 Step records

#### HTTP bind

FILE: `app/api/http_models.py`  
SYMBOL: `WorkbenchRequest`  
INPUT: JSON body. `extra="allow"`. Example is `WORKBENCH_EXAMPLE_REQUEST`.  
OUTPUT: Pydantic model dumped to dict.  
ACTUAL RESPONSIBILITY: HTTP DTO. Comments state it is **not Ω12-resolved**.  
DOWNSTREAM CONSUMERS: `presentation_workbench`.  
TESTS: `tests/api/test_omega16_openapi.py`, `tests/api/test_omega16_1_hardening.py`, `tests/interface/test_unified_workbench.py`.  
STATUS: **IMPLEMENTED** (DTO). Canonical application request **VERIFIED** in the class docstring.

#### Profile adapter

FILE: `app/api/payload_adapter.py`  
SYMBOL: `profile_from_workbench_body`  
INPUT: workbench dict (including `role_context.groomer.observed_conditions` merged into observations).  
OUTPUT: `DogProfileInput`. Raises `WorkbenchInputError` on missing breed / age-or-birthday / weight / activity / environment.  
ACTUAL RESPONSIBILITY: Fail-closed mapping. Age from birthday uses `as_of_date` if present, else `datetime.now`. Does **not** resolve warehouse IDs.  
DOWNSTREAM CONSUMERS: `_run_workbench_analysis`; also `project_to_dog_profile_input`.  
TESTS: `tests/api/test_omega16_1_hardening.py`, `tests/api/test_omega16_api_contract.py`.  
STATUS: **IMPLEMENTED**. Intended canonical HTTP adapter **VERIFIED** (module docstring + WorkbenchRequest docstring).

#### Engine choke point

FILE: `app/agent/engine.py`  
SYMBOL: `PPIEWellnessAgent.generate_reproducible_report`  
INPUT: `DogProfileInput`  
OUTPUT: `result.to_analyze_dict()` which is **`legacy_json` only**. Typed `AssessmentResult` fields (activities, grooming, evidence node bundle) are **not** returned to HTTP.  
ACTUAL RESPONSIBILITY: Single scientific/recommendation entry. Streamlit `run_engine` calls `asyncio.run(generate_reproducible_report)` — **not** the unused `generate_reproducible_report_sync` helper. **VERIFIED.**  
DOWNSTREAM CONSUMERS: workbench, `/api/v1/analyze`, three-surfaces, clinical-report, ppie assess/trace/console, legacy `/api/recommendations`, Streamlit, CSTC adapter, many tests.  
TESTS: `tests/test_formula_graph.py`, `tests/test_package_optimizer.py`, interface workbench tests.  
STATUS: **IMPLEMENTED**.

**CONFLICT (VERIFIED vs source comment):** The class docstring lists `Profile → Breed → Biology → Risk → Epidemiology → Activity → Nutrition → Ingredient → Product → Package → Assessment → Report → Validation → Trace → Export` and **omits Grooming, Confidence, Evidence**. Actual scheduling inserts those three (see §3). Runtime code wins. The docstring also names Package as if it composed packages; `PackageNode` only sets `deferred_to: "export"`.

#### AssessmentAgent

FILE: `app/agent/assessment_agent.py`  
SYMBOL: `AssessmentAgent.assess`  
INPUT: `DogProfileInput` in `ExecutionContext`  
OUTPUT: `AssessmentResult` then science attach into `legacy_json` / `debug` / `evidence` (try/except; failure preserves clinical result).  
ACTUAL RESPONSIBILITY: Graph owner. Science attach is **additive explainability**, not a second optimizer.  
DOWNSTREAM CONSUMERS: engine.  
TESTS: `tests/test_formula_graph.py`, `tests/test_validation_console.py`.  
STATUS: **IMPLEMENTED**.

#### FormulaGraph

FILE: `app/agent/formula_graph.py`  
SYMBOL: `FormulaGraph.execute`  
INPUT: `default_nodes()` membership  
OUTPUT: filled `ExecutionContext.outputs`; `runtime["graph_order"]`  
ACTUAL RESPONSIBILITY: Only scheduler. Nodes never call each other. Ready-set is **sorted alphabetically**.  
DOWNSTREAM CONSUMERS: all nodes.  
TESTS: `tests/test_formula_graph.py` (`test_graph_toposort_deterministic`).  
STATUS: **IMPLEMENTED**.

#### Export / assembler

FILE: `app/agent/nodes/export_node.py` → `app/agent/response_assembler.py`  
SYMBOL: `ExportNode.execute` / `assemble_frontend_response`  
INPUT: ExportNode **requires** biology, epidemiology, nutrition, activity, product, risk, report (plus trace/validation for scheduling). It passes `epidemiology`, `nutrition`, `feeding_plan`, and `management` into `assemble_frontend_response`. **None of those four parameters is read in the assembler body** (grep: only the function signature). Public JSON is built from `profile`, `biology`, `health_risk`/`risks`, ProductNode `reports`, and `repo`. **Not** GroomingNode. **Not** IngredientNode payload (assembler calls `map_ingredients` again). **VERIFIED.**  
OUTPUT: analyze JSON (`healthInsights`, `productRecommendations`, `wellnessPackages`, `activityRecommendations`, `groomer`, `scientificEvidence`, `debug`, …).  
ACTUAL RESPONSIBILITY: Public contract. Recomputes ingredients and packages. Rebuilds activity and grooming.  
DOWNSTREAM CONSUMERS: `to_analyze_dict`, clinical assessment, presentation.  
TESTS: package provenance, workbench, golden README (parity tool **MISSING**).  
STATUS: **IMPLEMENTED** (public). Activity/grooming/epidemiology/nutrition graph inputs **unread** by the assembler. Nutrition still reaches the public matcher via ProductNode `reports`.

#### Package search (inside assembler)

FILE: `app/agent/package_optimizer.py` `build_optimized_packages` → `app/agent/package_search.py` `run_package_search`  
INPUT: candidates, profile, budget, repo. `product_recs` argument is **deleted**.  
OUTPUT: `package_options`, `requirement_profile`, `care_model`, provenance.  
ACTUAL RESPONSIBILITY: Combinatorial package composer (`PACKAGE_OPTIMIZER_V2_1`).  
DOWNSTREAM CONSUMERS: `wellnessPackages` / `packageOptions` on analyze JSON.  
TESTS: `tests/interface/test_package_generation_provenance.py`, `tests/test_package_optimizer.py`.  
STATUS: **IMPLEMENTED**, independent of matcher **VERIFIED**.

#### Clinical assessment

FILE: `app/data/clinical_assessment.py`  
SYMBOL: `build_clinical_assessment`  
INPUT: frozen analyze dict + repo  
OUTPUT: modular report objects (`activity` from `activityRecommendations`, `grooming` from `groomer` list).  
ACTUAL RESPONSIBILITY: Projection. **Does not recompute formulas** (module docstring).  
DOWNSTREAM CONSUMERS: workbench presentations.  
TESTS: `tests/test_validation_console.py`, interface presentation tests.  
STATUS: **IMPLEMENTED** (projection).

#### Presentation

FILE: `app/presentation/adapter.py`  
SYMBOL: `build_workbench_presentations` / `build_canonical_result`  
INPUT: analyze + assessment  
OUTPUT: `workbench_presentation.v1` with `canonical` + `roles.*`. `CANONICAL_PIPELINE_STAGES` copied into developer `pipeline` as **strings**, not executed.  
ACTUAL RESPONSIBILITY: Role projection + `analysis_signature` over a subset of analyze fields (timing stripped). Greeting/`wellness_summary` is **not** in the signature.  
DOWNSTREAM CONSUMERS: HTTP 200 body; persist digest.  
TESTS: `tests/interface/test_unified_workbench.py`, `tests/interface/test_package_generation_provenance.py`.  
STATUS: **IMPLEMENTED**. Pipeline labels **CONFLICT** with FormulaGraph node ids **VERIFIED**.

#### Persist

FILE: `app/state/service.py` `persist_workbench_run`  
INPUT: envelope + profile  
OUTPUT: SQLite `AnalysisRecord` with `result_digest`  
ACTUAL RESPONSIBILITY: Store digest + input snapshot; groomer notes as events. Does not store full `legacy_json`.  
DOWNSTREAM CONSUMERS: tools `compare_analyses`, slices, products adapters.  
TESTS: `tests/state/test_omega17_*.py`.  
STATUS: **IMPLEMENTED** (lossy by design of `result_digest`).

---

## 3. Node-by-node graph

**VERIFIED execution order** (Kahn; alphabetical among ready nodes; unique given these edges):

1. `profile`  
2. `breed`  
3. `biology`  
4. `grooming` (ready with `risk` after biology; `"grooming" < "risk"`)  
5. `risk`  
6. `confidence` (`"confidence" < "epidemiology"`)  
7. `epidemiology`  
8. `activity`  
9. `nutrition`  
10. `ingredient`  
11. `evidence` (`"evidence" < "product"` after ingredient)  
12. `product`  
13. `package`  
14. `assessment`  
15. `report`  
16. `validation` (`"report" < "validation"` when both ready)  
17. `trace`  
18. `export`

**CONFLICT:** `PPIEWellnessAgent` docstring order ≠ this schedule. `tests/test_formula_graph.py::test_graph_toposort_deterministic` freezes `order()[0]=="profile"`, last `"export"`, `risk < nutrition`, `product < export` — **not** this full 18-id list. Phase 3 can print live `debug.formula_graph.order` to confirm the same sequence after warehouse bootstrap.

Kind legend: **reasoning** (dog-specific calculation) | **bookkeeping** (counts/traces) | **projection** (reshape existing data) | **stub** (deferred / empty).

### profile — ProfileNode

FILE: `app/agent/nodes/profile_node.py`  
FORMULA: `PROFILE_V1`  
EXECUTES: yes.  
INPUT: `context.profile`  
OUTPUT: dumped profile fields.  
CONSUMERS: scheduling only; later nodes read `context.profile` directly.  
AFFECTS CANONICAL ANALYSIS: only by existing as the graph root.  
DUPLICATE ELSEWHERE: HTTP adapter already built the same DTO.  
KIND: **projection**. STATUS: **IMPLEMENTED**.

### breed — BreedNode

FILE: `app/agent/nodes/breed_node.py`  
FORMULA: `BREED_RESOLVE_V1`  
EXECUTES: yes.  
INPUT: profile breed **strings**; `repository.breeds()`. Exact lower match, then `str.contains` fallback. Uses `repository.platform.normalize_breed_name` (`DataPlatform` alias map from warehouse, **not** Ω12). **VERIFIED.**  
OUTPUT: `breed_names`, `breed_rows`.  
CONSUMERS: **declared** by BiologyNode; BiologyNode **does not read** this output — it calls `run_biological_stage(repo, profile)` which uses `resolve_breed_rows` (`isin` / case-insensitive `isin`, **no** contains fallback). **VERIFIED.**  
AFFECTS CANONICAL ANALYSIS: **no** (dead for biology).  
DUPLICATE: `resolve_breed_rows` / `DataPlatform.normalize_breed_name`; load-time `_BREED_ALIASES` in `warehouse_biology.py` (Lab→Labrador Retriever, etc.); Ω12 `resolve_raw` (alias→`BREED_*` id). Four resolvers. Ω12 not imported.  
KIND: **reasoning** that is **unwired**. STATUS: **PARTIAL** / unused by downstream math.

### biology — BiologyNode

FILE: `app/agent/nodes/biology_node.py`  
FORMULA: `BIOLOGY_V2_1`  
EXECUTES: yes.  
INPUT: `DogProfileInput` + warehouse breeds/traits/environment.  
OUTPUT: `resolved_breeds`, split, activity_level, environment, trait_purposes, environmental_compatibility.  
CONSUMERS: ExportNode → assembler biology block (read); EpidemiologyNode stage input; activity **heuristic** uses `resolved_breeds` energy. Assembler does **not** read the epidemiology dict it is passed.  
AFFECTS CANONICAL ANALYSIS: **yes**.  
KIND: **reasoning**. STATUS: **IMPLEMENTED**.

### risk — RiskNode

FILE: `app/agent/nodes/risk_node.py`  
FORMULA: `RISK_V2_1`  
EXECUTES: yes.  
INPUT: `compute_risks(repo, profile)`. Context parameters `INTERACTION_MIN/MAX` are read and **discarded**.  
OUTPUT: `health_risk`, `risks`, `meta`.  
CONSUMERS: Epidemiology merge of `priority_conditions`; IngredientNode; ConfidenceNode; EvidenceNode; ExportNode → `healthInsights`. Also `resolve_groomer_boosts` inside `compute_risks` (sort flag).  
AFFECTS CANONICAL ANALYSIS: **yes** (public health).  
KIND: **reasoning**. STATUS: **IMPLEMENTED**.

### epidemiology — EpidemiologyNode

FILE: `app/agent/nodes/epidemiology_node.py`  
FORMULA: `EPIDEMIOLOGY_V2_1`  
EXECUTES: yes.  
INPUT: biology + `run_epidemiology_stage`; then **overwrites** `priority_conditions` from RISK risks when present.  
OUTPUT: epidemiology dict with risk-derived priorities.  
CONSUMERS: NutritionNode and ActivityNode (`priority_conditions`). ExportNode requires the node then **does not pass a used epidemiology payload** into public JSON.  
AFFECTS CANONICAL ANALYSIS: **yes** for matcher nutrition join; **no** for assembler fields.  
KIND: **reasoning** + merge. STATUS: **IMPLEMENTED**. Epi-stage priorities are subordinate to RISK when risks exist. **VERIFIED.**

### activity — ActivityNode

FILE: `app/agent/nodes/activity_node.py`  
FORMULA: `ACTIVITY_V2_1`  
EXECUTES: yes.  
INPUT: epidemiology `priority_conditions`[:10] ⨝ `condition_activities`.  
OUTPUT: `{management: {lifestyle_requirements: rows}, lifestyle_requirements}`.  
CONSUMERS: ExportNode **requires** the output then passes `management` into `assemble_frontend_response`. Assembler **never reads** `management` (parameter unused). AssessmentNode only sets `has_management: bool(activity output)`. Preventative system **re-queries** `condition_activities` itself.  
AFFECTS CANONICAL ANALYSIS: **no** (public `activityRecommendations` is heuristic).  
DUPLICATE: `pipeline_trace._management_lifestyle_count`; preventative nutrition activity lookup.  
KIND: **reasoning** unwired to public JSON. STATUS: **BROKEN** as a canonical activity engine (runs, unused). See G1.

### grooming — GroomingNode

FILE: `app/agent/nodes/grooming_node.py`  
FORMULA: `GROOMING_V1`  
EXECUTES: yes (scheduled because TraceNode depends on it).  
INPUT: **declares** profile + biology; **execute() ignores both**. Loads **all** `grooming_observation_defs` rows.  
OUTPUT: `{grooming_defs, count}` — catalog dump, not dog-specific.  
CONSUMERS: TraceNode (ordering only). **Not** ExportNode.  
AFFECTS CANONICAL ANALYSIS: **no**.  
KIND: **bookkeeping** / generic table load. STATUS: **PARTIAL**. See G2.

### nutrition — NutritionNode

FILE: `app/agent/nodes/nutrition_node.py`  
FORMULA: `NUTRITION_V2_1`  
EXECUTES: yes.  
INPUT: epidemiology priorities ⨝ `condition_ingredients` via `run_nutrition_stage`.  
OUTPUT: `nutrient_targets` (condition/ingredient/dose, **not** weight-scaled).  
CONSUMERS: ProductNode (`run_optimization_stage`); ExportNode passes nutrition dict into assembler but public `nutritionalTargets` come from **`map_ingredients(risks, weight)`**, not this list.  
AFFECTS CANONICAL ANALYSIS: **yes** for matcher reports; **no** for public nutrient table (different builder).  
KIND: **reasoning**. STATUS: **IMPLEMENTED** for matcher path. See G4.

### ingredient — IngredientNode

FILE: `app/agent/nodes/ingredient_node.py`  
FORMULA: `NUTRIENT_TARGET_V2_1` (same token as presentation stage `NUTRIENT_TARGET_V2_1`; NutritionNode uses `NUTRITION_V2_1`).  
EXECUTES: yes.  
INPUT: Declares dependency on `nutrition` but **execute() does not read** NutritionNode output. Reads RISK `risks` + `weight_kg` → `map_ingredients`. **VERIFIED.**  
OUTPUT: dose-scaled ingredient list.  
CONSUMERS: EvidenceNode (partial); PackageNode (count only). ExportNode **does not** consume it; assembler calls `map_ingredients` again.  
AFFECTS CANONICAL ANALYSIS: only if the second call is equivalent (**INFERRED** same function + same risks/weight).  
DUPLICATE: assembler `raw_ingredients`.  
KIND: **reasoning** duplicated at export. STATUS: **DUPLICATE**.

### product — ProductNode

FILE: `app/agent/nodes/product_node.py`  
FORMULA: `PRODUCT_MATCH_V2_1`  
EXECUTES: yes.  
INPUT: nutrition dict → `run_optimization_stage`.  
OUTPUT: `products`, `feeding_plan`, `reports` (`WellnessReportPayload` list).  
CONSUMERS: ExportNode → `build_product_recommendations(reports, …)` → public `productRecommendations`. PackageNode reads `reports` length only. **Packages do not use reports for membership.**  
AFFECTS CANONICAL ANALYSIS: **yes** for product cards / coverage; **no** for package SKU sets.  
KIND: **reasoning**. STATUS: **IMPLEMENTED**. See G5.

### package — PackageNode

FILE: `app/agent/nodes/package_node.py`  
FORMULA: `PACKAGE_OPTIMIZER_V2_1`  
EXECUTES: yes.  
INPUT: product/ingredient/risk presence.  
OUTPUT: `{package_ready: True, deferred_to: "export", …}`. **No packages.**  
CONSUMERS: AssessmentNode (scheduling). Real packages built in assembler.  
KIND: **stub**. STATUS: **PARTIAL** (name ≠ behavior). **VERIFIED.**

### assessment — AssessmentNode

FILE: `app/agent/nodes/assessment_node.py`  
FORMULA: `ASSESSMENT_PROJECT_V1`  
EXECUTES: yes.  
OUTPUT: counts (`risk_count`, `nutrient_target_count`, `report_count`, flags).  
CONSUMERS: ValidationNode. Not copied into `legacy_json` as the public assessment (HTTP uses `build_clinical_assessment` later).  
KIND: **bookkeeping**. STATUS: **IMPLEMENTED**.

### report — ReportNode

FILE: `app/agent/nodes/report_node.py`  
FORMULA: `REPORT_V1`  
EXECUTES: yes.  
OUTPUT: copy of ProductNode `reports`.  
CONSUMERS: ExportNode.  
KIND: **projection**. STATUS: **IMPLEMENTED**.

### confidence — ConfidenceNode

FILE: `app/agent/nodes/confidence_node.py`  
FORMULA: `CONFIDENCE_V1`  
EXECUTES: yes.  
OUTPUT: per-risk `confidence_percent` list.  
CONSUMERS: ValidationNode. Public confidence lives on `healthInsights` from RISK, not this node.  
KIND: **projection**. STATUS: **IMPLEMENTED** (debug/graph).

### evidence — EvidenceNode

FILE: `app/agent/nodes/evidence_node.py`  
FORMULA: `EVIDENCE_V1`  
EXECUTES: yes.  
INPUT: risk formula_execution lookups + ingredient evidence fields; looks up `clinical_evidence_base` row count but **does not attach those rows**.  
OUTPUT: `evidence_bundle`.  
CONSUMERS: ValidationNode / TraceNode. Assembler `collect_evidence` builds **public** `scientificEvidence` separately. Science attach may overwrite `AssessmentResult.evidence` after the graph.  
KIND: **bookkeeping**. STATUS: **PARTIAL**. Public evidence ≠ this bundle.

### validation — ValidationNode

FILE: `app/agent/nodes/validation_node.py`  
FORMULA: `VALIDATION_V1`  
EXECUTES: **before** ExportNode.  
OUTPUT: `ok` if `REQUIRED_NODES` (`profile, biology, risk, epidemiology, nutrition, product, report`) are present and no errors; `expected_outputs: ["legacy_json"]` **before** `legacy_json` exists. Does **not** require activity, grooming, ingredient, or package. **VERIFIED.**  
KIND: **bookkeeping**. STATUS: **IMPLEMENTED** with a sequencing quirk **VERIFIED**.

### trace — TraceNode

FILE: `app/agent/nodes/trace_node.py`  
FORMULA: `TRACE_V1`  
DEPENDS ON: validation, confidence, evidence, **grooming** (this is why GroomingNode must run).  
OUTPUT: graph_order, edges, execution/lookup traces. Copied into assembler debug.  
KIND: **bookkeeping**. STATUS: **IMPLEMENTED**.

### export — ExportNode

FILE: `app/agent/nodes/export_node.py`  
FORMULA: `EXPORT_LEGACY_V1`  
EXECUTES: last.  
OUTPUT: `legacy_json` = public analyze contract.  
KIND: **projection** + **recompute** (ingredients, packages, activity, grooming).  
STATUS: **IMPLEMENTED**. This is the true public compiler.

---

## 4. Canonical input / state analysis

**Do not create a new CanonicalDog class.**

### Can `DogProfileInput` be the canonical **runtime input**?

**YES, with documented gaps.** **VERIFIED.**

Reasons:

- Every engine entry (`generate_reproducible_report`, Streamlit, tests) already takes this model (`app/agent/state.py`).
- HTTP workbench and analyze adapters both terminate on it.
- Persistence re-projects `PersistentDog` **through** `profile_from_workbench_body` into the same DTO (`app/state/projection.py`).
- Formulas consume `age_years`, `weight_kg`, breed **strings**, environment, activity_level, `observed_conditions` — all on this model.

Missing **semantics** (not a reason to invent a parallel engine DTO):

| Gap | Evidence |
|---|---|
| No warehouse canonical IDs | Fields are display names. Ω12 IDs such as `BREED_B02F1BE9` never appear on the DTO. **VERIFIED** |
| No `as_of_date` | Age is already a float by the time the engine runs. Birthday non-determinism happens **before** the DTO. **VERIFIED** |
| No `dog_id` / `owner_id` | Persistence identity lives on `PersistentDog`. Engine is stateless per call. **VERIFIED** |
| No PROVIDED/UNKNOWN/NOT_PROVIDED | Ω11 `CanonicalDogInput` has `FieldValue` states; **not imported** by engine/HTTP. **VERIFIED** |
| `activity_level` default `"High"` on the Pydantic model | Workbench adapter **requires** an explicit activity and never relies on that default. Analyze adapter defaults `"Moderate"`. **CONFLICT** between model default and both adapters. **VERIFIED** |

### Competing representations (do not collapse in this phase)

| Model | File | Role | On hot path? |
|---|---|---|---|
| `WorkbenchRequest` | `http_models.py` | Canonical **HTTP** application contract (fail-closed) | yes |
| `AnalyzeRequest` | `http_models.py` | Legacy raw-engine HTTP | yes (`/api/v1/analyze`) |
| `DogProfileInput` | `app/agent/state.py` | Canonical **engine** input | yes |
| `PersistentDog` | `app/state/models.py` | Stored profile | yes, optional `dog_id` |
| `CanonicalDogInput` | `app/contracts/agent/input.py` | Ω11 future tools; extra=forbid; no silent defaults | **no** |
| `NormalizationResult` | `app/normalization/models.py` | Ω12 per-token mapping | **no** |
| `AgentPipelineState` | `app/agent/state.py` | Older typed pipeline bag | **no** — defined only; FormulaGraph uses `ExecutionContext.outputs`. **VERIFIED** unused |

**Canonical HTTP contract:** `WorkbenchRequest` + `profile_from_workbench_body`.  
**Canonical engine contract:** `DogProfileInput`.  
**Canonical persisted identity:** `PersistentDog` → workbench adapter → `DogProfileInput`.

Ω11 `CanonicalDogInput` must **not** replace `DogProfileInput` without an explicit mapping phase. That mapping is **not** proven. **BLOCKED** if someone proposes a silent swap.

---

## 5. Health flow

```
DogProfileInput
    ↓
RiskNode.compute_risks (RISK_V2_1)          ← public health
    ↓
health_risk.risks + meta
    ↓
ExportNode → build_health_insights → healthInsights / risks
    ↓
clinical_assessment health module / canonical.scientific_analysis.findings

SEPARATE:
run_package_search → resolve_care_model(repo, breed names, observations)
    ↓
del observations
    ↓
care_model pathways / star_nutrients → package ranking (balanced/optimal)
```

### `compute_risks`

INPUT: `DataRepository`, `DogProfileInput` (breeds, age, traits via warehouse joins, observations as used inside the function).  
OUTPUT: ranked risks, percents, confidence, formula_execution ledgers, `meta` (includes age stage).  
PURPOSE: Dog-specific preventative risk / wellness insights.  
CONSUMERS: Epidemiology merge, IngredientNode, assembler healthInsights.  
SCIENTIFIC DATA: `breed_conditions`, trait condition tables, interactions, benefits, mixed-breed matrix (node `tables`).  
DOG-SPECIFIC DATA: yes.  
OBSERVATION HANDLING: used inside RISK (groomer boost appears on insights as `groomer_priority`). Exact observation math is in `app/formulas/stages/health_risk.py` — not re-derived here.  
PACKAGE DEPENDENCY: none.  
PUBLIC API DEPENDENCY: **yes** (`healthInsights`).  
STATUS: **IMPLEMENTED**. **VERIFIED.**

### `resolve_care_model`

FILE: `app/data/scientific_care.py`  
INPUT: repo, **breed name list**, `observations` then **`del observations`**.  
OUTPUT: warehouse care model or empty `NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE`.  
PURPOSE: Breed-pathway preventative care for **package scoring**, not the public health list.  
CONSUMERS: `run_package_search` only (on this path).  
SCIENTIFIC DATA: warehouse observed breed conditions / pathways (see function body + empty-model notes).  
DOG-SPECIFIC DATA: breed names + demo flag. Age/weight/observations **not** used (`observations` discarded **VERIFIED**).  
PACKAGE DEPENDENCY: **yes**.  
PUBLIC API DEPENDENCY: `careModel` on analyze JSON via search envelope; not `healthInsights`.  
STATUS: **IMPLEMENTED**, intentionally observation-blind **VERIFIED**.

### Unify?

**Remain separate**, based on repository evidence, not preference:

- Different consumers (public insights vs package care score).
- Tests freeze packages independent of matcher, not independent of care_model.
- `resolve_care_model` explicitly refuses to invent conditions from observations.
- Sharing a lower-level join is **UNCLEAR** (both read biology warehouse, different shapes). Do not merge without Phase 3 numbers proving identical condition sets.

**CONFLICT:** Two “health” stories can disagree for the same dog (RISK list vs care pathways). That is current behavior, not a proven bug.

**CONFLICT (comment vs runtime):** `app/data/warehouse_biology.py` module docstring states Health Analysis now reads warehouse tables via `resolve_care_model`. Public `healthInsights` are built from `compute_risks`. `resolve_care_model` scores packages. Do not treat that comment as the assembler contract. **VERIFIED.**

---

## 6. Nutrition flow

Three builders exist. They are **not** the same calculation.

```
epidemiology.priority_conditions
        ↓
run_nutrition_stage → NutritionNode.nutrient_targets
        ↓
ProductNode.run_optimization_stage → matcher reports

risks + weight_kg
        ↓
map_ingredients  (IngredientNode AND assembler)
        ↓
public nutritionalTargets / ingredientRequirements

weight_kg + age_years
        ↓
build_requirement_profile          (AAFCO-style density minima)
        ↓
build_demo_requirement_profile     if WAGTOPIA_DEMO_MODE
        ↓
run_package_search nutrient validity

NON-DEMO:
run_package_search uses an empty nutrients stub
nutrient_mode = insufficient_product_nutrient_data
```

| Builder | File | Why it exists | Dog-specific? | Public analyze field |
|---|---|---|---|---|
| `run_nutrition_stage` | `app/formulas/stages/nutrition.py` | Condition→ingredient join for **matcher** | via epi priorities | not the public table |
| `map_ingredients` | `app/agent/ingredient_engine.py` | Weight-scaled doses from **risks** (JS ingredientEngine port) | yes | `nutritionalTargets` |
| `build_requirement_profile` | `app/data/scientific_requirements.py` | Life-stage density minima; **breed unused** | weight + age only | via demo `requirementProfile` |

`build_requirement_profile` callers: `build_demo_requirement_profile` only (`app/data/demo_scientific_dataset.py`). Production non-demo `run_package_search` **does not call it**. **VERIFIED.**

Do **not** collapse automatically. Matcher nutrition, public doses, and package AAFCO constraints are three contracts. Duplicate **work** is IngredientNode vs assembler both calling `map_ingredients` — same function, two invocations. ExportNode still **passes** the NutritionNode dict into `assemble_frontend_response`, which does not read it; matcher consumption happens earlier in ProductNode. **VERIFIED.**

---

## 7. Activity flow

### ActivityNode output

`lifestyle_requirements`: rows from `condition_activities` whose `condition` is in the top-10 RISK/epi priority **names**. Empty if table empty or no priorities.

### Assembler public output

`build_activity_recommendations(resolved_breeds, meta, pet_name)`:

- Daily minutes 75 / 60 / 45 from breed **energy** Extreme/High vs Low vs else.
- Senior ×0.75, puppy ×0.85 from RISK `meta` age stage.
- Generic physical/mental lists and a lifestyle tip.
- `condition_specific: []` **always**.

FILE: `app/agent/response_assembler.py`.  
**Same concept?** **NO.** Node = condition-linked warehouse activities. Assembler = breed-energy exercise heuristic. **VERIFIED.**

**Canonical activity implementation today:** the **heuristic** is what HTTP, clinical_assessment `_activity_module`, and therefore workbench roles consume. ActivityNode is **not** authoritative for the API.

`ExportNode` still lists `activity` as a dependency so the node **runs**, but `management` is an unused parameter (**VERIFIED** grep: only the signature mentions `management` in `assemble_frontend_response`).

Preventative nutrition (`build_preventative_nutrition_system`) re-reads `condition_activities` — a **third** activity-adjacent path, nested under preventative JSON, not `activityRecommendations`.

**Which should become authoritative?** **UNCLEAR.** No test asserts ActivityNode row contents. Tests consume `activityRecommendations` shape via clinical assessment. Wiring the node into the public field would **change** the customer activity module. Do not implement. **BLOCKED** until a contract names the winner.

Tests freezing heuristic behavior: no dedicated numeric-minute golden for activity was found in the files read. Clinical assessment copies whatever is on `activityRecommendations`. **INFERRED** that changing the heuristic would move workbench activity modules without a dedicated freeze.

---

## 8. Grooming flow

### GroomingNode output

Entire `grooming_observation_defs` table as a list of dicts. **Not** filtered by dog, breed, coat, or observations. Declared consumes are unused. **VERIFIED.**

### Public grooming output

Assembler builds `groomer`: seven **hardcoded** fields (eyes, ears, skin, teeth, limps, shedding, anal_gland) flagged if `observed_conditions` tokens match after whitespace→underscore. Not loaded from `grooming_observation_defs`. **VERIFIED.**

Clinical assessment `_grooming_module` reads `analyze["groomer"]` list as a checklist. Summary falls back to `"Grooming guidance"`. Interval fields stay empty unless present on a dict (they are not). **VERIFIED.**

### Is GroomingNode generic observation-definition loading?

**YES.** It is a table dump. **VERIFIED.**

### Other grooming logic

- `role_context.groomer.observed_conditions` merged into profile observations (adapter + `_split_workbench_body`).
- Persist records groomer notes as `GROOMER_OBSERVATION` events.
- `app/state/groomer.py` timestamps (not FormulaGraph).
- Hardcoded checklist in assembler (`groomer` array).
- **Third path (public health, not `groomer` list):** `resolve_groomer_boosts` in `app/formulas/stages/health_risk.py` maps observation tokens through `GROOMER_MAP` in `app/inference/config.py` (e.g. `itching`→Atopic Dermatitis, `limping`→Hip Dysplasia). Comment: heuristic, not literature rows. Flags `groomer_boosted` for **sort priority; does not change risk %**. Surfaces as `groomer_priority` on healthInsights. **VERIFIED.** Independent of GroomingNode and of the assembler checklist.
- `observations_for_legacy_analyze` (`app/state/groomer.py`): analyze/clinical-report/legacy recommendations merge process `SESSIONS` or a uniquely named PersistentDog. Workbench **does not** call this. **VERIFIED.**
- Isolated Ω17.1a / `app/state` grooming persistence is not a FormulaGraph reasoner.

### Enough evidence for canonical grooming analysis?

**NO.** There is no dog-specific grooming formula, interval table join, or coat-type → schedule function on the hot path. Inventing rules would violate the stop condition. **BLOCKED.** Existing public behavior is observation **flagging**, not analysis.

---

## 9. Product flow

```
NutritionNode.nutrition
    ↓
ProductNode.run_optimization_stage     PRODUCT_MATCH_V2_1
    ↓
reports (WellnessReportPayload)
    ↓
assembler build_product_recommendations
    ↓
productRecommendations  (public)
    ↓
wellness_coverage matching, productAnalyses, package_detail enrichment
    ✕ not package membership
```

`run_optimization_stage` (`app/formulas/stages/optimization.py`) matches catalog active ingredients to nutrition targets (knapsack / feeding-plan). That is the matcher.

Presentation `canonical.product_matching.recommendations` is this list. Developer pipeline **labels** include `PRODUCT_MATCH_V2_1` even though packages do not consume it. **VERIFIED** (`test_package_generation_provenance.py`).

---

## 10. Package flow

```
build_wellness_packages(product_recommendations, …)
    ↓
build_optimized_packages(..., product_recs=…)
    ↓
del product_recs                         VERIFIED
    ↓
load_candidate_products
apply_active_constraints (preferences)
run_package_search
    ↓
demo? build_demo_requirement_profile : empty nutrients stub
resolve_care_model(breeds, observations)  observations discarded
enumerate bundles → score by tier
    ↓
wellnessPackages / packageOptions / optimizerProvenance / careModel
```

**Are packages supposed to consume matcher outputs?**

**NO, according to actual code and tests.** Not UNCLEAR.

- `del product_recs` in `build_optimized_packages`. **VERIFIED**
- Developer contract: `independent_of_product_match is True`, `does_not_consume == "analyze.productRecommendations"`. **VERIFIED** (`tests/interface/test_package_generation_provenance.py`, `tests/interface/test_unified_workbench.py`).

Connecting them would **break those tests**. Do not connect. Treat independence as a frozen contract until an explicit product decision changes the tests.

**G17 (non-demo nutrients):** Code path is **VERIFIED**: non-demo search does **not** use `build_requirement_profile` and sets `insufficient_product_nutrient_data`. Whether commercial CSVs contain usable nutrient columns is **UNCLEAR** without a live catalog dump (Phase 3). Even if they do, **current code ignores them** unless demo mode.

`WAGTOPIA_DEMO_MODE` (`app/data/demo_catalog.py`) switches overlay catalog + demo requirement profile. **VERIFIED.**

---

## 11. Evidence / provenance flow

**Full analysis (in memory):**

- Per-risk `formula_execution` ledgers from `compute_risks`.
- Assembler `collect_evidence` → `scientificEvidence`.
- Debug `analyze_debug.v3`: risk_traces, formula_executions, package_rejects, decision_ledger, provenance_index (capped 500).
- Science attach: `evidence_objects`, `recommendation_explanations` on `AssessmentResult` (HTTP still returns `legacy_json` only from engine; presentation may surface analyze debug if requested).
- `analysis_signature`: SHA-256 of profile + healthInsights + nutritionalTargets + productRecommendations + wellnessPackages + scientificEvidence (timing stripped). Greeting hour is **not** in the signature. **VERIFIED.**

**Persisted:**

`result_digest` (`app/state/projection.py`):

- `package_product_ids` (up to **3** package rows per tier, product ids only)
- `finding_titles`
- `analysis_signature`
- `recommendation_snapshot` (tier bundle_id, product ids/names, cost, finding titles, nutrient min/max slices)

**Lost relative to full envelope:**

- Full `healthInsights` bodies, percents, ledgers
- Full `scientificEvidence` quotes/URLs
- `activityRecommendations`, `groomer`, biology, preventative system
- Matcher `productRecommendations` as objects (ids may appear in snapshot depending on snapshot helper — digest field itself is titles + package ids)
- Debug traces / formula_execution
- `careModel` / requirement profile
- Role projections
- `legacy_json` as a whole

Tools `compare_analyses` (`app/tools/adapters/compare.py`) compare **digests only**. **VERIFIED.**

Do not redesign persistence in this phase. Loss is **intentional given the digest schema**, not an accidental drop of a stored blob.

`_time_greeting()` uses `datetime.now().hour` inside `wellness_summary.greeting`. That makes **display** JSON time-of-day dependent. Signature excludes it. **VERIFIED.** Clinical/golden identity is therefore not tied to greeting; customer copy still moves with clock.

---

## 12. API flow

### Canonical application API

`POST /api/v1/presentation/workbench` → fail-closed adapter → one engine call → clinical assessment → workbench presentation → optional persist.

Response schema `workbench_presentation.v1`. Paths documented in `DEVELOPER_JSON_PATHS`. **VERIFIED.**

This is the **only** HTTP route that uses `profile_from_workbench_body`. **VERIFIED** (`app/api/main.py`).

### Legacy / parallel HTTP

| Route | Adapter | Notes |
|---|---|---|
| `POST /api/v1/analyze` | `profile_from_analyze_body` | Silent defaults 5y / 20kg / Moderate / Temperate Indoor / name Pet. **No `as_of_date`.** Merges `observations_for_legacy_analyze(pet_name)`. |
| `POST /api/v1/presentation/three-surfaces` | analyze adapter | Same silent defaults + birthday `datetime.now`. Not fail-closed. |
| `POST /api/v1/clinical-report` | analyze adapter | Also merges legacy groomer observations by pet name. |
| `POST /api/v1/ppie/assess`, `/ppie/trace`, validation-console (+ markdown, compare) | analyze adapter | Debug / integration. |
| `POST /api/recommendations` | analyze adapter | Legacy; may inject observations from name if body has none. |
| `POST /api/v1/ai/explain` | existing result | **Does not** run engine |
| `POST /api/v1/ai/tools/invoke` | gateway | Reads state/catalog; **does not** run engine |

### Presentation pipeline labels vs runtime

`CANONICAL_PIPELINE_STAGES` (`app/presentation/adapter.py`):  
`INPUT, PROFILE_NORMALIZE_V2_1, BREED_RESOLVE_V2_1, TRAIT_BLEND_V2_1, RISK_V2_1, NUTRIENT_TARGET_V2_1, ACTIVITY_V2_1, PRODUCT_MATCH_V2_1, PACKAGE_OPTIMIZER_V2_1, EVIDENCE_RANK_V2_1, VALIDATION_V2_1, OUTPUT`

This list is **not** `default_nodes()` and is **not** executed. Analyze JSON `pipeline_flow` is yet another list: `biology, health_risk, management, nutrition, products, feeding_plan` (`app/agent/variable_map.py`). **CONFLICT** of three pipeline vocabularies. **VERIFIED.**

---

## 13. Gap-by-gap analysis (G1–G18)

### G1 — ActivityNode unused by assembler

See §7.  
Node output: condition_activities rows.  
Assembler output: energy heuristic.  
Same concept: **no**.  
Existing canonical public activity: heuristic.  
Authoritative choice: **UNCLEAR** / **BLOCKED** (would change API).  
Tests: clinical assessment copies `activityRecommendations`; no ActivityNode content freeze found.

### G2 — GroomingNode not an ExportNode dependency

See §8.  
Node: full defs dump.  
Public checklist: hardcoded observation flags.  
Public health sort: `GROOMER_MAP` / `resolve_groomer_boosts` (not GroomingNode).  
Generic loading, not dog-specific reasoning: **yes**.  
Canonical grooming analysis: **MISSING** science. **BLOCKED** (do not invent).

### G3 — Two health builders

See §5.  
Recommendation from evidence: **remain separate**. Optional later shared join is **UNCLEAR**.

### G4 — Three nutrition builders

See §6.  
Duplicate invocation: `map_ingredients` twice.  
Intentionally different representations: matcher targets vs dose list vs (demo) AAFCO minima.  
Do not collapse.

### G5 — Product matching vs packages

See §9–§10.  
**Proven independent.** Tests freeze it. Do not connect.

### G6 — Ω12 off the runtime path

FILE tree: `app/normalization/` (`resolver.py`, `catalog.py`, `models.py`, version `MAPPING_CONFIG_VERSION = 1.0.0`).  
INPUT: `NormalizationInput(raw_value, entity_kind, source)`.  
OUTPUT: `NormalizationResult` (canonical_id/name, status, mapping_rule, candidates).  
MAPPINGS: `warehouse/mapping/{breed,condition,product,sex,observation}_aliases.csv`. README: not scientific fact tables. Canonical breed/condition/product ids must already exist in biology/commercial CSVs.  
TESTS: `tests/normalization/test_omega12_mapping.py` (Lab/Labrador → `BREED_B02F1BE9`, HD → hip dysplasia id, fail-closed). `tests/architecture/test_omega12_boundaries.py`:
- forbids `app/normalization/**` from importing engine/optimizer/search/scientific_care/scientific_requirements/formulas/presentation/LLM SDKs
- `ENGINE_TOUCHPOINTS` that must not import `app.normalization`: `package_search.py`, `package_optimizer.py`, `response_assembler.py`, `scientific_care.py`, `warehouse_biology.py`
- **Not** in that list: `engine.py`, `payload_adapter.py`, `biology_node.py`, `breed_node.py`. Isolation tests would **not** fail if Ω12 were called only from HTTP adapters. **VERIFIED.**
Production bypass: **yes**. No production import of `app.normalization` outside `app/normalization/` and its tests. Engine uses `DataPlatform.normalize_breed_name` / `resolve_breed_rows` on **display names**. HTTP comments: “Not Ω12-resolved.”  
Would wiring change behavior? **YES** if the engine received `BREED_*` ids: RISK/biology joins are on breed **names** after projection (`warehouse_biology.py` comment: `breed_id` preserved as a column; RISK matches `breed_name`). Passing Ω12 `canonical_name` instead of id might be closer, but equivalence of every current engine string vs mapping CSVs is **not proven**. Using ids as breed strings would **require invented mappings**.  
**BLOCKED.** Do not wire.

### G7 — Two HTTP profile adapters

| | `profile_from_analyze_body` | `profile_from_workbench_body` |
|---|---|---|
| Required breed | primary or breeds[0]; else ValueError | fail-closed MISSING_REQUIRED_INPUT |
| Age | birthday→now; else **5.0** | age_years or birthday required; no 5.0 |
| `as_of_date` | **not read** | parsed; used for birthday |
| Weight | weight_kg or weight; else **20.0** | required; both must match if both set |
| Environment | or `environment` or **Temperate Indoor** | required |
| Activity | or `activity` or **Moderate** | required |
| Name | default **Pet** | may be empty string; not replaced |
| Observations | `observed_conditions` plus **HTTP-layer** `observations_for_legacy_analyze(pet_name)` on analyze, clinical-report, and `/api/recommendations` | request `observed_conditions` plus `role_context.groomer.observed_conditions`. **No** session merge (adapter docstring). |
| Breed split | default 50 if secondary else 100 | same via `_split_pct` |
| Validation | loose `ValueError` | typed `WorkbenchInputError` |

**Intended canonical:** workbench fail-closed. **VERIFIED** (adapter module docstring, WorkbenchRequest docstring, OpenAPI).  
**Do not delete** the analyze adapter. It is still bound to `/api/v1/analyze`, three-surfaces, clinical-report, ppie assess/trace/console, and `/api/recommendations`. Debug presets remain analyze-body compatible (`app/debug/clinical_execution_debug.py`).

### G8 — Warehouse manifest / config drift

| Source | Value |
|---|---|
| `warehouse/manifest.yaml` | `version: 5.0.0-science`, `root: warehouse/science` |
| On disk | **no** `warehouse/science/` at warehouse root (Phase 1 + this analysis) |
| `resolve_clinical_root` | `PPIE_DATA_DIR` else `settings.warehouse_root` default `warehouse/` |
| `load_all_tables` | if `biology/breeds.csv` exists → `load_biology_warehouse` |
| Runtime version string | `_manifest_for(..., "5.0.0-biology")` |
| Configured manifest version | `5.0.0-science` **unused** on this fallback |

`warehouse/manifest.yaml` is **stale / not authoritative** for the current loader fallback. **VERIFIED.**  
Impact: HTTP `warehouse_version` reports biology loader version, not the YAML science version. Science-root files in the YAML are not the ones loaded. Biology views are the actual tables. Do not change warehouse paths in this phase.

### G9 — `waggy-frontend/` missing

FastAPI static routes, `tests/interface/frontend_paths.py`, Ω17.4-FE tests expect `waggy-frontend/`. Directory **not** on disk (Phase 1; reconfirmed this session `Test-Path` false). Out of scope for Core Brain wiring. User forbade frontend work here. STATUS: **MISSING** tree. Interface tests that require it would fail in Phase 3. **INFERRED** for test failure until Phase 3 runs them.

### G10 — Streamlit bypasses HTTP

FILE: `app/ui/renderer/navigation.py`  
`run_engine` → `asyncio.run(get_agent().generate_reproducible_report(profile))` in-process. **No** HTTP. **No** `profile_from_workbench_body`. `generate_reproducible_report_sync` exists on the engine class and is **not called** (only definition). Default Dolly: Golden×Lab, **age 3.0**, **28 kg**, Shanghai Summer, High, Female.

Role: **development / demo client**, not the canonical HTTP product UI. CSTC is a separate client (`app/ui/cstc/`) with its own Dolly.  
Tests: `tests/test_ui_templates.py` runs the **engine + HTML renderers** with the 4.3/30 kg unit-test Dolly, not Streamlit session_state and not `default_profile()`. Several of those tests are listed in `tests/conftest.py` skip notes. No test imports `streamlit`. **VERIFIED.**  
Do not migrate. Treat as **LEGACY / DUPLICATE** consumer of the same engine.

### G11 — Multiple Dolly fixtures

| Location | Breed order | Age / birthday | Weight | Environment | Activity | Observations | Role |
|---|---|---|---|---|---|---|---|
| `WORKBENCH_EXAMPLE_REQUEST` | Lab × Golden | birthday 2021-04-15, as_of 2026-09-09 | 30 | Temperate Outdoor | Moderate | joint_stiffness, itching | OpenAPI / Ω16 HTTP |
| Streamlit `default_profile` | Golden × Lab | **3.0** (no birthday) | **28** | Shanghai Summer | High | none | demo UI |
| Engine unit tests (`test_formula_graph`, `test_standard_report`, `test_validation_console`, `test_package_optimizer`, `test_ui_templates`, `test_engine_trace`) | Golden × Lab | **4.3** | 30 | Shanghai Summer | High | none | pytest engine |
| CSTC `mixed_lab_golden` | Lab × Golden | 5.0 + birthday 2021-04-15 | 30 | Temperate Outdoor | Moderate | joint_stiffness, itching | CSTC demo |
| `tests/interface/test_three_surface_contract.py` | Golden × Lab | birthday **2021-03-15**, **no as_of** (analyze adapter → `datetime.now`) | 30 | Shanghai Summer | High | [] | three-surface HTTP |
| `tests/golden/dolly.json` | (frozen analyze JSON, version 2.1.0) | — | — | — | — | — | parity fixture; **no pytest loader found** |
| Ω11 serialization tests | name Dolly | FieldValue model | — | — | — | — | contract types |

**Can one canonical fixture be chosen without breaking contracts?** **NO.** Ages 3.0 / 4.3 / 5.0 / birthday-derived, breed order, environment, and activity all differ. Unifying would change signatures and packages. Do not unify yet.

Closest “HTTP canonical demo” is `WORKBENCH_EXAMPLE_REQUEST`. Closest “engine unit” Dolly is 4.3 / Shanghai / High. Those are **two** contracts.

### G12 — Persistence loses evidence

See §11. Digest-only. Tools cannot reconstruct ledgers or full health. **VERIFIED.**

### G13 — Prototype auth / open CORS / ungated workbench

`CORSMiddleware allow_origins=["*"]`. `PersistentDog.owner_id` default `"prototype-local"`. Workbench POST has fail-closed **input** validation, not caller auth. Debug routes use `WAGTOPIA_DEVELOPER_ACCESS_KEY` when set. **VERIFIED.** Out of Core Brain math. Do not “fix security” in a data-flow phase.

### G14 — README vs AI

Phase 1: README still contradicts Gemini/chatbot in places. Docs conflict, not runtime. Not a pipeline breakpoint.

### G15 — `report_schema.ALGORITHM_VERSION = "PPIE"`

Engine `ALGORITHM_VERSION = "2.1.0"` (`app/agent/version.py`). Report schema uses the string `"PPIE"` (`app/data/report_schema.py`). Name clash **VERIFIED**. Standard report path is a **projection** (`build_standard_report`), not a second optimizer. Still a version-token **CONFLICT** for any client that compares those fields.

### G16 — Birthday age uses `datetime.now` when `as_of_date` absent

Callers of `age_years_from_birthday`:

| Caller | Passes `as_of`? |
|---|---|
| `profile_from_workbench_body` | yes, if body has `as_of_date` |
| `profile_from_analyze_body` | **never** |
| `project_to_dog_profile_input` / `dog_to_workbench_body` | **never** copies `as_of_date`. If stored dog has birthday and no `age_years`, recompute uses `datetime.now`. **VERIFIED.** |
| tests in `test_omega16_*` | explicit as_of |

Also clock-adjacent (not `age_years_from_birthday`): assembler `_time_greeting()` uses `datetime.now().hour`.

Effects:

- **Reproducibility:** analyze-path birthday-only profiles drift by calendar day (includes three-surfaces). Workbench is stable when `as_of_date` is sent (example and Ω16.1 tests). Persisted dogs with birthday-only also drift on recompute. **VERIFIED.**
- **Signatures:** age feeds RISK/nutrition/packages → `analysis_signature` moves when derived age moves. **INFERRED** (age is in profile block inside signature payload).
- **Golden tests:** golden README targets `POST /api/v1/analyze` via `tools/parity_suite.py`, which **does not exist** in this workspace. **MISSING** tool. Whether goldens still match 2.1.0 is **UNCLEAR** (G18).
- **API:** workbench documents the gap; analyze model Field description also admits `datetime.now`.

Assembler greeting clock is a **separate** non-determinism (not in signature).

Do not fix in this phase.

### G17 — Non-demo catalog nutrient sufficiency

**UNCLEAR** as a data question. **VERIFIED** that non-demo code **does not attempt** `build_requirement_profile` and stubs empty nutrients. Live row counts: Phase 3.

### G18 — Golden `dolly.json` vs ALGORITHM_VERSION 2.1.0

Fixture header says `"version": "2.1.0"`. **No** pytest file loads `tests/golden/*.json`. `tools/parity_suite.py` is **MISSING**. README instructions cannot be executed as written. **UNCLEAR** whether JSON still matches live analyze. Do not regenerate.

---

## 14. Dependency graph (desired vs actual)

Desired:

```
INPUT → RESOLUTION → HEALTH → NUTRITION → ACTIVITY → GROOMING
     → PRODUCTS → PACKAGES → PROVENANCE → API
```

Actual arrows (code → data → consumer):

```
INPUT
  WorkbenchRequest / AnalyzeRequest
      → payload_adapter
      → DogProfileInput                 actual consumer: FormulaGraph / stages
RESOLUTION
  Ω12 resolve()                         MISSING on hot path
  BreedNode breed_rows                  PARTIAL (unused by BiologyNode)
  run_biological_stage resolve_breed_rows  actual consumer: biology, activity heuristic
HEALTH
  compute_risks → healthInsights        actual consumer: API, ingredients, epi merge
  resolve_care_model → careModel        actual consumer: package_search only
                                        DUPLICATE / CONFLICT if treated as one health
NUTRITION
  run_nutrition_stage → ProductNode     actual consumer: matcher
  map_ingredients → nutritionalTargets  actual consumer: API
  build_requirement_profile             PARTIAL (demo packages only)
ACTIVITY
  ActivityNode.management               MISSING into assembler
  build_activity_recommendations        actual consumer: API
GROOMING
  GroomingNode.grooming_defs            MISSING into ExportNode
  hardcoded groomer checklist           actual consumer: API
PRODUCTS
  ProductNode.reports → productRecommendations
                                        actual consumer: API matcher view, coverage UI
PACKAGES
  run_package_search                    actual consumer: wellnessPackages
  ← productRecommendations              MISSING (del + tests)
PROVENANCE
  assembler scientificEvidence + debug  actual consumer: HTTP analyze
  EvidenceNode.evidence_bundle          PARTIAL (not public)
  result_digest                         PARTIAL / lossy for tools
API
  workbench_presentation.v1             actual consumer: HTTP clients
  CANONICAL_PIPELINE_STAGES labels      CONFLICT (not executed)
```

---

## 15. Duplicate / conflicting implementation map

| Topic | Implementations | Relation |
|---|---|---|
| Breed resolve | BreedNode (contains fallback); `resolve_breed_rows` (isin); `warehouse_biology._BREED_ALIASES` at load; Ω12 `resolve_raw` → ids | DUPLICATE; Ω12 isolated; load aliases target **names**, Ω12 targets **ids** |
| HTTP profile | analyze silent-default vs workbench fail-closed; most HTTP routes still analyze-adapter | CONFLICT by design |
| Analyze observations | body list vs `observations_for_legacy_analyze` session/name merge | CONFLICT vs workbench |
| Health | `compute_risks` vs `resolve_care_model` | DUPLICATE consumers; remain distinct |
| Health comment vs code | `warehouse_biology.py` module docstring says Health Analysis reads `resolve_care_model` | CONFLICT: public `healthInsights` come from `compute_risks` |
| Nutrition | three builders + double `map_ingredients`; assembler ignores NutritionNode dict | mixed duplicate / distinct |
| Activity | ActivityNode vs heuristic vs preventative re-query | CONFLICT of concepts |
| Grooming | defs dump vs hardcoded `groomer` flags vs `GROOMER_MAP` sort boosts | CONFLICT (three concepts) |
| Assembler unused args | `epidemiology`, `nutrition`, `feeding_plan`, `management` | PARTIAL / unread |
| Formula tokens | IngredientNode `NUTRIENT_TARGET_V2_1` vs NutritionNode `NUTRITION_V2_1` vs presentation stage list | CONFLICT |
| Packages | PackageNode stub vs assembler optimizer | stub vs real |
| Evidence | EvidenceNode vs `collect_evidence` vs science attach vs digest | PARTIAL stack |
| Pipeline names | FormulaGraph ids vs `pipeline_flow` vs `CANONICAL_PIPELINE_STAGES` vs engine docstring | CONFLICT |
| Algorithm version | `2.1.0` vs report_schema `"PPIE"` | CONFLICT |
| Warehouse version | YAML `5.0.0-science` vs loader `5.0.0-biology` | CONFLICT |
| Dolly | ≥6 fixtures | CONFLICT |
| Clients | workbench HTTP vs Streamlit vs missing waggy-frontend vs CSTC | DUPLICATE / MISSING |
| DataRepository | `app/data/repository.py` re-exported as `app.agent.utils.DataRepository` | same class, two import paths (not two engines) |

---

## 16. Minimal implementation sequence

Only phases the repository evidence supports. No rewrite, no new stack, no frontend, no AI unless needed to protect the boundary (not needed here).

### PHASE 3 — Baseline test audit

OBJECTIVE: Run the existing suite; record pass/fail; print live `debug.formula_graph.order` and confirm it matches §3; print `warehouse_version`; demo vs non-demo package path; compare whether goldens are referenced.  
EXISTING FILES: `tests/**`, `tests/golden/*.json`, `tests/conftest.py`.  
FILES LIKELY TO CHANGE: none required (report only), unless a later instruction allows a completion report file.  
EXISTING IMPLEMENTATION TO REUSE: pytest as already written.  
BEHAVIORAL CHANGE: none.  
TESTS REQUIRED: full suite (this **is** the phase).  
RISKS: frontend tests fail because `waggy-frontend/` is missing; DataPlatform skips already documented in Phase 1.  
BLOCKERS: none for running tests. Missing frontend is an **environment** gap, not a reason to skip Core Brain tests.

This phase is required before any wiring: G17/G18 and live warehouse/demo behavior are still UNCLEAR without execution. Graph **membership order** is already source-verified in §3.

### PHASE 4 — Warehouse integrity freeze (observational)

OBJECTIVE: Treat `load_biology_warehouse` + `5.0.0-biology` as the **actual** runtime warehouse. Document that `warehouse/manifest.yaml` is not the loader. Do **not** invent `warehouse/science` contents.  
EXISTING FILES: `app/data/loader.py`, `app/data/warehouse_biology.py`, `warehouse/manifest.yaml`, `warehouse/biology/`.  
FILES LIKELY TO CHANGE: possibly docs or a loader comment/version report — **only** if a later phase instructs a tiny consistency fix. Not CSV science.  
EXISTING IMPLEMENTATION TO REUSE: biology views already used.  
BEHAVIORAL CHANGE: none if only documented; aligning YAML without a science tree would be cosmetic.  
TESTS REQUIRED: `tests/interface/test_omega10_warehouse_health.py`, `tests/warehouse/`.  
RISKS: “fixing” the manifest to point at biology could be correct; fabricating science/ would be forbidden.  
BLOCKERS: do not fill empty health from invented science.

### PHASE 5 — Input-contract freeze (no deletion)

OBJECTIVE: Keep `DogProfileInput` as engine input and workbench as HTTP canonical. Keep analyze adapter. Do not unify Dolly. Add tests only if Phase 3 shows silent contract drift.  
EXISTING FILES: `payload_adapter.py`, `http_models.py`, `state.py`.  
FILES LIKELY TO CHANGE: tests documenting adapter differences (optional).  
EXISTING IMPLEMENTATION TO REUSE: both adapters.  
BEHAVIORAL CHANGE: none.  
TESTS REQUIRED: existing Ω16 tests already freeze workbench fail-closed and as_of_date.  
RISKS: “cleanup” of analyze defaults would change `/api/v1/analyze` and debug presets.  
BLOCKERS: none for freeze; **BLOCKED** for deleting analyze.

### PHASE 6 — Determinism (G16) — gated

OBJECTIVE: If Phase 3 shows birthday-only analyze drift affecting goldens or signatures, pass an explicit `as_of` into `profile_from_analyze_body` **only** when an API field exists. Today AnalyzeRequest has **no** `as_of_date`. Adding it is an API change.  
EXISTING FILES: `payload_adapter.py`, `http_models.py`.  
FILES LIKELY TO CHANGE: AnalyzeRequest + analyze adapter + tests.  
EXISTING IMPLEMENTATION TO REUSE: `age_years_from_birthday(..., as_of=)`.  
BEHAVIORAL CHANGE: analyze birthday-only results become stable **if and only if** clients send as_of; default remains now.  
TESTS REQUIRED: mirror Ω16.1 workbench tests on analyze.  
RISKS: clients without as_of still drift. Greeting clock remains.  
BLOCKERS: undefined AnalyzeRequest field today — **do not invent** the field until product/API instruction. Mark **BLOCKED** until then.

### Not proposed (evidence forbids or is insufficient)

| Idea | Why not a phase yet |
|---|---|
| Wire ActivityNode into `activityRecommendations` | Changes public activity; winner UNCLEAR; G1 BLOCKED |
| Wire GroomingNode into `groomer` | Node is not dog-specific; G2 BLOCKED (invented grooming) |
| Unify `compute_risks` and `resolve_care_model` | Different purpose; G3 remain separate |
| Collapse three nutrition builders | Different contracts; G4 |
| Feed matcher into packages | Tests freeze independence; G5 |
| Wire Ω12 into engine | Isolation tests + id/name mismatch; G6 BLOCKED |
| Expand `result_digest` to full JSON | Redesign persistence; forbidden here |
| Replace Streamlit with HTTP | G10 do not migrate |
| Unify Dolly | G11 would break contracts |
| Restore waggy-frontend | Frontend work forbidden; tree MISSING |
| AI / tools changes | Boundary already isolated; not required for Core Brain coherence |

---

## 17. Blockers

| ID | Blocker | Why |
|---|---|---|
| B1 | Ω12 wiring | Isolation tests + engine uses names not Ω12 ids. Equivalence of `warehouse/mapping` vs `normalize_breed_name` **not proven**. Invented mappings forbidden. |
| B2 | Canonical grooming analysis | No dog-specific grooming formula on disk. |
| B3 | Canonical activity winner | Two different concepts; public contract is the heuristic; no test names ActivityNode as source of truth. |
| B4 | Analyze-path `as_of_date` | Field exists on workbench only. Adding it is an undefined analyze API until specified. |
| B5 | Matcher→packages | Frozen `independent_of_product_match is True`. Connecting silently alters a contract. |
| B6 | Golden parity | `tools/parity_suite.py` MISSING; pytest does not load goldens. Cannot claim 2.1.0 match. |
| B7 | `waggy-frontend/` | Missing tree vs tests/docs. Not a Core Brain math blocker; is a Phase 3 interface-test blocker. |
| B8 | Non-demo package nutrients | Code stubs empty requirements; live nutrient completeness UNCLEAR. |

Stop conditions that **did** fire for future work: B1, B2, B3, B5 (contract defined **against** connecting), B6 (missing tool).

Stop conditions that **did not** fire for Phase 2 itself: we can describe the pipeline without guessing mappings.

---

## 18. Explicit non-goals

- Do not implement Phase 3 or later in this artifact’s wake.
- Do not add a second `generate_reproducible_report` or a parallel optimizer.
- Do not put health/nutrition math in `app/api/main.py` or `app/presentation/adapter.py`.
- Do not invent warehouse science, grooming schedules, or Ω12↔engine id maps.
- Do not delete `profile_from_analyze_body`, Streamlit, PackageNode, BreedNode, or ActivityNode.
- Do not connect product matching to package membership against frozen tests.
- Do not unify Dolly fixtures.
- Do not migrate Streamlit to HTTP.
- Do not expand persistence to full envelopes without a later evidence phase.
- Do not frontend work; do not AI-layer work for Core Brain coherence.
- Do not bump `ALGORITHM_VERSION`.
- Do not treat presentation `CANONICAL_PIPELINE_STAGES` as executable truth.

---

## Appendix A — Desired linear brain vs breakpoints (short)

```
Dog input                 VERIFIED (WorkbenchRequest / DogProfileInput)
   ↓
canonical resolution      PARTIAL (string aliases; Ω12 MISSING; BreedNode unused)
   ↓
canonical dog state       PARTIAL (engine DTO ≠ PersistentDog ≠ Ω11)
   ↓
health                    DUPLICATE (RISK vs care_model)
   ↓
nutrition                 DUPLICATE / PARTIAL (three builders)
   ↓
activity                  MISSING node→API (heuristic instead)
   ↓
grooming                  MISSING node→API (checklist instead)
   ↓
product matching          VERIFIED (independent)
   ↓
package optimization      VERIFIED (independent; PackageNode stub)
   ↓
evidence/provenance       PARTIAL (public collect_evidence; digest lossy)
   ↓
canonical result          VERIFIED (legacy_json) + CONFLICT (label pipelines)
   ↓
API                       VERIFIED (workbench projection)
```

---

## Appendix B — Conflicts recorded (not silently resolved)

1. Engine docstring order vs Kahn+alpha order (omits grooming, confidence, evidence; overstates PackageNode).  
2. Three pipeline vocabularies (graph nodes, `pipeline_flow`, presentation stages).  
3. `DogProfileInput.activity_level` default `"High"` vs analyze `"Moderate"` vs workbench required.  
4. Manifest `5.0.0-science` vs runtime `5.0.0-biology`.  
5. `ALGORITHM_VERSION` `2.1.0` vs report_schema `"PPIE"`.  
6. README vs implemented AI (G14, docs).  
7. Multiple Dolly identities.  
8. ActivityNode vs public activity.  
9. GroomingNode vs public `groomer` vs `GROOMER_MAP` health sort.  
10. Matcher vs packages (resolved **as independence**, not as a missing wire).  
11. Assembler signature accepts `epidemiology` / `nutrition` / `feeding_plan` / `management` and does not read them.  
12. `warehouse_biology.py` Health Analysis comment vs `compute_risks` public health.  
13. Ω12 ids vs engine name joins vs load-time name aliases.  
14. Workbench-only fail-closed adapter vs majority of HTTP routes still on analyze defaults.

---

STOP. Wait for an explicit Phase 3 instruction.
