# Waggy Warehouse Integrity Freeze

**Phase:** 4 — observational / forensic only  
**Date:** 2026-09-17  
**Workspace:** `c:\Users\Admin\Downloads\waggy`  
**Prior source of truth:** `docs/WAGGY_CORE_FORENSIC_MAP.md` (Phase 1), `docs/WAGGY_CANONICAL_DATA_FLOW.md` (Phase 2), `docs/WAGGY_BASELINE_TEST_AUDIT.md` (Phase 3)  
**Method:** Read-only repository inspection plus process-local runtime probes. No production code, tests, CSVs, YAML, JSON, schemas, configuration, golden fixtures, frontend, or warehouse data were modified.

**Claim labels**

| Label | Meaning |
|---|---|
| FACT | Observed in code, on-disk files, or this-phase runtime |
| INFERENCE | Architectural interpretation of those facts |
| UNKNOWN | Not established from repository evidence |

If this file and a later live run disagree, **runtime wins**.

---

# 1. Executive Summary

**Where Waggy Core gets knowledge today (FACT):**

The Core Brain (`PPIEWellnessAgent` → `AssessmentAgent` → `FormulaGraph`) loads through `DataRepository` / `DataPlatform` → `app.data.loader.load_all_tables`. In this workspace that path is **not** `warehouse/science` and **not** `warehouse/current`. It is:

1. `resolve_clinical_root()` → `warehouse/` (`PPIE_DATA_DIR` unset; `WAGGY_WAREHOUSE_ROOT` unset).
2. `is_native_warehouse(warehouse/)` = **False** because `warehouse/science/` **does not exist**.
3. `is_biology_warehouse(warehouse/)` = **True** because `warehouse/biology/breeds.csv` exists.
4. `load_biology_warehouse` projects `warehouse/biology/` + `warehouse/prevention/` into in-memory RISK_V2_1 tables and stamps version **`5.0.0-biology`**.

**Commercial / product knowledge on that same Core path (FACT):**

- Demo **OFF:** `product_catalog()` = **0** rows. Package optimizer `candidate_count=0`, `valid_count=0`. Product matcher recommendations = **0**.
- Demo **ON:** `overlay_frame` **replaces** (does not merge) five product-domain tables from `app/data/demo_catalog.py` (**12** synthetic products). Nutrient densities come from `app/data/demo_scientific_dataset.py` (`data_origin=demo_synthetic`). Matcher returns **1** SKU (`TR011`). Optimizer `candidate_count=12`, `valid_count=1152`, **20** displayed options per tier.

**A second warehouse interface exists and is not the Core Brain loader (FACT):**

`repository.warehouse.WarehouseInterface` reads **raw** CSVs including `commercial.product_master` (**16** rows) and `prevention.*`. `PPIEWellnessAgent` does **not** import it. Green `tests/warehouse/` therefore does **not** mean the engine has a product catalog.

**Stale metadata (FACT):**

| Artifact | Declared | Runtime Core |
|---|---|---|
| `warehouse/manifest.yaml` | `5.0.0-science`, `root: warehouse/science` | Unused by biology fallback |
| `warehouse/CANONICAL_MANIFEST.json` / `DOMAIN_REGISTRY.json` | science-only paths under `warehouse/science` | Unused (`is_native_warehouse` false) |
| `warehouse/current/release.json` | `active_version: native-runtime` | Not used for loading (`app/core/paths.py`) |
| HTTP workbench `warehouse_version` | — | `DataRepository.version` = `5.0.0-biology` |
| `GET /api/v1/science/versions` | `current_science_versions()` reads **manifest.yaml** | Would report `5.0.0-science` (source-traced; not live-called this phase if API key gated) |

**Synthetic-first / real-data-replaceable (INFERENCE, not implemented):**

The demo overlay is already a replaceable **commercial catalog + synthetic densities** seam. It is **not** a ScienceProvider. Biology/prevention CSVs remain the scientific tables in both demo modes. Demo SKU IDs **collide** with `product_master` IDs but names differ (SF001 = Farmina on disk vs Demo Fresh Beef Bowl in overlay).

**This phase does not freeze scientific validity.** Runtime-used ≠ validated. Many biology rows are `MISSING_PROVENANCE` or `needs_validation`.

---

# 2. Scope and Non-Goals

**In scope:** inventory of warehouse paths; loader map; runtime authority for demo ON/OFF; trust/status matrix; duplication; versions; missing-data semantics; observational provider seams; invariants.

**Out of scope / not done:** repairing loaders; merging DataRepository with WarehouseInterface; populating empty CSVs; converting demo into “real” products; creating ScienceProvider/ProductProvider/CommerceProvider; wiring Ω12, ActivityNode, or GroomingNode; restoring `waggy-frontend/`; making pytest green; regenerating goldens.

**Frontend failures** from Phase 3 remain class D missing assets and are **not** warehouse defects.

---

# 3. Warehouse Directory Inventory

**FACT — git snapshot this phase:** branch `main`, HEAD `0eb0410`, dirty working tree (Ω16/Ω17 + docs). Warehouse CSVs were not edited.

**FACT — `warehouse/science/` does not exist** at the warehouse root. `warehouse/runtime/` does not exist. `warehouse/current/product_portfolio/` does not exist.

**FACT — top-level `warehouse/` children:**

