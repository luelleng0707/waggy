# UNCERTAINTY

## 1. Formula identity
- Formula ID: `MAT-1008`
- Version: `v1.0`
- Module: `repository/mathematics/uncertainty.py`
- Function: `UncertaintyMathematicsEngine.evaluate`
- Lines: `11-66`

## 2. Purpose
Calculates uncertainty magnitude and prevalence bounds from contribution spread and confidence.

## 3. Equation
`StdDev = stddev(contributions)`
`UncertaintyFactor = max(min_uncertainty_factor, 1 - Confidence/100)`
`Uncertainty = StdDev * UncertaintyFactor`
`Lower = max(0, Estimated - Uncertainty)`
`Upper = max(Lower, Estimated + Uncertainty)`

## 4. Parameter provenance
- `min_uncertainty_factor=0.20`
- Source: `warehouse/formulas/coefficients.csv` (MAT-1008, PS_MAT1008_V1)

## 5. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Contributions `[6,5,4]` -> stddev `0.8165`
- Confidence `80` -> factor `max(0.2,0.2)=0.2`
- Uncertainty `0.1633`
- Bounds for estimated `15.9`: `[15.7367, 16.0633]`
