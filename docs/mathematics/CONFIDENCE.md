# CONFIDENCE

## 1. Formula identity
- Formula ID: `MAT-1005`
- Version: `v1.0` (default active), `v2.0` experimental
- Name: Confidence
- Module: `repository/mathematics/confidence.py`
- Function: `ConfidenceMathematicsEngine.evaluate`
- Lines: `9-74`

## 2. Purpose
Computes confidence score from evidence depth, study breadth, and agreement quality.

## 3. Inputs
- `observed_count` int count
- `trait_count` int count
- `env_count` int count
- `study_count` int count
- `agreement` float `%`

## 4. Equation
`EvidenceComponent = min(1, (observed_multiplier*Observed + Trait + Env) / evidence_denominator)`
`StudyComponent = min(1, StudyCount / study_denominator)`
`AgreementComponent = Agreement / 100`
`Confidence = (w_e*EvidenceComponent + w_s*StudyComponent + w_a*AgreementComponent) * 100`

## 5. Parameter provenance
- `w_e=0.45`, `w_s=0.25`, `w_a=0.30`
- `observed_multiplier=1.5`
- `evidence_denominator=20`
- `study_denominator=10`
- Source: `warehouse/formulas/coefficients.csv`, `MAT-1005`, `PS_MAT1005_V1`

## 6. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Observed=2, Trait=3, Env=1, Study=4, Agreement=88.9
- EvidenceComponent=`(1.5*2+3+1)/20=0.35`
- StudyComponent=`4/10=0.4`
- AgreementComponent=`0.889`
- Confidence=`(0.45*0.35+0.25*0.4+0.30*0.889)*100=52.92`

## 7. Interpretation audit (Ω9.3)

- This score is a **composite model confidence score**, not a direct scientific certainty posterior.
- Current components mixed in one number:
  - evidence quantity proxy (`observed`, `trait`, `env` counts),
  - study diversity proxy (`study_count`),
  - model agreement score (`MAT-1004` output).
- Publication note:
  - avoid labeling MAT-1005 as "scientific confidence" without qualifiers,
  - present it as runtime confidence weighting under configured engineering parameters.
