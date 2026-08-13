"""Confidence mathematics engine (MAT-1005)."""

from __future__ import annotations

from .formula_access import coefficient
from .formulas import FORMULA_REGISTRY
from .models import AgreementMetrics, ConfidenceMetrics, EstimatedEpidemiology, MathematicalFormulaTrace, ObservedEpidemiology


class ConfidenceMathematicsEngine:
    def __init__(self, version_overrides: dict[str, str] | None = None):
        self.version_overrides = version_overrides or {}

    def evaluate(
        self,
        observed: ObservedEpidemiology,
        estimated: EstimatedEpidemiology,
        agreement: AgreementMetrics,
        edges: tuple[dict[str, str], ...],
    ) -> ConfidenceMetrics:
        observed_count = sum(1 for edge in edges if edge.get("evidence_type", "").strip().lower() == "observed")
        trait_count = sum(
            1 for edge in edges if edge.get("evidence_type", "").strip().lower() in {"trait", "life_stage", "activity"}
        )
        env_count = sum(
            1 for edge in edges if edge.get("evidence_type", "").strip().lower() in {"environment", "interaction", "ingredient"}
        )
        study_count = len(
            {
                str(edge.get("citation_id", "")).strip()
                for edge in edges
                if str(edge.get("citation_id", "")).strip()
            }
        )

        observed_multiplier = coefficient("MAT-1005", "observed_multiplier", 1.5, self.version_overrides)
        evidence_denominator = max(0.000001, coefficient("MAT-1005", "evidence_denominator", 20.0, self.version_overrides))
        study_denominator = max(0.000001, coefficient("MAT-1005", "study_denominator", 10.0, self.version_overrides))
        evidence_weight = coefficient("MAT-1005", "evidence_weight", 0.45, self.version_overrides)
        study_weight = coefficient("MAT-1005", "study_weight", 0.25, self.version_overrides)
        agreement_weight = coefficient("MAT-1005", "agreement_weight", 0.30, self.version_overrides)

        evidence_component = min(1.0, (observed_count * observed_multiplier + trait_count + env_count) / evidence_denominator)
        study_component = min(1.0, study_count / study_denominator)
        agreement_component = agreement.normalized_agreement
        confidence = (evidence_weight * evidence_component + study_weight * study_component + agreement_weight * agreement_component) * 100.0

        formula = FORMULA_REGISTRY["MAT-1005"]
        trace = MathematicalFormulaTrace(
            formula_id=formula.formula_id,
            formula_version=formula.version,
            formula_name=formula.description,
            status="active",
            equation=formula.equation,
            substituted_equation=(
                f"confidence = ({round(evidence_weight,6)}*{round(evidence_component,6)} + "
                f"{round(study_weight,6)}*{round(study_component,6)} + "
                f"{round(agreement_weight,6)}*{round(agreement_component,6)})*100"
            ),
            python_file="repository/mathematics/confidence.py",
            python_function="ConfidenceMathematicsEngine.evaluate",
            source_line_start=9,
            source_line_end=74,
            input_variables=("observed_count", "trait_count", "env_count", "study_count", "agreement"),
            inputs={
                "observed_count": observed_count,
                "trait_count": trait_count,
                "env_count": env_count,
                "study_count": study_count,
                "agreement": round(agreement.agreement_percent, 6),
            },
            parameter_values={
                "observed_multiplier": round(observed_multiplier, 6),
                "evidence_denominator": round(evidence_denominator, 6),
                "study_denominator": round(study_denominator, 6),
                "evidence_weight": round(evidence_weight, 6),
                "study_weight": round(study_weight, 6),
                "agreement_weight": round(agreement_weight, 6),
            },
            intermediate_values={
                "evidence_component": round(evidence_component, 6),
                "study_component": round(study_component, 6),
                "agreement_component": round(agreement_component, 6),
            },
            output_variable="confidence_score",
            unit="percent",
            output=round(confidence, 6),
        )
        return ConfidenceMetrics(
            condition_id=estimated.condition_id,
            condition_name=estimated.condition_name,
            confidence_score=round(confidence, 6),
            observed_evidence_count=observed_count,
            trait_evidence_count=trait_count,
            environmental_evidence_count=env_count,
            study_count=study_count,
            formula_traces=(trace,),
        )
