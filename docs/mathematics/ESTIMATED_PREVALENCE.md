# ESTIMATED_PREVALENCE

## 1. Formula identity
- Formula ID: `MAT-1003`
- Formula version: `v1.0`
- Formula name: Bayesian Update
- Status: active
- Owning module: `repository/mathematics/aggregation.py` + `repository/mathematics/bayesian.py`
- Python implementation: `posterior_percent`
- Source lines: `repository/mathematics/bayesian.py 8-14`

## 2. Purpose
Combines prior observed prevalence and aggregated evidence prevalence with evidence strength.

## 3. Inputs
- `prior_percent` | float | % | 0-100 | source: MAT-1001 output
- `evidence_percent` | float | % | 0-100 | source: MAT-1002 output
- `strength` | float | ratio | 0-1 | source: MAT-1002 coefficients and evidence count
- `interaction_delta` | float | % | unbounded | source: interaction adjustment

## 4. Equation
`Posterior = logistic((1-s)*logit(Prior) + s*logit(Evidence))`
`Estimated = Posterior + InteractionDelta`

## 5. Code -> equation mapping
- `posterior_logit = ((1-s)*prior_logit) + (s*evidence_logit)`
- `probability_to_percent(logistic(posterior_logit))`
- `estimated = posterior + interaction_delta`

## 6. Parameter provenance
- `strength` bounded by MAT-1002 coefficients.
- No extra coefficients in MAT-1003 (`bayesian_scale=1.0`).

## 7. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- prior `18%`, evidence `5.5%`, strength `0.4`
- posterior (logit blend) `~11.2%`
- interaction delta `+1.8%`
- estimated `~13.0%`

## 8. Bayesian methodology audit (Ω9.3)

- Implementation in `repository/mathematics/bayesian.py`:
  - converts prior/evidence percentages to logits,
  - blends them with a scalar `strength`,
  - converts blended logit back to percent.
- This is a Bayesian-inspired update in logit space.
- It does **not** explicitly expose:
  - a likelihood function,
  - evidence model assumptions,
  - posterior normalization from prior x likelihood.
- Audit status: `METHODOLOGICAL_REVIEW_REQUIRED` for publication framing.
