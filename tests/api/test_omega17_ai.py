"""Ω17 HTTP: explain existing canonical result; engine stays independent."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.ai.conversation import reset_conversations
from app.ai.events import reset_events


def setup_function() -> None:
    reset_conversations()
    reset_events()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def _canonical(sig: str = "sig-http") -> dict:
    return {
        "schema": "canonical_analysis.v1",
        "analysis_id": sig,
        "input": {"dog_profile": {"name": "Dolly"}},
        "scientific_analysis": {
            "findings": [],
            "nutrient_targets": [],
            "evidence": [],
            "warehouse_status": {},
        },
        "product_matching": {"recommendations": []},
        "package_optimization": {
            "algorithm": "PACKAGE_OPTIMIZER_V2_1",
            "package_options": {
                "balanced": [
                    {
                        "bundle_id": "b1",
                        "products": [{"product_id": "P1", "name": "Staple A", "why_selected": "minima"}],
                    }
                ]
            },
            "search": {"llm_used": False, "evaluated_count": 4095},
        },
        "system": {"warnings": []},
    }


def test_explain_does_not_call_engine(monkeypatch: pytest.MonkeyPatch, client: TestClient):
    import app.api.main as api_main

    def boom(*_args, **_kwargs):
        raise AssertionError("explain must not call generate_reproducible_report")

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", boom)
    response = client.post(
        "/api/v1/ai/explain",
        json={
            "analysis_signature": "sig-http",
            "canonical": _canonical(),
            "user_message": "Why would I want this package?",
            "bundle_id": "b1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "waggy_ai_response.v1"
    assert body["analysis_signature"] == "sig-http"
    assert "Staple A" in body["message"]


def test_explain_mismatch_is_400(client: TestClient):
    response = client.post(
        "/api/v1/ai/explain",
        json={
            "analysis_signature": "other",
            "canonical": _canonical("sig-http"),
            "user_message": "Why?",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ANALYSIS_MISMATCH"


def test_gemini_without_key_does_not_break_workbench(monkeypatch: pytest.MonkeyPatch, client: TestClient):
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    health = client.get("/health")
    assert health.status_code == 200
    status = client.get("/api/v1/ai/status")
    assert status.status_code == 200
    assert status.json()["available"] is False
    assert status.json()["core_analysis_requires_ai"] is False
    explained = client.post(
        "/api/v1/ai/explain",
        json={
            "analysis_signature": "sig-http",
            "canonical": _canonical(),
            "user_message": "Why?",
        },
    )
    assert explained.status_code == 200
    assert explained.json()["response_type"] == "unavailable"


def test_profile_event_groomer_observation(client: TestClient):
    created = client.post(
        "/api/v1/profile/events",
        json={
            "dog_id": "dolly",
            "source": "GROOMER",
            "kind": "observation",
            "value": "coat appears dry",
        },
    )
    assert created.status_code == 200
    assert created.json()["kind"] == "observation"
    listed = client.get("/api/v1/profile/events", params={"dog_id": "dolly"})
    assert listed.status_code == 200
    assert listed.json()["events"][0]["source"] == "GROOMER"


def test_profile_event_cannot_write_science(client: TestClient):
    response = client.post(
        "/api/v1/profile/events",
        json={
            "dog_id": "dolly",
            "source": "SCIENTIFIC",
            "kind": "observation",
            "value": "invented warehouse row",
        },
    )
    assert response.status_code == 400
