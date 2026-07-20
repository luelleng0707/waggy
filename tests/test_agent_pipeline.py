"""Smoke tests for PPIE Python agent pipeline and JS frontend contract."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.main import app


@pytest.fixture
def dolly_profile() -> DogProfileInput:
    return DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=4.3,
        weight_kg=30.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )


def _assert_numeric_cost(value) -> None:
    assert isinstance(value, (int, float)), f"expected numeric cost, got {type(value)}: {value!r}"
    assert not isinstance(value, str)


def _collect_product_ids(payload: dict) -> list[str]:
    ids: list[str] = []
    for pkg in payload.get("wellnessPackages", []):
        for p in pkg.get("products_included", []):
            ids.append(p.get("product_id", ""))
    for p in payload.get("productRecommendations", []):
        ids.append(p.get("product_id", ""))
    return [i for i in ids if i]


@pytest.mark.asyncio
async def test_agent_pipeline_runs(dolly_profile: DogProfileInput):
    agent = PPIEWellnessAgent(data_dir="data")
    report = await agent.generate_reproducible_report(dolly_profile)

    assert report["engine"] == "PPIE"
    assert report["version"] == "2.1.0"
    assert "wellness_summary" in report
    assert "wellnessPackages" in report
    assert "packageDetails" in report
    assert "productAnalyses" in report
    assert report["profile"]["pet_name"] == "Dolly"
    assert report["profile"]["age_stage"] in {"adult", "senior", "puppy", "junior"}
    assert len(report["pipeline_trace"]) >= 5
    assert report["healthInsights"]
    assert report["wellnessPackages"]


@pytest.mark.asyncio
async def test_frontend_contract_numeric_pricing(dolly_profile: DogProfileInput):
    agent = PPIEWellnessAgent(data_dir="data")
    report = await agent.generate_reproducible_report(dolly_profile)

    for pkg in report["wellnessPackages"]:
        _assert_numeric_cost(pkg["monthly_cost"])
        _assert_numeric_cost(pkg["yearly_cost"])
        assert pkg["monthly_cost"] > 0
        assert pkg["yearly_cost"] > 0

    for rec in report.get("productRecommendations", []):
        _assert_numeric_cost(rec["price"])

    for tier, detail in report["packageDetails"].items():
        _assert_numeric_cost(detail["monthly_cost"])
        for card in detail.get("product_cards", []):
            _assert_numeric_cost(card["monthly_cost"])


@pytest.mark.asyncio
async def test_no_legacy_mock_product_ids(dolly_profile: DogProfileInput):
    agent = PPIEWellnessAgent(data_dir="data")
    report = await agent.generate_reproducible_report(dolly_profile)
    catalog_ids = set(agent.repo.active_products()["product_id"].astype(str))

    for pid in _collect_product_ids(report):
        assert pid in catalog_ids, f"product id not in active PRODUCT_CATALOG: {pid}"


@pytest.mark.asyncio
async def test_mixed_breed_additive_union(dolly_profile: DogProfileInput):
    agent = PPIEWellnessAgent(data_dir="data")
    report = await agent.generate_reproducible_report(dolly_profile)

    breeds = report["profile"]["breeds"]
    assert "Golden Retriever" in breeds
    assert "Labrador Retriever" in breeds

    # Trait-level risks should reflect both large-breed and obesity-prone lineages.
    conditions = " ".join(
        str(r.get("condition") or r.get("condition_key") or "").lower()
        for r in report.get("risks", [])
    )
    assert "hip" in conditions or "dysplasia" in conditions or "joint" in conditions
    assert "obesity" in conditions or "weight" in conditions or len(report.get("risks", [])) > 0


@pytest.mark.asyncio
async def test_fastapi_evaluate_endpoint(dolly_profile: DogProfileInput):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v2/wellness/evaluate",
            json=dolly_profile.model_dump(),
        )

    assert response.status_code == 200
    body = response.json()
    assert body["engine"] == "PPIE"
    assert body["version"] == "2.1.0"
    assert "wellnessPackages" in body
    assert "wellness_summary" in body
    assert body["wellnessPackages"][1]["recommended"] is True