| Path | Kind | Core Brain? | Notes |
|---|---|---|---|
| `warehouse/biology/` | 9 CSVs | **Yes** (projected) | Runtime scientific identity, traits, observed prevalence, conditions. `environment_facts` / `life_stage_health_*` / `size_risk_*` hashed but **not** projected into DataPlatform tables (except mixed-breed). |
| `warehouse/prevention/` | 2 CSVs | **Yes** (projected) | Condition ingredients + activities |
| `warehouse/commercial/` | 7 CSVs | **No** (Core catalog) | Loaded by WarehouseInterface + Ω12 identity catalog. Not by `load_biology_warehouse`. |
| `warehouse/nutrition/` | 5 CSVs | **No** (Core) | WarehouseInterface. Two composition files header-only |
| `warehouse/mapping/` | 5 CSVs + README | **No** (engine) | Ω12 aliases only |
| `warehouse/current/` | `README.md` + `release.json` | **No** | Historical pointer; pytest skips when product_portfolio empty |
| `warehouse/mechanisms/` | 9 CSVs | **No** (Core) | WarehouseInterface + `repository/mechanisms` |
| `warehouse/objectives/` | 6 CSVs | **No** (Core) | WarehouseInterface + `repository/objectives` |
| `warehouse/sources/` | 3 CSVs | **No** (Core) | WarehouseInterface |
| `warehouse/recipes/` | 2 CSVs | **No** (Core) | WarehouseInterface |
| `warehouse/reference/` | 5 CSVs including `papers.csv` (199) | Partial | WI loads 4 reference tables, **not** `papers.csv` |
| `warehouse/formulas/` | 7 CSVs | **No** (Core) | `FormulaWarehouseLoader` registers into WI at call time |
| `warehouse/optimization/` | 8 CSVs | **No** (Core) | Parallel `repository/optimization` stack |
| `warehouse/science_graph/` | 3 CSVs | **No** (Core) | Not in default WI `CANONICAL_DATASETS` |
| `warehouse/validation/` | 1 CSV | **No** | `actual_clinical_cases.csv` (2 rows) |
| `warehouse/benchmarks/` | 3 JSON | **No** (Core) | `repository/benchmarks` |
| `warehouse/repository/` | Python package | **No** (live science) | `ScientificRepository` reads **`warehouse/science/...`** which is missing → 0 entities |
| `warehouse/recovery_original/` | 192 files / 168 CSVs | **No** | Read-only intern recovery (README). Do not treat as runtime |
| `manifest.yaml`, `DOMAIN_REGISTRY.json`, `CANONICAL_MANIFEST.json` | metadata | **Stale for Core** | Science-root story |
| `MIGRATION_*.csv`, `VALIDATION_SUMMARY.csv`, `WAREHOUSE_GUIDE.csv` | reports | **No** | Migration documentation tables |

**FACT — `repository/warehouse/science/README.md` and `repository/warehouse/commercial/README.md`:** documentation only; they point canonical facts at root `warehouse/biology|prevention|nutrition|commercial`. They are not loaders.

---

# 4. Dataset Inventory

Active tree (excluding `recovery_original/`): **76 CSVs**. **6 header-only.** **7 `*_NEEDS_VALIDATION.csv`.** Row counts are FACT from this-phase CSV reads.

### 4.1 Biology

| Path | Rows | Header (abbrev.) | Data? | Manifest YAML? | Biology loader table? | WI dataset? | Domain | Authoritative for Core? | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| `biology/breeds.csv` | 48 | breed_id, breed_name, … status | Yes | No (stale science root) | `breeds` (projected; traits merged) | `biology.breeds` | scientific identity | **Yes** (name join) | High |
| `biology/breed_traits.csv` | 432 | fact_id, breed_id, trait_name, trait_value, … status | Yes | No | Merged onto `breeds` columns | `biology.breed_traits` | phenotype mapping | **Yes** as trait columns | High |
| `biology/observed_breed_conditions.csv` | 16 | fact_id, breed_id, condition, prevalence… | Yes | No | `breed_conditions` | `biology.observed_breed_conditions` | cited prevalence | **Yes** for RISK / care model | High |
| `biology/trait_condition_associations.csv` | 90 | trait_name, trait_value, condition, effect_value… | Yes | No | Split into 9 `*_conditions` tables (10 rows each) | `biology.trait_condition_associations` | trait–condition mapping | **Yes** | High |
| `biology/conditions.csv` | 34 | condition_id, condition_name, body_system… | Yes | No | `warehouse_conditions` | `biology.conditions` | identity | Loaded; RISK joins on **names** from other tables | High |
| `biology/environment_facts.csv` | 10 | environment_id, metric_name… | Yes | No | **Not a table** (file hashed) | `biology.environment_facts` | environment metrics | **No** for FormulaGraph | High |
| `biology/mixed_breed_NEEDS_VALIDATION.csv` | 10 | trait_a, trait_b, condition, factor, status=`needs_validation` | Yes | No | `mixed_breed_interactions` | `biology.mixed_breed_NEEDS_VALIDATION` | mixed-breed heuristic | **Used** by `scientific_care` | High |
| `biology/life_stage_health_NEEDS_VALIDATION.csv` | 10 | stage, core_health_problems, status=`needs_validation` | Yes | No | **Not a table** | WI yes | life stage | **No** for Core | High |
| `biology/size_risk_NEEDS_VALIDATION.csv` | 4 | status=`needs_validation` | Yes | No | **Not a table** | WI yes | size risk | **No** for Core | High |

Status on disk (FACT): breeds `active=9`, `MISSING_PROVENANCE=39`; all 432 traits `MISSING_PROVENANCE`; observed + trait associations `migrated`.

### 4.2 Prevention

| Path | Rows | Biology table | WI | Core use |
|---|---|---|---|---|
| `prevention/condition_ingredients.csv` | 12 | Copied to **both** `condition_ingredients_sci` and `_prev` | `prevention.condition_ingredients` | NutritionNode / matcher / care model (`repo.condition_ingredients()` dedupes to 12) |
| `prevention/condition_activities.csv` | 20 | `condition_activities` | `prevention.condition_activities` | ActivityNode lookup; **public** activity still assembler heuristic (Phase 2 G1). Status mix: `migrated=10`, `needs_validation=10` |

### 4.3 Commercial (on disk; not Core catalog)

| Path | Rows | WI | Ω12 | Engine catalog |
|---|---|---|---|---|
| `commercial/product_master.csv` | 16 | Yes | Product/brand identity | **No** |
| `commercial/product_feeding_guide.csv` | 23 | Yes | No | **No** |
| `commercial/product_functions_NEEDS_VALIDATION.csv` | 10 | **Not in default WI map** | No | **No** |
| `commercial/product_recipe.csv` | 0 header-only | Yes | No | **No** |
| `commercial/product_recipe_NEEDS_VALIDATION.csv` | 0 header-only | **Not in WI map** | No | **No** |
| `commercial/product_declared_nutrition.csv` | 0 header-only | Yes | No | **No** |
| `commercial/product_pricing_NEEDS_VALIDATION.csv` | 0 header-only | **Not in WI map** | No | **No** |

`product_master.status` = `NEEDS_VALIDATION` on **all 16** rows. `product_status` = `active` 12 / `sold_out` 4.

### 4.4 Nutrition (WarehouseInterface; not Core nutrient math)

