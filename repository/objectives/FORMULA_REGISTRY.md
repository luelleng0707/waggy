# Ω5.5 Formula Registry

Versioned formulas for deterministic objective and source planning.

## Objective Formulas

- `OBJ-501`: Objective priority from `ConditionAssessment.estimated_prevalence * condition_objectives.importance`.
- `OBJ-502`: Objective synergy contribution from `objective_synergies.csv`.
- `OBJ-503`: Objective conflict contribution from `objective_conflicts.csv`.
- `OBJ-504`: Objective contextual scaling from `objective_priorities.csv`.

## Mechanism/Ingredient Projection

- `MEC-505`: Mechanism importance from `objective_priority * objective_mechanisms.importance`.
- `ING-506`: Ingredient target demand from mechanism importance and `ingredient_mechanisms.effect_size`.

## Source Formulas

- `SRC-601`: Source effective amount from `natural_amount * bioavailability_factor`.
- `SRC-602`: Source coverage from `source_effective_amount / ingredient_target`.
