# ENVIRONMENT_MODEL

## Current environment modeling behavior

Current runtime and supporting architecture use a mixture of:

- climate string matching
- location/city descriptors (when provided)
- urbanicity/housing/activity descriptors
- profile environment fields

Status: PARTIAL / heuristic-heavy.

## Boundary classification

| Category | Current state |
|---|---|
| Measured epidemiological covariates | PARTIAL (limited explicit measured covariate flow in production path) |
| Engineering/environmental heuristics | PRESENT (string/category matching and rule-like adjustments) |
| Causal coefficients | Not established as canonical production science contract |

## Architecture requirement

- Keep environment-derived values clearly labeled as observed vs derived vs heuristic.
- Avoid presenting heuristic adjustments as confirmed causal epidemiological coefficients.
- Require provenance tags in developer trace for environment-derived condition influence values.
