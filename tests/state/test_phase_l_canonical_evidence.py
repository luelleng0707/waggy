"""Phase L — read-only evidence history, provenance, and canonical selection."""

from __future__ import annotations

from app.contracts.agent.enums import ObserverRole
from app.contracts.agent.observations import Observation
from app.data.breed_knowledge import BreedTraitFact
from app.normalization.enums import MappingStatus
from app.state.evidence import (
    build_evidence_profile,
    evidence_profile_payload,
    get_canonical_observation,
    get_evidence_history,
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


def test_owner_groomer_and_veterinarian_appear_in_history():
    dog = create_dog(_dog())
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "18", unit="kg", observed_at="2026-09-01T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "20", unit="kg", observed_at="2026-09-12T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00"))
    history = get_evidence_history(dog.dog_id, "weight_kg")
    roles = [item.observer_role for item in history]
    values = [item.value for item in history]
    assert roles == [ObserverRole.CUSTOMER, ObserverRole.GROOMER, ObserverRole.VETERINARIAN]
    assert values == ["18", "20", "22"]
    assert len(history) == 3


def test_conflicts_remain_separate_and_are_not_averaged():
    dog = create_dog(_dog(weight_kg=18.0))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg"))
    values = [item.value for item in get_evidence_history(dog.dog_id, "weight_kg")]
    assert values == ["20", "21", "22"]
    assert "21.0" not in values
    assert get_dog(dog.dog_id).weight_kg == 18.0


def test_provenance_and_event_id_are_preserved():
    dog = create_dog(_dog())
    event = record_physical_observation(
        _obs(
            dog.dog_id,
            ObserverRole.GROOMER,
            "coat_density",
            "dense",
            observed_at="2026-09-12T12:00:00+00:00",
            source_session_id="session-groomer-1",
        )
    )
    row = get_evidence_history(dog.dog_id, "coat_density")[0]
    assert row.event_id == event.event_id
    assert row.observation_id
    assert row.source == "GROOMER"
    assert row.observer_role == ObserverRole.GROOMER
    assert row.source != row.observer_role
    assert row.source_session_id == "session-groomer-1"
    assert row.observed_at == "2026-09-12T12:00:00+00:00"
    assert row.recorded_at == event.recorded_at
    assert row.observed_at != row.recorded_at
    assert "confidence" not in row.model_fields or row.model_dump().get("confidence") is None
    dumped = row.model_dump()
    assert "authority" not in dumped
    assert "evidence_score" not in dumped
    assert MappingStatus.UNRESOLVED.value not in dumped.values()


def test_missing_observed_at_is_not_fabricated_from_recorded_at():
    dog = create_dog(_dog())
    event = record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg"))
    row = get_evidence_history(dog.dog_id, "weight_kg")[0]
    assert event.observed_at is None
    assert row.observed_at is None
    assert row.recorded_at is not None
    assert row.recorded_at == event.recorded_at


def test_unknown_breed_dog_can_build_evidence_profile():
    dog = create_dog(_dog(breed_input_state="UNKNOWN", primary_breed=None, weight_kg=None))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "height_cm", "55", unit="cm", observed_at="2026-09-01T12:00:00+00:00"))
    profile = build_evidence_profile(dog.dog_id)
    assert profile.dog_id == dog.dog_id
    series = profile.series_for("height_cm")
    assert series is not None
    assert series.canonical_observation is not None
    assert series.canonical_observation.value == "55"
    assert get_dog(dog.dog_id).primary_breed is None
    assert get_dog(dog.dog_id).breed_input_state == "UNKNOWN"


def test_breed_derived_trait_is_never_physical_evidence():
    dog = create_dog(_dog())
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "coat_density", "dense"))
    fact = BreedTraitFact(trait_name="coat_type", trait_value="Double Coat")
    assert get_evidence_history(dog.dog_id, fact.trait_name) == []
    assert get_canonical_observation(dog.dog_id, "coat_type") is None
    types = [item.observation_type for item in build_evidence_profile(dog.dog_id).series]
    assert "coat_type" not in types
    assert "coat_density" in types


