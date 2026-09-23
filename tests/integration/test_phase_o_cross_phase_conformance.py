"""Phase O — J→K→L→M→N conformance. Tests only. No new evidence policy."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.contracts.agent.enums import InputState, ObserverRole
from app.contracts.agent.input import not_applicable, not_provided, provided, unknown
from app.contracts.agent.observations import Observation
from app.contracts.agent.survey import ProfessionalSurveyAnswer, ProfessionalSurveyResponse
from app.state.evidence import get_canonical_observation
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
    body = {"name": "Scout", "weight_kg": 18.0, "bcs": 5.0, "activity_level": "Moderate", "height_cm": 50.0}
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


def _answer(observation_type: str, presence, **overrides) -> ProfessionalSurveyAnswer:
    body = {"observation_type": observation_type, "presence": presence}
    body.update(overrides)
    return ProfessionalSurveyAnswer.model_validate(body)


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


def test_professional_survey_provided_reaches_n_and_absent_answers_do_not(client: TestClient):
    dog = create_dog(_dog())
    survey = ProfessionalSurveyResponse(
        dog_id=dog.dog_id,
        observer_role=ObserverRole.VETERINARIAN,
        source_session_id="session-vet-survey",
        answers=[
            _answer("weight_kg", provided("22"), unit="kg", observed_at="2026-09-19T12:00:00+00:00"),
            _answer("skin_appearance", unknown()),
            _answer("activity_level", not_provided()),
            _answer("bcs", not_applicable()),
        ],
    )
    assert survey.answers[1].presence.state == InputState.UNKNOWN
    assert survey.answers[2].presence.state == InputState.NOT_PROVIDED
    assert survey.answers[3].presence.state == InputState.NOT_APPLICABLE
    events = record_professional_survey(survey)
    assert len(events) == 1
    payload = _report(client, dog.dog_id)
    assert [item["observation_type"] for item in payload["series"]] == ["weight_kg"]
    row = payload["series"][0]["history"][0]
    assert row["value"] == "22"
    assert row["observer_role"] == "veterinarian"
    assert row["source"] == "VETERINARIAN"
    assert row["observer_role"] != row["source"]
    assert row["source_session_id"] == "session-vet-survey"
    assert row["event_id"] == events[0].event_id
    assert row["observed_at"] == "2026-09-19T12:00:00+00:00"
    assert row["recorded_at"] == events[0].recorded_at
    assert row["observed_at"] != row["recorded_at"]
    for field in _PROVENANCE:
        assert field in row
    assert "skin_appearance" not in [item["observation_type"] for item in payload["series"]]
    assert "activity_level" not in [item["observation_type"] for item in payload["series"]]
    assert "bcs" not in [item["observation_type"] for item in payload["series"]]


def test_http_canonical_follows_phase_l_source_precedence(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(
            dog.dog_id,
            ObserverRole.VETERINARIAN,
            "weight_kg",
            "22",
            unit="kg",
            observed_at="2026-09-15T12:00:00+00:00",
            source_session_id="session-vet-1",
        )
    )
    record_physical_observation(
        _obs(
            dog.dog_id,
            ObserverRole.CUSTOMER,
            "weight_kg",
            "23",
            unit="kg",
            observed_at="2026-09-19T12:00:00+00:00",
            source_session_id="session-owner-1",
        )
    )
    payload = _report(client, dog.dog_id)
    weight = _series(payload, "weight_kg")
    assert [row["value"] for row in weight["history"]] == ["22", "23"]
    expected = get_canonical_observation(dog.dog_id, "weight_kg")
    assert expected is not None
    assert weight["canonical_observation"]["event_id"] == expected.event_id
    assert weight["canonical_observation"]["value"] == "22"
    assert weight["canonical_observation"]["observer_role"] == "veterinarian"
    assert weight["canonical_observation"]["source"] == "VETERINARIAN"
    owner = weight["history"][1]
    assert owner["observer_role"] == "customer"
    assert owner["source"] == "USER"
    assert owner["observer_role"] != owner["source"]
    assert owner["source_session_id"] == "session-owner-1"
    assert owner["observed_at"] == "2026-09-19T12:00:00+00:00"
    assert owner["observed_at"] != owner["recorded_at"]
    for row in weight["history"]:
        for field in _PROVENANCE:
            assert field in row


def test_http_incompatible_units_have_no_delta_and_are_not_converted(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "44", unit="lb", observed_at="2026-09-05T12:00:00+00:00")
    )
    weight = _series(_report(client, dog.dog_id), "weight_kg")
    assert [(row["value"], row["unit"]) for row in weight["history"]] == [("20", "kg"), ("44", "lb")]
    assert weight["timeline"][0]["delta_from_previous"] is None
    assert weight["timeline"][1]["delta_from_previous"] is None
    assert "0.453" not in str(weight)
    assert "9.07" not in str(weight)


def test_activity_level_and_skin_appearance_have_no_numeric_delta(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "activity_level", "low", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "activity_level", "high", observed_at="2026-09-05T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "skin_appearance", "clear", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "skin_appearance", "redness", observed_at="2026-09-19T12:00:00+00:00")
    )
    payload = _report(client, dog.dog_id)
    for observation_type in ("activity_level", "skin_appearance"):
        series = _series(payload, observation_type)
        assert len(series["history"]) == 2
        assert all(point["delta_from_previous"] is None for point in series["timeline"])


def test_omitted_numeric_units_imply_comparison_without_rewriting_storage(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", observed_at="2026-09-05T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "height_cm", "50", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "height_cm", "52", observed_at="2026-09-05T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "bcs", "5", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "bcs", "6", observed_at="2026-09-19T12:00:00+00:00")
    )
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


def test_generic_event_outside_allowlist_is_absent_from_the_report(client: TestClient):
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
            "observed_at": "2026-09-01T12:00:00+00:00",
            "payload": {"observation_type": "coat_length", "observer_role": "customer"},
        },
    )
    assert created.status_code == 200
    assert created.json()["payload"]["observation_type"] == "coat_length"
    payload = _report(client, dog.dog_id)
    assert [item["observation_type"] for item in payload["series"]] == ["weight_kg"]
    filtered = _report(client, dog.dog_id, observation_type="coat_length")
    assert filtered["series"] == []


def test_as_of_canonical_is_selection_over_filtered_history(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    undated = record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg"))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    full = _report(client, dog.dog_id)
    replay = _report(client, dog.dog_id, as_of="2026-09-01T00:00:00+00:00")
    unfiltered = get_canonical_observation(dog.dog_id, "weight_kg")
    assert unfiltered is not None
    assert _series(full, "weight_kg")["canonical_observation"]["event_id"] == unfiltered.event_id
    assert _series(full, "weight_kg")["canonical_observation"]["value"] == "22"
    replay_weight = _series(replay, "weight_kg")
    assert [row["value"] for row in replay_weight["history"]] == ["20"]
    assert all(row["event_id"] != undated.event_id for row in replay_weight["history"])
    assert replay_weight["canonical_observation"]["value"] == "20"
    assert replay_weight["canonical_observation"]["observer_role"] == "customer"
    assert replay_weight["canonical_observation"]["event_id"] != unfiltered.event_id


def test_repeated_get_does_not_persist_evidence(client: TestClient):
    dog = create_dog(_dog(weight_kg=18.0, height_cm=50.0, bcs=5.0, activity_level="Moderate"))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    before_ids = [item.event_id for item in events_for(dog.dog_id)]
    before = get_dog(dog.dog_id)
    assert before is not None
    first = _report(client, dog.dog_id)
    second = _report(client, dog.dog_id)
    after = get_dog(dog.dog_id)
    assert after is not None
    assert [item.event_id for item in events_for(dog.dog_id)] == before_ids
    assert after.weight_kg == before.weight_kg == 18.0
    assert after.height_cm == before.height_cm == 50.0
    assert after.bcs == before.bcs == 5.0
    assert after.activity_level == before.activity_level == "Moderate"
    assert first["series"] == second["series"]
    assert _series(first, "weight_kg")["canonical_observation"]["value"] == "22"


def test_unknown_and_breed_derived_types_return_empty_series(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "coat_density", "dense", observed_at="2026-09-01T12:00:00+00:00")
    )
    for observation_type in ("coat_type", "not_a_physical_observation"):
        payload = _report(client, dog.dog_id, observation_type=observation_type)
        assert payload["series"] == []
    assert [item["observation_type"] for item in _report(client, dog.dog_id)["series"]] == ["coat_density"]
