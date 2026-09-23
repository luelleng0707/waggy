# Phase G — Canonical Evidence State + Temporal Pet Profile Contract

**Phase:** forensic / design-first / synthetic-first  
**Status:** COMPLETE as a design artifact  
**Implementation:** NOT STARTED  
**Implementation gate:** **BLOCKED** (see §25)

This document does not implement production behavior.  
It does not modify FormulaGraph, BreedNode, Biology, RISK, Epidemiology, Nutrition, ProductNode, package optimization, API schemas, HTTP adapters, warehouse CSVs, frontend, Mongo, or LLM authority.

Claim labels:

| Label | Meaning |
|-------|---------|
| VERIFIED | Observed in source, tests, or on-disk paths |
| PARTIALLY VERIFIED | Object exists; required semantics are incomplete or unused on the hot path |
| UNKNOWN | Not established by repository evidence |
| CONFLICTING | Two live contracts disagree |
| NOT IMPLEMENTED | Searched; absent or unwired |
| PROPOSED | Future conceptual contract. Not live behavior. |
| UNRESOLVED POLICY | Human/product decision still required. Do not guess. |

If this file and runtime disagree later, **runtime wins**.

Approved identity Policies A–D remain as recorded in `docs/PHASE_D5_HUMAN_POLICY_GATE.md`. This phase does not reopen them and does not migrate Core.

---

## 1. Phase status

| Item | Status |
|------|--------|
| Design artifact | this file |
| Production code | unchanged |
| Warehouse / mapping | unchanged |
| API / UI | unchanged |
| Mongo / LLM | not added |
| Tests encoding this design as implemented | none added |
| Phase H | not started |

---

## 2. Files inspected

Present and used:

- `docs/PHASE_D5_HUMAN_POLICY_GATE.md`
- `docs/PHASE_E_BREED_INPUT_AND_DOG_EVIDENCE_DESIGN.md`
- `docs/PHASE_F_CANONICAL_PET_EVIDENCE_ARCHITECTURE.md`
- `docs/WAGGY_CANONICAL_DATA_FLOW.md`
- `docs/WAGGY_WAREHOUSE_INTEGRITY_FREEZE.md`
- `app/contracts/agent/input.py`
- `app/contracts/agent/enums.py`
- `app/contracts/agent/observations.py`
- `app/contracts/agent/evidence.py`
- `app/contracts/agent/provenance.py`
- `app/contracts/agent/nutrition.py`
- `app/contracts/agent/products.py`
- `app/state/models.py`
- `app/state/projection.py`
- `app/state/store.py`
- `app/state/db.py`
- `app/state/groomer.py`
- `app/normalization/models.py`
- `app/normalization/enums.py`
- `app/normalization/resolver.py`
- `app/normalization/identity.py`
- `app/data/breed_knowledge.py`
- `app/data/breed_catalog.py`
- `app/data/repository.py`
- `warehouse/biology/breeds.csv`
- `warehouse/biology/breed_traits.csv`
- `warehouse/mapping/breed_aliases.csv`
- `app/agent/nodes/breed_node.py`
- `app/agent/nodes/biology_node.py`
- `app/agent/nodes/risk_node.py`
- `app/agent/nodes/activity_node.py`
- `app/agent/nodes/product_node.py`
- `app/agent/package_search.py`
- `app/agent/response_assembler.py`
- `app/api/http_models.py`
- `app/api/payload_adapter.py`
- `app/presentation/adapter.py`
- `app/ai/models.py` (`ProfileEvent`)
- `app/agent/state.py` (`DogProfileInput`)
- `repository/models/runtime.py` (`DogProfile`, `ResolvedDog`)
- `tests/normalization/test_omega12_breed_identity.py`
- `tests/normalization/test_omega12_mapping.py`
- `tests/architecture/test_omega12_boundaries.py`
- `tests/architecture/test_dog_profile_contract.py`
- `tests/data/test_breed_node_baseline.py`
- `tests/data/test_breed_knowledge_contract.py`
- `tests/state/test_omega17_1_contracts.py`
- `tests/state/test_omega17_2_contracts.py`
- `tests/offline/` (present; isolation only)

Missing evidence:

- `docs/WAGGY_BASELINE_TEST_AUDIT.md` — **NOT IMPLEMENTED** / missing on disk (cited by the warehouse freeze doc)

