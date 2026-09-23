# Phase E — Breed Input and Dog Evidence Design

**Phase:** forensic design only  
**Status:** COMPLETE as a design artifact  
**Implementation:** NOT STARTED  

This document does not implement architecture.  
It does not migrate Core consumers.  
It does not change Policies A–D.  
Human approval of Policies A–D was supplied in the instruction that commissioned this design. The earlier `docs/PHASE_D5_HUMAN_POLICY_GATE.md` fill-in fields were not edited in this phase.

Approved identity semantics (unchanged):

- A — multiple approved canonical candidates, no disambiguation rule → `AMBIGUOUS`
- B — unique colloquial terms without approved mapping → `UNRESOLVED`
- C — blank / whitespace identity input → `UNRESOLVED`
- D — explicit `x` / `×` / `/` → `MIXED`, ordered components, no inferred percentages

---

## 1. Executive summary

The current customer-to-Core path is:

```
HTTP WorkbenchRequest / AnalyzeRequest / PersistentDog
        ↓
app/api/payload_adapter.py::profile_from_workbench_body
  (or profile_from_analyze_body / project_to_dog_profile_input)
        ↓
app/agent/state.py::DogProfileInput
        ↓
PPIEWellnessAgent / FormulaGraph
```

`DogProfileInput.primary_breed` and `secondary_breed` are **free-text strings**. They are not Ω12 `NormalizationResult`s. They are not `BreedKnowledge`. They are not `breed_id`.

Ω12 `resolve_breed()` remains isolated. BreedCatalog/BreedKnowledge is a typed snapshot of the biology projection and is **not** called by FormulaGraph consumers.

Physical traits exist as **warehouse breed-derived columns** on the pivoted breed row. They are not a customer questionnaire. Owner/groomer observations exist as `observed_conditions: list[str]`. Those two sources are different fields. No precedence rule between them exists.

Workbench analysis **requires a non-blank breed string**. There is no wired “I don’t know” identity mode on the hot path. Nutrient **requirement bands** (`build_requirement_profile`) use **weight and age only** (`app/data/scientific_requirements.py`). Breed-specific care, epidemiology, and nutrition **targets** require a warehouse breed match.

Family/lineage is **not** a current model.

The smallest future contract that does not change Core today is: keep using existing input objects; do not invent a second dog mega-profile; treat breed identity as optional evidence at the **customer-input** layer; do not attach lineage or physical-questionnaire fields to Core until a later gated implementation.

---

## 2. Current repository evidence

| Area | What exists | Path |
|------|-------------|------|
| Engine profile | `DogProfileInput` | `app/agent/state.py` |
| HTTP DTOs | `WorkbenchRequest`, `AnalyzeRequest` | `app/api/http_models.py` |
| HTTP adapters | `profile_from_workbench_body`, `profile_from_analyze_body` | `app/api/payload_adapter.py` |
| Persistent dog | `PersistentDog`, `DogCreateRequest` | `app/state/models.py` |
| Persist → engine | `dog_to_workbench_body`, `project_to_dog_profile_input` | `app/state/projection.py` |
| Ω11 input (unused on hot path) | `CanonicalDogInput`, `FieldValue`, `InputState` | `app/contracts/agent/input.py` |
| Ω11 observation (unused on hot path) | `Observation` | `app/contracts/agent/observations.py` |
| Legacy matcher | `BreedNode.execute` | `app/agent/nodes/breed_node.py` |
| Independent biology lookup | `run_biological_stage` → `app.agent.utils.resolve_breed_rows` → `app.data.repository.resolve_breed_rows` (`isin` / casefold `isin`) | `app/formulas/stages/biological.py`, `app/agent/utils.py`, `app/data/repository.py` |
| Independent RISK lookup | `compute_risks`, `_breed_records` | `app/formulas/stages/health_risk.py` |
| Epidemiology lookup | `compute_epidemiology_risk` / `run_epidemiology_stage` (`isin` on condition `breed`) | `app/formulas/stages/epidemiology.py` |
| Care / packages | `resolve_care_model` | `app/data/scientific_care.py` |
| Ω12 identity | `resolve_breed` | `app/normalization/resolver.py` |
| Breed facts seam | `BreedKnowledge`, `BreedCatalog` | `app/data/breed_knowledge.py` |
| Trait pivot | `_apply_breed_traits` | `app/data/warehouse_biology.py` |
| Trait names | `TRAIT_NAMES` / `TRAIT_TABLES` | `app/data/breed_knowledge.py`, `app/data/native_loader.py` |
| Nutrient bands | `build_requirement_profile` | `app/data/scientific_requirements.py` |

