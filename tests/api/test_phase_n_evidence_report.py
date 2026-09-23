"""Phase N — read-only evidence report HTTP boundary over Phase M."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.contracts.agent.enums import ObserverRole
from app.contracts.agent.observations import Observation
from app.state.observations import record_physical_observation
from app.state.store import create_dog, events_for, get_dog
from app.state.models import DogCreateRequest


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


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_endpoint_returns_traceable_report_with_canonical_timeline_and_delta(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg", observed_at="2026-09-05T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(
            dog.dog_id,
            ObserverRole.VETERINARIAN,
            "weight_kg",
            "22",
            unit="kg",
            observed_at="2026-09-19T12:00:00+00:00",
            source_session_id="session-vet-1",
        )
    )
    before = [item.event_id for item in events_for(dog.dog_id)]
    response = client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={"generated_at": "2026-09-20T00:00:00+00:00"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["dog_id"] == dog.dog_id
    assert body["generated_at"] == "2026-09-20T00:00:00+00:00"
    assert body["as_of"] is None
    series = body["series"]
    weight = next(item for item in series if item["observation_type"] == "weight_kg")
    assert [row["value"] for row in weight["history"]] == ["20", "21", "22"]
    assert [row["observer_role"] for row in weight["history"]] == ["customer", "groomer", "veterinarian"]
    assert [row["source"] for row in weight["history"]] == ["USER", "GROOMER", "VETERINARIAN"]
    for row in weight["history"]:
        assert row["observation_id"]
        assert row["dog_id"] == dog.dog_id
        assert row["event_id"]
        assert row["observed_at"]
        assert row["recorded_at"]
        assert row["observed_at"] != row["recorded_at"]
        assert row["unit"] == "kg"
    assert weight["canonical_observation"]["value"] == "22"
    assert weight["canonical_observation"]["observer_role"] == "veterinarian"
    assert weight["canonical_observation"]["source"] == "VETERINARIAN"
    assert weight["timeline"][0]["delta_from_previous"] is None
    assert weight["timeline"][1]["delta_from_previous"]["delta"] == 1.0
    assert weight["timeline"][1]["observation"]["event_id"] == weight["history"][1]["event_id"]
    vet = weight["history"][2]
    assert vet["source_session_id"] == "session-vet-1"
    again = client.get(f"/api/v1/dogs/{dog.dog_id}/evidence-report")
    assert again.status_code == 200
    assert [item.event_id for item in events_for(dog.dog_id)] == before
    assert get_dog(dog.dog_id).weight_kg == 18.0


def test_categorical_observations_have_no_numeric_delta(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "coat_density", "sparse", observed_at="2026-08-20T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.GROOMER, "coat_density", "dense", observed_at="2026-09-05T12:00:00+00:00")
    )
    body = client.get(f"/api/v1/dogs/{dog.dog_id}/evidence-report").json()
    series = next(item for item in body["series"] if item["observation_type"] == "coat_density")
    assert all(point["delta_from_previous"] is None for point in series["timeline"])


def test_observation_type_and_as_of_are_passed_through(client: TestClient):
    dog = create_dog(_dog())
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "weight_kg", "20", unit="kg", observed_at="2026-08-20T12:00:00+00:00")
    )
    undated = record_physical_observation(_obs(dog.dog_id, ObserverRole.GROOMER, "weight_kg", "21", unit="kg"))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.VETERINARIAN, "weight_kg", "22", unit="kg", observed_at="2026-09-19T12:00:00+00:00")
    )
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "bcs", "5", observed_at="2026-08-20T12:00:00+00:00")
    )
    filtered = client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={"observation_type": "bcs"},
    ).json()
    assert [item["observation_type"] for item in filtered["series"]] == ["bcs"]
    replay = client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={"observation_type": "weight_kg", "as_of": "2026-09-01T00:00:00+00:00"},
    ).json()
    assert replay["as_of"] == "2026-09-01T00:00:00+00:00"
    weight = replay["series"][0]
    assert [row["value"] for row in weight["history"]] == ["20"]
    assert all(row["event_id"] != undated.event_id for row in weight["history"])
    assert all(row["observed_at"] is not None for row in weight["history"])
    assert all(row["observed_at"] != row["recorded_at"] for row in weight["history"])


def test_unknown_dog_uses_existing_not_found_error(client: TestClient):
    response = client.get("/api/v1/dogs/missing-dog/evidence-report")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOG_NOT_FOUND"
    assert response.json()["error"]["field"] == "dog_id"


def test_unknown_breed_report_excludes_breed_derived_traits(client: TestClient):
    dog = create_dog(_dog(breed_input_state="UNKNOWN", primary_breed=None, weight_kg=None))
    record_physical_observation(
        _obs(dog.dog_id, ObserverRole.CUSTOMER, "height_cm", "55", unit="cm", observed_at="2026-09-01T12:00:00+00:00")
    )
    body = client.get(f"/api/v1/dogs/{dog.dog_id}/evidence-report").json()
    assert body["dog_id"] == dog.dog_id
    assert [item["observation_type"] for item in body["series"]] == ["height_cm"]
    excluded = client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={"observation_type": "coat_type"},
    )
    assert excluded.status_code == 200
    assert excluded.json()["series"] == []
    stored = get_dog(dog.dog_id)
    assert stored is not None
    assert stored.primary_breed is None
    assert stored.breed_input_state == "UNKNOWN"
