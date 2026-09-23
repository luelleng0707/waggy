# Waggy / Wagtopia System

This is the **single authoritative project document**. Older Ω-phase reports, recovery inventories, and competing architecture markdown files are historical (`docs/archive/` or `legacy/docs/`).

If this file and the code disagree, **the code wins**. Update this file.

Aliases that only point here: `docs/WAGTOPIA_SYSTEM_ARCHITECTURE.md`, `docs/WAGTOPIA_SYSTEM_SPEC.md`.

---

## Ω10 runtime (current)

```
Dog
 → Breed resolver (DataRepository aliases)
 → Canonical biology warehouse (warehouse/biology + warehouse/prevention)
 → Breed traits (phenotype; many rows MISSING_PROVENANCE)
 → Observed breed conditions (cited intern prevalence)
 → Trait → condition associations (cited; listed separately, never summed into a fake estimate)
 → Preventative Health Analysis
 → Condition → nutrient / ingredient warehouse rows
 → Nutrition requirement engine + demo dry-matter product densities
 → PACKAGE_OPTIMIZER_V2_1 (2^N−1 exhaustive search, hard min/max)
 → Ranked Essential / Balanced / Optimal packages
 → One canonical result → Customer / Groomer / Business / Developer
```

`demo_breed_care.py` is **not** on this path. If the warehouse has no observed rows for the dog, Health Analysis returns `NOT_AVAILABLE`. It does not invent Labrador/Golden joint/skin pathways.

Demo catalog (`WAGTOPIA_DEMO_MODE`) remains a **commercial** overlay only.

Nutrition Facts is a **modal** (`waggy-frontend/index.html` `#nutrition-modal`). Package cards show product **names**, not SKUs.

---

## Document map

1. System purpose
2. Repository structure
3. Warehouse architecture
4. Scientific evidence model
5. Dog input model
6. Biology engine
7. Epidemiology engine
8. Estimation engine
9. Prevention engine
10. Nutrition requirement engine
11. Product matching
12. Exhaustive combination enumeration
13. Nutrient constraint filtering
14. Bundle optimization
15. Essential Care
16. Balanced Care
17. Optimal Care
18. Budget logic
19. Explainability
20. Canonical result
21. Role projections
22. API architecture
23. Frontend architecture
24. Demo data boundary
25. Scientific limitations
26. Testing strategy
27. Provenance strategy
28. Future AI boundary
29. Health Analysis
30. Nutrition Facts modal
31. Recovery history
32. Current data inventory
33. NEEDS_VALIDATION and MISSING_PROVENANCE
34. Agent data contracts (Ω11)
35. Normalization + entity mapping (Ω12)
36. Canonical API contract (Ω16)
37. Persistent dog state (Ω17.1)
38. Preference-aware recomputation (Ω17.2)
39. Recalculation provenance (Ω17.3)
40. Bounded tool gateway (Ω17.4)

---

# 1. System purpose

Wagtopia produces deterministic dog-wellness analysis:

```
ONE INPUT
    ↓
ONE ANALYSIS (PPIEWellnessAgent.generate_reproducible_report)
    ↓
ONE CANONICAL RESULT (canonical_analysis.v1)
    ↓
Customer / Groomer / Business / Developer projections
```

Role switching **never reruns** the engine. `POST /api/v1/presentation/workbench` runs analysis once.

There is **one** package composer: `PACKAGE_OPTIMIZER_V2_1` (`app/agent/package_optimizer.py` → `app/agent/package_search.py`).

Do not create role-specific algorithms. Do not create a second optimizer. Do not move calculation logic into the frontend. Do not use an LLM to choose products, nutrients, bundles, prices, or rankings.

LLM used for package composition = **NO**.

---

# 2. Repository structure

Directories that actually exist and matter:

| Path | Purpose |
|---|---|
| `app/` | Production FastAPI runtime, agent pipeline, presentation adapters |
| `app/agent/` | `PPIEWellnessAgent`, FormulaGraph nodes, `package_optimizer.py`, `package_search.py`, response assembler |
| `app/data/` | Warehouse-backed `DataRepository`, demo **catalog** overlay, nutrient requirements, `scientific_care.py` |
| `app/api/` | HTTP routes (`app/api/main`; `app/main.py` is a shim) |
| `app/presentation/` | Role projections of the canonical analysis. Does not compose packages. |
| `app/inference/` | Explainability wrappers around existing formula IDs |
| `app/science/` | Science-graph helpers for warehouse-backed evidence when present |
| `app/debug/` | Calculation / validation console traces |
| `app/ui/` | Server-rendered templates and CSTC desktop helpers (compatibility) |
| `warehouse/` | Immutable CSV scientific/commercial fact store. No Python. No inferred scores. |
| `repository/` | Warehouse loaders, MAT formula runtime, optimization **helpers**. **Does not** choose customer package SKUs. |
| `waggy-frontend/` | Portable product workbench. Copy this directory to run the UI against a Waggy HTTP API. |
| `legacy/` | Archived classic/business shells and Clinical Execution Explorer. Not the active product UI. |
| `tests/` | Unit, optimizer, interface, mathematics, warehouse QA |
| `scripts/` | `run_dev.py` (canonical local launcher), warehouse validation, Railway helpers |
| `docs/` | This architecture document, contributor notes, mathematics CSV inventories |

There is **no** `repository/frontend` production app. The live UI is `waggy-frontend/` (served by FastAPI at `GET /`, or independently via `node scripts/serve.mjs`).

Historical docs described `warehouse -> repository/engine -> repository/api -> repository/frontend`. That is **not** the running customer path. The running path is:

```
warehouse CSVs + optional demo overlay
  → DataRepository
  → PPIEWellnessAgent / FormulaGraph
  → PACKAGE_OPTIMIZER_V2_1 (app/agent/package_search.py)
  → presentation adapter
  → FastAPI HTTP contracts
  → waggy-frontend API client
  → workbench
```

