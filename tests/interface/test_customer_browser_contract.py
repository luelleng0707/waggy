from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


ROOT = Path(__file__).resolve().parents[2]


def _dolly_payload() -> dict:
    return {
        "name": "Dolly",
        "pet_name": "Dolly",
        "breeds": ["Golden Retriever", "Labrador Retriever"],
        "birthday": "2021-03-15",
        "weight": 30.1,
        "sex": "Female",
        "activity_level": "High",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
    }


def test_canonical_customer_route_serves_shell():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    assert "Personalized Wellness Analysis" in text
    assert "Load Demo Dog" in text
    assert "module-analyze" in text
    assert "page-module" in text


def test_frontend_uses_same_origin_api_not_hardcoded_ports():
    files = [
        ROOT / "legacy" / "app.js",
        ROOT / "legacy" / "catalog-service.js",
        ROOT / "legacy" / "business.js",
        ROOT / "legacy" / "ppie-validation-console.js",
        ROOT / "legacy" / "ppie-shell.js",
        ROOT / "legacy" / "workbench.js",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "127.0.0.1:8000" not in text
        assert "127.0.0.1:8010" not in text
        assert "127.0.0.1:8080" not in text
        assert "localhost:8000" not in text
        assert "localhost:8010" not in text
        assert "localhost:8080" not in text
        assert "railway.app" not in text.lower()
    catalog = (ROOT / "legacy" / "catalog-service.js").read_text(encoding="utf-8")
    app_js = (ROOT / "legacy" / "app.js").read_text(encoding="utf-8")
    assert "location.origin" in catalog
    assert "location.origin" in app_js
    assert "/api/v1/presentation/catalog" in catalog
    assert "/api/v1/clinical-report" in app_js
    workbench = (ROOT / "legacy" / "workbench.js").read_text(encoding="utf-8")
    assert "location.origin" in workbench
    assert "/api/v1/presentation/workbench" in workbench


def test_demo_profile_and_analysis_request_contract():
    app_js = (ROOT / "legacy" / "app.js").read_text(encoding="utf-8")
    assert "CANONICAL_DEMO_PROFILE" in app_js
    assert "name: 'Dolly'" in app_js
    assert "pet_name:" in app_js
    assert "loadClinicalReport" in app_js
    assert "JSON.stringify(requestBody)" in app_js
    assert "Content-Type': 'application/json'" in app_js or 'Content-Type": "application/json"' in app_js


def test_clinical_report_response_contract(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    client = TestClient(app)
    response = client.post("/api/v1/clinical-report", json=_dolly_payload())
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    body = response.json()
    analyze = body["analyze"]
    assessment = body["assessment"]
    assert "productRecommendations" in analyze
    assert "wellnessPackages" in analyze
    packages = analyze["wellnessPackages"]
    assert packages
    assert any(pkg.get("products_included") for pkg in packages)
    products = assessment["products"]
    assert "direct_items" in products
    assert "package_items" in products
    assert "source" in products
    assert products["package_items"]
    assert assessment["packages"]["tiers"]


def test_explicit_error_state_does_not_hide_http_status():
    app_js = (ROOT / "legacy" / "app.js").read_text(encoding="utf-8")
    shell = (ROOT / "legacy" / "ppie-shell.js").read_text(encoding="utf-8")
    assert "ANALYSIS UNAVAILABLE" in app_js
    assert "API returned HTTP" in app_js
    assert "formatAnalysisError" in app_js
    assert "ensure the API is running and refresh" not in app_js
    assert "wagtopia-retry-boot" in shell
    launcher = (ROOT / "scripts" / "run_dev.py").read_text(encoding="utf-8")
    assert "presentation/catalog" in launcher
    assert "stale" in launcher
    assert "CUSTOMER:" in launcher
