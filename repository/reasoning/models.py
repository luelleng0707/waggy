"""Deterministic reasoning contracts for Ω4 scientific inference."""

from __future__ import annotations

from dataclasses import dataclass, field

from repository.models.explainability import ScientificCitation
from repository.models.runtime import EvidenceGraph, ResolvedDog


@dataclass(frozen=True)
class FormulaTrace:
    formula_id: str
    formula_version: str
    equation: str
    inputs: dict[str, float | str]
    output: float | str


@dataclass(frozen=True)
class ReasoningChainStep:
    stage: str
    condition_id: str
    condition_name: str
    summary: str
    source_fact_ids: tuple[str, ...] = field(default_factory=tuple)
    citations: tuple[ScientificCitation, ...] = field(default_factory=tuple)
    formula_traces: tuple[FormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceContribution:
    condition_id: str
    condition_name: str
    source_type: str
    source_fact_id: str
    source_trait: str
    paper_name: str
    paper_link: str
    scientific_quote: str
    weight: float
    contribution_value: float
    formula_used: str


@dataclass(frozen=True)
class ObservedCondition:
    condition_id: str
    condition_name: str
    observed_prevalence: float
    population: str
    sample_size: str
    publication_year: str
    paper: str
    quote: str
    paper_link: str
    source_fact_id: str
    citations: tuple[ScientificCitation, ...] = field(default_factory=tuple)
    formula_traces: tuple[FormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EstimatedCondition:
    condition_id: str
    condition_name: str
    estimated_prevalence: float
    contributions: tuple[EvidenceContribution, ...] = field(default_factory=tuple)
    citations: tuple[ScientificCitation, ...] = field(default_factory=tuple)
    formula_traces: tuple[FormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AgreementResult:
    condition_id: str
    condition_name: str
    observed: float
    estimated: float
    absolute_difference: float
    relative_difference: float
    agreement_percentage: float
    formula_traces: tuple[FormulaTrace, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EmergingCondition:
    condition_id: str
    condition_name: str
    estimated_prevalence: float
    supporting_traits: tuple[str, ...]
    supporting_papers: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    reasoning_chain: tuple[ReasoningChainStep, ...]


@dataclass(frozen=True)
class ConditionAssessment:
    condition_id: str
    condition_name: str
    observed_prevalence: float | None
    estimated_prevalence: float
    agreement_percentage: float | None
    research_gap_status: str
    body_system: str
    required_mechanisms: tuple[str, ...]
    supporting_papers: tuple[str, ...]
    supporting_quotes: tuple[str, ...]
    formula_ids_used: tuple[str, ...]
    citations: tuple[ScientificCitation, ...]
    reasoning_chain: tuple[ReasoningChainStep, ...]
    formula_traces: tuple[FormulaTrace, ...]
    runtime_trace_stage_ids: tuple[str, ...]


@dataclass(frozen=True)
class ConditionAssessmentInput:
    resolved_dog: ResolvedDog
    evidence_graph: EvidenceGraph


@dataclass(frozen=True)
class StageRuntimeTrace:
    stage_name: str
    execution_time_ms: float
    formula_ids: tuple[str, ...]
    warehouse_rows_used: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    condition_ids: tuple[str, ...]
    input_summary: str
    output_summary: str
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReasoningRuntimeTrace:
    run_id: str
    stages: tuple[StageRuntimeTrace, ...] = field(default_factory=tuple)
