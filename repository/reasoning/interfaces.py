"""Deterministic mathematical stage contracts for Ω4 reasoning."""

from __future__ import annotations

from typing import Protocol

from repository.models.runtime import EvidenceGraph, ResolvedDog
from .models import (
    AgreementResult,
    ConditionAssessment,
    EstimatedCondition,
    ObservedCondition,
)


class ObservedEngine(Protocol):
    def evaluate(self, evidence_graph: EvidenceGraph) -> tuple[ObservedCondition, ...]:
        """Retrieve published observed epidemiology exactly as stored in evidence graph."""


class EstimatedEngine(Protocol):
    def evaluate(
        self,
        resolved_dog: ResolvedDog,
        evidence_graph: EvidenceGraph,
    ) -> tuple[EstimatedCondition, ...]:
        """Compute deterministic biological estimates from evidence contributions."""


class AgreementEngine(Protocol):
    def evaluate(
        self,
        observed: tuple[ObservedCondition, ...],
        estimated: tuple[EstimatedCondition, ...],
    ) -> tuple[AgreementResult, ...]:
        """Compute objective agreement metrics between observed and estimated values."""


class SystemAggregator(Protocol):
    def aggregate(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[ConditionAssessment, ...]:
        """Attach body-system aggregation attributes from warehouse mappings."""


class MechanismMapper(Protocol):
    def map(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[ConditionAssessment, ...]:
        """Attach mechanism requirements from warehouse mappings."""


class ConditionAssessmentBuilder(Protocol):
    def build(
        self,
        observed: tuple[ObservedCondition, ...],
        estimated: tuple[EstimatedCondition, ...],
        agreement: tuple[AgreementResult, ...],
    ) -> tuple[ConditionAssessment, ...]:
        """Build final Ω4 output: deterministic ConditionAssessment[] only."""
