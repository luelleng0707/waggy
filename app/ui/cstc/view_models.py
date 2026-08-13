"""Response mapping helpers for CSTC desktop presentation."""

from __future__ import annotations

from typing import Any

from .errors import MappingError
from .models import (
    ActivitySummary,
    AnalysisPresentation,
    BiologySummary,
    CalculationTraceSummary,
    ConfidenceSummary,
    DogSummary,
    EpidemiologySummary,
    EvidenceSummary,
    FinancialSummary,
    GroomingSummary,
    HealthSummary,
    NutritionSummary,
    PackageRecommendations,
    ProductRecommendations,
    ValidationSummary,
)


def build_presentation(analyze: dict[str, Any], assessment: dict[str, Any] | None = None) -> AnalysisPresentation:
    """Map existing analyze payload into normalized presentation models."""
    if not isinstance(analyze, dict):
        raise MappingError("Analyze response is not a dictionary")

    profile = analyze.get("profile") or {}
    breeds = tuple(str(x) for x in (profile.get("breeds") or ()) if x)
    dog = DogSummary(
        name=str(profile.get("pet_name") or "Unknown Dog"),
        breeds=breeds,
        age_years=_to_float(profile.get("age_years")),
        birthday=_to_str_or_none(profile.get("birthday")),
        weight_kg=_to_float(profile.get("weight_kg")),
        height_cm=_to_float(profile.get("height_cm")),
        sex=_to_str_or_none(profile.get("sex") or profile.get("gender")),
        activity_level=_to_str_or_none(profile.get("activity_level")),
        current_environment=_to_str_or_none(profile.get("current_environment")),
    )

    biology_payload = analyze.get("biology") or {}
    biology = BiologySummary(
        age_stage=_to_str_or_none(biology_payload.get("age_stage")),
        trait_summary=tuple(str(x) for x in (biology_payload.get("trait_summary") or ()) if x),
        descriptors=tuple((biology_payload.get("descriptors") or ())),
    )

    insights = tuple((analyze.get("healthInsights") or ()))
    health = HealthSummary(
        overall_score=_to_float(analyze.get("wellness_score")),
        priorities=tuple((analyze.get("risks") or ())),
        insights=insights,
    )

    epidemiology = EpidemiologySummary(
        priorities=tuple((analyze.get("risks") or ())),
        observed_conditions=tuple(str(x) for x in (profile.get("observed_conditions") or ()) if x),
    )

    nutrition = NutritionSummary(targets=tuple((analyze.get("nutritionalTargets") or ())))
    activity = ActivitySummary(payload=dict(analyze.get("activityRecommendations") or {}))
    grooming = GroomingSummary(flags=tuple((analyze.get("groomer") or ())))
    products = ProductRecommendations(products=tuple((analyze.get("productRecommendations") or ())))
    packages = PackageRecommendations(packages=tuple((analyze.get("wellnessPackages") or ())))

    monthly = dict(analyze.get("monthly_plan") or {})
    yearly = dict(analyze.get("yearly_plan") or {})
    package_economics = []
    for pkg in analyze.get("wellnessPackages") or ():
        if not isinstance(pkg, dict):
            continue
        package_economics.append(
            {
                "tier": pkg.get("tier"),
                "title": pkg.get("title"),
                "price_rmb": pkg.get("price_rmb"),
                "monthly_equivalent_rmb": pkg.get("monthly_equivalent_rmb"),
                "yearly_price_rmb": pkg.get("yearly_price_rmb"),
                "savings_rmb": pkg.get("savings_rmb"),
                "savings_percent": pkg.get("savings_percent"),
                "discount_percent": pkg.get("discount_percent"),
            }
        )
    financial = FinancialSummary(
        monthly_plan=monthly,
        yearly_plan=yearly,
        package_economics=tuple(package_economics),
    )

    confidence = ConfidenceSummary(payload=_pick_confidence_payload(analyze, assessment))
    evidence = EvidenceSummary(evidence=tuple((analyze.get("scientificEvidence") or analyze.get("evidence") or ())))

    debug = analyze.get("debug") or {}
    trace = CalculationTraceSummary(
        trace=tuple((analyze.get("calculationTrace") or ())),
        debug_formula_executions=tuple((debug.get("formula_executions") or ())),
    )

    validation_payload = {}
    if isinstance(assessment, dict):
        validation_payload = dict(assessment.get("validation") or {})
    validation = ValidationSummary(payload=validation_payload)

    return AnalysisPresentation(
        dog=dog,
        biology=biology,
        health=health,
        epidemiology=epidemiology,
        nutrition=nutrition,
        activity=activity,
        grooming=grooming,
        products=products,
        packages=packages,
        financial=financial,
        confidence=confidence,
        evidence=evidence,
        trace=trace,
        validation=validation,
        raw_analyze=analyze,
    )


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _pick_confidence_payload(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    if isinstance(assessment, dict) and isinstance(assessment.get("confidence"), dict):
        return dict(assessment.get("confidence") or {})
    debug = analyze.get("debug") or {}
    confidence = {
        "wellness_score": analyze.get("wellness_score"),
        "risk_count": len(analyze.get("risks") or []),
        "evidence_count": len(analyze.get("scientificEvidence") or []),
        "formula_execution_count": len(debug.get("formula_executions") or []),
    }
    return confidence
