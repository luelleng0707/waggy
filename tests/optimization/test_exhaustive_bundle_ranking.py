"""Exhaustive ranking uses all nutrient-valid bundles, not the Pareto subset."""

from __future__ import annotations

import pytest

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import PACKAGE_DISPLAY_LIMIT, evaluate_bundle, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.core.paths import clinical_root_str
from app.data.demo_scientific_dataset import build_demo_requirement_profile


def _dolly(**kwargs) -> DogProfileInput:
    data = dict(
        name="Dolly",
        primary_breed="Labrador Retriever",
        secondary_breed="Golden Retriever",
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


def test_exhaustive_count_and_ranking_pool(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    n = len(cands)
    search = run_package_search(candidates=cands, profile=_dolly())
    prov = search["provenance"]
    assert n == 12
    assert prov["evaluated_count"] == (2**n) - 1 == 4095
    assert prov["valid_count"] > prov["non_dominated_count"]
    assert prov["tier_valid_counts"]["essential"] > PACKAGE_DISPLAY_LIMIT
    assert len(search["package_options"]["essential"]) <= PACKAGE_DISPLAY_LIMIT
    assert len(search["package_options"]["essential"]) < prov["tier_valid_counts"]["essential"]
    costs = [ev["monthly_cost"] for ev in search["package_options"]["essential"]]
    assert costs == sorted(costs)


def test_removing_product_removes_its_bundles(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    full = run_package_search(candidates=cands, profile=_dolly())
    target = None
    for ev in full["package_options"]["essential"]:
        if "TR007" in ev["product_ids"] and "SF002" in ev["product_ids"]:
            target = ev
            break
    assert target is not None
    reduced = [c for c in cands if c["product_id"] != "TR007"]
    gone = run_package_search(candidates=reduced, profile=_dolly())
    for rows in gone["package_options"].values():
        for ev in rows:
            assert "TR007" not in ev["product_ids"]
            assert ev["bundle_id"] != target["bundle_id"]
    assert gone["provenance"]["evaluated_count"] == (2 ** len(reduced)) - 1


def test_choline_and_price_causality(demo_repo):
    cands = {c["product_id"]: dict(c) for c in load_candidate_products(demo_repo, 30.0)}
    req = build_demo_requirement_profile(weight_kg=30.0, age_years=4.3)
    before = evaluate_bundle(
        [cands["SF002"], cands["TR007"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    choline = next(r for r in before["nutrient_rows"] if r["nutrient"] == "choline_mg_per_kg_dm")
    assert choline["status"] in {"PASS", "LOW", "NO_MODELED_MAXIMUM"}
    priced = dict(cands["TR007"])
    priced["monthly_cost"] = float(priced["monthly_cost"]) + 8000
    priced["yearly_cost"] = float(priced.get("yearly_cost") or 0) + 96000
    mutated = [priced if c["product_id"] == "TR007" else c for c in cands.values()]
    ranked = run_package_search(candidates=mutated, profile=_dolly())
    first = ranked["package_options"]["essential"][0]
    assert "TR007" not in first["product_ids"] or first["monthly_cost"] >= before["monthly_cost"] + 7000


def test_deterministic_ordering(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    a = run_package_search(candidates=cands, profile=_dolly())
    b = run_package_search(candidates=cands, profile=_dolly())
    for tier in ("essential", "balanced", "optimal"):
        assert [x["bundle_id"] for x in a["package_options"][tier]] == [
            x["bundle_id"] for x in b["package_options"][tier]
        ]
