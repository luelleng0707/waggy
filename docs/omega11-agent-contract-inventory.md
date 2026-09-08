# Ω11 Agent Contract Inventory

Date: 2026-09-06.
Schema version: `1.0.0` (`AGENT_CONTRACT_SCHEMA_VERSION`).
Engine version reused: `ALGORITHM_VERSION = 2.1.0`.

---

## A. Existing reused contracts

| Name | File | Purpose | Owner | Consumers | Source of truth | Version | Status |
|---|---|---|---|---|---|---|---|
| `DogProfileInput` | `app/agent/state.py` | Engine/API dog input | Engine | PPIE, evaluate route, payload adapter | User/application payload | Engine 2.1.0 | REUSED UNCHANGED |
| `ALGORITHM_VERSION` / `ENGINE_NAME` | `app/agent/version.py` | Engine identity | Engine | Headers, analyze `version`, Ω11 `VersionStamp` | `app/agent/version.py` | 2.1.0 / PPIE | REUSED UNCHANGED |
| `DataRepository.version` / `csv_hash` | `app/data/repository.py`, `app/data/cache.py` | Warehouse identity | Data platform | HTTP headers, science versions | Loaded CSVs + manifest | runtime | REUSED (referenced, not copied) |
| Warehouse fact/paper columns | `warehouse/biology/observed_breed_conditions.csv`, `warehouse/reference/papers.csv` | Evidence/fact field names | Science | scientific_care, Ω11 evidence models | Warehouse CSVs | warehouse runtime | FIELD NAMES REUSED |
| careModel / requirementProfile / packageOptions | `app/data/scientific_care.py`, `scientific_requirements.py`, `package_search.py` | Capability payloads | Engine | Assembler, future adapters | Deterministic engine | 2.1.0 | REUSED VIA ADAPTERS ONLY |
| Status tokens | scientific_care / warehouse | `NOT_AVAILABLE`, `NEEDS_VALIDATION`, `MISSING_PROVENANCE`, `WAREHOUSE_EVIDENCE`, `migrated`, `NOT_MODELED` | Science / engine | Health Analysis, Ω11 enums | Warehouse + engine | existing | REUSED |
| `correlation_id` | workbench API | Invocation correlation | Application | Workbench | Request header/body | existing | REUSED AS OPTIONAL ID |
| `dog_id` convention | `repository/models/runtime.py` | `DOG::{name.lower()}` | Repository | Architecture tests | Convention (unstable) | existing | DOCUMENTED GAP |
| Authoring schema ids | `app/api/main.py` | `authoring_*.v1` | Science team | Authoring routes | Staging drafts | v1 | EXCLUDED FROM AGENT SURFACE |

---

## B. New contracts

| Name | File | Purpose | Owner | Consumers | Source of truth | Version | Status |
|---|---|---|---|---|---|---|---|
| `FieldValue` / `CanonicalDogInput` | `app/contracts/agent/input.py` | Agent dog input with presence states | Contract layer | Future tools, tests | User | schema 1.0.0 | NEW |
| `Observation` | `app/contracts/agent/observations.py` | Typed observation | Groomer/customer | Future tools | Observer | schema 1.0.0 | NEW |
| `ScientificEvidence` / `ScientificFact` | `app/contracts/agent/evidence.py` | Evidence + fact | Science | Future tools | Warehouse | schema 1.0.0 | NEW |
| `ScientificInference` / `PrevalenceValue` | `app/contracts/agent/inference.py` | Derived reasoning shape | Engine (data only) | Health contract | Engine output | schema 1.0.0 | NEW |
| `ProductRecord` / `BusinessConfiguration` | `app/contracts/agent/products.py` | Product vs commercial config | Catalog / business | Future optimize_bundles | Catalog / policy | schema 1.0.0 | NEW |
| `HealthAnalysisResult` | `app/contracts/agent/health.py` | Future `analyze_health` | Engine derived | Ω13 | careModel via adapter | schema 1.0.0 | NEW |
| `NutritionAnalysisResult` | `app/contracts/agent/nutrition.py` | Future `calculate_nutrition` | Engine derived | Ω13 | requirementProfile via adapter | schema 1.0.0 | NEW |
| `BundleSearchResult` | `app/contracts/agent/bundles.py` | Future `optimize_bundles` | Optimizer derived | Ω13 | package_search via adapter | schema 1.0.0 | NEW |
| `CanonicalAnalysis` | `app/contracts/agent/analysis.py` | One-run envelope | Engine derived | Future tools | Combined slices | schema 1.0.0 | NEW |
| `ReportProjection` | `app/contracts/agent/report.py` | Future `generate_report` projection stub | Presentation | Ω13 | Existing report builders | schema 1.0.0 | NEW |
| `ProvenanceRecord` | `app/contracts/agent/provenance.py` | Shared provenance | Shared | All derived contracts | Warehouse + engine versions | schema 1.0.0 | NEW |
| `VersionStamp` | `app/contracts/agent/versions.py` | engine/warehouse/schema/tool | Shared | All results | `ALGORITHM_VERSION` + repo version | schema 1.0.0 | NEW |
| `ToolError` | `app/contracts/agent/errors.py` | Typed tool errors | Contract layer | Future tools | Boundary | schema 1.0.0 | NEW |
| `AgentContext` | `app/contracts/agent/context.py` | Bounded actor context | Authorization (future) | Future agent host | Session/auth | schema 1.0.0 | NEW |
| `ToolRegistryEntry` | `app/contracts/agent/registry.py` | Future registry (no execute) | Contract layer | Ω13 | This file | tool 1.0.0 | NEW |
| `TraceabilityIds` | `app/contracts/agent/ids.py` | ID bag | Shared | Analysis envelope | Existing IDs | schema 1.0.0 | NEW |

