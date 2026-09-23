"""Ω16 HTTP DTOs for the two existing analysis contracts.

API DTO → existing canonical model:

    WorkbenchRequest / AnalyzeRequest
        → app.api.payload_adapter
            → app.agent.state.DogProfileInput
                → PPIEWellnessAgent.generate_reproducible_report

These models serialize HTTP. They do not duplicate scientific domain objects.
Nested engine payloads remain dicts so this layer does not invent fields.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

HTTP_API_VERSION = "v1"

# Runtime JSON paths on POST /api/v1/presentation/workbench (200 body).
# Do not invent alternate trees such as packages.funnel.
DEVELOPER_JSON_PATHS: dict[str, str] = {
    "health": "canonical.scientific_analysis.findings",
    "health_raw": "canonical.analyze.healthInsights",
    "health_customer": "roles.customer.health_analysis",
    "nutrition": "canonical.scientific_analysis.nutrient_targets",
    "nutrition_raw": "canonical.analyze.nutritionalTargets",
    "products": "canonical.product_matching.recommendations",
    "products_raw": "canonical.analyze.productRecommendations",
    "packages": "canonical.package_optimization.package_options",
    "packages_tiers": "canonical.package_optimization.tiers",
    "packages_raw": "canonical.analyze.packageOptions",
    "optimizer_provenance": "canonical.package_optimization.search",
    "optimizer_provenance_raw": "canonical.analyze.optimizerProvenance",
    "scientific_evidence": "canonical.scientific_analysis.evidence",
    "scientific_evidence_raw": "canonical.analyze.scientificEvidence",
    "engine_version": "canonical.analyze.version",
    "engine_version_envelope": "engine_version",
    "warehouse_version": "warehouse_version",
    "analysis_signature": "analysis_signature",
    "correlation_id": "presentation_correlation_id",
    "not_available_token": "NOT AVAILABLE FROM RUNTIME",
}

WORKBENCH_EXAMPLE_REQUEST: dict[str, Any] = {
    "name": "Dolly",
    "pet_name": "Dolly",
    "primary_breed": "Labrador Retriever",
    "secondary_breed": "Golden Retriever",
    "breeds": ["Labrador Retriever", "Golden Retriever"],
    "birthday": "2021-04-15",
    "as_of_date": "2026-09-09",
    "weight": 30,
    "sex": "Female",
    "activity_level": "Moderate",
    "current_environment": "Temperate Outdoor",
    "observed_conditions": ["joint_stiffness", "itching"],
    "correlation_id": "omega16-example-001",
    "role_context": {
        "groomer": {
            "observations": "coat dryness noted at shoulders",
            "observed_conditions": [],
        },
        "business": {"segment": ""},
    },
}


class AnalyzeRequest(BaseModel):
    """Loose raw-engine request. Legacy silent defaults still apply on this path only.

    Missing age → 5.0, missing weight → 20.0, missing activity → Moderate,
    missing environment → Temperate Indoor, empty name → Pet.
    Canonical internal weight field is DogProfileInput.weight_kg.
    """

    model_config = ConfigDict(extra="allow")

    name: str | None = Field(default=None, description="Display name. Legacy default: Pet.")
    pet_name: str | None = None
    petName: str | None = None
    dogName: str | None = None
    primary_breed: str | None = Field(default=None, description="Canonical HTTP breed string. Ω12 is not wired.")
    secondary_breed: str | None = None
    breeds: list[str] | str | None = None
    birthday: str | None = Field(default=None, description="YYYY-MM-DD. Age uses datetime.now when age_years omitted.")
    age_years: float | None = None
    weight: float | None = Field(default=None, description="Maps to DogProfileInput.weight_kg. Legacy default 20.")
    weight_kg: float | None = Field(default=None, description="Same canonical field as weight.")
    sex: str | None = None
    gender: str | None = None
    activity_level: str | None = Field(default=None, description="Legacy default Moderate.")
    activity: str | None = None
    current_environment: str | None = Field(default=None, description="Legacy default Temperate Indoor.")
    environment: str | None = None
    observed_conditions: list[str] | None = None
    monthly_budget: float | None = None


class WorkbenchRequest(BaseModel):
    """Canonical application request for POST /api/v1/presentation/workbench.

    Fail-closed: missing age/birthday, weight, breed, activity, or environment
    is MISSING_REQUIRED_INPUT. No 5-year / 20 kg / Moderate / indoor defaults.
    Name may be empty (display only). Does not invent nested dog: {}.
    Explicit breed_input_state=UNKNOWN is not omitted/blank breed and is not
    an Ω12 mapping status. UNKNOWN cannot enter breed-dependent analysis.
    """

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={"example": WORKBENCH_EXAMPLE_REQUEST},
    )

    name: str | None = Field(default=None, description="Optional display name. Empty string is allowed; not replaced with Dolly/Pet.")
    pet_name: str | None = None
    primary_breed: str | None = Field(
        default=None,
        description="Required unless breeds[0] is supplied or breed_input_state is UNKNOWN. Not Ω12-resolved.",
    )
    secondary_breed: str | None = None
    breeds: list[str] | str | None = None
    breed_input_state: str | None = Field(
        default=None,
        description="Optional. UNKNOWN means the owner does not know the breed. Reuses PersistentDog.breed_input_state. Not an Ω12 mapping status.",
    )
    birthday: str | None = Field(
        default=None,
        description="YYYY-MM-DD. Required if age_years is omitted. Age uses as_of_date when provided, else datetime.now.",
    )
    age_years: float | None = Field(default=None, description="Required if birthday is omitted. Must be > 0.")
    as_of_date: str | None = Field(
        default=None,
        description=(
            "Optional YYYY-MM-DD reference date for birthday → age. Deliberate Ω16 API addition. "
            "When omitted, birthday age still uses datetime.now (documented determinism gap)."
        ),
    )
    weight: float | None = Field(
        default=None,
        description="Body weight in kg. Canonical engine field is DogProfileInput.weight_kg. Required if weight_kg omitted.",
    )
    weight_kg: float | None = Field(
        default=None,
        description="Alias of weight. If both are supplied they must match; the API does not pick one.",
    )
    sex: str | None = Field(default=None, description="Optional free string. Not a closed enum at HTTP.")
    activity_level: str | None = Field(default=None, description="Required. Adapter does not default Moderate.")
    current_environment: str | None = Field(default=None, description="Required. Adapter does not default Temperate Indoor.")
    observed_conditions: list[str] | None = Field(default=None, description="Caller-supplied observations, not warehouse facts.")
    monthly_budget: float | None = Field(default=None, description="Commercial constraint. Never scientific evidence.")
    role_context: dict[str, Any] | None = Field(
        default=None,
        description="Application context. Must not select a different scientific algorithm.",
    )
    correlation_id: str | None = Field(
        default=None,
        description="Request metadata. Distinct from analysis_signature. Does not enter scientific formulas.",
    )
    dog_id: str | None = Field(
        default=None,
        description="Optional persistent dog id. Analysis still uses this request body. Missing dog_id stays transient.",
    )


class ApiErrorDetail(BaseModel):
    code: str = Field(description="Ω11 ToolErrorCode when applicable, e.g. MISSING_REQUIRED_INPUT.")
    message: str
    field: str | None = None
    fields: list[str] = Field(default_factory=list)


class ApiErrorResponse(BaseModel):
    error: ApiErrorDetail


class WorkbenchPresentationResponse(BaseModel):
    """Stable workbench envelope. Nested canonical/roles stay untyped dicts.

    Wrapper fields map to existing sources:
      api_version ← HTTP_API_VERSION (not engine)
      engine_version ← ALGORITHM_VERSION = canonical.analyze.version
      warehouse_version ← DataRepository.version = /health.data_version
      analysis_signature ← sha256 of canonical scientific slices
      presentation_correlation_id ← request metadata
    """

    model_config = ConfigDict(extra="allow")

    schema: str = Field(description="workbench_presentation.v1")
    api_version: str | None = Field(default=None, description="HTTP API label, currently v1. Not the engine version.")
    engine_version: str | None = Field(default=None, description="Copy of ALGORITHM_VERSION / canonical.analyze.version.")
    warehouse_version: str | None = Field(default=None, description="Copy of DataRepository.version.")
    analysis_signature: str
    presentation_correlation_id: str
    demo_catalog: bool
    catalog_source: str
    canonical: dict[str, Any]
    roles: dict[str, Any]


class AnalyzeRawResponse(BaseModel):
    """Documented top-level keys of the raw engine dict. extra allows the rest.

    This model is OpenAPI documentation only. The endpoint returns the unfiltered
    generate_reproducible_report dict and must not be response-filtered.
    """

    model_config = ConfigDict(extra="allow")

    engine: str | None = Field(default=None, description="PPIE")
    version: str | None = Field(default=None, description="ALGORITHM_VERSION (engine), not HTTP API v1.")
    profile: dict[str, Any] | None = None
    healthInsights: list[Any] | None = None
    nutritionalTargets: list[Any] | None = None
    productRecommendations: list[Any] | None = None
    wellnessPackages: list[Any] | None = None
    packageOptions: dict[str, Any] | None = None
    optimizerProvenance: dict[str, Any] | None = None
    scientificEvidence: list[Any] | None = None
    careModel: dict[str, Any] | None = None
    requirementProfile: dict[str, Any] | None = None
