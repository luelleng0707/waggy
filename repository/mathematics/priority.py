"""Priority mathematics engine (MAT-1007)."""

from __future__ import annotations

from .formula_access import coefficient
from .formulas import FORMULA_REGISTRY
from .models import AgreementMetrics, ConfidenceMetrics, MathematicalFormulaTrace, NoveltyMetrics, PriorityMetrics


class PriorityMathematicsEngine:
    def __init__(self, version_overrides: dict[str, str] | None = None):
        self.version_overrides = version_overrides or {}

    def rank(
        self,
        condition_id: str,
        condition_name: str,
        estimated_prevalence: float,
        confidence: ConfidenceMetrics,
        agreement: AgreementMetrics,
        novelty: NoveltyMetrics,
        rank: int,
    ) -> PriorityMetrics:
        min_agreement_scale = coefficient("MAT-1007", "min_agreement_scale", 0.10, self.version_overrides)
        agreement_scale = max(min_agreement_scale, agreement.agreement_percent / 100.0)
        novelty_multiplier = 1.0 + (novelty.novelty_score / 100.0)
        priority = estimated_prevalence * (confidence.confidence_score / 100.0) * novelty_multiplier * agreement_scale

        formula = FORMULA_REGISTRY["MAT-1007"]
        trace = MathematicalFormulaTrace(
            formula_id=formula.formula_id,
            formula_version=formula.version,
            formula_name=formula.description,
            status="active",
            equation=formula.equation,
            substituted_equation=(
                f"priority = {round(estimated_prevalence,6)}*({round(confidence.confidence_score,6)}/100)"
                f"*(1+{round(novelty.novelty_score,6)}/100)*{round(agreement_scale,6)}"
            ),
            python_file="repository/mathematics/priority.py",
            python_function="PriorityMathematicsEngine.rank",
            source_line_start=9,
            source_line_end=61,
            input_variables=("estimated_prevalence", "confidence_score", "novelty_score", "agreement_percent"),
            inputs={
                "estimated_prevalence": round(estimated_prevalence, 6),
                "confidence": round(confidence.confidence_score, 6),
                "novelty_score": round(novelty.novelty_score, 6),
                "agreement": round(agreement.agreement_percent, 6),
            },
            parameter_values={"min_agreement_scale": round(min_agreement_scale, 6)},
            intermediate_values={
                "agreement_scale": round(agreement_scale, 6),
                "novelty_multiplier": round(novelty_multiplier, 6),
            },
            output_variable="priority_score",
            unit="score",
            output=round(priority, 6),
        )
        return PriorityMetrics(
            condition_id=condition_id,
            condition_name=condition_name,
            priority_score=round(priority, 6),
            priority_rank=rank,
            formula_traces=(trace,),
        )
