# Phase F — Canonical Pet Evidence, Temporal Profile & Evidence-Layer Architecture

**Phase:** forensic / design only  
**Status:** COMPLETE as a design artifact  
**Implementation:** NOT STARTED  

This document does not implement production behavior.  
It does not modify FormulaGraph, BreedNode, Biology, RISK, Epidemiology, NutritionNode, ProductNode, package optimization, API contracts, warehouse data, frontend, Mongo, or LLM authority.

Claim labels used throughout:

| Label | Meaning |
|-------|---------|
| VERIFIED | Observed in source, tests, or on-disk paths in this workspace |
| INFERRED | Follows from the call graph; not proven by a live run this session |
| PROPOSED | Future conceptual architecture. Not implemented. |
| UNKNOWN | Not established by repository evidence |
| MISSING | Searched; not present or not wired |
| GAP | Current architecture cannot support a stated requirement without a later gated change |

If this file and runtime disagree later, **runtime wins**.

Human identity Policies A–D are **APPROVED** and recorded in `docs/PHASE_D5_HUMAN_POLICY_GATE.md` (documentation only). Those policies are **not** Core-migrated.

---

## 1. Scope

In scope:

- Read prior phase artifacts and the live contracts they name.
- Record human approval of Policies A–D in D.5 only.
- Distinguish identity, evidence, state, scientific knowledge, commerce, and recommendation.
- Design (not implement) temporal evidence, owner/groomer/veterinarian provenance, unknown-breed pathway, physical-trait evidence, nutritional-standard boundary, and Essential / Balanced / Optimal evidence layers.
- Identify reuse vs duplication vs gaps.

Out of scope (not done):

- Owner / groomer / veterinary questionnaires
- Temporal profile implementation
- NutritionalStandardResolver implementation
- Scientific evidence database
- MongoDB, LLM, external APIs
- Product / affiliate / partner ranking
- Package redesign
- BreedNode / FormulaGraph / API / frontend migration
- New breed aliases or mappings
- Invented scientific values or trait questionnaires

`docs/WAGGY_BASELINE_TEST_AUDIT.md` is **MISSING** from this workspace. Phase 3 is cited by `docs/WAGGY_WAREHOUSE_INTEGRITY_FREEZE.md` but the audit file is not on disk. Phase F does not reconstruct it.

---

## 2. Repository evidence

### 2.1 Prior artifacts read

| Artifact | On disk | Use |
|----------|---------|-----|
| `docs/PHASE_D_BREED_IDENTITY_SEMANTIC_REVIEW.md` | YES | 21 review cases; all were `REQUIRES_HUMAN_DECISION` at write time |
| `docs/PHASE_D5_HUMAN_POLICY_GATE.md` | YES | Policy A–D gate; Phase F recorded APPROVED |
| `docs/PHASE_C_LEGACY_VS_OMEGA12_BREED_IDENTITY.md` | YES | 81-input comparison; SAME 60 / AMBIGUOUS 16 / UNRESOLVED 5 / REGRESSION 0 |
| `docs/PHASE_E_BREED_INPUT_AND_DOG_EVIDENCE_DESIGN.md` | YES | Customer input vs identity vs traits vs nutrition dependencies |
| `docs/WAGGY_CORE_FORENSIC_MAP.md` | YES | Single choke point `PPIEWellnessAgent.generate_reproducible_report` |
| `docs/WAGGY_CANONICAL_DATA_FLOW.md` | YES | Desired linear brain is **not** how the graph executes |
| `docs/WAGGY_WAREHOUSE_INTEGRITY_FREEZE.md` | YES | Biology warehouse `5.0.0-biology`; demo catalog overlay |
| `docs/WAGGY_BASELINE_TEST_AUDIT.md` | **MISSING** | Cited by the freeze doc; not present |

### 2.2 Live contracts inspected (VERIFIED symbols)

