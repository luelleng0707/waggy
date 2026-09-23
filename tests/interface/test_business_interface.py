from __future__ import annotations

from fastapi.testclient import TestClient
from pathlib import Path
import pytest

from app.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    return TestClient(app)


def test_business_route_serves_dashboard(client: TestClient):
    response = client.get("/business")
    assert response.status_code == 200
    assert "workbench.js" in response.text
    assert 'data-role="business"' in response.text
    assert "Wagtopia Business Dashboard" not in response.text
    assert "formula_execution.v2" not in response.text
    assert "execution_id" not in response.text


def test_business_surface_contract_runtime_backed(client: TestClient):
    payload = {
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
    response = client.post(
        "/api/v1/presentation/three-surfaces",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert response.status_code == 200
    body = response.json()
    business = body.get("business") or {}
    assert business.get("surface") == "business"
    assert "overview" in business
    assert "portfolio" in business
    assert "health_opportunities" in business
    assert "financial_model" in business


def test_business_ui_contains_no_scientific_runtime_logic():
    root = Path(__file__).resolve().parents[2]
    text = (root / "legacy" / "archive" / "frontend" / "business.js").read_text(encoding="utf-8")
    forbidden = ("compute_risks(", "repository.mathematics", "warehouse/", "scientific_quote =")
    for token in forbidden:
        assert token not in text
