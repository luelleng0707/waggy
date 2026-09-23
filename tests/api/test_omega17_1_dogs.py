"""Ω17.1 HTTP: persistent dogs, events, preferences, analysis history."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.api.http_models import WORKBENCH_EXAMPLE_REQUEST


def _profile(**overrides) -> dict:
    body = {
        "name": "Dolly",
        "primary_breed": "Labrador Retriever",
        "secondary_breed": "Golden Retriever",
        "age_years": 5.4,
        "weight_kg": 30,
        "sex": "Female",
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": ["joint_stiffness"],
        "monthly_budget": 120,
    }
    body.update(overrides)
    return body


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_create_and_get_dog_does_not_run_engine(monkeypatch: pytest.MonkeyPatch, client: TestClient):
    import app.api.main as api_main

    def boom(*_args, **_kwargs):
        raise AssertionError("GET/POST dog must not call generate_reproducible_report")

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", boom)
    created = client.post("/api/v1/dogs", json=_profile())
    assert created.status_code == 200
    dog_id = created.json()["dog_id"]
    loaded = client.get(f"/api/v1/dogs/{dog_id}")
    assert loaded.status_code == 200
    assert loaded.json()["name"] == "Dolly"
    events = client.get(f"/api/v1/dogs/{dog_id}/events")
    assert events.status_code == 200
    missing = client.get("/api/v1/dogs/does-not-exist")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "DOG_NOT_FOUND"


def test_groomer_event_and_scientific_forbidden(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    created = client.post(
        f"/api/v1/dogs/{dog_id}/events",
        json={
            "event_type": "GROOMER_OBSERVATION",
            "source": "GROOMER",
            "payload": {"observation": "coat appears dry", "category": "coat", "severity": "mild"},
        },
    )
    assert created.status_code == 200
    assert created.json()["event_type"] == "GROOMER_OBSERVATION"
    forbidden = client.post(
        f"/api/v1/dogs/{dog_id}/events",
        json={"event_type": "SCIENTIFIC_FACT", "source": "USER", "payload": {"prevalence": 99}},
    )
    assert forbidden.status_code == 400
    assert forbidden.json()["error"]["code"] == "SCIENTIFIC_EVENT_FORBIDDEN"
    analysis_event = client.post(
        f"/api/v1/dogs/{dog_id}/events",
        json={"event_type": "ANALYSIS_RUN", "source": "SYSTEM", "payload": {}},
    )
    assert analysis_event.status_code == 400


def test_explicit_and_ambiguous_preferences(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    ok = client.post(
        f"/api/v1/dogs/{dog_id}/preferences",
        json={"category": "ingredient_exclusion", "value": "chicken", "status": "EXPLICIT"},
    )
    assert ok.status_code == 200
    listed = client.get(f"/api/v1/dogs/{dog_id}/preferences")
    assert listed.json()["preferences"][0]["value"] == "chicken"
    vague = client.post(
        f"/api/v1/dogs/{dog_id}/preferences",
        json={"category": "budget", "value": "That's expensive.", "status": "EXPLICIT"},
    )
    assert vague.status_code == 400
    assert vague.json()["error"]["code"] == "AMBIGUOUS_PREFERENCE"


def test_explain_durable_budget_persists_but_does_not_edit_package(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    canonical = {
        "schema": "canonical_analysis.v1",
        "analysis_id": "sig-persist",
        "input": {"dog_profile": {"name": "Dolly"}},
        "scientific_analysis": {"findings": [], "nutrient_targets": [], "evidence": [], "warehouse_status": {}},
        "product_matching": {"recommendations": []},
        "package_optimization": {
            "algorithm": "PACKAGE_OPTIMIZER_V2_1",
            "package_options": {
                "balanced": [{"bundle_id": "b1", "products": [{"product_id": "P1", "name": "Staple A"}]}]
            },
            "search": {"llm_used": False},
        },
        "system": {"warnings": []},
    }
    explained = client.post(
        "/api/v1/ai/explain",
        json={
            "analysis_signature": "sig-persist",
            "canonical": canonical,
            "user_message": "Keep it under 80",
            "dog_id": dog_id,
            "bundle_id": "b1",
        },
    )
    assert explained.status_code == 200
    body = explained.json()
    assert body["requested_recomputation"] is True
    assert "P1" in str(canonical)
    prefs = client.get(f"/api/v1/dogs/{dog_id}/preferences").json()["preferences"]
    assert any(item["category"] == "budget" and float(item["value"]) == 80.0 for item in prefs)
    loaded = client.get(f"/api/v1/dogs/{dog_id}").json()
    assert loaded["monthly_budget"] == 80.0


def test_analyze_from_dog_and_signature_changes_with_input(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile(birthday=None)).json()["dog_id"]
    first = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert first.status_code == 200
    sig_a = first.json()["analysis_signature"]
    second = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert second.status_code == 200
    assert second.json()["analysis_signature"] == sig_a
    client.patch(f"/api/v1/dogs/{dog_id}", json={"weight_kg": 24.5, "confirmed": True})
    third = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert third.status_code == 200
    assert third.json()["analysis_signature"] != sig_a
    history = client.get(f"/api/v1/dogs/{dog_id}/analyses").json()["analyses"]
    assert len(history) == 3
    assert history[0]["analysis_signature"] == sig_a


def test_workbench_without_dog_id_stays_transient(client: TestClient):
    payload = dict(WORKBENCH_EXAMPLE_REQUEST)
    payload["age_years"] = 5.4
    payload.pop("birthday", None)
    response = client.post("/api/v1/presentation/workbench", json=payload)
    assert response.status_code == 200
    listed = client.get("/api/v1/dogs/missing")
    assert listed.status_code == 404


def test_incomplete_dog_analyze_fail_closed(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json={"name": "NoFacts"}).json()["dog_id"]
    response = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "MISSING_REQUIRED_PROFILE_INPUT"


def test_gemini_unavailable_does_not_break_dog_state(monkeypatch: pytest.MonkeyPatch, client: TestClient):
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    created = client.post("/api/v1/dogs", json=_profile())
    assert created.status_code == 200
    health = client.get("/health")
    assert health.status_code == 200
    assert "GEMINI_API_KEY" not in created.text
    assert "GOOGLE_API_KEY" not in created.text
