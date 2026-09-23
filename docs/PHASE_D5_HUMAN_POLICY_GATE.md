# Phase D.5 — Breed Identity Human Policy Gate

**Phase:** D.5 — policy decision record  
**Status:** COMPLETE as a gate document; **Policies A–D HUMAN-APPROVED** (recorded in Phase F; no Core migration)  
**Phase E:** design artifact completed (`docs/PHASE_E_BREED_INPUT_AND_DOG_EVIDENCE_DESIGN.md`). Approval fields below were empty during that design phase.  
**Phase F:** documentation-only recording of the explicit human approvals. Does **not** migrate BreedNode, FormulaGraph, or any Core consumer.

This document does **not** implement identity semantics.  
Cursor is **not** the human/domain/product owner.  
Existing Ω12 behavior is **not** by itself the approval.  
Legacy BreedNode behavior is **not** the approval.  
Silence is **not** approval.  
The fill-in fields below are now filled from the human instruction that commissioned Phase F.

---

## 1. Purpose

Convert the completed Phase D evidence review into an explicit human-approved policy decision record that later gates Phase E.

Phase D recorded **what the two systems currently do**.  
Phase D.5 records **which proposed identity policies a human must accept, reject, or revise** before any implementation phase may treat those policies as binding.

---

## 2. Scope

In scope:

- Document four candidate identity-resolution policies (A–D).
- Map the 21 Phase D review cases onto those four policies.
- Separate OBSERVED behavior from PROPOSED POLICY.
- Leave every human decision field **PENDING** (original D.5 deliverable). Phase F later recorded APPROVED in those fields only.

Out of scope (not done in this phase):

- Approving or rejecting any policy.
- Creating or editing aliases.
- Changing Ω12 resolver rules.
- Migrating BreedNode, RISK, Biology, Epidemiology, scientific_care, or FormulaGraph.
- API / B2C / Workbench changes.
- Mongo, LLM, fuzzy matching, embeddings, popularity or prevalence selection.
- A third identity engine.
- Phase E.

---

## 3. Authoritative evidence

Used:

| Source | Role |
|---|---|
| `docs/PHASE_D_BREED_IDENTITY_SEMANTIC_REVIEW.md` | 21 review cases; all `REQUIRES_HUMAN_DECISION` |
| `docs/PHASE_C_LEGACY_VS_OMEGA12_BREED_IDENTITY.md` | 81-input comparison; 21 disagreements |
| `app/normalization/resolver.py` | `resolve_breed()`, blank / shared-token / mixed rules |
| `app/normalization/identity.py` | Ω12 breed identity provider / aliases surface |
| `warehouse/mapping/breed_aliases.csv` | Five approved display aliases |
| `warehouse/biology/breeds.csv` | Canonical warehouse identities |
| `app/agent/nodes/breed_node.py` | Legacy matcher (`normalize` + exact + `str.contains` + `iloc[0]`) |
| `tests/data/test_breed_node_baseline.py` | Current-behavior **capture** of BreedNode (not a meaning contract) |
| `tests/normalization/test_omega12_mapping.py` | Current Ω12 rule tests |
| `tests/normalization/test_omega12_breed_identity.py` | Phase A+B facade tests |

Not used:

- Web search, Wikipedia, breed registries, Amazon, veterinary sites.
- LLM world knowledge as identity evidence.
- Product-catalog popularity.
- Warehouse row order as semantic meaning.

If a claim is not in those sources, this document marks it **NOT ESTABLISHED BY CURRENT EVIDENCE**.

---

## 4. Current architecture boundary

Three concepts remain distinct. This phase does not merge them.

```
A. Legacy FormulaGraph / Core breed matching
   BreedNode.execute → DataRepository.breeds()
   exact case-insensitive match, then pandas str.contains, first row (iloc[0])

B. Ω12 breed identity resolution
   resolve_breed() → resolve_raw(..., EntityKind.BREED)
   not wired into FormulaGraph or production Core consumers

C. Typed BreedCatalog / BreedKnowledge fact-provider seam
   Core trait join by canonical display name
   not an identity matcher
```

Frozen for this phase:

- No third identity engine.
- No second resolver.
- No new alias CSV.
- No silent Ω12 → legacy fallback.
- No Core consumer migration.
- No API/UI change.
- No `ALGORITHM_VERSION` change.

Future conceptual path (not implemented here):

```
human-reviewed identity knowledge
        ↓
deterministic breed resolver
        ↓
NormalizationResult
        ↓
explicitly approved Core consumers
```

---

