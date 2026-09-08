from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.data.demo_catalog import demo_product_ids
from app.presentation.adapter import build_three_surface_presentations


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


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_dolly_gets_demo_catalog_candidates(demo_client: TestClient):
    catalog = demo_client.get("/api/v1/presentation/catalog?weight_kg=30.1").json()
    assert catalog.get("demo_catalog") is True
    assert catalog.get("count") >= 8
    ids = {str(row.get("product_id")) for row in catalog.get("products") or []}
    assert ids == demo_product_ids()


def test_dolly_packages_include_demo_catalog_products(demo_client: TestClient):
    response = demo_client.post("/api/v1/clinical-report", json=_dolly_payload())
    assert response.status_code == 200
    analyze = response.json()["analyze"]
    recs = analyze.get("productRecommendations") or []
    packages = analyze.get("wellnessPackages") or []
    assert packages, "PACKAGE_OPTIMIZER_V2_1 must still emit wellnessPackages"

    composed = [
        pkg
        for pkg in packages
        if isinstance(pkg, dict) and (pkg.get("products_included") or pkg.get("product_cards"))
    ]
    assert composed, "at least one package must include products_included from the optimizer"

    catalog_ids = demo_product_ids()
    selected: set[str] = set()
    for pkg in composed:
        rows = pkg.get("products_included") or pkg.get("product_cards") or []
        assert isinstance(pkg.get("monthly_cost"), (int, float))
        assert isinstance(pkg.get("yearly_cost"), (int, float))
        assert pkg.get("yearly_discount_factor") is not None
        for item in rows:
            pid = str(item.get("product_id") or "")
            assert pid in catalog_ids
            selected.add(pid)
            assert item.get("name") or item.get("product_name")
            assert item.get("monthly_cost") is not None or item.get("price") is not None
    assert selected, "package products must correspond to demo catalog IDs"

    assessment = response.json()["assessment"]
    product_items = ((assessment.get("products") or {}).get("items")) or []
    if not recs:
        assert product_items, "customer recommended products fall back to optimizer composition, not frontend invention"
        rec_ids = {str(item.get("product_id")) for item in product_items if item.get("product_id")}
        assert rec_ids <= catalog_ids
    else:
        rec_ids = {str(item.get("product_id")) for item in recs if item.get("product_id")}
        assert rec_ids <= catalog_ids


def test_three_surfaces_share_one_demo_analysis(demo_client: TestClient):
    response = demo_client.post("/api/v1/presentation/three-surfaces", json=_dolly_payload())
    assert response.status_code == 200
    body = response.json()
    assert body.get("demo_catalog") is True
    assert body.get("presentation_correlation_id")
    assert body.get("analysis_signature")
    customer = body["customer"]
    business = body["business"]
    developer = body["developer"]
    customer_pkgs = customer["wellness"]["package_composition"]
    business_pkgs = business["portfolio"]["package_composition"]
    assert customer_pkgs
    assert len(customer_pkgs) == len(business_pkgs)
    assert any(pkg.get("products") for pkg in customer_pkgs)
    assert any(pkg.get("products") for pkg in business_pkgs)
    assert developer.get("pipeline")
    assert "PRODUCT_MATCH_V2_1" in developer["pipeline"]
    assert "PACKAGE_OPTIMIZER_V2_1" in developer["pipeline"]
    assert developer["catalog_input"]["source"] == "demo"


def test_no_frontend_hardcoded_package_contents():
    frontend = [
        ROOT / "legacy" / "app.js",
        ROOT / "legacy" / "ppie-shell.js",
        ROOT / "legacy" / "ppie-ui.js",
        ROOT / "legacy" / "business.js",
        ROOT / "legacy" / "index.html",
        ROOT / "legacy" / "business.html",
        ROOT / "legacy" / "workbench.html",
        ROOT / "legacy" / "workbench.js",
    ]
    for path in frontend:
        text = path.read_text(encoding="utf-8")
        assert "if demo" not in text.lower() or "demo_catalog" in text
        assert "Demo Fresh Beef Bowl" not in text
        assert "products_included = [" not in text
        assert '"SF001"' not in text
        assert "SF001" not in text


def test_adapter_does_not_invent_demo_packages():
    analyze = {
        "profile": {"pet_name": "Dolly", "breeds": ["Labrador Retriever"], "weight_kg": 30.1},
        "productRecommendations": [],
        "wellnessPackages": [
            {"tier": "essential", "title": "Essential Care", "products_included": []}
        ],
    }
    payload = build_three_surface_presentations(analyze, None, None, "corr-test")
    pkg = payload["customer"]["wellness"]["package_composition"][0]
    assert pkg["products"] == []
    assert pkg["composition_status"] == "NOT AVAILABLE FROM RUNTIME"
    blob = str(payload)
    assert "Demo Fresh Beef Bowl" not in blob
