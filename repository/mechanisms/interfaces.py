"""Single-method contracts for Ω5 mechanism network stages."""

from __future__ import annotations

from typing import Protocol

from repository.reasoning.models import ConditionAssessment

from .models import DoseTarget, InteractionReport, MechanismNeed, MechanismPlan, StageMechanismTrace


class MechanismResolver(Protocol):
    def resolve(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[MechanismNeed, ...]:
        """Resolve condition priorities into mechanism needs from warehouse facts."""


class MechanismPlanner(Protocol):
    def plan(self, needs: tuple[MechanismNeed, ...]) -> tuple[MechanismPlan, ...]:
        """Aggregate mechanism needs into deterministic biological mechanism plans."""


class DosePlanner(Protocol):
    def plan(
        self,
        mechanism_plan: tuple[MechanismPlan, ...],
        assessments: tuple[ConditionAssessment, ...],
        profile_context: dict[str, str | float] | None = None,
    ) -> tuple[DoseTarget, ...]:
        """Generate deterministic dose targets from observed dose-response evidence."""


class InteractionAnalyzer(Protocol):
    def analyze(self, dose_targets: tuple[DoseTarget, ...]) -> InteractionReport:
        """Analyze synergies, conflicts, and cofactor constraints for target ingredients."""


class MechanismTraceBuilder(Protocol):
    def build(
        self,
        stage_name: str,
        execution_time_ms: float,
        formula_ids: tuple[str, ...],
        warehouse_rows_used: tuple[str, ...],
        input_summary: str,
        output_summary: str,
        warnings: tuple[str, ...] = (),
    ) -> StageMechanismTrace:
        """Build immutable stage trace records for Ω5 runtime."""