## 5. Observation vs policy

**OBSERVED** = what the repository currently does (code, tests, Phase C/D).  
**PROPOSED POLICY** = a candidate rule presented for human approval.  
**HUMAN DECISION** = empty until a human fills it.

Do not read OBSERVED as intended meaning.  
Do not read PROPOSED POLICY as approved.  
Do not read Ω12 tests as product policy.  
Do not read BreedNode capture tests as product policy.

---

## 6. Policy A — shared / generic breed terms

### POLICY A

**Status:** APPROVED

**POLICY_A_STATUS:** APPROVED  
**POLICY_A_DECISION:** APPROVE  
**POLICY_A_NOTES:** Human Phase F instruction. Shared/generic terms remain AMBIGUOUS. No automatic canonical selection. No ranking of candidates. No invented preferred breed. Examples: Cocker, Collie, Dachshund, Dog, English, Hound, Inu, Pinscher, Retriever, Sheepdog, Spaniel, Terrier.

**Decision required:** APPROVE / REJECT / REVISE — **APPROVE recorded**

### Proposed policy

If an input has multiple valid approved canonical candidates and there is no explicit approved disambiguation rule, the identity resolver returns **AMBIGUOUS**. It selects no canonical identity. Candidate list membership is the semantic property; candidate order must not imply ranking. A future product/API layer may later present candidates for clarification; that UX is outside this phase.

### Observed (repository / Phase D)

Ω12 `shared_name_token`: when a folded token is a name-token of **two or more** warehouse canonical breeds, `resolve_breed()` returns `AMBIGUOUS`, `canonical_id=None`, candidates in warehouse encounter order.

Evidence:

- `app/normalization/resolver.py` (`shared_name_token`)
- `tests/normalization/test_omega12_mapping.py::test_f_ambiguous_retriever`
- `tests/normalization/test_omega12_mapping.py::test_f_ambiguous_terrier`
- `tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved`
- Phase D cases D-01 … D-12

Legacy BreedNode: after alias normalize, exact match, then `str.contains` (pandas default regex) and `iloc[0]` — one row if any substring hits.

Evidence:

- `app/agent/nodes/breed_node.py`
- `tests/data/test_breed_node_baseline.py::test_contains_retriever_is_first_dataframe_contains_hit` (capture: `Retriever` → Golden Retriever)

Phase D D-04 `Dog` is a special observation: legacy selected **French Bulldog**; Ω12 candidates are German Shepherd Dog, Bernese Mountain Dog, Chinese Rural Dog. French Bulldog is **not** in that Ω12 candidate set.

Whether a shared token **must** remain AMBIGUOUS as product policy: **NOT ESTABLISHED BY CURRENT EVIDENCE** (Phase D: `NO_EXPLICIT_CONTRACT` on all twelve cases).

### Phase D cases under Policy A

| Case | Input | Legacy (observed) | Ω12 (observed) |
|------|-------|-------------------|----------------|
| D-01 | Cocker | American Cocker Spaniel | AMBIGUOUS — American Cocker Spaniel, English Cocker Spaniel |
| D-02 | Collie | Border Collie | AMBIGUOUS — Border Collie, Rough Collie |
| D-03 | Dachshund | Wirehaired Dachshund | AMBIGUOUS — Wirehaired, Smooth, Longhaired Dachshund |
| D-04 | Dog | French Bulldog | AMBIGUOUS — German Shepherd Dog, Bernese Mountain Dog, Chinese Rural Dog |
| D-05 | English | Old English Sheepdog | AMBIGUOUS — Old English Sheepdog, English Springer Spaniel, English Cocker Spaniel |
| D-06 | Hound | Afghan Hound | AMBIGUOUS — Afghan Hound, Basset Hound |
| D-07 | Inu | Shiba Inu | AMBIGUOUS — Shiba Inu, Akita Inu |
| D-08 | Pinscher | Miniature Pinscher | AMBIGUOUS — Miniature Pinscher, Doberman Pinscher |
| D-09 | Retriever | Golden Retriever | AMBIGUOUS — Golden Retriever, Labrador Retriever |
| D-10 | Sheepdog | Old English Sheepdog | AMBIGUOUS — Old English Sheepdog, Shetland Sheepdog |
| D-11 | Spaniel | Cavalier King Charles Spaniel | AMBIGUOUS — Cavalier, American Cocker, English Springer, English Cocker |
| D-12 | Terrier | Boston Terrier | AMBIGUOUS — seven warehouse terriers |

HUMAN DECISION: **APPROVED**

---

