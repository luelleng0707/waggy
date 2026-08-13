# COVERAGE

## Formula identity
- IDs: `COV-703`, `COV-704`
- Module: `repository/optimization/coverage.py`

## Purpose
Measures target ingredient coverage and dose accuracy for a candidate bundle.

## Equations
- `Coverage% = (Provided / Required) * 100`
- `DoseAccuracy = max(0, 100 - mean(|Coverage% - 100|))`

## Inputs
- target amounts from `TargetIntakePlan`
- provided amounts from candidate composition + product composition rows.

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Required EPA `420`, provided `398`
- Coverage `94.7619%`
- If mean absolute coverage deviation is `7.2`, dose accuracy `92.8`
