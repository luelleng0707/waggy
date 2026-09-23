# Waggy

Waggy (also called Wagtopia in env vars, routes, and some files) is an **evidence-backed dog-care decision system**. It separates:

1. **scientific warehouse facts** (CSV, with provenance and status)
2. **deterministic reasoning** (one Python engine)
3. **commercial catalog / demo overlay** (search space, not science)
4. **role-specific UI projections** of one analysis

It is **not** a veterinary diagnostic system, not a guaranteed disease-prevention product, and not an LLM that “knows” veterinary science.

**Authoritative internals:** [docs/WAGGY_SYSTEM.md](docs/WAGGY_SYSTEM.md)

---

# 1. What Waggy Does

Conceptual flow (what the runtime actually does today):

```
Dog profile + optional observations
        ↓
DataRepository (warehouse CSVs; optional demo catalog overlay)
        ↓
scientific_care.resolve_care_model   → careModel (preventative findings)
        ↓
requirement profile                  → nutrient min/max (density basis)
        ↓
PACKAGE_OPTIMIZER_V2_1
  run_package_search                 → 2^N−1 subsets when N ≤ 14
        ↓
response_assembler                   → one analyze dict
        ↓
presentation adapter                 → Customer / Groomer / Business / Developer
```

The LLM is **not** the scientific authority. There is **no** Gemini, MCP, or chatbot in this repository. `optimizerProvenance.llm_used` is `false`.

Ω12 (`app/normalization/`) maps raw strings to warehouse identity IDs. It is **not** in the diagram above and is **not** called by HTTP or the optimizer.

---

# 2. Core Design Principle

These are different layers. Do not collapse them.

| Layer | Meaning | Authority |
|---|---|---|
| **User input** | Stated breed, age, weight, budget | Customer / caller |
| **Observation** | Individual-dog note (e.g. dense coat) | Groomer / customer — **not** a warehouse fact |
| **Scientific fact** | Structured warehouse relationship + status | Science / CSV |
| **Scientific evidence** | Paper, quote, link, year on the **fact/relationship** | Science / CSV |
| **Inference** | Engine output from facts + this dog | Deterministic engine |
| **Recommendation** | Ranked packages / products from the optimizer | `PACKAGE_OPTIMIZER_V2_1` |
| **Presentation** | Role copy, HTML, Nutrition Facts modal | UI adapter |
| **LLM explanation** | **NOT IMPLEMENTED** | Must never create facts |

Intended data path:

```
RAW DATA
 → NORMALIZATION          (PARTIAL: payload aliases, breed name resolve)
 → ENTITY RESOLUTION      (PARTIAL: breed aliases in repository)
 → EVIDENCE VALIDATION    (PARTIAL: status flags exist; many rows still NEEDS_VALIDATION / MISSING_PROVENANCE / migrated)
 → CANONICAL WAREHOUSE    (CURRENT: warehouse/biology, prevention, commercial, reference)
 → DETERMINISTIC REASONING (CURRENT: PPIEWellnessAgent)
 → STRUCTURED RESULT      (CURRENT: analyze dict)
 → AI / UI PRESENTATION   (CURRENT: four UI projections; AI chat PLANNED)
```

---

# 3. Architecture

```
                    ┌───────────────────────────┐
                    │ Papers / intern recovery  │
                    │ (historical intake)       │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ Authoring staging         │
                    │ (drafts; not the engine)  │
                    └─────────────┬─────────────┘
                                  │  (manual / science team; not agent tools)
                                  ▼
                    ┌───────────────────────────┐
                    │ Canonical warehouse CSVs  │
                    │ biology / prevention /    │
                    │ commercial / papers       │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ DataRepository            │
                    │ + scientific_care         │
                    │ + requirement profile     │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ PPIEWellnessAgent         │
                    │ generate_reproducible_    │
                    │ report                    │
                    └─────────────┬─────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
             careModel     requirementProfile   catalog candidates
                 │                │                │
                 └────────────────┼────────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │ PACKAGE_OPTIMIZER_V2_1    │
                    │ run_package_search        │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ One analyze dict          │
                    │ + optimizerProvenance     │
                    └─────────────┬─────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
         Customer             Groomer              Business
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                      Developer / OpenAPI / debug
```

Engine version: `ALGORITHM_VERSION = 2.1.0` (`app/agent/version.py`). Engine name: `PPIE`.

---

# 4. Single Source of Truth

```
ONE INPUT → ONE ANALYSIS → FOUR PROJECTIONS
```

