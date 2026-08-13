# HARMONY

## Formula identity
- Formula ID: `HRM-711`
- Module: `repository/optimization/harmony.py`

## Purpose
Computes deterministic final candidate score from independent dimensions.

## Equation
`Harmony = 0.30*Coverage + 0.20*Dose + 0.15*Absorption + 0.10*Synergy + 0.10*Calories + 0.10*Constraints - 0.05*Conflict`

## Code mapping
- Weights are literal in `DeterministicHarmonyCalculator.calculate`.
- `calories_percent` uses helper `_calorie_score`.
- `constraint_satisfaction` uses passed/total ratio.

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Coverage 95, Dose 94, Absorption 92, Synergy 89, Calories 97, Constraints 100, Conflict 3
- Harmony `= 0.30*95 + 0.20*94 + 0.15*92 + 0.10*89 + 0.10*97 + 0.10*100 - 0.05*3`
- Harmony `= 89.55`