| Area | Symbol | Path |
|------|--------|------|
| Engine snapshot | `DogProfileInput` | `app/agent/state.py` |
| Persist snapshot | `PersistentDog` | `app/state/models.py` |
| Persist → engine | `project_to_dog_profile_input`, `dog_to_workbench_body` | `app/state/projection.py` |
| Ω11 input | `CanonicalDogInput`, `FieldValue`, `InputState` | `app/contracts/agent/input.py`, `app/contracts/agent/enums.py` |
| Typed observation | `Observation`, `ObserverRole` | `app/contracts/agent/observations.py` |
| Domain split | `DomainKind` | `app/contracts/agent/enums.py` |
| Science contracts | `ScientificEvidence`, `ScientificFact` | `app/contracts/agent/evidence.py` |
| Provenance | `ProvenanceRecord` | `app/contracts/agent/provenance.py` |
| Nutrition contract | `NutrientRequirement`, `NutritionAnalysisResult` | `app/contracts/agent/nutrition.py` |
| Product contract | `ProductRecord`, `BusinessConfiguration` | `app/contracts/agent/products.py` |
| Bundle tiers | `BundleTier` | `app/contracts/agent/enums.py` |
| Events | `ProfileEvent`, `EventSource`, `EventKind` | `app/ai/models.py` |
| Event store | `record_event`, `_apply_event_to_current` | `app/state/store.py` |
| Event schema | `events` / `dogs` / `preferences` | `app/state/db.py` |
| Preferences | `PreferenceRecord.superseded` | `app/state/models.py` |
| Groomer adapter | `apply_groomer_update` | `app/state/groomer.py` |
| Identity | `resolve_breed`, `NormalizationResult` | `app/normalization/resolver.py`, `app/normalization/models.py` |
| Identity provider | `Omega12BreedIdentityProvider` | `app/normalization/identity.py` |
| Breed facts | `BreedKnowledge`, `BreedTraitFact` | `app/data/breed_knowledge.py` |
| Nutrient bands | `build_requirement_profile`, `SOURCE` | `app/data/scientific_requirements.py` |
| Package tiers | `TIER_SEMANTICS` | `app/agent/package_search.py` |
| Commercial filter | `PackageConstraints` (`scientific=False`) | `app/agent/catalog_eligibility.py` |
| Core matchers | `BreedNode.execute`, `run_biological_stage`, `compute_risks`, `run_epidemiology_stage`, `run_nutrition_stage` | listed Phase E paths |

`ResolutionResult` remains **MISSING** as a type. Ω12 emits `NormalizationResult`.

---

## 3. Current-state architecture

**VERIFIED** hot path (Phase 1/2/E, re-checked against source):

```
HTTP WorkbenchRequest / AnalyzeRequest / PersistentDog
        ↓
profile_from_workbench_body  (fail-closed; breed string required)
        ↓
DogProfileInput              (scalar snapshot)
        ↓
PPIEWellnessAgent.generate_reproducible_report
        ↓
FormulaGraph nodes (independent breed lookups)
        ↓
ExportNode / assemble_frontend_response
        ↓
run_package_search (independent of ProductNode matcher)
```

**VERIFIED properties:**

1. `DogProfileInput` is one required free-text `primary_breed` plus optional `secondary_breed` and `breed_split_pct` default `50.0` (`app/agent/state.py`).
2. Workbench rejects blank breed (`app/api/payload_adapter.py::profile_from_workbench_body`).
3. Ω12 `resolve_breed()` is isolated (`tests/architecture/test_omega12_boundaries.py`).
4. Breed-derived traits are warehouse pivot columns (`TRAIT_NAMES`); per-fact provenance is discarded (`app/data/warehouse_biology.py::_apply_breed_traits`).
5. Owner/groomer observations on the hot path are `observed_conditions: list[str]`. `Observation` is unused on HTTP.
6. `build_requirement_profile` uses weight and age only; docstring: “Breed is not used.” Source is a **secondary** AAFCO-style summary, not a warehouse standard (`app/data/scientific_requirements.py`).
7. FormulaGraph nutrition targets come from epidemiology condition joins (`run_nutrition_stage`); the `profile` argument is unused.
8. Package **essential** ranking does not use breed-care scores; balanced/optimal do (`TIER_SEMANTICS`). Non-demo packages do not apply nutrient bands (empty nutrient dict).
9. `PersistentDog` stores **current scalars**. `PROFILE_UPDATE` **overwrites** those scalars (`app/state/store.py::_apply_event_to_current`, `_write_dog`).
10. `events` is append-only with `timestamp` + `created_at` both set to `_now()` at insert (`record_event`).
11. `PreferenceRecord` can be marked `superseded`; events cannot.
12. `EventSource` is `USER` / `GROOMER` / `SYSTEM` / `SCIENTIFIC`. Scientific **writes** are forbidden (`FORBIDDEN_EVENT_TYPES`, `_validate_event`).
13. `ObserverRole` is `customer` / `groomer` / `system`. Veterinarian is **MISSING**.
14. `DomainKind` already separates `USER_INPUT`, `OBSERVATION`, `SCIENTIFIC_EVIDENCE`, `SCIENTIFIC_FACT`, `PRODUCT_FACT`, `RECOMMENDATION`, `PROJECTION`.
15. Product matching and package membership remain independent (`docs/WAGGY_CANONICAL_DATA_FLOW.md`; `del product_recs` / `independent_of_product_match`).

This is **not** an evidence-layer architecture. It is a snapshot-in → graph-out engine plus a separate SQLite current-state store.

---

## 4. Proposed future conceptual architecture

**PROPOSED.** Not implemented. Not a new mega-`DogProfile`.

