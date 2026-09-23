# Ω10 Repository Audit Report

Generated 2026-09-03. This is an audit of what currently executes. It is not a second architecture specification. Authoritative behavior: [WAGGY_SYSTEM.md](WAGGY_SYSTEM.md).

## Runtime architecture

What actually executes:

```
warehouse CSVs (+ optional WAGTOPIA_DEMO_MODE catalog overlay)
  → DataRepository (app/data/repository.py, loader.py, warehouse_biology.py)
  → PPIEWellnessAgent / FormulaGraph (app/agent/)
  → scientific_care.resolve_care_model (warehouse biology / prevention only)
  → PACKAGE_OPTIMIZER_V2_1 (app/agent/package_search.py; exhaustive 2^N−1)
  → presentation adapter (app/presentation/adapter.py)
  → FastAPI (app/api/main.py)
  → waggy-frontend at GET /
```

Ω17.4-FE moved the active workbench from `legacy/workbench.*` into copyable `waggy-frontend/`. This audit snapshot is otherwise unchanged.

There is one analysis execution path. Role switching calls `POST /api/v1/presentation/workbench` once and projects Customer / Groomer / Business / Developer from the same canonical result.

`PACKAGE_OPTIMIZER_V2_1` is the only package composer. The frontend does not enumerate combinations, calculate nutrients, or choose SKUs.

Historical Electron / PPie / workbench-classic files are archived in `legacy/archive/frontend/`. `GET /classic`, `/business`, and `/developer` now load the same workbench. They are not a second optimizer.

## Warehouse architecture

Canonical scientific / commercial facts:

| Path | Role | Rows (data) |
|---|---|---|
| `warehouse/biology/breeds.csv` | Breed identity | 48 |
| `warehouse/biology/breed_traits.csv` | Phenotype traits | 432 |
| `warehouse/biology/observed_breed_conditions.csv` | Cited breed–condition prevalence | 16 |
| `warehouse/biology/trait_condition_associations.csv` | Cited trait–condition links | 90 |
| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | Mixed-breed rows requiring validation | 10 |
| `warehouse/prevention/condition_ingredients.csv` | Condition → ingredient / nutrient | 12 |
| `warehouse/reference/papers.csv` | Paper identity | 199 |
| `warehouse/commercial/product_master.csv` | Product identity / names | 16 |
| `warehouse/commercial/product_functions_NEEDS_VALIDATION.csv` | Functions requiring validation | 10 |
| `warehouse/commercial/product_feeding_guide.csv` | Feeding records | 23 |

`warehouse/recovery_original/` is read-only intern recovery material. Mapping: 719 rows; 248 `NEEDS_VALIDATION`; 471 `MISSING_PROVENANCE`; 0 `CONFLICT_REQUIRES_VALIDATION`.

`warehouse/science/` is not the Health Analysis path. `warehouse/current/` has no clinical CSVs; it is a placeholder README.

## Data sources

| Dataset | Classification |
|---|---|
| `warehouse/biology/observed_breed_conditions.csv` | Scientific (intern cited prevalence) |
| `warehouse/biology/trait_condition_associations.csv` | Scientific (intern cited associations) |
| `warehouse/prevention/condition_ingredients.csv` | Scientific (intern cited ingredient links) |
| `warehouse/reference/papers.csv` | Scientific (paper identity) |
| `warehouse/biology/breeds.csv` | Identity (some `MISSING_PROVENANCE`) |
| `warehouse/biology/breed_traits.csv` | Recovered phenotype; 432 `MISSING_PROVENANCE` — surface, do not fill |
| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | Validation-required |
| `warehouse/commercial/product_master.csv` | Recovered commercial identity |
| `warehouse/commercial/product_functions_NEEDS_VALIDATION.csv` | Validation-required commercial |
| `warehouse/commercial/product_feeding_guide.csv` | Recovered commercial feeding |
| `app/data/demo_catalog.py` | Demo-only commercial overlay |
| `app/data/demo_scientific_dataset.py` | Synthetic product densities for demo optimizer math |
| `app/data/demo_breed_care.py` | Obsolete; retired stub, not imported |
| `app/data/scientific_requirements.py` | Secondary AAFCO-style summary, not primary AAFCO |
| `warehouse/recovery_original/` | Recovered intern originals (read-only) |

## Documentation inventory

### KEEP

