# Backend architecture

Current map of the PPIE Python backend. Update this file when routes, stages, or ownership change.

**Runtime:** Python 3 · FastAPI · CSV via `data/manifest.yaml`  
**Not used at runtime:** Supabase / PostgreSQL

---

## System shape

```text
Frontend (demo) / Wagtopia host
        │
        ▼
FastAPI  app.api.main
        │  x-api-key · timing · optional PPIE_DEBUG
        ▼
payload_adapter  (profile_from_analyze_body)
        │
        ▼
PPIEWellnessAgent.generate_reproducible_report
        │
        ├─ biological
        ├─ health_risk          ← primary condition ranking
        ├─ epidemiology         ← CSV enrich (priorities often overwritten)
        ├─ management
        ├─ nutrition
        └─ optimization + package_optimizer
        │
        ▼
response_assembler
        │
        ├─ ClinicalAssessment     [assess]
        ├─ EngineTrace / Console  [debug only]
        └─ clinical report blobs  [demo / transitional]
        │
        ▼
JSON
```

**Data plane:**

```text
data/manifest.yaml → loader → DataPlatform (in-memory) → DataRepository → stages
```

---

## Request lifecycle

1. CORS + timing middleware  
2. API key (`x-api-key` ∈ `API_KEYS`) on protected routes  
3. Body → normalized dog profile  
4. Breed resolve (aliases → breed rows)  
5. Trait blend  
6. Risk / condition ranking (`RISK_V2_1`)  
7. Evidence + ingredient mapping  
8. Nutrition targets  
9. Product match + package optimize  
10. Assemble response (+ optional assessment / debug)

Formula IDs per stage: [FORMULAS.md](FORMULAS.md). Endpoints: [API.md](API.md).

---

## Module ownership

| Area | Path | Role |
|------|------|------|
| Orchestrator | `app/agent/engine.py` | Stage order, reproducible report |
| Biological | `app/agent/stages/biological.py` | Breed + traits |
| Health risk | `app/agent/stages/health_risk.py` | Primary ranking (`RISK_V2_1`) |
| Epidemiology | `app/agent/stages/epidemiology.py` | CSV multipliers / enrich |
| Nutrition | `app/agent/stages/nutrition.py` | Targets |
| Optimization | `app/agent/stages/optimization.py` | Product path into optimizer |
| Package optimizer | `app/agent/package_optimizer.py` | `PACKAGE_OPTIMIZER_V2_1` |
| Assembler | `app/agent/response_assembler.py` | Analyze envelope |
| Inference helpers | `app/inference/` | Registry, opt-in formulas, constants |
| Repository | `app/data/repository.py` | CSV queries — **no clinical math** |
| Assessment | `app/data/clinical_assessment.py` | Projection only |
| Debug | `app/data/engine_trace.py`, `validation_console.py` | Observability |

---

## Pipeline stages (execution order)

| # | Stage | Formula IDs | Notes |
|---|--------|-------------|--------|
| 1 | Profile normalize | `PROFILE_NORMALIZE_V2_1` | Adapter |
| 2 | Breed | `BREED_RESOLVE_V2_1` | Aliases + `BREEDS.csv` |
| 3 | Traits | `TRAIT_BLEND_V2_1` | Mixed-breed blend |
| 4 | Risk | `RISK_V2_1` | Locked parity path |
| 5 | Nutrition | `NUTRIENT_TARGET_V2_1` | Condition → targets |
| 6 | Activity / grooming | `ACTIVITY_V2_1` | Prescription rules |
| 7 | Evidence | `EVIDENCE_RANK_V2_1` | Attach papers |
| 8 | Products | `PRODUCT_MATCH_V2_1` | Catalog match |
| 9 | Coverage | `COVERAGE_V2_1` | provided / recommended |
| 10 | Packages | `PACKAGE_OPTIMIZER_V2_1` | Tier packages |
| 11 | Validation slots | `VALIDATION_V2_1` | Benchmarks when present |
| 12 | Assessment | `ASSESSMENT_PROJECT_V1` | **Never recomputes** |

Projections (ClinicalAssessment, EngineTrace, Validation Console) consume frozen analyze — they are not a second engine.

---

## Ownership matrix

| Class | Examples | Policy |
|-------|----------|--------|
| **LOCKED** | `app/agent/**` stages, package_optimizer, repository loaders, golden/parity tests, clinical_assessment projection rules | Algorithm bump + tests |
| **SEMI** | API routes, payload adapter, Layer B copy, clinical_report_builder | Careful; prefer assess contract |
| **REPLACEABLE** | Demo JS/CSS, Streamlit, archive | Wagtopia / local demo |

**Layer decision tree**

- Number, ranking, coverage, score → Layer A  
- Wording only → Layer B  
- Layout, commerce, CRM → Layer C  
- Catalog price / SKU / dog SoR → Wagtopia data (not PPIE formulas)

**Anti-patterns:** frontend recalculating coverage; hardcoding product IDs in formulas; parsing % from prose; treating saved reports as live truth; showing CSV filenames in production UI.

---

## Dual paths (current debt)

| Topic | Reality |
|-------|---------|
| Risk | `health_risk` ranks; epidemiology may enrich — do not assume one path only |
| Nutrition vs packages | Nutrition stage sets targets; optimizer builds coverage matrix |
| Response shapes | Preferred `ClinicalAssessment`; demo still uses analyze / clinical-report megadicts |
| Inference package | `app/inference/` helpers exist; several formulas are `enabled=False` (not production-wired) |

---

## Code-owned constants (intentional)

After data simplification, these live in Python (not CSV):

- `CATEGORY_WEIGHTS`, `SCORE_WEIGHTS`, `NUTRIENT_CATALOG`, `INGREDIENT_ORDER_PERCENTS`
- `GROOMER_MAP`, wellness / goal maps
- Confidence ladder logic in `app/inference/confidence.py`

Scientific facts stay in `data/`. See [DATA.md](DATA.md).

---

## Auth gaps (know before public expose)

Protected by API key in typical assess/analyze paths. Gaps historically include some wellness evaluate variants, groomer submit, breeds list, `/health`, and static assets — treat public exposure carefully. Details: [API.md](API.md).

---

## Version axes

| Axis | Source of truth | Bump when |
|------|-----------------|-----------|
| Algorithm | `app/agent/version.py` | Formula / ranking changes |
| Data | `data/manifest.yaml` `version` + content hash | CSV science/catalog changes |
| Presentation | Report schema labels | UI / module layout only |

Never conflate the three. Persist DogProfile; re-assess for live care — do not treat old report JSON as truth.

---

## Related

- [FORMULAS.md](FORMULAS.md) · [DATA.md](DATA.md) · [API.md](API.md) · [DEBUGGING.md](DEBUGGING.md)