```
PET IDENTITY
  dog_id / name / species (when known)
  not a dump of traits, science, or products

PET EVIDENCE  (append-only records)
  who / when / what / unit / context / status
  OWNER_REPORTED | PROFESSIONAL_GROOMER | PROFESSIONAL_VETERINARIAN

PET STATE  (projection)
  CURRENT / HISTORICAL / SUPERSEDED views of evidence
  never the only copy of the fact

IDENTITY RESOLUTION  (Ω12; isolated until a later gate)
  RESOLVED | AMBIGUOUS | UNRESOLVED | MIXED
  Policies A–D

BREED KNOWLEDGE  (facts about a breed)
  BreedKnowledge / BreedTraitFact

SCIENTIFIC KNOWLEDGE
  ScientificEvidence (papers) + ScientificFact (approved relationships)

NUTRITIONAL STANDARD
  versioned recognized baseline (species + jurisdiction + life stage + date)
  Essential constraint only

PRODUCT / COMMERCE
  catalog, nutrients-as-declared, price, availability, partner listing

RECOMMENDATION
  eligibility → fit → package optimization
  must not rewrite standards or science
```

Intended dependency (**PROPOSED**):

```
Pet evidence  →  applicability
Standard      →  Essential constraint
Science       →  additional consideration (does not overwrite standard)
Product data  →  candidates only
Optimizer     →  packages
```

Do not encode this as FormulaGraph rules in this phase.

---

## 5. Identity vs evidence distinction

| Concept | Meaning | Current object | Class |
|---------|---------|----------------|-------|
| Pet identity | Which animal this record is | `PersistentDog.dog_id`, `name` | VERIFIED (snapshot identity) |
| Breed identity | Canonical breed mapping of a **string** | Ω12 `NormalizationResult`; engine uses free-text `primary_breed` | VERIFIED split |
| Breed knowledge | Facts about a breed population | `BreedKnowledge` / warehouse breed row | VERIFIED |
| Pet evidence | Something claimed about **this** animal | `observed_conditions`, `Observation`, `ProfileEvent` | VERIFIED partial |
| Pet state | Current projected values | `PersistentDog` scalars / `DogProfileInput` | VERIFIED snapshot, not projection API |
| Scientific knowledge | External / warehouse claims | `ScientificEvidence`, `ScientificFact`, biology CSVs | VERIFIED contracts; hot path uses CSVs / discarded provenance |
| Product / commerce | Sellable items | `ProductRecord`, demo catalog, `PackageConstraints` | VERIFIED |
| Recommendation | Packages / products to show | assembler + `run_package_search` | VERIFIED |

**PROPOSED principle:** breed identity is optional evidence for personalization, not a prerequisite for having a pet, evidence, or Essential nutrition bands.

**GAP:** workbench and `REQUIRED_FOR_TOOLS` treat `primary_breed` as required PROVIDED. Unknown-breed personalization is **NOT CURRENTLY SUPPORTED** (Phase E Q8, re-verified).

**Do not collapse** these into one `DogProfile`. `AgentPipelineState` already holds stage dicts; that is a pipeline bag, not an evidence model (**VERIFIED** `app/agent/state.py`).

---

## 6. Owner / groomer / veterinarian provenance

### 6.1 What exists

| Provenance class | Existing | Class |
|------------------|----------|-------|
| Owner / customer | `ObserverRole.CUSTOMER`; `EventSource.USER`; `USER_STATEMENT`; `canonical_dog_from_engine` always tags observations as CUSTOMER | VERIFIED |
| Groomer | `ObserverRole.GROOMER`; `EventSource.GROOMER`; `GROOMER_OBSERVATION`; `app/state/groomer.py`; workbench `role_context.groomer.observed_conditions` merged into `observed_conditions` | VERIFIED |
| Veterinarian | No `ObserverRole`, `ActorRole`, `EventSource`, or event type | **MISSING** |
| System | `ObserverRole.SYSTEM`; `EventSource.SYSTEM` | VERIFIED |
| Scientific write into dog events | Forbidden (`SCIENTIFIC_EVENT_FORBIDDEN`) | VERIFIED invariant |

`Observation` already has `observer_role`, `observation_type`, `value`, `unit`, `confidence`, `timestamp`, `confirmation_status` (`app/contracts/agent/observations.py`). It is **not** a groomer survey and is unused on the workbench hot path.

Groomer events must remain observations, not diagnoses (`store.py::_validate_event`, `groomer.py` module docstring). **VERIFIED.**

### 6.2 Proposed provenance classes

**PROPOSED** labels (not new enums until a later gate proves `ObserverRole` / `EventSource` cannot be extended):

- `OWNER_REPORTED` — maps most closely to existing `CUSTOMER` / `USER`
- `PROFESSIONAL_GROOMER` — maps most closely to existing `GROOMER`
- `PROFESSIONAL_VETERINARIAN` — **MISSING** today; do not invent diagnosis fields