---

## 3. Verified current architecture

Answers A–W. Do not infer missing behavior.

| # | Question | Finding | Label |
|---|----------|---------|-------|
| A | What represents a pet? | Several objects: `PersistentDog.dog_id` (SQLite persist), `DogProfileInput` (engine DTO, no `dog_id`), `CanonicalDogInput.dog_id` (optional, unused on HTTP), `repository.models.runtime.DogProfile` (immutable; `dog_id` convention `DOG::{name}` is a documented gap). | CONFLICTING (duplicate identities) |
| B | What represents current pet state? | `PersistentDog` scalars (`weight_kg`, `primary_breed`, …) overwritten by SQL `UPDATE` (`store._write_dog`). Engine sees `DogProfileInput` after `project_to_dog_profile_input`. | VERIFIED overwrite snapshot |
| C | What represents historical events? | SQLite `events` table + `ProfileEvent` (`app/ai/models.py`). `events_for` returns append-only rows ordered by `timestamp`, `event_id`. `test_patch_dog_updates_and_preserves_history` asserts a `PROFILE_UPDATE` row remains after weight change. | VERIFIED |
| D | What represents an observation? | Hot path: `observed_conditions: list[str]`. Typed: `Observation` (unused on HTTP). Events: `GROOMER_OBSERVATION` / `USER_STATEMENT`. | PARTIALLY VERIFIED |
| E | What represents scientific evidence? | Warehouse CSVs + `ScientificEvidence` / `ScientificFact` contracts. Trait pivot discards `fact_id` / papers / status. Events cannot write science (`SCIENTIFIC_EVENT_FORBIDDEN`). | PARTIALLY VERIFIED |
| F | What represents provenance? | `ProvenanceRecord` (Ω11 contract). Event `source` / `timestamp` / `session_id`. Warehouse columns discarded on breed-trait pivot. | PARTIALLY VERIFIED |
| G | What represents a breed? | Customer: free-text `primary_breed` / `secondary_breed`. Warehouse: `breed_id` + `breed_name`. Ω12: `NormalizationResult`. Core join: display name, not `breed_id`. | CONFLICTING (three systems) |
| H | What represents breed-derived traits? | `TRAIT_NAMES` on pivoted breed row / `BreedTraitFact`. | VERIFIED |
| I | What represents owner input? | Workbench body; `EventSource.USER`; `ObserverRole.CUSTOMER`; `USER_STATEMENT`. | VERIFIED |
| J | What represents groomer input? | `GROOMER_OBSERVATION`; `app/state/groomer.py`; workbench `role_context.groomer.observed_conditions` merged into the same token list. | VERIFIED |
| K | What represents veterinarian input? | No `ObserverRole`, `EventSource`, or event type. | NOT IMPLEMENTED |
| L | Is observer role modeled? | Yes: `ObserverRole` = `customer` / `groomer` / `system`. Not on `observed_conditions` tokens. | PARTIALLY VERIFIED |
| M | Do timestamps distinguish observed / recorded / became current? | `ProfileEvent.timestamp` and `created_at` are both set to `_now()` at insert (`record_event`). `Observation.timestamp` is a single optional field. No `observed_at`. No “became current” timestamp. | NOT IMPLEMENTED (cannot distinguish) |
| N | Append-only, overwrite, or projected? | Events append. Current scalars overwrite. `current_projection()` dumps latest event **per kind/type** plus the dog snapshot; it does not replay field values as-of a date. | VERIFIED hybrid (append + overwrite); not a field projection |
| O | Can historical state be reconstructed as-of a date? | No `as_of` argument on `current_projection` or `project_to_dog_profile_input`. Events can be listed; weight-as-of is not computed. | NOT IMPLEMENTED |
| P | Authority model? | Partial write rules only: `USER` `USER_STATEMENT` does not overwrite weight (`test_user_statement_is_not_groomer_and_does_not_overwrite_weight`). `PROFILE_UPDATE` applies if source is `GROOMER`/`SYSTEM` **or** `confirmed`. Not a vet>groomer>owner ranking. | PARTIALLY VERIFIED |
| Q | Physical traits as individual-dog observations? | No owner size/coat/ear/muzzle questionnaire fields. Optional `height_cm` / `bcs` scalars. `TRAIT_NAMES` are breed-derived. | NOT IMPLEMENTED |
| R | Are `observed_conditions` owner observations or generic tokens? | Generic `list[str]`. Adapter may merge owner + groomer lists (`_request_observations`). Role is lost after merge. | VERIFIED generic tokens |
| S | Breed-derived vs observed traits distinguishable? | Different objects (`BreedTraitFact` vs `observed_conditions`). No paired evidence layer. No precedence. | PARTIALLY VERIFIED |
| T | Can HTTP represent “I don’t know”? | Workbench requires non-blank `primary_breed` or `breeds[0]`. `InputState.UNKNOWN` exists on `CanonicalDogInput` and is unused by `app/api`. | NOT IMPLEMENTED on HTTP |
| U | Can `PersistentDog` represent missing/unknown breed? | `primary_breed: str \| None` allowed. `project_to_dog_profile_input` then fails (`MISSING_REQUIRED_PROFILE_INPUT`). `None` is not `InputState.UNKNOWN`. | PARTIALLY VERIFIED (store yes; engine no) |
| V | Mixed-breed uncertainty model? | Ω12 `MIXED` + ordered components (isolated). Engine: two strings + `breed_split_pct`. No “unknown split” flag. | PARTIALLY VERIFIED / CONFLICTING |
| W | Are breed percentages scientifically supported or adapter defaults? | `_split_pct` inserts `50.0` if secondary present and split omitted; `100.0` otherwise. RISK/epidemiology use `mixed_breed_matrix.factor`, not the profile percentage. `variable_map` aliases matrix `factor` → name `breed_split_pct` (parity map). | VERIFIED adapter default; not a scientific 50/50 |

