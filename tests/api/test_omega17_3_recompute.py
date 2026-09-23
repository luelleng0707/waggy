"""Ω17.3 HTTP: system-owned recalculation explanation and digest compare."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.state.version import WAGGY_RECALCULATION_EXPLANATION_SCHEMA, WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA


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


def test_recompute_returns_system_explanation_and_persists_snapshot(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    first = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert first.status_code == 200
    sig_a = first.json()["analysis_signature"]
    recomputed = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["Chicken"]}},
    )
    assert recomputed.status_code == 200
    body = recomputed.json()
    explanation = body["explanation"]
    assert explanation["schema"] == WAGGY_RECALCULATION_EXPLANATION_SCHEMA
    assert explanation["llm_used"] is False
    assert explanation["scientific"] is False
    assert explanation["science_changed"] is False
    assert explanation["previous_analysis_signature"] == sig_a
    assert explanation["new_analysis_signature"] == body["analysis_signature"]
    kinds = [item["kind"] for item in explanation["causes"]]
    assert "CATALOG_ELIGIBILITY" in kinds
    catalog = next(item for item in explanation["causes"] if item["kind"] == "CATALOG_ELIGIBILITY")
    assert "SF002" in catalog["ineligible_product_ids"]
    facts = " ".join(explanation["summary_facts"])
    assert "chicken" in facts.lower()
    assert "not a scientific finding" in facts.lower()
    history = client.get(f"/api/v1/dogs/{dog_id}/analyses").json()["analyses"]
    digest = history[-1]["result_digest"]
    assert digest["package_product_ids"]
    assert digest["recommendation_snapshot"]["schema"] == WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA
    assert digest["recalculation_explanation"]["schema"] == WAGGY_RECALCULATION_EXPLANATION_SCHEMA


def test_compare_uses_stored_digests_and_does_not_run_engine(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    import app.api.main as api_main

    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    client.post(f"/api/v1/dogs/{dog_id}/analyze")
    client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["chicken"]}},
    )
    history = client.get(f"/api/v1/dogs/{dog_id}/analyses").json()["analyses"]
    previous_id = history[0]["analysis_id"]
    new_id = history[-1]["analysis_id"]

    calls = {"n": 0}
    original = api_main.agent.generate_reproducible_report

    async def spy(profile):
        calls["n"] += 1
        return await original(profile)

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", spy)
    compared = client.get(
        f"/api/v1/dogs/{dog_id}/analyses/compare",
        params={"previous_analysis_id": previous_id, "new_analysis_id": new_id},
    )
    assert compared.status_code == 200
    payload = compared.json()
    assert payload["schema"] == "analysis_compare.v1"
    assert payload["engine_ran"] is False
    assert payload["llm_used"] is False
    assert payload["explanation"]["science_changed"] is False
    assert "CATALOG_ELIGIBILITY" in [item["kind"] for item in payload["explanation"]["causes"]]
    assert calls["n"] == 0

    latest_two = client.get(f"/api/v1/dogs/{dog_id}/analyses/compare")
    assert latest_two.status_code == 200
    assert latest_two.json()["previous_analysis_id"] == previous_id
    assert latest_two.json()["new_analysis_id"] == new_id


def test_compare_without_history_is_400(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    response = client.get(f"/api/v1/dogs/{dog_id}/analyses/compare")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "COMPARISON_UNAVAILABLE"
