# PRIORITY

## 1. Formula identity
- Formula ID: `MAT-1007`
- Version: `v1.0`
- Module: `repository/mathematics/priority.py`
- Function: `PriorityMathematicsEngine.rank`
- Lines: `9-61`

## 2. Purpose
Ranks conditions by prevalence burden adjusted by confidence, novelty, and agreement.

## 3. Equation
`AgreementScale = max(min_agreement_scale, Agreement/100)`
`NoveltyMultiplier = 1 + Novelty/100`
`Priority = Estimated * (Confidence/100) * NoveltyMultiplier * AgreementScale`

## 4. Parameter provenance
- `min_agreement_scale=0.10`
- Source: `warehouse/formulas/coefficients.csv` (MAT-1007, PS_MAT1007_V1)

## 5. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Estimated `22`, Confidence `76`, Novelty `4`, Agreement `90`
- Scale `0.9`, Multiplier `1.04`
- Priority `22*0.76*1.04*0.9=15.6442`
