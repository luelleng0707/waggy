# FORMULA_REGISTRY_CANONICAL_CONTRACT

## Canonical target
- Runtime canonical formula ownership candidate: `repository/formulas/`.

## Contract
- Formula identity: `(formula_id, version)`.
- Active version resolution: deterministic (`active` highest lexical version; else latest catalog version).
- Explicit version resolution: exact, deterministic, no silent substitution.
- Parameter/coefficient identity: `(formula_id, version, parameter_set_id, parameter_name)`.
- Missing formula/version/config: explicit error (`KeyError` / validation issue), not silent success.
- Trace requirement: configuration returned must include `formula_id`, `version`, `status`, `parameter_set_id`, `coefficients`.

## Scope guard
- No MAT-1001..MAT-1008 methodology changes in this phase.
- Contract only concerns ownership and resolution interface behavior.