## 7. Policy B — unique colloquial / short breed names

### POLICY B

**Status:** APPROVED

**POLICY_B_STATUS:** APPROVED  
**POLICY_B_DECISION:** APPROVE  
**POLICY_B_NOTES:** Human Phase F instruction. Corgi, Husky, and Bulldog remain UNRESOLVED unless explicit approved knowledge exists. No aliases created in Phase F.

**Decision required:** APPROVE / REJECT / REVISE — **APPROVE recorded**

### Proposed policy

A unique-looking colloquial term is not automatically an approved identity. The resolver may resolve it only after an explicit human-approved mapping exists. Until that mapping exists:

- `Corgi` → UNRESOLVED
- `Husky` → UNRESOLVED
- `Bulldog` → UNRESOLVED

This phase does **not** create those aliases. This phase does **not** assign a canonical target.

### Observed (repository / Phase D)

Ω12: token appears in exactly one current canonical name **and** is not an approved alias → `UNRESOLVED` / `no_approved_mapping`. Catalog uniqueness ≠ approved identity knowledge.

Evidence:

- `app/normalization/resolver.py` (token hits used only when `len(token_hits) >= 2`)
- `app/normalization/identity.py` (`variants_for("corgi"|"husky"|"bulldog")` empty)
- `warehouse/mapping/breed_aliases.csv` — does not contain Corgi, Husky, or Bulldog
- `tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved`
- `tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants`
- Phase D D-13 … D-15; inactive candidate-knowledge rows with **no canonical target assigned**

Legacy BreedNode selected a single `contains` row:

- Corgi → Pembroke Welsh Corgi
- Husky → Siberian Husky
- Bulldog → French Bulldog

That selection is **EXISTING_RUNTIME_BEHAVIOR**. It is not an approved alias.

Whether any of these terms **must** remain unresolved as product policy, or later become aliases to a named identity: **NOT ESTABLISHED BY CURRENT EVIDENCE**.

### Phase D cases under Policy B

| Case | Input | Legacy (observed) | Ω12 (observed) |
|------|-------|-------------------|----------------|
| D-13 | Corgi | Pembroke Welsh Corgi | UNRESOLVED |
| D-14 | Husky | Siberian Husky | UNRESOLVED |
| D-15 | Bulldog | French Bulldog | UNRESOLVED |

HUMAN DECISION: **APPROVED**

---

## 8. Policy C — blank / missing breed input

### POLICY C

**Status:** APPROVED

**POLICY_C_STATUS:** APPROVED  
**POLICY_C_DECISION:** APPROVE  
**POLICY_C_NOTES:** Human Phase F instruction. Blank/whitespace identity input remains UNRESOLVED. Do not fall back to Beagle or the first warehouse row.

**Decision required:** APPROVE / REJECT / REVISE — **APPROVE recorded**

### Proposed policy

Blank or whitespace-only breed **identity** input is not interpreted as a specific breed:

- `""` → UNRESOLVED
- whitespace-only → UNRESOLVED

No fallback to the first warehouse row. No fallback to Beagle. No default breed selection.

This concerns identity resolution only. It does not define future UI for missing breed data.

### Observed (repository / Phase D)

Ω12: `is_blank` → `UNRESOLVED` / `blank_or_missing` / `InputState.NOT_PROVIDED`.

Evidence:

- `app/normalization/resolver.py` (`_blank_result`)
- `tests/normalization/test_omega12_mapping.py::test_q_blank_breed_is_not_provided` (`""`)
- `tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_blank_mixed_hyphen_and_intra_word_x`

Legacy BreedNode: empty / whitespace `contains` matches every row; `iloc[0]` is the first dataframe row, currently Beagle (`BREED_23ECEA52`).

Evidence:

- `app/agent/nodes/breed_node.py`
- `tests/data/test_breed_node_baseline.py::test_empty_primary_contains_all_and_takes_first_dataframe_row` (capture, not meaning contract)
- Phase D D-16, D-17

Whether blank input **must** stay unresolved as product identity policy: **NOT ESTABLISHED BY CURRENT EVIDENCE**.

Workbench missing-required-field HTTP behavior (`MISSING_REQUIRED_INPUT` for absent breed on some routes) is a separate API presence contract. It does not define BreedNode empty-string matching. Mapping that API contract onto identity-resolver blank policy: **NOT ESTABLISHED BY CURRENT EVIDENCE**.

### Phase D cases under Policy C

