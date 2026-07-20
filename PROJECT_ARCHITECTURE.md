# PROJECT_ARCHITECTURE.md

**PPIE / Wagtopia — Phase 0 Complete Project Analysis**  
**Status:** Audit only. No refactors performed.  
**Algorithm stamp:** `2.1.0` (`app/agent/version.py`)  
**Data manifest:** `data/manifest.yaml` v2.1.0 (45 manifested tables; 47 CSV files on disk)  
**Generated:** 2026-07-21

---

## Executive summary

PPIE is a **deterministic clinical wellness engine**:

```
Dog profile (HTTP JSON)
  → FastAPI (app/api/main.py)
  → PPIEWellnessAgent pipeline (app/agent/engine.py)
  → CSV science tables (data/ via DataPlatform)
  → Analyze JSON + ClinicalAssessment / Clinical Report
  → Static demo UI (index.html + root JS)
  → Developer Validation Console (debug/calculation.html)
```

**Clinical math is locked in Python**, primarily:

| Concern | Module |
|---------|--------|
| Risk ranking | `app/agent/stages/health_risk.py` (`RISK_V2_1`) |
| Nutrient targets | `app/agent/ingredient_engine.py` (`NUTRIENT_TARGET_V2_1`) |
| Package tiers | `app/agent/package_optimizer.py` (`PACKAGE_OPTIMIZER_V2_1`) |
| Response shape | `app/agent/response_assembler.py` |

CSVs supply prevalence, doses, catalog, evidence quotes — **not formulas**.

**Dual UI surfaces:**

1. **Customer demo** — FastAPI static `index.html` → `POST /api/v1/clinical-report`
2. **Streamlit journey** — `app/ui/demo_app.py` (secondary; Jinja templates)
3. **Developer report** — `/debug/calculation?debug=1` → single-page Validation Console (`validation_console.v7`)

---

