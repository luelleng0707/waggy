"""Uncertainty mathematics engine (MAT-1008)."""

from __future__ import annotations

import math

from .formula_access import coefficient
from .formulas import FORMULA_REGISTRY
from .models import ConfidenceMetrics, EstimatedEpidemiology, MathematicalFormulaTrace, UncertaintyMetrics
from .normalization import canonical_percent


class UncertaintyMathematicsEngine:
    def __init__(self, version_overrides: dict[str, str] | None = None):
        self.version_overrides = version_overrides or {}

    def evaluate(
        self,
        estimated: EstimatedEpidemiology,
        confidence: ConfidenceMetrics,
        edges: tuple[dict[str, str], ...],
    ) -> UncertaintyMetrics:
        contributions = [
            canonical_percent(edge.get("value_number", ""))
            for edge in edges
            if edge.get("evidence_type", "").strip().lower() != "observed"
        ]
        if contributions:
            mean = sum(contributions) / float(len(contributions))
            variance = sum((value - mean) ** 2 for value in contributions) / float(len(contributions))
            stddev = math.sqrt(variance)
        else:
            stddev = 0.0
        min_factor = coefficient("MAT-1008", "min_uncertainty_factor", 0.20, self.version_overrides)
        uncertainty_factor = max(min_factor, 1.0 - (confidence.confidence_score / 100.0))
        uncertainty = stddev * uncertainty_factor
        lower = max(0.0, estimated.estimated_prevalence - uncertainty)
        upper = max(lower, estimated.estimated_prevalence + uncertainty)

        formula = FORMULA_REGISTRY["MAT-1008"]
        trace = MathematicalFormulaTrace(
            formula_id=formula.formula_id,
            formula_version=formula.version,
            formula_name=formula.description,
            status="active",
            equation=formula.equation,
            substituted_equation=(
                f"uncertainty = stddev({[round(v, 6) for v in contributions]})*{round(uncertainty_factor,6)}"
            ),
            python_file="repository/mathematics/uncertainty.py",
            python_function="UncertaintyMathematicsEngine.evaluate",
            source_line_start=11,
            source_line_end=66,
            input_variables=("contributions", "confidence_score"),
            inputs={
                "stddev": round(stddev, 6),
                "uncertainty_factor": round(uncertainty_factor, 6),
                "confidence": round(confidence.confidence_score, 6),
            },
            parameter_values={"min_uncertainty_factor": round(min_factor, 6)},
            intermediate_values={"lower_bound": round(lower, 6), "upper_bound": round(upper, 6)},
            output_variable="uncertainty",
            unit="percent",
            output=round(uncertainty, 6),
        )
        return UncertaintyMetrics(
            condition_id=estimated.condition_id,
            condition_name=estimated.condition_name,
            lower_bound=round(lower, 6),
            upper_bound=round(upper, 6),
            uncertainty=round(uncertainty, 6),
            evidence_count=len(contributions),
            formula_traces=(trace,),
        )
