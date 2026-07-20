# Changelog

Chronological record of meaningful backend and docs changes. Prefer short entries.

---

## 2026-07 — Data normalization planning pack

- Added DATA_ARCHITECTURE_V2, DATA_DICTIONARY, DATA_CONSUMERS, DATA_RELATIONSHIPS, DATA_DUPLICATION_REPORT, DATA_NORMALIZATION, DATA_MIGRATION_V2.  
- Planning only — no CSV moves, no clinical changes.

---

## 2026-07 — Full Backend Observatory (Validation Console v3)

- Production emits `analyze.debug` risk traces + stage timings; packages expose full reject lists.  
- Console schema `validation_console.v3`: formula explorer, code/CSV maps, reverse lookup, observability coverage %, nutrition math projection, raw production objects.  
- No clinical math changes; equation text still not exposed.

---

## 2026-07 — Data architecture review (column-level)

- Added [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md): full inventory of 47 live CSVs, column ownership, duplication, merge matrix, target 16–18 domain files. Design only — no migration yet.

---

## 2026-07 — Documentation consolidation

- Collapsed fragmented docs into eight living files: README, BACKEND_ARCHITECTURE, FORMULAS, DATA, API, DEBUGGING, ROADMAP, CHANGELOG.  
- Removed phase diaries and migration notes from `docs/` (git history + `archive/docs/` retain them).

---

## 2026-07 — Validation Console formula inspector

- `validation_console.v2` with Formula Ledger, dependency graph, expanded risk chain slots, nutrition/products/packages/evidence inspectors.  
- Central `FORMULA_REGISTRY` in `app/inference/formula_registry.py`.  
- Observability only; clinical outputs unchanged. Honest `NOT CURRENTLY TRACEABLE` gaps documented in DEBUGGING.

---

## 2026-07 — Data simplification

- Removed algorithmic `data/inference/` CSVs.  
- Algorithms/weights/ladders/goal maps live in Python.  
- Scientific nutrient estimates under `5_scientific_nutrition/INGREDIENT_NUTRIENT_ESTIMATES.csv`.  
- Parity preserved for `RISK_V2_1`, package optimizer, nutrition targets.

---

## 2026-07 — Inference package

- Added `app/inference/` helpers (resolver, confidence, opt-in F1/F2/F5, registry).  
- Opt-in formulas remain `enabled=False` until approved.

---

## 2026 — Live Validation Console & EngineTrace

- Debug-gated Validation Console (presets, compare, repository browser, Dev menu).  
- EngineTrace with formula IDs and consistency checks.  
- Preferred API path: `POST /api/v1/ppie/assess` → ClinicalAssessment.

---

## 2026 — Repository audit & archive

- Historical docs/assets moved under `archive/` where appropriate.  
- Production path clarified as Python FastAPI + CSV manifest (not Supabase).

---

## Earlier

Shop UI removal from demo shell; ClinicalAssessment as preferred contract; demo still transitional via clinical-report where needed. See `archive/docs/` for older phase write-ups.