- Sole composer of care packages: `PACKAGE_OPTIMIZER_V2_1` (`app/agent/package_optimizer.py` → `app/agent/package_search.py`).
- `POST /api/v1/presentation/workbench` runs `generate_reproducible_report` **once**, then `build_workbench_presentations`.
- Role switch in the workbench must **not** rerun the engine.
- Do not add a customer engine, a groomer engine, or a frontend optimizer.

**CURRENT:** workbench, three-surfaces, analyze, evaluate, and clinical-report all call the same `PPIEWellnessAgent.generate_reproducible_report`.

---

# 5. Scientific Warehouse

Active scientific/commercial facts for Health Analysis and catalog identity:

| Path | Role |
|---|---|
| `warehouse/biology/breeds.csv` | Breed identity |
| `warehouse/biology/conditions.csv` | Condition identity |
| `warehouse/biology/observed_breed_conditions.csv` | Breed → condition **observed prevalence** (fact + evidence columns) |
| `warehouse/biology/breed_traits.csv` | Breed phenotype (many `MISSING_PROVENANCE`) |
| `warehouse/biology/trait_condition_associations.csv` | Trait → condition associations (listed separately; not summed into a fake %) |
| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | Mixed-breed interaction rows — **not** validated science |
| `warehouse/biology/life_stage_health_NEEDS_VALIDATION.csv` | Flagged |
| `warehouse/biology/size_risk_NEEDS_VALIDATION.csv` | Flagged |
| `warehouse/prevention/condition_ingredients.csv` | Condition → ingredient/nutrient preventative mapping |
| `warehouse/prevention/condition_activities.csv` | Condition → activity |
| `warehouse/reference/papers.csv` | Paper catalog (many `NEEDS_VALIDATION`) |
| `warehouse/commercial/product_master.csv` | Product identity (`status` often `NEEDS_VALIDATION`) |

Evidence belongs on **relationship/fact rows**, not as “one paper glued to a condition entity.” A condition can have multiple papers via multiple facts.

Typical fact columns (observed breed conditions):  
`fact_id`, `breed_id`, `breed_name`, `condition_id`, `condition_name`, `measure_type`, `value_number`, `unit`, `scientific_quote`, `paper_name`, `paper_link`, `publication_year`, `study_type`, `species`, `status`.

**Not interchangeable:**

- condition ≠ condition evidence
- breed ≠ breed–condition prevalence
- trait ≠ trait–condition association
- product ≠ product scientific evidence

`warehouse/recovery_original/` is **read-only historical recovery**. It is not the active runtime warehouse.

`warehouse/science/` and `warehouse/manifest.yaml` (`schema: science_only`) are used by older MAT / science-graph loaders. They are **not** the Health Analysis path (`scientific_care` reads `warehouse/biology` + `warehouse/prevention`).

---

# 6. Evidence and Provenance

Statuses you will actually see:

| Token | Meaning |
|---|---|
| `WAREHOUSE_EVIDENCE` | Engine found warehouse rows for this care model |
| `NOT_AVAILABLE` / `NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE` | No usable approved value — **valid result**, not zero |
| `NEEDS_VALIDATION` / `needs_validation` | Present, not accepted as validated science |
| `MISSING_PROVENANCE` | Identity/phenotype without citation |
| `migrated` | Recovered intern row — **not** `APPROVED` |
| `NOT_MODELED` | Named nutrient category with no numeric min/max |
| `NOT_APPLICABLE` | e.g. senior-specific minima when the dog is not senior |

There is **no** warehouse status `APPROVED` on current Health Analysis rows. Ω11 reserves `APPROVED` for a future validated-for-use state. Do not map `migrated` → `APPROVED`.

Unsupported prevalence must **not** be invented. Trait associations are listed separately. They are **not** combined into an estimated mixed-breed %.

HTTP provenance headers (on API responses): `X-PPIE-Algorithm-Version`, `X-PPIE-Data-Version`, `X-PPIE-Csv-Hash`.

---

# 7. Scientific Reasoning

Health Analysis (`app/data/scientific_care.py` `resolve_care_model`), per resolved breed name:

1. Observed prevalence from `observed_breed_conditions.csv` when a numeric value and citation exist.
2. Phenotype from `breed_traits.csv` (often `MISSING_PROVENANCE`).
3. Matching `trait_condition_associations.csv` rows listed **separately**.
4. Preventative targets from `condition_ingredients.csv`.
5. Mixed-breed CSV surfaced as **flagged**, not as validated prevalence.