| Path | Rows |
|---|---|
| `nutrition/ingredients.csv` | 9 |
| `nutrition/units.csv` | 2 |
| `nutrition/ingredient_composition.csv` | 0 header-only |
| `nutrition/food_composition.csv` | 0 header-only |
| `nutrition/ingredient_composition_NEEDS_VALIDATION.csv` | 12 (`measure_type=dose_recommendation_only`, not product dry-matter) |

### 4.5 Mapping (Ω12 only)

| Path | Rows |
|---|---|
| `mapping/breed_aliases.csv` | 5 |
| `mapping/condition_aliases.csv` | 3 |
| `mapping/product_aliases.csv` | 2 (SF001→Farmina, TR011→Zeal mussels) |
| `mapping/observation_aliases.csv` | 4 |
| `mapping/sex_aliases.csv` | 6 |

Runtime Ω12 catalog counts (FACT, `load_catalog()`): breed by_id **48**, condition **34**, product **16** (from **commercial master**, not demo), brand **5**.

### 4.6 In-memory policy tables (not CSVs)

FACT: `app/data/native_loader.py` `PACKAGE_TIERS` (3 rows, staple `SF001`) and `PRODUCT_DEFAULTS` (5 keys → TR001/TR011/TR003/TR007/TR008) are injected by `build_biology_views`. They are **Repository policy constants**, not warehouse science.

### 4.7 Synthetic demo (not CSVs)

FACT: `app/data/demo_catalog.py` — 12 products, 12 prices, 12 feeding rules, 8 component rows, 12 functions. `app/data/demo_scientific_dataset.py` — per-SKU synthetic DM densities. Activated only when `WAGTOPIA_DEMO_MODE` is truthy.

### 4.8 Parallel stacks (present, not Core)

Mechanisms, objectives, sources, recipes, formulas, optimization, science_graph, reference (incl. 199 papers), validation (2 clinical cases), benchmarks JSON: on disk; consumed by `repository.*` and/or WI; **no** `from repository.*` imports under `app/` except debug math replay.

---

# 5. Runtime Loader Map

### LOADER A — `load_all_tables` / `load_biology_warehouse` (CORE)

- **Path:** `app/data/loader.py` → `app/data/warehouse_biology.py` `load_biology_warehouse`
- **Reads:** `biology/*.csv` + `prevention/*.csv` (all CSVs hashed; subset projected)
- **Called by:** `DataPlatform.__init__` ← `bootstrap(clinical_root_str())` ← `PPIEWellnessAgent`
- **Produces:** in-memory tables listed in §6; `Manifest.version="5.0.0-biology"`
- **Transformations:** column rename/project; breed_traits pivoted onto breed rows; trait_condition_associations bucketed by `trait_name`; hardcoded display aliases (Lab→Labrador Retriever, etc.); sci/prev ingredient tables are **copies of the same frame**
- **Normalization:** strings as loaded; prevalence parsed later in `DataPlatform.breed_conditions`
- **Filtering:** none on species/status/year (module docstring)
- **Fallback:** if `warehouse/science` existed, native loader would run first and `merge_biology_into` would fill **empty** native tables only
- **Demo:** does not change this loader; overlay is later
- **Missing data:** missing CSV → empty DataFrame; `allow_empty=True` on generated FileSpecs
- **Authority:** **RUNTIME_AUTHORITATIVE for Core Brain science**
- **Evidence:** this-phase bootstrap log `Biology warehouse views: breeds=48 breed_conditions=16 ingredients=12`; `version=5.0.0-biology hash=66017507555b51c7 files=11`

### LOADER B — `DataPlatform._frame` + `overlay_frame` (CORE commercial seam)

- **Path:** `app/data/repository.py` `_frame` → `app/data/demo_catalog.overlay_frame`
- **Reads:** in-memory table named `products` / `product_components` / `product_pricing` / `product_feeding_rules` / `product_functions`
- **Demo OFF:** returns base (biology views have **no** `products` table → empty)
- **Demo ON:** **replaces** the whole frame with demo DataFrame (`return demo.copy()`, not concat)
- **Called by:** all `DataRepository.product_*` accessors used by ProductNode, package optimizer, catalog API
- **Public API:** yes (`GET` catalog routes; workbench packages/recs)
- **Authority:** **RUNTIME_AUTHORITATIVE for engine products when demo ON**; **empty** when demo OFF
- **Evidence:** platform snapshot catalog 0 vs 12

### LOADER C — `demo_product_nutrient` (CORE package nutrient math)

- **Path:** `app/data/demo_scientific_dataset.py`
- **Called by:** `app/agent/package_search.py`
- **Produces:** synthetic DM densities + `data_origin=demo_synthetic`
- **Demo behavior:** lookup by product_id; used to build requirement profile / validity when demo products exist
- **Does not read warehouse commercial recipe files**
- **Authority:** synthetic commercial densities only. AAFCO-style minima are `scientific_requirements.py` (secondary source; `warehouse_authoritative: False`)

### LOADER D — `WarehouseInterface` (PARALLEL, NOT CORE)

- **Path:** `repository/warehouse/warehouse_interface.py`
- **Reads:** `CANONICAL_DATASETS` under `settings.warehouse_root` (raw pandas)
- **Called by:** `repository/pipeline`, `repository/mechanisms`, `repository/objectives`, `repository/optimization`, `repository/science_graph`, `repository/formulas`, `scripts/validate_warehouse.py`, tests
- **Not called by:** `app/agent/engine.py` / FormulaGraph
- **Produces:** raw frames including `commercial.product_master` (16), empty recipe/nutrition composition
- **Validation:** `validate()` this phase: `ok=False`, **8** issues (broken FK `COND_*` / `ING_*` vs biology/nutrition id styles)
- **Authority:** **authoritative for the parallel mathematics/QA stack, not for Core HTTP analysis**
- **Evidence:** `app/` has no `WarehouseInterface` import; WI snapshot rows

### LOADER E — `ScientificRepository` (DEAD for current disk layout)

- **Path:** `warehouse/repository/scientific.py`
- **Reads:** `warehouse/science/breed/breeds.csv`, `science/product/PRODUCT_CATALOG.csv`, …
- **Called by:** `DataRepository.scientific()` if something invoked it
- **FormulaGraph:** **no** `get_breed` / `scientific()` calls under `app/agent/`
- **This-phase call:** `sci.breeds()` = **0**, `sci.products()` = **0** (directory missing; empty lists, not exception)
- **Authority:** **not runtime**

### LOADER F — Ω12 `app/normalization/catalog.py`