Hot path (VERIFIED, re-stated from Phase E/F):

```
WorkbenchRequest / PersistentDog
        ↓
profile_from_workbench_body   (breed string required)
        ↓
DogProfileInput
        ↓
PPIEWellnessAgent / FormulaGraph
```

Ω12 remains isolated (`tests/architecture/test_omega12_boundaries.py`).

---

## 4. Existing reusable contracts

Reuse these. Do not invent a parallel type.

| Need | Reuse | Notes |
|------|--------|-------|
| Pet persist identity | `PersistentDog.dog_id` | No species field |
| Engine snapshot DTO | `DogProfileInput` | Required `primary_breed: str` |
| Presence / “I don’t know” | `InputState` + `FieldValue` | Unused on HTTP |
| Individual observation | `Observation` | Unused on HTTP |
| Observer role | `ObserverRole` | No veterinarian |
| Domain split | `DomainKind` | Already separates observation / science / product / recommendation / projection |
| Breed string mapping | `NormalizationResult` / `MappingStatus` / `resolve_breed` | Isolated |
| Breed population facts | `BreedKnowledge` / `BreedTraitFact` | Not an observation |
| Scientific paper / fact | `ScientificEvidence` / `ScientificFact` | Unused on hot path |
| Provenance blob | `ProvenanceRecord` | Scientific-oriented fields |
| Time-stamped pet log | `ProfileEvent` + `events` | Do not create a second log |
| Preference history | `PreferenceRecord.superseded` | Preferences only |
| Nutrient row | `NutrientRequirement` + `maximum_specified` | No jurisdiction/version |
| Product vs commerce | `ProductRecord` / `BusinessConfiguration` | Commercial must not alter science |
| Package names | `BundleTier` | Scoring tiers today, not evidence layers |
| Commercial filter | `PackageConstraints` (`scientific=False`) | |
| Event write guard | `FORBIDDEN_EVENT_TYPES` | Includes `DIAGNOSIS`, `SCIENTIFIC_FACT` |

`repository.models.runtime.DogProfile` / `ResolvedDog` are a **fourth** dog shape. Do not promote them as the canonical persist model. Treat as legacy/runtime-pipeline types unless a later gate proves otherwise.

`ProfileEvent` lives in `app/ai/models.py`. Placement is awkward. Moving it is implementation; not this phase.

---

## 5. Existing gaps