Do **not** create `ProfessionalObservation` if `Observation.observer_role` can carry the role. A new class would duplicate `Observation`.

Do **not** turn owner or groomer tokens into diagnoses. `FORBIDDEN_EVENT_TYPES` already includes `DIAGNOSIS`.

`observed_conditions` does **not** store role per token. After merge, owner and groomer strings are indistinguishable on `DogProfileInput`. **GAP.**

---

## 7. Temporal dog profile

### 7.1 Required property (PROPOSED)

A dog’s current state is a **projection** of time-stamped evidence. Historical records are not destroyed.

Conceptual lifecycle: `CURRENT` / `HISTORICAL` / `SUPERSEDED`.

### 7.2 What the repository actually does

| Mechanism | Behavior | Class |
|-----------|----------|-------|
| `PersistentDog.weight_kg` (and other scalars) | Single current value; SQL `UPDATE` overwrites | VERIFIED |
| `PROFILE_UPDATE` | Appends an `events` row, then `_apply_event_to_current` overwrites the scalar when source is GROOMER/SYSTEM or `confirmed` | VERIFIED |
| `events.timestamp` / `created_at` | Both set to `_now()` at insert; no `observed_at` vs `recorded_at` | VERIFIED |
| `events_for` / history dump | Append-only list ordered by timestamp | VERIFIED |
| `PreferenceRecord.superseded` | Prior preference rows kept, flagged superseded | VERIFIED |
| `Observation.timestamp` | Optional; unused on hot path | VERIFIED |
| `CURRENT` / `HISTORICAL` / `SUPERSEDED` as evidence states | Not an evidence-record enum | **MISSING** |
| Reconstruct weight as of a past date | No projection function found | **MISSING** |

**GAP:** the store is “append event + mutate current snapshot,” not “current = query(evidence, as_of).” History exists for events; the engine only sees the latest `DogProfileInput` scalars.

**PROPOSED seam (do not implement):** treat `ProfileEvent` as the evidence log and `PersistentDog` as a cached projection. Do not invent a second event table. Do not move `ProfileEvent` out of `app/ai/models.py` in this phase (placement is awkward; changing it is implementation).

Minimum future fields to investigate against **existing** columns before adding any:

| Desired concept | Existing field | Status |
|-----------------|----------------|--------|
| source_type | `ProfileEvent.source`, `ProvenanceRecord.source_type`, `Observation.observer_role` | EXISTING (split across objects) |
| observed_at | — | **MISSING** (only `timestamp` = record time) |
| recorded_at | `ProfileEvent.created_at` / `timestamp` | EXISTING_BUT_DIFFERENT_SEMANTICS |
| subject | `dog_id` | EXISTING |
| observation | `kind` / `value` / `payload` / `Observation.observation_type` | EXISTING_BUT_DIFFERENT_SEMANTICS |
| value / unit | `value` string; `Observation.unit` | EXISTING partial |
| confidence | `Observation.confidence`; preference `status` | EXISTING unused / different |
| status | `ProfileEvent.status` (`recorded` / `explicit`) | EXISTING_BUT_DIFFERENT_SEMANTICS |
| supersedes | `PreferenceRecord.superseded` only | EXISTING for preferences; **MISSING** for weight/traits |

Do not add these fields now.

---

## 8. Unknown-breed pathway

Three states must stay distinct (**PROPOSED** product language; current objects in parentheses):

| Future UX / meaning | Identity resolution | Current engine / API | Class |
|---------------------|---------------------|----------------------|-------|
| “I don’t know my dog’s breed” | Breed evidence **absent by choice** | No explicit mode. Closest unused: `InputState.UNKNOWN` | GAP / PROPOSED reuse |
| “System cannot resolve the supplied name” | `UNRESOLVED` (Policy B/C or unknown token) | Ω12 `UNRESOLVED`; workbench never sends blank; dummy string can run and miss warehouse rows | VERIFIED split |
| “Supplied name is ambiguous” | `AMBIGUOUS` (Policy A) | Ω12 `AMBIGUOUS`; BreedNode still `contains`+`iloc[0]` | VERIFIED split |

**VERIFIED:** blank Ω12 → `UNRESOLVED` / `blank_or_missing`. Workbench blank → `MISSING_REQUIRED_INPUT`. Those are **not** the same as “I don’t know.”

**PROPOSED backend concepts (no UI):**

- Input mode / presence: reuse `InputState` (`UNKNOWN` vs `NOT_PROVIDED` vs `PROVIDED` vs `INVALID`).
- Resolution: reuse `MappingStatus` (`RESOLVED` / `AMBIGUOUS` / `UNRESOLVED` / `MIXED`).
- Do not invent a third enum.

**GAP:** `engine_profile_from_canonical` refuses non-PROVIDED `primary_breed` (`REQUIRED_FOR_TOOLS`). `project_to_dog_profile_input` fails if `PersistentDog.primary_breed` is `None`.

