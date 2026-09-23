"""Phase J — existing event API can persist owner/groomer physical observations."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.contracts.agent.enums import ObserverRole
from app.state.observations import physical_observations_for
from app.state.store import get_dog


def _profile(**overrides) -> dict:
    body = {
        "name": "Scout",
        "age_years": 4.0,
        "weight_kg": 18.0,
        "activity_level": "Moderate",
        "current_environment": "Temperate Indoor",
    }
    body.update(overrides)
    return body


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_http_owner_physical_observation_preserves_observed_at(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile(breed_input_state="UNKNOWN")).json()["dog_id"]
    created = client.post(
        f"/api/v1/dogs/{dog_id}/events",
        json={
            "event_type": "USER_STATEMENT",
            "source": "USER",
            "value": "32",
            "observed_at": "2026-09-19T12:00:00+00:00",
            "payload": {
                "observation_type": "weight_kg",
                "unit": "kg",
                "observer_role": "customer",
            },
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["observed_at"] == "2026-09-19T12:00:00+00:00"
    assert body["recorded_at"]
    assert body["observed_at"] != body["recorded_at"]
    assert body["payload"]["observation_type"] == "weight_kg"
    listed = client.get(f"/api/v1/dogs/{dog_id}/events")
    assert listed.status_code == 200
    stored = next(item for item in listed.json()["events"] if item["event_id"] == body["event_id"])
    assert stored["observed_at"] == "2026-09-19T12:00:00+00:00"
    observations = physical_observations_for(dog_id)
    assert observations[0].observer_role == ObserverRole.CUSTOMER
    assert observations[0].value == "32"
    dog = get_dog(dog_id)
    assert dog is not None
    assert dog.weight_kg == 18.0
    assert dog.breed_input_state == "UNKNOWN"


def test_http_groomer_physical_observation_does_not_overwrite_weight(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile(weight_kg=18.0)).json()["dog_id"]
    created = client.post(
        f"/api/v1/dogs/{dog_id}/events",
        json={
            "event_type": "GROOMER_OBSERVATION",
            "source": "GROOMER",
            "value": "22",
            "payload": {
                "observation_type": "weight_kg",
                "unit": "kg",
                "observer_role": "groomer",
            },
        },
    )
    assert created.status_code == 200
    assert created.json()["observed_at"] is None
    assert created.json()["recorded_at"]
    dog = client.get(f"/api/v1/dogs/{dog_id}").json()
    assert dog["weight_kg"] == 18.0


def test_http_rejects_breed_derived_trait_as_observation(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    response = client.post(
        f"/api/v1/dogs/{dog_id}/events",
        json={
            "event_type": "USER_STATEMENT",
            "source": "USER",
            "value": "Double Coat",
            "payload": {"observation_type": "coat_type", "observer_role": "customer"},
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_EVENT_PAYLOAD"
    assert response.json()["error"]["field"] == "observation_type"
