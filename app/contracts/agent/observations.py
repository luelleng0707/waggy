"""Groomer/customer observations. Not scientific facts and not diagnoses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, ObserverRole


class Observation(BaseModel):
    """Individual-dog observation.

    OBSERVATION ≠ SCIENTIFIC_FACT
    OBSERVATION ≠ DIAGNOSIS

    The engine may later map an observation to an existing warehouse
    trait/relationship if that mapping exists. This model does not perform
    that mapping and has no diagnosis field.
    """

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.OBSERVATION
    observation_id: str | None = None
    dog_id: str | None = None
    observer_role: ObserverRole
    observation_type: str = Field(
        description="e.g. coat_density, morphology, observed_sign — not a diagnosis code",
    )
    value: str
    unit: str | None = None
    confidence: str | None = Field(
        default=None,
        description="Optional; warehouse facts already use a confidence column.",
    )
    timestamp: str | None = None
    source_session_id: str | None = Field(
        default=None,
        description="Explicit session id if authorized persistent state is used. Not hidden merge.",
    )
    confirmation_status: str | None = None
