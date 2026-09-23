"""Phase Q — J→N evidence pipeline gate. Tests only. No new semantics."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.contracts.agent.enums import ObserverRole
from app.contracts.agent.input import not_provided, provided
from app.contracts.agent.observations import Observation
from app.contracts.agent.survey import ProfessionalSurveyAnswer, ProfessionalSurveyResponse
from app.state.evidence import get_canonical_observation, get_evidence_history
from app.state.models import DogCreateRequest
from app.state.observations import record_physical_observation
from app.state.store import create_dog, events_for, get_dog
from app.state.survey import record_professional_survey

_PROVENANCE = (
    "observation_id",
    "dog_id",
    "observation_type",
    "value",
    "unit",
    "observer_role",
    "source",
    "observed_at",
    "recorded_at",
    "source_session_id",
    "event_id",
)


def _dog(**overrides) -> DogCreateRequest:
    body = {"name": "Scout", "weight_kg": 18.0, "height_cm": 50.0, "bcs": 5.0, "activity_level": "Moderate"}
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


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def _report(client: TestClient, dog_id: str, **params) -> dict:
    response = client.get(f"/api/v1/dogs/{dog_id}/evidence-report", params=params)
    assert response.status_code == 200
    return response.json()


def _series(payload: dict, observation_type: str) -> dict:
    return next(item for item in payload["series"] if item["observation_type"] == observation_type)


def test_professional_survey_reaches_the_http_report(client: TestClient):
    dog = create_dog(_dog())
    events = record_professional_survey(
        ProfessionalSurveyResponse(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.GROOMER,
            source_session_id="session-groomer-q",
            answers=[
                ProfessionalSurveyAnswer(
                    observation_type="weight_kg",
                    presence=provided("21"),
                    unit="kg",
                    observed_at="2026-09-12T12:00:00+00:00",
                ),
                ProfessionalSurveyAnswer(observation_type="skin_appearance", presence=not_provided()),
            ],
        )
    )
    assert len(events) == 1
    before_ids = [item.event_id for item in events_for(dog.dog_id)]
    before = get_dog(dog.dog_id)
    first = _report(client, dog.dog_id)
    second = _report(client, dog.dog_id)
    assert first["dog_id"] == second["dog_id"]
    assert first["as_of"] == second["as_of"]
    assert first["series"] == second["series"]
    assert [item["observation_type"] for item in first["series"]] == ["weight_kg"]
    row = first["series"][0]["history"][0]
    assert row["value"] == "21"
    assert row["observer_role"] == "groomer"
    assert row["source"] == "GROOMER"
    assert row["observer_role"] != row["source"]
    assert row["observation_id"]
    assert row["event_id"] == events[0].event_id
    assert row["observed_at"] == "2026-09-12T12:00:00+00:00"
    assert row["recorded_at"] == events[0].recorded_at
    assert row["observed_at"] != row["recorded_at"]
    assert row["source_session_id"] == "session-groomer-q"
    for field in _PROVENANCE:
        assert field in row
    after = get_dog(dog.dog_id)
    assert after is not None and before is not None
    assert [item.event_id for item in events_for(dog.dog_id)] == before_ids
    assert after.weight_kg == before.weight_kg == 18.0
    assert after.height_cm == before.height_cm
    assert after.bcs == before.bcs
    assert after.activity_level == before.activity_level


def test_http_source_precedence_is_not_latest_wins(client: TestClient):
    older_vet = create_dog(_dog())
    record_physical_observation(
        _obs(older_vet.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-15T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(older_vet.dog_id, ObserverRole.CUSTOMER, "weight_kg", "25", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    weight = _series(_report(client, older_vet.dog_id), "weight_kg")
    assert [row["value"] for row in weight["history"]] == ["22", "25"]
    phase_l = get_canonical_observation(older_vet.dog_id, "weight_kg")
    assert phase_l is not None
    assert weight["canonical_observation"]["event_id"] == phase_l.event_id
    assert weight["canonical_observation"]["value"] == "22"
    assert weight["canonical_observation"]["observer_role"] == "veterinarian"

    newer_vet = create_dog(_dog(name="Ridge"))
    record_physical_observation(
        _obs(newer_vet.dog_id, ObserverRole.CUSTOMER, "weight_kg", "18", unit="kg", observed_at="2026-09-01T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(newer_vet.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    later = _series(_report(client, newer_vet.dog_id), "weight_kg")
    assert [row["value"] for row in later["history"]] == ["18", "22"]
    assert later["canonical_observation"]["value"] == "22"
    assert later["canonical_observation"]["observer_role"] == "veterinarian"
    assert later["canonical_observation"]["event_id"] == get_canonical_observation(newer_vet.dog_id, "weight_kg").event_id


def test_http_incompatible_units_are_not_converted(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "44", unit="lb", observed_at="2026-09-05T12:00:00+00:00")
    )
    weight = _series(_report(client, dog.dog_id), "weight_kg")
    assert [(row["value"], row["unit"]) for row in weight["history"]] == [("20", "kg"), ("44", "lb")]
    assert weight["timeline"][1]["delta_from_previous"] is None
    stored = get_dog(dog.dog_id)
    assert stored is not None
    assert stored.weight_kg == 18.0


def test_categorical_types_have_no_delta(client: TestClient):
    dog = create_dog(_dog())
    pairs = (
        ("activity_level", "low", "high"),
        ("skin_appearance", "clear", "redness"),
        ("coat_density", "sparse", "dense"),
    )
    for observation_type, first, second in pairs:
        record_physical_observation(
            _obs(dog.dog_id, ObserverRole.CUSTOMER, observation_type, first, observed_at="2026-08-20T12:00:00+00:00")
        )
        record_physical_observation(
            _obs(dog.dog_id, ObserverRole.GROOMER, observation_type, second, observed_at="2026-09-05T12:00:00+00:00")
        )
    payload = _report(client, dog.dog_id)
    for observation_type, _, _ in pairs:
        series = _series(payload, observation_type)
        assert len(series["timeline"]) == 2
        assert all(point["delta_from_previous"] is None for point in series["timeline"])


def test_omitted_units_compare_without_writing_a_unit(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", observed_at="2026-08-20T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", observed_at="2026-09-05T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "height_cm", "50", observed_at="2026-08-20T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "height_cm", "52", observed_at="2026-09-05T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.CUSTOMER, "bcs", "5", observed_at="2026-08-20T12:00:00+00:00"))
    record_physical_observation(_obs(dog.dog_id, ObserverRole.VETERINARIAN, "bcs", "6", observed_at="2026-09-19T12:00:00+00:00"))
    payload = _report(client, dog.dog_id)
    weight = _series(payload, "weight_kg")
    height = _series(payload, "height_cm")
    bcs = _series(payload, "bcs")
    assert [row["unit"] for row in weight["history"]] == [None, None]
    assert [row["unit"] for row in height["history"]] == [None, None]
    assert [row["unit"] for row in bcs["history"]] == [None, None]
    assert weight["timeline"][1]["delta_from_previous"]["delta"] == 1.0
    assert weight["timeline"][1]["delta_from_previous"]["unit"] == "kg"
    assert height["timeline"][1]["delta_from_previous"]["delta"] == 2.0
    assert height["timeline"][1]["delta_from_previous"]["unit"] == "cm"
    assert bcs["timeline"][1]["delta_from_previous"]["delta"] == 1.0
    assert bcs["timeline"][1]["delta_from_previous"]["unit"] is None


def test_generic_event_outside_the_allowlist_is_not_a_report_series(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    created = client.post(
        f"/api/v1/dogs/{dog.dog_id}/events",
        json={
            "event_type": "USER_STATEMENT",
            "source": "USER",
            "value": "long",
            "payload": {"observation_type": "coat_length", "observer_role": "customer"},
        },
    )
    assert created.status_code == 200
    payload = _report(client, dog.dog_id)
    assert [item["observation_type"] for item in payload["series"]] == ["weight_kg"]


def test_as_of_canonical_is_selected_from_filtered_history_only(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "19", unit="kg"))
    early_owner = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-01T12:00:00+00:00")
    )
    early_vet = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-08-15T12:00:00+00:00")
    )
    later_owner = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "25", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    later_vet = record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "30", unit="kg", observed_at="2026-09-20T12:00:00+00:00")
    )
    replay = _report(client, dog.dog_id, observation_type="weight_kg", as_of="2026-09-01T00:00:00+00:00")
    series = _series(replay, "weight_kg")
    assert [row["event_id"] for row in series["history"]] == [early_owner.event_id, early_vet.event_id]
    assert series["canonical_observation"]["event_id"] == early_vet.event_id
    assert series["canonical_observation"]["value"] == "22"
    unfiltered = get_canonical_observation(dog.dog_id, "weight_kg")
    assert unfiltered is not None
    assert unfiltered.event_id == later_vet.event_id
    assert series["canonical_observation"]["event_id"] != unfiltered.event_id
    full_ids = [item.event_id for item in get_evidence_history(dog.dog_id, "weight_kg")]
    assert later_owner.event_id in full_ids
    assert later_vet.event_id in full_ids
    assert later_owner.event_id not in [row["event_id"] for row in series["history"]]
