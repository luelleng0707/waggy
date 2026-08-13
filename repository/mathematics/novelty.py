"""Novelty mathematics engine (MAT-1006)."""

from __future__ import annotations

from .formula_access import coefficient
from .formulas import FORMULA_REGISTRY
from .models import ConfidenceMetrics, EstimatedEpidemiology, MathematicalFormulaTrace, NoveltyMetrics, ObservedEpidemiology


class NoveltyMathematicsEngine:
    def __init__(self, version_overrides: dict[str, str] | None = None):
        self.version_overrides = version_overrides or {}

    def evaluate(
        self,
        observed: ObservedEpidemiology,
        estimated: EstimatedEpidemiology,
        confidence: ConfidenceMetrics,
    ) -> NoveltyMetrics:
        delta = max(0.0, estimated.estimated_prevalence - observed.observed_prevalence)
        confidence_scale = confidence.confidence_score / 100.0
        novelty_score = delta * confidence_scale
        observed_max = coefficient("MAT-1006", "emerging_observed_max", 0.5, self.version_overrides)
        estimated_min = coefficient("MAT-1006", "emerging_estimated_min", 10.0, self.version_overrides)
        confidence_min = coefficient("MAT-1006", "emerging_confidence_min", 70.0, self.version_overrides)
        emerging = (
            observed.observed_prevalence <= observed_max
            and estimated.estimated_prevalence >= estimated_min
            and confidence.confidence_score >= confidence_min
        )
        rationale = (
            "Emerging biological concern detected from high estimated prevalence with near-zero observed baseline."
            if emerging
            else "Novelty remains within expected observed-estimated envelope."
        )
        formula = FORMULA_REGISTRY["MAT-1006"]
        trace = MathematicalFormulaTrace(
            formula_id=formula.formula_id,
            formula_version=formula.version,
            formula_name=formula.description,
            status="active",
            equation=formula.equation,
            substituted_equation=(
                f"novelty = max(0,{round(estimated.estimated_prevalence,6)}-{round(observed.observed_prevalence,6)})"
                f"*({round(confidence.confidence_score,6)}/100)"
            ),
            python_file="repository/mathematics/novelty.py",
            python_function="NoveltyMathematicsEngine.evaluate",
            source_line_start=9,
            source_line_end=63,
            input_variables=("observed_prevalence", "estimated_prevalence", "confidence_score"),
            inputs={
                "observed_prevalence": round(observed.observed_prevalence, 6),
                "estimated_prevalence": round(estimated.estimated_prevalence, 6),
                "confidence": round(confidence.confidence_score, 6),
            },
            parameter_values={
                "emerging_observed_max": round(observed_max, 6),
                "emerging_estimated_min": round(estimated_min, 6),
                "emerging_confidence_min": round(confidence_min, 6),
            },
            intermediate_values={"delta": round(delta, 6), "confidence_scale": round(confidence_scale, 6)},
            output_variable="novelty_score",
            unit="score",
            output=round(novelty_score, 6),
        )
        return NoveltyMetrics(
            condition_id=estimated.condition_id,
            condition_name=estimated.condition_name,
            novelty_score=round(novelty_score, 6),
            emerging_biological_concern=emerging,
            rationale=rationale,
            formula_traces=(trace,),
        )