| File | Reason |
|---|---|
| `docs/WAGGY_SYSTEM.md` | Authoritative master document |
| `docs/WAGTOPIA_SYSTEM_ARCHITECTURE.md` | Stable alias |
| `docs/WAGTOPIA_SYSTEM_SPEC.md` | Stable alias |
| `docs/README.md` | Docs index |
| `docs/CONTRIBUTING.md` | Active contributor rules |
| `docs/DATA.md` | Pointer used by warehouse READMEs |
| `docs/validation_report.md` | Generated warehouse QA (8 FK blockers) |
| `docs/AUDIT_REPORT.md` | This Ω10 audit |
| `docs/architecture/*.csv` | Test inventories |
| `docs/mathematics/*.csv` | MAT test inventories |
| `docs/interface/*.csv` | Claim-coverage tests |
| `README.md`, `legacy/README.md`, `repository/README.md`, `warehouse/README.md` | Entry / layer pointers |
| `repository/**/FORMULA_REGISTRY.md` | Formula-layer catalogs used by validators |
| `warehouse/recovery_original/**` | Protected recovery evidence |

### MERGE

Useful content from prior architecture / Ω / recovery markdown is now in `docs/WAGGY_SYSTEM.md`. Overlapping `.md` files were already removed from the working tree before Ω10 doc cleanup, except recovery reports.

### ARCHIVE

| File | Reason |
|---|---|
| `docs/archive/DATA_RECOVERY_REPORT.md` | Recovery provenance, not active runtime contract |
| `docs/archive/DATA_RECOVERY_INVENTORY.md` | Recovery inventory |
| `docs/archive/architecture/TARGET_FILE_TREE.txt` | Historical tree note |
| `legacy/docs/` | Pre-existing historical markdown |
| `legacy/archive/` | Pre-cutover trees |

### DELETE

No scientific CSVs or recovery blobs were deleted. No second pass over intern evidence.

## Runtime dependency inventory

| Component | Status |
|---|---|
| `app/data/scientific_care.py` | Active Health Analysis |
| `app/data/warehouse_biology.py` | Active loader merge |
| `app/agent/package_search.py` | Sole optimizer |
| `app/data/demo_scientific_dataset.py` | Active demo densities only |
| `app/data/demo_catalog.py` | Active demo overlay |
| `app/data/demo_breed_care.py` | Dead; raises if called |
| `waggy-frontend/` | Active unified UI (Ω17.4-FE) |
| `legacy/workbench.*` | Removed; replaced by `waggy-frontend/` |
| `legacy/archive/frontend/` | Archived classic/business/phone-shell UIs (reference) |
| `legacy/debug/calculation.html` | Internal Clinical Execution Explorer |
| `legacy/archive/omega9.6b/` | Isolated historical snapshot |
| `repository/optimization/` | MAT helpers, not customer SKU composer |

No production import points back into `legacy/archive/` or `demo_breed_care` care-model data.

## Synthetic-data inventory

| Component | Necessary? |
|---|---|
| Demo catalog products / prices | Yes, while `WAGTOPIA_DEMO_MODE` is the demo commercial overlay |
| Demo dry-matter densities | Yes, for exhaustive optimizer math in demo mode |
| Demo synthetic breed-care pathways | **No. Retired.** |
| Hardcoded Labrador/Golden joint/skin as science | **No. Removed from runtime.** |

## Test inventory

| Suite | Verifies |
|---|---|
| `tests/interface/test_omega10_warehouse_health.py` | Warehouse Health Analysis, no demo fallback, modal, role `bundle_id` identity |
| `tests/interface/test_exhaustive_nutrient_optimizer.py` | 2^N−1, min/max reject, breed changes Balanced not Essential minima |
| `tests/interface/test_omega910_bundle_reasoning.py` | Product names, ledger, ranking, nutrition modal copy |
| `tests/interface/test_bundle_*` | Tiers, budget, display options, comparison |
| `tests/optimization/` | Exhaustive ranking determinism |
| `tests/mathematics/`, `tests/math_debugger/`, `tests/formulas/` | MAT stack, not package membership |
| `tests/architecture/` | One engine, presentation boundary, spec tokens |
| `tests/warehouse_qa/`, `tests/science_graph/` | Warehouse QA / historical graph (skipped unless `warehouse/current` CSVs exist) |
| `tests/test_*.py` listed in `tests/conftest.py` | Historical DataPlatform projection; skipped without `warehouse/current/product_portfolio` |

## Known limitations (do not “fix” by invention)

- 432 phenotype traits have `MISSING_PROVENANCE`.
- Mixed-breed / life-stage / size-risk intern material remains `NEEDS_VALIDATION`.
- 248 mapping rows `NEEDS_VALIDATION`; 471 `MISSING_PROVENANCE`.
- 8 warehouse FK blockers in `docs/validation_report.md` (legacy `COND_*` / `ING_*` IDs).
- Zinc is currently the only modeled star nutrient mapped from warehouse ingredients.
- Demo product densities are synthetic commercial math.
- MAT mixed-breed path still uses `profile.breeds[0]`; Health Analysis loads observed rows for every resolved breed name.
