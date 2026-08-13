"""Versioned formula registry for Ω5.5 objectives and source planning."""

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
    "OBJ-501": FormulaDefinition(
        formula_id="OBJ-501",
        version="1.0.0",
        equation="objective_priority = estimated_prevalence * condition_objective_importance",
        description="Base priority contribution from each condition-objective relationship.",
        units="priority_points",
    ),
    "OBJ-502": FormulaDefinition(
        formula_id="OBJ-502",
        version="1.0.0",
        equation="network_bonus = sum(positive_synergy_effect where both objectives present)",
        description="Objective synergy reinforcement score.",
        units="effect_points",
    ),
    "OBJ-503": FormulaDefinition(
        formula_id="OBJ-503",
        version="1.0.0",
        equation="network_penalty = sum(conflict_effect where both objectives present)",
        description="Objective conflict penalty score.",
        units="effect_points",
    ),
    "OBJ-504": FormulaDefinition(
        formula_id="OBJ-504",
        version="1.0.0",
        equation="objective_priority_final = objective_priority * priority_multiplier",
        description="Contextual objective priority scaling from objective_priorities table.",
        units="priority_points",
    ),
    "MEC-505": FormulaDefinition(
        formula_id="MEC-505",
        version="1.0.0",
        equation="mechanism_importance = objective_priority * objective_mechanism_importance",
        description="Mechanism priority derived from objective-mechanism mapping.",
        units="priority_points",
    ),
    "ING-506": FormulaDefinition(
        formula_id="ING-506",
        version="1.0.0",
        equation="ingredient_target = sum(mechanism_importance * effect_size_percent)",
        description="Ingredient demand from mechanism coverage and observed effects.",
        units="dose_points",
    ),
    "SRC-601": FormulaDefinition(
        formula_id="SRC-601",
        version="1.0.0",
        equation="source_value = natural_amount * bioavailability_factor",
        description="Bioavailability-adjusted source amount score.",
        units="effective_amount",
    ),
    "SRC-602": FormulaDefinition(
        formula_id="SRC-602",
        version="1.0.0",
        equation="coverage_score = source_value / ingredient_target",
        description="Source coverage against required ingredient target.",
        units="coverage_ratio",
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
