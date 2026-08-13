# INTERVIEW_CLAIM_COVERAGE

| claim | runtime evidence | surface(s) | exact source | status |
|---|---|---|---|---|
| AI-enabled recommendation workflow | `PPIEWellnessAgent` executes deterministic analyze pipeline and emits recommendations | `/`, `/business`, `/developer` | `app/api/main.py:/api/v1/analyze`, `app/agent/engine.py`, `app/agent/formula_graph.py` | VERIFIED |
| product portfolio | Runtime returns product catalog/recommendation/package structures | `/`, `/business` | `app/agent/response_assembler.py`, `app/api/main.py:/api/v1/store` | VERIFIED |
| dog breed scope | Breed input and breed lookup path are active | `/`, `/business`, `/developer` | `app/api/main.py:/api/breeds`, `app/agent/nodes/breed_node.py` | VERIFIED |
| scientific research | Scientific evidence payload exists but coverage/lineage completeness varies | `/`, `/developer` | `app/agent/response_assembler.py` (`scientificEvidence`), `app/debug/clinical_execution_debug.py` | PARTIAL |
| market research | No dedicated runtime market-model engine producing market KPIs | `/business` | no canonical production runtime owner identified | NOT IMPLEMENTED |
| synthetic customer/dog profiles | Deterministic Dolly/mixed profile paths are available for demo use | `/`, `/business`, `/developer` | `legacy/app.js`, `legacy/business.js`, `legacy/ppie-validation-console.js` presets | VERIFIED |
| personalized recommendations | Product/package output depends on profile and runtime scoring | `/`, `/business` | `app/agent/nodes/product_node.py`, `app/agent/nodes/package_node.py` | VERIFIED |
| product gaps | Runtime business projection currently marks gaps as unavailable | `/business` | `app/presentation/adapter.py` (`product_gaps: NOT AVAILABLE`) | PARTIAL |
| portfolio expansion | No dedicated expansion engine in current production path | `/business` | `app/presentation/adapter.py` (`portfolio_expansion: NOT AVAILABLE`) | PARTIAL |
| complete care packages | Package bundles and tiers are generated where candidate set is available | `/`, `/business` | `app/agent/bundle_engine.py`, `app/agent/package_optimizer.py` | VERIFIED |
| financial modeling | Monthly/yearly economics and recurring fields are emitted when calculable | `/`, `/business` | `app/agent/bundle_engine.py`, `app/agent/response_assembler.py` | VERIFIED |
| product costs | Product and plan cost fields are runtime-backed | `/`, `/business`, `/developer` | `app/agent/response_assembler.py`, product pricing datasets | VERIFIED |
| consumption | Serving/feeding consumption logic exists but coverage is profile/data dependent | `/`, `/business` | `app/agent/bundle_engine.py`, feeding rule reads in `app/data/repository.py` | PARTIAL |
| package pricing | Package pricing fields are returned when package generated | `/`, `/business` | `app/agent/response_assembler.py`, `app/agent/bundle_engine.py` | VERIFIED |
| discounts | Discount values are conditional and not guaranteed | `/`, `/business` | bundle/package pricing fields in analyze payload | PARTIAL |
| recurring economics | Monthly-equivalent/yearly relationships are provided when package economics available | `/`, `/business` | `app/agent/bundle_engine.py` | VERIFIED |
| experimental products | No explicit production runtime module for experimental product opportunity analysis | `/business` | no canonical owner in `app/` runtime path | NOT IMPLEMENTED |
| rapid scaling | No production runtime output for scaling KPI computation | `/business` | no canonical owner in `app/` runtime path | NOT IMPLEMENTED |

## Notes

- VERIFIED = directly supported by current production runtime + surfaced in at least one canonical browser interface.
- PARTIAL = runtime/surface support exists but is incomplete, conditional, or explicitly marked unavailable for some fields.
- NOT IMPLEMENTED = no trustworthy production runtime contract currently found.