Unknown-breed personalization using age / weight / BCS / activity / observations: **NOT CURRENTLY SUPPORTED** as an end-to-end path. Nutrient **band function** can run without breed (**VERIFIED** `build_requirement_profile`). That function is not the workbench unknown-breed product path.

Adapter `_split_pct` still inserts `50.0` when a secondary breed is present (**VERIFIED**). Conflicts with Policy D / “do not infer 50/50” for **structured** split. Recorded; not fixed.

---

## 9. Physical-trait pathway

**VERIFIED warehouse breed-derived traits** (`TRAIT_NAMES`): `size`, `body_type`, `coat_type`, `energy`, `skull_type`, `climate`, `lifespan`, `weakness_group`, `function_group`.

These are **not** a questionnaire. They are breed-row values after `_apply_breed_traits`.

| Kind | Current | Class |
|------|---------|-------|
| Breed-derived trait | `BreedTraitFact` / breed-row columns | VERIFIED |
| Individually observed trait | No typed size/coat/ear/muzzle fields on the dog | **MISSING** |
| Owner-reported trait | `observed_conditions` tokens; optional `height_cm` / `bcs` / `activity_level` / `weight_kg` | VERIFIED scalars + tokens; not a trait matrix |
| Precedence among the three | None | **UNKNOWN** / not established |

**PROPOSED:** an `ObservedTrait` is evidence about the individual (`Observation` / future event payload), never a write into `BreedKnowledge`.

Do not invent questionnaire items, trait values, or CSV mappings. Do not assume a physical trait identifies a breed.

Closest unused typed slot: `CanonicalDogInput.observations` / `Observation.observation_type`. Reuse before creating `ObservedTrait` as a class.

`height_cm` and `bcs` are copied to the assembler only; scientific use is **NOT ESTABLISHED** (Phase E; re-checked `response_assembler.py`).

---

## 10. Scientific knowledge boundary

**Mandatory distinction (PROPOSED language; objects VERIFIED where named):**

| Layer | Meaning | Existing object |
|-------|---------|-----------------|
| SCIENTIFIC STANDARD | Recognized nutritional / regulatory baseline | `build_requirement_profile` + `SOURCE` (secondary AAFCO-style; **not** a versioned standard registry) |
| PEER-REVIEWED EVIDENCE | Papers / quotes / study metadata | `ScientificEvidence`; warehouse paper columns; discarded on trait pivot |
| DOG OBSERVATION | Individual animal | `Observation` / `ProfileEvent` / `observed_conditions` |
| PRODUCT DATA | Declared composition / commerce | `ProductRecord`, demo catalog |

`ScientificFact.is_scientifically_usable` is true for `APPROVED` or `WAREHOUSE_EVIDENCE` (`app/contracts/agent/evidence.py`). Warehouse rows are often `MISSING_PROVENANCE` (**VERIFIED** `breed_traits.csv`). Do not map `migrated` → `APPROVED` (`EvidenceStatus` docstring).

**Invariant (PROPOSED; matches existing “events cannot write science”):** a paper must not replace a standard minimum. The scientific layer may add a consideration. It must not rewrite Essential constraints.

Customer breed input must not become the scientific-paper entity contract (Phase E §12). **PROPOSED** reuse of that boundary.

No scientific claims were entered in this phase.

---

## 11. Nutritional-standard boundary

### 11.1 Current

**VERIFIED** `app/data/scientific_requirements.py`:

- Hardcoded `_PROFILE` minima/maxima from a **secondary** PetMD-style AAFCO summary.
- `SOURCE.primary_standard` is `False`; `warehouse_authoritative` is `False`.
- Size from `weight_kg`; life stage from `age_years` (`puppy/growth`, `adult maintenance`, `senior`).
- Senior-specific minima are `NOT_AVAILABLE`; adult figures reused with a note.
- `maximum is None` when the source omitted a max; emitted as `maximum_specified: false`.
- No jurisdiction, market, effective date, or standard version field.
- No FEDIAF (or other) table.
- No `NutritionalStandardResolver` symbol.

**VERIFIED** UI/package already distinguishes missing max in copy: `_status_label` + `NO_MODELED_MAXIMUM` / “Meets minimum” vs “Within range” (`app/agent/package_search.py`). Named tokens `DEFINED_MAXIMUM` / `NO_DEFINED_MAXIMUM` / `UNKNOWN` as a closed enum are **MISSING**.

`NutrientRequirement` has `minimum`, `maximum`, `unit`, `basis`, `life_stage`, `source`, `provenance`. It does **not** have `standard`, `standard_version`, or `jurisdiction` (**VERIFIED** `app/contracts/agent/nutrition.py`).

### 11.2 Proposed resolver

**PROPOSED** conceptual function (name is a design label, not a class to add now):

