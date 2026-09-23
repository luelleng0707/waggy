from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.presentation.adapter import (
    NA,
    build_business_presentation,
    build_customer_presentation,
    project_package_composition,
)


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


def _runtime_package_with_products() -> dict:
    return {
        "tier": "balanced",
        "package_id": "balanced",
        "title": "Balanced Care",
        "recommended": True,
        "best_for": "Fill nutrient targets",
        "monthly_cost": 120,
        "yearly_cost": 1324.8,
        "yearly_discount_factor": 0.92,
        "coverage_score": 88,
        "products_included": [
            {
                "product_id": "SF001",
                "name": "Fresh Beef Bowl",
                "brand": "Wagtopia",
                "category": "Fresh Food",
                "monthly_cost": 80,
                "yearly_cost": 960,
                "price": 88,
                "serving_size": "220g/day",
                "daily_amount": "220g/day",
                "monthly_quantity": "12 packs/year",
                "why_selected": "Selected as staple",
                "yearly_plan": {"daily_serving": "220 g", "packages_needed": 12},
            },
            {
                "product_id": "TR011",
                "name": "Joint Chew",
                "brand": "Wagtopia",
                "category": "Treat",
                "monthly_cost": 40,
                "yearly_cost": 480,
                "price": 45,
                "serving_size": "1 chew/day",
                "why_selected": "Joint support",
            },
        ],
    }


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_runtime_package_output_preserves_product_composition_when_present(client: TestClient):
    response = client.post("/api/v1/clinical-report", json=_dolly_payload())
    assert response.status_code == 200
    analyze = response.json()["analyze"]
    packages = analyze.get("wellnessPackages") or []
    assert packages, "runtime must emit wellnessPackages"
    for pkg in packages:
        products = pkg.get("products_included") or pkg.get("product_cards") or []
        if products:
            assert any(item.get("product_id") or item.get("name") or item.get("product_name") for item in products)
        else:
            # Current warehouse product catalog is empty; do not treat empty shells as composition.
            assert products == []


def test_adapter_does_not_discard_package_products():
    analyze = {
        "profile": {"pet_name": "Dolly", "breeds": ["Labrador Retriever"], "weight_kg": 30},
        "productRecommendations": [
            {
                "product_id": "SF001",
                "product_name": "Fresh Beef Bowl",
                "brand": "Wagtopia",
                "category": "Fresh Food",
                "price": 88,
                "why_selected": "Staple match",
            }
        ],
        "wellnessPackages": [_runtime_package_with_products()],
        "healthInsights": [],
        "scientificEvidence": [],
    }
    customer = build_customer_presentation(analyze, None)
    business = build_business_presentation(analyze, None)
    for pkg in customer["wellness"]["package_composition"] + business["portfolio"]["package_composition"]:
        assert pkg["composition_status"] == "AVAILABLE"
        names = [item["name"] for item in pkg["products"]]
        assert "Fresh Beef Bowl" in names
        assert "Joint Chew" in names
        assert pkg["products"][0]["product_id"] == "SF001"
        assert pkg["monthly_cost"] == 120


def test_customer_package_presentation_renders_package_products():
    root = Path(__file__).resolve().parents[2]
    shell = (root / "legacy" / "archive" / "frontend" / "ppie-shell.js").read_text(encoding="utf-8")
    ui = (root / "legacy" / "archive" / "frontend" / "ppie-ui.js").read_text(encoding="utf-8")
    assert "Recommended products" in shell
    assert "Care packages" in shell
    assert "pkg.products" in ui
    assert "NOT AVAILABLE FROM RUNTIME" in ui
    assert "Products included" in shell


def test_business_package_presentation_renders_package_products():
    root = Path(__file__).resolve().parents[2]
    html = (root / "legacy" / "archive" / "frontend" / "business.html").read_text(encoding="utf-8")
    js = (root / "legacy" / "archive" / "frontend" / "business.js").read_text(encoding="utf-8")
    assert "CARE PACKAGE OPPORTUNITIES" in html
    assert "package_composition" in js
    assert "NOT AVAILABLE FROM RUNTIME" in js


def test_missing_package_composition_is_explicitly_unavailable():
    projected = project_package_composition({"tier": "essential", "title": "Empty Care"})
    assert projected["composition_status"] == NA
    assert projected["products"] == []
    assert projected["monthly_cost"] == NA
    live = build_customer_presentation(
        {"wellnessPackages": [{"tier": "essential", "title": "Empty Care"}], "productRecommendations": []},
        None,
    )
    pkg = live["wellness"]["package_composition"][0]
    assert pkg["composition_status"] == NA
    assert pkg["products"] == []
    blob = str(pkg)
    assert "Fresh Beef Bowl" not in blob
    assert "demo-product" not in blob.lower()