- **Reads:** `biology/breeds.csv`, `biology/conditions.csv`, `commercial/product_master.csv`, `mapping/*.csv`
- **Engine path:** **not wired** (Phase 2 G6; isolation tests)
- **Authority:** mapping tests only

### LOADER G — native science loader (NOT TAKEN)

- **Path:** `app/data/native_loader.py` `is_native_warehouse`
- **Gate:** `(root / "science").exists()` — **False**
- **Would read:** `DOMAIN_REGISTRY.json` paths under `warehouse/science/`
- **Note:** `DOMAIN_REGISTRY.json` **does** exist at warehouse root, but the science folder check fails first

### LOADER H — historical `breed_analysis` / `load_manifest` (NOT TAKEN)

- Third branch of `load_all_tables` when neither native nor biology
- `warehouse/current/README.md` still describes `product_portfolio/*.csv` + `manifest.yaml` as the archive PPIE would load — **stale vs biology fallback**

### LOADER I — ParameterRepository / UnitNormalizer

- **AssessmentAgent** constructs `ParameterRepository()` / `UnitNormalizer()` **in-memory defaults**
- `from_warehouse(warehouse/runtime/...)` **exists** but **is not called**; `warehouse/runtime/` **missing**
- **Authority:** hardcoded Python constants, not CSVs

### LOADER J — `DataRepository.load_csv` legacy path

- Resolves via in-memory manifest tables first; else `pd.read_csv` on disk
- Listed in architecture test as a known noncanonical reader
- **INFERENCE:** leftover compatibility; Core nodes use typed accessors

---

# 6. Runtime Authority Matrix

Process-local probes this phase. Demo via `WAGTOPIA_DEMO_MODE` only. Unmodified `WORKBENCH_EXAMPLE_REQUEST`. Isolated processes (demo ON/OFF). HTTP 200 both.

| Concern | Demo OFF | Demo ON | Runtime authority |
|---|---|---|---|
| Warehouse root | `...\waggy\warehouse` | same | `resolve_clinical_root` |
| Loader | `load_biology_warehouse` | same | Core |
| `DataRepository.version` / HTTP `warehouse_version` | `5.0.0-biology` | `5.0.0-biology` | Core stamp |
| `csv_hash` / files | `66017507555b51c7` / 11 | same | Hashed biology+prevention files |
| Biology / breeds | 48 projected | 48 | biology CSVs |
| Health findings / insights | 3 findings, 7 insights; `demo_synthetic=false`; warehouse_status present | **same titles** | biology + prevention + RISK; **not** demo |
| Nutrition public targets | present (7 insights path); matcher 0 | matcher 1 (`TR011`) | condition_ingredients + matcher; demo only adds catalog |
| Activity (public) | assembler heuristic | same | **not** ActivityNode rows (Phase 2 G1; not re-litigated) |
| Grooming defs table | **0** rows | 0 | biology loader does not project defs |
| Products (engine) | **0** | **12** demo | overlay_frame |
| Product nutrients | none (claim: dry-matter unavailable) | synthetic demo densities | demo_scientific_dataset + scientific_requirements |
| Product components | 0 | 8 | demo |
| Package candidates / valid | 0 / 0 | 12 / 1152 | optimizer on active catalog |
| Displayed per tier | 0 / 0 / 0 | 20 / 20 / 20 | optimizer display limit |
| `catalog_source` | `"warehouse"` | `"demo"` | presentation flag |
| `demo_catalog` | false | true | presentation flag |
| `optimizer.search.synthetic_demo_data` | false | true | provenance |
| `requirementProfile.product_data_origin` | absent | `demo_synthetic` | provenance |
| `requirementProfile.synthetic_demo_data` | false | false | flag means AAFCO profile is not “demo science” |
| `requirementProfile.claim_wording` | nutrient validation incomplete — product dry-matter data unavailable | Meets modeled baseline nutrient constraints. | |
| analysis_signature | `956ade7005dea38b1fc996cf53909f308473d96790d392952be12189d37f9b63` | `c33710a3d3c9152aec73480a9f9b1484d0efbd3b48541252229054768ecb6500` | differs because recs/packages differ |
| WarehouseInterface `product_master` | 16 (not used by engine) | 16 | parallel stack |
| ScientificRepository products | 0 | 0 | missing `warehouse/science` |

---

# 7. Demo vs Non-Demo Data Flow

```
warehouse/biology + prevention
        ↓
load_biology_warehouse  →  DataPlatform._tables  (science; demo-invariant)
        ↓
DataPlatform._frame(name)
        ↓
   demo OFF: empty products
   demo ON:  replace with demo_catalog frames
        ↓
ProductNode (PRODUCT_MATCH_V2_1)     PackageNode (PACKAGE_OPTIMIZER_V2_1)
        ↓                                    ↓
productRecommendations                  wellnessPackages
        (independent; G5 frozen)
```

**FACT:** Demo does **not** alter biology row counts, health insight titles, or `warehouse_version`.

**FACT:** Overlay **replaces** product tables rather than unioning with `product_master`.

**FACT:** Demo does **not** write CSVs. Persistence of demo SKUs into SQLite would only happen if a `dog_id` analysis were stored (not exercised; no `dog_id` on example request).

**FACT:** Seven demo IDs collide with commercial master IDs and **disagree on name** (SF001 Farmina vs Demo Fresh Beef Bowl). `PACKAGE_TIERS.staple_product_id` is hardcoded `SF001`.

**INFERENCE:** Current demo is useful evidence for a **ProductProvider** that is synthetic-complete, but SKU identity is **not** a safe join key onto `product_master` without an explicit mapping decision.

---

# 8. Scientific/Biological Dataset Status

