# REASONING_ESTIMATION (Ω4)

## Formula identities
- `EST-001` canonical percentage normalization
- `EST-002` contribution = normalized value * weight
- `EST-003` interaction factor delta
- `EST-004` estimated prevalence mean
- Implementation: `repository/reasoning/estimation/engine.py`, `repository/reasoning/mathematics/formulas.py`

## Equations
- `EST-001: canonical_percentage(x) = x*100 when x<=1 else x`
- `EST-002: contribution = canonical_percentage(value) * weight`
- `EST-003: factor_delta = (factor - 1) * baseline_percent`
- `EST-004: estimated_prevalence = mean(contributions)`

## Inputs
- edge `value_number`, `factor`, `effect_direction`, `weight` from evidence graph edges.

## Parameter provenance
- Weight constants currently coded in `repository/reasoning/estimation/engine.py`.
- PARAMETER_STATUS = ENGINEERING_ASSUMPTION.

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- normalized values: `18, 12, 9`
- weighted contributions: `9, 4.8, 2.7`
- estimate: `(9+4.8+2.7)/3 = 5.5`
