"""Individual pet observations. Not scientific facts, diagnoses, or breed-derived traits."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, ObserverRole

# Individual-observable types already used as persist fields or Observation examples.
# Not warehouse TRAIT_NAMES (size, body_type, coat_type, energy, skull_type, …).
PHYSICAL_OBSERVATION_TYPES = frozenset(
    {
        "weight_kg",
        "height_cm",
        "bcs",
        "activity_level",
        "coat_density",
        "skin_appearance",
    }
)

# Must stay aligned with app.data.breed_knowledge.TRAIT_NAMES. Copied here so
# observation contracts do not import warehouse/knowledge modules.
BREED_DERIVED_TRAIT_NAMES = frozenset(
    {
        "size",
        "body_type",
        "coat_type",
        "energy",
        "skull_type",
        "climate",
        "lifespan",
        "weakness_group",
        "function_group",
    }
)


class Observation(BaseModel):
    """Individual-pet observation.

    OBSERVATION ≠ SCIENTIFIC_FACT
    OBSERVATION ≠ DIAGNOSIS
    OBSERVATION ≠ BreedTraitFact / warehouse TRAIT_NAMES

    This model does not map an observation to breed knowledge and has no
    diagnosis field. Values stay caller-supplied strings; this phase does
    not invent categorical enums.
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
    timestamp: str | None = Field(
        default=None,
        description="Legacy optional stamp. Not observed_at and not recorded_at.",
    )
    observed_at: str | None = Field(
        default=None,
        description="When the fact was observed. None means observation time is unknown.",
    )
    recorded_at: str | None = Field(
        default=None,
        description="When Waggy stored the observation. Distinct from observed_at.",
    )
    source_session_id: str | None = Field(
        default=None,
        description="Explicit session id if authorized persistent state is used. Not hidden merge.",
    )
    confirmation_status: str | None = None

    def to_event_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "observation_type": self.observation_type,
            "observer_role": self.observer_role.value,
            "value": self.value,
        }
        if self.unit:
            payload["unit"] = self.unit
        if self.observation_id:
            payload["observation_id"] = self.observation_id
        if self.confirmation_status:
            payload["confirmation_status"] = self.confirmation_status
        return payload


def is_breed_derived_trait_name(observation_type: str) -> bool:
    return observation_type in BREED_DERIVED_TRAIT_NAMES


def is_physical_observation_type(observation_type: str) -> bool:
    return observation_type in PHYSICAL_OBSERVATION_TYPES
