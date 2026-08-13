"""Versioned deterministic formulas for Ω5 mechanism network."""

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
    "OBJ-001": FormulaDefinition(
        formula_id="OBJ-001",
        version="1.0.0",
        equation="objective = deterministic lookup(condition_id)",
        description="Maps each condition to one or more biological objectives.",
        units="categorical",
    ),
    "MEC-201": FormulaDefinition(
        formula_id="MEC-201",
        version="1.0.0",
        equation="condition_mechanism_importance = estimated_prevalence * importance_weight / 100",
        description="Condition contribution into mechanism demand using warehouse importance.",
        units="priority_points",
    ),
    "MEC-202": FormulaDefinition(
        formula_id="MEC-202",
        version="1.0.0",
        equation="mechanism_importance = sum(condition_mechanism_importance)",
        description="Aggregates condition-level contributions for each mechanism.",
        units="priority_points",
    ),
    "DOS-301": FormulaDefinition(
        formula_id="DOS-301",
        version="1.0.0",
        equation="baseline_amount = dose_mg_per_kg * reference_weight_kg",
        description="Converts dose-response mg/kg rows into absolute daily amount using deterministic reference weight.",
        units="mg_per_day",
    ),
    "DOS-302": FormulaDefinition(
        formula_id="DOS-302",
        version="1.0.0",
        equation="target_amount = baseline_amount * mechanism_importance_scalar",
        description="Scales baseline biological target by mechanism demand from Ω5 planning.",
        units="dose_unit_per_day",
    ),
    "INT-401": FormulaDefinition(
        formula_id="INT-401",
        version="1.0.0",
        equation="interaction eligibility = ingredient_a in set and ingredient_b in set",
        description="Deterministically filters interaction rows to current target ingredient set.",
        units="boolean",
    ),
    "INT-402": FormulaDefinition(
        formula_id="INT-402",
        version="1.0.0",
        equation="missing cofactor = required_factor not present in target ingredient set",
        description="Flags absent cofactors from absorption_factors evidence.",
        units="boolean",
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