| Dataset | Core consumer | Runtime-authoritative? | Duplicate? | Complete enough for current engine? | NEEDS_VALIDATION file? | Value type (not validity) |
|---|---|---|---|---|---|---|
| breeds | BreedNode, RISK, epidemiology, care model | Yes (display names) | vs Ω12 ids; vs ScientificRepository | Yes for name resolve of Dolly Lab×Golden | No | identity; 39/48 `MISSING_PROVENANCE` |
| breed_traits | merged onto breeds | Yes as phenotype columns | vs trait_condition_associations | Loaded; provenance missing on all 432 | No | phenotype mapping |
| observed_breed_conditions | RISK / scientific_care | Yes | vs conditions.csv identity | 16 rows — sparse vs 48 breeds | No | cited prevalence (`migrated`) |
| trait_condition_associations | trait `*_conditions` tables | Yes | vs size_risk_NEEDS_VALIDATION (unused) | 90 associations → 10 per trait table | No | mappings (`migrated`) |
| conditions.csv | warehouse_conditions | Identity loaded; joins are names | vs prevention condition_id | 34 active | No | identity |
| condition ingredients | NutritionNode, matcher, care | Yes | sci+prev identical copies | 12 rows | No | mappings + doses (`migrated`) |
| condition activities | ActivityNode; assembler **ignores** for public JSON | Table yes; public output **no** | vs heuristic minutes | 20 rows | Partial row status | activity mappings |
| mixed_breed_NEEDS_VALIDATION | scientific_care flagged mix | Used as flagged table | none proven | 10 rows | **Yes** (filename + status) | heuristic interactions |
| environment_facts | Core no; `repository/pipeline/biological_runtime` yes | Core **no** | — | 10 rows exist | No | environment metrics |
| life_stage / size_risk NEEDS_VALIDATION | Core no; pipeline yes | Core **no** | — | rows exist | **Yes** | unvalidated notes |
| hardcoded `_BREED_ALIASES` | `normalize_breed_name` | Yes for Lab/GSD/Golden | vs `mapping/breed_aliases.csv` (Ω12) | 5 aliases | No | display alias, not science |
| PACKAGE_TIERS / PRODUCT_DEFAULTS | packages / defaults | Policy | vs empty commercial | 3 + 5 | No | configuration |

**Do not equate `migrated` with independently validated science.** That judgment is not in this freeze.

---

# 9. Product/Commercial Dataset Status

Answers to the required questions (FACT):

1. **Physical product data:** `warehouse/commercial/*` + demo Python modules + recovery_original copies.
2. **Actual rows:** master 16, feeding_guide 23, functions_NEEDS_VALIDATION 10; recipe / declared nutrition / pricing_NEEDS_VALIDATION **header-only**.
3. **Loaded by DataRepository:** **No** commercial CSVs. Demo overlay only when env set.
4. **Loaded by WarehouseInterface:** `product_master` 16, `product_recipe` 0, `product_declared_nutrition` 0, `product_feeding_guide` 23. Functions/pricing/recipe_NEEDS_VALIDATION **not** in `CANONICAL_DATASETS`.
5. **Reaches Core engine:** only demo overlay tables (demo ON).
6. **Reaches ProductNode:** `run_optimization_stage` → `repo.product_catalog()` / components. Demo ON: 1 recommendation (`TR011`). Demo OFF: 0.
7. **Reaches package optimization:** `load_candidate_products` from active catalog. Independent of matcher (G5). Demo ON 1152 valid; OFF 0.
8. **Demo-only products:** the 12 `Wagtopia Demo` SKUs when env on.
9. **Incomplete:** all commercial nutrient/recipe/pricing tables empty or NEEDS_VALIDATION; master itself labeled `NEEDS_VALIDATION`.
10. **Unusable as Core catalog today:** commercial files, because biology loader never attaches them to `products`.

**Phase 3 contradiction — documented, not resolved:**

| Stack | `product_master` / catalog |
|---|---|
| `tests/warehouse` WarehouseInterface | loads `commercial.product_master` (16) |
| Engine `DataRepository` | biology views; **0** product rows demo OFF |

EQUIVALENCE NOT PROVEN between commercial master and any engine `products` table. Schemas differ (master: `product_category`, `recipe_version`, `product_status`; demo: `category`, `subcategory`, `status`, `tags`). Names for shared IDs **differ**.

**Commercial nutrient data usable by the engine?** **No.** Empty recipe + empty declared nutrition + biology path does not load master.

---

# 10. Synthetic/Demo Dataset Analysis

| Item | Evidence |
|---|---|
| Source | `app/data/demo_catalog.py`, `demo_scientific_dataset.py` |
| Activation | `WAGTOPIA_DEMO_MODE` in {1,true,yes,on} |
| Scope | Product-domain tables only (`DEMO_TABLES`); docstring: commercial overlay |
| Count | 12 products; deterministic IDs SF001, SF002, TR011, TR001, TR003, TR007, TR008, JB001, HY001, HG001, SK001, DN001 |
| Distinguishable | Names/brand `"Wagtopia Demo"`; provenance `synthetic_demo_product_data`, `product_data_origin=demo_synthetic`, workbench `catalog_source=demo` |
| Nutrients | Synthetic DM + extras; **not** manufacturer facts (module docstring) |
| Ingredients | Declared-label demo components only (8 rows) |
| Public API | Yes when demo on (recs, packages, catalog_source) |
| Optimizer | Yes |
| Persist to warehouse CSVs | **No** |
| Persist to dog SQLite | UNKNOWN if `dog_id` set (not probed) |
| Affects biology/health | **No** (same 7 insight titles; `health_analysis.demo_synthetic=false`) |
| Replacement semantics | **Replace** table, not merge |

**Synthetic-first evidence (INFERENCE):** Demo already proves the engine can run end-to-end packages when a catalog + density function exist, without editing FormulaGraph. It does **not** prove a clean ID namespace vs commercial master.

`scripts/run_dev.py` sets demo true by default (Phase 1). Pytest autouse **deletes** the env (Phase 3).

---

# 11. Data Trust / Status Matrix

A dataset may have several properties.

