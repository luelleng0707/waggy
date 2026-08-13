# SYNERGY

## Formula identity
- Formula ID: `SYN-706`
- Module: `repository/optimization/synergy.py`

## Purpose
Computes synergy score from positive ingredient synergy rows.

## Equation
`SynergyScore = mean(effect_strength) * 100`

## Inputs
- `effect_strength` from `warehouse/optimization/ingredient_synergies.csv`

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- strengths `[0.62, 0.55, 0.48]`
- mean `0.55`
- score `55`