```
species + market/jurisdiction + life stage + date
        → applicable standard identity
        → versioned requirement set
```

Do **not** hardcode `if USA: AAFCO` into Core.  
Do **not** implement fallback-to-reference-standard now. That policy must be explicit and versioned in a later gate.

A missing maximum must not mean “unlimited safe maximum.” Map later onto existing `maximum_specified` rather than inventing a parallel boolean.

---

## 12. Essential / Balanced / Optimal semantics

### 12.1 Current package tiers (VERIFIED)

`BundleTier` = `essential` / `balanced` / `optimal`.

`TIER_SEMANTICS` today:

| Tier | Purpose string | Breed-care eligibility | Breed-care ranking | Budget ceiling |
|------|----------------|------------------------|--------------------|----------------|
| essential | “Minimum viable nutritional care.” | False | False | True |
| balanced | “Baseline nutritional adequacy plus breed-specific preventive considerations.” | True | True | True |
| optimal | “Best-scoring valid care package without a customer budget ceiling.” | False | True | False |

These are **scoring / budget / breed-care** tiers, not the evidence-layer definitions below. Essential still calls `resolve_care_model` on breed strings. Non-demo nutrient bands are empty.

They must not be treated as price tiers, but optimal currently **drops the budget ceiling**. That is **EXISTING_BUT_DIFFERENT_SEMANTICS** vs “broadest evidence-supported preventative approach.”

### 12.2 Intended evidence layers (PROPOSED — not implemented)

```
ESSENTIAL
  recognized nutritional baseline + safety constraints
  species / jurisdiction / life stage / standard version / effective date
  preserve min, max-or-NO_DEFINED_MAXIMUM, basis, unit, source
  paper does not overwrite these numbers

BALANCED
  Essential
  + individual dog evidence (when present)
  + relevant scientific evidence (when applicable)
  not “breed required”

OPTIMAL
  Essential
  + Balanced
  + additional applicable evidence
  + broader preventative optimization when supported
  not automatically “more than the minimum is healthier”
```

Do not create numerical targets in this phase. Do not claim “more than minimum” is healthier.

---

## 13. Product / commerce boundary

**VERIFIED:**

- `ProductRecord` separates identity, commercial, nutrition amounts, evidence, eligibility (`app/contracts/agent/products.py`).
- `BusinessConfiguration` docstring: commercial search space **must not alter scientific truth**.
- `PackageConstraints.as_dict()["scientific"]` is `False` (`app/agent/catalog_eligibility.py`).
- Matcher and optimizer are independent; affiliate/availability do not write nutrient minima.
- Demo overlay **replaces** commercial tables; biology tables stay (`docs/WAGGY_WAREHOUSE_INTEGRITY_FREEZE.md`).

**PROPOSED** future dependency (unchanged from the instruction; not implemented):

```
Dog evidence → requirements / evidence → product eligibility → product fit → package optimization
```

Product data must not determine scientific truth.  
Affiliate availability must not determine nutritional requirements.

Do not modify ProductNode, `package_optimizer`, `run_package_search`, or the matcher in this phase.

### 13.1 Future nutrition table data (PROPOSED UI contract; no UI change)

Current customer nutrition rows already carry min/max/actual/status/source-ish fields (`app/presentation/adapter.py::_customer_nutrition_facts`). Legacy mental model “Per Pack / Required / Maximum / Status” is **INFERRED** from that projection, not rebuilt as UI.

Future columns to support **later** (do not add now):

| Future distinction | Closest existing field | Status |
|--------------------|------------------------|--------|
| Essential requirement | `required_minimum` / `required_density_min_dm` | EXISTING |
| Defined vs no maximum | `maximum_specified`, `allowed_maximum` | EXISTING |
| Scientific consideration | `breed_recommended` / `star` (breed-care, not paper layer) | EXISTING_BUT_DIFFERENT_SEMANTICS |
| Dog-specific reason | — | **MISSING** |
| Package contribution | `actual` / `actual_per_day` / `nutrient_contributions` | EXISTING |
| Evidence source | `source` / `source_type` / `source_reference` | EXISTING partial |

---

## 14. B2C / B2B compatibility

**VERIFIED:** `ActorRole` includes `customer`, `groomer`, `business`, `science`, `developer`, `ai_agent`. Presentation builds `roles.*`. There is **no** partner-catalog preferential ranker and **no** B2B contract in `app/contracts`.

**PROPOSED** (do not implement partner ranking):

```
B2C: owner → dog → owner observations → optional groomer/vet evidence → recommendations
B2B: partner org → professional workflow → staff observation → dog evidence → partner-aware ranking
```

Partner status must never alter Essential / scientific requirements. Commercial ranking stays downstream of `PackageConstraints` (`scientific=False`).

---

## 15. Future multi-species compatibility

