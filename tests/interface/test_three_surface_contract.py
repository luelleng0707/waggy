from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    return TestClient(app)


def _dolly_payload() -> dict:
    return {
        "name": "Dolly",
        "pet_name": "Dolly",
        "breeds": ["Golden Retriever", "Labrador Retriever"],
        "birthday": "2021-03-15",
        "weight": 30,
        "sex": "Female",
        "activity_level": "High",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
    }


def test_three_surfaces_share_same_analysis_signature(client: TestClient):
    payload = _dolly_payload()
    response = client.post(
        "/api/v1/presentation/three-surfaces",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert response.status_code == 200
    body = response.json()
    sig = body.get("analysis_signature")
    assert sig
    assert body.get("customer", {}).get("surface") == "customer"
    assert body.get("business", {}).get("surface") == "business"
    assert body.get("developer", {}).get("surface") == "developer"
    assert body.get("customer", {}).get("dog", {}).get("name") == "Dolly"
    assert "overview" in (body.get("business") or {})


def test_three_surfaces_debug_payload_opt_in(client: TestClient):
    payload = _dolly_payload()
    no_debug = client.post(
        "/api/v1/presentation/three-surfaces",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    yes_debug = client.post(
        "/api/v1/presentation/three-surfaces?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert no_debug.status_code == 200
    assert yes_debug.status_code == 200
    assert (no_debug.json().get("developer") or {}).get("execution_records") == []
    records = (yes_debug.json().get("developer") or {}).get("execution_records") or []
    assert len(records) > 0
    assert all((r.get("execution_origin") in {"engine_formula_execution", "engine_trace_section"}) for r in records if isinstance(r, dict))