| ID | Gap | Label |
|----|-----|-------|
| G1 | No single canonical pet type | CONFLICTING |
| G2 | “I don’t know” ≠ HTTP / engine | NOT IMPLEMENTED |
| G3 | `InputState.UNKNOWN` unused; tools require PROVIDED breed | VERIFIED |
| G4 | Veterinarian role / event type | NOT IMPLEMENTED |
| G5 | `observed_at` ≠ `recorded_at` ≠ became-current | NOT IMPLEMENTED |
| G6 | No as-of field projection | NOT IMPLEMENTED |
| G7 | Current scalars overwrite; events kept but unused for replay | VERIFIED |
| G8 | Owner/groomer collapsed in `observed_conditions` | VERIFIED |
| G9 | No individual physical-trait observations | NOT IMPLEMENTED |
| G10 | No lineage / family evidence | NOT IMPLEMENTED (Phase E) |
| G11 | Adapter infers 50/100 split | VERIFIED; conflicts with Policy D spirit for structured split |
| G12 | Trait provenance discarded at pivot | VERIFIED |
| G13 | Ω11 science/observation unused on hot path | VERIFIED |
| G14 | No conflict-representation object | NOT IMPLEMENTED |
| G15 | No versioned nutritional standard / jurisdiction | NOT IMPLEMENTED |
| G16 | Package tiers ≠ Essential/Balanced/Optimal evidence layers | CONFLICTING semantics |
| G17 | Phase 3 audit file missing | NOT IMPLEMENTED |

---

## 6. Proposed conceptual architecture

**PROPOSED.** Not implemented. Not a mega-`DogProfile`.

```
IDENTITY          PersistentDog.dog_id (+ future species)
     │
     ▼
EVIDENCE LOG      ProfileEvent (append-only) + Observation payloads
     │            OWNER / GROOMER / (future) VETERINARIAN / SYSTEM
     ▼
CURRENT STATE     projection of evidence as_of now  →  cache may be PersistentDog
HISTORICAL STATE  same function as_of T
     │
     ├── breed identity evidence (optional)  →  Ω12 MappingStatus
     └── individual observations
              │
              ▼
STANDARDS         Essential nutritional constraint (not papers)
SCIENCE           ScientificEvidence / ScientificFact
     │
     ▼
RECOMMENDATION    derived analysis
     │
     ▼
COMMERCE          ProductRecord / partner ranking  (cannot write science)
```

Breed is **optional evidence**, not a prerequisite for having identity, observations, or (eventually) Essential bands.

Do not encode this as FormulaGraph rules now.

---

## 7. Pet identity model

**VERIFIED current:** identity for persist is `PersistentDog.dog_id` + `name` + optional `owner_id`.

**PROPOSED reuse:**

- Canonical persist identity = `dog_id` (opaque string; not Mongo ObjectId).
- Display name = `name`.
- Species is **not** on `PersistentDog`. Warehouse/BreedKnowledge/ScientificEvidence already have a `species` **string**. Do not add a species field in this phase.
- Breed is **not** identity of the pet. It is optional evidence attached to the pet.

**Cases (product; Core unchanged):**

| Case | Identity of the pet | Breed evidence | Policy |
|------|---------------------|----------------|--------|
| A known exact breed | `dog_id` | PROVIDED string / future controlled `canonical_name` | may resolve Ω12 RESOLVED |
| B family/category only (“some kind of shepherd”) | `dog_id` | must not auto-select | Policy A if shared token → AMBIGUOUS |
| C “I don’t know” | `dog_id` | `InputState.UNKNOWN` | ≠ blank Ω12 UNRESOLVED; ≠ HTTP missing |
| D mixed | `dog_id` | MIXED / primary+secondary | Policy D; no inferred % |
| E ambiguous | `dog_id` | AMBIGUOUS | Policy A; no first-row |
| F unresolved | `dog_id` | UNRESOLVED | Policy B/C; no invented canonical |

**UNRESOLVED POLICY:** whether persist stores `InputState` on breed, or only `primary_breed=None` meaning “not provided.” `None` today is not UNKNOWN.

Do not create `Pet` / `Animal` classes in this phase.

---

## 8. Observation model

**Reuse `Observation`.** Do not add `ObservedTrait` or `ProfessionalObservation` until a later gate proves `Observation` cannot carry `observer_role` + `observation_type` + `value` + `unit`.

**PROPOSED mapping (labels → existing):**

