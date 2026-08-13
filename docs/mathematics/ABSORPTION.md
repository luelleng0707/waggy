# ABSORPTION

## Formula identity
- Formula ID: `ABS-705`
- Module: `repository/optimization/absorption.py`

## Purpose
Computes absorption score from factual ingredient interaction effect factors.

## Equation
`AbsorptionScore = mean(effect_factor) * 100`

## Inputs
- `effect_factor` from `warehouse/optimization/ingredient_interactions.csv`
- ingredient presence from candidate composition.

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- factors `[1.08, 1.04, 0.97]`
- mean `1.03`
- score `103.0`
