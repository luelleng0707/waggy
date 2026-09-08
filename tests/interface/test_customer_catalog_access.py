from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

import app.api.main as api_main
from app.api.main import app


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


def test_customer_page_loads():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Personalized Wellness Analysis" in response.text
    assert "workbench.js" in response.text
    classic = client.get("/classic")
    assert classic.status_code == 200
    assert "catalog-service.js" in classic.text


def test_customer_catalog_boot_succeeds_without_frontend_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(api_main, "VALID_KEYS", {"locked-key"})
    client = TestClient(app)
    catalog = client.get("/api/v1/presentation/catalog?weight_kg=30.1")
    assert catalog.status_code == 200
    body = catalog.json()
    assert isinstance(body.get("products"), list)
    store = client.get("/api/v1/store?weight_kg=30.1")
    assert store.status_code == 200
    assert store.json().get("count") == body.get("count")


def test_no_secret_appears_in_frontend_assets():
    root = Path(__file__).resolve().parents[2]
    files = [
        root / "legacy" / "app.js",
        root / "legacy" / "catalog-service.js",
        root / "legacy" / "business.js",
        root / "legacy" / "ppie-shell.js",
        root / "legacy" / "ppie-ui.js",
        root / "legacy" / "index.html",
        root / "legacy" / "workbench.js",
        root / "legacy" / "workbench.html",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "wagtopia-demo-key" not in text
        assert "WAGTOPIA_BUSINESS_ACCESS_KEY" not in text
        assert "WAGTOPIA_DEVELOPER_ACCESS_KEY" not in text
        assert "127.0.0.1:8000" not in text
        assert "localhost:8000" not in text


def test_protected_mutation_endpoint_remains_protected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(api_main, "VALID_KEYS", {"locked-key"})
    client = TestClient(app)
    blocked = client.post("/api/v1/analyze", json=_dolly_payload())
    assert blocked.status_code == 401
    allowed = client.post(
        "/api/v1/analyze",
        headers={"x-api-key": "locked-key"},
        json=_dolly_payload(),
    )
    assert allowed.status_code == 200


def test_catalog_service_uses_presentation_catalog_endpoint():
    root = Path(__file__).resolve().parents[2]
    text = (root / "legacy" / "catalog-service.js").read_text(encoding="utf-8")
    assert "/api/v1/presentation/catalog" in text
    assert "x-api-key" not in text or "if (API_KEY)" in text
    assert "wagtopia-demo-key" not in text
