"""Phase P — the two evidence serializers stay distinct, and the HTTP stamp stays metadata."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.contracts.agent.enums import ObserverRole
from app.contracts.agent.observations import Observation
from app.state.evidence import build_evidence_profile, evidence_profile_payload
from app.state.evidence_report import build_evidence_report, evidence_report_payload
from app.state.models import DogCreateRequest
from app.state.observations import record_physical_observation
from app.state.store import create_dog, events_for, get_dog


def _dog() -> DogCreateRequest:
    return DogCreateRequest.model_validate(
        {"name": "Scout", "weight_kg": 18.0, "bcs": 5.0, "activity_level": "Moderate"}
    )


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_profile_and_report_serializers_have_different_contracts():
    dog = create_dog(_dog())
    record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.CUSTOMER,
            observation_type="weight_kg",
            value="20",
            unit="kg",
            observed_at="2026-08-20T12:00:00+00:00",
        )
    )
    profile = evidence_profile_payload(build_evidence_profile(dog.dog_id))
    report = evidence_report_payload(build_evidence_report(dog.dog_id, generated_at="2026-09-20T00:00:00+00:00"))
    assert set(profile) == {"dog_id", "physical_evidence"}
    assert set(report) == {"dog_id", "generated_at", "as_of", "series"}
    assert "canonical" in profile["physical_evidence"][0]
    assert "timeline" in report["series"][0]
    assert "physical_evidence" not in report
    assert "series" not in profile


def test_generated_at_does_not_rewrite_observation_time_or_persist(client: TestClient):
    dog = create_dog(_dog())
    event = record_physical_observation(
        Observation(
            dog_id=dog.dog_id,
            observer_role=ObserverRole.VETERINARIAN,
            observation_type="weight_kg",
            value="22",
            unit="kg",
            observed_at="2026-09-19T12:00:00+00:00",
            source_session_id="session-vet-p",
        )
    )
    before_ids = [item.event_id for item in events_for(dog.dog_id)]
    response = client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={
            "generated_at": "2026-09-20T00:00:00+00:00",
            "as_of": "2026-09-19T12:00:00+00:00",
            "observation_type": "weight_kg",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"dog_id", "generated_at", "as_of", "series"}
    assert body["generated_at"] == "2026-09-20T00:00:00+00:00"
    assert body["as_of"] == "2026-09-19T12:00:00+00:00"
    row = body["series"][0]["history"][0]
    assert row["observed_at"] == event.observed_at == "2026-09-19T12:00:00+00:00"
    assert row["recorded_at"] == event.recorded_at
    assert row["observed_at"] != body["generated_at"]
    assert row["recorded_at"] != body["generated_at"]
    assert row["source_session_id"] == "session-vet-p"
    assert row["observer_role"] == "veterinarian"
    assert row["source"] == "VETERINARIAN"
    client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={"generated_at": "1999-01-01T00:00:00+00:00"},
    )
    stored = next(item for item in events_for(dog.dog_id) if item.event_id == event.event_id)
    assert [item.event_id for item in events_for(dog.dog_id)] == before_ids
    assert stored.observed_at == event.observed_at
    assert stored.recorded_at == event.recorded_at
    assert get_dog(dog.dog_id).weight_kg == 18.0


def test_unestablished_type_stays_empty_and_unknown_dog_stays_not_found(client: TestClient):
    dog = create_dog(_dog())
    empty = client.get(
        f"/api/v1/dogs/{dog.dog_id}/evidence-report",
        params={"observation_type": "coat_length"},
    )
    assert empty.status_code == 200
    assert empty.json()["series"] == []
    missing = client.get("/api/v1/dogs/missing-dog/evidence-report")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "DOG_NOT_FOUND"
    assert missing.json()["error"]["field"] == "dog_id"
