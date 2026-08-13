"""Immutable Ω9 mathematics models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MathematicalFormulaTrace:
    formula_id: str
    formula_version: str
    formula_name: str = ""
    status: str = ""
    equation: str = ""
    substituted_equation: str = ""
    python_file: str = ""
    python_function: str = ""
    source_line_start: int = 0
    source_line_end: int = 0
    input_variables: tuple[str, ...] = field(default_factory=tuple)
    inputs: dict[str, float | int | str] = field(default_factory=dict)
    parameter_values: dict[str, float | int | str] = field(default_factory=dict)
    intermediate_values: dict[str, float | int | str] = field(default_factory=dict)
    output_variable: str = ""
    unit: str = ""
    warehouse_row_ids: tuple[str, ...] = field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    paper_names: tuple[str, ...] = field(default_factory=tuple)
    paper_links: tuple[str, ...] = field(default_factory=tuple)
    scientific_quotes: tuple[str, ...] = field(default_factory=tuple)
    output: float | int | str = 0.0


@dataclass(frozen=True)
class ObservedEpidemiology:
    condition_id: str
    condition_name: str
    observed_prevalence: float
    evidence_count: int
    supporting_quotes: tuple[str, ...] = field(default_factory=tuple)
    supporting_papers: tuple[str, ...] = field(default_factory=tuple)
    supporting_links: tuple[str, ...] = field(default_factory=tuple)
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EstimatedEpidemiology:
    condition_id: str
    condition_name: str
    estimated_prevalence: float
    trait_prevalence: float
    environment_prevalence: float
    interaction_adjustment: float
    evidence_count: int
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AgreementMetrics:
    condition_id: str
    condition_name: str
    absolute_error: float
    relative_error: float
    agreement_percent: float
    normalized_agreement: float
    prediction_error: float
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ConfidenceMetrics:
    condition_id: str
    condition_name: str
    confidence_score: float
    observed_evidence_count: int
    trait_evidence_count: int
    environmental_evidence_count: int
    study_count: int
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class NoveltyMetrics:
    condition_id: str
    condition_name: str
    novelty_score: float
    emerging_biological_concern: bool
    rationale: str
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class UncertaintyMetrics:
    condition_id: str
    condition_name: str
    lower_bound: float
    upper_bound: float
    uncertainty: float
    evidence_count: int
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PriorityMetrics:
    condition_id: str
    condition_name: str
    priority_score: float
    priority_rank: int
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MathematicalAssessment:
    condition_id: str
    condition_name: str
    observed_prevalence: float
    estimated_prevalence: float
    confidence: float
    agreement: float
    priority: float
    novelty: float
    uncertainty: float
    lower_bound: float
    upper_bound: float
    supporting_formulas: tuple[str, ...] = field(default_factory=tuple)
    supporting_quotes: tuple[str, ...] = field(default_factory=tuple)
    supporting_papers: tuple[str, ...] = field(default_factory=tuple)
    supporting_links: tuple[str, ...] = field(default_factory=tuple)
    supporting_evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    formula_traces: tuple[MathematicalFormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MathematicsStageTrace:
    stage_name: str
    formula_ids: tuple[str, ...]
    input_summary: str
    output_summary: str
    elapsed_ms: float


@dataclass(frozen=True)
class MathematicsTrace:
    run_id: str
    stages: tuple[MathematicsStageTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MathematicsRuntimeResult:
    assessments: tuple[MathematicalAssessment, ...]
    trace: MathematicsTrace