`ResolutionResult` is **not** a repository type. Ω12 emits `NormalizationResult` (`app/normalization/models.py`).

---

## 3. Existing input / profile models

### 3.1 `DogProfileInput` — hot-path engine input

`app/agent/state.py::DogProfileInput`

| Field | Type / default | Role |
|-------|----------------|------|
| `name` | `str` required | Display |
| `primary_breed` | `str` required | Free-text breed string |
| `secondary_breed` | `str \| None` | Optional second free-text breed |
| `breed_split_pct` | `float` default `50.0` | Copied into biology payload; not used as mixed-matrix factor |
| `age_years` | `float` required `> 0` | Age |
| `weight_kg` | `float` required `> 0` | Weight |
| `current_environment` | `str` required | Environment string |
| `activity_level` | `str` default `"High"` on the model; workbench adapter requires it | Activity string |
| `sex` / `gender` | optional | Copied through |
| `birthday` | optional | Age source |
| `height_cm` | optional | Copied to assembler; scientific use **NOT ESTABLISHED** |
| `bcs` | optional | Copied to assembler; scientific use **NOT ESTABLISHED** |
| `observed_conditions` | `list[str]` | Caller/groomer observation tokens |
| `monthly_budget` | optional | Commercial constraint |

This is the object FormulaGraph nodes receive via `ExecutionContext.profile`.

### 3.2 HTTP

`WorkbenchRequest` (`app/api/http_models.py`): `primary_breed` **or** `breeds[0]` required after `profile_from_workbench_body` (`_blank(primary)` → `MISSING_REQUIRED_INPUT`). Comment: “Not Ω12-resolved.”

`AnalyzeRequest`: looser; `profile_from_analyze_body` still requires `primary_breed or breeds[]` (`ValueError`). Silent defaults for age/weight/activity/environment on this path only.

### 3.3 Persistent dog

`PersistentDog.primary_breed` is `str | None`. `DogCreateRequest.primary_breed` is optional.  
`project_to_dog_profile_input` rebuilds a workbench body and **fails** if breed (and age/weight/activity/environment) are missing (`app/state/projection.py`).

### 3.4 `CanonicalDogInput`

`app/contracts/agent/input.py` already has `InputState.UNKNOWN` / `NOT_PROVIDED` on `primary_breed`.  
`REQUIRED_FOR_TOOLS` includes `primary_breed` **PROVIDED**.  
`canonical_dog_from_engine` / `engine_profile_from_canonical` exist (`app/contracts/agent/adapters.py`) but `app/api` does not import them. `REQUIRED_FOR_TOOLS` plus `CanonicalDogInput.validate_for_tools` mean `InputState.UNKNOWN` on `primary_breed` cannot become `DogProfileInput` through `engine_profile_from_canonical`.

Do not invent a second presence-state type. This one already exists and is unused on the live HTTP path.

---

## 4. Existing breed identity model

Three systems remain distinct.

### 4.1 Customer/engine string

Canonical **customer-selected** representation today: a **display-name string** (`primary_breed` / `secondary_breed` / `breeds[]`).

Warehouse `breed_id` exists on `breeds.csv` and on `BreedKnowledge.breed_id`.  
Core FormulaGraph consumers join on the projected `breed` **display name** after `normalize_breed_name` / exact / `contains` / `isin` — not on `breed_id`.  
`app/data/breed_knowledge.py` states this explicitly.

UI selection of a controlled list is **not implemented**. Nothing in the HTTP DTO is a `breed_id`.

### 4.2 Legacy / Core matching (unchanged)

| Consumer | Function | Match |
|----------|----------|--------|
| BreedNode | `BreedNode.execute` | normalize + exact + `str.contains` + `iloc[0]` |
| Biology | `run_biological_stage` → `app.agent.utils.resolve_breed_rows` | `isin` / casefold `isin` (`app/data/repository.py::resolve_breed_rows`) |
| RISK | `_breed_records` | exact then `str.contains` + `iloc[0]` |
| Epidemiology | `compute_epidemiology_risk` / `run_epidemiology_stage` | `isin` on normalized names |
| Care model | `care_model_from_warehouse` | normalize then `isin`; fallback `str.contains(..., regex=False)` |

