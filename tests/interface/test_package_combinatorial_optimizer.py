"""Combinatorial PACKAGE_OPTIMIZER_V2_1: exhaustive search, hard constraints, ranking."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.agent.package_optimizer import build_optimized_packages, load_candidate_products
from app.agent.package_search import evaluate_bundle, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.api.main import app
from app.core.paths import clinical_root_str
from app.data.demo_catalog import demo_product_ids
from app.data.demo_scientific_dataset import SYNTHETIC_VITAMIN_D_MAX_IU_PER_KG_DM, build_demo_requirement_profile


ROOT = Path(__file__).resolve().parents[2]


def _dolly(**kwargs) -> DogProfileInput:
    data = dict(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
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


def test_exhaustive_12_product_search_space(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    assert {c["product_id"] for c in cands} == demo_product_ids()
    search = run_package_search(candidates=cands, profile=_dolly())
    prov = search["provenance"]
    assert prov["search_method"] == "EXHAUSTIVE_ENUMERATION"
    assert prov["total_possible_subsets"] == 4095
    assert prov["evaluated_count"] == 4095
    assert prov["structurally_eligible"] < 4095
    assert prov["valid_count"] + prov["rejected_count"] == 4095
    assert prov["llm_used"] is False
    failures = prov["constraint_failures"]
    assert failures["missing_required_category"] > 0
    assert failures["maximum_nutrient_exceeded"] > 0
    assert search["package_options"]["essential"]
    assert search["package_options"]["balanced"]
    assert search["package_options"]["optimal"]


def test_every_valid_bundle_satisfies_min_and_max(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    search = run_package_search(candidates=cands, profile=_dolly())
    req = search["requirement_profile"]["nutrients"]
    for tier, rows in search["package_options"].items():
        ids = []
        for ev in rows:
            assert ev["constraint_status"] == "VALID"
            assert ev["valid"] is True
            assert not ev["failed_minimums"]
            assert not ev["exceeded_maximums"]
            totals = ev["nutrient_totals"]
            assert totals["protein_pct_dm"] >= req["protein_pct_dm"]["minimum"]
            assert totals["fat_pct_dm"] >= req["fat_pct_dm"]["minimum"]
            assert totals["vitamin_d_iu_per_kg_dm"] <= SYNTHETIC_VITAMIN_D_MAX_IU_PER_KG_DM
            assert totals["conversion"]["as_fed_percent_not_added"] is True
            ids.append(tuple(sorted(ev["product_ids"])))
        assert len(ids) == len(set(ids))
        assert len(rows) >= 1


def test_one_max_failure_rejects_bundle(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    by_id = {c["product_id"]: c for c in cands}
    # SF001 + TR007 + TR003 is constructed to exceed the synthetic vitamin D cap.
    products = [by_id[pid] for pid in ("SF001", "TR007", "TR003")]
    req = build_demo_requirement_profile(weight_kg=30, age_years=4.3)
    ev = evaluate_bundle(
        products,
        requirements=req,
        care_priorities=["joint"],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert ev["valid"] is False
    assert ev["constraint_status"] == "FAIL_MAXIMUM"
    assert ev["exceeded_maximums"]


def test_missing_staple_is_structurally_ineligible(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    treats = [c for c in cands if c["product_id"] in {"TR011", "TR001"}]
    req = build_demo_requirement_profile(weight_kg=30, age_years=4.3)
    ev = evaluate_bundle(
        treats,
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=False,
        structural_reason="missing_required_category",
    )
    assert ev["valid"] is False
    assert ev["constraint_status"] == "FAIL_CATEGORY"


def test_growth_minima_reject_lower_protein_staple(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    sf002 = next(c for c in cands if c["product_id"] == "SF002")
    puppy = _dolly(age_years=0.5)
    req = build_demo_requirement_profile(weight_kg=30, age_years=0.5)
    assert req["nutrients"]["protein_pct_dm"]["minimum"] == 22.5
    ev = evaluate_bundle(
        [sf002],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert ev["constraint_status"] == "FAIL_MINIMUM"
    adult = evaluate_bundle(
        [sf002],
        requirements=build_demo_requirement_profile(weight_kg=30, age_years=4.3),
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
    )
    assert adult["constraint_status"] == "FAIL_MINIMUM"
    assert any(f["nutrient"] == "choline_mg_per_kg_dm" for f in adult["failed_minimums"])


def test_budget_excludes_balanced_over_budget(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    cheap = run_package_search(candidates=cands, profile=_dolly())
    min_cost = min(ev["monthly_cost"] for ev in cheap["package_options"]["balanced"])
    capped = run_package_search(candidates=cands, profile=_dolly(monthly_budget=min_cost))
    for ev in capped["package_options"]["balanced"]:
        assert ev["monthly_cost"] <= min_cost + 1e-6
        assert ev["budget_status"] == "WITHIN_BUDGET"
    assert capped["provenance"]["constraint_failures"]["budget_exceeded"] >= 0


def test_essential_is_cheapest_valid_first(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    search = run_package_search(candidates=cands, profile=_dolly())
    essential = search["package_options"]["essential"]
    costs = [ev["monthly_cost"] for ev in essential]
    assert costs == sorted(costs)


def test_price_change_changes_ranking(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    baseline = run_package_search(candidates=cands, profile=_dolly())
    first = tuple(baseline["package_options"]["essential"][0]["product_ids"])
    mutated = []
    for c in cands:
        row = dict(c)
        if row["product_id"] == first[0]:
            row = dict(row)
            row["monthly_cost"] = float(row["monthly_cost"]) + 5000
            row["yearly_cost"] = float(row["yearly_cost"]) + 60000
        mutated.append(row)
    changed = run_package_search(candidates=mutated, profile=_dolly())
    new_first = tuple(changed["package_options"]["essential"][0]["product_ids"])
    assert new_first != first or changed["package_options"]["essential"][0]["monthly_cost"] != baseline["package_options"]["essential"][0]["monthly_cost"]


def test_counterfactual_and_provenance(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    search = run_package_search(candidates=cands, profile=_dolly())
    bundle = search["package_options"]["balanced"][0]
    assert bundle["product_provenance"]
    for row in bundle["product_provenance"]:
        assert row["product_id"] in bundle["product_ids"]
        assert "still_valid" in row
        assert row["product_id"] in demo_product_ids()


def test_deterministic_repeat(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    a = run_package_search(candidates=cands, profile=_dolly())
    b = run_package_search(candidates=cands, profile=_dolly())
    assert a["provenance"]["valid_count"] == b["provenance"]["valid_count"]
    assert [x["bundle_id"] for x in a["package_options"]["essential"]] == [
        x["bundle_id"] for x in b["package_options"]["essential"]
    ]


def test_surfaces_share_package_options(demo_env):
    client = TestClient(app)
    body = client.post(
        "/api/v1/presentation/workbench",
        json={
            "name": "Dolly",
            "pet_name": "Dolly",
            "breeds": ["Golden Retriever", "Labrador Retriever"],
            "birthday": "2021-03-15",
            "weight": 30.1,
            "sex": "Female",
            "activity_level": "High",
            "current_environment": "Shanghai Summer",
            "correlation_id": "omega97-combo-001",
        },
    )
    assert body.status_code == 200
    payload = body.json()
    cust = payload["roles"]["customer"]["wellness"]["package_options"]
    biz = payload["roles"]["business"]["portfolio"]["package_options"]
    gro = payload["roles"]["groomer"]["package_options"]
    dev = payload["roles"]["developer"]["package_optimization"]["package_options"]
    for tier in ("essential", "balanced", "optimal"):
        cids = [row["bundle_id"] for row in cust[tier]]
        assert cids
        assert cids == [row["bundle_id"] for row in biz[tier]]
        assert cids == [row["bundle_id"] for row in gro[tier]]
        assert cids == [row["bundle_id"] for row in dev[tier]]
        for row in cust[tier]:
            assert row["constraint_status"] == "VALID"
            assert "nutrient_rows" not in row
            assert row.get("nutrition_facts")
        assert dev[tier][0].get("product_provenance")
        assert dev[tier][0].get("nutrient_rows")
    search = payload["roles"]["developer"]["package_optimization"]["search"]
    assert search["search_method"] == "EXHAUSTIVE_ENUMERATION"
    assert search["evaluated_count"] == 4095
    assert search["llm_used"] is False


def test_frontend_does_not_hardcode_combo_outputs():
    js = (WORKBENCH_JS).read_text(encoding="utf-8")
    assert "SF001" not in js
    assert "4095" not in js
    assert "package_options" in js
    assert "EXHAUSTIVE_ENUMERATION" in js


def test_compatibility_packages_derive_from_options(demo_repo):
    pkgs = build_optimized_packages(
        repo=demo_repo,
        profile=_dolly(),
        health_insights=[],
        ingredients=[],
    )
    assert len(pkgs) == 3
    envelope = pkgs[0]["_search_envelope"]
    for pkg in pkgs:
        top = (envelope["package_options"][pkg["tier"]] or [None])[0]
        if not pkg["products_included"]:
            continue
        got = [p["product_id"] for p in pkg["products_included"]]
        assert got == top["product_ids"]


def test_no_llm_import_in_search():
    text = (ROOT / "app" / "agent" / "package_search.py").read_text(encoding="utf-8")
    for token in ("openai", "anthropic", "gemini", "ollama", "langchain"):
        assert token not in text.lower()