Findings are **preventative considerations**, not diagnoses. `diagnosis_claim` is false.

If the warehouse has no observed rows for the dog’s breeds: **NOT_AVAILABLE**. The retired module `app/data/demo_breed_care.py` is **not** on this path (it raises if called).

---

# 8. Mixed-Breed Reasoning

Health Analysis loads observed conditions for **every resolved breed name** on the profile (primary and secondary).

It does **not** fabricate a combined mixed-breed disease prevalence.

`warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` remains flagged.

A separate MAT pipeline (`repository/pipeline`) currently resolves breed using `profile.breeds[0]` only. That stack is **not** the package composer. See [docs/WAGGY_SYSTEM.md](docs/WAGGY_SYSTEM.md) §25.

No evidence → `NOT_AVAILABLE`. Not `0`. Not an average.

---

# 9. Deterministic Package Optimization

Algorithm id: `PACKAGE_OPTIMIZER_V2_1`.

For candidate count `N ≤ 14` (`EXHAUSTIVE_MAX_N`):

```
2^N − 1 non-empty subsets
  → nutrient calculation (dry-matter ledger)
  → hard minimum filter
  → hard maximum filter
  → staple / structural eligibility
  → care-pathway scoring (Balanced / Optimal)
  → budget (hard ceiling on Essential and Balanced; Optimal ignores customer budget)
  → dominance is an audit statistic (not the display gate)
  → rank per tier
  → display up to PACKAGE_DISPLAY_LIMIT (20) per tier
```

If `N > 14`, search is `BOUNDED_ENUMERATION_MAX_SIZE` (not full power set).

Tiers (from `TIER_SEMANTICS` in `package_search.py`):

| Tier | Nutritional validity | Breed-care eligibility | Budget ceiling |
|---|---|---|---|
| Essential | Required | No | Yes, if supplied |
| Balanced | Required | Yes (needs some care coverage when pathways exist) | Yes, if supplied |
| Optimal | Required | Ranking uses care; eligibility does not require it | **No** |

Invalid bundles are **rejected**, not ranked. `llm_used: false`.

Without `WAGTOPIA_DEMO_MODE`, product dry-matter densities are generally **unavailable**; the search records `insufficient_product_nutrient_data` rather than inventing science.

---

# 10. Nutrition Model

- Basis: **dry-matter density** (`percent_dry_matter` / mg per kg DM), not invented grams/day feeding amounts.
- Minima/maxima: `app/data/scientific_requirements.py` — **secondary** AAFCO-style summary (PetMD-style project source). **Not** a warehouse CSV. **Not** a primary AAFCO table.
- Senior-specific numeric minima: **NOT_AVAILABLE** (adult figures reused with an explicit note).
- Carbohydrate, fiber, water: **NOT_MODELED**.
- Demo product densities: `app/data/demo_scientific_dataset.py` — **synthetic commercial/demo input, not scientific evidence**.
- Nutrition Facts UI: modal `#nutrition-modal` on the workbench (not inline on cards).

Do not present density minima as universal grams/day.

---

# 11. Product Matching

`PRODUCT_MATCH_V2_1` can emit `productRecommendations`. In the current demo/workbench path that list is often **empty**. Packages still come from the **optimizer over the catalog**, not from the matcher.

Empty matcher output is a commercial-input limitation, not a medical engine. There is **no** public `match_products` / `evaluate_product` tool.

Ω10.2 / Ω11: product matching stays **internal / weak** until a warehouse-backed matcher exists.

---

# 12. Business Configuration

**CURRENT:** catalog overlay via `WAGTOPIA_DEMO_MODE`; optional `monthly_budget` on the dog input; product `product_status` on warehouse rows (e.g. `active` / `sold_out`).

**PLANNED (typed in Ω11, not applied by the optimizer today):** `BusinessConfiguration` — allowed brands/products, advertising vs in-store vs online vs fulfillment lists.

Business policy may change the **candidate catalog**. It must not change prevalence, nutrient science, or evidence.

Advertising ≠ inventory ≠ scientific approval ≠ medical efficacy.

No live sales/revenue pipeline is implemented. Do not treat purchases as health outcomes.

---

# 13. Roles and Data Boundaries