BiologyNode **depends on** the breed node in the DAG (`app/agent/nodes/biology_node.py`) but `run_biological_stage` reads `context.profile`, not `breed_rows`. RiskNode similarly calls `compute_risks(repo, profile)`.

### 4.3 Ω12

`resolve_breed()` → `NormalizationResult` with `status`, `canonical_id`, `canonical_name`, `candidates`, `components`.  
Not imported by FormulaGraph / BreedNode / RISK / Biology / Epidemiology / scientific_care (`tests/architecture/test_omega12_boundaries.py`).

Approved aliases remain the five rows in `warehouse/mapping/breed_aliases.csv`.

### 4.4 BreedCatalog

`BiologyCsvBreedCatalog` wraps `breeds_df()` + alias map. Exact/casefold `get_by_canonical_name`.  
Consumed by `tests/data/test_breed_knowledge_contract.py` and `DataPlatform.breed_catalog()`. **Not** a FormulaGraph matcher.

---

## 5. Existing physical-trait model

Confirmed warehouse trait names (`TRAIT_TABLES` / `TRAIT_NAMES`):

| Trait | Warehouse `trait_name` | Runtime breed-row column |
|-------|------------------------|--------------------------|
| size | `size` | `size` |
| body type | `body_type` | `body_type` |
| coat type | `coat_type` | `coat_type` |
| energy | `energy` | `energy` |
| skull type | `skull_type` | `skull_type` |
| climate | `climate` | `climate` |
| lifespan | `lifespan` | `lifespan` |
| weakness group | `weakness_group` | `weakness_group` |
| function group | `function_group` | `function_group` |

Source: `warehouse/biology/breed_traits.csv` (per-fact rows with `fact_id`, `status` often `MISSING_PROVENANCE`).  
Projection: `app/data/warehouse_biology.py::_apply_breed_traits` copies **only** `trait_value` onto the breed row. `fact_id`, papers, quotes, and per-trait status are **discarded** on that pivot.

`BreedTraitFact` (`app/data/breed_knowledge.py`) is `trait_name` + `trait_value` only. Comment: “Does not carry discarded CSV fact_id / papers / per-trait status.”

These traits are **breed-derived warehouse facts**, not customer-answered questionnaire fields.

`variable_map.py` still lists older intern column aliases (`body_size`, `energy_level`, …). Runtime biology uses the TRAIT_TABLES names above. Treat variable_map as a **parity/documentation map**, not a second live schema.

---

## 6. Existing product / nutrition dependencies

| Stage | Breed required? | Other inputs | Evidence |
|-------|-----------------|--------------|----------|
| Nutrient band function | **No** | `weight_kg`, `age_years` | `build_requirement_profile` docstring: “Breed is not used.” Size band from weight (`dog_size_band`), stage from age (`life_stage_band`). |
| Nutrition **targets** (FormulaGraph) | Indirect **yes** | Epidemiology `priority_conditions` | `run_nutrition_stage` joins conditions → ingredients. Empty priorities → empty targets. The `profile` parameter is unused in that function. |
| Epidemiology priorities | **Yes** (name match) | Biology resolved traits for trait-condition union | `run_epidemiology_stage` / `compute_epidemiology_risk` |
| Care model / package pathways | **Yes** (name match) | `observations` argument is discarded (`del observations`) | `resolve_care_model` → `care_model_from_warehouse`; empty breed list → `_empty_model` |
| Package search requirements | Demo only for bands | Demo: `build_demo_requirement_profile(weight_kg, age_years)` → `build_requirement_profile`. Non-demo: empty `nutrients` (“product dry-matter data unavailable”). Missing weight/age fall back to `10` / `5` inside `run_package_search` only. | `app/agent/package_search.py::run_package_search` |
| Package search care | Always attempted | `primary_breed` + `secondary_breed` strings → `resolve_care_model`. Essential tier: `uses_breed_care_for_eligibility` / `uses_breed_care_for_ranking` are `False`. Balanced/optimal use care scores. | same file, `TIER_SEMANTICS` |
| Product node | Nutrition + profile | `run_optimization_stage(repo, profile, nutrition)` | `app/agent/nodes/product_node.py` |
| Activity node | Indirect | Top epidemiology conditions; does **not** read `profile.activity_level` | `ActivityNode.execute` |
| Assembler activity copy | Breed-derived `energy` / `function_group` if resolved | Age stage from meta | `build_activity_recommendations` |
| RISK | Breed match for trait/observed-condition risks | `observed_conditions` via `resolve_groomer_boosts`; `breed_split_pct` unused | `compute_risks` |

