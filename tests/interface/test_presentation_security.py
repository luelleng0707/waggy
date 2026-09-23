from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


def _dolly() -> dict:
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


def test_customer_route_stays_public_when_surface_keys_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.setenv("WAGTOPIA_BUSINESS_ACCESS_KEY", "biz-key")
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    client = TestClient(app)
    assert client.get("/").status_code == 200


def test_business_and_developer_debug_console_requires_access_key_when_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.setenv("WAGTOPIA_BUSINESS_ACCESS_KEY", "biz-key")
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    client = TestClient(app)

    assert client.get("/business").status_code == 200
    assert client.get("/developer").status_code == 200
    assert client.get("/debug/calculation").status_code == 401
    assert client.get("/debug/calculation", headers={"x-wagtopia-access-key": "dev-key"}).status_code == 200


def test_three_surface_api_requires_business_key_when_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.setenv("WAGTOPIA_BUSINESS_ACCESS_KEY", "biz-key")
    monkeypatch.delenv("API_KEYS", raising=False)
    client = TestClient(app)

    blocked = client.post("/api/v1/presentation/three-surfaces", json=_dolly())
    assert blocked.status_code == 401

    allowed = client.post(
        "/api/v1/presentation/three-surfaces",
        headers={"x-wagtopia-access-key": "biz-key"},
        json=_dolly(),
    )
    assert allowed.status_code == 200


def test_presentation_pages_do_not_embed_query_credentials(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    client = TestClient(app)

    for route in ("/", "/business", "/developer"):
        response = client.get(route)
        assert response.status_code == 200
        assert "access_key=" not in response.text