`repository/optimization` and `repository/mathematics` remain tested parallel layers for warehouse-backed risk/epidemiology math. They must not be confused with `PACKAGE_OPTIMIZER_V2_1`.

---

# 3. Warehouse architecture

## Warehouse

`warehouse/` is immutable source data. Scientific facts are stored rows, not inferred scores.

Evidence-bearing relationship rows should preserve, when present:

- `scientific_quote`
- `paper_name`
- `paper_link`
- `publication_year`
- `study_type`
- `species`
- `status`

**Entity data** (breeds, products, ingredients, conditions) is identity and attributes.

**Evidence-bearing relationship data** (breed↔condition, ingredient↔mechanism, paper citations) is where scientific claims live.

The warehouse currently has **open validation blockers** (foreign-key mismatches). See §20. `scripts/validate_warehouse.py` emits `docs/validation_report.md` (generated artifact, not an architecture spec).

## Two data planes (must not be mixed)

| Plane | What it is | What it is not |
|---|---|---|
| Warehouse CSVs | Intended scientific/commercial facts | Currently incomplete for product personalization |
| Demo overlay (`WAGTOPIA_DEMO_MODE=true`) | Synthetic commercial catalog + synthetic product densities | Scientific evidence |
| Secondary AAFCO-style summary (`app/data/scientific_requirements.py`) | Modeled baseline nutrient densities transcribed from project source material (PetMD-style AAFCO summary) | Primary AAFCO tables; warehouse evidence |

Never call demo products scientifically validated. Never upgrade the secondary summary to “primary AAFCO.”

---

# 4. Scientific evidence model

Evidence lives on **relationships**, not on isolated entities:

breed → trait → condition/pathway → nutrient/ingredient → product

Where a paper exists, attach it to the relationship row (`scientific_quote`, `paper_name`, `paper_link`, `publication_year`). Do not attach a single paper to a condition when multiple papers can support that condition.

If prevalence data does not exist: **do not fabricate a probability**. Use `NOT_AVAILABLE` / “Not available from current scientific warehouse.” Trait associations may be listed separately; they are never summed into a fake combined estimate.

Demo synthetic breed-care is disabled at runtime. Never silently upgrade demo catalog products to warehouse evidence.

Warehouse-backed MAT stack (not package membership): MAT-1001 MAT-1002 MAT-1003 MAT-1004 MAT-1005 MAT-1006 MAT-1007 MAT-1008.

---

# 5. Dog input model

Canonical input is `DogProfileInput` / `profile` on the analyze payload: name, breeds, age/birthday, weight, sex, activity, environment, observed conditions, optional monthly budget, optional groomer `role_context`.

Groomer observations on a **request** still require a new analysis. Ω17.1 also persists dog identity and longitudinal events in SQLite (`app/state/`). That store is **dog-specific state**, not a scientific knowledge base. Projection is fail-closed via `profile_from_workbench_body`. See [omega17.1-dog-state.md](omega17.1-dog-state.md).

---

# 6. Biology engine

FormulaGraph stages: profile normalization, breed / morphology, biological traits, observed conditions. Mixed-breed warehouse mathematics currently resolves breed using `profile.breeds[0]` in `WarehouseBackedDogResolver.resolve` / `repository/pipeline/biological_runtime.py`. Additional breeds are ignored in that MAT path. Package Essential minima still do not use breed.

---

# 7. Epidemiology engine

Warehouse-backed observed prevalence is MAT-1001 when evidence rows exist. Demo breed-care does **not** invent epidemiological percentages.

---

# 8. Estimation engine

Estimated prevalence / risk is MAT-1002 / MAT-1003 when warehouse evidence exists. MAT-1003 Bayesian-style blend has no explicit likelihood; **METHODOLOGICAL_REDESIGN_REQUIRED: true**. MAT-1005 uncertainty bounds are **not a formal statistical confidence interval**. MAT-1004: **agreement is not confidence**.

---

# 9. Prevention engine

Prevention / activity / grooming nodes emit structured recommendations. Breed-care pathways are **preventative considerations**, never diagnoses. Language: “higher prevalence / increased risk”, “associated pathway”. Never “your dog has X”.

## FormulaGraph pipeline

Actual FormulaGraph / agent stages (implemented):

```
INPUT (DogProfileInput)
→ NORMALIZATION / profile
→ BREED / morphology
→ BIOLOGICAL TRAITS
→ OBSERVED CONDITIONS
→ ESTIMATED / RISK (warehouse-backed when data exists)
→ PREVENTION / ACTIVITY / GROOMING
→ NUTRITION TARGETS (matcher nutrients — often empty in demo)
→ PRODUCT_MATCH_V2_1 (may return zero products)
→ PACKAGE_OPTIMIZER_V2_1 exhaustive search (independent of matcher)
→ ASSESSMENT / REPORT / VALIDATION / TRACE
→ CANONICAL RESULT
→ ROLE PROJECTIONS
```

**CURRENT / DONE:** profile, breed, biology, risk, activity, nutrition node, product match, package optimizer V2.1, workbench projections.

**PARTIAL:** warehouse-backed scientific product matching (empty matcher output in demo is expected).

**FUTURE:** primary AAFCO tables in warehouse; non-synthetic product densities; warehouse-backed breed-care `*`; clinical diagnosis.

`PRODUCT_MATCH_V2_1` and `PACKAGE_OPTIMIZER_V2_1` are **independent**. Empty matcher output does not empty packages. Packages come from the active catalog.

Coarse presentation-pipeline labels used in architecture tests: profile normalization, biological resolution, evidence collection, mathematical assessment, optimization, presentation projection.

---

# 10. Nutrition requirement engine

Source: `app/data/scientific_requirements.py`.

- Basis: **nutrient density per kg dry matter**, not a standalone “daily gram” published by the source.
- Life stage: puppy/growth if age < 1 year; senior if age ≥ 7 (senior **numeric** minima are `NOT_AVAILABLE` — adult maintenance reused); else adult maintenance.
- Size/weight: recorded; used to **scale daily dry-matter intake**, not to change % DM minima.
- Breed: **not** used for baseline minima.