**Q7:** The **function** `build_requirement_profile` operates without breed. FormulaGraph nutrition **targets** and warehouse care pathways do not. Package **essential** ranking does not use breed-care scores, but `run_package_search` still resolves a care model from breed strings. Non-demo nutrient bands are not applied (empty nutrient dict).

**Q8:** An explicit unknown-breed customer mode is **NOT CURRENTLY SUPPORTED** on workbench (breed string required). An unmatched dummy string can start the engine and yield empty science/care. That is not an unknown-breed product path.

---

## 7. Exact breed input flow

**OBSERVED**

1. Customer (or persist) supplies a string, typically a canonical display name in tests (`"Labrador Retriever"`).
2. Adapter writes `DogProfileInput.primary_breed`.
3. Each Core consumer independently normalizes and looks up warehouse rows.
4. If the string is a current alias (`Lab`, `GSD`, …), `normalize_breed_name` maps to the canonical **display name**, then name-join proceeds.
5. Ω12 is not consulted.

**DESIGN (not implemented)**

A future controlled list can emit the same display name the warehouse already uses as the Core join key, or later emit `breed_id` **without changing Core join in this phase**. Identifier strategy remains: Core join = canonical display name; `breed_id` = warehouse key.

Do not invent a new ID format here.

---

## 8. Mixed breed flow

**OBSERVED structured mixed (customer/engine)**

`primary_breed` + optional `secondary_breed` + `breed_split_pct`.

Adapter defaults (`app/api/payload_adapter.py::_split_pct`):

- secondary present, split omitted → `50.0`
- no secondary, split omitted → `100.0`

Biology copies `breed_split_pct` into its payload (`run_biological_stage`).  
RISK mixed adjustment uses `mixed_breed_matrix` **pair × condition × factor**, not `breed_split_pct` (`apply_mixed_breed_nudge`).  
Epidemiology mixed hits also use that matrix (`run_epidemiology_stage`).  
`variable_map.py` aliases matrix `factor` to the name `breed_split_pct` — column-name parity, **not** proof that the profile percentage drives science.

**OBSERVED Ω12 mixed strings**

`Lab x Golden` etc. → `MIXED` components. Not consumed by FormulaGraph.

**DESIGN**

Reuse `primary_breed` / `secondary_breed` / `breed_split_pct` for “two named breeds, optional known split.”  
Do not invent a second percentage model.  
Do not infer a split when absent (today the adapter **does** insert 50/100 — that is an existing semantic conflict with Policy D’s “do not infer percentages” for **strings**, and with the design principle for unknown split). Marked below as a clarification, not a change in this phase.

More than two breed components, or MIXED string components as Core evidence: **NOT CURRENTLY REPRESENTED**.

---

## 9. Family / lineage flow

Searched: `mother`, `father`, `parent_breed`, `lineage`, `family_breed`.

No profile/API/warehouse field represents parent identities.

`variable_map.py` schema token `inherited_traits` is an alias for mixed-matrix `condition`, not a parentage model.  
`app/agent/wellness_map.py::friendly_trait_label` “working lineage” is display wording around `function_group`.  
`PreferenceRecord` (`app/state/models.py`) is a generic `category`/`value` store, not a mother/father model.

**Status:** `NOT_CURRENTLY_REPRESENTED`  
**Do not** infer dog identity, trait percentages, or Mendelian inheritance from parents.  
A future lineage object would be **evidence**, not `primary_breed`.

---

## 10. Unknown breed flow