def test_current_projection_is_unchanged_and_persistent_dog_is_not_updated():
    dog = create_dog(_dog(weight_kg=18.0))
    before = current_projection(dog.dog_id)
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    after = current_projection(dog.dog_id)
    assert set(before.keys()) == {"history", "current", "dog"}
    assert set(after.keys()) == {"history", "current", "dog"}
    assert after["dog"]["weight_kg"] == 18.0
    canonical = get_canonical_observation(dog.dog_id, "weight_kg")
    assert canonical is not None
    assert canonical.value == "22"
    assert get_dog(dog.dog_id).weight_kg == 18.0


def test_source_precedence_beats_newer_lower_precedence():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-15T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "23", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    canonical = get_canonical_observation(dog.dog_id, "weight_kg")
    assert canonical is not None
    assert canonical.value == "22"
    assert canonical.observer_role == ObserverRole.VETERINARIAN
    history = get_evidence_history(dog.dog_id, "weight_kg")
    assert [item.value for item in history] == ["22", "23"]


def test_recency_within_same_source_class():
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-15T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "23", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    canonical = get_canonical_observation(dog.dog_id, "weight_kg")
    assert canonical is not None
    assert canonical.value == "23"
    assert canonical.observer_role == ObserverRole.VETERINARIAN


def test_same_day_observations_remain_distinct():
    dog = create_dog(_dog())
    first = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "bcs", "5", observed_at="2026-09-19T09:00:00+00:00")
    )
    second = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "bcs", "6", observed_at="2026-09-19T15:00:00+00:00")
    )
    history = get_evidence_history(dog.dog_id, "bcs")
    assert [item.event_id for item in history] == [first.event_id, second.event_id]
    assert [item.value for item in history] == ["5", "6"]
    canonical = get_canonical_observation(dog.dog_id, "bcs")
    assert canonical is not None
    assert canonical.event_id == second.event_id


def test_missing_observed_at_does_not_take_another_records_date():
    dog = create_dog(_dog())
    owner = record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg"))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    history = get_evidence_history(dog.dog_id, "weight_kg")
    owner_row = next(item for item in history if item.event_id == owner.event_id)
    assert owner_row.observed_at is None
    canonical = get_canonical_observation(dog.dog_id, "weight_kg")
    assert canonical is not None
    assert canonical.value == "21"
    assert canonical.observer_role == ObserverRole.GROOMER


def test_history_filter_and_profile_omits_types_without_evidence():
    dog = create_dog(_dog())
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "skin_appearance", "redness"))
    assert [item.observation_type for item in get_evidence_history(dog.dog_id)] == ["skin_appearance"]
    assert get_evidence_history(dog.dog_id, "weight_kg") == []
    profile = build_evidence_profile(dog.dog_id)
    assert [item.observation_type for item in profile.series] == ["skin_appearance"]
    assert profile.series_for("weight_kg") is None
    assert get_canonical_observation(dog.dog_id, "weight_kg") is None


def test_inbody_style_report_keeps_traceable_points():
    dog = create_dog(_dog(weight_kg=18.0))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "18", unit="kg", observed_at="2026-09-01T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "20", unit="kg", observed_at="2026-09-12T12:00:00+00:00")
    )
    vet = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "bcs", "6", observed_at="2026-09-19T12:00:00+00:00")
    )
    payload = evidence_profile_payload(build_evidence_profile(dog.dog_id))
    weight = next(item for item in payload["physical_evidence"] if item["observation_type"] == "weight_kg")
    assert weight["canonical"]["value"] == "22"
    assert weight["canonical"]["observer_role"] == "veterinarian"
    assert weight["canonical"]["event_id"] == vet.event_id
    assert weight["canonical"]["observed_at"] == "2026-09-19T12:00:00+00:00"
    assert [row["value"] for row in weight["history"]] == ["18", "20", "22"]
    for row in weight["history"]:
        assert row["event_id"]
        assert row["observer_role"]
        assert "observed_at" in row
        assert "recorded_at" in row
    assert get_dog(dog.dog_id).weight_kg == 18.0
