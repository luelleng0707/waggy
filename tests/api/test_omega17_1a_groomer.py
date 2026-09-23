"""Ω17.1a: legacy groomer routes write canonical GROOMER_OBSERVATION when a dog exists."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app

ROOT = Path(__file__).resolve().parents[2]


def _dog() -> dict:
    return {
        "name": "Dolly",
        "primary_breed": "Labrador Retriever",
        "age_years": 5.4,
        "weight_kg": 30,
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": [],
    }


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_groomer_update_without_dog_stays_transient(client: TestClient):
    mutate = client.post(
        "/api/v1/groomer/update",
        json={
            "pet_name": "Unsaved",
            "pet_id": "Unsaved",
            "observed_conditions": ["session_only_flag_must_not_leak"],
        },
    )
    assert mutate.status_code == 200
    assert mutate.json()["payload"]["canonical"] is False
    session = client.get("/api/v1/groomer/session/Unsaved")
    assert "session_only_flag_must_not_leak" in (session.json().get("observed_conditions") or [])
    listed = client.get("/api/v1/dogs/Unsaved")
    assert listed.status_code == 404


def test_groomer_update_with_saved_dog_persists_observation(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_dog()).json()["dog_id"]
    mutate = client.post(
        "/api/v1/groomer/update",
        json={
            "pet_name": "Dolly",
            "pet_id": "Dolly",
            "dog_id": dog_id,
            "observed_conditions": ["coat_dryness"],
            "notes": "coat appears dry at shoulders",
        },
    )
    assert mutate.status_code == 200
    assert mutate.json()["payload"]["canonical"] is True
    events = client.get(f"/api/v1/dogs/{dog_id}/events").json()["events"]
    types = [item["event_type"] for item in events]
    assert "GROOMER_OBSERVATION" in types
    values = [item["value"] for item in events]
    assert "coat_dryness" in values
    assert any(item.get("source") == "GROOMER" for item in events)
    dog = client.get(f"/api/v1/dogs/{dog_id}").json()
    assert "coat_dryness" in dog["observed_conditions"]
    assert "dermatological disease" not in str(events).lower()


def test_groomer_update_does_not_write_warehouse(client: TestClient):
    biology = ROOT / "warehouse" / "biology" / "breeds.csv"
    before = biology.read_bytes() if biology.is_file() else b""
    dog_id = client.post("/api/v1/dogs", json=_dog()).json()["dog_id"]
    client.post(
        "/api/v1/groomer/update",
        json={"pet_name": "Dolly", "dog_id": dog_id, "observed_conditions": ["coat_dryness"]},
    )
    after = biology.read_bytes() if biology.is_file() else b""
    assert before == after


def test_main_has_no_independent_groomer_session_dict():
    text = (ROOT / "app" / "api" / "main.py").read_text(encoding="utf-8")
    assert "_groomer_sessions" not in text
    assert "apply_groomer_update" in text


def test_unknown_dog_id_on_groomer_update_is_404(client: TestClient):
    response = client.post(
        "/api/v1/groomer/update",
        json={"pet_name": "Dolly", "dog_id": "missing-dog", "observed_conditions": ["x"]},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOG_NOT_FOUND"