| Case | Input | Legacy (observed) | Ω12 (observed) |
|------|-------|-------------------|----------------|
| D-16 | `""` | Beagle | UNRESOLVED / `blank_or_missing` |
| D-17 | `"   "` | Beagle | UNRESOLVED / `blank_or_missing` |

HUMAN DECISION: **APPROVED**

---

## 9. Policy D — mixed breed expressions

### POLICY D

**Status:** APPROVED

**POLICY_D_STATUS:** APPROVED  
**POLICY_D_DECISION:** APPROVE  
**POLICY_D_NOTES:** Human Phase F instruction. Mixed expressions remain MIXED with ordered independently resolved components and no inferred percentages. Examples: Lab x Golden, Lab × Golden, Lab / Golden, Beagle x French Bulldog. Separators remain the already-implemented x / × / /.

**Decision required:** APPROVE / REJECT / REVISE — **APPROVE recorded**

### Proposed policy

Explicit mixed separators indicate MIXED input. The resolver:

1. identifies components,
2. resolves each component independently where possible,
3. preserves component order,
4. returns MIXED,
5. does not infer percentages,
6. does not assume 50/50,
7. does not collapse the expression into a single canonical breed.

Example (observed Ω12, not a newly invented mapping):

`Lab x Golden` → MIXED  
components in expression order: Labrador Retriever, Golden Retriever.

This phase does not broaden mixed separators beyond the separators already implemented (`x` / `×` / `/` with the existing standalone-separator rule).

Intra-word letter `x` is not a mixed separator. Phase D warehouse intra-word case is **Foxhound** (both paths RESOLVED; not a disagreement). Ω12 tests also assert `Boxer` is not MIXED; Boxer is not a current warehouse canonical identity (`test_r_intra_word_x_is_not_mixed`). Boxer is **not** one of the 21 Phase D disagreements.

Structured profile fields `primary_breed` / `secondary_breed` / `breed_split_pct` remain a separate input surface from mixed **strings**.

### Observed (repository / Phase D)

Ω12 `_MIXED_SPLIT` and `_try_mixed_breed`: status `MIXED`, `canonical_id=None`, components in split order, rule `mixed_breed_separator`.

Evidence:

- `app/normalization/resolver.py`
- `tests/normalization/test_omega12_mapping.py::test_r_mixed_breed_is_not_a_new_canonical_breed` (`Labrador x Golden`)
- `tests/normalization/test_omega12_mapping.py::test_r_slash_mixed_breed`
- `tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_blank_mixed_hyphen_and_intra_word_x`
- Phase D D-18 … D-21

Legacy BreedNode treated the whole string as one matcher name and selected **none** on these four Phase D mixed inputs.

Whether Core consumers **must** consume MIXED components (vs ignore mixed strings, vs collapse them): **NOT ESTABLISHED BY CURRENT EVIDENCE**.

### Phase D cases under Policy D

| Case | Input | Legacy (observed) | Ω12 (observed) |
|------|-------|-------------------|----------------|
| D-18 | Lab x Golden | selected=no | MIXED — Labrador Retriever, Golden Retriever (aliases) |
| D-19 | Lab × Golden | selected=no | MIXED — same components |
| D-20 | Lab / Golden | selected=no | MIXED — same components |
| D-21 | Beagle x French Bulldog | selected=no | MIXED — Beagle, French Bulldog (canonical names) |

HUMAN DECISION: **APPROVED**

---

## 10. Current Ω12 behavior (summary)

Facade: `resolve_breed()` in `app/normalization/resolver.py`, exported from `app/normalization/__init__.py`. Delegates to `resolve_raw(..., EntityKind.BREED)`. `_resolve_identity` was not rewritten for this gate.

Approved display aliases currently in `warehouse/mapping/breed_aliases.csv`:

| Alias | Canonical |
|-------|-----------|
| Lab | Labrador Retriever |
| Labrador | Labrador Retriever |
| Golden | Golden Retriever |
| German Shepherd | German Shepherd Dog |
| GSD | German Shepherd Dog |

Canonical exact names (48 warehouse identities) currently RESOLVE when the input is that display name. Phase C recorded those as SAME with legacy. They are **not** among the 21 Phase D disagreements.

Statuses used by Ω12: `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED`, `MIXED`.

---

## 11. Current legacy behavior where relevant

`BreedNode.execute` (`app/agent/nodes/breed_node.py`):

1. `names = [primary_breed]` plus `secondary_breed` if truthy.
2. `platform.normalize_breed_name` (alias map, including the same five display aliases plus canonical self-aliases).
3. Exact case-insensitive column match on `breed`.
4. Else `str.contains(key, na=False)` (pandas default regex).
5. If any hit: `iloc[0].to_dict()`.