If the source does not specify a maximum: **NOT SPECIFIED IN MODELED SOURCE**. Do not invent one.

### Adult maintenance (demo dog age 4.3)

| Nutrient | Unit | Minimum | Maximum |
|---|---|---|---|
| Protein | % DM | 18.0 | NOT SPECIFIED IN MODELED SOURCE |
| Fat | % DM | 5.5 | NOT SPECIFIED IN MODELED SOURCE |
| Calcium | % DM | 0.5 | 2.5 |
| Phosphorus | % DM | 0.4 | 1.6 |
| Magnesium | % DM | 0.06 | NOT SPECIFIED IN MODELED SOURCE |
| Potassium | % DM | 0.6 | NOT SPECIFIED IN MODELED SOURCE |
| Sodium | % DM | 0.08 | NOT SPECIFIED IN MODELED SOURCE |
| Chloride | % DM | 0.12 | NOT SPECIFIED IN MODELED SOURCE |
| Iron | mg/kg DM | 40.0 | NOT SPECIFIED IN MODELED SOURCE |
| Copper | mg/kg DM | 7.3 | NOT SPECIFIED IN MODELED SOURCE |
| Zinc | mg/kg DM | 80.0 | NOT SPECIFIED IN MODELED SOURCE |
| Manganese | mg/kg DM | 5.0 | NOT SPECIFIED IN MODELED SOURCE |
| Selenium | mg/kg DM | 0.35 | 2.0 |
| Iodine | mg/kg DM | 1.0 | 11.0 |
| Vitamin A | IU/kg DM | 5000 | 250000 |
| Vitamin D | IU/kg DM | 500 | 3000 |
| Vitamin E | IU/kg DM | 50 | NOT SPECIFIED IN MODELED SOURCE |
| Vitamin B1 | mg/kg DM | 2.25 | NOT SPECIFIED IN MODELED SOURCE |
| Vitamin B2 | mg/kg DM | 5.2 | NOT SPECIFIED IN MODELED SOURCE |
| Vitamin B6 | mg/kg DM | 1.5 | NOT SPECIFIED IN MODELED SOURCE |
| Niacin (B3) | mg/kg DM | 13.6 | NOT SPECIFIED IN MODELED SOURCE |
| Pantothenic acid (B5) | mg/kg DM | 12.0 | NOT SPECIFIED IN MODELED SOURCE |
| Folic acid (B9) | mg/kg DM | 0.216 | NOT SPECIFIED IN MODELED SOURCE |
| Choline | mg/kg DM | 1360 | NOT SPECIFIED IN MODELED SOURCE |

Growth (age < 1) uses the `growth_min` / `growth_max` fields in the same module (higher protein/fat/Ca/P, etc.).

**NOT_MODELED:** water; carbohydrate/fiber (named in the source, no numeric min/max).

Statuses used by the ledger:

- Hard minimum / hard maximum → `FAIL_MINIMUM` / `FAIL_MAXIMUM` invalidate the whole bundle
- `PASS`, `LOW` (just above minimum), `NEAR_MAXIMUM` (≥80% of max, still ≤ max), `NO_MODELED_MAXIMUM`, `NOT_MODELED`, `NO_MODELED_MINIMUM`
- Breed-preventive `*` is **not** a baseline minimum

---

# 10. Nutrition requirement engine — nutrient calculation

Implemented in `app/data/demo_scientific_dataset.py` (`product_daily_contribution`, `aggregate_contributions`). Used by `evaluate_bundle`. There is **no** second calculator in JavaScript.

Reference weight = 30 kg. Serving scale = `weight_kg / 30`.

For an ingestible product:

```
servings     = servings_per_day × (weight_kg / 30)
as_fed_g     = serving_size_g × servings
daily_dm_g   = as_fed_g × (dry_matter_percent / 100)
daily_dm_kg  = daily_dm_g / 1000
```

Percent nutrients (grams/day):

```
grams_per_day = (% DM / 100) × daily_dm_g
```

Density nutrients (amount/day):

```
amount_per_day = density_per_kg_DM × daily_dm_kg
```

`extra_per_serving` is an absolute daily addend scaled by servings.

Bundle aggregation (never add as-fed percentages across products):

```
total_dm_g = Σ daily_dm_g
% DM       = 100 × Σ(grams_per_day) / total_dm_g
mg or IU per kg DM = Σ(amount_per_day) / (total_dm_g / 1000)
```

Derived daily requirement (UI):

```
required_daily_min = source_density_min × dog_daily_dm_kg
  (for % DM: minimum/100 × daily_dm_g)
```

### Worked example (runtime, Dolly 30 kg adult, SF002 + TR007)

Daily DM ≈ 0.302 kg/day.

| Nutrient | Actual DM | Source min | Derived daily min | Actual / day | % min | Max | Status |
|---|---|---|---|---|---|---|---|
| Protein | 19.87% DM | 18% DM | 54.36 g/day | 60 g/day | 110% | NOT SPECIFIED | NO_MODELED_MAXIMUM |
| Fat | 8.94% DM | 5.5% DM | 16.61 g/day | 27 g/day | 163% | NOT SPECIFIED | NO_MODELED_MAXIMUM |
| Calcium | 0.79% DM | 0.5% DM | 1.51 g/day | 2.4 g/day | 159% | 2.5% DM | PASS |
| Vitamin D | 1904 IU/kg DM | 500 | 151 IU/day | 575 IU/day | 381% | 3000 IU/kg DM | PASS |
| Choline | 1457 mg/kg DM | 1360 | 411 mg/day | 440 mg/day | 107% | NOT SPECIFIED | LOW (still valid) |

SF002 staple at 30 kg: 400 g as-fed × 75% DM = 300 g DM. TR007 adds 2 g DM.

---