| Layer | Blank / omitted breed |
|-------|------------------------|
| Ω12 | `UNRESOLVED` / `blank_or_missing` (Policy C; already implemented) |
| Workbench adapter | `MISSING_REQUIRED_INPUT` |
| `DogProfileInput` | `primary_breed: str` required; empty string is a valid Python string and triggers legacy contains-all / first-row on BreedNode and RISK |
| `CanonicalDogInput` | `UNKNOWN` / `NOT_PROVIDED` exist; `REQUIRED_FOR_TOOLS` + `engine_profile_from_canonical` refuse non-PROVIDED `primary_breed` |
| `PersistentDog` | `None` allowed; cannot project to engine |

There is no customer token meaning “I don’t know” that skips lookup without sending `""`.

Physical-trait questionnaire as a substitute path: **NOT CURRENTLY REPRESENTED**.

---

## 11. Breed-derived vs observed evidence

| Kind | Where it lives | Status |
|------|----------------|--------|
| BREED_DERIVED | Pivoted columns on `repo.breeds()` / `BreedTraitFact` | EXISTING (warehouse → Core lookup) |
| OBSERVED (condition tokens) | `DogProfileInput.observed_conditions` | EXISTING |
| OBSERVED (typed) | `Observation` | EXISTING, unused on hot path |
| OBSERVED (physical questionnaire) | — | NOT_CURRENTLY_REPRESENTED |
| Precedence BREED_DERIVED vs OBSERVED | — | NOT ESTABLISHED BY CURRENT EVIDENCE |

`resolve_care_model` deletes the observations argument (`del observations`). Observations do not invent warehouse conditions there.

RISK uses `observed_conditions` as groomer boosts (`resolve_groomer_boosts`), separate from breed-row traits.

No code equates owner-reported coat/energy with warehouse `coat_type`/`energy`.

---

## 12. Scientific-context boundary

Customer breed input is a **user string / future controlled selection**.

Scientific warehouse rows use `breed_name` / `breed_id` on facts (`breed_traits.csv`, `observed_breed_conditions.csv`). Paper text terms such as “Retriever” are **not** a customer-input mode.

Do not reuse the customer BreedInput contract as the paper-entity contract. Future scientific extraction remains: source → candidates → human review → approved knowledge → Core. Not designed further here. No LLM.

---

## 13. Product-personalization boundary

Do not redesign packages.

Factual split:

- **Weight/age nutrient band function:** no breed (`build_requirement_profile`). Reached from packages only via demo `build_demo_requirement_profile`.
- **Condition-linked targets, care pathways, epidemiology, RISK trait tables:** need a resolved warehouse breed (or breed-derived traits from a matched row).
- **Unknown breed + physical questionnaire → personalization:** **NOT CURRENTLY SUPPORTED**.

Classification for the desired unknown-breed + traits + context path: **NOT CURRENTLY SUPPORTED** (API requires breed; no questionnaire; no trait-as-input join).

---

## 14. Proposed conceptual contract (minimal, not implemented)

Reuse existing objects. Do not add a `DogProfile` dump.

Conceptual layers (names are design labels, not new classes):

```
CUSTOMER INPUT
  mode (design candidate; see §15)
  identity references (existing strings / future controlled canonical_name)
  optional secondary + optional split (existing fields)
  unknown/not_provided (existing InputState; unused on hot path)
  observations (existing list[str] / unused Observation)
  age, weight, activity, environment (existing)

IDENTITY (Ω12; isolated)
  NormalizationResult

BREED KNOWLEDGE (fact provider; isolated)
  BreedKnowledge / BreedTraitFact

CORE (unchanged)
  DogProfileInput as today
```

A future `BreedInput` object is **not** introduced as a class in this phase. It would duplicate `DogProfileInput` + `CanonicalDogInput` unless a later implementation proves those two cannot carry mode/unknown/lineage.

Lineage and physical-questionnaire observations stay **out** of Core until a gated implementation.

The contract must not contain product recommendations, scientific claims, nutrition calculations, packages, LLM output, or inferred breed percentages.

---

## 15. Existing vs proposed fields

