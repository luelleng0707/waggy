"""Ω16: one engine, four projections."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.http_models import WORKBENCH_EXAMPLE_REQUEST
from app.api.main import app
import app.api.main as api_main


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_workbench_calls_generate_reproducible_report_once(monkeypatch: pytest.MonkeyPatch, demo_client: TestClient):
    calls = {"n": 0}
    original = api_main.agent.generate_reproducible_report

    async def spy(profile):
        calls["n"] += 1
        return await original(profile)

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", spy)
    response = demo_client.post("/api/v1/presentation/workbench", json=WORKBENCH_EXAMPLE_REQUEST)
    assert response.status_code == 200
    assert calls["n"] == 1
    body = response.json()
    assert set(body["roles"]) == {"customer", "groomer", "business", "developer"}


def test_role_projections_differ_but_share_signature(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=WORKBENCH_EXAMPLE_REQUEST).json()
    roles = body["roles"]
    assert roles["customer"]["surface"] == "customer"
    assert roles["groomer"]["surface"] == "groomer"
    assert roles["business"]["surface"] == "business"
    assert roles["developer"]["surface"] == "developer"
    assert roles["customer"] != roles["groomer"]
    assert roles["customer"] != roles["business"]
    assert roles["developer"]["analysis_signature"] == body["analysis_signature"]
    assert body["canonical"]["analysis_id"] == body["analysis_signature"]

    def _has_key(obj: object, token: str) -> bool:
        if isinstance(obj, dict):
            return token in obj or any(_has_key(value, token) for value in obj.values())
        if isinstance(obj, list):
            return any(_has_key(item, token) for item in obj)
        return False

    assert not _has_key(roles["customer"], "independent_of_product_match")
    assert roles["developer"]["package_optimization"]["formula_id"] == "PACKAGE_OPTIMIZER_V2_1"


def test_role_context_without_observations_does_not_change_science(demo_client: TestClient):
    customer = dict(WORKBENCH_EXAMPLE_REQUEST)
    customer["role_context"] = {"customer": {"presentation_role": "customer"}}
    business = dict(WORKBENCH_EXAMPLE_REQUEST)
    business["role_context"] = {"business": {"segment": "retail"}}
    a = demo_client.post("/api/v1/presentation/workbench", json=customer).json()
    b = demo_client.post("/api/v1/presentation/workbench", json=business).json()
    assert a["analysis_signature"] == b["analysis_signature"]
    assert a["canonical"]["scientific_analysis"]["findings"] == b["canonical"]["scientific_analysis"]["findings"]


def test_no_role_specific_analysis_routes(demo_client: TestClient):
    paths = demo_client.get("/openapi.json").json()["paths"]
    for suffix in ("customer", "groomer", "business", "developer"):
        assert f"/api/v1/analyze/{suffix}" not in paths
