from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_canonical_presentation_routes_are_available(client: TestClient):
    for route in ("/", "/demo", "/classic", "/business", "/developer"):
        response = client.get(route)
        assert response.status_code == 200, route
        assert "workbench.js" in response.text
        assert "role-selector" in response.text


def test_debug_calculation_route_remains_compatibility_endpoint(client: TestClient):
    response = client.get("/debug/calculation")
    assert response.status_code == 200
    assert "Clinical Execution Explorer" in response.text


def test_openapi_includes_canonical_and_compatibility_routes(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})
    assert "/" in paths
    assert "/demo" in paths
    assert "/classic" in paths
    assert "/business" in paths
    assert "/developer" in paths
    assert "/debug/calculation" in paths
    assert "/api/v1/presentation/workbench" in paths
