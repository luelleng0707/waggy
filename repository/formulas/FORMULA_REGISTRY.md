# Ω9.1 Formula-as-Data Runtime

This package loads and resolves mathematical formulas from `warehouse/formulas/` without changing mathematical code when versions or coefficients change.

## Responsibilities

- Load formula metadata (`formulas.csv`)
- Load version states (`formula_versions.csv`)
- Load parameter sets (`parameter_sets.csv`)
- Load coefficients (`coefficients.csv`)
- Validate configuration completeness
- Resolve active or requested versions
- Expose immutable coefficient lookup API

## Runtime Guarantees

- Deterministic resolution for same warehouse content
- No formula mutation in code paths
- Backward compatibility through active default versions