Phase 5.8.2 tests capture this as **current behavior**, including:

- `Retriever` → first contains hit (Golden Retriever in the current dataframe)
- `""` → first dataframe row (Beagle in the current warehouse)

Those tests do not state product identity meaning.

---

## 12. The 21 Phase D cases grouped by policy

Confirmed against `docs/PHASE_D_BREED_IDENTITY_SEMANTIC_REVIEW.md`. No extra policy cases added. Case classifications were not modified.

| Policy | Cases | Count |
|--------|-------|-------|
| A shared / generic | D-01 … D-12 | 12 |
| B unique colloquial | D-13 … D-15 | 3 |
| C blank | D-16, D-17 | 2 |
| D mixed | D-18 … D-21 | 4 |
| **Total** | | **21** |

All 21 remain `REQUIRES_HUMAN_DECISION` at the Phase D case level. This gate does not close any of them.

---

## 13. Human decision fields

Copy/fill by the human/domain/product owner. Do not treat pre-filled PENDING as approval.

```
POLICY A
Status: APPROVED
Decision required: APPROVE / REJECT / REVISE
POLICY_A_STATUS: APPROVED
POLICY_A_DECISION: APPROVE
POLICY_A_NOTES: Shared/generic terms remain AMBIGUOUS. No automatic selection. No candidate ranking.

POLICY B
Status: APPROVED
Decision required: APPROVE / REJECT / REVISE
POLICY_B_STATUS: APPROVED
POLICY_B_DECISION: APPROVE
POLICY_B_NOTES: Corgi / Husky / Bulldog remain UNRESOLVED without approved mapping. No aliases added.

POLICY C
Status: APPROVED
Decision required: APPROVE / REJECT / REVISE
POLICY_C_STATUS: APPROVED
POLICY_C_DECISION: APPROVE
POLICY_C_NOTES: Blank/whitespace remains UNRESOLVED. No Beagle / first-row fallback.

POLICY D
Status: APPROVED
Decision required: APPROVE / REJECT / REVISE
POLICY_D_STATUS: APPROVED
POLICY_D_DECISION: APPROVE
POLICY_D_NOTES: Explicit x / × / / remains MIXED. Ordered independent components. No inferred percentages.
```

Recorded by Phase F from the explicit human instruction. Ω12 current behavior is unchanged. Core consumers are unchanged.

---

## 14. Non-decisions

The original D.5 deliverable did **not** approve A–D (fields were PENDING).

Phase F recorded human APPROVED on A–D in this file only. Phase F still did **not**:

- add aliases (including Corgi / Husky / Bulldog)
- modify Ω12 resolver semantics
- modify the identity provider
- migrate BreedNode, RISK, Biology, Epidemiology, scientific_care, or FormulaGraph
- call `resolve_breed()` from Core consumers
- change API or B2C UI
- add Mongo, LLM, fuzzy matching, or a third engine
- infer mixed-breed percentages
- rank AMBIGUOUS candidates
- treat warehouse uniqueness as ontology uniqueness
- treat legacy first-row / contains hits as approved knowledge
- implement any Core migration implied by A–D

---

## 15. Phase E / implementation entry conditions

Human decisions A–D are now **APPROVED** in this file.

Phase E (breed input / dog evidence **design**) already exists as `docs/PHASE_E_BREED_INPUT_AND_DOG_EVIDENCE_DESIGN.md` and did not implement Core migration.

Approval of A–D does **not** authorize:

- BreedNode migration
- FormulaGraph consumer migration
- alias creation
- API / UI change
- Mongo / LLM

A **separate** gated implementation phase is still required before any of those. Unapproved candidate knowledge stays inactive. Do not treat Ω12 tests or BreedNode capture tests as a substitute for that later gate.

---

## 16. Change log / implementation status

| Item | Status |
|------|--------|
| Policy decision record created | YES — this file |
| Human APPROVED recorded for A–D | YES — Phase F documentation update |
| Policies implemented in code | NO |
| Aliases added | NO |
| Ω12 changed | NO |
| Core consumers migrated | NO |
| Warehouse / mapping data changed | NO |
| Tests added that encode proposed policy as approved | NO |
| Phase E design | YES — separate design artifact; not implementation |
| Phase F Core implementation | NO |

**Implementation status:** documentation / policy gate only.

---

## 17. Git / dirty-tree note

This phase added only this artifact. Pre-existing unrelated uncommitted repository work was not overwritten.