| Dataset | Runtime Core? | Rows | Source | Status tags | Consumer | Notes |
|---|---|---|---|---|---|---|
| biology/breeds | RUNTIME_AUTHORITATIVE | 48 | CSV | 9 active / 39 MISSING_PROVENANCE | BreedNode | |
| biology/breed_traits | RUNTIME_USED_BUT_INCOMPLETE | 432 | CSV | all MISSING_PROVENANCE | merged traits | |
| observed_breed_conditions | RUNTIME_AUTHORITATIVE | 16 | CSV | migrated | RISK / care | sparse |
| trait_condition_associations | RUNTIME_AUTHORITATIVE | 90 | CSV | migrated | trait tables | |
| biology/conditions | RUNTIME_USED_BUT_INCOMPLETE | 34 | CSV | active | identity; name joins elsewhere | |
| mixed_breed_NEEDS_VALIDATION | RUNTIME_USED_BUT_INCOMPLETE | 10 | CSV | needs_validation | care model flagged | filename + status |
| environment_facts | PRESENT_NOT_RUNTIME_USED (Core) | 10 | CSV | migrated | repository pipeline | hashed into csv_hash |
| life_stage_health_NEEDS_VALIDATION | PRESENT_NOT_RUNTIME_USED (Core) | 10 | CSV | needs_validation | pipeline | |
| size_risk_NEEDS_VALIDATION | PRESENT_NOT_RUNTIME_USED (Core) | 4 | CSV | needs_validation | pipeline | |
| prevention ingredients | RUNTIME_AUTHORITATIVE | 12 | CSV | migrated | nutrition / matcher | sci/prev duplicate |
| prevention activities | RUNTIME_USED_BUT_INCOMPLETE | 20 | CSV | 10 migrated / 10 needs_validation | ActivityNode only | public JSON unused |
| package_tiers / product_defaults | RUNTIME_AUTHORITATIVE (policy) | 3 / 5 | Python | n/a | packages | staple SF001 |
| demo products | SYNTHETIC_DEMO | 12 | Python | demo | Product/Package nodes | env gated |
| commercial product_master | PRESENT_NOT_RUNTIME_USED (Core); WI used | 16 | CSV | NEEDS_VALIDATION | WI, Ω12 | ID clash vs demo |
| commercial recipe/nutrition/pricing | HEADER_ONLY | 0 | CSV | n/a | WI empty | |
| commercial functions_NEEDS_VALIDATION | PRESENT_NOT_RUNTIME_USED | 10 | CSV | NEEDS_VALIDATION | not in WI map | |
| nutrition composition canonical | HEADER_ONLY | 0 | CSV | | WI | |
| nutrition composition NEEDS_VALIDATION | PRESENT_NOT_RUNTIME_USED (Core) | 12 | CSV | needs_validation; dose_recommendation_only | WI | not product DM |
| mapping aliases | PRESENT_NOT_RUNTIME_USED (engine) | 20 | CSV | Ω12 | tests | |
| warehouse/science | STALE_OR_LEGACY / MISSING | — | metadata only | | native loader unused | |
| warehouse/current | STALE_OR_LEGACY | empty portfolio | release.json | | pytest skips | |
| mechanisms/objectives/… | PRESENT_NOT_RUNTIME_USED (Core) | see §4 | CSV | WI validate fails FKs | repository.* | DUPLICATE_SOURCE vs biology id scheme |
| recovery_original | STALE_OR_LEGACY | 168 CSVs | intern snapshots | | forensic only | |
| ScientificRepository | UNKNOWN/dead path | 0 | missing science dir | | DataRepository.scientific() | |

---

# 12. Duplicate and Conflicting Sources

| Pair | Schemas identical? | Rows identical? | Semantics identical? | Runtime-authoritative? | Intentional separation? | Verdict |
|---|---|---|---|---|---|---|
| `manifest.yaml` 5.0.0-science vs loader 5.0.0-biology | n/a | n/a | **No** | biology loader | Unknown; looks stale | CONFLICT (G8) |
| `warehouse/science` vs `warehouse/biology` | n/a | science **missing** | — | biology | Docs say science not current Health path | FACT missing dir |
| `warehouse/current` vs warehouse root | n/a | current empty | README still product_portfolio | root biology | Historical pointer | STALE |
| DataRepository vs WarehouseInterface | **No** | **No** (projected vs raw; products 0 vs 16) | Overlapping biology names, different product story | DR for Core; WI for parallel stack | INFERENCE: two stacks | EQUIVALENCE NOT PROVEN |
| condition_ingredients sci vs prev | Yes (copy) | Yes | Same 12 rows twice then deduped | Yes after concat+dedupe | Comment claims sci/prev split | DUPLICATE in memory |
| prevention ingredients vs nutrition/ingredient_composition_NEEDS_VALIDATION | **No** | Different (dose recs vs condition links) | Related ingredients | prevention for Core | UNKNOWN | EQUIVALENCE NOT PROVEN |
| product_recipe vs product_recipe_NEEDS_VALIDATION | **No** (different headers) | both 0 | — | neither for Core | UNKNOWN | both HEADER_ONLY |
| product_master vs demo catalog | **No** | 7 shared IDs; names differ | **No** | demo when env on | Demo overlay vs intern commercial | CONFLICT |
| product_master vs native PRODUCT_CATALOG | science file missing | — | — | — | DOMAIN_REGISTRY points at missing path | STALE |
| `_BREED_ALIASES` vs `mapping/breed_aliases.csv` | different columns | overlapping Lab/GSD/Golden | display vs canonical_id | hardcoded for engine | Ω12 isolated | DUPLICATE_SOURCE |
| `reference.condition_mechanisms` vs `mechanisms.condition_mechanisms` | not compared bytewise | 39 vs 11 | UNKNOWN | neither Core | UNKNOWN | EQUIVALENCE NOT PROVEN |
| WI validation IDs `COND_HIP_DYSPLASIA` vs biology `COND_653473C1` | n/a | broken FK | **No** | biology ids for Core | UNKNOWN leftover taxonomy | CONFLICT |
| HTTP workbench version vs `/api/v1/science/versions` | n/a | biology vs yaml science | **No** | workbench uses repo.version | two version helpers | CONFLICT |
| `csv_hash` files vs in-memory tables | n/a | 11 files vs 19 tables | hash includes unused biology CSVs | version string biology | hashing vs projection | document only |

---

# 13. Version / Manifest / Release Matrix

| Source | Value | Agrees with Core runtime? |
|---|---|---|
| `warehouse/manifest.yaml` | `5.0.0-science`, `root: warehouse/science` | **No** |
| `CANONICAL_MANIFEST.json` | `5.0.0-science`, domains under science/ | **No** |
| `DOMAIN_REGISTRY.json` | `5.0.0-science`, `products: product/PRODUCT_CATALOG.csv` | **No** (native path not taken) |
| `warehouse/current/release.json` | `native-runtime`, `schema: 3.1.0-native`, `clinical_root: warehouse` | Partial (root yes; native no) |
| `DataRepository.version` | `5.0.0-biology` | **Yes** (self) |
| Workbench `warehouse_version` | `5.0.0-biology` | **Yes** |
| `ALGORITHM_VERSION` / `engine_version` | `2.1.0` | Yes (engine, not warehouse) |
| `current_science_versions()` | reads YAML version | **No** vs Core |
| Tests `tests/warehouse` | WI loads commercial master | **No** vs engine catalog |
| `warehouse/README.md` | biology + prevention + commercial → DataRepository | Partial: commercial **not** actually in DataRepository |
| Docs WAGGY_SYSTEM commercial overlay | demo commercial only | **Yes** vs runtime |

