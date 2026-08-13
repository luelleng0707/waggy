# CALORIE_CALCULATION

## Formula identity
- IDs: `CAL-708`, `CAL-709`
- Module: `repository/optimization/calories.py`

## Purpose
Computes daily calories and percent of feeding requirement.

## Equations
- `DailyCalories = sum(servings_i * kcal_per_serving_i)`
- `PercentDailyRequirement = (DailyCalories / MaxDailyCalories) * 100`

## Inputs
- `kcal_per_serving` from `warehouse/optimization/calorie_density.csv`
- `max_daily_calories` from `warehouse/optimization/feeding_constraints.csv`

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Product A: `2 * 18 = 36`
- Product B: `1 * 22 = 22`
- Daily calories: `58`
- If max daily `420`: `58/420*100 = 13.81%`