| Design label | Existing | Gap |
|--------------|----------|-----|
| OWNER_REPORTED | `ObserverRole.CUSTOMER` + `EventSource.USER` + `USER_STATEMENT` | tokens lose role |
| GROOMER_OBSERVED | `ObserverRole.GROOMER` + `GROOMER_OBSERVATION` | same |
| VETERINARIAN_* | — | NOT IMPLEMENTED; do not invent diagnosis fields |
| SYSTEM_DERIVED | `ObserverRole.SYSTEM` / `DomainKind.PROJECTION` / `DERIVED_ANALYSIS` | no derived-trait object |
| BREED_DERIVED | `BreedTraitFact` / breed-row columns | not an Observation |
| SCIENTIFIC_EVIDENCE | `ScientificEvidence` / `DomainKind.SCIENTIFIC_*` | not an Observation |

**PROPOSED lineage (not probabilistic unless a later gate adds it):**

```
BreedTraitFact          population knowledge
Observation             one observer, one type, one value, one time
ProfileEvent            durable log row pointing at that observation
PersistentDog scalars   cache of latest applied PROFILE_UPDATE only
```

`Observation.confidence` exists as optional **string**. Do not invent numeric probabilities. Using it is **UNRESOLVED POLICY**.

Groomer category examples in the prompt (coat, skin, nails, …) are **not** a questionnaire schema. If later implemented, they are `observation_type` values, not warehouse `TRAIT_NAMES`.

Veterinary clinical findings / diagnoses are **future placeholders**. `FORBIDDEN_EVENT_TYPES` already forbids `DIAGNOSIS` on the event write path. Do not invent vet fields now.

---

## 9. Evidence model

**PROPOSED taxonomy — reuse `DomainKind`, do not add a sixth parallel enum unless a later gate requires it.**

| Layer | DomainKind (existing) | Typical object |
|-------|----------------------|----------------|
| Owner input | `USER_INPUT` | `CanonicalDogInput` / workbench body |
| Observation | `OBSERVATION` | `Observation` / groomer-user events |
| Breed knowledge | (warehouse; not DomainKind-tagged on `BreedKnowledge`) | `BreedKnowledge` |
| Scientific evidence | `SCIENTIFIC_EVIDENCE` | `ScientificEvidence` |
| Scientific fact | `SCIENTIFIC_FACT` | `ScientificFact` |
| Derived state | `PROJECTION` / `DERIVED_ANALYSIS` | **no typed current-state projection object** |
| Recommendation | `RECOMMENDATION` | packages / products shown |
| Commerce | `PRODUCT_FACT` / `COMMERCIAL_CONFIGURATION` | `ProductRecord` |

`BreedKnowledge` has no `domain` field. That is a **gap**, not permission to merge it into `Observation`.

Do not store a paper as an observation. Do not store a product as a scientific fact.

---

## 10. Temporal model

**Required product property (PROPOSED):**

T1 weight = 10 kg remains as evidence.  
T2 weight = 15 kg is new evidence.  
Current projection = 15 kg.  
Projection as_of T1 = 10 kg.  
Old row is not deleted.

**What `ProfileEvent` can support today (VERIFIED):**

| Desired | Existing | Verdict |
|---------|----------|---------|
| pet_id | `dog_id` | YES |
| event identity | `event_id` | YES |
| recorded time | `timestamp` and `created_at` (same `_now()`) | YES as record time; **cannot** split observed vs recorded |
| observed_at | — | GAP |
| source | `source` | YES (`USER`/`GROOMER`/`SYSTEM`/`SCIENTIFIC`) |
| observer role | not a field; infer from `source` / event_type | PARTIAL |
| domain | not a field | GAP |
| value | `value` + `payload` | YES (string + JSON) |
| status | `status` (`recorded` / `explicit`) | PARTIAL / different meaning |
| supersession | preferences only | GAP for weight/traits |
| provenance | `session_id`, `correlation_id`, `notes` | PARTIAL; not `ProvenanceRecord` |

**Do not silently reinterpret `timestamp` as `observed_at`.**

**Do not create a second event log.**

**PROPOSED later field decision (not implemented):** add `observed_at` only after a gated schema change; keep `timestamp`/`created_at` as recorded time. Until then, as-of **observation time** is **NOT IMPLEMENTED**.

`current_projection` latest-wins **by event kind/type**, not by field (`store.py::current_projection`). That is not the T1/T2 weight example. Do not pretend it is.

---

## 11. Current-state projection model

**PROPOSED semantics (not coded):**

