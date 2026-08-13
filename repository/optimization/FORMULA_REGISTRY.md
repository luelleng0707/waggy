# Ω6 Formula Registry

Versioned deterministic formulas used by the optimization layer.

## TGT-701 — Target Intake
- Equation: `required_amount = mean(source_natural_amount / max(source_bioavailability, 0.01))`
- Purpose: Build `TargetIntakePlan` from `IngredientSourcePlan[]`.

## CND-702 — Candidate Enumeration
- Equation: `candidate_space = cartesian_product(product_serving_ranges)`
- Purpose: Exhaustively enumerate product-serving combinations.

## COV-703 — Ingredient Coverage
- Equation: `coverage_percent = (provided / required) * 100`
- Purpose: Measure per-ingredient target coverage.

## COV-704 — Dose Accuracy
- Equation: `dose_accuracy = max(0, 100 - mean(abs(coverage - 100)))`
- Purpose: Penalize over/under-provision distance from exact dose.

## ABS-705 — Absorption
- Equation: `absorption_score = mean(effect_factor) * 100`
- Purpose: Aggregate interaction effects from `ingredient_interactions.csv`.

## SYN-706 — Synergy
- Equation: `synergy_score = mean(effect_strength) * 100`
- Purpose: Aggregate positive synergies from `ingredient_synergies.csv`.

## CON-707 — Conflict
- Equation: `conflict_penalty = mean(penalty_strength) * 100`
- Purpose: Aggregate negative interactions from `ingredient_conflicts.csv`.

## CAL-708 — Daily Calories
- Equation: `daily_calories = sum(servings * kcal_per_serving)`
- Purpose: Compute caloric burden per candidate.

## CAL-709 — Daily Requirement Share
- Equation: `calorie_percent = (daily_calories / max_daily_calories) * 100`
- Purpose: Measure calorie load versus feeding constraint.

## CST-710 — Constraint Satisfaction
- Equation: `constraint_satisfaction = passed_constraints / total_constraints`
- Purpose: Quantify hard-rule pass rate.

## HRM-711 — Harmony
- Equation: `0.30*coverage + 0.20*dose + 0.15*absorption + 0.10*synergy + 0.10*calories + 0.10*constraints - 0.05*conflict`
- Purpose: Deterministic objective function for candidate ranking.

## OPT-712 — Optimizer
- Equation: `optimized_bundle = argmax(harmony_score) over feasible candidates`
- Purpose: Select top feasible bundle deterministically.
