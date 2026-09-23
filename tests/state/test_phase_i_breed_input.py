"""Phase I — persist UNKNOWN reuses breed_input_state and fails closed before Core."""

from __future__ import annotations

import pytest

from app.contracts.agent.adapters import engine_profile_from_canonical
from app.contracts.agent.enums import InputState
from app.contracts.agent.input import CanonicalDogInput, provided, unknown
from app.normalization.enums import MappingStatus
from app.normalization.resolver import resolve_breed
from app.state.errors import DogStateError
from app.state.models import DogCreateRequest
from app.state.projection import dog_to_workbench_body, project_to_dog_profile_input
from app.state.store import create_dog


def _dog(**overrides) -> DogCreateRequest:
    body = {
        "name": "Scout",
        "age_years": 4.0,
        "weight_kg": 18.0,
        "activity_level": "Moderate",
        "current_environment": "Temperate Indoor",
    }
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def test_persist_unknown_reuses_breed_input_state_without_breed_string():
    dog = create_dog(_dog(breed_input_state="UNKNOWN"))
    assert dog.breed_input_state == InputState.UNKNOWN
    assert dog.primary_breed is None
    assert dog.breed_input_state != MappingStatus.UNRESOLVED
    assert dog.breed_input_state != MappingStatus.AMBIGUOUS
    body = dog_to_workbench_body(dog)
    assert body["breed_input_state"] == InputState.UNKNOWN
    assert "primary_breed" not in body


def test_persist_unknown_cannot_carry_a_breed_string():
    with pytest.raises(DogStateError) as exc:
        create_dog(_dog(primary_breed="Labrador Retriever", breed_input_state="UNKNOWN"))
    assert exc.value.code == "INVALID_EVENT_PAYLOAD"


def test_unknown_projection_fails_closed_and_is_not_omitted_breed():
    unknown_dog = create_dog(_dog(breed_input_state="UNKNOWN"))
    with pytest.raises(DogStateError) as unknown_exc:
        project_to_dog_profile_input(unknown_dog.dog_id)
    assert unknown_exc.value.code == "INVALID_INPUT"
    assert unknown_exc.value.field == "breed_input_state"
    assert "UNKNOWN" in str(unknown_exc.value)

    omitted = create_dog(DogCreateRequest(name="Incomplete"))
    with pytest.raises(DogStateError) as omitted_exc:
        project_to_dog_profile_input(omitted.dog_id)
    assert omitted_exc.value.code == "MISSING_REQUIRED_PROFILE_INPUT"
    assert omitted_exc.value.code != unknown_exc.value.code


def test_known_breed_projection_unchanged():
    dog = create_dog(
        _dog(
            primary_breed="Labrador Retriever",
            secondary_breed="Golden Retriever",
        )
    )
    profile = project_to_dog_profile_input(dog.dog_id)
    assert profile.primary_breed == "Labrador Retriever"
    assert profile.secondary_breed == "Golden Retriever"
    assert resolve_breed("Labrador Retriever").status == MappingStatus.RESOLVED


def test_engine_adapter_refuses_unknown_without_fabricating_a_breed():
    dog = CanonicalDogInput(
        name=provided("Scout"),
        primary_breed=unknown(),
        age_years=provided(2.0),
        weight_kg=provided(12.0),
        environment=provided("Temperate Indoor"),
        activity_level=provided("Moderate"),
    )
    with pytest.raises(ValueError, match="UNKNOWN breed cannot enter breed-dependent analysis"):
        engine_profile_from_canonical(dog)
    assert dog.primary_breed.value is None
    assert resolve_breed("Corgi").status == MappingStatus.UNRESOLVED
    assert resolve_breed("Corgi").status != dog.primary_breed.state
