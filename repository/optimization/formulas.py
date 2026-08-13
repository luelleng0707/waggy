"""Versioned Ω6 optimization formulas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormulaDefinition:
    formula_id: str
    version: str
    equation: str
    description: str
    units: str


FORMULA_REGISTRY: dict[str, FormulaDefinition] = {
    "TGT-701": FormulaDefinition(
        "TGT-701",
        "1.0.0",
        "required_amount = mean(source_natural_amount / max(source_bioavailability, 0.01))",
        "Target daily intake estimation from IngredientSourcePlan baseline amounts.",
        "ingredient_unit_per_day",
    ),
    "CND-702": FormulaDefinition(
        "CND-702",
        "1.0.0",
        "candidate_space = cartesian_product(product_serving_ranges)",
        "Deterministic candidate enumeration from product serving bounds.",
        "candidate_count",
    ),
    "COV-703": FormulaDefinition(
        "COV-703",
        "1.0.0",
        "coverage_percent = (provided / required) * 100",
        "Ingredient-level coverage percentage.",
        "percent",
    ),
    "COV-704": FormulaDefinition(
        "COV-704",
        "1.0.0",
        "dose_accuracy = max(0, 100 - mean(abs(coverage_percent - 100)))",
        "Dose accuracy derived from deviation to exact target.",
        "percent",
    ),
    "ABS-705": FormulaDefinition(
        "ABS-705",
        "1.0.0",
        "absorption_score = mean(effect_factor) * 100",
        "Absorption score from factual ingredient interactions.",
        "percent",
    ),
    "SYN-706": FormulaDefinition(
        "SYN-706",
        "1.0.0",
        "synergy_score = mean(effect_strength) * 100",
        "Synergy score from ingredient_synergies table.",
        "percent",
    ),
    "CON-707": FormulaDefinition(
        "CON-707",
        "1.0.0",
        "conflict_penalty = mean(penalty_strength) * 100",
        "Conflict penalty from ingredient_conflicts table.",
        "percent",
    ),
    "CAL-708": FormulaDefinition(
        "CAL-708",
        "1.0.0",
        "daily_calories = sum(servings * kcal_per_serving)",
        "Daily caloric burden from candidate product servings.",
        "kcal_per_day",
    ),
    "CAL-709": FormulaDefinition(
        "CAL-709",
        "1.0.0",
        "calorie_percent = (daily_calories / max_daily_calories) * 100",
        "Percentage of daily calorie allowance consumed by bundle candidate.",
        "percent",
    ),
    "CST-710": FormulaDefinition(
        "CST-710",
        "1.0.0",
        "constraint_satisfaction = passed_constraints / total_constraints",
        "Constraint satisfaction percentage.",
        "percent",
    ),
    "HRM-711": FormulaDefinition(
        "HRM-711",
        "1.0.0",
        "harmony = 0.30*coverage + 0.20*dose + 0.15*absorption + 0.10*synergy + 0.10*calories + 0.10*constraints - 0.05*conflict",
        "Final deterministic harmony score.",
        "score_percent",
    ),
    "OPT-712": FormulaDefinition(
        "OPT-712",
        "1.0.0",
        "optimized_bundle = argmax(harmony_score) over feasible candidates",
        "Deterministic optimizer objective and tie-break order.",
        "candidate_id",
    ),
}


def as_float(value: str | float | int | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0
