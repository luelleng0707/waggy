"""Canonical dog input. Distinguishes PROVIDED from UNKNOWN / NOT_PROVIDED."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.contracts.agent.enums import DomainKind, InputState
from app.contracts.agent.errors import ToolError, invalid_input, missing_required_input
from app.contracts.agent.observations import Observation

T = TypeVar("T")

REQUIRED_FOR_TOOLS = ("primary_breed", "age_years", "weight_kg")


class FieldValue(BaseModel, Generic[T]):
    """A scalar with an explicit presence state.

    UNKNOWN is not 0, false, or an average.
    NOT_PROVIDED is not a default.
    INVALID may retain the rejected value for diagnostics.
    """

    model_config = ConfigDict(extra="forbid")

    state: InputState
    value: T | None = None

    @model_validator(mode="after")
    def _state_matches_value(self) -> FieldValue[T]:
        if self.state == InputState.PROVIDED and self.value is None:
            raise ValueError("PROVIDED requires a value")
        if self.state in {InputState.UNKNOWN, InputState.NOT_PROVIDED, InputState.NOT_APPLICABLE}:
            if self.value is not None:
                raise ValueError(f"{self.state} must not carry a value")
        return self


def provided(value: T) -> FieldValue[T]:
    return FieldValue[T](state=InputState.PROVIDED, value=value)


def not_provided() -> FieldValue[T]:
    return FieldValue[T](state=InputState.NOT_PROVIDED, value=None)


def unknown() -> FieldValue[T]:
    return FieldValue[T](state=InputState.UNKNOWN, value=None)


def not_applicable() -> FieldValue[T]:
    return FieldValue[T](state=InputState.NOT_APPLICABLE, value=None)


def invalid(value: T | None = None) -> FieldValue[T]:
    return FieldValue[T](state=InputState.INVALID, value=value)


class CanonicalDogInput(BaseModel):
    """User-provided dog profile for future tools.

    This is not scientific evidence. A stated breed or weight remains input.

    Required for tool execution: primary_breed, age_years, weight_kg — all
    PROVIDED. Missing required fields become MISSING_REQUIRED_INPUT.
    This model does not default age to 5 or weight to 20.
    """

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.USER_INPUT
    dog_id: str | None = Field(
        default=None,
        description="Optional. Existing convention DOG::{name.lower()} is a documented gap.",
    )
    name: FieldValue[str] = Field(default_factory=not_provided)
    primary_breed: FieldValue[str] = Field(default_factory=not_provided)
    secondary_breed: FieldValue[str] = Field(default_factory=not_provided)
    breed_split_pct: FieldValue[float] = Field(default_factory=not_provided)
    age_years: FieldValue[float] = Field(default_factory=not_provided)
    birthday: FieldValue[str] = Field(default_factory=not_provided)
    weight_kg: FieldValue[float] = Field(default_factory=not_provided)
    sex: FieldValue[str] = Field(default_factory=not_provided)
    activity_level: FieldValue[str] = Field(default_factory=not_provided)
    environment: FieldValue[str] = Field(default_factory=not_provided)
    height_cm: FieldValue[float] = Field(default_factory=not_provided)
    bcs: FieldValue[float] = Field(default_factory=not_provided)
    monthly_budget: FieldValue[float] = Field(default_factory=not_provided)
    observations: list[Observation] = Field(default_factory=list)

    def missing_required_fields(self) -> list[str]:
        missing: list[str] = []
        for name in REQUIRED_FOR_TOOLS:
            field = getattr(self, name)
            if field.state != InputState.PROVIDED or field.value is None:
                missing.append(name)
        return missing

    def invalid_fields(self) -> list[str]:
        names = [
            "name",
            "primary_breed",
            "secondary_breed",
            "breed_split_pct",
            "age_years",
            "birthday",
            "weight_kg",
            "sex",
            "activity_level",
            "environment",
            "height_cm",
            "bcs",
            "monthly_budget",
        ]
        return [name for name in names if getattr(self, name).state == InputState.INVALID]

    def validate_for_tools(self) -> ToolError | None:
        invalid_names = self.invalid_fields()
        if invalid_names:
            return invalid_input(invalid_names)
        missing = self.missing_required_fields()
        if missing:
            return missing_required_input(missing)
        return None