| Actor | Input today | Can modify today | Receives |
|---|---|---|---|
| Customer | Dog profile, optional budget; optional saved dog | Request body; `POST /api/v1/dogs` (prototype, no production auth) | Customer projection |
| Groomer | Observations on the request; durable `GROOMER_OBSERVATION` when a dog is identified | `POST /api/v1/groomer/update` writes canonical dog events when `dog_id` or a unique name matches; unnamed pets stay a transient cache | Groomer projection |
| Business | Optional `WAGTOPIA_BUSINESS_ACCESS_KEY` | Commercial pages/API when key set | Business projection; **no** real analytics warehouse |
| Science team | Authoring drafts | Staging `POST /api/v1/authoring/evidence` + materialize (**off** the agent tool surface) | Authoring/research routes |
| Developer | Optional `WAGTOPIA_DEVELOPER_ACCESS_KEY`, `PPIE_DEBUG` | Code / debug console | Developer projection, traces, versions |
| AI explanation | Optional `POST /api/v1/ai/explain` after analysis; optional `POST /api/v1/ai/tools/invoke` | Structured preference **candidates** via `propose_preference` only; cannot persist preferences, write warehouse facts, or edit packages. Recalculation provenance is copied from the system contract when supplied | Explanation / Q&A; `recalculation` is system-owned |

Full RBAC, customer accounts, and permissioned tool calls are **PLANNED** (Ω11 `ActorRole` / `AgentContext` are contracts only).

Privacy architecture is a design requirement and is not yet a production security guarantee.

---

# 14. Groomer Observation Model

Observations are **observations**, not scientific facts and not diagnoses.

Example: `"dense coat"` may later map to a warehouse trait **if** that mapping exists. The observation itself does not become a disease or a prevalence.

Engine input today: `DogProfileInput.observed_conditions: list[str]`.

Ω11 typed `Observation` exists in `app/contracts/agent/observations.py` and is **not** wired to HTTP.

Hidden groomer merge on **analyze / clinical-report** is an **application** behavior (`observations_for_legacy_analyze`). The canonical workbench contract does **not** merge groomer cache or saved-dog observations unless they are on the request. It is a determinism limitation on those legacy paths. Canonical tool contracts must not depend on it.

---

# 15. AI Chatbot Architecture

Chat UI / live Gemini orchestration is **NOT IMPLEMENTED**. The internal tool path is **CURRENT** (Ω17.4):

```
AI Chatbot / Gemini
        ↓ intent
Authorized tool selection (allowlisted names only)
        ↓
Permission / input validation (WaggyToolGateway)
        ↓
Deterministic Waggy capability (stored digest / catalog / validator)
        ↓
Canonical bounded result (waggy_tool_result.v1)
        ↓
AI explanation only
```

The LLM **must not**: invent facts or prevalence; invent product claims; choose products; override min/max; write warehouse rows; silently edit the dog; answer from general knowledge when the user asked for Waggy-approved evidence.

---

# 16. Evidence-Bounded Chat

**PARTIAL.** Internal tools exist (`POST /api/v1/ai/tools/invoke`). There is still no chat dock that selects tools. MCP / external tool server is **NOT IMPLEMENTED**.

Pattern: question → authorized tool → bounded structured data → “I don’t have approved Waggy evidence for that” when `NOT_AVAILABLE`.

Do not claim a chatbot UI exists.

---

# 17. Scientific Traceability

Designed chain (partially present in analyze / developer funnel):

```
Finding (careModel.condition_records)
  → fact_id / paper_name / quote / link / year / status
  → preventative targets
  → optimizer care pathways on Balanced/Optimal
  → package options + filter_funnel + example_rejections
```

Developer UI can show funnel counts and rejection reasons from `optimizerProvenance`. That is how “why did this product not appear?” is answered — **not** by an LLM.

Live end-to-end provenance objects for a future agent envelope: Ω11 `ProvenanceRecord` (typed); assembly of a full chain from a live analyze run is **not** an external API yet.

---

# 18. AI Chat UI

**NOT IMPLEMENTED.** Workbench has Customer / Groomer / Business / Developer tabs. There is no chat dock.

---

# 19. Backend Mutation Through AI

**NOT IMPLEMENTED.** No `set_preferences`, `update_customer_preferences`, or `record_observation` tools.

`propose_preference` returns a validated candidate only. Preference mutation remains an explicit application-authorized operation (`POST /api/v1/dogs/{id}/preferences` or `/recompute`).

Authoring WRITE routes are science-team staging, not chatbot tools.

---

# 20. Tool Architecture

