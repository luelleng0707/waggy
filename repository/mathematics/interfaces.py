"""Interfaces for Ω9 mathematics engines."""

from __future__ import annotations

from typing import Protocol

from repository.models.runtime import EvidenceGraph
from repository.reasoning.models import ConditionAssessment

from .models import (
    AgreementMetrics,
    ConfidenceMetrics,
    EstimatedEpidemiology,
    MathematicalAssessment,
    MathematicsRuntimeResult,
    NoveltyMetrics,
    ObservedEpidemiology,
    PriorityMetrics,
    UncertaintyMetrics,
)


class ObservedEngine(Protocol):
    def evaluate(self, condition_id: str, condition_name: str, edges: tuple[dict[str, str], ...], citations: dict[str, dict[str, str]]) -> ObservedEpidemiology:
        """Compute observed prevalence metrics."""


class TraitAggregationEngine(Protocol):
    def estimate(self, condition_id: str, condition_name: str, observed: ObservedEpidemiology, edges: tuple[dict[str, str], ...]) -> EstimatedEpidemiology:
        """Compute estimated prevalence from trait/environment evidence."""


class AgreementEngine(Protocol):
    def evaluate(self, observed: ObservedEpidemiology, estimated: EstimatedEpidemiology) -> AgreementMetrics:
        """Compute agreement metrics."""


class ConfidenceEngine(Protocol):
    def evaluate(self, observed: ObservedEpidemiology, estimated: EstimatedEpidemiology, agreement: AgreementMetrics, edges: tuple[dict[str, str], ...]) -> ConfidenceMetrics:
        """Compute confidence metrics."""


class NoveltyEngine(Protocol):
    def evaluate(self, observed: ObservedEpidemiology, estimated: EstimatedEpidemiology, confidence: ConfidenceMetrics) -> NoveltyMetrics:
        """Compute novelty metrics."""


class UncertaintyEngine(Protocol):
    def evaluate(self, estimated: EstimatedEpidemiology, confidence: ConfidenceMetrics, edges: tuple[dict[str, str], ...]) -> UncertaintyMetrics:
        """Compute uncertainty bounds."""


class PriorityEngine(Protocol):
    def rank(self, condition_id: str, condition_name: str, estimated_prevalence: float, confidence: ConfidenceMetrics, agreement: AgreementMetrics, novelty: NoveltyMetrics, rank: int) -> PriorityMetrics:
        """Compute priority score/rank."""


class MathematicsRuntime(Protocol):
    def run(self, evidence_graph: EvidenceGraph, condition_assessments: tuple[ConditionAssessment, ...] = ()) -> MathematicsRuntimeResult:
        """Compute full mathematical assessments."""


class AssessmentAssembler(Protocol):
    def assemble(
        self,
        observed: ObservedEpidemiology,
        estimated: EstimatedEpidemiology,
        agreement: AgreementMetrics,
        confidence: ConfidenceMetrics,
        novelty: NoveltyMetrics,
        uncertainty: UncertaintyMetrics,
        priority: PriorityMetrics,
    ) -> MathematicalAssessment:
        """Assemble final mathematical assessment payload."""
