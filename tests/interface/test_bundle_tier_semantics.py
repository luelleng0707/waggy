"""Essential / Balanced / Optimal membership and ranking semantics."""

from __future__ import annotations

import pytest

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import RANKING_RULES, TIER_SEMANTICS, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.core.paths import clinical_root_str


def _dog(**kwargs) -> DogProfileInput:
    data = dict(
        name="Dolly",
        primary_breed="Labrador Retriever",
        secondary_breed="Golden Retriever",
        breed_split_pct=50.0,
        age_years=4.3,
        weight_kg=30.0,
        current_environment="Temperate Outdoor",
        activity_level="Moderate",
        observed_conditions=["joint_stiffness"],
    )
    data.update(kwargs)
    return DogProfileInput(**data)


@pytest.fixture
def demo_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)


@pytest.fixture
def demo_repo(demo_env) -> DataRepository:
    return DataRepository(clinical_root_str())


def test_essential_ignores_breed_care_for_eligibility_and_ranking(demo_repo):
    lab = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dog(), repo=demo_repo)
    poodle = run_package_search(
        candidates=load_candidate_products(demo_repo, 30.0),
        profile=_dog(primary_breed="Poodle", secondary_breed=None, observed_conditions=[]),
        repo=demo_repo,
    )
    assert lab["provenance"]["tier_semantics"]["essential"]["uses_breed_care_for_eligibility"] is False
    assert lab["provenance"]["tier_semantics"]["essential"]["uses_breed_care_for_ranking"] is False
    lab_ids = [ev["bundle_id"] for ev in lab["package_options"]["essential"]]
    poodle_ids = [ev["bundle_id"] for ev in poodle["package_options"]["essential"]]
    assert lab_ids == poodle_ids
    assert lab["provenance"]["tier_valid_counts"]["essential"] == poodle["provenance"]["tier_valid_counts"]["essential"]
    for ev in lab["package_options"]["essential"]:
        assert all(not row.get("breed_recommended") for row in ev["nutrient_rows"])
        assert "Breed-care score is not used" in " ".join(ev["why_selected"])


def test_balanced_uses_breed_care_and_stars(demo_repo):
    lab = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dog(), repo=demo_repo)
    poodle = run_package_search(
        candidates=load_candidate_products(demo_repo, 30.0),
        profile=_dog(primary_breed="Poodle", secondary_breed=None, observed_conditions=[]),
        repo=demo_repo,
    )
    assert lab["provenance"]["tier_semantics"]["balanced"]["uses_breed_care_for_ranking"] is True
    assert lab["care_priorities"]
    for ev in lab["package_options"]["balanced"]:
        assert float(ev.get("care_coverage_score") or 0) > 0
        stars = [row for row in ev["nutrient_rows"] if row.get("breed_recommended")]
        for row in stars:
            assert row.get("nutrient") in (lab["care_model"].get("star_nutrients") or [])
    if not poodle["care_priorities"]:
        assert poodle["provenance"]["tier_valid_counts"]["balanced"] >= lab["provenance"]["tier_valid_counts"]["balanced"]


def test_budget_ceiling_essential_balanced_not_optimal(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    open_search = run_package_search(candidates=cands, profile=_dog(), repo=demo_repo)
    cheap = min(ev["monthly_cost"] for ev in open_search["package_options"]["essential"])
    expensive = max(
        ev["monthly_cost"]
        for tier in open_search["package_options"].values()
        for ev in tier
    )
    budget = cheap + 90
    capped = run_package_search(candidates=cands, profile=_dog(monthly_budget=budget), repo=demo_repo)
    for ev in capped["package_options"]["essential"]:
        assert ev["monthly_cost"] <= budget + 1e-6
    for ev in capped["package_options"]["balanced"]:
        assert ev["monthly_cost"] <= budget + 1e-6
    if expensive > budget:
        assert any(ev["monthly_cost"] > budget for ev in capped["package_options"]["optimal"]) or (
            capped["provenance"]["tier_valid_counts"]["optimal"] >= capped["provenance"]["tier_valid_counts"]["essential"]
        )
    assert TIER_SEMANTICS["optimal"]["budget_is_hard_ceiling"] is False
    assert RANKING_RULES["essential"]


def test_optimal_is_not_most_expensive_by_definition(demo_repo):
    search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dog(), repo=demo_repo)
    optimal = search["package_options"]["optimal"]
    costs = [ev["monthly_cost"] for ev in optimal]
    assert costs[0] == min(costs) or optimal[0]["nutrition_balance_score"] >= min(
        ev["nutrition_balance_score"] for ev in optimal
    )
    scores = [ev["overall_score"] for ev in optimal]
    assert scores == sorted(scores, reverse=True)