## 0. System context

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────────┐
│ index.html  │────▶│ FastAPI          │────▶│ PPIEWellnessAgent  │
│ + root JS   │     │ app/api/main.py  │     │ engine.py          │
└─────────────┘     └──────────────────┘     └─────────┬──────────┘
┌─────────────┐              │                         │
│ debug/      │──────────────┤                         ▼
│ calculation │              │              ┌────────────────────┐
└─────────────┘              │              │ DataRepository     │
┌─────────────┐              │              │ DataPlatform       │
│ Streamlit   │── optional ──┘              │ data/*.csv         │
│ app/ui      │                             └────────────────────┘
└─────────────┘
```

---

## 1. Folder analysis

### Top-level

| Folder / file | Purpose | Runtime role | Consumers | Dead? | Can delete? |
|---------------|---------|--------------|-----------|-------|-------------|
| `app/` | Python backend | Production | uvicorn, tests | No | No |
| `data/` | Scientific + product CSVs | Production snapshot | DataPlatform | Partial unused tables | No (migrate first) |
| `debug/` | Validation Console HTML | Debug-only | `/debug/calculation` | No | No |
| `docs/` | Architecture / data / API docs | Human | Engineers | N/A | Keep living set |
| `tests/` | Pytest + golden/parity | CI | Dev | No | No |
| `tools/` | Parity suite, dictionary gen | Dev scripts | Engineers | No | No |
| `archive/` | Historical docs/JS | None | None | Yes archive | Keep as archive |
| `node_modules/` | npm deps (minimal) | Optional | package.json scripts | N/A | `.gitignore` ok |
| `parity_output/` | Local parity dumps | Dev artifact | tools | Ephemeral | Safe to ignore |
| `.streamlit/` | Streamlit config | Streamlit only | demo_app | Secondary | Keep if Streamlit kept |
| Root `*.js` / `*.css` / `index.html` | Demo + console UI | Production static | FastAPI FileResponse | No | No |

### `app/` packages

```
app/
├── main.py                 → uvicorn entry shim
├── api/                    → HTTP surface
├── agent/                  → clinical pipeline + math
│   └── stages/             → biology, epidemiology, health_risk, nutrition, optimization
├── data/                   → CSV platform + reports + debug console builders
├── inference/              → formula IDs, constants, opt-in wrappers
└── ui/                     → Streamlit + Jinja (secondary)
    ├── renderer/
    ├── templates/
    └── static/
```

| Path | Purpose | Imports | Imported by | Complexity | Can delete? |
|------|---------|---------|-------------|------------|-------------|
| `app/api/` | Routes, payload adapter, evidence helpers | agent, data, inference | uvicorn | Medium | No |
| `app/agent/` | Locked clinical path | data, inference, formula_trace | api, tests, ui | **High** | No |
| `app/agent/stages/` | Stage runners | repository, state | engine | High | No |
| `app/data/` | Load/validate/join CSVs; assessment; console | pandas, manifest | agent, api | High | No |
| `app/inference/` | Registry + constants + opt-in | config | agent (constants), console, tests | Medium | No (trim opt-ins later) |
| `app/ui/` | Streamlit journey | agent, jinja | streamlit CLI | Medium | Optional product path |

---

## 2. File analysis (catalog)

### 2.1 Python — entry & API

| File | Purpose | Key exports | Consumers |
|------|---------|-------------|-----------|
| `app/main.py` | Re-export FastAPI `app` | `app` | uvicorn |
| `app/api/main.py` | All HTTP routes + static mounts | `app`, `agent` | Clients, demos |
| `app/api/payload_adapter.py` | Body → `DogProfileInput` | `profile_from_analyze_body` | analyze/assess/console |
| `app/api/evidence.py` | Condition evidence/products | `get_evidence_for_condition` | `/api/v1/evidence/*` |

### 2.2 Python — agent (clinical)

| File | Purpose | Key functions | Can delete? |
|------|---------|---------------|-------------|
| `engine.py` | Pipeline orchestration + timings | `PPIEWellnessAgent.generate_reproducible_report` | No |
| `state.py` | Pydantic models | `DogProfileInput`, pipeline state | No |
| `version.py` | `ALGORITHM_VERSION=2.1.0` | constants | No |
| `utils.py` | Facades / rounding / keys | `DataRepository`, `js_round` | No |
| `stages/biological.py` | Breed + trait resolve | `run_biological_stage` | No |
| `stages/epidemiology.py` | Alternate prevalence path | `run_epidemiology_stage` | **Legacy residue** (priorities overwritten by health_risk) |
| `stages/health_risk.py` | **RISK_V2_1** | `compute_risks`, … + `formula_execution` | No |
| `stages/nutrition.py` | Stage join condition→ingredients | `run_nutrition_stage` | Keep (stage still runs; assembly remaps) |
| `stages/optimization.py` | Product match stage | `run_optimization_stage` | Keep (assembler packages dominate UI) |
| `ingredient_engine.py` | Dose + nutrient map | `map_ingredients`, `calculate_dose` | No |
| `package_optimizer.py` | 3-tier packages | `build_optimized_packages` | No |
| `package_detail.py` | Enrich package detail | `enrich_package_for_detail` | No |
| `bundle_engine.py` | Monthly/yearly plans | `build_monthly_plan` | No |
| `response_assembler.py` | Frontend analyze JSON | `assemble_frontend_response` | No |
| `calculation_trace.py` | `calculationTrace` | `build_calculation_trace` | No |
| `pipeline_trace.py` | Stage metadata | `build_pipeline_trace` | No |
| `variable_map.py` | CSV path metadata for API | `VARIABLE_MAP` | No |
| `wellness_map.py` | Condition → goal titles | `goal_for_condition` | No |
| `condition_lookup.py` | Fuzzy condition match | `condition_matches` | No |
| `formula_trace.py` | Execution ledger helpers | `empty_execution`, `step`, … | No |

### 2.3 Python — data platform & reports

| File | Purpose | Consumers |
|------|---------|-----------|
| `repository.py` | `DataPlatform` + `DataRepository` | Entire agent |
| `loader.py` | Manifest CSV load + `_csv_row` | bootstrap |
| `runtime.py` | Process singleton / hot reload | api, agent |
| `schemas.py` / `validators.py` / `cache.py` / `watcher.py` | Manifest, validation, hash, FS watch | bootstrap |
| `clinical_assessment.py` | Modular ClinicalAssessment | `/ppie/assess` |
| `clinical_report_builder.py` | Clinical report v3 | `/clinical-report` |
| `report_generator.py` / `report_models.py` / `report_schema.py` | Standard report widgets | `/clinical-report` |
| `engine_trace.py` | EngineTrace debug | `/ppie/trace` |
| `validation_console.py` | Developer report payload v7 | `/validation-console` |
| `console_inspectors.py` | Console projections | validation_console |
| `assessment_diff.py` | Compare left/right | compare endpoint |
| `debug_*.py` | Presets, repo browser, boot banner | debug routes |

### 2.4 Python — inference

| File | Role | Production? |
|------|------|-------------|
| `formula_registry.py` | Formula ID catalog | Yes (IDs) |
| `config.py` | Weights, groomer map, score weights | Yes (constants) |
| `models.py` | `InferredValue`, `NOT_TRACEABLE` | Yes |
| `resolver.py` | Canonical keys | Yes |
| `risk.py` | Observatory ledger helper | Observability |
| `nutrition.py` / `ingredient.py` / `confidence.py` / `score.py` | Opt-in / wrappers | Mostly **no** / tests |
| `breed.py` / `explanation.py` | Thin wrappers | Low use |

### 2.5 Python — UI (Streamlit)

| File | Purpose | Primary consumer |
|------|---------|------------------|
| `ui/demo_app.py` | Streamlit entry | `streamlit run` |
| `ui/renderer/*.py` | Navigation + page VMs | Streamlit |
| `ui/templates/**` | Jinja HTML | Streamlit renderers |

### 2.6 Frontend (root)

| File | Purpose | API calls |
|------|---------|-----------|
| `index.html` | Demo shell | — |
| `app.js` | Boot clinical report + shell | `POST /api/v1/clinical-report` |
| `catalog-service.js` | Product cache | `GET /api/v1/store` |
| `report-renderer.js` | Widget render | none (props) |
| `ppie-shell.js` / `ppie-ui.js` / `ppie-sheets.js` | Shell / components / drawers | none |
| `ppie-trace.js` | EngineTrace panel | uses `payload.trace` |
| `ppie-dev-menu.js` | Dev fab links | none |
| `ppie-validation-console.js` | **Full Assessment Developer Report** | validation-console + debug APIs |
| `ppie-validation-console.css` / `theme.css` / `styles.css` | Styling | — |
| `debug/calculation.html` | Console host page | loads console JS |

### 2.7 Tests & tools

| Path | Purpose |
|------|---------|
| `tests/test_agent_pipeline.py` | Pipeline + HTTP contract |
| `tests/test_*report*.py` / `test_clinical_assessment.py` | Report/assessment |
| `tests/test_package_optimizer.py` | Packages |
| `tests/test_validation_console*.py` | Developer console |
| `tests/test_engine_trace.py` | EngineTrace |
| `tests/test_inference_*.py` | Inference layer / parity |
| `tests/test_ui_templates.py` | Jinja smoke |
| `tests/golden/` | Frozen response baselines |
| `tests/parity/` | Per-dog JS/Py parity dumps |
| `tools/parity_suite.py` | Parity runner |
| `tools/gen_data_dictionary_tables.py` | Docs helper |

---

## 3. Backend formula analysis

### Formula registry (IDs)

| Formula ID | Owner | Emits ledger? | Notes |
|------------|-------|---------------|-------|
| `PROFILE_NORMALIZE_V2_1` | payload_adapter | No | Request → profile |
| `BREED_RESOLVE_V2_1` | biological | No | Aliases + BREEDS |
| `TRAIT_BLEND_V2_1` | biological | No | Trait fields |
| `RISK_V2_1` | health_risk | **Yes** | Locked risk |
| `RISK_TRACE_V1` | inference.risk | Obs only | Not production overwrite |
| `NUTRIENT_TARGET_V2_1` | ingredient_engine | **Yes** | Dose map |
| `NUTRIENT_EST_V1` | inference.ingredient | No | Opt-in |
| `ING_FRAC_ORDER_V1` | inference.ingredient | No | Opt-in |
| `ACTIVITY_V2_1` | response_assembler | No | Activity plan |
| `PRODUCT_MATCH_V2_1` | optimization / optimizer | No | Catalog match |
| `COVERAGE_V2_1` | package_optimizer | Partial | provided/recommended |
| `PACKAGE_OPTIMIZER_V2_1` | package_optimizer | **Yes** | Tiers |
| `CONDITION_SUPPORT_V1` | inference.nutrition | No | Disabled |
| `EVIDENCE_RANK_V2_1` | response_assembler | No | Evidence attach |
| `VALIDATION_V2_1` | calculation_trace | No | Validation slots |
| `ASSESSMENT_PROJECT_V1` | clinical_assessment | No | Projection |
| `CONF_V1` | inference.confidence | No | Opt-in ladder |

### RISK_V2_1 (locked)

```
Inputs: breeds, traits, observed_conditions, age
  ↓
Lookups: SIZE/BODYTYPE/…_CONDITIONS (max prevalence per category)
  ↓
base_risk = clamp(sum(prevalences))   # NOT mean — JS parity
  ↓
× TRAIT_INTERACTIONS factors (clamp 0.8–1.2)
  ↓
× TRAIT_BENEFITS reduction_factor
  ↓
× MIXED_BREED_MATRIX (multi-breed)
  ↓
Significance: purebred → BREED_CONDITIONS prevalence;
              mixed → trait estimate ∪ breed observed
  ↓
Senior age ≥7 → ×1.05
  ↓
Outputs: risk_percent, confidence_percent
Confidence: round(len(evidence)/TOTAL_TRAIT_CATEGORIES*100,1)
            # category coverage only — not CONF_V1 ladder
Consumers: healthInsights, nutrition, packages, assessment
```

### NUTRIENT_TARGET_V2_1

```
Inputs: risks[], weight_kg
  ↓
CONDITION_INGREDIENTS (sci ∪ prev) match
  ↓
calculate_dose (mg_per_kg or absolute)
  ↓
max(daily) across conditions per ingredient
  ↓
Outputs: daily/monthly dose, for_conditions
Consumers: packages, nutritionalTargets, product coverage
```

### PACKAGE_OPTIMIZER_V2_1

```
Inputs: candidates, nutrient targets, health goals, tier
  ↓
Pick staple (PACKAGE_TIERS) → optimize essential|balanced|optimal
  ↓
coverage_matrix → score (coverage, clinical, evidence, diversity, cost)
  ↓
Accept / reject with reasons[]
  ↓
Outputs: wellnessPackages[3]
```

### Constants in Python (not CSV)

`app/inference/config.py`: category weights, groomer observation map, package score weights, surplus penalty, nutrient catalog seeds.

---

## 4. API analysis

| Method | Path | Backend | CSV / data | Response | UI consumer |
|--------|------|---------|------------|----------|-------------|
| GET | `/health` | platform_meta | breeds | health JSON | ops |
| GET | `/api/v1/catalog` | catalog_api_rows | products* | catalog | optional |
| GET | `/api/v1/store` | store_api_rows | products* | store | `catalog-service.js` |
| GET | `/api/v1/store/{id}` | store row | products* | product | optional |
| POST | `/api/v1/analyze` | generate_reproducible_report | all clinical | analyze | legacy/alternate |
| POST | `/api/v1/clinical-report` | analyze + reports + assessment | all | report envelope | **`app.js`** |
| POST | `/api/v1/ppie/assess` | ClinicalAssessment | all | assessment | API clients |
| POST | `/api/v2/wellness/evaluate` | agent report | all | wellness | alternate |
| POST | `/api/v1/ppie/trace` | EngineTrace | analyze | trace | debug |
| POST | `/api/v1/ppie/validation-console` | build_validation_console | all | console v7 | **Developer Report** |
| POST | `…/markdown` | console_to_markdown | — | text | export |
| POST | `…/compare` | compare_analyses | — | diff | console (legacy compare) |
| GET | `/api/v1/ppie/debug/*` | status/presets/repo | platform | meta | console |
| GET | `/api/v1/evidence/{c}` | evidence helper | evidence CSVs | list | optional |
| GET | `/api/v1/products/{c}` | products helper | catalog | list | optional |
| POST | `/api/recommendations` | map_legacy_response | analyze | legacy | optional |
| * | groomer routes | in-memory sessions | — | session | optional |
| GET | `/` | FileResponse | — | index.html | demo |
| GET | `/debug/calculation` | FileResponse | — | calculation.html | **dev report** |

Auth: `x-api-key: wagtopia-demo-key` on most POST APIs.  
Debug routes: `PPIE_DEBUG` or `?debug=1`.

---

## 5. UI analysis

### 5.1 Demo (`index.html`)

| Item | Detail |
|------|--------|
| Endpoint | `POST /api/v1/clinical-report` (+ store) |
| Objects | `analyze`, `standard_report` / clinical report, assessment modules |
| Order | Catalog load → report fetch → shell mount → widgets |
| Traceability | Weak in customer UI; EngineTrace only with debug payload |
| Duplicate risk | Report widgets vs shell cards can overlap narrative |

### 5.2 Developer Report (`debug/calculation.html`)

| Item | Detail |
|------|--------|
| Endpoint | `POST /api/v1/ppie/validation-console?debug=1` |
| Shape | `validation_console.v7` — **single page**, sections 0–15 |
| Objects | `formula_executions`, lookups, modifiers, packages, raw objects, gaps |
| TOC | In-page anchors only (not separate feature tabs) |
| Honesty | Missing instrumentation = `NOT CURRENTLY TRACEABLE` inline |

### 5.3 Streamlit (`app/ui`)

| Item | Detail |
|------|--------|
| Entry | `streamlit run app/ui/demo_app.py` |
| Templates | journey, wellness, diary, components |
| Note | Parallel UX; not the FastAPI static path |

---

## 6. Data folder audit

### Layout

```
data/
├── manifest.yaml
├── README.md
├── breed_analysis/
│   ├── 1_biological_traits/     BREEDS, aliases, mixed matrices
│   ├── 2_evolutionary_profiles/ purposes, environment, explanations
│   ├── 3_management_considerations/ breed/trait condition prevalences, interactions, weights, timeline
│   ├── 4_preventative_interventions/ activities, benefits, grooming, prescription rules
│   └── 5_scientific_nutrition/  condition ingredients, evidence, mechanisms, priorities, aliases
├── preventative_ingredients/    parallel CONDITION_INGREDIENTS + EVIDENCE + PROTOCOLS
└── product_portfolio/           catalog, pricing, components, feeding, functions, tiers, EXT_*
```

### Manifested vs disk

| | Count |
|--|------:|
| CSV on disk | 47 |
| Manifested | 45 |
| Unmanifested | **2** — `STAPLE_FOOD.csv`, `TREATS.csv` |

### Consumer summary (high signal)

| CSV / table | Used by | Formula |
|-------------|---------|---------|
| `BREEDS` | biological, health_risk | BREED / TRAIT / RISK |
| `BREED_ALIASES` | biological | BREED |
| `*_CONDITIONS` (9 files) | health_risk, epidemiology | RISK |
| `BREED_CONDITIONS` | health_risk significance | RISK |
| `TRAIT_INTERACTIONS` | health_risk | RISK |
| `TRAIT_BENEFITS` | health_risk | RISK |
| `MIXED_BREED_MATRIX` | health_risk | RISK |
| `MIXED_BREED_INTERACTIONS` | **loaded, unused** | — |
| `CONDITION_INGREDIENTS` (sci+prev) | ingredient_engine, nutrition stage | NUTRIENT |
| `INGREDIENT_EVIDENCE*` | ingredient_engine, assembler | EVIDENCE |
| `PRODUCT_*` | optimizer, catalog/store | PRODUCT / PACKAGE |
| `PACKAGE_TIERS` | package_optimizer | PACKAGE |
| `ACTIVITY_*` | response_assembler | ACTIVITY |
| `ACTIVITY_EVIDENCE` | **unused** | — |
| `CONDITION_PROTOCOLS` | **unused** | — |
| `PRODUCT_DEFAULTS` | **loaded, unused in selection** | — |
| `TRAIT_CONTRIBUTION_WEIGHTS` | limited / reportish | — |
| `CLINICAL_RISK_TIMELINE` | reports | — |
| Dual `CONDITION_INGREDIENTS` / evidence homes | sci ∪ prev merge | NUTRIENT |

### Structural issues (for Phase 1+)

1. **9 isomorphic trait prevalence files** → normalize to `trait_conditions`
2. **Dual nutrition homes** (breed_analysis/5 vs preventative_ingredients)
3. **Evidence scattered** across clinical_evidence_base, ingredient_evidence×2, activity_evidence
4. **No papers master table** — citations inline on rows
5. **Units mixed** in CSV text fields; conversion ad hoc in Python
6. **Formulas absent from CSV** (correct) but **constants in Python** (`config.py`) blur “science vs algorithm”

Full column dictionaries already drafted in `docs/DATA_DICTIONARY.md` / `DATA_ARCHITECTURE_V2.md`.

---

## 7. Runtime trace (one assessment)

Example: Dolly — Golden Retriever × Labrador, adult, high activity.

```
POST /api/v1/ppie/validation-console?debug=1
  (or POST /api/v1/clinical-report)
        │
        ▼
profile_from_analyze_body          PROFILE_NORMALIZE_V2_1
        │
        ▼
PPIEWellnessAgent.generate_reproducible_report
        │
        ├─1 biology ────────────── BREEDS, aliases, trait_purposes, environmental_matrices
        │                            BREED_RESOLVE_V2_1, TRAIT_BLEND_V2_1
        │
        ├─2 health_risk ────────── trait_*_conditions, interactions, benefits,
        │                            mixed_breed_matrix, breed_conditions
        │                            RISK_V2_1 + formula_execution ledger
        │
        ├─3 epidemiology ───────── (runs) then priorities ← health_risk risks
        │
        ├─4 management ─────────── condition_activities
        │
        ├─5 nutrition stage ────── condition_ingredients (join only)
        │
        ├─6 optimization stage ─── products / components / pricing / feeding
        │
        └─7 assembly ───────────── map_ingredients (NUTRIENT_TARGET_V2_1)
                                   build_optimized_packages (PACKAGE_OPTIMIZER_V2_1)
                                   healthInsights, evidence, activities, traces
                                   analyze.debug (formula_executions, timings)
        │
        ▼
build_clinical_assessment / reports (if clinical-report / assess)
        │
        ▼
JSON → index.html shell  OR  validation_console.v7 → Developer Report UI
```

**Every function call of interest (assembly path):**

`profile_from_analyze_body` → `run_biological_stage` → `compute_risks` → `run_epidemiology_stage` → `_run_management_stage` → `run_nutrition_stage` → `run_optimization_stage` → `assemble_frontend_response` → `map_ingredients` → `build_optimized_packages` → `build_health_insights` → `collect_evidence` → `build_calculation_trace` → (`build_clinical_assessment`) → (`build_validation_console`)

---

## 8. Duplicate logic & dead-code estimate

| Area | Issue | Estimate |
|------|-------|----------|
| Epidemiology vs health_risk | Dual prevalence paths; health_risk wins | Medium debt |
| Nutrition stage vs map_ingredients | Stage join + assembler remap | Medium |
| Optimization stage vs package_optimizer | Stage products vs tier optimizer | Medium |
| Dual CONDITION_INGREDIENTS | sci ∪ prev merge | Data debt |
| 9 trait condition CSVs | Isomorphic schema | Data debt |
| Streamlit vs static demo | Two UIs | Product choice |
| Unused tables | mixed_breed_interactions, activity_evidence, condition_protocols, product_defaults | ~4 tables |
| Opt-in inference formulas | EST / FRAC / CONF / SUPPORT | Test-only surface |
| Unmanifested STAPLE_FOOD / TREATS | Orphan files | Wire or archive |

**Rough dead-code estimate:** ~10–15% of data tables unused; ~20% of `app/ui` unused by FastAPI path; epidemiology priority path partially dead; inference opt-ins unused in production analyze.

---

## 9. Output objects (contracts)

| Object | Producer | Consumers |
|--------|----------|-----------|
| `analyze` (frontend envelope) | response_assembler | app.js, assess, console |
| `healthInsights[]` | assembler from risks | UI, nutrition |
| `nutritionalTargets[]` | build_nutritional_targets | UI, packages |
| `wellnessPackages[]` | package_optimizer + detail | UI |
| `calculationTrace` | calculation_trace | UI / console |
| `debug.formula_executions` | health_risk / ingredients / packages | Developer Report |
| `ClinicalAssessment` | clinical_assessment | `/ppie/assess` |
| Clinical / standard report | report builders | `/clinical-report` |
| `validation_console.v7` | validation_console | Developer Report page |

---

## 10. Living documentation map

| Doc | Role |
|-----|------|
| `README.md` | Boot / overview |
| `docs/DEBUGGING.md` | Developer Report |
| `docs/DATA_*.md` | Warehouse planning (V2) |
| `docs/FORMULAS.md` / `BACKEND_ARCHITECTURE.md` / `API.md` | Living references (if present) |
| **`PROJECT_ARCHITECTURE.md` (this file)** | Phase 0 audit baseline |

---

## 11. Phase 0 conclusions (inputs to later phases)

### Keep as-is (do not casually rewrite)

- `RISK_V2_1` math in `health_risk.py`
- `map_ingredients` / dose rules
- `build_optimized_packages` selection behavior
- Manifest-driven `DataPlatform` pattern
- Algorithm version `2.1.0` parity suite

### Must fix in future architecture (Phases 1–6)

1. **Normalized scientific warehouse** (breeds / traits / conditions / papers / evidence rows) — see user Phase 1 schema
2. **Single assessment agent orchestrator** — engines must not call each other ad hoc
3. **Unit conversion layer** — canonical mg, kg, mg/kg/day
4. **Papers master + one-row-one-study evidence**
5. **Retire unused tables / dual nutrition homes after migration**
6. **Developer Report** already single-page — extend with papers/unit conversion when warehouse lands

### Explicit Phase 0 commitment

> **No code rewritten. No CSV deleted. No warehouse created yet.**  
> Implementation of Phases 1–6 begins only after stakeholder acceptance of this audit.

---

## 12. Proposed next steps (not executed)

| Phase | Deliverable |
|-------|-------------|
| 1 | New `data/reference|science|runtime|generated/` skeleton + empty schemas (parallel to current `data/`) |
| 2 | `unit_conversion.csv` + converter module |
| 3 | Engine module split (`risk_engine.py`, …) wrapping current math with full traces |
| 4 | `assessment_agent.py` orchestration |
| 5 | Extend Developer Report sections for papers / units / prevention |
| 6 | `DATA_MIGRATION_REPORT.md` + parity gates before archive |

---

## Appendix A — Quick inventory counts

| Kind | Count |
|------|------:|
| Python modules under `app/` | ~71 |
| Root + debug JS (major) | ~10 |
| HTML entry pages | 2 (+ Jinja many) |
| CSV files | 47 |
| Manifested tables | 45 |
| Formula registry IDs | 17 |
| FastAPI route groups | ~20+ |
| Pytest modules | 11 |

## Appendix B — Absolute entry commands

```bash
# API + static demo
py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Developer Report
# open http://127.0.0.1:8000/debug/calculation?debug=1

# Streamlit (secondary)
streamlit run app/ui/demo_app.py

# Tests
py -3 -m pytest tests/ -q
```

---

*End of Phase 0 audit.*
