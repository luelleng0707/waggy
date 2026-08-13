# Ω9 Mathematics Formula Registry

## MAT-1001 — Observed Aggregation
- `observed_prevalence = mean(observed_edge_values)`

## MAT-1002 — Trait Aggregation
- `trait_environment_aggregate = logistic(weighted_mean(logit(edge_prevalence)))`

## MAT-1003 — Bayesian Update
- `posterior = logistic((1-strength)*logit(prior)+strength*logit(evidence))`

## MAT-1004 — Agreement
- `agreement = max(0, 100-(abs_error/max(observed,1e-6))*100)`

## MAT-1005 — Confidence
- `confidence = weighted_evidence_score * agreement_factor`

## MAT-1006 — Novelty
- `novelty = max(0, estimated-observed) * confidence_scale`

## MAT-1007 — Priority
- `priority = estimated * confidence * (1+novelty/100) * agreement_scale`

## MAT-1008 — Uncertainty
- `uncertainty = stddev(contributions) * uncertainty_factor`
