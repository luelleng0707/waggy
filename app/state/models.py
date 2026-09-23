"""Persistent dog-state contracts. Not warehouse facts and not engine DTOs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.state.version import (
    WAGGY_ANALYSIS_RECORD_SCHEMA,
    WAGGY_DOG_STATE_SCHEMA,
    WAGGY_PREFERENCE_SCHEMA,
)

EventType = Literal[
    "PROFILE_UPDATE",
    "GROOMER_OBSERVATION",
    "VETERINARIAN_OBSERVATION",
    "USER_STATEMENT",
    "USER_PREFERENCE",
    "PACKAGE_INTERACTION",
    "ANALYSIS_RUN",
    "SYSTEM_EVENT",
]
PreferenceCategory = Literal[
    "budget",
    "ingredient_exclusion",
    "product_exclusion",
    "product_dislike",
    "package_rejection",
    "package_acceptance",
    "feeding",
    "convenience",
    "subscription",
]
PreferenceStatus = Literal["EXPLICIT"]
PackageAction = Literal[
    "accepted",
    "rejected",
    "asked_why",
    "requested_cheaper",
    "requested_exclusion",
]

FORBIDDEN_EVENT_TYPES = frozenset(
    {
        "SCIENTIFIC",
        "SCIENTIFIC_FACT",
        "DIAGNOSIS",
        "WAREHOUSE_WRITE",
        "NUTRIENT_OVERRIDE",
        "PREVALENCE_UPDATE",
        "PACKAGE_MUTATION",
    }
)
ALLOWED_EVENT_TYPES = frozenset(
    {
        "PROFILE_UPDATE",
        "GROOMER_OBSERVATION",
        "VETERINARIAN_OBSERVATION",
        "USER_STATEMENT",
        "USER_PREFERENCE",
        "PACKAGE_INTERACTION",
        "ANALYSIS_RUN",
        "SYSTEM_EVENT",
    }
)
PUBLIC_EVENT_TYPES = ALLOWED_EVENT_TYPES - {"ANALYSIS_RUN"}
ALLOWED_PREFERENCE_CATEGORIES = frozenset(
    {
        "budget",
        "ingredient_exclusion",
        "product_exclusion",
        "product_dislike",
        "package_rejection",
        "package_acceptance",
        "feeding",
        "convenience",
        "subscription",
    }
)


class PersistentDog(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_DOG_STATE_SCHEMA, alias="schema")
    dog_id: str
    owner_id: str | None = "prototype-local"
    name: str
    primary_breed: str | None = None
    secondary_breed: str | None = None
    breed_split_pct: float | None = None
    birthday: str | None = None
    age_years: float | None = None
    weight_kg: float | None = None
    sex: str | None = None
    activity_level: str | None = None
    current_environment: str | None = None
    height_cm: float | None = None
    bcs: float | None = None
    observed_conditions: list[str] = Field(default_factory=list)
    monthly_budget: float | None = None
    breed_input_state: str | None = Field(
        default=None,
        description="Optional InputState for breed. UNKNOWN is not UNRESOLVED or AMBIGUOUS.",
    )
    created_at: str
    updated_at: str


class PreferenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_PREFERENCE_SCHEMA, alias="schema")
    preference_id: str
    dog_id: str
    category: str
    value: str
    source: str = "USER"
    status: PreferenceStatus = "EXPLICIT"
    event_id: str | None = None
    created_at: str
    superseded: bool = False


class AnalysisRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_ANALYSIS_RECORD_SCHEMA, alias="schema")
    analysis_id: str
    dog_id: str
    analysis_signature: str
    engine_version: str | None = None
    warehouse_version: str | None = None
    input_snapshot: dict[str, Any] = Field(default_factory=dict)
    result_digest: dict[str, Any] = Field(default_factory=dict)
    result_status: str = "ok"
    created_at: str
    correlation_id: str | None = None


class DogCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str | None = None
    owner_id: str | None = "prototype-local"
    name: str
    primary_breed: str | None = None
    secondary_breed: str | None = None
    breed_split_pct: float | None = None
    birthday: str | None = None
    age_years: float | None = None
    weight_kg: float | None = None
    weight: float | None = None
    sex: str | None = None
    activity_level: str | None = None
    current_environment: str | None = None
    height_cm: float | None = None
    bcs: float | None = None
    observed_conditions: list[str] | None = None
    monthly_budget: float | None = None
    breed_input_state: str | None = Field(
        default=None,
        description="Optional. UNKNOWN means the owner does not know the breed.",
    )


class DogPatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    primary_breed: str | None = None
    secondary_breed: str | None = None
    breed_split_pct: float | None = None
    birthday: str | None = None
    age_years: float | None = None
    weight_kg: float | None = None
    weight: float | None = None
    sex: str | None = None
    activity_level: str | None = None
    current_environment: str | None = None
    height_cm: float | None = None
    bcs: float | None = None
    observed_conditions: list[str] | None = None
    monthly_budget: float | None = None
    confirmed: bool = False


class DogEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str
    source: str
    payload: dict[str, Any] = Field(default_factory=dict)
    value: str | None = None
    status: str = "recorded"
    session_id: str | None = None
    correlation_id: str | None = None
    confirmed: bool = False
    notes: str | None = None
    observed_at: str | None = Field(
        default=None,
        description="When the fact was observed. None means observation time is unknown. Not recorded_at.",
    )


class PreferenceCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str
    value: str
    status: str = "EXPLICIT"
    source: str = "USER"


class PreferenceChange(BaseModel):
    """User/commercial constraints only. Not scientific facts or optimizer instructions."""

    model_config = ConfigDict(extra="forbid")

    excluded_ingredients: list[str] | None = None
    monthly_budget: float | None = None


class RecomputationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preference_change: PreferenceChange | None = None
    expected_analysis_signature: str | None = None
    correlation_id: str | None = None
    provenance: str | None = "USER"
