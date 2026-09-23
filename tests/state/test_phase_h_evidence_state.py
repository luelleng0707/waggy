"""Phase H — additive evidence/state infrastructure. Does not migrate Core."""

from __future__ import annotations

from app.contracts.agent.enums import InputState, ObserverRole
from app.contracts.agent.input import CanonicalDogInput, provided, unknown
from app.contracts.agent.observations import Observation
from app.normalization.enums import MappingStatus
from app.normalization.resolver import resolve_breed
from app.state.errors import DogStateError
from app.state.models import DogCreateRequest
from app.state.store import create_dog, events_for, get_dog, record_event
import pytest


def _dog(**overrides) -> DogCreateRequest:
    body = {"name": "Scout"}
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def test_observation_keeps_observed_at_distinct_from_recorded_at():
    obs = Observation(
        observer_role=ObserverRole.GROOMER,
        observation_type="weight_kg",
        value="28",
        unit="kg",
        observed_at="2026-09-20T12:00:00+00:00",
        recorded_at="2026-09-22T08:00:00+00:00",
    )
    assert obs.observed_at == "2026-09-20T12:00:00+00:00"
    assert obs.recorded_at == "2026-09-22T08:00:00+00:00"
    assert obs.observed_at != obs.recorded_at
    assert obs.timestamp is None


def test_observation_unknown_observed_at_is_not_fabricated():
    obs = Observation(
        observer_role=ObserverRole.CUSTOMER,
        observation_type="weight_kg",
        value="20",
        unit="kg",
    )
    assert obs.observed_at is None
    assert obs.recorded_at is None
    assert obs.timestamp is None


def test_record_event_preserves_observed_at_and_sets_recorded_at():
    dog = create_dog(_dog())
    event = record_event(
        dog_id=dog.dog_id,
        source="GROOMER",
        kind="observation",
        value="28",
        event_type="GROOMER_OBSERVATION",
        payload={"observation_type": "weight_kg", "unit": "kg"},
        observed_at="2026-09-20T12:00:00+00:00",
    )
    assert event.observed_at == "2026-09-20T12:00:00+00:00"
    assert event.recorded_at is not None
    assert event.observed_at != event.recorded_at
    assert event.timestamp is not None
    loaded = events_for(dog.dog_id)
    stored = next(item for item in loaded if item.event_id == event.event_id)
    assert stored.observed_at == "2026-09-20T12:00:00+00:00"
    assert stored.recorded_at == event.recorded_at


def test_record_event_does_not_fabricate_observed_at():
    dog = create_dog(_dog())
    event = record_event(
        dog_id=dog.dog_id,
        source="USER",
        kind="observation",
        value="20",
        event_type="USER_STATEMENT",
        payload={"observation_type": "weight_kg"},
    )
    assert event.observed_at is None
    assert event.recorded_at is not None
    assert event.timestamp == event.created_at


def test_observer_roles_owner_groomer_remain_and_veterinarian_is_representable():
    assert ObserverRole.CUSTOMER == "customer"
    assert ObserverRole.GROOMER == "groomer"
    assert ObserverRole.SYSTEM == "system"
    assert ObserverRole.VETERINARIAN == "veterinarian"
    owner = Observation(observer_role=ObserverRole.CUSTOMER, observation_type="scratching", value="frequent")
    groomer = Observation(observer_role=ObserverRole.GROOMER, observation_type="skin_appearance", value="redness")
    vet = Observation(observer_role=ObserverRole.VETERINARIAN, observation_type="clinical_note", value="exam recorded")
    assert owner.observer_role != groomer.observer_role
    assert vet.observer_role == ObserverRole.VETERINARIAN


def test_multiple_observers_are_preserved_separately():
    dog = create_dog(_dog())
    record_event(
        dog_id=dog.dog_id,
        source="USER",
        kind="observation",
        value="scratches frequently at home",
        event_type="USER_STATEMENT",
        payload={"observer_role": "customer", "observation_type": "scratching"},
    )
    record_event(
        dog_id=dog.dog_id,
        source="GROOMER",
        kind="observation",
        value="visible skin redness",
        event_type="GROOMER_OBSERVATION",
        payload={"observer_role": "groomer", "observation_type": "skin_appearance"},
    )
    record_event(
        dog_id=dog.dog_id,
        source="VETERINARIAN",
        kind="observation",
        value="clinical exam note",
        event_type="VETERINARIAN_OBSERVATION",
        payload={"observer_role": "veterinarian", "observation_type": "clinical_note"},
    )
    history = [item for item in events_for(dog.dog_id) if item.kind == "observation"]
    sources = [item.source for item in history]
    values = [item.value for item in history]
    assert sources.count("USER") == 1
    assert sources.count("GROOMER") == 1
    assert sources.count("VETERINARIAN") == 1
    assert "scratches frequently at home" in values
    assert "visible skin redness" in values
    assert "clinical exam note" in values
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg is None


def test_conflicting_weight_observations_are_not_collapsed():
    dog = create_dog(_dog(weight_kg=18.0))
    record_event(
        dog_id=dog.dog_id,
        source="USER",
        kind="observation",
        value="20",
        event_type="USER_STATEMENT",
        payload={"observation_type": "weight_kg", "unit": "kg"},
    )
    record_event(
        dog_id=dog.dog_id,
        source="GROOMER",
        kind="observation",
        value="22",
        event_type="GROOMER_OBSERVATION",
        payload={"observation_type": "weight_kg", "unit": "kg"},
    )
    weights = [
        item.value
        for item in events_for(dog.dog_id)
        if item.kind == "observation" and item.payload.get("observation_type") == "weight_kg"
    ]
    assert weights == ["20", "22"]
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg == 18.0


def test_unknown_breed_is_not_unresolved_or_ambiguous():
    dog = create_dog(_dog(breed_input_state="UNKNOWN"))
    assert dog.primary_breed is None
    assert dog.breed_input_state == InputState.UNKNOWN
    assert dog.breed_input_state != MappingStatus.UNRESOLVED
    assert dog.breed_input_state != MappingStatus.AMBIGUOUS
    canonical = CanonicalDogInput(
        name=provided("Scout"),
        primary_breed=unknown(),
        age_years=provided(2.0),
        weight_kg=provided(12.0),
    )
    assert canonical.primary_breed.state == InputState.UNKNOWN
    assert canonical.primary_breed.value is None
    assert canonical.primary_breed.state != MappingStatus.UNRESOLVED
    assert canonical.primary_breed.state != MappingStatus.AMBIGUOUS
    omega = resolve_breed("Corgi")
    assert omega.status == MappingStatus.UNRESOLVED
    assert omega.status != InputState.UNKNOWN


def test_unknown_breed_cannot_carry_a_breed_string():
    with pytest.raises(DogStateError) as exc:
        create_dog(_dog(primary_breed="Labrador Retriever", breed_input_state="UNKNOWN"))
    assert exc.value.code == "INVALID_EVENT_PAYLOAD"


def test_omega12_statuses_unchanged_by_evidence_state():
    assert resolve_breed("Labrador Retriever").status == MappingStatus.RESOLVED
    assert resolve_breed("Retriever").status == MappingStatus.AMBIGUOUS
    assert resolve_breed("Corgi").status == MappingStatus.UNRESOLVED
    assert resolve_breed("").status == MappingStatus.UNRESOLVED
    assert resolve_breed("Lab x Golden").status == MappingStatus.MIXED