---

## C. Adapter contracts

| Name | File | Purpose | Owner | Consumers | Source of truth | Version | Status |
|---|---|---|---|---|---|---|---|
| `canonical_dog_from_engine` | `app/contracts/agent/adapters.py` | `DogProfileInput` → canonical | Contract | Tests; future Ω13 | Engine profile | schema 1.0.0 | NEW ADAPTER |
| `engine_profile_from_canonical` | same | Canonical → engine; **no silent defaults** | Contract | Tests; future Ω13 | Canonical input | schema 1.0.0 | NEW ADAPTER |
| `health_from_care_model` | same | careModel dict → `HealthAnalysisResult` | Contract | Tests; future Ω13 | Engine careModel | schema 1.0.0 | NEW ADAPTER |
| `nutrition_from_requirement_profile` | same | requirementProfile → nutrition result | Contract | Tests; future Ω13 | Engine profile | schema 1.0.0 | NEW ADAPTER |
| `bundles_from_search_envelope` | same | package_options + provenance → bundles | Contract | Tests; future Ω13 | Optimizer envelope | schema 1.0.0 | NEW ADAPTER |
| `fact_from_warehouse_row` / `evidence_from_warehouse_row` | same | CSV-shaped dict → fact/evidence | Contract | Tests | Warehouse row | schema 1.0.0 | NEW ADAPTER |
| `product_from_catalog_row` | same | Catalog row → product (no invented price) | Contract | Tests | Catalog | schema 1.0.0 | NEW ADAPTER |
| `profile_from_analyze_body` | `app/api/payload_adapter.py` | Application JSON → engine (legacy defaults) | API | Existing HTTP | Browser/legacy payload | 2.1.0 | EXISTING — NOT AGENT CONTRACT |

---

## D. Future tool contracts

| Name | File | Purpose | Owner | Consumers | Source of truth | Version | Status |
|---|---|---|---|---|---|---|---|
| `analyze_health` | registry + `health.py` | Health slice | Engine | Future agent | One PPIE run / careModel | tool 1.0.0 | DEFINED, NOT IMPLEMENTED |
| `calculate_nutrition` | registry + `nutrition.py` | Nutrition slice | Engine | Future agent | One PPIE run / requirementProfile | tool 1.0.0 | DEFINED, NOT IMPLEMENTED |
| `optimize_bundles` | registry + `bundles.py` | Bundle slice | Optimizer | Future agent | `PACKAGE_OPTIMIZER_V2_1` | tool 1.0.0 | DEFINED, NOT IMPLEMENTED |
| `generate_report` | registry | Presentation projection | Presentation | Future agent | Existing report builders | tool 1.0.0 | DEFINED, NOT IMPLEMENTED |
| `match_products` | — | — | — | — | — | — | NOT A PUBLIC TOOL |

---

## E. Frozen contracts

| Name | File | Purpose | Owner | Consumers | Source of truth | Version | Status |
|---|---|---|---|---|---|---|---|
| Analyze HTTP dict | `app/agent/response_assembler.py` | Application payload | Engine | Browser APIs | Engine | 2.1.0 | FROZEN |
| Workbench / three-surface projections | `app/presentation/adapter.py` | Role UI | Presentation | Workbench | Analyze dict | existing | FROZEN |
| Optimizer mathematics | `app/agent/package_search.py` | Exhaustive search | Optimizer | Engine | Formulas | PACKAGE_OPTIMIZER_V2_1 | FROZEN |
| Health reasoning | `app/data/scientific_care.py` | Warehouse care model | Science/engine | Engine | Warehouse | existing | FROZEN |
| Nutrition mathematics | `app/data/scientific_requirements.py` | Density minima | Engine | Optimizer | Secondary source constants | existing | FROZEN |
| Warehouse CSVs | `warehouse/**` | Facts | Science | Engine | CSVs | runtime | FROZEN |
| Authoring WRITE | `POST /api/v1/authoring/*` | Evidence staging | Science team | Authoring UI | Drafts | v1 | FROZEN / OFF AGENT SURFACE |
