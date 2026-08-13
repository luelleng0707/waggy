# MECHANISM_OBJECTIVE

## Formula identity
- IDs: `OBJ-501`, `OBJ-502`, `OBJ-503`, `OBJ-504`, `MEC-505`
- Version: `1.0.0`
- Modules: `repository/objectives/runtime.py`

## Purpose
Maps conditions to objectives, applies objective priority scaling, then projects objectives to mechanisms.

## Core equations
- `OBJ-501`: `ObjectivePriority = EstimatedPrevalence * ConditionObjectiveImportance`
- `OBJ-504`: `ObjectivePriorityFinal = ObjectivePriority * PriorityMultiplier`
- `MEC-505`: `MechanismImportance = ObjectivePriorityFinal * ObjectiveMechanismImportance`

## Parameter provenance
- Priority multipliers from `warehouse/objectives/objective_priorities.csv`
- Coefficients are data-driven by row importance values.

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Estimated `62`, condition-objective `0.92` -> `57.04`
- Multiplier `1.08` -> `61.6032`
- Objective-mechanism `0.95` -> mechanism `58.523`