# 11. Product matching

`PRODUCT_MATCH_V2_1` may return zero products. It is independent of `PACKAGE_OPTIMIZER_V2_1`. Empty matcher output does not empty packages.

---

# 12. Exhaustive combination enumeration

**Sole composer** of care-package membership. Code: `app/agent/package_optimizer.py` → `app/agent/package_search.py`.

For N catalog products, every non-empty subset is evaluated:

```
candidate_count = 2^N − 1
```

Demo catalog N = 12 → **4095**. Method: `EXHAUSTIVE_ENUMERATION` when N ≤ 14. Larger N uses bounded enumeration (`BOUNDED_ENUMERATION_MAX_SIZE`) — not used by the 12-product demo.

For each candidate:

1. Daily amounts / DM / every modeled nutrient (same functions as §6).
2. Structural staple rule (≥1 staple). Failure → `FAIL_CATEGORY` / missing staple. **Not ranked.**
3. Every nutrient vs minimum. Any miss → `FAIL_MINIMUM`. **Not ranked.**
4. Every nutrient vs maximum **when specified**. Any exceed → `FAIL_MAXIMUM`. **Not ranked.**
5. Care-pathway score (after validity).
6. Budget applied **after** nutrient validity (per tier).
7. Dominance computed as an **audit statistic** (`non_dominated_count`). It is **not** the customer display filter.
8. Rank **all** tier-eligible nutrient-valid bundles; display top `PACKAGE_DISPLAY_LIMIT` (20, cap 50).

A bundle is **not** valid because average nutrition looks good. **Every** modeled nutrient must pass. Care score cannot compensate. Budget cannot make an invalid bundle valid.

```
actual < minimum  → FAIL_MINIMUM  → removed before ranking
actual > maximum  → FAIL_MAXIMUM  → removed before ranking
both pass         → nutrient-valid
```

There is no “close enough” threshold and no average-nutrition override.

---

# 13. Nutrient constraint filtering

Every returned option includes `nutrition_ledger` / `nutrition_facts` produced from the optimizer rows, not recomputed in the browser.

Per nutrient (canonical fields): `nutrient_id`, display name, unit, `actual_density_dm`, `actual_per_day`, `required_density_min_dm`, `required_daily_min`, `maximum_density_dm`, `maximum_daily_amount`, statuses, `%` of min/max, headroom, source, `breed_recommended`.

Customer table columns: Nutrient | Per Pack / Daily Pack | Required Daily Amount | Maximum Daily Amount | % of Minimum | Status.

Developer view also shows density (actual / min / max DM) and product × nutrient contributions.

---

# 14. Bundle optimization

Ranking and scoring after hard constraints. Exact sort keys are in `RANKING_RULES` / `_rank_tier`.

---

# 15. Essential Care

Three **ranking policies** over the same nutrient-valid universe. Not three optimizers.

| | Essential | Balanced | Optimal |
|---|---|---|---|
| Purpose | Minimum viable nutritional care | Baseline + breed-preventive considerations | Best-scoring valid package |
| Breed-care eligibility | No | Yes: `care_coverage > 0` when pathways exist | No (all nutrient-valid) |
| Breed-care ranking | No | Yes (first sort key) | Yes (in overall score) |
| Budget | Hard ceiling if supplied | Hard ceiling if supplied | **No** ceiling; cost informational |
| Rank order | monthly cost ↑, product count ↑, score ↓, bundle_id | care ↓, nutrition_balance ↓, cost ↑, count ↑, bundle_id | overall_score ↓, balance ↓, care ↓, count ↑, cost ↑, bundle_id |

Displayed: 20 of N valid combinations per tier. UI must say “20 of 1152 …”, not imply only 20 existed.

---

# 16. Balanced Care

Baseline = size, life stage, modeled DM minima/maxima.

Breed-specific `*` only when the backend sets `breed_recommended = true` from warehouse preventative ingredient→nutrient mapping in `scientific_care.py` (currently zinc when a cited zinc row exists). Intern phenotype used for estimation is flagged `MISSING_PROVENANCE` and is not treated as validated science.

Labrador Retriever × Golden Retriever Health Analysis uses intern `observed_breed_conditions.csv` (hip dysplasia 12.7% / 14.9%, Labrador obesity 18.5%, Golden atopic dermatitis 13.2%) with paper names, quotes, and PMC links.

Legend:

> * Breed-specific preventative target derived from warehouse ingredient–condition evidence.

Do not star ordinary healthy nutrients. Essential must not show breed `*`.

Do not claim a supplement reduces disease chance unless a warehouse row says so.

---

# 19. Explainability

Each displayed option includes `products[]` and `product_provenance` (developer; customer gets selection_reason).

Counterfactual: remove product X, re-evaluate remaining combo.

Runtime example:

- SF002: “Provides baseline staple nutrition required for adult maintenance 30.0 kg dog.”
- TR007: “Raises modeled Choline density above the adult maintenance minimum (1200.0 → 1456.95 mg/kg DM; required 1360.0).”

`why_ranked` is generated from rank, valid count, and score components. Not LLM prose.

---

## Rejected-bundle traceability

Developer explorer (from search provenance, not invented strings):

Runtime Dolly demo:

- SF002 → `FAIL_MINIMUM` choline 1200 < 1360 mg/kg DM
- SF001 + TR003 → `FAIL_MAXIMUM` vitamin D 3974 > 3000 IU/kg DM → REMOVED FROM CANDIDATE SET

Funnel counters and per-nutrient failure counts are runtime-generated. Do not hardcode 4095 or 1152 in frontend logic.

---

# 17. Optimal Care

Optimal uses baseline + all supported preventative pathways, nutrient balance, diversity, and complementarity. Price is secondary. Nutrient safety maximums remain hard. No customer budget ceiling.

---

# 18. Budget logic

Exact sort keys are in `RANKING_RULES` / `_rank_tier` in `package_search.py` (see §9).

