from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    return TestClient(app)


def test_developer_route_serves_developer_ui(client: TestClient):
    response = client.get("/developer")
    assert response.status_code == 200
    assert "workbench.js" in response.text
    assert 'data-role="developer"' in response.text
    assert "Clinical Execution Explorer" not in response.text


def test_developer_surface_read_only_contract(client: TestClient):
    response = client.get("/debug/calculation")
    assert response.status_code == 200
    text = response.text
    assert "Clinical Execution Explorer" in text
    assert "Run assessment" in text
    assert "<form" not in text


def test_developer_debug_api_requires_optional_access_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    client = TestClient(app)
    payload = {
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
    blocked = client.post(
        "/api/v1/ppie/validation-console?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert blocked.status_code == 401
    allowed = client.post(
        "/api/v1/ppie/validation-console?debug=1&access_key=dev-key",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert allowed.status_code == 200
