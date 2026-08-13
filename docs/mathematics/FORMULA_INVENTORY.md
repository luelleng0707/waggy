# Formula Inventory

| Formula ID | Version | Module | Function | Purpose | Inputs | Outputs | Parameters | Warehouse Dependencies | Documentation | Tests |
|---|---|---|---|---|---|---|---|---|---|---|
| MAT-1001 | v1.0 | `repository/mathematics/epidemiology.py` | `ObservedEpidemiologyEngine.evaluate` | Observed prevalence | observed edges | observed prevalence | none | EvidenceGraph | `OBSERVED_PREVALENCE.md` | `tests/mathematics` |
| MAT-1002 | v1.0 | `repository/mathematics/aggregation.py` | `TraitAggregationEngine.estimate` | Trait/env aggregation | non-observed edges | evidence prevalence | min/max/divisor | formulas coefficients | `TRAIT_AGGREGATION.md` | `tests/mathematics` |
| MAT-1003 | v1.0 | `repository/mathematics/bayesian.py` | `posterior_percent` | Bayesian update | prior,evidence,strength | posterior prevalence | bayesian_scale | formulas coefficients | `ESTIMATED_PREVALENCE.md` | `tests/mathematics` |
| MAT-1004 | v1.0 | `repository/mathematics/agreement.py` | `AgreementMathematicsEngine.evaluate` | Agreement metrics | observed,estimated | agreement | agreement_floor | formulas coefficients | `AGREEMENT.md` | `tests/mathematics` |
| MAT-1005 | v1.0/v2.0 | `repository/mathematics/confidence.py` | `ConfidenceMathematicsEngine.evaluate` | Confidence | evidence counts + agreement | confidence | weights/denominators | formulas coefficients | `CONFIDENCE.md` | `tests/mathematics`,`tests/formulas` |
| MAT-1006 | v1.0 | `repository/mathematics/novelty.py` | `NoveltyMathematicsEngine.evaluate` | Novelty | observed,estimated,confidence | novelty | thresholds | formulas coefficients | `NOVELTY.md` | `tests/mathematics` |
| MAT-1007 | v1.0 | `repository/mathematics/priority.py` | `PriorityMathematicsEngine.rank` | Priority | estimated/conf/agree/novelty | priority | min_agreement_scale | formulas coefficients | `PRIORITY.md` | `tests/mathematics` |
| MAT-1008 | v1.0 | `repository/mathematics/uncertainty.py` | `UncertaintyMathematicsEngine.evaluate` | Uncertainty bounds | contributions+confidence | bounds | min_uncertainty_factor | formulas coefficients | `UNCERTAINTY.md` | `tests/mathematics` |
| TGT-701..OPT-712 | 1.0.0 | `repository/optimization/*` | calculators | Optimization chain | target/candidate stats | bundle score/choice | code+warehouse | optimization datasets | `COVERAGE.md`,`HARMONY.md`,`BUNDLE_OPTIMIZATION.md` | `tests/optimization` |
| EST-001..MEC-001 | 1.0.0 | `repository/reasoning/*` | reasoning engines | Ω4 deterministic inference | evidence graph | condition assessment | code constants + lookups | reference + biology datasets | `REASONING_ESTIMATION.md`,`REASONING_AGREEMENT.md`,`BODY_SYSTEM_MAPPING.md`,`CONDITION_MECHANISM_MAPPING.md` | `tests/reasoning` |

Notes:
- Parameters marked as code constants and not loaded from formula warehouse are `PARAMETER_STATUS = ENGINEERING_ASSUMPTION`.
- Runtime execution provenance parity for app V2 formulas is tracked separately in `EXECUTION_FORMULA_MAP.md` and `docs/architecture/FORMULA_EXECUTION_PARITY.csv`.
