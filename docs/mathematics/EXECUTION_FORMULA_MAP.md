# EXECUTION_FORMULA_MAP

Execution map for formulas currently observed in the app runtime developer debugger (`/debug/calculation?debug=1`).

## App runtime formulas (V2 path)

| Formula ID | Version | Actual source | Actual function | Computation documentation | Input variables | Parameters | Output | Warehouse dependencies | Evidence dependencies | Replay capability | Sensitivity capability | Scientific status | Publication status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PROFILE_NORMALIZE_V2_1 | 2.1.0 | `app/api/payload_adapter.py` | `profile_from_analyze_body` | Not documented as formal equation | Profile payload fields | none | normalized profile | none | none | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| BREED_RESOLVE_V2_1 | 2.1.0 | `app/formulas/stages/biological.py` | `run_biological_stage` | Not documented as formal equation | breeds, split | none | resolved breeds | breeds, aliases | none | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| TRAIT_BLEND_V2_1 | 2.1.0 | `app/formulas/stages/biological.py` | `run_biological_stage` | Not documented as formal equation | resolved breeds | none | trait summary | trait matrices | none | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| RISK_V2_1 | 2.1.0 | `app/formulas/stages/health_risk.py` | `compute_risks` | Formal equation not documented in runtime payload | traits, profile, observed conditions | interaction/category parameters | risk/confidence | risk and trait tables | optional evidence IDs | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| NUTRIENT_TARGET_V2_1 | 2.1.0 | `app/agent/ingredient_engine.py` | `map_ingredients` | Formal equation not documented in runtime payload | risk outputs, profile | none | nutrient targets | condition ingredients tables | ingredient evidence refs when emitted | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| ACTIVITY_V2_1 | 2.1.0 | `app/agent/nodes/activity_node.py` | `ActivityNode.execute` | Not documented as formal equation | profile + epidemiology state | none | activity recommendations | condition activities | none | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| PRODUCT_MATCH_V2_1 | 2.1.0 | `app/formulas/stages/optimization.py` | `run_optimization_stage` | Not documented as formal equation | nutrient targets, profile | none | product ranking | product catalog tables | none | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| PACKAGE_OPTIMIZER_V2_1 | 2.1.0 | `app/agent/package_optimizer.py` | `build_optimized_packages` | Not documented as formal equation | products, targets, risks | score weights | package tiers | package + pricing tables | none | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| EVIDENCE_RANK_V2_1 | 2.1.0 | `app/agent/response_assembler.py` | `collect_evidence` | Not documented as formal equation | conditions, ingredients | none | evidence bundle | evidence tables | paper/link fields if emitted | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| VALIDATION_V2_1 | 2.1.0 | `app/agent/calculation_trace.py` + `app/data/clinical_assessment.py` | validation projection path | Not documented as formal equation | observed vs estimated | none | validation rows | inherited from risk path | inherited from evidence path | NOT_IMPLEMENTED | NOT_IMPLEMENTED | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |
| GROOMING_OBS_V2_1 | 2.1.0 | `app/agent/nodes/grooming_node.py` | `GroomingNode.execute` | Not documented as formal equation | profile observations | none | grooming checklist | grooming defs | none | NOT_APPLICABLE | NOT_APPLICABLE | NOT_AVAILABLE_FOR_THIS_EXECUTION | NOT_ASSESSED |

## Repository mathematics formulas (MAT path)

These formulas are documented and replay-capable in `repository/math_debugger`, but are not the same execution namespace as V2 app runtime formulas.

- `MAT-1001` .. `MAT-1008`: replay-supported by `repository.math_debugger.independent_replay`
- Sensitivity support depends on replay trace completeness

Use `docs/architecture/FORMULA_EXECUTION_PARITY.csv` for cross-namespace parity status.