| Name | Status |
|---|---|
| `get_dog_profile` | **CURRENT** internal tool — stored dog fields; no engine |
| `analyze_health` | **CURRENT** internal tool — stored analysis digest slice |
| `calculate_nutrition` | **CURRENT** internal tool — stored nutrition snapshot slice |
| `get_products` | **CURRENT** internal tool — narrow catalog filters; no SQL |
| `get_package_options` | **CURRENT** internal tool — stored package digest; not a second optimizer |
| `get_recalculation_explanation` | **CURRENT** internal tool — `waggy_recalculation_explanation.v1` |
| `compare_analyses` | **CURRENT** internal tool — stored digest diff; `engine_ran: false` |
| `propose_preference` | **CURRENT** candidate only; does not persist |
| `optimize_bundles` / `generate_report` | Ω11 **PLANNED** registry names; not executable Ω17.4 tools |
| `evaluate_product` / `match_products` | **NOT** a public tool |
| Tool server / `POST /tools/call` / MCP | **NOT IMPLEMENTED** |
| `POST /api/v1/ai/tools/invoke` | **CURRENT** application adapter — not MCP |

Ω11 defines `app/contracts/agent/` and `FUTURE_TOOL_REGISTRY` (**no `execute`**). Ω17.4 executable tools are `app/tools/` (`WaggyToolGateway`).

An external MCP agent **cannot** call a tool server. Application HTTP may invoke the allowlisted gateway. Closest full-analysis HTTP is still `POST /api/v2/wellness/evaluate` (`DogProfileInput` → full analyze dict). That is not a tool.

See [docs/omega17.4-completion-report.md](docs/omega17.4-completion-report.md).

---

# 21. Canonical Tool Contracts

**Defined, not served.** See [docs/omega11-agent-data-contract-report.md](docs/omega11-agent-data-contract-report.md).

Intended dog input: name, breed(s), age, weight, sex, activity, environment, observations, optional `monthly_budget`.

`role_context` is **not** a scientific input. It is workbench presentation / extra observations on the HTTP body. Scientific math must stay role-neutral.

Ω11 `CanonicalDogInput` does **not** silent-default age=5 / weight=20. The **legacy** adapter `profile_from_analyze_body` **still does** (and birthday age uses `datetime.now()` unless workbench `as_of_date` is set). `profile_from_workbench_body` is fail-closed. Documented gap on the raw analyze path.

---

# 22. Data Lifecycle

```
RAW WORLD
 → intern recovery / papers          (historical: warehouse/recovery_original — READ-ONLY)
 → authoring drafts                  (staging)
 → scientific review                 (PARTIAL: flags, not an automated promotion pipeline)
 → canonical warehouse CSVs
 → DataRepository + engine
 → HTTP / workbench / internal tool gateway
 → MCP / external agents             (PLANNED)
```

The warehouse is **not** an ingestion dump. New papers must not blindly overwrite facts. Publication date alone does not authorize a row.

---

# 23. Handling Incoherent / Conflicting Data

States in use: `NEEDS_VALIDATION`, `MISSING_PROVENANCE`, `migrated`, `NOT_AVAILABLE`, `active` (identity tables).

`CONFLICT` / `DEPRECATED`: **not** first-class Health Analysis statuses today (recovery reported `CONFLICT_REQUIRES_VALIDATION` count 0 at close).

Ω12 maps `"HD"` → warehouse condition `COND_653473C1` (Hip Dysplasia). That is **normalization**, not inference. Do not treat mapping as science. The engine path does not yet consume Ω12.

Do not delete incomplete evidence. Do not silently promote flags to validated science.

Warehouse QA still reports **8 foreign-key blockers** on mechanism tables (legacy IDs). See [docs/WAGGY_SYSTEM.md](docs/WAGGY_SYSTEM.md) §25. `docs/validation_report.md` is generated by `scripts/validate_warehouse.py`.

---

# 24. Privacy Boundary

Customer-level analysis must not become business “health outcomes.” Aggregate business analytics are **PLANNED** and **not implemented**.

Optional keys: `API_KEYS` (`x-api-key` on some routes), `WAGTOPIA_BUSINESS_ACCESS_KEY`, `WAGTOPIA_DEVELOPER_ACCESS_KEY`. If unset, those gates do not apply. CORS is `*`. `POST /api/v1/groomer/update` writes `GROOMER_OBSERVATION` events when a dog can be identified; otherwise it uses a process cache for unnamed pets. Durable dog events use SQLite (`WAGGY_STATE_PATH`).

Privacy architecture is a design requirement and is not yet a production security guarantee.

---

# 25. Business Analytics

**NOT IMPLEMENTED** as a metrics product. No package-acceptance, conversion, or revenue feed.

