"""Ω5 deterministic models: ConditionAssessment[] -> mechanism network outputs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BiologicalObjective:
    objective_id: str
    objective_name: str
    rationale: str


@dataclass(frozen=True)
class MechanismConditionLink:
    condition_id: str
    condition_name: str
    importance_weight: float
    scientific_quote: str
    paper_name: str
    paper_link: str


@dataclass(frozen=True)
class MechanismNeed:
    mechanism_id: str
    mechanism_name: str
    description: str
    objective: BiologicalObjective
    supporting_conditions: tuple[MechanismConditionLink, ...] = field(default_factory=tuple)
    aggregate_importance: float = 0.0
    formula_ids_used: tuple[str, ...] = field(default_factory=tuple)
    warehouse_rows_used: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MechanismPlan:
    mechanism_id: str
    mechanism: str
    objective: str
    supporting_conditions: tuple[str, ...]
    importance: float
    supporting_papers: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    formula_ids_used: tuple[str, ...]
    dose_formula_ids: tuple[str, ...]
    interaction_notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DoseTarget:
    ingredient_id: str
    ingredient_name: str
    desired_amount: float
    unit: str
    formula_id: str
    reasoning: str
    papers: tuple[str, ...]
    quotes: tuple[str, ...]
    mechanisms_supported: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class InteractionFinding:
    finding_type: str
    ingredient_a: str
    ingredient_b: str
    effect_strength: float
    scientific_quote: str
    paper_name: str
    paper_link: str


@dataclass(frozen=True)
class InteractionReport:
    positive_synergies: tuple[InteractionFinding, ...] = field(default_factory=tuple)
    negative_interactions: tuple[InteractionFinding, ...] = field(default_factory=tuple)
    missing_cofactors: tuple[str, ...] = field(default_factory=tuple)
    absorption_enhancers: tuple[InteractionFinding, ...] = field(default_factory=tuple)
    absorption_inhibitors: tuple[InteractionFinding, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StageMechanismTrace:
    stage_name: str
    execution_time_ms: float
    formula_ids: tuple[str, ...] = field(default_factory=tuple)
    warehouse_rows_used: tuple[str, ...] = field(default_factory=tuple)
    input_summary: str = ""
    output_summary: str = ""
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MechanismRuntimeTrace:
    run_id: str
    stages: tuple[StageMechanismTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MechanismRuntimeResult:
    mechanism_plan: tuple[MechanismPlan, ...]
    dose_targets: tuple[DoseTarget, ...]
    interaction_report: InteractionReport
    trace: MechanismRuntimeTrace
