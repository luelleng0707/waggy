"""Agreement mathematics engine (MAT-1004)."""

from __future__ import annotations

from .formulas import FORMULA_REGISTRY
from .models import AgreementMetrics, EstimatedEpidemiology, MathematicalFormulaTrace, ObservedEpidemiology


class AgreementMathematicsEngine:
    def evaluate(self, observed: ObservedEpidemiology, estimated: EstimatedEpidemiology) -> AgreementMetrics:
        abs_error = abs(observed.observed_prevalence - estimated.estimated_prevalence)
        relative_error = abs_error / max(observed.observed_prevalence, 0.000001)
        agreement = max(0.0, 100.0 - (relative_error * 100.0))
        normalized = agreement / 100.0
        prediction_error = estimated.estimated_prevalence - observed.observed_prevalence

        formula = FORMULA_REGISTRY["MAT-1004"]
        trace = MathematicalFormulaTrace(
            formula_id=formula.formula_id,
            formula_version=formula.version,
            formula_name=formula.description,
            status="active",
            equation=formula.equation,
            substituted_equation=(
                f"agreement = max(0, 100-(|{round(observed.observed_prevalence,6)}-{round(estimated.estimated_prevalence,6)}|/"
                f"max({round(observed.observed_prevalence,6)},1e-6))*100)"
            ),
            python_file="repository/mathematics/agreement.py",
            python_function="AgreementMathematicsEngine.evaluate",
            source_line_start=9,
            source_line_end=50,
            input_variables=("observed_prevalence", "estimated_prevalence"),
            inputs={
                "observed": round(observed.observed_prevalence, 6),
                "estimated": round(estimated.estimated_prevalence, 6),
            },
            intermediate_values={
                "absolute_error": round(abs_error, 6),
                "relative_error": round(relative_error, 6),
                "normalized_agreement": round(normalized, 6),
            },
            output_variable="agreement_percent",
            unit="percent",
            output=round(agreement, 6),
        )
        return AgreementMetrics(
            condition_id=observed.condition_id,
            condition_name=observed.condition_name,
            absolute_error=round(abs_error, 6),
            relative_error=round(relative_error, 6),
            agreement_percent=round(agreement, 6),
            normalized_agreement=round(normalized, 6),
            prediction_error=round(prediction_error, 6),
            formula_traces=(trace,),
        )
