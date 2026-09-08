"""Every returned bundle exposes a complete nutrient ledger from the optimizer."""

from __future__ import annotations

import pytest

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import evaluate_bundle, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.core.paths import clinical_root_str
from app.data.demo_scientific_dataset import build_demo_requirement_profile


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


@pytest.fixture
def search(demo_repo):
    return run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly(), repo=demo_repo)


def test_every_valid_bundle_has_complete_ledger(search):
    for tier, rows in search["package_options"].items():
        assert rows
        for ev in rows:
            ledger = ev["nutrition_ledger"]
            assert ledger["nutrients"]
            assert ledger["daily_dm_kg"] > 0
            assert "density" in (ledger.get("daily_requirement_note") or "").lower() or "dry matter" in (
                ledger.get("daily_requirement_note") or ""
            ).lower()
            for row in ledger["nutrients"]:
                assert row.get("nutrient")
                assert "actual_density_dm" in row
                assert "actual_per_day" in row
                assert "required_density_min_dm" in row
                assert "required_daily_min" in row
                if row.get("required_minimum") is not None and row.get("actual") is not None:
                    assert row.get("percent_of_minimum") is not None
                    dm_kg = float(ledger["daily_dm_kg"])
                    kind = row.get("kind")
                    minimum = float(row["required_minimum"])
                    derived = row.get("required_daily_min")
                    if derived is not None and kind == "pct_dm":
                        expected = minimum / 100.0 * float(ledger["daily_dm_g"])
                        assert abs(float(derived) - expected) < 1e-6
                    elif derived is not None and kind in {"mg_kg_dm", "iu_kg_dm"}:
                        expected = minimum * dm_kg
                        assert abs(float(derived) - expected) < 1e-6
                    daily = row.get("actual_per_day")
                    density = row.get("actual_density_dm")
                    if daily is not None and density is not None and kind in {"mg_kg_dm", "iu_kg_dm"}:
                        assert abs(float(daily) - float(density) * dm_kg) < 1e-4 or row.get("products_contributing")
                if row.get("status") in {"FAIL_MINIMUM", "FAIL_MAXIMUM"}:
                    raise AssertionError(f"invalid row leaked into {tier}: {row.get('nutrient')}")
            assert ev["coverage_summary"]["daily_dm_kg"] == ledger["daily_dm_kg"] or abs(
                float(ev["coverage_summary"]["daily_dm_kg"]) - float(ledger["daily_dm_kg"])
            ) < 1e-9


def test_daily_requirement_is_derived_not_copied_from_source(demo_repo):
    cands = {c["product_id"]: c for c in load_candidate_products(demo_repo, 30.0)}
    req = build_demo_requirement_profile(weight_kg=30.0, age_years=4.3)
    ev = evaluate_bundle(
        [cands["SF002"], cands["TR007"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    vit = next(r for r in ev["nutrient_rows"] if r["nutrient"] == "vitamin_d_iu_per_kg_dm")
    assert vit["required_density_min_dm"] == 500
    assert vit["required_daily_min"] != 500
    assert abs(float(vit["required_daily_min"]) - 500 * float(ev["daily_dm_kg"])) < 1e-6
    assert ev["constraint_status"] == "VALID"


def test_minimum_and_maximum_are_hard_filters(demo_repo):
    cands = {c["product_id"]: c for c in load_candidate_products(demo_repo, 30.0)}
    req = build_demo_requirement_profile(weight_kg=30.0, age_years=4.3)
    alone = evaluate_bundle(
        [cands["SF002"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert alone["constraint_status"] == "FAIL_MINIMUM"
    assert any(f["nutrient"] == "choline_mg_per_kg_dm" for f in alone["failed_minimums"])
    hot = evaluate_bundle(
        [cands["SF001"], cands["TR003"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert hot["constraint_status"] == "FAIL_MAXIMUM"
    search = run_package_search(candidates=list(cands.values()), profile=_dolly())
    for rows in search["package_options"].values():
        for ev in rows:
            assert ev["bundle_id"] != alone["bundle_id"]
            assert ev["bundle_id"] != hot["bundle_id"]
            assert not ev["failed_minimums"]
            assert not ev["exceeded_maximums"]
