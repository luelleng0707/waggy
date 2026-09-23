from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from fastapi.testclient import TestClient
from pathlib import Path
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


def test_surface_backing_apis_work_without_x_api_key_when_api_keys_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(api_main, "VALID_KEYS", {"locked-key"})
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    client = TestClient(app)

    clinical = client.post("/api/v1/clinical-report", json=_dolly_payload())
    assert clinical.status_code == 200

    surfaces = client.post("/api/v1/presentation/three-surfaces?debug=1", json=_dolly_payload())
    assert surfaces.status_code == 200
    body = surfaces.json()
    assert body.get("customer", {}).get("surface") == "customer"
    assert body.get("business", {}).get("surface") == "business"
    assert body.get("developer", {}).get("surface") == "developer"

    debug_console = client.post("/api/v1/ppie/validation-console?debug=1", json=_dolly_payload())
    assert debug_console.status_code == 200


def test_non_surface_api_still_respects_x_api_key_gate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(api_main, "VALID_KEYS", {"locked-key"})
    client = TestClient(app)
    assert client.get("/api/v1/presentation/catalog").status_code == 200
    assert client.get("/api/v1/store").status_code == 200
    assert client.post("/api/v1/analyze", json=_dolly_payload()).status_code == 401
    assert client.post("/api/v1/ppie/assess", json=_dolly_payload()).status_code == 401
    assert client.post(
        "/api/v1/analyze",
        headers={"x-api-key": "locked-key"},
        json=_dolly_payload(),
    ).status_code == 200


def test_frontend_contains_no_embedded_secrets_or_localhost_api_urls():
    root = Path(__file__).resolve().parents[2]
    files = [
        root / "legacy" / "archive" / "frontend" / "app.js",
        root / "legacy" / "archive" / "frontend" / "business.js",
        root / "legacy" / "archive" / "frontend" / "catalog-service.js",
        root / "legacy" / "ppie-validation-console.js",
        WORKBENCH_JS,
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "wagtopia-demo-key" not in text
        assert "127.0.0.1:8000" not in text
        assert "localhost:8000" not in text
        assert "http://127.0.0.1" not in text
        assert "http://localhost" not in text


def test_customer_boot_failure_has_explicit_ui_states():
    root = Path(__file__).resolve().parents[2]
    text = (root / "legacy" / "archive" / "frontend" / "app.js").read_text(encoding="utf-8")
    assert "showBootState('loading')" in text
    assert "authentication/configuration failure" in text
    assert "network failure" in text
    assert "Retry the analysis when the service is available." in text


def test_business_surface_and_presentation_api_respect_business_gate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WAGTOPIA_BUSINESS_ACCESS_KEY", "biz-key")
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    client = TestClient(app)
    assert client.get("/business").status_code == 200
    blocked = client.post("/api/v1/presentation/three-surfaces", json=_dolly_payload())
    assert blocked.status_code == 401

    allowed_surface = client.get("/business")
    assert allowed_surface.status_code == 200
    assert "workbench.js" in allowed_surface.text
    allowed = client.post(
        "/api/v1/presentation/three-surfaces",
        headers={"x-wagtopia-access-key": "biz-key"},
        json=_dolly_payload(),
    )
    assert allowed.status_code == 200


def test_developer_surface_and_debug_endpoints_respect_developer_gate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    client = TestClient(app)
    assert client.get("/developer").status_code == 200
    blocked = client.post("/api/v1/ppie/validation-console?debug=1", json=_dolly_payload())
    assert blocked.status_code == 401

    allowed_surface = client.get("/debug/calculation", headers={"x-wagtopia-access-key": "dev-key"})
    assert allowed_surface.status_code == 200
    assert "Clinical Execution Explorer" in allowed_surface.text
    allowed = client.post(
        "/api/v1/ppie/validation-console?debug=1",
        headers={"x-wagtopia-access-key": "dev-key"},
        json=_dolly_payload(),
    )
    assert allowed.status_code == 200


def test_debug_internal_endpoints_still_require_debug_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PPIE_DEBUG", "false")
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    monkeypatch.delenv("API_KEYS", raising=False)
    client = TestClient(app)

    response = client.post(
        "/api/v1/ppie/validation-console?debug=0",
        headers={"x-wagtopia-access-key": "dev-key"},
        json=_dolly_payload(),
    )
    assert response.status_code == 403
