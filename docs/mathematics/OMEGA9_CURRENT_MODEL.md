# OMEGA9_CURRENT_MODEL

This document freezes the current production Omega 9 mathematics implementation exactly as implemented in `repository/mathematics` and `repository/pipeline/biological_runtime.py`.

## Runtime execution order (actual)

1. MAT-1001 Observed prevalence (`ObservedEpidemiologyEngine.evaluate`)
2. MAT-1002 Trait/environment aggregation (`TraitAggregationEngine.estimate`, first trace)
3. MAT-1003 Bayesian-style update (`TraitAggregationEngine.estimate` + `bayesian.posterior_percent`, second trace)
4. MAT-1004 Agreement (`AgreementMathematicsEngine.evaluate`)
5. MAT-1005 Confidence (`ConfidenceMathematicsEngine.evaluate`)
6. MAT-1006 Novelty (`NoveltyMathematicsEngine.evaluate`)
7. MAT-1008 Uncertainty (`UncertaintyMathematicsEngine.evaluate`)
8. MAT-1007 Priority (`PriorityMathematicsEngine.rank`)

## MAT-1001
- Formula ID: MAT-1001
- Current formula: `observed_prevalence = mean(observed_edge_values)`
- Implementation: `repository/mathematics/epidemiology.py::ObservedEpidemiologyEngine.evaluate`
- Parameters: none consumed in code (`observed_mean_scale` exists in warehouse coefficients but is unused)
- Coefficient source: `warehouse/formulas/coefficients.csv`
- Inputs: observed edges (`observed_value` or `value_number`) for each condition
- Outputs: `observed_prevalence`, `evidence_count`
- Dependencies: `canonical_percent` normalization; evidence_graph observed edges
- Upstream formulas: none
- Downstream formulas: MAT-1003 prior, MAT-1004, MAT-1006
- Warehouse facts used: `biology.observed_breed_conditions` through pipeline evidence graph
- Known assumptions: equal weighting across observed rows; no sample-size weighting
- Known limitations: combines heterogeneous study populations as simple mean; no explicit mixed-breed separation in aggregation
- Publication risk: MEDIUM

## MAT-1002
- Formula ID: MAT-1002
- Current formula: `evidence_percent = logistic(sum(logit(p_i)*w_i)/sum(w_i))`
- Implementation: `repository/mathematics/aggregation.py::TraitAggregationEngine.estimate`
- Parameters: `min_strength`, `max_strength`, `strength_divisor` from formula coefficients; evidence-type weights from `weights.py`
- Coefficient source: `warehouse/formulas/coefficients.csv` and hardcoded `repository/mathematics/weights.py`
- Inputs: non-observed edges (`trait`, `environment`, `interaction`, `life_stage`, `activity`, `ingredient`)
- Outputs: `evidence_percent`, `trait_prevalence`, `environment_prevalence`
- Dependencies: logit/logistic normalization and probability clamp
- Upstream formulas: MAT-1001 (fallback source when no non-observed edges)
- Downstream formulas: MAT-1003
- Warehouse facts used: trait/environment/mixed/life_stage/activity/ingredient derived evidence rows
- Known assumptions: hardcoded evidence-type weights; bounded evidence strength schedule
- Known limitations: strong engineering dependence; interaction evidence reused downstream
- Publication risk: HIGH

## MAT-1003
- Formula ID: MAT-1003
- Current formula: `posterior = logistic((1-s)*logit(prior)+s*logit(evidence)); estimated = max(0, posterior + interaction_delta)`
- Implementation: `repository/mathematics/aggregation.py::TraitAggregationEngine.estimate` and `repository/mathematics/bayesian.py::posterior_percent`
- Parameters: `strength` from MAT-1002; implicit prior fallback `10.0` when observed prior is falsy
- Coefficient source: `warehouse/formulas/coefficients.csv` includes `bayesian_scale` but it is unused
- Inputs: MAT-1001 observed prevalence, MAT-1002 evidence_percent, interaction delta
- Outputs: `estimated_prevalence`
- Dependencies: probability clamp `[1e-6, 1-1e-6]`, strength clamp `[0,1]`
- Upstream formulas: MAT-1001, MAT-1002
- Downstream formulas: MAT-1004, MAT-1006, MAT-1007, MAT-1008
- Warehouse facts used: inherited from MAT-1002 edge sources and interaction factors
- Known assumptions: Bayesian-style naming without explicit likelihood model
- Known limitations: not formal Bayesian posterior with explicit P(E|H) definition
- Publication risk: BLOCKED

## MAT-1004
- Formula ID: MAT-1004
- Current formula: `agreement = max(0, 100 - (|obs-est|/max(obs,1e-6))*100)`
- Implementation: `repository/mathematics/agreement.py::AgreementMathematicsEngine.evaluate`
- Parameters: none consumed (`agreement_floor` exists in coefficients but is unused)
- Coefficient source: `warehouse/formulas/coefficients.csv`
- Inputs: MAT-1001 observed prevalence, MAT-1003 estimated prevalence
- Outputs: `agreement_percent`, `normalized_agreement`, `absolute_error`, `relative_error`, `prediction_error`
- Dependencies: epsilon denominator guard `1e-6`
- Upstream formulas: MAT-1001, MAT-1003
- Downstream formulas: MAT-1005, MAT-1007
- Warehouse facts used: indirectly via upstream formulas
- Known assumptions: deterministic model-observation agreement metric
- Known limitations: agreement is not confidence or posterior probability
- Publication risk: MEDIUM

