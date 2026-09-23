"""Phase J — individual physical observations reuse Observation + ProfileEvent."""

from __future__ import annotations

import pytest

from app.contracts.agent.enums import DomainKind, ObserverRole
from app.contracts.agent.observations import (
    BREED_DERIVED_TRAIT_NAMES,
    PHYSICAL_OBSERVATION_TYPES,
    Observation,
)
from app.data.breed_knowledge import TRAIT_NAMES, BreedTraitFact
from app.state.errors import DogStateError
from app.state.models import DogCreateRequest
from app.state.observations import (
    observation_from_event,
    physical_observations_for,
    record_physical_observation,
)
from app.state.store import create_dog, events_for, get_dog, record_event


def _dog(**overrides) -> DogCreateRequest:
    body = {"name": "Scout"}
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def test_physical_types_are_disjoint_from_breed_derived_traits():
    assert set(TRAIT_NAMES) == BREED_DERIVED_TRAIT_NAMES
    assert PHYSICAL_OBSERVATION_TYPES.isdisjoint(TRAIT_NAMES)


def test_customer_can_record_a_physical_observation():
    dog = create_dog(_dog())
    event = record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="coat_density",
            value="dense",
        )
    )
    assert event.source == "USER"
    assert event.event_type == "USER_STATEMENT"
    assert event.kind == "observation"
    assert event.payload["observation_type"] == "coat_density"
    assert event.payload["observer_role"] == "customer"
    loaded = physical_observations_for(dog.dog_id)
    assert len(loaded) == 1
    assert loaded[0].observer_role == ObserverRole.CUSTOMER
    assert loaded[0].observation_type == "coat_density"
    assert loaded[0].value == "dense"
    assert loaded[0].domain == DomainKind.OBSERVATION


def test_groomer_can_record_a_physical_observation():
    dog = create_dog(_dog())
    event = record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            observation_type="skin_appearance",
            value="redness",
        )
    )
    assert event.source == "GROOMER"
    assert event.event_type == "GROOMER_OBSERVATION"
    loaded = physical_observations_for(dog.dog_id)
    assert loaded[0].observer_role == ObserverRole.GROOMER
    assert loaded[0].observation_type == "skin_appearance"


def test_veterinarian_uses_the_same_observation_model():
    dog = create_dog(_dog())
    event = record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.VETERINARIAN,
            observation_type="bcs",
            value="6",
        )
    )
    assert event.source == "VETERINARIAN"
    assert event.event_type == "VETERINARIAN_OBSERVATION"
    loaded = observation_from_event(event)
    assert loaded.observer_role == ObserverRole.VETERINARIAN
    assert type(loaded) is Observation


def test_unknown_breed_dog_can_hold_physical_observations():
    dog = create_dog(_dog(breed_input_state="UNKNOWN"))
    assert dog.primary_breed is None
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="weight_kg",
            value="32",
            unit="kg",
        )
    )
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="height_cm",
            value="55",
            unit="cm",
        )
    )
    types = [item.observation_type for item in physical_observations_for(dog.dog_id)]
    assert types == ["weight_kg", "height_cm"]
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.breed_input_state == "UNKNOWN"
    assert loaded.primary_breed is None


def test_observer_role_is_preserved_on_roundtrip():
    dog = create_dog(_dog())
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="coat_density",
            value="dense",
        )
    )
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            observation_type="coat_density",
            value="dense",
        )
    )
    roles = [item.observer_role for item in physical_observations_for(dog.dog_id)]
    assert roles == [ObserverRole.CUSTOMER, ObserverRole.GROOMER]
    dumped = events_for(dog.dog_id)[-1].model_dump(by_alias=True)
    restored = observation_from_event(events_for(dog.dog_id)[-1])
    assert dumped["payload"]["observer_role"] == "groomer"
    assert restored.observer_role == ObserverRole.GROOMER