```
project(dog_id, as_of) → field values
  for each field (weight_kg, …):
    consider evidence rows with recorded_at ≤ as_of
      (and observed_at ≤ as_of IF that field exists)
    do not delete older rows
    do not invent values
    if none: NOT_PROVIDED / UNKNOWN per InputState
```

**VERIFIED today:**

- Cache = `PersistentDog` row.
- Apply rules = `_apply_event_to_current` (groomer token append; confirmed/groomer/system profile field overwrite).
- Engine projection = `project_to_dog_profile_input` → workbench adapter (fail-closed).
- Incomplete persist (name only) cannot reach the engine (`test_projection_fail_closed_no_silent_defaults`).

**UNRESOLVED POLICY:**

- Which evidence rows are eligible to become current (confirmed only? any groomer? latest any source?).
- Whether `PersistentDog` remains a writable cache or becomes read-only projection output.
- How UNKNOWN breed projects into `DogProfileInput` without sending `""` (which BreedNode `contains` would treat as all rows).

Do not implement replay now.

---

## 12. Owner vs groomer vs veterinarian evidence

**How different observers contribute without wiping the profile (PROPOSED):**

1. Each contribution is an **append** `ProfileEvent` (existing).
2. Typed body is an `Observation` (existing) in payload or a future adapter; not a replacement of the whole `PersistentDog`.
3. Current scalars change only through an explicit projection rule (today: overwrite selected fields). That rule is **not** “replace the entire profile.”
4. Multiple weights from owner and groomer **both stay in `events`**. Choosing one as current is **UNRESOLVED POLICY**. Do not encode VET > GROOMER > OWNER.

**VERIFIED partial behavior:** unconfirmed `USER_STATEMENT` with `weight_kg=99` does **not** change `PersistentDog.weight_kg`. Confirmed user patch does, and keeps a history event.

Veterinarian: **NOT IMPLEMENTED**. Future extension of `ObserverRole` / `EventSource` is a gated enum change, not a new observation class.

B2B: same observation objects; partner ranking is commerce-only (`PackageConstraints.scientific=False`). **PROPOSED**; no partner ranker exists.

---

## 13. Breed-derived vs individual-derived evidence

```
Breed Knowledge          BreedKnowledge / BreedTraitFact / warehouse row
        ↓
Population-level evidence   (not this dog)

Individual Observation   Observation / observed_conditions / events
        ↓
Individual-level evidence

Scientific Paper         ScientificEvidence
        ↓
Scientific evidence

Current Pet State        projection (PROPOSED; today overwrite snapshot)
        ↓
Recommendation           assembler / packages
        ↓
Product matching         ProductNode / catalog
        ↓
Partner prioritization   NOT IMPLEMENTED; must not write science
```

Forbidden directions (PROPOSED invariants; some already enforced):

| Forbidden | Current guard |
|-----------|---------------|
| Product → Science | `BusinessConfiguration` docstring; `PackageConstraints.scientific=False` |
| Partner priority → health conclusion | no partner ranker |
| Affiliate price → scientific suitability | no affiliate layer on Core science |
| Breed label → guaranteed individual trait | no code copies warehouse coat onto owner coat (there is no owner coat field) |
| Paper → automatic individual diagnosis | `FORBIDDEN_EVENT_TYPES` includes `DIAGNOSIS`; `Observation` has no diagnosis field |

---

## 14. Scientific evidence boundary

**Reuse `ScientificEvidence` + `ScientificFact` + `ProvenanceRecord` + `EvidenceStatus`.**

Eventual item kinds in the prompt (Paper, Guideline, Standard, Systematic review, Clinical study) are **PROPOSED labels** for `study_type` / `source_type` strings. Do not create those classes or rows now.

`ScientificEvidence` already has: `paper_id`, `paper_name`, `paper_link`, `publication_year`, `study_type`, `species`, `scientific_quote`, `status`, `warehouse_version`, `source_table`, `relationship_ref`.

**MISSING** on that contract (do not add now): version, jurisdiction, population, life stage, conditions, variables, applicability constraints as first-class fields. `ProvenanceRecord` also lacks jurisdiction/effective date.

Do not invent citations, AAFCO/FEDIAF tables, or therapeutic claims. Do not treat conversation examples as warehouse facts.

A paper does not become a pet observation. A breed trait does not become an observed individual trait.

---

## 15. Nutritional standard boundary

