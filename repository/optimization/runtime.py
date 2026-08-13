"""Ω6 optimization runtime orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from repository.objectives.models import IngredientSourcePlan
from repository.warehouse import WarehouseInterface
from repository.warehouse.warehouse_interface import CANONICAL_DATASETS

from .absorption import DeterministicAbsorptionCalculator
from .calories import DeterministicCalorieCalculator
from .candidate_generator import ExhaustiveCandidateGenerator
from .conflict import DeterministicConflictCalculator
from .constraints import DeterministicConstraintChecker
from .coverage import DeterministicCoverageCalculator
from .formulas import as_float
from .harmony import DeterministicHarmonyCalculator
from .models import (
    BundleCandidate,
    OptimizationRuntimeResult,
    OptimizedBundle,
    TargetIntake,
    TargetIntakePlan,
)
from .optimizer import DeterministicBundleOptimizer
from .synergy import DeterministicSynergyCalculator
from .trace import DeterministicTraceBuilder


def register_optimization_datasets() -> None:
    dataset_map = {
        "optimization.product_compositions": "optimization/product_compositions.csv",
        "optimization.product_servings": "optimization/product_servings.csv",
        "optimization.ingredient_interactions": "optimization/ingredient_interactions.csv",
        "optimization.ingredient_synergies": "optimization/ingredient_synergies.csv",
        "optimization.ingredient_conflicts": "optimization/ingredient_conflicts.csv",
        "optimization.calorie_density": "optimization/calorie_density.csv",
        "optimization.feeding_constraints": "optimization/feeding_constraints.csv",
        "optimization.package_constraints": "optimization/package_constraints.csv",
    }
    for dataset_name, relative_path in dataset_map.items():
        if dataset_name not in CANONICAL_DATASETS:
            from pathlib import Path

            CANONICAL_DATASETS[dataset_name] = Path(relative_path)


class DeterministicTargetIntakePlanner:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def plan(self, source_plan: tuple[IngredientSourcePlan, ...]) -> TargetIntakePlan:
        sources = self.warehouse.load_dataset("sources.ingredient_sources")
        source_refs = {
            (
                str(row.get("source_id", "")).strip(),
                str(row.get("ingredient_id", "")).strip(),
            ): {
                "quote": str(row.get("scientific_quote", "")).strip(),
                "paper": str(row.get("paper_name", "")).strip(),
                "link": str(row.get("paper_link", "")).strip(),
            }
            for _, row in sources.iterrows()
        }
        grouped: dict[str, list[IngredientSourcePlan]] = {}
        for row in source_plan:
            grouped.setdefault(row.ingredient_id, []).append(row)

        targets: list[TargetIntake] = []
        for ingredient_id in sorted(grouped):
            rows = grouped[ingredient_id]
            baseline_values: list[float] = []
            row_ids: list[str] = []
            quotes: list[str] = []
            papers: list[str] = []
            links: list[str] = []
            unit = rows[0].unit
            for row in rows:
                effective = row.natural_amount / max(0.01, row.bioavailability)
                baseline_values.append(effective)
                row_ids.extend(row.warehouse_rows_used)
                quotes.extend(row.supporting_quotes)
                papers.extend(row.supporting_papers)
                ref = source_refs.get((row.source_id, row.ingredient_id), {})
                if ref.get("quote"):
                    quotes.append(str(ref["quote"]))
                if ref.get("paper"):
                    papers.append(str(ref["paper"]))
                if ref.get("link"):
                    links.append(str(ref["link"]))
            required = sum(baseline_values) / float(len(baseline_values)) if baseline_values else 0.0
            targets.append(
                TargetIntake(
                    ingredient_id=ingredient_id,
                    required_amount=round(required, 6),
                    unit=unit,
                    formula_id="TGT-701",
                    input_values={"source_count": len(rows), "mean_effective_amount": round(required, 6)},
                    warehouse_row_ids=tuple(sorted(set(row_ids))),
                    scientific_quotes=tuple(dict.fromkeys([q for q in quotes if q])),
                    paper_names=tuple(sorted(set([p for p in papers if p]))),
                    paper_links=tuple(sorted(set([link for link in links if link]))),
                )
            )
        return TargetIntakePlan(targets=tuple(targets), formula_ids_used=("TGT-701",))


@dataclass(frozen=True)
class OptimizationRuntime:
    warehouse: WarehouseInterface
    target_intake_planner: DeterministicTargetIntakePlanner | None = None
    candidate_generator: ExhaustiveCandidateGenerator | None = None
    coverage_calculator: DeterministicCoverageCalculator | None = None
    absorption_calculator: DeterministicAbsorptionCalculator | None = None
    synergy_calculator: DeterministicSynergyCalculator | None = None
    conflict_calculator: DeterministicConflictCalculator | None = None
    calorie_calculator: DeterministicCalorieCalculator | None = None
    constraint_checker: DeterministicConstraintChecker | None = None
    harmony_calculator: DeterministicHarmonyCalculator | None = None
    optimizer: DeterministicBundleOptimizer | None = None
    trace_builder: DeterministicTraceBuilder | None = None

    def __post_init__(self) -> None:
        register_optimization_datasets()
        if self.target_intake_planner is None:
            object.__setattr__(self, "target_intake_planner", DeterministicTargetIntakePlanner(self.warehouse))
        if self.candidate_generator is None:
            object.__setattr__(self, "candidate_generator", ExhaustiveCandidateGenerator(self.warehouse))
        if self.coverage_calculator is None:
            object.__setattr__(self, "coverage_calculator", DeterministicCoverageCalculator(self.warehouse))
        if self.absorption_calculator is None:
            object.__setattr__(self, "absorption_calculator", DeterministicAbsorptionCalculator(self.warehouse))
        if self.synergy_calculator is None:
            object.__setattr__(self, "synergy_calculator", DeterministicSynergyCalculator(self.warehouse))
        if self.conflict_calculator is None:
            object.__setattr__(self, "conflict_calculator", DeterministicConflictCalculator(self.warehouse))
        if self.calorie_calculator is None:
            object.__setattr__(self, "calorie_calculator", DeterministicCalorieCalculator(self.warehouse))
        if self.constraint_checker is None:
            object.__setattr__(self, "constraint_checker", DeterministicConstraintChecker(self.warehouse))
        if self.harmony_calculator is None:
            object.__setattr__(self, "harmony_calculator", DeterministicHarmonyCalculator())
        if self.optimizer is None:
            object.__setattr__(self, "optimizer", DeterministicBundleOptimizer())
        if self.trace_builder is None:
            object.__setattr__(self, "trace_builder", DeterministicTraceBuilder())

    def run(
        self,
        ingredient_source_plan: tuple[IngredientSourcePlan, ...],
        profile_context: dict[str, str | float] | None = None,
    ) -> OptimizationRuntimeResult:
        profile_context = profile_context or {}
        life_stage = str(profile_context.get("life_stage", "adult")).strip().lower() or "adult"
        weight_kg = as_float(profile_context.get("weight_kg", 20.0))
        if weight_kg <= 0:
            weight_kg = 20.0

        run_id = uuid.uuid4().hex
        trace_rows: list[dict[str, object]] = []

        target_plan = self._timed_stage(
            trace_rows,
            "Target Intake Planner",
            lambda: self.target_intake_planner.plan(ingredient_source_plan),  # type: ignore[union-attr]
            formula_ids=("TGT-701",),
            warehouse_rows=tuple(
                sorted({row_id for item in ingredient_source_plan for row_id in item.warehouse_rows_used})
            ),
            input_summary="IngredientSourcePlan[]",
        )
        candidates = self._timed_stage(
            trace_rows,
            "Candidate Generator",
            lambda: self.candidate_generator.generate(target_plan),  # type: ignore[union-attr]
            formula_ids=("CND-702",),
            warehouse_rows=tuple(),
            input_summary="TargetIntakePlan",
        )
        evaluated = self._timed_stage(
            trace_rows,
            "Candidate Evaluation",
            lambda: self._evaluate_candidates(candidates, target_plan, life_stage, weight_kg),
            formula_ids=("COV-703", "COV-704", "ABS-705", "SYN-706", "CON-707", "CAL-708", "CAL-709", "CST-710", "HRM-711"),
            warehouse_rows=tuple(),
            input_summary="BundleCandidate[]",
        )
        optimized = self._timed_stage(
            trace_rows,
            "Optimizer",
            lambda: self.optimizer.optimize(evaluated),  # type: ignore[union-attr]
            formula_ids=("OPT-712",),
            warehouse_rows=tuple(),
            input_summary="EvaluatedBundle[]",
        )
        trace = self.trace_builder.build(run_id, tuple(trace_rows))  # type: ignore[union-attr]
        return OptimizationRuntimeResult(
            target_intake_plan=target_plan,
            bundle_candidates=candidates,
            optimized_bundle=optimized,
            trace=trace,
        )

    def _evaluate_candidates(
        self,
        candidates: tuple[BundleCandidate, ...],
        target_plan: TargetIntakePlan,
        life_stage: str,
        weight_kg: float,
    ) -> tuple[OptimizedBundle, ...]:
        results: list[OptimizedBundle] = []
        for candidate in candidates:
            coverage = self.coverage_calculator.calculate(candidate, target_plan)  # type: ignore[union-attr]
            interactions = self.absorption_calculator.calculate(candidate)  # type: ignore[union-attr]
            interactions = self.synergy_calculator.calculate(candidate, interactions)  # type: ignore[union-attr]
            interactions = self.conflict_calculator.calculate(candidate, interactions)  # type: ignore[union-attr]
            calories = self.calorie_calculator.calculate(candidate, life_stage, weight_kg)  # type: ignore[union-attr]
            constraints = self.constraint_checker.check(candidate, calories, life_stage, weight_kg)  # type: ignore[union-attr]
            harmony = self.harmony_calculator.calculate(coverage, interactions, calories, constraints)  # type: ignore[union-attr]

            row_ids = set(candidate.warehouse_row_ids) | set(calories.warehouse_row_ids)
            row_ids.update([row for target in target_plan.targets for row in target.warehouse_row_ids])
            row_ids.update([row for rule in constraints for row in rule.warehouse_row_ids])
            row_ids.update([signal.warehouse_row_id for signal in interactions.absorption_signals])
            row_ids.update([signal.warehouse_row_id for signal in interactions.synergy_signals])
            row_ids.update([signal.warehouse_row_id for signal in interactions.conflict_signals])

            quotes = []
            papers = []
            links = []
            for target in target_plan.targets:
                quotes.extend(target.scientific_quotes)
                papers.extend(target.paper_names)
                links.extend(target.paper_links)
            for signal in interactions.absorption_signals + interactions.synergy_signals + interactions.conflict_signals:
                quotes.append(signal.scientific_quote)
                papers.append(signal.paper_name)
                links.append(signal.paper_link)
            for rule in constraints:
                quotes.extend(rule.scientific_quotes)
                papers.extend(rule.paper_names)
                links.extend(rule.paper_links)

            formula_ids = set(target_plan.formula_ids_used)
            formula_ids.update(candidate.formula_ids_used)
            formula_ids.update(coverage.formula_ids_used)
            formula_ids.update(interactions.formula_ids_used)
            formula_ids.update(calories.formula_ids_used)
            formula_ids.update([rule.formula_id for rule in constraints])
            formula_ids.update(harmony.formula_ids_used)

            results.append(
                OptimizedBundle(
                    candidate=candidate,
                    target_intake_plan=target_plan,
                    coverage_report=coverage,
                    calorie_report=calories,
                    interaction_report=interactions,
                    constraints=constraints,
                    harmony_report=harmony,
                    formula_ids_used=tuple(sorted(formula_ids)),
                    warehouse_row_ids=tuple(sorted(set([row for row in row_ids if row]))),
                    scientific_quotes=tuple(dict.fromkeys([text for text in quotes if text])),
                    paper_names=tuple(sorted(set([text for text in papers if text]))),
                    paper_links=tuple(sorted(set([text for text in links if text]))),
                )
            )
        return tuple(results)

    @staticmethod
    def _timed_stage(
        trace_rows: list[dict[str, object]],
        stage_name: str,
        fn,
        formula_ids: tuple[str, ...],
        warehouse_rows: tuple[str, ...],
        input_summary: str,
    ):
        started = time.perf_counter()
        output = fn()
        elapsed = (time.perf_counter() - started) * 1000.0
        trace_rows.append(
            {
                "stage_name": stage_name,
                "formula_ids": formula_ids,
                "input_summary": input_summary,
                "output_summary": type(output).__name__,
                "warehouse_row_ids": warehouse_rows,
                "elapsed_ms": elapsed,
            }
        )
        return output
