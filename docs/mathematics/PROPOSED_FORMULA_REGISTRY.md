# PROPOSED_FORMULA_REGISTRY

This is a disposition registry for current MAT formulas and their proposed future replacements. No production behavior changes are applied in Omega 9.5.

## MAT-1001
- CURRENT_FORMULA: simple mean of observed prevalence values.
- PROBLEM: no sample-size weighting; heterogeneous study populations can be mixed equally.
- FUTURE_FORMULA: weighted observed prevalence aggregator (weight by sample size and study quality).
- REQUIRED_DATA: sample size, population stratification, study quality fields.
- REQUIRED_PARAMETERS: study quality weights (estimated from validation set).
- SCIENTIFIC_SUPPORT_REQUIRED: explicit weighting rationale and sensitivity analysis.
- MIXED_BREED_SUPPORT: separate mixed-breed observed channel required.
- ENVIRONMENT_SUPPORT: not primary.
- UNCERTAINTY_SUPPORT: observed data confidence/heterogeneity interval.
- PUBLICATION_STATUS: KEEP_WITH_RESTRICTIONS
- ACTION: REVISE

## MAT-1002
- CURRENT_FORMULA: weighted log-odds aggregation over non-observed evidence.
- PROBLEM: hardcoded evidence-type weights and engineering strength parameters.
- FUTURE_FORMULA: calibrated prevalence estimation model with empirically estimated coefficients.
- REQUIRED_DATA: condition-labeled cohorts linking traits/environments/interactions to prevalence.
- REQUIRED_PARAMETERS: fitted coefficients with uncertainty bounds.
- SCIENTIFIC_SUPPORT_REQUIRED: numeric coefficient provenance.
- MIXED_BREED_SUPPORT: explicit mixture/phenotype representation.
- ENVIRONMENT_SUPPORT: measured covariates with provenance.
- UNCERTAINTY_SUPPORT: coefficient and data uncertainty channels.
- PUBLICATION_STATUS: HIGH_RISK
- ACTION: REPLACE

## MAT-1003
- CURRENT_FORMULA: Bayesian-style logit blend + additive interaction delta.
- PROBLEM: no explicit likelihood model; terminology overstates Bayesian validity.
- METHODOLOGICAL_REDESIGN_REQUIRED: true
- FUTURE_FORMULA: formal Bayesian update or relabeled deterministic logit combiner.
- REQUIRED_DATA: prior specification dataset + evidence likelihood definition.
- REQUIRED_PARAMETERS: prior and likelihood hyperparameters.
- SCIENTIFIC_SUPPORT_REQUIRED: explicit P(H), P(E|H), normalization assumptions.
- MIXED_BREED_SUPPORT: priors conditioned on breed mixture/phenotype.
- ENVIRONMENT_SUPPORT: evidence likelihood with environment covariates.
- UNCERTAINTY_SUPPORT: posterior intervals.
- PUBLICATION_STATUS: BLOCKED
- ACTION: REPLACE

## MAT-1004
- CURRENT_FORMULA: relative-error agreement between observed and estimated prevalence.
- PROBLEM: can be misinterpreted as confidence if terminology is sloppy.
- FUTURE_FORMULA: retain agreement metric with strict semantics and edge-case documentation.
- REQUIRED_DATA: observed and estimated prevalence pairs.
- REQUIRED_PARAMETERS: epsilon/tolerance policy only.
- SCIENTIFIC_SUPPORT_REQUIRED: interpretation documentation.
- MIXED_BREED_SUPPORT: inherited from upstream observed/estimated channels.
- ENVIRONMENT_SUPPORT: inherited from estimated channel.
- UNCERTAINTY_SUPPORT: should remain separate from uncertainty channels.
- PUBLICATION_STATUS: MEDIUM
- ACTION: KEEP

## MAT-1005
- CURRENT_FORMULA: weighted composite of evidence counts, study counts, agreement.
- PROBLEM: engineering coefficients + overlap with evidence already used in estimation.
- FUTURE_FORMULA: decomposed quality vector (coverage, quality, agreement, uncertainty, completeness) with optional late-stage summary.
- REQUIRED_DATA: citation quality fields, evidence coverage maps, missingness indicators.
- REQUIRED_PARAMETERS: transparent aggregation rules; avoid hidden weight dominance.
- SCIENTIFIC_SUPPORT_REQUIRED: documented rationale for any remaining weights.
- MIXED_BREED_SUPPORT: ensure evidence coverage is ancestry/phenotype aware.
- ENVIRONMENT_SUPPORT: separate quality indicators for environment evidence.
- UNCERTAINTY_SUPPORT: separate model/data uncertainty channels.
- PUBLICATION_STATUS: HIGH_RISK
- ACTION: REVISE

## MAT-1006
- CURRENT_FORMULA: positive observed-estimated gap scaled by confidence + threshold flag.
- PROBLEM: threshold engineering assumptions; insufficient distinction between no evidence vs true low risk.
- FUTURE_FORMULA: evidence-gap state machine with explicit states (observed, estimated-without-observation, emerging-concern, insufficient-evidence).
- REQUIRED_DATA: evidence completeness and direct-observation presence flags.
- REQUIRED_PARAMETERS: state thresholds only if empirically justified.
- SCIENTIFIC_SUPPORT_REQUIRED: transparent threshold provenance.
- MIXED_BREED_SUPPORT: state logic robust to mixed evidence channels.
- ENVIRONMENT_SUPPORT: state logic should account for environment evidence quality.
- UNCERTAINTY_SUPPORT: map states to uncertainty channels.
- PUBLICATION_STATUS: HIGH_RISK
- ACTION: REPLACE

## MAT-1007
- CURRENT_FORMULA: multiplicative priority from estimated prevalence, confidence, novelty, agreement floor.
- PROBLEM: compounds upstream engineering assumptions and duplicated confidence influence.
- FUTURE_FORMULA: multi-component priority architecture using separate observed prevalence, estimated prevalence, agreement, uncertainty, evidence coverage, severity/preventability (if sourced).
- REQUIRED_DATA: severity/preventability datasets and calibrated benchmarks.
- REQUIRED_PARAMETERS: explicit policy-level weighting, ideally scenario-configurable.
- SCIENTIFIC_SUPPORT_REQUIRED: provenance for each component and any weights.
- MIXED_BREED_SUPPORT: inherited from upstream redesign.
- ENVIRONMENT_SUPPORT: inherited from upstream redesign.
- UNCERTAINTY_SUPPORT: explicit propagation and reporting.
- PUBLICATION_STATUS: HIGH_RISK
- ACTION: REPLACE

## MAT-1008
- CURRENT_FORMULA: dispersion of non-observed inputs scaled by confidence-derived factor.
- PROBLEM: heuristic; not formal statistical uncertainty decomposition.
- FUTURE_FORMULA: split uncertainty channels: DATA_UNCERTAINTY, PARAMETER_UNCERTAINTY, MODEL_UNCERTAINTY, EVIDENCE_HETEROGENEITY.
- REQUIRED_DATA: replicate observations, parameter posterior/fit diagnostics, model error benchmarks.
- REQUIRED_PARAMETERS: channel-specific uncertainty controls.
- SCIENTIFIC_SUPPORT_REQUIRED: explicit statistical interpretation.
- MIXED_BREED_SUPPORT: separate uncertainty for mixture assumptions.
- ENVIRONMENT_SUPPORT: uncertainty contributions from environment covariates.
- UNCERTAINTY_SUPPORT: full decomposition.
- PUBLICATION_STATUS: HIGH_RISK
- ACTION: REPLACE
