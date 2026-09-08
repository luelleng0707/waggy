# Ω12 Normalization + Entity Mapping — Design

Status: IMPLEMENTED (see `docs/omega12-normalization-entity-mapping-report.md`).
Date: 2026-09-08.
Ω11 baseline: PASS WITH GAPS (`docs/omega11-agent-data-contract-report.md`).
Engine version: `ALGORITHM_VERSION = 2.1.0` (unchanged).
Ω11 schema: `1.0.0` (unchanged).
Ω12 mapping config version: `1.0.0` (separate from the algorithm version).

## 1. Problem

Callers use informal strings (`Lab`, `HD`, `very dense coat`) for entities that already have warehouse IDs (`BREED_B02F1BE9`, `COND_653473C1`). There is no fail-closed, inspectable mapping result that preserves raw → normalized → canonical → why.

Existing engine breed aliases (`app/data/warehouse_biology.py` `_BREED_ALIASES`) silently rewrite names for RISK_V2_1. They do not return AMBIGUOUS/UNRESOLVED and are not a public mapping contract.

## 2. Scope

- Representation fold: trim, case-fold, collapse internal whitespace.
- Exact lookup against canonical warehouse identity tables + explicit alias CSVs.
- Shared-token ambiguity (e.g. `retriever` matches two breed names) → AMBIGUOUS.
- Mixed-breed separators → MIXED (components), never a new breed entity.
- Typed `NormalizationResult` using Ω11 `DomainKind`.
- Observation aliases remain `OBSERVATION`.

## 3. Non-scope

Scientific reasoning, prevalence, optimizer, HTTP adapter defaults, Gemini, MCP, tool server, RAG, web lookup, fuzzy Levenshtein, lb→kg body-weight conversion, creating canonical entities, rewriting warehouse facts, wiring this layer into `generate_reproducible_report`.

## 4. Current repository behavior

| Mechanism | Location | Notes |
|---|---|---|
| Breed display aliases | `warehouse_biology._BREED_ALIASES` | Lab, Labrador, Golden, GSD, German Shepherd → canonical **names**. On the engine path. Ω12 copies these as mapping data; does not change the tuple. |
| Identity aliases | `_project_aliases` | Each `breed_name` aliases to itself. |
| `DataRepository.normalize_breed_name` | `app/data/repository.py` | Lowercase lookup; unknown returns original strip. **Does not fail closed.** |
| `condition_key` | `app/inference/resolver.py` | Slugify only — not ID resolution. |
| Ingredient aliases | `warehouse/science_graph/ingredient_aliases.csv` | Scientific/mechanistic; **not** used by Ω12. |
| UnitNormalizer | `app/data/warehouse/units.py` | Maps kg→mg for warehouse tooling. **Not** used for dog body weight. |
| HTTP defaults | `profile_from_analyze_body` | age=5, weight=20. Ω12 must not reintroduce these. |
| Ω11 `CanonicalDogInput` | `app/contracts/agent/input.py` | Missing fields stay NOT_PROVIDED. |

## 5. Canonical entity sources (read-only)

| Entity | File | ID | Name |
|---|---|---|---|
| Breed | `warehouse/biology/breeds.csv` | `breed_id` | `breed_name` |
| Condition | `warehouse/biology/conditions.csv` | `condition_id` | `condition_name` |
| Product | `warehouse/commercial/product_master.csv` | `product_id` | `product_name` |
| Brand | distinct `brand` on product_master | brand string | brand string |

Demo catalog overlay is **not** a mapping source (process-global demo must not change Ω12).

## 6. Normalization rules

1. `None` / `""` / whitespace-only → UNRESOLVED (or MISSING_REQUIRED_INPUT when the caller asked to resolve a required field). Never age=5 / weight=20.
2. Trim; case-fold for lookup; collapse runs of whitespace to one space.
3. Do not strip hyphens (`X-Y` vs `XY`).
4. Do not substring-extract entities from claim-like sentences.
5. Full-string exact match only against the folded key.

## 7. Mapping rules

Lookup order:

1. Exact folded key = canonical name or canonical ID.
2. Exact folded key = explicit alias row (must point at a real warehouse ID).
3. If the folded key is a whitespace token that appears in **two or more** canonical names of that kind → AMBIGUOUS with candidates.
4. Else UNRESOLVED.

Alias CSVs live in `warehouse/mapping/` (identity aliases, not scientific facts). Load-time: alias → unknown ID is an error; alias → two IDs is AMBIGUOUS for that key.

## 8. Ambiguity

`retriever` → Golden Retriever + Labrador Retriever → AMBIGUOUS. Do not pick Labrador.

## 9. Unresolved

`fluffster` → UNRESOLVED. Do not create `fluff_dog`.

## 10. Domain semantics

`EntityKind` (lookup kind) is not Ω11 `DomainKind`. Results set `domain_kind`:

| EntityKind | DomainKind |
|---|---|
| breed, sex, age_years, weight_kg | USER_INPUT |
| observation | OBSERVATION |
| condition (identity only) | USER_INPUT — **not** SCIENTIFIC_FACT |
| product | PRODUCT_FACT |
| brand | COMMERCIAL_CONFIGURATION |

Never emit SCIENTIFIC_EVIDENCE, SCIENTIFIC_FACT, SCIENTIFIC_INFERENCE, RECOMMENDATION, or PROJECTION from this layer.

## 11. Evidence boundary

`HD` → `COND_653473C1` / Hip Dysplasia. Stop. No prevalence.

## 12. Determinism

Pure functions + immutable catalog loaded from CSVs. No `datetime.now()`, random, LLM, or HTTP.

## 13. Tests

`tests/normalization/` — exact, alias, case/whitespace, unresolved, ambiguous, mixed, collisions, domain attacks, no defaults, determinism.

## 14. Known limitations

- Not on the engine/HTTP path (by design).
- Observation vocabulary is Ω12 mapping-only (`dense_coat`), not a warehouse trait fact.
- No lb→kg.
- Shared-token rule is exact token equality, not fuzzy match.
- Ingredient science aliases unused.

## 15. Future integration

Ω16 may call this resolver before tools. Ω13 evidence validation is separate. Engine may later consume RESOLVED IDs — not in Ω12.