| Concept | Existing field/object | Status | Evidence | Change now? |
|---------|----------------------|--------|----------|-------------|
| Customer breed string | `DogProfileInput.primary_breed` | EXISTING | `app/agent/state.py` | NO |
| Second breed | `DogProfileInput.secondary_breed` | EXISTING | same | NO |
| HTTP breed list | `WorkbenchRequest.breeds` | EXISTING | `app/api/http_models.py` | NO |
| Split percentage input | `breed_split_pct` | EXISTING_BUT_DIFFERENT_SEMANTICS | default 50/100 in adapter; science uses `mixed_breed_matrix.factor` | NO |
| Mixed **string** | Ω12 `MIXED` | EXISTING | `resolve_breed`; Policy D | NO |
| Warehouse breed id | `breed_id` / `BreedKnowledge.breed_id` | EXISTING | `breeds.csv`; not Core join | NO |
| Core join name | projected `breed` column | EXISTING | `warehouse_biology._project_breeds` | NO |
| Ω12 identity result | `NormalizationResult` | EXISTING | `app/normalization/models.py` | NO |
| Input presence UNKNOWN | `CanonicalDogInput.primary_breed` + `InputState` | EXISTING | unused on workbench | NO |
| Exact-known UI mode | — | NOT_CURRENTLY_REPRESENTED | no controlled list | NO |
| Mixed-breed UI mode | partially `primary`+`secondary` | EXISTING_BUT_DIFFERENT_SEMANTICS | two strings, not MIXED components | NO |
| Family/lineage | — | NOT_CURRENTLY_REPRESENTED | no parent fields | NO |
| Unknown-breed mode | — | NOT_CURRENTLY_REPRESENTED | workbench requires string | NO |
| Breed-derived traits | `TRAIT_NAMES` on breed row / `BreedTraitFact` | EXISTING | `breed_knowledge.py`, `warehouse_biology.py` | NO |
| Trait provenance on Core row | discarded at pivot | EXISTING | `_apply_breed_traits`; `BreedTraitFact` docstring | NO |
| Observed condition tokens | `observed_conditions` | EXISTING | `DogProfileInput` | NO |
| Typed observation | `Observation` / `CanonicalDogInput.observations` | EXISTING | constructed only in `canonical_dog_from_engine`; unused on HTTP/FormulaGraph | NO |
| Physical-trait questionnaire | — | NOT_CURRENTLY_REPRESENTED | no owner size/coat/energy fields; do not reuse `BreedTraitFact` | NO |
| Generic persist preference | `PreferenceRecord` | EXISTING_BUT_DIFFERENT_SEMANTICS | `category`/`value` store (e.g. budget in `dog_to_workbench_body`); not parentage | NO |
| Trait precedence | — | NOT ESTABLISHED BY CURRENT EVIDENCE | — | NO |
| BreedCatalog | `BiologyCsvBreedCatalog` | EXISTING | unused by FormulaGraph | NO |
| `ResolutionResult` | — | NOT_CURRENTLY_REPRESENTED | do not invent; use `NormalizationResult` | NO |
| Mega `DogProfile` | `AgentPipelineState` holds stage dicts | EXISTING | not a unified evidence object | NO |

Design-candidate **mode** names (`EXACT_KNOWN_BREED`, `MIXED_BREED`, `FAMILY_OR_LINEAGE_KNOWN`, `UNKNOWN_BREED`) have **no** existing enum. Status: **PROPOSED** as documentation labels only — not schema fields, not implemented.

---

## 16. Answers to required questions

**Q1.** Current canonical customer-selected breed = **free-text display name** (`primary_breed` / `breeds[0]`). Not `breed_id`. Not Ω12 id.

**Q2.** Exact: yes as a matching string. Mixed: two strings + optional split (partial). Unknown: no explicit mode. Lineage: no.

**Q3.** Warehouse-pivoted `size`, `body_type`, `coat_type`, `energy`, `skull_type`, `climate`, `lifespan`, `weakness_group`, `function_group`.

**Q4.** `breed_traits.csv` → `_apply_breed_traits` → `repo.breeds()` → Biology / RISK / care trait helpers.

**Q5.** `observed_conditions` on the profile; groomer merge in API/state. Not physical traits.

**Q6.** Different fields; no paired evidence layer; no precedence.

**Q7.** Requirement **band function** yes (weight/age, `build_requirement_profile`). Condition nutrition **targets** and care pathways no (need breed match). Package essential ranking does not use breed-care scores; non-demo packages do not apply those bands.

**Q8.** Explicit unknown-breed path: **NOT CURRENTLY SUPPORTED**. Dummy unmatched string: engine runs, science mostly empty.

