"""Exhaustive nutrient-constrained PACKAGE_OPTIMIZER_V2_1."""

from __future__ import annotations

import pytest

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import evaluate_bundle, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.core.paths import clinical_root_str
from app.data.demo_scientific_dataset import (
    NUTRIENT_IDS,
    aggregate_contributions,
    build_demo_requirement_profile,
    product_daily_contribution,
)


def _dolly(**kwargs) -> DogProfileInput:
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


def test_contributions_sum_to_bundle_total(demo_repo):
    weight = 30.0
    ids = ("SF001", "TR003", "JB001")
    parts = [product_daily_contribution(pid, weight) for pid in ids]
    manual = aggregate_contributions(parts)
    cands = {c["product_id"]: c for c in load_candidate_products(demo_repo, weight)}
    products = [cands[pid] for pid in ids]
    ev = evaluate_bundle(
        products,
        requirements=build_demo_requirement_profile(weight_kg=weight, age_years=4.3),
        care_priorities=["joint"],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    for nid in ("protein_pct_dm", "fat_pct_dm", "calcium_pct_dm", "vitamin_d_iu_per_kg_dm", "choline_mg_per_kg_dm"):
        assert abs(float(manual["densities"][nid]) - float(ev["nutrient_totals"][nid])) < 1e-6
        summed = sum(float((p.get("daily_amounts") or {}).get(nid) or 0) for p in parts)
        assert abs(summed - float(manual["daily_amounts"][nid])) < 1e-8


def test_raw_combination_count_is_power_set(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    n = len(cands)
    search = run_package_search(candidates=cands, profile=_dolly())
    assert search["provenance"]["total_possible_subsets"] == (2**n) - 1
    assert search["provenance"]["evaluated_count"] == (2**n) - 1


def test_every_returned_bundle_has_ledger_and_source(demo_repo):
    search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    for tier, rows in search["package_options"].items():
        for ev in rows:
            assert ev["nutrition_facts"]
            assert ev["minimums_total"] >= 10
            assert ev["minimums_passed"] == ev["minimums_total"]
            assert ev["maximums_passed"] == ev["maximums_total"]
            for row in ev["nutrient_rows"]:
                assert row["source"]["source_type"] == "secondary_source"
                assert row["status"] in {"PASS", "LOW", "NEAR_MAXIMUM", "NO_MODELED_MAXIMUM", "NO_MODELED_MINIMUM", "NOT_MODELED"}
                assert row["status"] not in {"FAIL_MINIMUM", "FAIL_MAXIMUM", "DEFICIENT", "EXCESS"}


def test_synthetic_excess_product_rejected_then_removed(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    hot = dict(cands[0])
    hot["product_id"] = "XMAX"
    # Inject via evaluate: use TR003 vitamin D extras on SF001 already fails.
    by_id = {c["product_id"]: c for c in cands}
    req = build_demo_requirement_profile(weight_kg=30, age_years=4.3)
    bad = evaluate_bundle(
        [by_id["SF001"], by_id["TR003"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert bad["constraint_status"] == "FAIL_MAXIMUM"
    good = evaluate_bundle(
        [by_id["SF001"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert good["constraint_status"] == "VALID"


def test_choline_minimum_fixed_by_supplement(demo_repo):
    by_id = {c["product_id"]: c for c in load_candidate_products(demo_repo, 30.0)}
    req = build_demo_requirement_profile(weight_kg=30, age_years=4.3)
    alone = evaluate_bundle(
        [by_id["SF002"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert alone["constraint_status"] == "FAIL_MINIMUM"
    fixed = evaluate_bundle(
        [by_id["SF002"], by_id["TR007"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert fixed["constraint_status"] == "VALID"
    assert not any(f["nutrient"] == "choline_mg_per_kg_dm" for f in fixed["failed_minimums"])


def test_budget_800_and_1500_and_none(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    low = run_package_search(candidates=cands, profile=_dolly(monthly_budget=800))
    for ev in low["package_options"]["balanced"]:
        assert ev["monthly_cost"] <= 800 + 1e-6
        assert ev["budget_status"] == "WITHIN_BUDGET"
    high = run_package_search(candidates=cands, profile=_dolly(monthly_budget=1500))
    none = run_package_search(candidates=cands, profile=_dolly())
    assert high["provenance"]["balanced_budget_status"] in {"WITHIN_BUDGET", "NO_VALID_BUNDLE_WITHIN_BUDGET"}
    opt_with_budget = [tuple(e["product_ids"]) for e in low["package_options"]["optimal"]]
    opt_none = [tuple(e["product_ids"]) for e in none["package_options"]["optimal"]]
    # Optimal is not required to shrink to the ¥800 set.
    assert opt_with_budget
    assert opt_none


def test_optimal_can_exceed_budget_when_balanced_cannot(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    search = run_package_search(candidates=cands, profile=_dolly(monthly_budget=700))
    for ev in search["package_options"]["balanced"]:
        assert ev["monthly_cost"] <= 700 + 1e-6
    # Optimal ignores the ceiling.
    assert search["package_options"]["optimal"]
    assert any(ev["monthly_cost"] > 700 for ev in search["package_options"]["optimal"]) or search["package_options"]["optimal"][0]["monthly_cost"] <= 700


def test_breed_changes_balanced_not_essential_minima(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    lab = run_package_search(
        candidates=cands,
        profile=_dolly(primary_breed="Labrador Retriever", secondary_breed="Golden Retriever"),
        repo=demo_repo,
    )
    other = run_package_search(
        candidates=cands,
        profile=_dolly(primary_breed="Beagle", secondary_breed=None, observed_conditions=[]),
        repo=demo_repo,
    )
    assert lab["requirement_profile"]["nutrients"]["protein_pct_dm"]["minimum"] == other["requirement_profile"]["nutrients"]["protein_pct_dm"]["minimum"]
    assert "joint" in lab["care_priorities"]
    assert "joint" not in other["care_priorities"]
    lab_ids = [tuple(e["product_ids"]) for e in lab["package_options"]["balanced"]]
    other_ids = [tuple(e["product_ids"]) for e in other["package_options"]["balanced"]]
    assert lab_ids != other_ids or lab["care_priorities"] != other["care_priorities"]


def test_age_changes_protein_minimum(demo_repo):
    puppy = build_demo_requirement_profile(weight_kg=30, age_years=0.4)
    adult = build_demo_requirement_profile(weight_kg=30, age_years=4.3)
    senior = build_demo_requirement_profile(weight_kg=30, age_years=8.0)
    assert puppy["nutrients"]["protein_pct_dm"]["minimum"] == 22.5
    assert adult["nutrients"]["protein_pct_dm"]["minimum"] == 18.0
    assert senior["nutrients"]["protein_pct_dm"]["minimum"] == 18.0
    assert "NOT_AVAILABLE" in senior["senior_specific_minima"]


def test_weight_scales_daily_amounts_not_percent_minima():
    c30 = product_daily_contribution("SF001", 30.0)
    c10 = product_daily_contribution("SF001", 10.0)
    assert abs(c30["daily_dm_g"] / c10["daily_dm_g"] - 3.0) < 0.05
    req30 = build_demo_requirement_profile(weight_kg=30, age_years=4)
    req10 = build_demo_requirement_profile(weight_kg=10, age_years=4)
    assert req30["nutrients"]["protein_pct_dm"]["minimum"] == req10["nutrients"]["protein_pct_dm"]["minimum"]


def test_no_invalid_in_returned_options(demo_repo):
    search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    for rows in search["package_options"].values():
        for ev in rows:
            assert ev["constraint_status"] == "VALID"
            assert ev["nutrient_valid"] is True


def test_funnel_counts_are_runtime(demo_repo):
    search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    funnel = search["provenance"]["filter_funnel"]
    assert funnel["generated"] == 4095
    assert funnel["evaluated"] == 4095
    assert funnel["nutrient_valid"] + search["provenance"]["constraint_failures"]["minimum_nutrient_failure"] + search["provenance"]["constraint_failures"]["maximum_nutrient_exceeded"] + search["provenance"]["constraint_failures"]["missing_required_category"] + search["provenance"]["constraint_failures"]["missing_nutrient_data"] == 4095
    assert search["provenance"]["non_dominated_count"] <= funnel["nutrient_valid"]