Do not implement cat/rabbit/hamster support.

**VERIFIED dog-shaped assumptions:**

- Types named `DogProfileInput`, `PersistentDog`, `CanonicalDogInput`, `dog_id`.
- `build_requirement_profile(*, weight_kg, age_years)` — no species argument.
- Life-stage bands are canine (`puppy/growth`, senior ≥ 7).
- Warehouse `species` column / `BreedKnowledge.species` / `ScientificEvidence.species` exist as **strings** (typically `Canis lupus familiaris`).
- Ω12 `EntityKind` has no species kind.

**PROPOSED** future roots (labels only): Animal / Species / LifeStage / Observation / Evidence / NutritionalStandard / ScientificClaim / Product.

Where today’s names would block expansion: engine input type, requirement function signature, life-stage cutoffs, event `dog_id`, HTTP dog routes. Do not rename them now.

---

## 16. MongoDB future seam

**VERIFIED:** no `pymongo` / `motor` in production code. Isolation tests forbid them in Ω12 / offline modules.

Do not decide collection names.

**PROPOSED evaluation** of document-oriented *domains* (storage later; domain remains storage-independent):

| Domain | Why document-shaped (INFERRED) | Current home (VERIFIED) |
|--------|--------------------------------|-------------------------|
| Breed knowledge | Identity + trait facts + status | CSV + `BreedKnowledge` |
| Scientific papers / claims | Nested quotes, links, review state | warehouse paper columns; `ScientificEvidence` |
| Nutritional standards | Versioned nested nutrient sets | hardcoded `_PROFILE` |
| Product catalog + nutrient declarations | Nested commercial + composition | demo overlay / empty Core catalog |
| Commerce listings / affiliate / availability / regional pricing | Variable vendor documents | `ProductCommercialData` fields; not a live catalog |

SQLite `var/waggy_state.sqlite` is the **current** dog-state store (**VERIFIED**). Future Mongo must not become the scientific authority or the FormulaGraph. It is a provider implementation concern.

---

## 17. Deterministic Core principles

**PROPOSED** (aligned with existing AI module comments):

The Core Brain remains:

- human-defined rules
- scientific knowledge (reviewed)
- deterministic calculations
- structured evidence

An LLM must not: set nutritional requirements, infer breed identity, invent evidence, score claims, or replace FormulaGraph math.

**VERIFIED:** `app/ai/` exists; `app/ai/models.py` states “Model output is untrusted input.” Feedback cannot write `FORBIDDEN_EVENT_TYPES`. That is the correct *direction*: AI around the Core, not as scientific authority.

Do not add an LLM in this phase. Do not use the existing explain path as evidence of scientific competence.

Policies A–D remain deterministic Ω12 rules.

---

## 18. Existing contracts that can be reused

Do not add a parallel type when these exist:

| Need | Reuse |
|------|--------|
| Presence / “I don’t know” | `InputState` + `FieldValue` |
| Breed string mapping | `NormalizationResult` / `resolve_breed` / `MappingStatus` |
| Breed population facts | `BreedKnowledge` / `BreedTraitFact` / `BreedCatalog` |
| Individual observation | `Observation` |
| Domain separation | `DomainKind` |
| Scientific paper vs fact | `ScientificEvidence` / `ScientificFact` |
| Provenance blob | `ProvenanceRecord` |
| Nutrient constraint row | `NutrientRequirement` + `maximum_specified` |
| Product vs commerce | `ProductRecord` / `BusinessConfiguration` |
| Package tier names | `BundleTier` |
| Time-stamped dog log | `ProfileEvent` + `events` table |
| Current snapshot cache | `PersistentDog` |
| Preference history | `PreferenceRecord.superseded` |
| Commercial-only filter | `PackageConstraints` (`scientific=False`) |
| Engine DTO (until a later gate) | `DogProfileInput` |
| Groomer vs owner role | `ObserverRole` / `EventSource` |

---

## 19. Concepts that must NOT be duplicated

| Do not create | Why |
|---------------|-----|
| `BreedInput` class | Duplicates `DogProfileInput` + `CanonicalDogInput` (Phase E Q12) |
| `ResolutionResult` | Use `NormalizationResult` |
| New unknown-state enum | Use `InputState` |
| Mega `DogProfile` dump | Collapses identity/evidence/science/products |
| Second percentage model | `breed_split_pct` already exists (different semantics) |
| `ObservedTrait` class before proving `Observation` insufficient | Same slot |
| `ProfessionalObservation` | Extend `observer_role` |
| Second event log | `ProfileEvent` / `events` exist |
| `NutritionalStandardResolver` class now | Design label only |
| New max-flag boolean | Use `maximum_specified` |
| New alias CSV / Corgi-Husky-Bulldog aliases | Policy B |
| Mongo models | Future seam only |
| LLM classifier for breed or nutrients | Forbidden |

