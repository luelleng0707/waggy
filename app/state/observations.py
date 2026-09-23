"""Persist individual physical observations via existing ProfileEvent storage.

Not a second event log. Not breed-derived knowledge. Not a projection engine.
Does not import Ω12, the Core graph, or scientific_care.
"""

from __future__ import annotations

from app.ai.models import EventSource, ProfileEvent
from app.contracts.agent.enums import ObserverRole
from app.contracts.agent.observations import (
    BREED_DERIVED_TRAIT_NAMES,
    PHYSICAL_OBSERVATION_TYPES,
    Observation,
    is_breed_derived_trait_name,
    is_physical_observation_type,
)
from app.state.errors import DogStateError
from app.state.store import events_for, record_event, require_dog

_ROLE_TO_SOURCE: dict[ObserverRole, EventSource] = {
    ObserverRole.CUSTOMER: "USER",
    ObserverRole.GROOMER: "GROOMER",
    ObserverRole.VETERINARIAN: "VETERINARIAN",
    ObserverRole.SYSTEM: "SYSTEM",
}

_SOURCE_TO_ROLE: dict[str, ObserverRole] = {
    "USER": ObserverRole.CUSTOMER,
    "GROOMER": ObserverRole.GROOMER,
    "VETERINARIAN": ObserverRole.VETERINARIAN,
    "SYSTEM": ObserverRole.SYSTEM,
}


def reject_breed_derived_observation_type(observation_type: str | None) -> None:
    if observation_type and is_breed_derived_trait_name(str(observation_type)):
        raise DogStateError(
            "INVALID_EVENT_PAYLOAD",
            "breed-derived trait names cannot be recorded as individual observations",
            field="observation_type",
        )


def record_physical_observation(observation: Observation) -> ProfileEvent:
    """Append one individual observation. Does not overwrite PersistentDog scalars."""
    dog_id = (observation.dog_id or "").strip()
    if not dog_id:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "dog_id is required", field="dog_id")
    require_dog(dog_id)
    observation_type = (observation.observation_type or "").strip()
    if not observation_type:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "observation_type is required", field="observation_type")
    reject_breed_derived_observation_type(observation_type)
    if not is_physical_observation_type(observation_type):
        raise DogStateError(
            "INVALID_EVENT_PAYLOAD",
            "observation_type is not an established physical observation",
            field="observation_type",
        )
    value = (observation.value or "").strip()
    if not value:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "observation value is required", field="value")
    source = _ROLE_TO_SOURCE[observation.observer_role]
    event = record_event(
        dog_id=dog_id,
        source=source,
        kind="observation",
        value=value,
        session_id=observation.source_session_id,
        payload=observation.to_event_payload(),
        observed_at=observation.observed_at,
    )
    return event


def observation_from_event(event: ProfileEvent) -> Observation:
    payload = event.payload or {}
    role_raw = payload.get("observer_role")
    if role_raw:
        observer_role = ObserverRole(str(role_raw))
    else:
        observer_role = _SOURCE_TO_ROLE.get(event.source, ObserverRole.SYSTEM)
    return Observation(
        observation_id=str(payload.get("observation_id") or event.event_id),
        dog_id=event.dog_id,
        observer_role=observer_role,
        observation_type=str(payload.get("observation_type") or ""),
        value=event.value,
        unit=str(payload["unit"]) if payload.get("unit") else None,
        observed_at=event.observed_at,
        recorded_at=event.recorded_at,
        source_session_id=event.session_id,
        confirmation_status=str(payload["confirmation_status"]) if payload.get("confirmation_status") else None,
        timestamp=event.timestamp,
    )


def physical_observations_for(dog_id: str) -> list[Observation]:
    """All stored physical observations, in event order. No conflict resolution."""
    require_dog(dog_id)
    observations: list[Observation] = []
    for event in events_for(dog_id):
        observation_type = (event.payload or {}).get("observation_type")
        if not isinstance(observation_type, str):
            continue
        if observation_type in PHYSICAL_OBSERVATION_TYPES:
            observations.append(observation_from_event(event))
    return observations


def assert_physical_types_are_not_breed_traits() -> None:
    overlap = PHYSICAL_OBSERVATION_TYPES & BREED_DERIVED_TRAIT_NAMES
    if overlap:
        raise RuntimeError(f"physical observation types overlap breed-derived names: {sorted(overlap)}")