**VERIFIED:** `build_requirement_profile` is a hardcoded secondary AAFCO-style summary; breed unused; `maximum_specified` when max is None; no jurisdiction/version resolver.

**PROPOSED (design only, Phase F restated):**

- ESSENTIAL = applicable recognized standard (species, jurisdiction, life stage, standard version, effective date).
- BALANCED = Essential + individual evidence + applicable science.
- OPTIMAL = Balanced + additional supported prevention — **not** “more than minimum is better.”
- Paper must not overwrite Essential minima.

Do not implement nutrition architecture in this phase. Do not invent values.

`BundleTier` names may later align with those layers; **today they do not**.

---

## 16. Recommendation boundary

**VERIFIED:** public recommendations come from assembler + `run_package_search` after FormulaGraph. Product matcher is independent of packages.

**PROPOSED:** recommendation is `DomainKind.RECOMMENDATION` / `DERIVED_ANALYSIS`. It consumes current pet-state projection + applicable science + Essential constraints. It is not evidence about the dog and not a scientific fact.

Do not change ProductNode or the optimizer.

---

## 17. Commerce boundary

**VERIFIED:** `ProductRecord` splits identity / commercial / declared nutrition / eligibility. Demo catalog overlay replaces commercial tables; biology stays.

**PROPOSED:** partner/affiliate ranking is downstream of eligibility. Commerce never writes `ScientificFact`, nutrient minima, or Ω12 mappings.

Do not add product data or affiliate links in this phase.

---

## 18. Multi-species boundary

Current product is dogs. Do not implement other species.

| Naturally species-neutral (PROPOSED reuse) | Dog-shaped today (VERIFIED) |
|--------------------------------------------|-----------------------------|
| `Observation`, `ObserverRole`, `EvidenceStatus` | `DogProfileInput`, `PersistentDog`, `dog_id` |
| `ScientificEvidence.species` (string) | `build_requirement_profile` canine life-stage bands |
| `ProductRecord`, `ProfileEvent` | `BreedCatalog` / canine `TRAIT_NAMES` |
| `DomainKind` | HTTP dog routes |

Support `species = DOG` without requiring it forever. Do not rename types now.

---

## 19. Mongo storage boundary

**VERIFIED:** no pymongo/motor. SQLite `var/waggy_state.sqlite` is the persist store (`app/state/db.py`).

**PROPOSED:**

```
Domain contract (PersistentDog, ProfileEvent, Observation, ScientificFact, …)
        ↓
Repository interface (already conceptually store.py / BreedCatalog)
        ↓
SQLite adapter (today) / Mongo adapter (later)
```

Not: Domain = BSON / ObjectId.

Do not name collections. Do not add Mongo.

Document-oriented *later* candidates remain those listed in Phase F §16 (breed knowledge, papers, standards, catalog, commerce). Dog **events** can stay relational or become documents; **UNKNOWN**.

---

## 20. Synthetic-first implementation plan

**PROPOSED fixture contract for a later phase. Do not create fixtures now.**

Minimum later fixtures (synthetic, labeled as such):

| Fixture | Must include | Must not include |
|---------|--------------|------------------|
| Synthetic pet identity | `dog_id`, name; breed PROVIDED or UNKNOWN | invented warehouse breed |
| Synthetic owner observation | `ObserverRole.CUSTOMER`, type, value, recorded time | diagnosis, prevalence |
| Synthetic groomer observation | `GROOMER`, externally observable type | clinical diagnosis |
| Synthetic vet observation | only after role exists | therapeutic claims presented as warehouse science |
| Synthetic scientific evidence | `ScientificEvidence` with `status=NEEDS_VALIDATION` or explicit synthetic flag | fake journal authority |
| Synthetic product | `ProductRecord` / existing demo overlay | “scientifically proven” copy |

Reuse `app/data/demo_catalog.py` / `demo_scientific_dataset.py` as the **existing** synthetic product seam. Do not treat demo densities as Essential standards.

---

## 21. API boundary

**Do not change WorkbenchRequest in this phase.**

Future HTTP must eventually distinguish (**PROPOSED**):

Owner: known breed / unknown breed / mixed / physical observations / measurements / environment / activity / conditions.  
Ambiguous and unresolved are **resolver outputs**, not owner buttons (except “I’m not sure which of these”).  
Professional: role, observations, measurements, datetime, provenance.  
Scientific: metadata/provenance/version — not a customer route.

