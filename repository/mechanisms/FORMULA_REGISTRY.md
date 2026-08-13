# Ω5 Formula Registry

This registry defines deterministic and versioned formulas used by the Ω5 biological mechanism and dose network.

## OBJ-001
- **Version:** `1.0.0`
- **Equation:** `objective = deterministic lookup(condition_id)`
- **Purpose:** Create a biological objective layer between condition and mechanism.

## MEC-201
- **Version:** `1.0.0`
- **Equation:** `condition_mechanism_importance = estimated_prevalence * importance_weight / 100`
- **Purpose:** Convert clinical priority into condition-specific mechanism contribution.

## MEC-202
- **Version:** `1.0.0`
- **Equation:** `mechanism_importance = sum(condition_mechanism_importance)`
- **Purpose:** Aggregate multiple condition contributions into a single mechanism importance value.

## DOS-301
- **Version:** `1.0.0`
- **Equation:** `baseline_amount = dose_mg_per_kg * reference_weight_kg`
- **Purpose:** Convert warehouse dose-response rows into a baseline absolute target.

## DOS-302
- **Version:** `1.0.0`
- **Equation:** `target_amount = baseline_amount * mechanism_importance_scalar`
- **Purpose:** Scale baseline dose by biological demand and profile factors.

## INT-401
- **Version:** `1.0.0`
- **Equation:** `interaction eligibility = ingredient_a in set and ingredient_b in set`
- **Purpose:** Determine which interaction rows apply to current dose targets.

## INT-402
- **Version:** `1.0.0`
- **Equation:** `missing cofactor = required_factor not present in target ingredient set`
- **Purpose:** Flag required but absent cofactors from absorption evidence.
