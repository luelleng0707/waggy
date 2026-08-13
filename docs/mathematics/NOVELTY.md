# NOVELTY

## 1. Formula identity
- Formula ID: `MAT-1006`
- Version: `v1.0`
- Module: `repository/mathematics/novelty.py`
- Function: `NoveltyMathematicsEngine.evaluate`
- Lines: `9-63`

## 2. Purpose
Scores novelty from positive estimated-vs-observed delta scaled by confidence and flags emerging concerns.

## 3. Equation
`Delta = max(0, Estimated - Observed)`
`Novelty = Delta * (Confidence/100)`
`EmergingConcern = (Observed <= Omax) and (Estimated >= Emin) and (Confidence >= Cmin)`

## 4. Parameters
- `Omax=0.5`, `Emin=10.0`, `Cmin=70.0`
- Source: `warehouse/formulas/coefficients.csv` (MAT-1006, PS_MAT1006_V1)

## 5. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Observed `0`, Estimated `18`, Confidence `80`
- Delta `18`
- Novelty `18*0.8=14.4`
- Emerging concern = true
