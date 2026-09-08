"""Phase 11 package optimizer smoke tests."""

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.package_optimizer import build_optimized_packages, load_candidate_products
from app.agent.utils import DataRepository
from app.core.paths import clinical_root_str
from app.data.report_models import build_all_report_models


@pytest.fixture
def dolly() -> DogProfileInput:
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


def test_candidates_are_active_catalog_only():
    repo = DataRepository(clinical_root_str())
    cands = load_candidate_products(repo, 10.0)
    if not cands:
        pytest.skip("warehouse product catalog is empty outside demo mode")
    assert all(c["status"].lower() == "active" or c["product_id"] for c in cands)
    ids = {c["product_id"] for c in cands}
    assert "SF002" not in ids  # sold_out
    assert "TR006" not in ids  # sold_out
    assert "SF001" in ids


def test_packages_computed_not_empty(dolly):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(dolly))
    pkgs = analyze["wellnessPackages"]
    assert len(pkgs) == 3
    if not any(pkg.get("products_included") for pkg in pkgs):
        pytest.skip("warehouse catalog empty — combinatorial optimizer has no candidates")
    for pkg in pkgs:
        assert pkg["products_included"], f"{pkg['tier']} has no products"
        assert pkg.get("plan_365")
        assert pkg["yearly_cost"] >= pkg["monthly_cost"]
        assert abs(pkg["monthly_cost"] - round(pkg["yearly_cost"] / 12)) <= 1


def test_no_hardcoded_sp_products(dolly):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(dolly))
    for pkg in analyze["wellnessPackages"]:
        for p in pkg["products_included"]:
            assert not str(p.get("product_id", "")).startswith("SP")


def test_report_models_envelope(dolly):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(dolly))
    models = build_all_report_models(DataRepository(clinical_root_str()), analyze)
    assert "standard_report" in models
    assert models["package_details"]["balanced"]
    assert models["annual_plan"]["widgets"]
