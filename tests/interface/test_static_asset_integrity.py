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


def test_core_static_surfaces_and_assets_load(client: TestClient):
    routes = [
        "/",
        "/business",
        "/developer",
        "/app.js",
        "/styles.css",
        "/business.js",
        "/business.css",
        "/ppie-validation-console.js",
        "/ppie-validation-console.css",
        "/favicon.ico",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"{route} returned {response.status_code}"


def test_production_surface_html_has_no_localhost_or_demo_secret(client: TestClient):
    for route in ("/", "/business", "/developer"):
        text = client.get(route).text
        assert "127.0.0.1" not in text
        assert "localhost" not in text
        assert "file://" not in text
        assert "wagtopia-demo-key" not in text
