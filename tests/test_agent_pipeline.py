"""Smoke tests for PPIE Python agent pipeline and JS frontend contract."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.agent.engine import PPIEWellnessAgent
from app.agent.response_assembler import LEGACY_MOCK_PATTERN
from app.agent.state import DogProfileInput
from app.main import app

MOCK_ID_PATTERN = LEGACY_MOCK_PATTERN


@pytest.fixture
def dolly_profile() -> DogProfileInput:
    return DogProfileInput(
        name="dolly",
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
    assert report["profile"]["sizeBracket"] == "large"
    assert len(report["pipeline_trace"]) >= 5
    assert report["epidemiology"]["priority_conditions"]


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

    for pid in _collect_product_ids(report):
        assert not MOCK_ID_PATTERN.match(pid), f"legacy mock id leaked: {pid}"


@pytest.mark.asyncio
async def test_mixed_breed_additive_union(dolly_profile: DogProfileInput):
    agent = PPIEWellnessAgent(data_dir="data")
    report = await agent.generate_reproducible_report(dolly_profile)

    evidence = report["epidemiology"]["breed_evidence_detail"]
    breeds_seen = {row["breed"] for row in evidence}
    assert "Golden Retriever" in breeds_seen
    assert "Labrador Retriever" in breeds_seen

    conditions = {row["condition"].lower() for row in evidence}
    assert any("obesity" in c for c in conditions)
    assert any("hip" in c for c in conditions)


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
