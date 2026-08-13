"""Bundle optimizer selection logic."""

from __future__ import annotations

from .models import OptimizedBundle


class DeterministicBundleOptimizer:
    def optimize(self, candidates: tuple[OptimizedBundle, ...]) -> OptimizedBundle:
        if not candidates:
            raise ValueError("No bundle candidates available for optimization.")

        feasible = [item for item in candidates if all(rule.passed for rule in item.constraints)]
        pool = feasible if feasible else list(candidates)
        pool.sort(
            key=lambda item: (
                -item.harmony_report.harmony_score,
                -item.harmony_report.constraint_satisfaction_percent,
                item.candidate.candidate_id,
            )
        )
        best = pool[0]
        formula_ids = tuple(sorted(set(best.formula_ids_used + ("OPT-712",))))
        return OptimizedBundle(
            candidate=best.candidate,
            target_intake_plan=best.target_intake_plan,
            coverage_report=best.coverage_report,
            calorie_report=best.calorie_report,
            interaction_report=best.interaction_report,
            constraints=best.constraints,
            harmony_report=best.harmony_report,
            formula_ids_used=formula_ids,
            warehouse_row_ids=best.warehouse_row_ids,
            scientific_quotes=best.scientific_quotes,
            paper_names=best.paper_names,
            paper_links=best.paper_links,
        )
