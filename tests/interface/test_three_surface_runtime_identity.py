from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


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


def test_three_surfaces_share_single_correlation_and_signature(client: TestClient):
    correlation_id = "omega97a-dolly-correlation"
    response = client.post(
        "/api/v1/presentation/three-surfaces?debug=1",
        headers={"x-wagtopia-correlation-id": correlation_id},
        json=_dolly_payload(),
    )
    assert response.status_code == 200

    body = response.json()
    assert body["schema"] == "three_surface_presentation.v1"
    assert body.get("presentation_correlation_id") == correlation_id
    assert body.get("analysis_signature")
    assert body.get("customer", {}).get("surface") == "customer"
    assert body.get("business", {}).get("surface") == "business"
    assert body.get("developer", {}).get("surface") == "developer"
    assert body.get("customer", {}).get("dog", {}).get("name") == "Dolly"

    customer_packages = body.get("customer", {}).get("wellness", {}).get("package_composition") or []
    business_packages = body.get("business", {}).get("portfolio", {}).get("package_composition") or []
    developer_packages = body.get("developer", {}).get("package_optimization", {}).get("packages") or []
    assert customer_packages
    assert business_packages
    assert developer_packages
    assert [p.get("tier") for p in customer_packages] == [p.get("tier") for p in business_packages]

    execution_records = body.get("developer", {}).get("execution_records") or []
    assert execution_records, "debug-mode developer projection should include execution records"

    customer_blob = str(body.get("customer") or {})
    business_blob = str(body.get("business") or {})
    developer_blob = str(body.get("developer") or {})

    assert "execution_id" not in customer_blob
    assert "source_location" not in customer_blob
    assert "execution_id" not in business_blob
    assert "source_location" not in business_blob
    assert "execution_records" in developer_blob
