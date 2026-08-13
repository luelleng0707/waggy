# AGREEMENT

## 1. Formula identity
- Formula ID: `MAT-1004`
- Formula version: `v1.0`
- Name: Agreement
- Status: active
- Module: `repository/mathematics/agreement.py`
- Function: `AgreementMathematicsEngine.evaluate`
- Lines: `9-50`

## 2. Purpose
Quantifies error and agreement between observed and estimated prevalence.

## 3. Inputs
- `observed_prevalence` float `%` source MAT-1001
- `estimated_prevalence` float `%` source MAT-1003

## 4. Equation
- `AbsoluteError = |Observed - Estimated|`
- `RelativeError = AbsoluteError / max(Observed, 1e-6)`
- `Agreement% = max(0, 100 - RelativeError*100)`

## 5. Code mapping
- `abs_error = abs(observed - estimated)`
- `relative_error = abs_error / max(observed, 0.000001)`
- `agreement = max(0.0, 100.0 - (relative_error * 100.0))`

## 6. Parameters
- `agreement_floor=0.0` from formulas coefficients.
- PARAMETER_STATUS = ENGINEERING_ASSUMPTION

## 7. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Observed `18`, Estimated `16`
- AbsoluteError `2`
- RelativeError `2/18=0.111111`
- Agreement `100*(1-0.111111)=88.8889%`

## 8. Edge-case audit (Ω9.3)

- `observed = 0`, `estimated > 0`:
  - denominator uses `max(observed, 1e-6)` so relative error becomes very large and agreement floors to `0`.
- `observed > 0`, `estimated = 0`:
  - relative error is `observed/observed = 1`, so agreement is `0`.
- `observed = 0`, `estimated = 0`:
  - absolute error `0`, relative error `0 / 1e-6 = 0`, agreement `100`.
- `missing observed`:
  - upstream MAT-1001 emits `NO_EVIDENCE`; agreement still computes numerically using observed fallback.
- `missing estimated`:
  - not expected in normal runtime, because estimated is produced by MAT-1003 before MAT-1004.
- `observed = estimated`:
  - absolute error `0`, agreement `100`.
