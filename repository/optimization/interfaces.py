"""Single-method Ω6 optimization interfaces."""

from __future__ import annotations

from typing import Protocol

from repository.objectives.models import IngredientSourcePlan

from .models import (
    BundleCandidate,
    BundleConstraint,
    CalorieReport,
    CoverageReport,
    HarmonyReport,
    InteractionReport,
    OptimizedBundle,
    OptimizationTrace,
    TargetIntakePlan,
)


class TargetIntakePlanner(Protocol):
    def plan(self, source_plan: tuple[IngredientSourcePlan, ...]) -> TargetIntakePlan:
        """Create target intake plan from ingredient source outputs."""


class CandidateGenerator(Protocol):
    def generate(self, target_plan: TargetIntakePlan) -> tuple[BundleCandidate, ...]:
        """Enumerate deterministic bundle candidates."""


class CoverageCalculator(Protocol):
    def calculate(self, candidate: BundleCandidate, target_plan: TargetIntakePlan) -> CoverageReport:
        """Calculate ingredient coverage for one candidate."""


class AbsorptionCalculator(Protocol):
    def calculate(self, candidate: BundleCandidate) -> InteractionReport:
        """Calculate absorption effects from interactions."""


class SynergyCalculator(Protocol):
    def calculate(self, candidate: BundleCandidate, report: InteractionReport) -> InteractionReport:
        """Calculate positive synergy effects."""


class ConflictCalculator(Protocol):
    def calculate(self, candidate: BundleCandidate, report: InteractionReport) -> InteractionReport:
        """Calculate conflict penalties."""


class CalorieCalculator(Protocol):
    def calculate(self, candidate: BundleCandidate, life_stage: str, weight_kg: float) -> CalorieReport:
        """Calculate calorie burden metrics."""


class ConstraintChecker(Protocol):
    def check(
        self,
        candidate: BundleCandidate,
        calorie_report: CalorieReport,
        life_stage: str,
        weight_kg: float,
    ) -> tuple[BundleConstraint, ...]:
        """Evaluate constraints and return deterministic pass/fail records."""


class HarmonyCalculator(Protocol):
    def calculate(
        self,
        coverage: CoverageReport,
        interactions: InteractionReport,
        calories: CalorieReport,
        constraints: tuple[BundleConstraint, ...],
    ) -> HarmonyReport:
        """Calculate deterministic harmony score."""


class BundleOptimizer(Protocol):
    def optimize(
        self,
        candidates: tuple[OptimizedBundle, ...],
    ) -> OptimizedBundle:
        """Select best feasible optimized bundle candidate."""


class TraceBuilder(Protocol):
    def build(self, run_id: str, stages: tuple[dict[str, object], ...]) -> OptimizationTrace:
        """Build immutable optimization trace object."""