`SCORE_WEIGHTS` feed `overall_score` (used as Essential tie-break and Optimal primary key). Essential care weight = 0.

Diversity (`_diverse`) exists in the module but **display truncation is rank-then-slice**, not Pareto-then-show-7.

---

## Exhaustive search statistics

Provenance fields (runtime; example values from Dolly 12-product demo, not production constants):

| Field | Example |
|---|---|
| generated / evaluated | 4095 |
| structurally eligible | 3072 |
| missing staple | 1023 |
| failed minimum | 1024 |
| failed maximum | 896 |
| nutrient-valid | 1152 |
| non-dominated (audit) | 7 |
| Essential / Balanced / Optimal valid | 1152 / 896 / 1152 |
| displayed | 20 / 20 / 20 |

`dominance_is_display_filter` = false.

---

# 27. Provenance strategy

| Claim | Allowed wording |
|---|---|
| Baseline nutrients | “Meets modeled baseline nutrient constraints.” Secondary AAFCO-style summary. |
| Demo products | “Product nutrient data in this demo are synthetic.” |
| Breed `*` | Demo breed-care model; warehouse evidence not loaded |
| Complete diet | **Never** claim a guaranteed complete diet |

`llm_used` is always false on optimizer provenance.

---

# 20. Canonical result

`canonical_analysis.v1` is the single analysis envelope. Role projections read it. They do not regenerate packages.

---

# 21. Role projections

Customer, Groomer, Business, and Developer are **projections** of one canonical result. Bundle IDs are identical across roles. Switching roles in the workbench does not call the engine.

Customer/Groomer show product **names**. Developer may show `Name — SKU`. Business may show both.

---

# 22. API architecture

Canonical app: `app.api.main` (`PPIEWellnessAgent`). Shim: `app.main:app`.

HTTP API version (`OpenAPI info.version`) is **v1**. Engine version remains `ALGORITHM_VERSION` (`2.1.0`). They are not the same.

Two analysis HTTP contracts (not the same response):

| | Raw analysis | Workbench |
|---|---|---|
| Method / path | `POST /api/v1/analyze` | `POST /api/v1/presentation/workbench` |
| Purpose | Raw `generate_reproducible_report` JSON | One analysis + four role projections |
| Adapter | `profile_from_analyze_body` (legacy silent defaults) | `profile_from_workbench_body` (fail-closed) |
| Auth | `API_KEYS` / `x-api-key` when set | not behind that gate (hardening gap) |
| Groomer session merge | yes (`observations_for_legacy_analyze`: unique saved dog or unnamed cache) | **no** |

There are no `/api/v1/analyze/{role}` routes. Ω12 is not wired to HTTP. See [omega16-api-contract-design.md](omega16-api-contract-design.md).

Primary:

GET /
GET /demo
GET /classic
GET /business
GET /developer
GET /debug/calculation
GET /health
POST /api/v1/analyze
POST /api/v1/presentation/workbench
POST /api/v1/presentation/three-surfaces
POST /api/v1/ai/explain
POST /api/v1/dogs
GET /api/v1/presentation/catalog
GET /api/v1/catalog

| Method | Path |
|---|---|
| GET | `/health` |
| GET | `/` and `/demo` (canonical workbench) |
| GET | `/classic`, `/business`, `/developer` (same workbench; role aliases) |
| GET | `/debug/calculation` (Clinical Execution Explorer, not a product UI) |
| POST | `/api/v1/analyze` |
| POST | `/api/v1/presentation/workbench` |
| POST | `/api/v1/presentation/three-surfaces` |
| POST | `/api/v1/ai/explain` (optional explanation; does not run the engine) |
| POST | `/api/v1/dogs` (persistent dog identity; does not run the engine) |
| GET | `/api/v1/presentation/catalog`, `/api/v1/catalog` |

Also served: clinical-report, PPIE validation/debug, science graph, authoring, store, research, groomer session endpoints. Workbench assets under `/workbench.js`, `/workbench.css`, `/theme.css`. Archived reference UIs under `/archive/frontend/`.

Local launcher: `py -3 scripts/run_dev.py` (sets `WAGTOPIA_DEMO_MODE=true` by default).

Agent-facing typed contracts (not HTTP, not a tool server): `app/contracts/agent/`. See [omega11-agent-data-contract-report.md](omega11-agent-data-contract-report.md). Existing `/api/v1` routes are unchanged.

---

# 23. Frontend architecture

Unified workbench (`waggy-frontend/`) is the **only active product frontend**. Customer, Groomer, Business, and Developer are tabs / intake variations of one page. `GET /classic`, `GET /business`, and `GET /developer` load that same workbench (`?role=` or the path selects the tab). The Clinical Execution Explorer remains `GET /debug/calculation`. Old classic/business HTML is archived in `legacy/archive/frontend/` and is not linked from the workbench chrome.

The frontend talks to Waggy only through HTTP (`src/api/client.js`). It does not import Python, warehouse CSVs, `scientific_care`, or optimizer modules. Copy `waggy-frontend/` into another workspace to host the UI separately. Set `WAGGY_API_BASE_URL` (or `?api=`) when the UI is not same-origin with the API.

Frontend **must not**:

- enumerate subsets
- calculate nutrients or prices
- choose SKUs
- hardcode `SF001`, `4095`, or package membership

It **may**: show/hide panels, compare selected `bundle_id`s using backend fields, POST a new analysis when intake (including budget or groomer observations) changes.

Customer: dog header, WHY BALANCED CARE briefing, compact option cards, Why this bundle, Nutrition Facts, Compare, Choose, Health Analysis (`#health-analysis`).

Groomer observations live on the **request** (`role_context`). Changing them requires a new analysis because they are inputs, not a view filter.

---

# 28. Future AI boundary

LLM must never:

- choose SKUs or package membership
- override nutrient min/max
- invent scientific requirements
- alter prices
- bypass maxima because care coverage improved

A future explanation agent may **narrate** deterministic results. It may not modify them.

