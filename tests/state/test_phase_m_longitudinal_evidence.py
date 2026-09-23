"""Phase M — longitudinal evidence report, deltas, and as-of replay."""

from __future__ import annotations

from app.contracts.agent.enums import ObserverRole
from app.contracts.agent.observations import Observation
from app.data.breed_knowledge import BreedTraitFact
from app.state.evidence import get_canonical_observation
from app.state.evidence_report import (
    build_evidence_report,
    evidence_report_payload,
)
from app.state.models import DogCreateRequest
from app.state.observations import record_physical_observation
from app.state.store import create_dog, current_projection, get_dog


def _dog(**overrides) -> DogCreateRequest:
    body = {"name": "Scout", "weight_kg": 18.0, "bcs": 5.0, "activity_level": "Moderate"}
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def _obs(dog_id: str, role: ObserverRole, observation_type: str, value: str, **overrides) -> Observation:
    body = {
        "dog_id": dog_id,
        "observer_role": role,
        "observation_type": observation_type,
        "value": value,
    }
    body.update(overrides)
    return Observation.model_validate(body)


def test_full_chronological_history_keeps_owner_groomer_and_vet_visible():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg", observed_at="2026-09-05T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    report = build_evidence_report(dog.dog_id, generated_at="2026-09-20T00:00:00+00:00")
    series = report.series_for("weight_kg")
    assert series is not None
    assert [item.value for item in series.history] == ["20", "21", "22"]
    assert [item.observer_role for item in series.history] == [
        ObserverRole.CUSTOMER,
        ObserverRole.GROOMER,
        ObserverRole.VETERINARIAN,
    ]
    assert [item.source for item in series.history] == ["USER", "GROOMER", "VETERINARIAN"]
    for item in series.history:
        assert item.event_id
        assert item.observation_id
        assert item.observed_at
        assert item.recorded_at
        assert item.observed_at != item.recorded_at
        assert item.source != item.observer_role or item.source == "GROOMER"


def test_canonical_observation_is_reused_from_phase_l():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-15T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "23", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    report = build_evidence_report(dog.dog_id)
    series = report.series_for("weight_kg")
    expected = get_canonical_observation(dog.dog_id, "weight_kg")
    assert series is not None
    assert expected is not None
    assert series.canonical_observation is not None
    assert series.canonical_observation.event_id == expected.event_id
    assert series.canonical_observation.value == "22"
    assert series.canonical_observation.observer_role == ObserverRole.VETERINARIAN
    assert [item.value for item in series.history] == ["22", "23"]


def test_numeric_deltas_and_first_point_has_none():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg", observed_at="2026-09-05T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    series = build_evidence_report(dog.dog_id).series_for("weight_kg")
    assert series is not None
    assert series.timeline[0].delta_from_previous is None
    assert series.timeline[1].delta_from_previous is not None
    assert series.timeline[1].delta_from_previous.delta == 1.0
    assert series.timeline[1].delta_from_previous.unit == "kg"
    assert series.timeline[2].delta_from_previous is not None
    assert series.timeline[2].delta_from_previous.delta == 1.0
    payload = evidence_report_payload(build_evidence_report(dog.dog_id, generated_at="2026-09-20T00:00:00+00:00"))
    assert payload["generated_at"] == "2026-09-20T00:00:00+00:00"
    assert payload["as_of"] is None
    weight = payload["series"][0]
    assert weight["timeline"][0]["delta_from_previous"] is None
    assert weight["timeline"][1]["delta_from_previous"]["delta"] == 1.0


def test_categorical_values_produce_no_delta():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "coat_density", "sparse", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "coat_density", "dense", observed_at="2026-09-05T12:00:00+00:00")
    )
    series = build_evidence_report(dog.dog_id).series_for("coat_density")
    assert series is not None
    assert [item.value for item in series.history] == ["sparse", "dense"]
    assert all(point.delta_from_previous is None for point in series.timeline)


def test_incompatible_units_produce_no_delta():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "44", unit="lb", observed_at="2026-09-05T12:00:00+00:00")
    )
    series = build_evidence_report(dog.dog_id).series_for("weight_kg")
    assert series is not None
    assert [item.value for item in series.history] == ["20", "44"]
    assert series.timeline[1].delta_from_previous is None


def test_missing_observed_at_is_not_fabricated():
    dog = create_dog(_dog())
    event = record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg"))
    report = build_evidence_report(dog.dog_id, generated_at="2026-09-20T00:00:00+00:00")
    series = report.series_for("weight_kg")
    assert series is not None
    assert series.history[0].observed_at is None
    assert series.history[0].recorded_at == event.recorded_at
    assert series.history[0].observed_at != report.generated_at


def test_as_of_excludes_future_and_undated_observations():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    undated = record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg"))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    replay = build_evidence_report(dog.dog_id, as_of="2026-09-01T00:00:00+00:00")
    series = replay.series_for("weight_kg")
    assert series is not None
    assert [item.value for item in series.history] == ["20"]
    assert all(item.event_id != undated.event_id for item in series.history)
    assert replay.as_of == "2026-09-01T00:00:00+00:00"
    full = build_evidence_report(dog.dog_id)
    assert [item.value for item in full.series_for("weight_kg").history] == ["20", "22", "21"]


def test_persistent_dog_is_not_mutated_and_projection_is_not_the_report():
    dog = create_dog(_dog(weight_kg=18.0))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    report = build_evidence_report(dog.dog_id)
    projection = current_projection(dog.dog_id)
    assert get_dog(dog.dog_id).weight_kg == 18.0
    assert set(projection.keys()) == {"history", "current", "dog"}
    assert projection["dog"]["weight_kg"] == 18.0
    assert "series" not in projection
    assert report.series_for("weight_kg").canonical_observation.value == "22"


def test_unknown_breed_dog_can_produce_report():
    dog = create_dog(_dog(breed_input_state="UNKNOWN", primary_breed=None, weight_kg=None))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "height_cm", "55", unit="cm", observed_at="2026-09-01T12:00:00+00:00")
    )
    report = build_evidence_report(dog.dog_id)
    series = report.series_for("height_cm")
    assert series is not None
    assert series.canonical_observation.value == "55"
    assert get_dog(dog.dog_id).primary_breed is None
    assert get_dog(dog.dog_id).breed_input_state == "UNKNOWN"


def test_breed_derived_traits_remain_excluded():
    dog = create_dog(_dog())
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "coat_density", "dense"))
    fact = BreedTraitFact(trait_name="coat_type", trait_value="Double Coat")
    report = build_evidence_report(dog.dog_id)
    assert report.series_for(fact.trait_name) is None
    assert report.series_for("coat_density") is not None
    empty = build_evidence_report(dog.dog_id, observation_type="coat_type")
    assert empty.series == []


def test_same_day_observations_remain_distinct():
    dog = create_dog(_dog())
    first = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "bcs", "5", observed_at="2026-09-19T10:00:00+00:00")
    )
    second = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "bcs", "5.5", observed_at="2026-09-19T12:00:00+00:00")
    )
    third = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "bcs", "6", observed_at="2026-09-19T15:00:00+00:00")
    )
    series = build_evidence_report(dog.dog_id).series_for("bcs")
    assert series is not None
    assert [item.event_id for item in series.history] == [first.event_id, second.event_id, third.event_id]
    assert series.timeline[1].delta_from_previous.delta == 0.5
    assert series.timeline[2].delta_from_previous.delta == 0.5
    assert series.canonical_observation.event_id == third.event_id
