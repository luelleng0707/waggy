from __future__ import annotations

from repository.objectives.models import IngredientSourcePlan
from repository.optimization import (
    DeterministicAbsorptionCalculator,
    DeterministicBundleOptimizer,
    DeterministicCalorieCalculator,
    DeterministicConflictCalculator,
    DeterministicConstraintChecker,
    DeterministicCoverageCalculator,
    DeterministicHarmonyCalculator,
    DeterministicSynergyCalculator,
    DeterministicTargetIntakePlanner,
    ExhaustiveCandidateGenerator,
    OptimizationRuntime,
    register_optimization_datasets,
)
from repository.warehouse import WarehouseInterface


def _source_plan() -> tuple[IngredientSourcePlan, ...]:
    return (
        IngredientSourcePlan(
            source_id="SRC_001",
            ingredient_id="ING_F9E1B8CF",
            ingredient_name="Omega-3",
            natural_amount=820.0,
            unit="mg_per_100g",
            bioavailability=0.82,
            coverage_score=1.0,
            formula_ids_used=("SRC-601",),
            supporting_papers=("Nutrients",),
            supporting_quotes=("Omega-3 bioavailability reference.",),
            warehouse_rows_used=("sources.ingredient_sources:SRC_001:ING_F9E1B8CF",),
        ),
        IngredientSourcePlan(
            source_id="SRC_003",
            ingredient_id="ING_41BF6A84",
            ingredient_name="Glucosamine",
            natural_amount=1100.0,
            unit="mg_per_100g",
            bioavailability=0.63,
            coverage_score=1.0,
            formula_ids_used=("SRC-601",),
            supporting_papers=("Marine Drugs",),
            supporting_quotes=("Glucosamine source reference.",),
            warehouse_rows_used=("sources.ingredient_sources:SRC_003:ING_41BF6A84",),
        ),
        IngredientSourcePlan(
            source_id="SRC_004",
            ingredient_id="ING_996AE66D",
            ingredient_name="MSM",
            natural_amount=900.0,
            unit="mg_per_100g",
            bioavailability=0.68,
            coverage_score=1.0,
            formula_ids_used=("SRC-601",),
            supporting_papers=("Frontiers in Veterinary Science",),
            supporting_quotes=("MSM source reference.",),
            warehouse_rows_used=("sources.ingredient_sources:SRC_004:ING_996AE66D",),
        ),
    )


def _runtime():
    register_optimization_datasets()
    return WarehouseInterface()


def test_target_intake_calculation_deterministic():
    planner = DeterministicTargetIntakePlanner(_runtime())
    plan_a = planner.plan(_source_plan())
    plan_b = planner.plan(_source_plan())
    assert plan_a == plan_b
    assert plan_a.targets
    assert all(target.formula_id == "TGT-701" for target in plan_a.targets)


def test_candidate_generation_and_coverage():
    warehouse = _runtime()
    planner = DeterministicTargetIntakePlanner(warehouse)
    target_plan = planner.plan(_source_plan())
    generator = ExhaustiveCandidateGenerator(warehouse)
    candidates = generator.generate(target_plan)
    assert candidates

    coverage = DeterministicCoverageCalculator(warehouse).calculate(candidates[0], target_plan)
    assert coverage.items
    assert coverage.mean_coverage_percent >= 0.0
    assert "COV-703" in coverage.formula_ids_used


def test_absorption_synergy_conflict_chain():
    warehouse = _runtime()
    planner = DeterministicTargetIntakePlanner(warehouse)
    target_plan = planner.plan(_source_plan())
    candidate = ExhaustiveCandidateGenerator(warehouse).generate(target_plan)[0]

    report = DeterministicAbsorptionCalculator(warehouse).calculate(candidate)
    report = DeterministicSynergyCalculator(warehouse).calculate(candidate, report)
    report = DeterministicConflictCalculator(warehouse).calculate(candidate, report)

    assert report.formula_ids_used
    assert report.absorption_score_percent >= 0.0
    assert report.synergy_score_percent >= 0.0
    assert report.conflict_penalty_percent >= 0.0


def test_calorie_and_constraint_checks():
    warehouse = _runtime()
    planner = DeterministicTargetIntakePlanner(warehouse)
    target_plan = planner.plan(_source_plan())
    candidate = ExhaustiveCandidateGenerator(warehouse).generate(target_plan)[0]

    calories = DeterministicCalorieCalculator(warehouse).calculate(candidate, "adult", 22.0)
    constraints = DeterministicConstraintChecker(warehouse).check(candidate, calories, "adult", 22.0)

    assert calories.daily_calories >= 0.0
    assert constraints
    assert all(rule.formula_id == "CST-710" for rule in constraints)


def test_harmony_and_optimizer_determinism():
    warehouse = _runtime()
    planner = DeterministicTargetIntakePlanner(warehouse)
    target_plan = planner.plan(_source_plan())
    candidates = ExhaustiveCandidateGenerator(warehouse).generate(target_plan)

    coverage_calc = DeterministicCoverageCalculator(warehouse)
    absorption_calc = DeterministicAbsorptionCalculator(warehouse)
    synergy_calc = DeterministicSynergyCalculator(warehouse)
    conflict_calc = DeterministicConflictCalculator(warehouse)
    calorie_calc = DeterministicCalorieCalculator(warehouse)
    checker = DeterministicConstraintChecker(warehouse)
    harmony_calc = DeterministicHarmonyCalculator()
    optimizer = DeterministicBundleOptimizer()

    evaluated = []
    for candidate in candidates[:5]:
        coverage = coverage_calc.calculate(candidate, target_plan)
        interactions = absorption_calc.calculate(candidate)
        interactions = synergy_calc.calculate(candidate, interactions)
        interactions = conflict_calc.calculate(candidate, interactions)
        calories = calorie_calc.calculate(candidate, "adult", 22.0)
        constraints = checker.check(candidate, calories, "adult", 22.0)
        harmony = harmony_calc.calculate(coverage, interactions, calories, constraints)
        from repository.optimization.models import OptimizedBundle

        evaluated.append(
            OptimizedBundle(
                candidate=candidate,
                target_intake_plan=target_plan,
                coverage_report=coverage,
                calorie_report=calories,
                interaction_report=interactions,
                constraints=constraints,
                harmony_report=harmony,
                formula_ids_used=tuple(),
                warehouse_row_ids=tuple(),
                scientific_quotes=tuple(),
                paper_names=tuple(),
                paper_links=tuple(),
            )
        )
    first = optimizer.optimize(tuple(evaluated))
    second = optimizer.optimize(tuple(evaluated))
    assert first == second


def test_end_to_end_runtime_is_deterministic():
    runtime = OptimizationRuntime(warehouse=_runtime())
    source_plan = _source_plan()
    profile = {"life_stage": "adult", "weight_kg": 22.0}

    first = runtime.run(source_plan, profile)
    second = runtime.run(source_plan, profile)

    assert first.target_intake_plan == second.target_intake_plan
    assert first.bundle_candidates == second.bundle_candidates
    assert first.optimized_bundle == second.optimized_bundle
