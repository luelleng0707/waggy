"""Professional survey envelope. Not a pet profile and not a second evidence model.

GROOMER and VETERINARIAN share Observation. This module does not import
Ω12, Core, scientific_care, or product/package code.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.contracts.agent.enums import InputState, ObserverRole
from app.contracts.agent.input import FieldValue
from app.contracts.agent.observations import (
    Observation,
    is_breed_derived_trait_name,
    is_physical_observation_type,
)

PROFESSIONAL_SURVEY_ROLES = frozenset({ObserverRole.GROOMER, ObserverRole.VETERINARIAN})

# Reuse InputState. NOT_ASSESSED is not an existing enum member.
# NOT_PROVIDED is the established stand-in for "this item was not assessed."
SURVEY_ANSWER_STATES = frozenset(
    {
        InputState.PROVIDED,
        InputState.UNKNOWN,
        InputState.NOT_PROVIDED,
        InputState.NOT_APPLICABLE,
    }
)


class ProfessionalSurveyAnswer(BaseModel):
    """One professional answer for an established physical observation type.

    PROVIDED carries a value and becomes an Observation.
    UNKNOWN / NOT_PROVIDED / NOT_APPLICABLE carry no value and do not become
    Observation rows.
    """

    model_config = ConfigDict(extra="forbid")

    observation_type: str
    presence: FieldValue[str]
    unit: str | None = None
    observed_at: str | None = Field(
        default=None,
        description="When this answer was observed. None means unknown. Not recorded_at.",
    )

    @model_validator(mode="after")
    def _type_and_state_are_established(self) -> ProfessionalSurveyAnswer:
        if is_breed_derived_trait_name(self.observation_type):
            raise ValueError("breed-derived trait names cannot be professional survey answers")
        if not is_physical_observation_type(self.observation_type):
            raise ValueError("observation_type is not an established physical observation")
        if self.presence.state not in SURVEY_ANSWER_STATES:
            raise ValueError("survey answer state must be an InputState, not an Ω12 mapping status")
        if self.presence.state != InputState.PROVIDED and self.observed_at is not None:
            raise ValueError("non-PROVIDED survey answers must not carry observed_at")
        return self

    def to_observation(
        self,
        *,
        dog_id: str,
        observer_role: ObserverRole,
        source_session_id: str | None = None,
    ) -> Observation | None:
        if self.presence.state != InputState.PROVIDED or self.presence.value is None:
            return None
        return Observation(
            dog_id=dog_id,
            observer_role=observer_role,
            observation_type=self.observation_type,
            value=str(self.presence.value),
            unit=self.unit,
            observed_at=self.observed_at,
            source_session_id=source_session_id,
        )


class ProfessionalSurveyResponse(BaseModel):
    """Envelope around professional Observation objects. Not a pet profile."""

    model_config = ConfigDict(extra="forbid")

    dog_id: str
    observer_role: ObserverRole
    answers: list[ProfessionalSurveyAnswer] = Field(default_factory=list)
    source_session_id: str | None = None

    @model_validator(mode="after")
    def _professional_role_and_identity(self) -> ProfessionalSurveyResponse:
        if not (self.dog_id or "").strip():
            raise ValueError("dog_id is required")
        if self.observer_role not in PROFESSIONAL_SURVEY_ROLES:
            raise ValueError("observer_role must be GROOMER or VETERINARIAN")
        return self

    def observations(self) -> list[Observation]:
        """PROVIDED answers only. UNKNOWN / NOT_PROVIDED do not invent Observation values."""
        out: list[Observation] = []
        for answer in self.answers:
            item = answer.to_observation(
                dog_id=self.dog_id.strip(),
                observer_role=self.observer_role,
                source_session_id=self.source_session_id,
            )
            if item is not None:
                out.append(item)
        return out
