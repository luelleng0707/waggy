"""Centralized versioned scientific formula registry for Ω4 reasoning."""

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
    "EST-001": FormulaDefinition(
        formula_id="EST-001",
        version="1.0.0",
        equation="canonical_percentage(x) = x*100 when x<=1 else x",
        description="Normalize ratio or percent-like prevalence value into percentage units.",
        units="percent",
    ),
    "EST-002": FormulaDefinition(
        formula_id="EST-002",
        version="1.0.0",
        equation="contribution = canonical_percentage(value) * weight",
        description="Contribution value for trait/environment/life-stage/activity/ingredient evidence edges.",
        units="percent",
    ),
    "EST-003": FormulaDefinition(
        formula_id="EST-003",
        version="1.0.0",
        equation="contribution_from_factor = (factor - 1) * baseline_percent",
        description="Convert interaction factor into additive percentage delta using baseline prevalence.",
        units="percent",
    ),
    "EST-004": FormulaDefinition(
        formula_id="EST-004",
        version="1.0.0",
        equation="estimated_prevalence = sum(contributions) / count(contributions)",
        description="Deterministic estimate from mean of evidence contributions.",
        units="percent",
    ),
    "AGR-001": FormulaDefinition(
        formula_id="AGR-001",
        version="1.0.0",
        equation="absolute_difference = abs(observed - estimated)",
        description="Absolute gap between observed and estimated prevalence.",
        units="percent",
    ),
    "AGR-002": FormulaDefinition(
        formula_id="AGR-002",
        version="1.0.0",
        equation="relative_difference = absolute_difference / observed",
        description="Relative gap ratio when observed prevalence is non-zero.",
        units="ratio",
    ),
    "AGR-003": FormulaDefinition(
        formula_id="AGR-003",
        version="1.0.0",
        equation="agreement_percentage = max(0, 100 - relative_difference*100)",
        description="Agreement percentage derived strictly from relative difference.",
        units="percent",
    ),
    "SYS-001": FormulaDefinition(
        formula_id="SYS-001",
        version="1.0.0",
        equation="system(condition) -> lookup(condition_systems.csv)",
        description="Body system mapping is direct warehouse lookup, no numerical transform.",
        units="categorical",
    ),
    "MEC-001": FormulaDefinition(
        formula_id="MEC-001",
        version="1.0.0",
        equation="mechanisms(condition) -> lookup(condition_mechanisms.csv)",
        description="Required mechanisms are direct warehouse lookup, no scoring.",
        units="categorical",
    ),
}


def numeric_or_zero(value: str | float | int | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def canonical_percentage(value: str | float | int | None) -> float:
    num = numeric_or_zero(value)
    if num <= 1.0:
        return num * 100.0
    return num


def contribution_from_factor(factor: str | float | int | None, baseline_percent: float) -> float:
    f = numeric_or_zero(factor)
    return (f - 1.0) * baseline_percent


def estimated_prevalence(contributions: tuple[float, ...]) -> float:
    if not contributions:
        return 0.0
    return sum(contributions) / float(len(contributions))


def agreement_absolute_difference(observed: float, estimated: float) -> float:
    return abs(observed - estimated)


def agreement_relative_difference(observed: float, estimated: float) -> float:
    if observed == 0.0:
        return 0.0
    return agreement_absolute_difference(observed, estimated) / observed


def agreement_percentage(observed: float, estimated: float) -> float:
    rel = agreement_relative_difference(observed, estimated)
    return max(0.0, 100.0 - (rel * 100.0))