def test_observed_at_stays_distinct_from_recorded_at():
    dog = create_dog(_dog())
    event = record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="weight_kg",
            value="20",
            unit="kg",
            observed_at="2026-09-19T12:00:00+00:00",
        )
    )
    assert event.observed_at == "2026-09-19T12:00:00+00:00"
    assert event.recorded_at is not None
    assert event.observed_at != event.recorded_at
    loaded = physical_observations_for(dog.dog_id)[0]
    assert loaded.observed_at == "2026-09-19T12:00:00+00:00"
    assert loaded.recorded_at == event.recorded_at
    assert loaded.timestamp == event.timestamp
    assert loaded.timestamp != loaded.observed_at


def test_missing_observed_at_is_not_fabricated():
    dog = create_dog(_dog())
    event = record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            observation_type="height_cm",
            value="58",
            unit="cm",
        )
    )
    assert event.observed_at is None
    assert event.recorded_at is not None
    loaded = physical_observations_for(dog.dog_id)[0]
    assert loaded.observed_at is None
    assert loaded.recorded_at == event.recorded_at


def test_conflicting_observations_remain_separate():
    dog = create_dog(_dog(weight_kg=18.0))
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="weight_kg",
            value="20",
            unit="kg",
        )
    )
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            observation_type="weight_kg",
            value="22",
            unit="kg",
        )
    )
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="coat_density",
            value="medium",
        )
    )
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            observation_type="coat_density",
            value="high",
        )
    )
    weights = [
        item.value
        for item in physical_observations_for(dog.dog_id)
        if item.observation_type == "weight_kg"
    ]
    coats = [
        (item.observer_role, item.value)
        for item in physical_observations_for(dog.dog_id)
        if item.observation_type == "coat_density"
    ]
    assert weights == ["20", "22"]
    assert coats == [(ObserverRole.CUSTOMER, "medium"), (ObserverRole.GROOMER, "high")]
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg == 18.0


def test_physical_observation_does_not_overwrite_persistent_dog_scalars():
    dog = create_dog(_dog(weight_kg=18.0, height_cm=50.0, bcs=5.0, activity_level="Moderate"))
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            observation_type="weight_kg",
            value="22",
            unit="kg",
        )
    )
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.VETERINARIAN,
            observation_type="bcs",
            value="6",
        )
    )
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg == 18.0
    assert loaded.height_cm == 50.0
    assert loaded.bcs == 5.0
    assert loaded.activity_level == "Moderate"


def test_breed_derived_trait_cannot_become_an_individual_observation():
    dog = create_dog(_dog())
    fact = BreedTraitFact(trait_name="coat_type", trait_value="Double Coat")
    assert fact.trait_name in TRAIT_NAMES
    with pytest.raises(DogStateError) as helper_exc:
        record_physical_observation(
            Observation(
                dog_id=dog.dog_id,
                observer_role=ObserverRole.CUSTOMER,
                observation_type=fact.trait_name,
                value=fact.trait_value,
            )
        )
    assert helper_exc.value.code == "INVALID_EVENT_PAYLOAD"
    with pytest.raises(DogStateError) as event_exc:
        record_event(
            dog_id=dog.dog_id,
            source="USER",
            kind="observation",
            value=fact.trait_value,
            event_type="USER_STATEMENT",
            payload={"observation_type": "coat_type", "observer_role": "customer"},
        )
    assert event_exc.value.code == "INVALID_EVENT_PAYLOAD"
    assert physical_observations_for(dog.dog_id) == []


def test_unestablished_physical_type_is_rejected():
    dog = create_dog(_dog())
    with pytest.raises(DogStateError) as exc:
        record_physical_observation(
            Observation(
                dog_id=dog.dog_id,
                observer_role=ObserverRole.CUSTOMER,
                observation_type="coat_length",
                value="SHORT",
            )
        )
    assert exc.value.code == "INVALID_EVENT_PAYLOAD"
    assert exc.value.field == "observation_type"