Until then: workbench cannot say “I don’t know.” Persist can store `primary_breed=None` but cannot project to the engine.

---

## 22. AI authority boundary

**VERIFIED:** `app/ai/` exists; model output is untrusted; scientific event writes are forbidden.

**PROPOSED path:**

```
AI output → candidate/suggestion → human review / deterministic rules → accepted knowledge
```

LLM must not directly mutate: standards, pet observations, breed mappings, nutrient requirements, product suitability facts.

No LLM work in this phase.

---

## 23. Open policy questions

| ID | Question | Status |
|----|----------|--------|
| P1 | Workbench adopts `InputState.UNKNOWN` for “I don’t know”? | UNRESOLVED POLICY |
| P2 | Persist `None` breed vs explicit UNKNOWN state? | UNRESOLVED POLICY |
| P3 | Add `observed_at` to `ProfileEvent` / `Observation`? | UNRESOLVED POLICY (schema) |
| P4 | Who may update current weight without confirmation? | PARTIALLY specified in code; not a product policy |
| P5 | Conflict display vs auto-pick when owner and groomer disagree? | UNRESOLVED POLICY — do not rank roles |
| P6 | Keep adapter 50/100 when split omitted? | UNRESOLVED POLICY (conflicts with no-inferred-%) |
| P7 | Extend `ObserverRole` with veterinarian? | UNRESOLVED POLICY |
| P8 | `PersistentDog` cache vs read-only projection? | UNRESOLVED POLICY |
| P9 | Trait precedence breed-derived vs observed | UNRESOLVED POLICY |
| P10 | Essential packages without breed? | UNRESOLVED POLICY |
| P11 | UI emits `breed_id` or display name? | UNRESOLVED POLICY |
| P12 | Move `ProfileEvent` out of `app/ai/models.py`? | UNKNOWN (placement) |

---

## 24. Explicit non-goals

This phase did **not**:

- modify FormulaGraph, BreedNode, Biology, RISK, Epidemiology, NutritionNode, ProductNode, package optimization
- modify API schemas or HTTP adapters
- add Mongo, LLM, aliases, mapping CSV rows
- add questionnaire / groomer / veterinarian UI
- add scientific papers, AAFCO/FEDIAF data, products, affiliate links
- create fake scientific data or fixtures
- create a mega `DogProfile`
- create a second event log or second resolver
- infer missing policy
- convert UNKNOWN → UNRESOLVED or AMBIGUOUS → a selected breed
- implement nutrition architecture
- begin Phase H

---

## 25. Implementation gates for Phase H

Implementation of this contract is **BLOCKED** until a later gated phase decides **all** of:

1. **Canonical pet identity** — which object is source of truth (`PersistentDog.dog_id` vs engine vs `repository.DogProfile`). Recommended reuse: persist `dog_id`; do not add a new identity type. Still needs an explicit gate.
2. **Observation vs derived knowledge** — reuse `Observation` vs `BreedTraitFact` vs `ScientificFact` vs `DomainKind.PROJECTION`. Boundary is designed here; wiring is not authorized.
3. **Temporal semantics** — `timestamp` must not be silently treated as `observed_at`. Adding `observed_at` is a schema gate. As-of projection is not implementable without that decision if observation time ≠ record time.
4. **Source/provenance** — reuse `ObserverRole` / `EventSource` / `ProvenanceRecord`. Veterinarian extension is a separate enum gate.
5. **Current-state projection semantics** — overwrite-cache vs replay. Conflict policy must not be guessed.
6. **Unknown vs unresolved vs ambiguous** — conceptually: `InputState.UNKNOWN` ≠ `MappingStatus.UNRESOLVED` ≠ `MappingStatus.AMBIGUOUS`. HTTP/engine still cannot express UNKNOWN. Adopting it is an **API gate**, not a silent persist change.

Phase H, if commissioned, must be **one** of those gates — recommended: **API/design-only** specification of UNKNOWN vs UNRESOLVED vs AMBIGUOUS on workbench/persist/projection, still without Core matcher migration, questionnaires, Mongo, or as-of replay.

Do not start Phase H from this document alone.

---

## 26. Change control

| Item | This phase |
|------|------------|
| This file | created |
| Production / data / API | unchanged |
| D.5 / Phase F | not rewritten |
