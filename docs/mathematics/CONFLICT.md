# CONFLICT

## Formula identity
- Formula ID: `CON-707`
- Module: `repository/optimization/conflict.py`

## Purpose
Computes conflict penalty from negative interaction rows.

## Equation
`ConflictPenalty = mean(penalty_strength) * 100`

## Inputs
- `penalty_strength` from `warehouse/optimization/ingredient_conflicts.csv`

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- penalties `[0.21, 0.08]`
- mean `0.145`
- conflict penalty `14.5`