If sales data existed, purchase would still **not** be medical efficacy.

---

# 26. Frontend

Verified routes (`tests/interface/test_canonical_routes.py`):

| Path | What |
|---|---|
| `GET /` | Canonical workbench (`waggy-frontend/index.html`) |
| `GET /demo` | Same workbench |
| `GET /classic` | Same workbench (customer role) |
| `GET /business` | Same workbench (business role) |
| `GET /developer` | Same workbench (developer role) |
| `GET /debug/calculation` | Clinical Execution Explorer (internal debug) |
| `GET /archive/frontend/` | Archived classic/business UIs (reference only) |
| `GET /health` | Process health JSON (not a “health report”) |

Workbench: one page, role selector, Health → Nutrition → Products → Packages, Nutrition Facts **modal**, compare, optional Ask Waggy, optional saved-dog / care history. No competing classic/business/developer apps.

Portable copy: [`waggy-frontend/`](waggy-frontend/). It talks to Waggy only over HTTP. Isolation report: [docs/omega17.4-fe-completion-report.md](docs/omega17.4-fe-completion-report.md).

---

# 27. API

FastAPI app: `app.api.main:app` (shim `app.main:app`). OpenAPI: `GET /openapi.json` (verified). Swagger UI: FastAPI default `GET /docs` (generated; not a custom product page).

Engine version on analyze payload: `engine` / `version` (`2.1.0`). OpenAPI `info.version` is HTTP **v1**, not the engine. Headers: `X-PPIE-Algorithm-Version`, `X-PPIE-Data-Version`, `X-PPIE-Csv-Hash`.

### Analysis (application endpoints, not tools)

| Method | Path | Purpose | Input | Output | Status |
|---|---|---|---|---|---|
| POST | `/api/v1/analyze` | Raw engine JSON | Loose JSON (Node/Python aliases). Merges in-memory groomer session. API key if `API_KEYS` set | Analyze `dict` | CURRENT compatibility endpoint |
| POST | `/api/v2/wellness/evaluate` | Same engine, typed | `DogProfileInput` | Same analyze dict | CURRENT; no tool envelope |
| POST | `/api/v1/presentation/workbench` | One analysis + four projections | Fail-closed `WorkbenchRequest` + optional `role_context` + optional `dog_id` | `workbench_presentation.v1` | CURRENT application contract |
| POST | `/api/v1/dogs` | Persistent dog identity | Profile fields; no engine run | `waggy_dog_state.v1` | CURRENT prototype (SQLite; no production auth) |
| POST | `/api/v1/dogs/{dog_id}/analyze` | Project stored dog → existing engine | Fail-closed projection | Same workbench envelope | CURRENT |
| POST | `/api/v1/presentation/three-surfaces` | Customer/business/developer | Analyze body; optional business key | Three projections | CURRENT |
| POST | `/api/v1/clinical-report` | Report projection | Analyze body | `{analyze, assessment, report, ...}` JSON | CURRENT projection |

Silent defaults (**analyze / evaluate-adjacent adapters only**): missing age → `5.0`, missing weight → `20.0`, default environment/activity/name. **Workbench does not inherit those defaults.** Birthday-derived age is reproducible when the workbench request includes `as_of_date` (copyable Dolly example uses `2026-09-09`). See [docs/omega16-api-contract-design.md](docs/omega16-api-contract-design.md).

