# CONSTRAINTS

## Formula identity
- Formula ID: `CST-710`
- Module: `repository/optimization/constraints.py`

## Purpose
Evaluates candidate feasibility across serving, package, life-stage, weight, availability, and calorie constraints.

## Equation
`ConstraintSatisfaction% = passed_constraints / total_constraints * 100`

## Inputs
- serving rules: `warehouse/optimization/product_servings.csv`
- package rules: `warehouse/optimization/package_constraints.csv`
- feeding rules: `warehouse/optimization/feeding_constraints.csv`

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Passed 11 of 12 checks
- Satisfaction `91.67%`