Ω17 implements that narrator as an optional layer: `POST /api/v1/ai/explain` plus
`app/ai/` (Waggy-owned policy, ExplanationContext, ModelProvider, FakeProvider,
prototype Gemini adapter). Analysis still does not call an LLM. See
[omega17-ai-architecture.md](omega17-ai-architecture.md).

Ω11 defined the typed domain language (`CanonicalDogInput`, evidence/fact/inference, health/nutrition/bundle slices, provenance, versions, typed errors). It did **not** implement Gemini, MCP, a tool server, or chat UI. Warehouse `NEEDS_VALIDATION` / `MISSING_PROVENANCE` research is a later scientific phase, not this contract layer.

Ω17.4 adds an **internal** allowlisted gateway (`app/tools/`, `POST /api/v1/ai/tools/invoke`). That is not MCP and not a second recommender. See §40.

---

# 26. Testing strategy

Run (Windows):

```bash
py -3 -m pytest tests/normalization tests/architecture/test_omega12_boundaries.py -q
py -3 -m pytest tests/optimization -q
py -3 -m pytest tests/interface -q
py -3 -m pytest tests/mathematics -q
py -3 -m pytest tests/formulas -q
py -3 -m pytest tests/math_debugger -q
py -3 -m pytest tests/science_graph -q
py -3 -m pytest tests/warehouse_qa -q
py -3 -m pytest tests/tools tests/architecture/test_omega17_4_tool_isolation.py tests/api/test_omega17_4_tools.py -q
```

Optimizer/interface tests prove: 4095 evaluated for N=12; min/max are hard; daily amounts derived from DM; Essential ≠ breed-optimized; budget ceiling Essential/Balanced not Optimal; surfaces share bundle IDs; frontend has no SKU/`4095` hardcoding.

Mathematics tests cover `repository/mathematics` MAT-1001…MAT-1008. That stack is **not** the package composer.

After documentation consolidation, treat counts from the latest `pytest` run as source of truth (do not copy stale Ω-phase pass counts).

Latest full run (2026-09-02): **325 passed, 33 skipped, 0 failed**.

Canonical current-architecture suites (`tests/optimization`, `tests/interface`, `tests/mathematics`, `tests/formulas`, `tests/math_debugger`, `tests/science_graph`, `tests/warehouse_qa`, `tests/architecture`, `tests/pipeline`, `tests/test_package_optimizer.py`): **266 passed, 2 skipped**.

Older `tests/test_*.py` files that assert the historical DataPlatform CSV projection (`breeds` table, warehouse-backed `healthInsights`) are skipped while that projection is empty. They are not PACKAGE_OPTIMIZER_V2_1 regressions.

---

# 25. Scientific limitations

- Health Analysis reads intern warehouse biology; it does **not** invent prevalence or citations.
- Phenotype `breed_traits.csv` rows are **MISSING_PROVENANCE** — listed as trait associations, never converted into a combined estimated %.
- Mixed-breed, life-stage, and size-risk CSVs remain **NEEDS_VALIDATION**.
- Demo catalog + densities = **synthetic commercial math**, not scientific evidence.
- Breed-care `*` = warehouse zinc mapping when a cited zinc ingredient row exists; not demo synthetic joint/skin.
- Requirement source = **secondary** AAFCO-style summary, not primary AAFCO.
- Senior-specific numeric minima = **NOT_AVAILABLE**.
- Water and carbohydrate/fiber = **NOT_MODELED**.
- No clinical diagnosis.
- Mixed-breed warehouse mathematics currently resolves breed using `profile.breeds[0]` in `WarehouseBackedDogResolver.resolve` / `repository/pipeline/biological_runtime.py`. Additional breeds are ignored in that MAT path. Package Essential minima still do not use breed. Health Analysis *does* load observed conditions for every resolved breed name.
- MAT-1005 uncertainty bounds are **not a formal statistical confidence interval**.
- MAT-1004: **agreement is not confidence**.
- MAT-1003 Bayesian-style blend has no explicit likelihood; **METHODOLOGICAL_REDESIGN_REQUIRED: true**.
- Railway/production deployment is not asserted by this specification.
- Older `tests/test_*.py` cases that require a populated DataPlatform `breeds` table are skipped while that projection is empty (they are not package-optimizer regressions).

### Warehouse validation blockers (unchanged; not “fixed” by documentation)

VALIDATION_STATUS: FAIL  
ERROR_COUNT: 8  
RESOLUTION_POLICY: separate controlled warehouse correction task

| dataset | row | foreign_key | referenced_id | expected_dataset | problem | recommended_correction |
|---|---|---|---|---|---|---|
| mechanisms.condition_mechanisms | line 2 | condition_id | COND_HIP_DYSPLASIA | biology.conditions.condition_id | Legacy condition_id not present in canonical conditions IDs. | Map legacy condition IDs to canonical IDs (e.g., Hip Dysplasia canonical condition_id) or add controlled alias mapping table. |
| mechanisms.condition_mechanisms | line 6 | condition_id | COND_ATOPIC_DERMATITIS | biology.conditions.condition_id | Legacy condition_id not present in canonical conditions IDs. | Map legacy condition IDs to canonical IDs or add explicit alias normalization in warehouse curation. |
| mechanisms.condition_mechanisms | line 9 | condition_id | COND_OBESITY | biology.conditions.condition_id | Legacy condition_id not present in canonical conditions IDs. | Map legacy condition IDs to canonical IDs or re-key rows using canonical IDs. |
| mechanisms.food_mechanisms | line 2 | ingredient_id | ING_EPA | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 3 | ingredient_id | ING_DHA | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 4 | ingredient_id | ING_COLLAGEN | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 5 | ingredient_id | ING_VITAMIN_C | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 6 | ingredient_id | ING_ZINC | nutrition.ingredients.ingredient_id | Ingredient ID namespace mismatch (`ING_ZINC` vs canonical `ING_723DBC80`). | Introduce deterministic ID mapping or re-key to canonical ingredient IDs in curation migration. |

