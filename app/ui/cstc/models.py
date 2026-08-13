"""Presentation models for CSTC-style Wagtopia desktop shell."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AnalyzeDogRequest:
    """UI-level request model mapped to existing Wagtopia API payload."""

    name: str
    primary_breed: str
    secondary_breed: str | None = None
    breed_split_pct: float = 50.0
    age_years: float | None = None
    birthday: str | None = None
    weight_kg: float = 20.0
    height_cm: float | None = None
    sex: str | None = None
    activity_level: str = "Moderate"
    current_environment: str = "Temperate Indoor"
    bcs: float | None = None
    observed_conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class DogSummary:
    name: str
    breeds: tuple[str, ...]
    age_years: float | None
    birthday: str | None
    weight_kg: float | None
    height_cm: float | None
    sex: str | None
    activity_level: str | None
    current_environment: str | None


@dataclass(frozen=True)
class BiologySummary:
    age_stage: str | None
    trait_summary: tuple[str, ...]
    descriptors: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class HealthSummary:
    overall_score: float | None
    priorities: tuple[dict[str, Any], ...]
    insights: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class EpidemiologySummary:
    priorities: tuple[dict[str, Any], ...]
    observed_conditions: tuple[str, ...]


@dataclass(frozen=True)
class NutritionSummary:
    targets: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ActivitySummary:
    payload: dict[str, Any]


@dataclass(frozen=True)
class GroomingSummary:
    flags: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ProductRecommendations:
    products: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class PackageRecommendations:
    packages: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class FinancialSummary:
    monthly_plan: dict[str, Any]
    yearly_plan: dict[str, Any]
    package_economics: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ConfidenceSummary:
    payload: dict[str, Any]


@dataclass(frozen=True)
class EvidenceSummary:
    evidence: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class CalculationTraceSummary:
    trace: tuple[dict[str, Any], ...]
    debug_formula_executions: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class ValidationSummary:
    payload: dict[str, Any]


@dataclass(frozen=True)
class AnalysisPresentation:
    dog: DogSummary
    biology: BiologySummary
    health: HealthSummary
    epidemiology: EpidemiologySummary
    nutrition: NutritionSummary
    activity: ActivitySummary
    grooming: GroomingSummary
    products: ProductRecommendations
    packages: PackageRecommendations
    financial: FinancialSummary
    confidence: ConfidenceSummary
    evidence: EvidenceSummary
    trace: CalculationTraceSummary
    validation: ValidationSummary
    raw_analyze: dict[str, Any] = field(default_factory=dict)
