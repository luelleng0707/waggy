"""Immutable Ω6 optimization models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TargetIntake:
    ingredient_id: str
    required_amount: float
    unit: str
    formula_id: str
    input_values: dict[str, float | str]
    warehouse_row_ids: tuple[str, ...]
    scientific_quotes: tuple[str, ...]
    paper_names: tuple[str, ...]
    paper_links: tuple[str, ...]


@dataclass(frozen=True)
class TargetIntakePlan:
    targets: tuple[TargetIntake, ...] = field(default_factory=tuple)
    formula_ids_used: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BundleCandidateItem:
    product_id: str
    servings_per_day: float
    serving_unit: str
    warehouse_row_ids: tuple[str, ...]


@dataclass(frozen=True)
class BundleCandidate:
    candidate_id: str
    items: tuple[BundleCandidateItem, ...]
    formula_ids_used: tuple[str, ...] = field(default_factory=tuple)
    warehouse_row_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BundleConstraint:
    constraint_id: str
    passed: bool
    formula_id: str
    detail: str
    input_values: dict[str, float | str]
    warehouse_row_ids: tuple[str, ...]
    scientific_quotes: tuple[str, ...]
    paper_names: tuple[str, ...]
    paper_links: tuple[str, ...]


@dataclass(frozen=True)
class CoverageItem:
    ingredient_id: str
    required_amount: float
    provided_amount: float
    coverage_percent: float
    formula_id: str
    warehouse_row_ids: tuple[str, ...]


@dataclass(frozen=True)
class CoverageReport:
    items: tuple[CoverageItem, ...] = field(default_factory=tuple)
    mean_coverage_percent: float = 0.0
    dose_accuracy_percent: float = 0.0
    formula_ids_used: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CalorieReport:
    daily_calories: float
    energy_density_kcal_per_serving: float
    percent_of_daily_requirement: float
    formula_ids_used: tuple[str, ...]
    warehouse_row_ids: tuple[str, ...]


@dataclass(frozen=True)
class InteractionSignal:
    signal_id: str
    ingredient_a: str
    ingredient_b: str
    effect_value: float
    scientific_quote: str
    paper_name: str
    paper_link: str
    warehouse_row_id: str


@dataclass(frozen=True)
class InteractionReport:
    absorption_signals: tuple[InteractionSignal, ...] = field(default_factory=tuple)
    synergy_signals: tuple[InteractionSignal, ...] = field(default_factory=tuple)
    conflict_signals: tuple[InteractionSignal, ...] = field(default_factory=tuple)
    absorption_score_percent: float = 0.0
    synergy_score_percent: float = 0.0
    conflict_penalty_percent: float = 0.0
    formula_ids_used: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class HarmonyReport:
    coverage_percent: float
    dose_accuracy_percent: float
    absorption_percent: float
    synergy_percent: float
    conflict_penalty_percent: float
    calories_percent: float
    constraint_satisfaction_percent: float
    harmony_score: float
    formula_ids_used: tuple[str, ...]
    input_values: dict[str, float | str]


@dataclass(frozen=True)
class OptimizedBundle:
    candidate: BundleCandidate
    target_intake_plan: TargetIntakePlan
    coverage_report: CoverageReport
    calorie_report: CalorieReport
    interaction_report: InteractionReport
    constraints: tuple[BundleConstraint, ...]
    harmony_report: HarmonyReport
    formula_ids_used: tuple[str, ...]
    warehouse_row_ids: tuple[str, ...]
    scientific_quotes: tuple[str, ...]
    paper_names: tuple[str, ...]
    paper_links: tuple[str, ...]


@dataclass(frozen=True)
class OptimizationStageTrace:
    stage_name: str
    formula_ids: tuple[str, ...]
    input_summary: str
    output_summary: str
    warehouse_row_ids: tuple[str, ...]
    elapsed_ms: float


@dataclass(frozen=True)
class OptimizationTrace:
    run_id: str
    stages: tuple[OptimizationStageTrace, ...]


@dataclass(frozen=True)
class OptimizationRuntimeResult:
    target_intake_plan: TargetIntakePlan
    bundle_candidates: tuple[BundleCandidate, ...]
    optimized_bundle: OptimizedBundle
    trace: OptimizationTrace
