from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from app.core.paths import clinical_root_str
from app.data.clinical_assessment import build_clinical_assessment
from app.data.repository import DataRepository


ROOT = Path(__file__).resolve().parents[2]


def test_package_products_render_even_when_matcher_recommendations_are_empty():
    analyze = {
        "profile": {
            "pet_name": "Dolly",
            "name": "Dolly",
            "breeds": ["Labrador Retriever", "Golden Retriever"],
            "weight_kg": 30.1,
            "activity_level": "High",
        },
        "productRecommendations": [],
        "wellnessPackages": [
            {
                "tier": "balanced",
                "title": "Balanced Care",
                "recommended": True,
                "monthly_cost": 823,
                "yearly_cost": 9874,
                "yearly_discount_factor": 0.92,
                "products_included": [
                    {
                        "product_id": "SF001",
                        "name": "Demo Fresh Beef Bowl",
                        "brand": "Wagtopia Demo",
                        "monthly_cost": 742,
                        "yearly_cost": 8904,
                        "price": 168,
                    },
                    {
                        "product_id": "TR011",
                        "name": "Demo Joint Mobility Chew",
                        "brand": "Wagtopia Demo",
                        "monthly_cost": 96,
                        "yearly_cost": 1157,
                        "price": 89,
                    },
                ],
            }
        ],
    }
    assessment = build_clinical_assessment(DataRepository(clinical_root_str()), analyze)
    products = assessment["products"]
    packages = assessment["packages"]
    assert products["direct_items"] == []
    assert products["matcher_available"] is False
    assert products["source"] == "package_composition"
    assert {item["product_id"] for item in products["package_items"]} == {"SF001", "TR011"}
    tier = packages["tiers"][0]
    assert tier["products"]
    assert tier["monthly_cost"] == 823
    assert tier["yearly_cost"] == 9874
    names = [item["name"] for item in tier["products"]]
    assert "Demo Fresh Beef Bowl" in names


def test_customer_shell_does_not_suppress_package_products():
    shell = (ROOT / "legacy" / "archive" / "frontend" / "ppie-shell.js").read_text(encoding="utf-8")
    ui = (ROOT / "legacy" / "archive" / "frontend" / "ppie-ui.js").read_text(encoding="utf-8")
    assert "No direct matcher recommendations available from current scientific target data." in shell
    assert "Care packages" in shell
    assert "pkg.products" in ui
    assert "monthly_cost" in ui
    assert "yearly_cost" in ui
    assert "Savings vs monthly billing" in shell
    assert "No products available" not in shell
    assert "direct_items" in shell
    assert "PACKAGE_OPTIMIZER_V2_1" in shell


def test_live_demo_packages_keep_products_included(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    client = TestClient(app)
    response = client.post(
        "/api/v1/clinical-report",
        json={
            "name": "Dolly",
            "pet_name": "Dolly",
            "breeds": ["Golden Retriever", "Labrador Retriever"],
            "birthday": "2021-03-15",
            "weight": 30.1,
            "sex": "Female",
            "activity_level": "High",
            "current_environment": "Shanghai Summer",
            "observed_conditions": [],
        },
    )
    assert response.status_code == 200
    body = response.json()
    analyze = body["analyze"]
    assessment = body["assessment"]
    assert analyze.get("productRecommendations") == [] or isinstance(analyze.get("productRecommendations"), list)
    packages = analyze["wellnessPackages"]
    composed = [pkg for pkg in packages if pkg.get("products_included")]
    assert composed
    for pkg in composed:
        assert pkg.get("monthly_cost") is not None
        assert pkg.get("yearly_cost") is not None
    assert assessment["products"]["package_items"]
    if not (analyze.get("productRecommendations") or []):
        assert assessment["products"]["source"] == "package_composition"
        assert assessment["products"]["direct_items"] == []
