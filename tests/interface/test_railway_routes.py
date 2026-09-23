from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    return TestClient(app)


def test_three_surface_routes_and_health(client: TestClient):
    assert client.get("/").status_code == 200
    assert client.get("/business").status_code == 200
    assert client.get("/developer").status_code == 200
    assert client.get("/health").status_code == 200


def test_openapi_contains_core_routes(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json().get("paths", {})
    assert "/api/v1/analyze" in paths
    assert "/api/v1/presentation/three-surfaces" in paths
    assert "/business" in paths
    assert "/developer" in paths


def test_surface_access_keys_when_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.setenv("WAGTOPIA_BUSINESS_ACCESS_KEY", "biz-key")
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    client = TestClient(app)

    assert client.get("/business").status_code == 200
    assert client.get("/business?access_key=biz-key").status_code == 200

    assert client.get("/developer").status_code == 200
    assert client.get("/debug/calculation").status_code == 401
    assert client.get("/debug/calculation?access_key=dev-key").status_code == 200
