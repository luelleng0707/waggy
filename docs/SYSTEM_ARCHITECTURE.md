# SYSTEM_ARCHITECTURE.md

One architecture. One execution path. One scientific warehouse.

## Overview

```
DogProfile → Validation → Repository → FormulaGraph → AssessmentResult → API → Demo UI
```

PPIE is a **clinical calculation engine**. Wagtopia owns product experience; this repo owns deterministic science → assessment.

---

## Warehouse

Canonical scientific database under `warehouse/`:

| Layer | Contents |
|-------|----------|
| `reference/` | Entities: breeds, conditions, traits, ingredients, products, papers, foods, activities, life_stages |
| `science/` | Relationships + operational facts (risk tables, products ops, nutrition facts) |
| `runtime/` | aliases, parameters, units |

CSV is a **storage format**. Entities and relationships are the model.

---

## Repository

**Owner of all data access.**

| Interface | Role |
|-----------|------|
| `DataPlatform` / `DataRepository` (`app/data/`) | Loads warehouse; builds **in-memory** formula views; typed accessors for stages |
| `ScientificRepository` (`warehouse/repository/`) | Entity/relationship objects (`get_breed`, `get_condition_relationship`, …) |
| `native_loader` | Joins reference/science/runtime → formula DataFrames (never written to disk) |

FormulaGraph must not open CSV files.

---

## Formula engine

| Piece | Location |
|-------|----------|
| FormulaGraph + nodes | `app/agent/` |
| Clinical stages | `app/formulas/stages/` |
| AssessmentAgent | `app/agent/assessment_agent.py` |

**Responsibility:** calculation only (risk, nutrition, products, packages).  
**Not responsible:** loading CSVs, joins across warehouse files, persistence.

---

## AssessmentResult

Typed result from `AssessmentAgent.assess()` → serialized to analyze JSON for API / demo UI.

Includes health insights, wellness packages, nutritional targets, debug/trace (volatile).

---

## API

`app/api/` + `app/main.py` (uvicorn).

Primary clinical routes: assess / clinical-report / ppie.  
Also: catalog, authoring (tooling), platform status (tooling).

Auth: `x-api-key` (demo key configurable).

---

## Frontend contract

Demo only: `index.html` + root `*.js` / CSS, plus Streamlit under `app/ui/`.

Contract: **DogProfile in → ClinicalAssessment JSON out**.  
Replaceable by Wagtopia clients without changing formulas.

---

## Supporting packages (scientific authoring — not FormulaGraph)

| Package | Role |
|---------|------|
| `authoring/`, `curation/`, `ontology/` | Evidence staging + ontology |
| `science_pipeline/` | Validate / publish science |

These must never change clinical math silently.