---

# 14. Missing-Data Semantics

Observed / source-traced. Not changed.

| Domain | Missing / empty behavior |
|---|---|
| Biology breeds | Empty CSV → empty frame; BreedNode resolves 0 profiles (would degrade RISK). Dolly still resolved 2 profiles (FACT). |
| Breed unknown name | `normalize_breed_name` returns original string; `resolve_breed_rows` empty mask |
| Health / observed conditions | Sparse table → fewer breed-linked findings; engine still emitted 7 insights / 12 ranked conditions (FACT) |
| Nutrition ingredients | Empty would yield empty targets; 12 rows present |
| Activity public | Heuristic even when 20 warehouse rows exist (fail-open to hardcoded minutes, not to empty) |
| Grooming defs | Empty table → GroomingNode dumps 0; public checklist is hardcoded observations (G2) |
| Products demo OFF | Empty catalog → matcher 0, optimizer 0, claim_wording dry-matter unavailable (**returns empty, does not invent SKUs**) |
| Products demo ON | Synthetic fill (**explicit env**, not silent warehouse invention) |
| Packages | Empty candidates → 0 displayed; envelopes still exist as tiers |
| Header-only commercial nutrients | WI loads empty frames; Core never sees them |
| Invalid WI FKs | `validate()` reports errors; Core does not run that validator |
| Demo-only | Opt-in overlay; pytest deletes env |
| `DataRepository.load_csv` missing file | warning + empty DataFrame |
| Native/science missing | skip native; biology fallback (not exception) |
| `ScientificRepository` missing science | empty entity lists |

**INFERENCE for synthetic-first:** empty commercial currently **fails open to zero products**, not to invented science. Demo is the only synthetic fill and is flagged.

---

# 15. Current Knowledge vs Commerce Boundary

**What exists (FACT):**

```
DogProfileInput
    → biology/prevention (scientific knowledge)
    → healthInsights / nutritionalTargets / careModel
    → ProductNode: match against active catalog (demo or empty)
    → PackageNode: combinatorial search on same catalog
         independently of matcher recs
```

There is **not** a three-layer production path:

```
requirements → scientific product fit → commercial availability
```

Today it is:

```
requirements → available products in DataRepository.product_catalog()
```

Availability = rows in that catalog. Demo ON, that catalog is synthetic. Demo OFF, it is empty (commercial master is **not** “availability”).

`product_master.product_status` (`active`/`sold_out`) is **not** consulted by the engine.

Presentation already **labels** `catalog_source` demo vs warehouse and matcher-vs-package independence (`independent_of_product_match` in developer package_optimization). That is provenance, not a commerce engine.

**Preserve later:** dog fit (biology/nutrition/matcher) vs commerce priority (price, stock, affiliate). Do not implement that split in this phase.

---

# 16. Synthetic-First Readiness Assessment

1. **Already sufficient for synthetic execution:** biology+prevention for health; demo catalog+densities for packages. Live demo ON workbench HTTP 200, 1152 valid bundles.
2. **Demo datasets as evidence:** yes, for a **product/commerce** substitute. Not for replacing breeds/conditions.
3. **Hard-coded to warehouse structures:** `warehouse_biology` column maps; WI `CANONICAL_DATASETS` paths; Ω12 paths; ScientificRepository `science/` layout.
4. **Direct CSV readers (architecture-tracked):** loader, native_loader, repository.py, warehouse_biology, parameters, units, normalization/catalog, validation runtime, recover_intern script. FormulaGraph nodes use DataRepository accessors, not paths.
5. **Depend on DataRepository internals:** FormulaGraph, scientific_care, package_search, response_assembler, evidence API.
6. **Obvious future seams:** (a) biology/prevention snapshot, (b) product catalog + densities + pricing, (c) optional commerce/availability. See §17.
7. **Ambiguous seams:** WarehouseInterface vs DataRepository; PACKAGE_TIERS in Python vs CSV; AAFCO minima in Python vs warehouse nutrition; Ω12 vs display aliases.
8. **Must remain unchanged while providers are introduced later:** single FormulaGraph; matcher ⟂ packages; demo not silently becoming commercial master; NEEDS_VALIDATION not auto-promoted; warehouse_version observable; Ω12 off engine until a dedicated decision.

**Readiness (INFERENCE):** Core can already run synthetic-complete **packages** via env overlay. It cannot run synthetic-complete **science** without the biology CSVs (and should not invent them). Real commercial replaceability is **blocked** by empty recipe/DM tables **and** by the loader not attaching `product_master`.

---

# 17. Proposed Future Provider Seams (OBSERVATIONAL ONLY)

Do **not** implement. Names are proposals, not API commitments.

### Seam 1 — Scientific knowledge (candidate wrap of LOADER A)

- **Existing code:** `load_biology_warehouse` + `DataPlatform` breed/condition/ingredient/activity accessors + `scientific_care.resolve_care_model` + formula stages
- **Input:** biology/prevention CSVs (today)
- **Output:** projected tables / care model
- **Caller:** FormulaGraph nodes
- **Demo:** none (must stay that way unless explicitly designed)
- **Replaceable later:** CSV → other snapshot with **same projected columns**
- **Unresolved:** whether WI raw biology should ever replace projections; Ω12 ids vs names

### Seam 2 — Product catalog + nutrient densities (candidate wrap of LOADERS B+C)

- **Existing code:** `overlay_frame` + `product_catalog()` + `demo_product_nutrient` + `load_candidate_products`
- **Input:** empty or demo tables today; commercial CSVs unused by Core
- **Output:** candidate SKUs + densities
- **Caller:** ProductNode, PackageNode
- **Demo:** **is** the current implementation
- **Replaceable later:** real catalog with densities, **without** rewriting optimizer combinatorics
- **Unresolved:** SKU ID collision; whether overlay should merge vs replace; sold_out handling

### Seam 3 — Commerce / offer (currently mixed into Seam 2)

- **Existing code:** demo pricing, feeding rules, `product_status` on disk unused
- **Unresolved:** no separate Core interface

### Seam 4 — Parallel WI stack

- **Existing code:** `WarehouseInterface`
- **INFERENCE:** closer to a **QA / mechanism / future formula warehouse** than to Core Brain
- **UNKNOWN:** whether it is the intended future ScienceProvider
- **Must not** be silently swapped under FormulaGraph