**Q9.** Attach at **customer input**, beside (not inside) `BreedKnowledge`. Closest unused typed slot: `CanonicalDogInput.observations` / `Observation.observation_type` (`app/contracts/agent/observations.py`). That is **not** a physical-trait questionnaire today. Do not write questionnaire answers onto warehouse breed rows. Exact field names: **NOT ESTABLISHED** beyond “do not reuse `BreedTraitFact` as owner input.”

**Q10.** Attach as **separate evidence**, not `primary_breed`. No existing hook.

**Q11.** `DogProfileInput`, `CanonicalDogInput`, `PersistentDog`, `WorkbenchRequest`, `NormalizationResult`, `BreedKnowledge`, `Observation`.

**Q12.** A new `BreedInput` class would duplicate those. Do not add it in this phase.

**Q13.** Clarify before any later implementation: required vs UNKNOWN breed; adapter 50/100 split vs “do not infer percentages”; `observed_conditions` vs `Observation`; name-join vs `breed_id`; three independent matchers; `CanonicalDogInput` unused.

**Q14.** Smallest future contract without changing Core today: document modes; reuse existing fields; keep Ω12 isolated; keep Policies A–D; do not add lineage/questionnaire to FormulaGraph.

---

## 17. Unknowns / unresolved design questions

- Whether a later UI emits `breed_id` or only canonical display name. **NOT ESTABLISHED.**
- Whether workbench will adopt `InputState.UNKNOWN` instead of requiring a string. **NOT ESTABLISHED** (product/API decision).
- Whether adapter-default `50.0` split remains when a human later implements “unknown split.” **NOT ESTABLISHED.**
- Whether more than two mixed components ever enter Core. **NOT ESTABLISHED.**
- Trait precedence (breed-derived vs observed vs questionnaire). **NOT ESTABLISHED.**
- Whether packages should run on weight/age bands alone as a product policy when breed is unknown. `TIER_SEMANTICS["essential"]` already ignores breed-care for eligibility/ranking; that is not an approved unknown-breed product policy. **NOT ESTABLISHED.**
- Whether non-demo package search will ever call `build_requirement_profile` once product dry-matter data exists. **NOT ESTABLISHED.**
- How `height_cm` / `bcs` / `activity_level` / `current_environment` interact with unknown-breed personalization. RISK notes that activity/weight/climate modifiers are not applied in the RISK_V2_1 ledger (`compute_risks` “note”). Assembler activity uses breed energy. **Partial / NOT ESTABLISHED** as a unified evidence model.

---

## 18. Explicit non-decisions

This phase did not:

- implement modes, lineage, or a questionnaire
- add aliases or change Policies A–D
- migrate BreedNode or call `resolve_breed()` from Core
- change FormulaGraph, RISK, Biology, Epidemiology, scientific_care
- change API or frontend
- add Mongo, LLM, or fuzzy matching
- invent precedence or inheritance
- invent scientific paper-term meanings
- create `ResolutionResult` or a new alias CSV
- update `PHASE_D5_HUMAN_POLICY_GATE.md` fill-in fields

---

## 19. Phase E implementation prerequisites

A later **implementation** phase (not this document) would need, at minimum:

1. Human confirmation that this design’s reuse of existing fields is acceptable (no new `BreedInput` class yet).
2. An explicit product decision on unknown-breed **API** behavior (keep required string vs adopt `InputState.UNKNOWN`). That is a new API/product decision, not an identity Policy A–D question.
3. No Core matcher migration until a separate gated consumer-migration phase.
4. No questionnaire/lineage fields until their own gated schema phase.

If any of those is treated as in-scope without a new gate: **STOP**.

---

## 20. Recommended next gated phase

**One narrow phase:** record Policies A–D as approved in the D.5 decision fields (documentation only), then a **separate** gated phase to specify — still without Core migration — whether `CanonicalDogInput.InputState.UNKNOWN` may become the workbench representation of “I don’t know,” including fail-closed projection rules for `PersistentDog` with `primary_breed=None`.

Do not start BreedNode migration, questionnaire implementation, or lineage schema in that phase.

---

## 21. Change log

| Item | Status |
|------|--------|
| Design artifact | this file |
| Production code | unchanged |
| Warehouse / mapping | unchanged |
| Ω12 / BreedNode / FormulaGraph / API / UI | unchanged |
| Tests encoding this design as implemented | none added |