### Catalog

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/catalog` | Product rows |
| GET | `/api/v1/presentation/catalog` | Presentation catalog |
| GET | `/api/v1/store` | Store rows |
| GET | `/api/v1/store/{product_id}` | One product |

Demo catalog when `WAGTOPIA_DEMO_MODE` is true (`/health` reports `demo_catalog`, `catalog_source`).

### Other registered routes (exist; not “tools”)

- PPIE debug / validation-console (`PPIE_DEBUG` or `?debug=1` for some)
- Science graph: `/api/v1/graph/*`, `/api/v1/science/{audit,coverage,versions}` (API key when configured)
- Authoring + research helpers (science staging; **not** agent read/calculate)
- Groomer session: `/api/v1/groomer/update`, `/api/v1/groomer/session/{pet_id}` (canonical dog events when identified; transient cache otherwise)
- Dog state: `/api/v1/dogs`, `/api/v1/dogs/{id}/events`, `/api/v1/dogs/{id}/preferences`, `/api/v1/dogs/{id}/recompute`, `/api/v1/dogs/{id}/analyses`, `/api/v1/dogs/{id}/analyses/compare` (SQLite; not warehouse)
- AI: `POST /api/v1/ai/explain` (does not run the engine); `POST /api/v1/ai/tools/invoke` (allowlisted gateway; not MCP)
- `GET /api/breeds`, evidence/products-by-condition helpers
- `GET /authoring/explorer` looks for `authoring/studio/explorer.html` at **repo root**; the file currently lives under `legacy/authoring/studio/explorer.html` — this page may **404**

Do not treat the route list as a stable external-agent SDK.

---

# 28. Developer Provenance

Typical analyze keys (not an OpenAPI model): `profile`, `careModel`, `requirementProfile`, `packageOptions`, `optimizerProvenance` (includes `filter_funnel`, `llm_used`), `scientificEvidence`, `engine`, `version`, plus legacy aliases (`pet`, `risks`, `products`) and a `debug` blob.

Workbench adds `correlation_id`. Developer projection exposes optimizer funnel.

Matcher vs optimizer: packages are **not** taken from empty `productRecommendations`.

---

# 29. Testing

```bash
py -3 -m pytest -q
```

Targeted:

```bash
py -3 -m pytest tests/contracts tests/architecture/test_omega11_boundaries.py -q
py -3 -m pytest tests/normalization tests/architecture/test_omega12_boundaries.py -q
py -3 -m pytest tests/optimization -q
py -3 -m pytest tests/interface -q
py -3 -m pytest tests/mathematics tests/formulas tests/science_graph tests/warehouse_qa -q
py -3 -m pytest tests/tools tests/architecture/test_omega17_4_tool_isolation.py tests/api/test_omega17_4_tools.py -q
```

`tests/interface` includes exhaustive `2^N−1` searches and workbench POSTs; those can take **tens of minutes**.

Ω11 contract + boundary (2026-09-08): **39 passed**.  
Canonical-routes + contracts check for this README (2026-09-08): **34 passed**.  
Larger executed unique suite in the Ω11 report: **287 passed, 32 skipped, 0 failed**; **112** long interface optimizer tests were **not** re-run that session (duration).

Skips: historical DataPlatform tests while `warehouse/current` clinical CSVs are empty (`tests/conftest.py`).

Do not copy stale Ω-phase pass counts. Latest numbers: [docs/omega11-agent-data-contract-report.md](docs/omega11-agent-data-contract-report.md) §26 and [docs/WAGGY_SYSTEM.md](docs/WAGGY_SYSTEM.md) §26.

---

# 30. Determinism

**Intended:** same dog input + observations + warehouse version + catalog + budget + `ALGORITHM_VERSION` → same packages and care model.

**Current limitations:**

- `profile_from_analyze_body` defaults age/weight/activity/environment (legacy analyze path only) (legacy analyze path)
- `profile_from_workbench_body` is fail-closed (no 5-year / 20 kg defaults)
- Birthday → age uses `datetime.now()` unless workbench `as_of_date` is supplied
- In-memory groomer session merge on analyze / clinical-report (not workbench)
- Process-global `WAGTOPIA_DEMO_MODE`
- `N > 14` bounded enumeration (not full `2^N−1`)
- Without demo densities, nutrient validation is incomplete

Ω11 contracts exclude `demo_mode` as a scientific field and refuse silent numeric defaults. Canonical workbench HTTP is fail-closed; raw `/api/v1/analyze` is not.

---

# 31. Demo / Synthetic Data

`py -3 scripts/run_dev.py` sets `WAGTOPIA_DEMO_MODE=true` and `PPIE_DEBUG=true` by default.

The demo catalog (`app/data/demo_catalog.py`, names like “Demo Fresh Beef Bowl”) plus demo dry-matter densities are **synthetic commercial input** used to demonstrate the optimizer.

**They are not scientific evidence and must not be interpreted as veterinary recommendations or real market data.**

Health Analysis still reads the **warehouse**, not demo breed-care invention.

---

# 32. Known Limitations

- No MCP, live Gemini chat UI, or public tool marketplace
- Internal allowlisted tools exist; they do not run the engine and do not mutate preferences
- External MCP agents cannot call named tools
- Ω11 contracts not wired to HTTP
- Ω12 mapping not wired to HTTP / engine
- Product matcher often empty
- Nutrient requirements are a secondary source, not warehouse AAFCO
- Senior-specific minima NOT_AVAILABLE
- Many warehouse rows `NEEDS_VALIDATION` / `MISSING_PROVENANCE` / `migrated`
- Mixed-breed validated prevalence not available
- Demo catalog required for a populated nutrient search
- Silent HTTP defaults and session merge on **legacy analyze** (not workbench)
- No production auth/privacy guarantee
- No business analytics / sales data
- Authoring explorer path likely 404 at documented root
- 8 warehouse FK blockers on mechanism tables
- `warehouse/current` clinical projection empty (old tests skipped)
- Railway/`nixpacks.toml` exist; **production deployment is not asserted**

---

# 33. Roadmap

Separated from current implementation.

| Item | Status |
|---|---|
| Ω10 warehouse-backed Health Analysis + exhaustive optimizer + workbench | CURRENT |
| Ω11 canonical agent data contracts | CURRENT (types/registry only) |
| Ω11.5 this README | CURRENT |
| Ω12 normalization + entity mapping | CURRENT (off engine/HTTP path) |
| Ω16 canonical API + role-aware workbench | CURRENT |
| Tool adapter / tool server (`analyze_health`, …) | CURRENT internal gateway (`app/tools/`); MCP / tool server PLANNED |
| External-agent integration test | PLANNED |
| Bounded Gemini/chat UI | PLANNED — must not reason |
| Warehouse flag research (do not invent values to clear flags) | PLANNED scientific work |
| Primary AAFCO in warehouse; real product densities | PLANNED |
| Production hardening (auth, privacy, durable sessions) | PLANNED |

Do not treat the above as shipped.

---

# 34. Development Workflow

Verified from `scripts/run_dev.py`, `requirements.txt`, `pytest.ini`, `app.main:app`:

```bash
py -3 -m pip install -r requirements.txt
py -3 scripts/run_dev.py
```

Open the URL the launcher prints (usually `http://127.0.0.1:8000/`). Role switcher is on that page. Demo catalog **ON** by default.

```bash
py -3 -m pytest -q
```

OpenAPI: `http://127.0.0.1:8000/openapi.json`  
Health: `http://127.0.0.1:8000/health`

Optional: `scripts/run_wagtopia_local.py` (multi-interface launcher). Production-style start in `nixpacks.toml`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

There is no separate Node frontend build. UI is FastAPI static files from `legacy/`.

---

# 35. Contributing Rules

See also [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

1. Never put inferred values into canonical evidence without validation.
2. Never fabricate prevalence.
3. Never silently overwrite evidence.
4. Preserve provenance columns and status flags.
5. Keep observations separate from scientific facts.
6. Keep commercial / demo catalog separate from science.
7. Keep product rows separate from medical efficacy.
8. Do not hardcode SKU membership in the optimizer or frontend.
9. Do not let an LLM override deterministic reasoning.
10. Do not make role-specific copies of the engine.
11. Prefer one analysis and projections.
12. Preserve `warehouse/recovery_original/`.
13. Do not delete incomplete evidence.
14. Mark uncertainty (`NOT_AVAILABLE`, `NEEDS_VALIDATION`, `MISSING_PROVENANCE`).
15. Treat `NOT_AVAILABLE` as valid.
16. Add tests before changing scientific or optimizer behavior.
17. Never silently change science while doing UI work.

---

# 36. Architectural Non-Negotiables

### Scientific boundary

LLMs (when added) explain and orchestrate. They do not create scientific truth.

### Deterministic boundary

Health, nutrition constraints, eligibility, and package optimization are deterministic capabilities (`PACKAGE_OPTIMIZER_V2_1`, `resolve_care_model`).

### Evidence boundary

Scientific claims must trace to warehouse rows and their status. No evidence → `NOT_AVAILABLE`.

### Commercial boundary

Catalog policy and demo overlay change the search space, not prevalence or papers.

### Observation boundary

Groomer notes are observations, not facts and not diagnoses.

### Agent boundary

Agents must use authorized capabilities. There is **no** tool server yet. Authoring WRITE is not an agent read tool.

### Projection boundary

Customer, Groomer, Business, and Developer consume one canonical analysis.

---

## Docs map

| Doc | Role |
|---|---|
| [docs/WAGGY_SYSTEM.md](docs/WAGGY_SYSTEM.md) | Canonical system specification |
| [docs/omega11-agent-data-contract-report.md](docs/omega11-agent-data-contract-report.md) | Ω11 contracts |
| [docs/omega12-normalization-entity-mapping-report.md](docs/omega12-normalization-entity-mapping-report.md) | Ω12 mapping |
| [docs/DATA.md](docs/DATA.md) | Data layout pointer |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Contributor rules |
| [docs/archive/](docs/archive/) | Historical / recovery reports |
