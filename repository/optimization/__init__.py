"""Ω6 deterministic biological optimization engine."""

from .absorption import DeterministicAbsorptionCalculator
from .calories import DeterministicCalorieCalculator
from .candidate_generator import ExhaustiveCandidateGenerator
from .conflict import DeterministicConflictCalculator
from .constraints import DeterministicConstraintChecker
from .coverage import DeterministicCoverageCalculator
from .harmony import DeterministicHarmonyCalculator
from .models import (
    BundleCandidate,
    BundleCandidateItem,
    BundleConstraint,
    CalorieReport,
    CoverageItem,
    CoverageReport,
    HarmonyReport,
    InteractionReport,
    InteractionSignal,
    OptimizationRuntimeResult,
    OptimizationStageTrace,
    OptimizationTrace,
    OptimizedBundle,
    TargetIntake,
    TargetIntakePlan,
)
from .optimizer import DeterministicBundleOptimizer
from .runtime import DeterministicTargetIntakePlanner, OptimizationRuntime, register_optimization_datasets
from .synergy import DeterministicSynergyCalculator
from .trace import DeterministicTraceBuilder

__all__ = [
    "BundleCandidate",
    "BundleCandidateItem",
    "BundleConstraint",
    "CalorieReport",
    "CoverageItem",
    "CoverageReport",
    "DeterministicAbsorptionCalculator",
    "DeterministicBundleOptimizer",
    "DeterministicCalorieCalculator",
    "DeterministicConflictCalculator",
    "DeterministicConstraintChecker",
    "DeterministicCoverageCalculator",
    "DeterministicHarmonyCalculator",
    "DeterministicSynergyCalculator",
    "DeterministicTargetIntakePlanner",
    "DeterministicTraceBuilder",
    "ExhaustiveCandidateGenerator",
    "HarmonyReport",
    "InteractionReport",
    "InteractionSignal",
    "OptimizationRuntime",
    "OptimizationRuntimeResult",
    "OptimizationStageTrace",
    "OptimizationTrace",
    "OptimizedBundle",
    "TargetIntake",
    "TargetIntakePlan",
    "register_optimization_datasets",
]
