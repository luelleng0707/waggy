# END_TO_END_RUNTIME_ARCHITECTURE

This document describes the **current** Wagtopia system as implemented today.

## Runtime entrypoint

- Process: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Entry module: `app/main.py` -> `app.api.main:app`
- Shared analysis runtime owner: `app.agent.engine.PPIEWellnessAgent`
- Shared data loader owner: `app.data.repository.DataRepository` (warehouse CSV-backed)

## Stage-by-stage pipeline (current state)

| # | Stage | Canonical owner | Input type | Output type | Production runtime status | Repository status | Formula IDs / execution tags | Warehouse datasets | Evidence dependency | Downstream consumers | Failure behavior | Trace/provenance behavior |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | INPUT | `app.api.main` | HTTP JSON | request dict | IMPLEMENTED | PARALLEL (repo has separate typed models) | n/a | n/a | none | all API routes | 400/500 response | HTTP timing headers |
| 2 | PROFILE NORMALIZATION | `app.api.payload_adapter.profile_from_analyze_body` | request dict | `DogProfileInput` | IMPLEMENTED | PARALLEL | `PROFILE_V1` | `biology.breeds`, profile fields | none | graph context | 400 validation error | profile values copied into execution context |
| 3 | BIOLOGICAL RESOLUTION | `app.agent.nodes.biology_node` | profile + breed context | biological traits snapshot | IMPLEMENTED | PARALLEL (`repository/pipeline`) | `BIOLOGY_V2_1` | biology domain CSVs | indirect | risk, epidemiology | stage warnings/errors in node output | node trace in execution trace |
| 4 | EVIDENCE COLLECTION / GRAPH | `app.agent.nodes.evidence_node` | condition/risk context | evidence bundle | PARTIAL | PARALLEL (`repository/science_graph`) | `EVIDENCE_V2_1` | evidence/citation datasets | required for scientific support | report, developer trace | empty evidence lists preserved | citations and evidence rows in debug payload when available |
| 5 | CONDITION ASSESSMENT | `app.agent.nodes.risk_node` | biology + profile | condition-level risk outputs | IMPLEMENTED | PARALLEL (`repository/reasoning`) | `RISK_V2_1` | condition and trait tables | optional/partial | nutrition, product planning | graceful fallback with missing values | debug formula_executions entries |
| 6 | MATHEMATICAL ASSESSMENT | `app.agent` runtime formulas | risk inputs | agreement/confidence-like fields | PARTIAL | PARALLEL (`repository/mathematics`) | app runtime formula IDs (not MAT-100x owner) | condition/evidence related tables | partial | report + priorities | values may be unavailable; no synthetic fill | exposed via validation console |
| 7 | OBJECTIVE RESOLUTION | `app.agent.nodes.assessment_node` | condition and risk outputs | objective-like assessment fields | PARTIAL | PARALLEL (`repository/objectives`) | stage-local logic | assessment modules | partial | package and presentation | returns sparse structures when missing | included in assessment payload |
| 8 | MECHANISM PLANNING | app stage logic | assessment context | mechanism-oriented fields | PARTIAL | PARALLEL (`repository/mechanisms`) | stage-local logic | mechanisms datasets | dependent on blocker-prone refs | ingredient planning | unresolved refs remain not fabricated | visible as unavailable/partial in debug |
| 9 | DOSE TARGETS | app nutrition path | risk + profile + product constraints | target values | PARTIAL | PARALLEL (`repository/optimization` TGT-701) | app internal formulas | nutrition / feeding tables | optional | ingredient + product planning | missing values propagate as unavailable | trace entries + payload fields |
| 10 | INGREDIENT PLANNING | `app.agent.nodes.ingredient_node` | nutrition/targets | ingredient priorities | PARTIAL | PARALLEL (`repository/objectives`, `repository/sources`) | stage-local logic | ingredient/evidence tables | partial | product optimization | sparse lists allowed | debug execution + section lookups |
| 11 | SOURCE PLANNING | app data/recommendation path | ingredient signals | source/product constraints | PARTIAL | PARALLEL (`repository/sources`) | stage-local logic | catalog and product mapping tables | indirect | product node | unresolved mapping -> empty candidates | lookup trace if debug enabled |
| 12 | PRODUCT CANDIDATE GENERATION | `app.agent.nodes.product_node` | ingredient + profile | product recommendations | IMPLEMENTED | PARALLEL (`repository/optimization`) | optimization stage formulas | product, feeding, pricing, function tables | indirect | package and financial | empty candidates handled without crash | execution trace + debug records |
| 13 | NUTRITION / CALORIE CHECK | app optimization/nutrition pipeline | product set + dog profile | nutrition/calorie signals | PARTIAL | PARALLEL (`repository/optimization/calories.py`) | app stage calculations | feeding rules + composition tables | none | package scoring, UI | may return unavailable metrics | developer trace when available |
| 14 | ABSORPTION ANALYSIS | app package optimization | candidate package | absorption-aware scoring terms | PARTIAL | PARALLEL (`repository/optimization/absorption.py`) | `PACKAGE_OPTIMIZER_V2_1` components | product/ingredient relation data | optional | package selection | degraded score path on missing inputs | in formula execution details when emitted |
| 15 | SYNERGY ANALYSIS | app package optimization | candidate package | synergy terms | PARTIAL | PARALLEL (`repository/optimization/synergy.py`) | `PACKAGE_OPTIMIZER_V2_1` components | ingredient/function relations | optional | package selection | fallback to neutral impact | debug output where available |
| 16 | CONFLICT ANALYSIS | app package optimization | candidate package | conflict penalties | PARTIAL | PARALLEL (`repository/optimization/conflict.py`) | `PACKAGE_OPTIMIZER_V2_1` components | interaction/constraint sources | optional | package selection | fallback if data absent | debug output where available |
| 17 | CONSTRAINT CHECKING | app bundle + optimizer path | package candidate | valid/invalid package | IMPLEMENTED | PARALLEL (`repository/optimization/constraints.py`) | app bundle constraints | feeding/pricing/rules | none | final package and economics | invalid combos filtered | trace includes selected package rationale |
| 18 | HARMONY SCORE | app package optimizer | package-level aggregated terms | package score/rank | IMPLEMENTED (package-level) | PARALLEL (`repository/optimization/harmony.py`) | `PACKAGE_OPTIMIZER_V2_1` | package candidate data | optional | final package | ties/weak signal handled deterministically | formula execution records include output |
| 19 | OPTIMIZED PACKAGE | `app.agent.nodes.package_node` + `app.agent.bundle_engine` | ranked package candidates | selected package(s) | IMPLEMENTED | PARALLEL | package optimizer outputs | product/pricing/feed data | optional | report/export/presentation | returns fewer/empty packages if needed | trace + pricing fields in output |
| 20 | FINANCIAL MODEL | `app.agent.bundle_engine` + `response_assembler` | package/product economics | monthly/yearly plan fields | PARTIAL | PARALLEL (repo architecture target only) | bundle equations in app runtime | pricing + serving data | none | customer/business presentations | `NOT AVAILABLE` for missing fields | financial values carried in analyze payload |
| 21 | PRESENTATION PROJECTION | `app.presentation.adapter` | analyze + assessment + optional debug console | three surface payload | IMPLEMENTED | n/a | `analysis_signature`, `presentation_correlation_id` | none | developer view may include evidence status | `/`, `/business`, `/developer` | missing fields explicitly marked unavailable | correlation/signature preserved |
| 22 | CUSTOMER / BUSINESS / DEVELOPER | `legacy/*.html` + JS + API routes | projected payloads | rendered UI | IMPLEMENTED | n/a | n/a | none | customer/business filtered; developer expanded | browser users | route auth/feature gates | route-level and debug trace controls |

## Notes on production vs repository

- Production HTTP runtime executes `app/` modules directly.
- `repository/` modules are substantial and tested, but currently PARALLEL / TEST-ONLY for scientific runtime cutover.
- Developer provenance surfaces are debug-gated and may contain `NOT AVAILABLE`, `NOT DOCUMENTED`, or `NOT IMPLEMENTED` statuses.