---

## 20. Open questions

| # | Question | Class |
|---|----------|-------|
| Q1 | Should workbench emit `InputState.UNKNOWN` for “I don’t know”? | UNKNOWN (API/product) |
| Q2 | Should UI emit `breed_id` or canonical display name? | UNKNOWN (Phase E) |
| Q3 | Keep adapter 50/100 default when split is unknown? | UNKNOWN (conflicts with approved “no inferred %”) |
| Q4 | Trait precedence: breed-derived vs observed vs owner-reported? | UNKNOWN — do not invent |
| Q5 | May Essential packages run on weight/age bands when breed is unknown? | UNKNOWN (code can compute bands; policy not approved) |
| Q6 | When will non-demo `run_package_search` call `build_requirement_profile`? | UNKNOWN |
| Q7 | `observed_at` vs `recorded_at` — add fields or reuse `timestamp`? | UNKNOWN |
| Q8 | Is `PersistentDog` allowed to remain a writable cache of the projection? | UNKNOWN |
| Q9 | Extend `ObserverRole` with veterinarian, or a later professional enum? | UNKNOWN |
| Q10 | Should `ProfileEvent` move out of `app/ai/models.py`? | UNKNOWN (placement only) |
| Q11 | How do `height_cm` / `bcs` / `activity_level` / environment enter evidence? | UNKNOWN |
| Q12 | More than two mixed components in Core? | UNKNOWN |
| Q13 | Fallback reference standard when a market has no adopted profile? | UNKNOWN — must be explicit later |
| Q14 | Partner ranking fields? | UNKNOWN — must not touch science |
| Q15 | Reconstruct Phase 3 baseline audit (file missing)? | MISSING artifact |

---

## 21. Explicitly deferred implementation

Not started and not authorized by this phase:

- Owner / groomer / veterinary questionnaires
- Temporal projection API (`as_of`, CURRENT/HISTORICAL/SUPERSEDED)
- Nutritional standard resolver
- Scientific evidence database / paper ingestion
- MongoDB
- Product / affiliate / partner ranking
- Package redesign to match §12.2
- BreedNode / FormulaGraph / RISK / Biology / Epidemiology / Nutrition / Product migration
- API / frontend changes
- Alias additions
- LLM scientific authority
- Multi-species runtime
- Lineage / Mendelian inference
- Trait precedence rules
- Invented nutrient numbers

---

## 22. Phase F exit criteria

This phase is complete when:

1. Policies A–D are recorded APPROVED in D.5 — **done (documentation only)**.
2. This architecture document exists and classifies claims — **done**.
3. No production / warehouse / API / Ω12 / Core consumer code changed in this phase — **required**.
4. Existing breed/normalization isolation tests still pass — **required**.
5. Implementation of the proposed architecture is **not** started.

---

## 23. Gaps that block the intended product (do not fix now)

| ID | Gap | Evidence |
|----|-----|----------|
| G1 | Breed required for workbench / tools / persist→engine | `payload_adapter`, `REQUIRED_FOR_TOOLS`, `projection.py` |
| G2 | No explicit “I don’t know” distinct from blank / unresolved / ambiguous | No input mode enum; `InputState.UNKNOWN` unused on HTTP |
| G3 | No veterinarian provenance | `ObserverRole` / `EventSource` |
| G4 | Current state overwrites; no as-of projection | `_write_dog`, `_apply_event_to_current` |
| G5 | No `observed_at` ≠ `recorded_at` | `record_event` sets both to now |
| G6 | Owner vs groomer collapsed in `observed_conditions` | merge in `payload_adapter._request_observations` |
| G7 | No individual physical-trait evidence model | Phase E; `TRAIT_NAMES` are breed-derived |
| G8 | No versioned nutritional standard / jurisdiction | `scientific_requirements.py` hardcoded secondary source |
| G9 | Package tiers ≠ evidence layers | `TIER_SEMANTICS` vs §12.2 |
| G10 | Trait provenance discarded at Core pivot | `_apply_breed_traits` |
| G11 | Structured split infers 50/100 | `_split_pct` |
| G12 | Phase 3 audit file missing | `docs/WAGGY_BASELINE_TEST_AUDIT.md` |
| G13 | Ω11 science/nutrition/observation contracts unused on hot path | `app/api` does not import them |

---

## 24. Change control

| Item | This phase |
|------|------------|
| `docs/PHASE_D5_HUMAN_POLICY_GATE.md` | Decision fields → APPROVED only |
| `docs/PHASE_F_CANONICAL_PET_EVIDENCE_ARCHITECTURE.md` | Created |
| Production code | Unchanged |
| Warehouse / mapping | Unchanged |
| Ω12 / BreedNode / FormulaGraph / API / UI | Unchanged |
| Mongo / LLM | Not added |
| Tests encoding this design as live behavior | None added |