---

# 24. Demo data boundary

**CURRENT / DONE:** exhaustive PACKAGE_OPTIMIZER_V2_1; nutrient ledger; hard min/max; many options per tier; unified workbench; one analysis / four projections.

Warehouse-backed MAT stack (not package membership): MAT-1001 MAT-1002 MAT-1003 MAT-1004 MAT-1005 MAT-1006 MAT-1007 MAT-1008. Inventories remain in `docs/mathematics/*.csv`.

**NEXT (scientific warehouse work, after Ω11 contracts):** intern research on 248 `NEEDS_VALIDATION` + 471 `MISSING_PROVENANCE` flags. Do not invent values to clear them. Ω11 itself is the agent data-contract layer (`app/contracts/agent/`), not a warehouse-cleanup phase.

**FUTURE:** primary AAFCO in warehouse; non-synthetic product densities; optional explanation LLM that cannot change membership; warehouse FK repair (the 8 blockers above).

Do not treat old Ω-phase checklists as current status.

---

# 29. Health Analysis

Customer Health Analysis is projected from `careModel` produced by `app/data/scientific_care.py` during `PACKAGE_OPTIMIZER_V2_1`.

For every resolved breed name:

1. Load `warehouse/biology/observed_breed_conditions.csv` (cited observed prevalence).
2. Load `warehouse/biology/breed_traits.csv` phenotype rows. Many are `MISSING_PROVENANCE`.
3. Load `warehouse/biology/trait_condition_associations.csv` and list matching associations separately. Do not add those rows into a combined estimated %.
4. Load `warehouse/prevention/condition_ingredients.csv` for preventative nutrient/ingredient targets.
5. Surface `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` as flagged, not as validated science.

Copy rules:

- Conditions are preventative considerations, not diagnoses.
- Observed prevalence is shown per breed when a warehouse row has a numeric prevalence and a citation.
- Estimated prevalence is `NOT_AVAILABLE` unless a warehouse-supported estimator exists. Intern trait associations are listed, not fabricated into a percentage.
- Do not claim a supplement reduces disease chance unless a warehouse row says so.

Structured pathway records (`care_pathway_records`) travel with Balanced / Optimal packages so the optimizer and “Why this bundle?” share the same evidence.

---

# 30. Nutrition Facts modal

Package cards do **not** contain the nutrient table.

Cards show: rank, product **names**, monthly price, minimum/maximum pass counts, care-pathway chips, **Why this bundle?** and **View nutrition**.

`View nutrition` opens `#nutrition-modal` in `waggy-frontend/index.html`:

- centered overlay, darkened + blurred backdrop
- X, Escape, and backdrop click close the modal
- internally scrollable table: Nutrient, Per Package, Required Daily, Maximum Daily, Coverage, Status
- `*` only when `breed_recommended` is true for that nutrient
- product names from `product_master` / catalog overlay, never customer-facing `SF002` / `TR007`

Developer view may still show SKUs.

---

# 31. Recovery history

Intern research was recovered from git (`a122a83`, snapshot `d6384a0`) into canonical warehouse CSVs. Read-only originals: `warehouse/recovery_original/`.

Do not run another migration unless a concrete validation failure requires it. Do not rewrite git history. Do not delete recovery blobs.

Historical recovery reports live in `docs/archive/`.

---

# 32. Current data inventory

Canonical warehouse (scientific / commercial facts):

| Path | Role |
|---|---|
| `warehouse/biology/breeds.csv` | Breed identity |
| `warehouse/biology/breed_traits.csv` | Phenotype traits (many `MISSING_PROVENANCE`) |
| `warehouse/biology/observed_breed_conditions.csv` | Cited breed–condition prevalence |
| `warehouse/biology/trait_condition_associations.csv` | Cited trait–condition links |
| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | Mixed-breed rows requiring validation |
| `warehouse/prevention/condition_ingredients.csv` | Condition → ingredient / nutrient |
| `warehouse/reference/papers.csv` | Paper identity + links |
| `warehouse/commercial/product_master.csv` | Product identity / names |
| `warehouse/commercial/product_functions_NEEDS_VALIDATION.csv` | Functions requiring validation |
| `warehouse/commercial/product_feeding_guide.csv` | Feeding records |

Demo overlay (`WAGTOPIA_DEMO_MODE`): `app/data/demo_catalog.py` + `app/data/demo_scientific_dataset.py` — commercial densities only.

Retired: `app/data/demo_breed_care.py` is not on the Health Analysis path.

---

# 33. NEEDS_VALIDATION and MISSING_PROVENANCE

These flags are **first-class outputs**, not defects to invent away.

- `NEEDS_VALIDATION` — intern or recovered row is present but not accepted as validated science. Surface it. Do not treat it as confirmed prevalence or a product claim.
- `MISSING_PROVENANCE` — identity or phenotype exists without a citable study. Do not fill quotes, years, or paper links.
- `CONFLICT_REQUIRES_VALIDATION` — none at recovery close.

A later scientific phase should tackle remaining validation and provenance flags. Ω10 surfaces them. Ω11 does not resolve them; it only preserves their status tokens in typed contracts.

---

# 34. Agent data contracts (Ω11)

Typed agent-facing domain models live in `app/contracts/agent/`. They transport data; they do not reason, optimize, or write warehouse facts.

Authoritative reports: [omega11-agent-data-contract-design.md](omega11-agent-data-contract-design.md), [omega11-agent-contract-inventory.md](omega11-agent-contract-inventory.md), [omega11-agent-data-contract-report.md](omega11-agent-data-contract-report.md).

Existing browser APIs and `DogProfileInput` are unchanged. Future tools (`analyze_health`, `calculate_nutrition`, `optimize_bundles`, `generate_report`) are named in the registry only — not executed in Ω11.

---

# 35. Normalization + entity mapping (Ω12)

