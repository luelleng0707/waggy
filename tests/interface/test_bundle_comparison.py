"""Customer comparison payload is assembled from canonical optimizer options."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app


@pytest.fixture
def demo_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)


def test_options_are_comparable_across_tiers(demo_env):
    client = TestClient(app)
    body = client.post(
        "/api/v1/presentation/workbench",
        json={
            "name": "Dolly",
            "pet_name": "Dolly",
            "breeds": ["Labrador Retriever", "Golden Retriever"],
            "birthday": "2021-04-15",
            "weight": 30,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Outdoor",
            "correlation_id": "omega10-compare-001",
        },
    )
    assert body.status_code == 200
    payload = body.json()
    options = payload["roles"]["customer"]["wellness"]["package_options"]
    picked = []
    for tier in ("essential", "balanced", "optimal"):
        assert options[tier]
        picked.append(options[tier][0])
    keys = {"monthly_cost", "product_ids", "care_pathways", "budget_status", "nutrition_facts"}
    for ev in picked:
        assert keys <= set(ev)
        assert ev["bundle_id"]
        assert ev["nutrition_facts"]
        assert ev.get("products") is not None
