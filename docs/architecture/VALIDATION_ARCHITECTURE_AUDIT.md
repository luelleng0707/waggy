# VALIDATION_ARCHITECTURE_AUDIT

## DATA QA
- `repository/warehouse_qa/*`
- `scripts/validate_warehouse.py`
- Validates schema/FK/citation and warehouse integrity.

## FORMULA QA
- `repository/math_debugger/formula_validator.py`
- `tests/formulas/*`, `tests/mathematics/*`, `tests/math_debugger/*`

## RUNTIME TESTING
- Pipeline/runtime regression suites under `tests/*`.

## ARCHITECTURE TESTING
- Architecture audit artifacts and `package.json` architecture test script.

## SCIENTIFIC EVIDENCE VALIDATION
- Currently partial through warehouse QA and evidence field checks.
- Numeric parameter scientific support remains unresolved for many engineering coefficients.

## Consolidation guidance
- Do not merge validation systems with different responsibilities.
- Standardize reporting surface first, then harmonize execution pipelines.
