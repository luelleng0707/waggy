"""Agreement analysis stage."""

from __future__ import annotations

from repository.reasoning.mathematics import (
    FORMULA_REGISTRY,
    agreement_absolute_difference,
    agreement_percentage,
    agreement_relative_difference,
)
from repository.reasoning.models import (
    AgreementResult,
    EstimatedCondition,
    FormulaTrace,
    ObservedCondition,
)


class DeterministicAgreementEngine:
    def evaluate(
        self,
        observed: tuple[ObservedCondition, ...],
        estimated: tuple[EstimatedCondition, ...],
    ) -> tuple[AgreementResult, ...]:
        observed_by_condition = {o.condition_id: o for o in observed}
        results: list[AgreementResult] = []

        for est in estimated:
            obs = observed_by_condition.get(est.condition_id)
            if obs is None:
                continue

            abs_diff = agreement_absolute_difference(obs.observed_prevalence, est.estimated_prevalence)
            rel_diff = agreement_relative_difference(obs.observed_prevalence, est.estimated_prevalence)
            agree_pct = agreement_percentage(obs.observed_prevalence, est.estimated_prevalence)

            f1 = FORMULA_REGISTRY["AGR-001"]
            f2 = FORMULA_REGISTRY["AGR-002"]
            f3 = FORMULA_REGISTRY["AGR-003"]
            traces = (
                FormulaTrace(
                    formula_id=f1.formula_id,
                    formula_version=f1.version,
                    equation=f1.equation,
                    inputs={"observed": obs.observed_prevalence, "estimated": est.estimated_prevalence},
                    output=abs_diff,
                ),
                FormulaTrace(
                    formula_id=f2.formula_id,
                    formula_version=f2.version,
                    equation=f2.equation,
                    inputs={"absolute_difference": abs_diff, "observed": obs.observed_prevalence},
                    output=rel_diff,
                ),
                FormulaTrace(
                    formula_id=f3.formula_id,
                    formula_version=f3.version,
                    equation=f3.equation,
                    inputs={"relative_difference": rel_diff},
                    output=agree_pct,
                ),
            )
            results.append(
                AgreementResult(
                    condition_id=est.condition_id,
                    condition_name=est.condition_name,
                    observed=obs.observed_prevalence,
                    estimated=est.estimated_prevalence,
                    absolute_difference=abs_diff,
                    relative_difference=rel_diff,
                    agreement_percentage=agree_pct,
                    formula_traces=traces,
                )
            )
        return tuple(results)
