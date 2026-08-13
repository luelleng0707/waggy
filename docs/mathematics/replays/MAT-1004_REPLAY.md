# Calculation Replay

Formula:
MAT-1004:1.0.0

## Inputs
- estimated = 1.511908 (unitless)
- observed = 0.0 (unitless)

## Parameters
- None

## Formula
agreement = max(0, 100-(abs_error/max(observed,1e-6))*100)

## Substituted Formula
agreement = max(0, 100-(|0.0-1.511908|/max(0.0,1e-6))*100)

## Intermediate Calculations
- absolute_error = 1.511908
- normalized_agreement = 0.0
- relative_error = 1511908.0

## Final Result
- Production: 0.0
- Independent replay: 0.0
- Delta: 0.0
- Status: MATCH

## Provenance
- warehouse evidence rows: 1
- code: repository/mathematics/agreement.py::AgreementMathematicsEngine.evaluate