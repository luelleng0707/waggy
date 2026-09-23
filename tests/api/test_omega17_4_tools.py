"""Ω17.4 HTTP tool invoke. Application adapter only; engine stays unused."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.state.models import DogCreateRequest
from app.state.store import create_dog, save_analysis
from app.state.version import WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA
from app.tools.version import WAGGY_TOOL_RESULT_SCHEMA


def _dog() -> dict:
    return DogCreateRequest.model_validate(
        {
            "name": "Dolly",
            "primary_breed": "Labrador Retriever",
            "age_years": 5.4,
            "weight_kg": 30,
            "activity_level": "Moderate",
            "current_environment": "Temperate Outdoor",
        }
    ).model_dump(mode="json", exclude_none=True)


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_http_invoke_does_not_call_engine(monkeypatch: pytest.MonkeyPatch, client: TestClient):
    import app.api.main as api_main

    dog = create_dog(DogCreateRequest.model_validate(_dog()))

    def boom(*_args, **_kwargs):
        raise AssertionError("tool invoke must not call generate_reproducible_report")

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", boom)
    response = client.post(
        "/api/v1/ai/tools/invoke",
        json={"tool": "get_dog_profile", "arguments": {"dog_id": dog.dog_id}, "request_id": "req-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == WAGGY_TOOL_RESULT_SCHEMA
    assert body["status"] == "ok"
    assert body["scientific"] is False
    assert body["llm_used"] is False
    assert body["request"]["request_id"] == "req-1"
    assert body["data"]["dog"]["name"] == "Dolly"
    assert body["data"]["engine_ran"] is False


def test_http_unknown_and_forbidden_tools(client: TestClient):
    unknown = client.post("/api/v1/ai/tools/invoke", json={"tool": "run_sql", "arguments": {}})
    assert unknown.status_code == 403
    assert unknown.json()["errors"][0]["code"] == "TOOL_NOT_ALLOWED"
    missing = client.post("/api/v1/ai/tools/invoke", json={"tool": "invent_science", "arguments": {}})
    assert missing.status_code == 400
    assert missing.json()["errors"][0]["code"] == "UNKNOWN_TOOL"


def test_http_health_slice_from_stored_digest(monkeypatch: pytest.MonkeyPatch, client: TestClient):
    import app.api.main as api_main

    dog = create_dog(DogCreateRequest.model_validate(_dog()))
    save_analysis(
        dog_id=dog.dog_id,
        analysis_signature="sig-http",
        engine_version="2.1.0",
        warehouse_version="test",
        input_snapshot={},
        result_digest={
            "finding_titles": ["Joints"],
            "package_product_ids": {"balanced": ["SF001"]},
            "recommendation_snapshot": {
                "schema": WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA,
                "scientific": False,
                "science": {"finding_titles": ["Joints"], "nutrients": [{"nutrient": "protein", "min": 1, "max": 2}]},
                "recommendations": {
                    "balanced": {
                        "bundle_id": "b1",
                        "product_ids": ["SF001"],
                        "product_names": ["Beef"],
                        "monthly_cost": 80,
                    }
                },
            },
        },
    )

    def boom(*_args, **_kwargs):
        raise AssertionError("analyze_health HTTP must not call the engine")

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", boom)
    response = client.post(
        "/api/v1/ai/tools/invoke",
        json={"tool": "analyze_health", "arguments": {"dog_id": dog.dog_id}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["findings"][0]["title"] == "Joints"
    assert body["data"]["engine_ran"] is False


def test_http_propose_preference_does_not_mutate(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_dog()).json()["dog_id"]
    response = client.post(
        "/api/v1/ai/tools/invoke",
        json={
            "tool": "propose_preference",
            "arguments": {"type": "ingredient_exclusion", "value": "chicken", "dog_id": dog_id},
        },
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["persisted"] is False
    assert body["requires_authorized_mutation"] is True
    prefs = client.get(f"/api/v1/dogs/{dog_id}/preferences").json()["preferences"]
    assert prefs == []
    missing = client.post(
        "/api/v1/ai/tools/invoke",
        json={"tool": "set_preferences", "arguments": {"dog_id": dog_id}},
    )
    assert missing.status_code == 403
