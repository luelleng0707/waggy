"""Final harmony score calculator."""

from __future__ import annotations

from .models import BundleConstraint, CalorieReport, CoverageReport, HarmonyReport, InteractionReport


class DeterministicHarmonyCalculator:
    def calculate(
        self,
        coverage: CoverageReport,
        interactions: InteractionReport,
        calories: CalorieReport,
        constraints: tuple[BundleConstraint, ...],
    ) -> HarmonyReport:
        coverage_percent = coverage.mean_coverage_percent
        dose_accuracy = coverage.dose_accuracy_percent
        absorption = interactions.absorption_score_percent
        synergy = interactions.synergy_score_percent
        conflict = interactions.conflict_penalty_percent
        calories_percent = _calorie_score(calories.percent_of_daily_requirement)
        constraint_satisfaction = _constraint_satisfaction(constraints)

        harmony = (
            (0.30 * coverage_percent)
            + (0.20 * dose_accuracy)
            + (0.15 * absorption)
            + (0.10 * synergy)
            + (0.10 * calories_percent)
            + (0.10 * constraint_satisfaction)
            - (0.05 * conflict)
        )
        return HarmonyReport(
            coverage_percent=round(coverage_percent, 6),
            dose_accuracy_percent=round(dose_accuracy, 6),
            absorption_percent=round(absorption, 6),
            synergy_percent=round(synergy, 6),
            conflict_penalty_percent=round(conflict, 6),
            calories_percent=round(calories_percent, 6),
            constraint_satisfaction_percent=round(constraint_satisfaction, 6),
            harmony_score=round(harmony, 6),
            formula_ids_used=("CST-710", "HRM-711"),
            input_values={
                "w_coverage": 0.30,
                "w_dose_accuracy": 0.20,
                "w_absorption": 0.15,
                "w_synergy": 0.10,
                "w_calories": 0.10,
                "w_constraints": 0.10,
                "w_conflict_penalty": 0.05,
                "coverage": coverage_percent,
                "dose_accuracy": dose_accuracy,
                "absorption": absorption,
                "synergy": synergy,
                "conflict_penalty": conflict,
                "calories_score": calories_percent,
                "constraint_satisfaction": constraint_satisfaction,
            },
        )


def _constraint_satisfaction(constraints: tuple[BundleConstraint, ...]) -> float:
    if not constraints:
        return 0.0
    passed = sum(1 for item in constraints if item.passed)
    return (passed / float(len(constraints))) * 100.0


def _calorie_score(percent_of_daily_requirement: float) -> float:
    if percent_of_daily_requirement <= 100.0:
        return 100.0
    excess = percent_of_daily_requirement - 100.0
    return max(0.0, 100.0 - excess)
