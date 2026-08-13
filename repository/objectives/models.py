"""Ω5.5 deterministic objective-network models."""

from __future__ import annotations

from dataclasses import dataclass, field

from repository.mechanisms.models import MechanismPlan


@dataclass(frozen=True)
class ObjectiveConditionLink:
    condition_id: str
    condition_name: str
    condition_prevalence: float
    importance: float
    scientific_quote: str
    paper_name: str
    paper_link: str


@dataclass(frozen=True)
class ObjectivePlan:
    objective_id: str
    objective_name: str
    objective_description: str
    supporting_conditions: tuple[ObjectiveConditionLink, ...]
    objective_priority: float
    supporting_papers: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    formula_ids_used: tuple[str, ...]
    warehouse_rows_used: tuple[str, ...]


@dataclass(frozen=True)
class ObjectiveNetworkSummary:
    synergies: tuple[str, ...] = field(default_factory=tuple)
    conflicts: tuple[str, ...] = field(default_factory=tuple)
    formula_ids_used: tuple[str, ...] = field(default_factory=tuple)
    warehouse_rows_used: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IngredientPlan:
    ingredient_id: str
    ingredient_name: str
    source_mechanisms: tuple[str, ...]
    source_objectives: tuple[str, ...]
    target_amount: float
    unit: str
    formula_ids_used: tuple[str, ...]
    supporting_papers: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    warehouse_rows_used: tuple[str, ...]


@dataclass(frozen=True)
class IngredientSourcePlan:
    source_id: str
    ingredient_id: str
    ingredient_name: str
    natural_amount: float
    unit: str
    bioavailability: float
    coverage_score: float
    formula_ids_used: tuple[str, ...]
    supporting_papers: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    warehouse_rows_used: tuple[str, ...]


@dataclass(frozen=True)
class ObjectiveStageTrace:
    stage_name: str
    execution_time_ms: float
    formula_ids: tuple[str, ...] = field(default_factory=tuple)
    warehouse_rows_used: tuple[str, ...] = field(default_factory=tuple)
    input_summary: str = ""
    output_summary: str = ""


@dataclass(frozen=True)
class ObjectiveRuntimeTrace:
    run_id: str
    stages: tuple[ObjectiveStageTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ObjectiveRuntimeResult:
    objective_plan: tuple[ObjectivePlan, ...]
    mechanism_plan: tuple[MechanismPlan, ...]
    ingredient_plan: tuple[IngredientPlan, ...]
    ingredient_source_plan: tuple[IngredientSourcePlan, ...]
    network_summary: ObjectiveNetworkSummary
    trace: ObjectiveRuntimeTrace