### Seam 5 — Ω12 identity

- **Existing code:** mapping CSVs + catalog
- **Not a warehouse science provider**
- **Do not wire** (G6)

ParameterRepository/UnitNormalizer `from_warehouse` are **unused** seams pointing at missing `warehouse/runtime/`.

---

# 18. Frozen Architectural Invariants

These are **recommendations to freeze**, not permission to implement providers now.

| ID | Invariant | Freeze? | Evidence |
|---|---|---|---|
| A | Do not create a second Core Brain pipeline | **FREEZE** | Single `generate_reproducible_report`. WI/repository stacks are parallel, not a second HTTP engine. |
| B | `DogProfileInput` remains canonical engine input unless later evidence | **FREEZE** | Unchanged from Phases 1–3; workbench still fail-closed into it |
| C | Do not create a second CanonicalDog runtime DTO for cleanliness | **FREEZE** | No new evidence against Phase 2 |
| D | Do not silently replace runtime warehouse sources | **FREEZE** | YAML already disagrees with biology fallback; swapping to WI/commercial/science would change catalog and possibly health joins |
| E | Do not treat demo synthetic products as real commercial data | **FREEZE** | Provenance flags; name clash vs Farmina/Zeal master; module docstrings |
| F | Scientific knowledge and commercial availability remain distinguishable | **FREEZE** | Demo does not change health insights; catalog_source flag; empty non-demo catalog |
| G | Product fit and commerce priority remain conceptually separable | **FREEZE** | Matcher ⟂ packages already; no stock/affiliate layer in Core. Keep separable. |
| H | Future real datasets replaceable without rewriting Core decision logic | **FREEZE as goal** | Demo overlay already substitutes catalog without FormulaGraph rewrite. Commercial CSVs are **not** that substitute yet. |
| I | Unknown/incomplete science must not be silently converted into invented facts | **FREEZE** | NEEDS_VALIDATION / MISSING_PROVENANCE left as-is; empty catalog → 0 products not fake SKUs |
| J | Warehouse version/provenance remain observable | **FREEZE** | Workbench `warehouse_version`, csv_hash, demo flags. Also freeze awareness of the **YAML vs biology** version split until an explicit decision. |
| K | Future provider abstraction wraps existing responsibilities, no parallel engine | **FREEZE** | Wrap LOADER A/B/C; do not route HTTP through `repository.pipeline.biological_runtime` |

---

# 19. Unresolved Questions

1. Should Core ever load `commercial/product_master.csv` into `products`, or is demo the only catalog until a dedicated commercial integration? **UNKNOWN** (product decision). Even if loaded, recipe/DM tables are empty.
2. Should demo SKUs be remapped so they cannot collide with commercial IDs? **UNKNOWN**.
3. Is `WarehouseInterface` a future provider boundary or a leftover QA/math warehouse? **UNKNOWN**.
4. Should `current_science_versions()` be aligned with `5.0.0-biology`? **Not decided** (would be a code change).
5. Are `MISSING_PROVENANCE` breed/trait rows acceptable long-term science? **Not judged here.**
6. Will GroomingNode remain empty (`grooming_observation_defs` not projected)? **UNKNOWN** until a grooming phase.
7. Does intern `recovery_original` contain a richer product recipe that was intentionally not promoted? **Not inspected row-by-row this phase** (forbidden to copy into production).
8. Persist path: can demo SKUs be stored as if real when `dog_id` is set? **UNKNOWN** (not probed).

---

# 20. Evidence / Commands / Runtime Observations

**Environment (FACT):** Windows, Python 3.13.7, pytest 9.1.1 (not re-run as a green-suite campaign). Shell: `WAGTOPIA_DEMO_MODE`, `PPIE_DATA_DIR`, `WAGGY_WAREHOUSE_ROOT` unset.

**Commands (outside repo; read-only):**

- Inventory + DataPlatform + WI + Ω12: `C:\Users\Admin\waggy-phase4-probe.py` → `waggy-phase4-probe.json`
- Isolated workbench: `waggy-phase4-workbench.py false|true` → `waggy-phase4-wb-off.json` / `waggy-phase4-wb-on.json`

**Workbench (FACT):**

| | Demo OFF | Demo ON |
|---|---|---|
| HTTP | 200 | 200 |
| schema | `workbench_presentation.v1` | same |
| engine | 2.1.0 | same |
| warehouse_version | 5.0.0-biology | same |
| catalog_source | warehouse | demo |
| health insights | 7 | 7 (same titles) |
| health findings | Hip Dysplasia, Obesity, Atopic Dermatitis | same |
| product recs | 0 | 1 TR011 |
| candidates / valid | 0 / 0 | 12 / 1152 |
| displayed tiers | 0/0/0 | 20/20/20 |
| signature | `956ade70…7f9b63` | `c33710a3…ecb6500` (matches Phase 3 demo-on) |

`debug.formula_graph.order` is **not** on the workbench envelope (`debug=1` did not add it). Graph order MATCH remains Phase 3 engine evidence; this phase did not re-dump node order from FormulaGraph.

**WI validate:** `ok=False`, 8 broken_reference issues (mechanism IDs vs biology/nutrition IDs).

**Note:** An in-process probe that nulled `DataPlatform` between TestClient calls produced HTTP 500 (`platform not bootstrapped`). That is a **probe artifact**, not a production demo-ON defect. Isolated processes both returned 200.

---

# 21. Phase 4 Gate Decision

**GATE: PASS** (observational freeze complete)

The runtime warehouse boundary is frozen as:

- Core science = `warehouse/biology` + `warehouse/prevention` via `load_biology_warehouse` (`5.0.0-biology`)
- Core products = demo overlay **or empty**, **not** `product_master`
- Parallel WI stack exists and must not be mistaken for Core
- Metadata (`manifest.yaml`, `warehouse/science`, `warehouse/current`) is stale relative to Core
- Demo is a flagged commercial substitute, not validated commerce
- Empty/incomplete commercial nutrient tables remain empty; nothing was invented

**Not unblocked:** filling catalogs, merging loaders, wiring Ω12, treating WI as the engine warehouse.

**Exactly one recommended next phase:** **Phase 5 — Breed + trait** (still observational/contract freeze on the resolver and trait projection that already consume these biology tables; do **not** wire Ω12; do **not** attach commercial products).

---

STOP. Wait for human review. Do not proceed to Phase 5 until instructed.