## MAT-1005
- Formula ID: MAT-1005
- Current formula: `confidence = (w_e*evidence_component + w_s*study_component + w_a*agreement_component)*100`
- Implementation: `repository/mathematics/confidence.py::ConfidenceMathematicsEngine.evaluate`
- Parameters: `observed_multiplier`, `evidence_denominator`, `study_denominator`, `evidence_weight`, `study_weight`, `agreement_weight`
- Coefficient source: `warehouse/formulas/coefficients.csv` (v1.0 active, v2.0 available)
- Inputs: edge counts by evidence type, citation count, agreement normalized
- Outputs: `confidence_score`
- Dependencies: denominator floors `1e-6`, component caps via `min(1.0, ...)`
- Upstream formulas: MAT-1004; indirectly MAT-1001..1003 through edges/agreement
- Downstream formulas: MAT-1006, MAT-1007, MAT-1008
- Warehouse facts used: all edge classes and citations in condition graph
- Known assumptions: all coefficients are engineering parameters in current evidence state
- Known limitations: evidence volume reused after prevalence stage, potential double counting
- Publication risk: HIGH

## MAT-1006
- Formula ID: MAT-1006
- Current formula: `novelty = max(0, estimated-observed)*(confidence/100)` with thresholded `emerging_biological_concern`
- Implementation: `repository/mathematics/novelty.py::NoveltyMathematicsEngine.evaluate`
- Parameters: `emerging_observed_max`, `emerging_estimated_min`, `emerging_confidence_min`
- Coefficient source: `warehouse/formulas/coefficients.csv`
- Inputs: observed prevalence, estimated prevalence, confidence score
- Outputs: `novelty_score`, `emerging_biological_concern`, rationale string
- Dependencies: delta floor at zero
- Upstream formulas: MAT-1001, MAT-1003, MAT-1005
- Downstream formulas: MAT-1007
- Warehouse facts used: indirectly via upstream formulas
- Known assumptions: threshold logic is engineering-defined
- Known limitations: does not explicitly separate no-evidence from true low-risk
- Publication risk: HIGH

## MAT-1007
- Formula ID: MAT-1007
- Current formula: `priority = estimated*(confidence/100)*(1+novelty/100)*max(min_agreement_scale, agreement/100)`
- Implementation: `repository/mathematics/priority.py::PriorityMathematicsEngine.rank`
- Parameters: `min_agreement_scale`
- Coefficient source: `warehouse/formulas/coefficients.csv`
- Inputs: estimated prevalence, confidence, novelty, agreement
- Outputs: `priority_score`, `priority_rank`
- Dependencies: multiplicative composition and agreement floor
- Upstream formulas: MAT-1003, MAT-1004, MAT-1005, MAT-1006
- Downstream formulas: none in MAT stack (used as ranked output)
- Warehouse facts used: indirectly via upstream formulas
- Known assumptions: multiplicative compounding of engineering-sensitive upstream signals
- Known limitations: uncertainty propagation is implicit and not decomposed
- Publication risk: HIGH

## MAT-1008
- Formula ID: MAT-1008
- Current formula: `uncertainty = stddev(non_observed_values) * max(min_uncertainty_factor, 1-confidence/100)`
- Implementation: `repository/mathematics/uncertainty.py::UncertaintyMathematicsEngine.evaluate`
- Parameters: `min_uncertainty_factor`
- Coefficient source: `warehouse/formulas/coefficients.csv`
- Inputs: non-observed edge values, confidence, estimated prevalence
- Outputs: `uncertainty`, `lower_bound`, `upper_bound`
- Dependencies: lower bound floor at zero, uncertainty-factor floor
- Upstream formulas: MAT-1003, MAT-1005; non-observed evidence edges
- Downstream formulas: none
- Warehouse facts used: same non-observed edge channels as MAT-1002
- Known assumptions: heuristic dispersion-based uncertainty factor
- Known limitations: not a formal statistical confidence interval
- Publication risk: HIGH

## Mixed-breed and environment behavior in current path
- Mixed-breed handling currently resolves dog breed using `profile.breeds[0]` in `WarehouseBackedDogResolver.resolve`.
- Additional mixed-breed evidence can still enter via `biology.mixed_breed_NEEDS_VALIDATION` trait matching, which can overlap with breed and trait channels.
- Environment matching is climate-string based in `WarehouseBackedEnvironmentResolver`; city/urbanicity/housing/walking inputs are preserved but not all are transformed into separate measured epidemiological covariates.

## Production freeze marker
- Benchmark output hash (SHA256): `b2b200753bc955b6568cbc52c83e88151db65370c58159e9d718a7e0a75b9303`
