# REASONING_AGREEMENT (Ω4)

## Formula identities
- `AGR-001`: absolute difference
- `AGR-002`: relative difference
- `AGR-003`: agreement percentage
- Implementation: `repository/reasoning/agreement/engine.py`, `repository/reasoning/mathematics/formulas.py`

## Equations
- `AGR-001: |Observed - Estimated|`
- `AGR-002: AGR-001 / Observed`
- `AGR-003: max(0, 100 - AGR-002*100)`

## Inputs
- observed prevalence
- estimated prevalence

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Observed `17`, Estimated `16`
- Absolute `1`
- Relative `1/17 = 0.05882`
- Agreement `94.118`