Ω12 is a fail-closed identity layer. It is **not** on the HTTP / `generate_reproducible_report` path.

```
RAW REPRESENTATION
        ↓
NORMALIZATION (trim / case-fold / whitespace)
        ↓
ENTITY RESOLUTION (approved aliases + canonical names/IDs)
        ↓
CANONICAL DATA (warehouse identity)
        ↓
ENGINE (unchanged; still uses existing breed-name aliases internally)
```

Mapping does **not** equal scientific inference. `"HD"` → `COND_653473C1` (Hip Dysplasia) is identity. It does not produce prevalence, diagnosis, product selection, or a package.

Statuses: `RESOLVED`, `AMBIGUOUS`, `UNRESOLVED`, plus `MIXED` for structured mixed-breed input (`Labrador x Golden`) that is **not** a new canonical breed. Ambiguous tokens such as `retriever` do not pick Labrador.

Implementation: `app/normalization/`, alias CSVs in `warehouse/mapping/` (not scientific fact tables). Mapping config version `1.0.0` is separate from `ALGORITHM_VERSION` (`2.1.0`). Reports: [omega12-normalization-entity-mapping-design.md](omega12-normalization-entity-mapping-design.md), [omega12-normalization-entity-mapping-report.md](omega12-normalization-entity-mapping-report.md).

---

# 36. Canonical API contract (Ω16)

Ω16 makes the existing HTTP boundary explicit. It does not add a second engine, optimizer, Gemini, MCP, Ω12 wiring, or Ω13.

```
ROLE INPUT → payload_adapter → DogProfileInput → generate_reproducible_report → existing projectors → ONE frontend
```

`POST /api/v1/analyze` remains the raw engine contract (legacy defaults + session merge).

`POST /api/v1/presentation/workbench` is the fail-closed application contract: missing age/weight/breed/activity/environment is `MISSING_REQUIRED_INPUT` (HTTP 400 `{error:{...}}`). Empty name is allowed. `as_of_date` is an optional birthday reference date. With `birthday` + `as_of_date`, age is deterministic via `age_years_from_birthday`. Without `as_of_date`, birthday age still uses `datetime.now`. Explicit `age_years` wins over birthday.

Public/stable: request DTOs, error DTO, workbench envelope, documented extraction paths. Nested `canonical.analyze` / debug / timing are **internal**. See [omega16-api-contract-design.md](omega16-api-contract-design.md) and [omega16.1-completion-report.md](omega16.1-completion-report.md).

---

# 37. Persistent dog state (Ω17.1)

This layer stores dog-specific state and interaction history. It does not become a scientific knowledge base.

User preferences and groomer observations are not scientific facts.

AI explanations cannot directly modify canonical scientific analysis or package composition.

```
Persistent dog
  → fail-closed projection
  → DogProfileInput
  → Waggy Engine
  → analysis_signature + digest
```

SQLite path: `WAGGY_STATE_PATH` (default `var/waggy_state.sqlite`). Independent of Gemini. GET dog/events does not run the engine. See [omega17.1-dog-state.md](omega17.1-dog-state.md).

---

# 38. Preference-aware recomputation (Ω17.2)

Validated user preferences can trigger a **new** deterministic analysis. They do not mutate warehouse facts, nutrient min/max, or a completed analysis row.

```
POST /api/v1/dogs/{dog_id}/recompute
        ↓
validate excluded_ingredients / monthly_budget
        ↓
persist USER_PREFERENCE (existing SQLite)
        ↓
catalog eligibility (app/agent/catalog_eligibility.py)
        ↓
PACKAGE_OPTIMIZER_V2_1 / run_package_search  (unchanged math)
        ↓
new analysis_signature + history row
```

Budget still uses `DogProfileInput.monthly_budget` (existing optimizer ceiling on essential/balanced). Ingredient exclusions never become `DogProfileInput` fields. `POST /api/v1/ai/explain` still does not run the engine.

See [omega17.2-completion-report.md](omega17.2-completion-report.md).

---

# 39. Recalculation provenance (Ω17.3)

"Why did my recommendation change?" is answered from deterministic structured data, not model prose.

```
previous analysis digest
        +
new analysis digest
        +
preference changes / eligibility
        ↓
waggy_recalculation_explanation.v1
        ↓
POST /recompute.explanation
GET  /analyses/compare
POST /ai/explain  (echo only; cannot invent causes)
```

`result_digest` keeps `package_product_ids` / `finding_titles` / `analysis_signature` and adds `recommendation_snapshot` plus `recalculation_explanation`. Compare does not run the engine. The LLM, when used, may only verbalize `summary_facts`.

See [omega17.3-completion-report.md](omega17.3-completion-report.md).

---

# 40. Bounded tool gateway (Ω17.4)

AI may interpret intent and call an allowlisted Waggy capability. It may not become scientific authority, recommender, optimizer, or warehouse editor.

```
AI
        ↓
WaggyToolGateway (allowlist, schema, role, dog scope)
        ↓
stored dog / stored analysis digest / injected catalog / preference validator
        ↓
waggy_tool_result.v1
```

Registered tools: `get_dog_profile`, `analyze_health`, `calculate_nutrition`, `get_products`, `get_package_options`, `get_recalculation_explanation`, `compare_analyses`, `propose_preference`. There is no `set_preferences` tool. Preference mutation remains an explicit application-authorized operation.

HTTP: `POST /api/v1/ai/tools/invoke`. Not MCP.

Health/nutrition/package tools read stored analysis **digests**, not a live engine run. Missing evidence is `NOT_AVAILABLE`. `compare_analyses` has `engine_ran: false`. Prototype auth is `owner_id` / `authorized_dog_ids`; production auth is deferred.

Ω11 `FUTURE_TOOL_REGISTRY` remains non-executing. Portable UI isolation is a separate report: [omega17.4-fe-completion-report.md](omega17.4-fe-completion-report.md).

See [omega17.4-completion-report.md](omega17.4-completion-report.md).
