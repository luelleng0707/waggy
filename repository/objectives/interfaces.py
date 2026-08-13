"""Single-method contracts for Ω5.5 objective architecture."""

from __future__ import annotations

from typing import Protocol

from repository.reasoning.models import ConditionAssessment

from .models import ObjectiveNetworkSummary, ObjectivePlan, ObjectiveStageTrace


class ObjectiveResolver(Protocol):
    def resolve(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[ObjectivePlan, ...]:
        """Resolve condition assessments into objective candidates."""


class ObjectivePlanner(Protocol):
    def plan(self, objectives: tuple[ObjectivePlan, ...]) -> tuple[ObjectivePlan, ...]:
        """Apply objective-priority multipliers to produce final objective plans."""


class ObjectiveNetwork(Protocol):
    def map(self, objectives: tuple[ObjectivePlan, ...]) -> ObjectiveNetworkSummary:
        """Map objective synergies and conflicts from immutable warehouse evidence."""


class ObjectiveTraceBuilder(Protocol):
    def build(
        self,
        stage_name: str,
        execution_time_ms: float,
        formula_ids: tuple[str, ...],
        warehouse_rows_used: tuple[str, ...],
        input_summary: str,
        output_summary: str,
    ) -> ObjectiveStageTrace:
        """Create deterministic stage trace entries."""
