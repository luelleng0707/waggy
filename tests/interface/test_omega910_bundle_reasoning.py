"""OMEGA 9.10: names, care-level semantics, nutrition facts, roles, frontend honesty."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import evaluate_bundle, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.api.main import app
from app.core.paths import clinical_root_str
from app.data.demo_catalog import demo_product_ids
from app.data.demo_scientific_dataset import build_demo_requirement_profile


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_SKUS = ("SF001", "SF002", "TR003", "TR007", "TR011", "JB001")
DIAGNOSIS_PHRASES = (
    "your dog has",
    "this supplement will prevent",
    "this guarantees reduced risk",
    "diagnosed with",
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
        observed_conditions=["joint_stiffness", "itching"],
    )
    data.update(kwargs)
    return DogProfileInput(**data)


def _dolly_json(**kwargs) -> dict:
    payload = {
        "name": "Dolly",
        "pet_name": "Dolly",
        "breeds": ["Labrador Retriever", "Golden Retriever"],
        "birthday": "2021-04-15",
        "weight": 30,
        "sex": "Female",
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": ["joint_stiffness", "itching"],
        "correlation_id": "omega910-demo-001",
    }
    payload.update(kwargs)
    return payload


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


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def _first(search: dict, tier: str) -> dict:
    rows = search["package_options"][tier]
    assert rows, f"no {tier} options"
    return rows[0]


def test_a_product_id_resolves_to_catalog_name(demo_repo, search):
    catalog = {
        str(row["product_id"]): str(row["product_name"])
        for _, row in demo_repo.active_products().iterrows()
    }
    for tier, rows in search["package_options"].items():
        for ev in rows:
            names = ev.get("display_product_names") or []
            assert names, f"{tier} {ev['bundle_id']} missing display names"
            for item in ev["products"]:
                pid = str(item["product_id"])
                assert item["product_name"] == catalog[pid]
                assert item["product_name"] != pid
                assert item["product_name"] in names


def test_b_essential_has_no_breed_specific_mandatory_requirements(search):
    assert search["provenance"]["tier_semantics"]["essential"]["uses_breed_care_for_eligibility"] is False
    assert search["provenance"]["tier_semantics"]["essential"]["uses_breed_care_for_ranking"] is False
    for ev in search["package_options"]["essential"]:
        assert ev.get("preventative_pathways") in ([], None)
        assert all(not row.get("breed_recommended") for row in ev["nutrient_rows"])
        assert "Breed-care score is not used" in " ".join(ev["why_selected"])


def test_c_balanced_contains_baseline_plus_preventative(search):
    assert search["care_priorities"]
    for ev in search["package_options"]["balanced"]:
        assert ev["minimums_passed"] == ev["minimums_total"]
        assert float(ev.get("care_coverage_score") or 0) > 0
        assert ev.get("preventative_pathways")
        reasoning = ev["bundle_reasoning"]
        assert reasoning["baseline_nutrition"]
        assert reasoning["preventative_care"]


def test_d_optimal_contains_baseline_plus_preventative(search):
    for ev in search["package_options"]["optimal"]:
        assert ev["minimums_passed"] == ev["minimums_total"]
        assert ev.get("preventative_pathways")
        assert ev["bundle_reasoning"]["baseline_nutrition"]
        assert ev["bundle_reasoning"]["preventative_care"]


def test_e_all_nutrient_minimums_enforced(search):
    for ev in search["package_options"]["essential"]:
        assert not ev.get("failed_minimums")
        for row in ev["nutrient_rows"]:
            if row.get("required_minimum") is not None and row.get("actual") is not None:
                assert float(row["actual"]) + 1e-9 >= float(row["required_minimum"])


def test_f_available_nutrient_maximums_enforced(search):
    for ev in search["package_options"]["essential"]:
        assert not ev.get("exceeded_maximums")
        for row in ev["nutrient_rows"]:
            if row.get("maximum_specified") and row.get("actual") is not None:
                assert float(row["actual"]) <= float(row["allowed_maximum"]) + 1e-9


def test_g_missing_maximum_does_not_create_artificial_failure(demo_repo):
    cands = {p["product_id"]: p for p in load_candidate_products(demo_repo, 30.0)}
    req = build_demo_requirement_profile(weight_kg=30.0, age_years=4.3)
    ev = evaluate_bundle(
        [cands["SF002"], cands["TR007"]],
        requirements=req,
        care_priorities=[],
        monthly_budget=None,
        structurally_ok=True,
        structural_reason=None,
        star_nutrients=[],
        apply_stars=False,
    )
    protein = next(row for row in ev["nutrient_rows"] if row["nutrient"] == "protein_pct_dm")
    assert protein["maximum_specified"] is False
    assert protein["allowed_maximum"] is None
    assert protein["status"] != "FAIL_MAXIMUM"
    assert "Not specified" in (protein.get("maximum_copy") or "")


def test_h_every_evaluated_combination_receives_nutrient_ledger(demo_repo):
    cands = load_candidate_products(demo_repo, 30.0)
    req = build_demo_requirement_profile(weight_kg=30.0, age_years=4.3)
    for combo in ([cands[0]], [cands[0], cands[1]], cands[:3]):
        ev = evaluate_bundle(
            combo,
            requirements=req,
            care_priorities=["joint"],
            monthly_budget=None,
            structurally_ok=True,
            structural_reason=None,
            star_nutrients=[],
            apply_stars=False,
        )
        assert ev["nutrient_rows"]
        assert ev["nutrition_ledger"]["nutrients"] or ev["nutrient_rows"]


def test_i_rejected_combinations_retain_rejection_reasons(search):
    rejections = search["provenance"]["example_rejections"]
    assert rejections
    for row in rejections:
        assert row.get("reason")
        assert row.get("constraint_status")
        assert row.get("nutrient_row_count", 0) > 0


def test_j_returned_bundles_have_explainable_ranking(search):
    for tier, rows in search["package_options"].items():
        for ev in rows:
            assert ev.get("rank")
            assert ev.get("ranking_rule")
            assert ev.get("bundle_reasoning", {}).get("ranking")
            assert ev.get("why_outranked") is not None
            assert ev.get("why_selected")


def test_k_budget_excludes_invalid_essential_balanced(demo_repo):
    open_search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    cheap = min(ev["monthly_cost"] for ev in open_search["package_options"]["essential"])
    capped = run_package_search(
        candidates=load_candidate_products(demo_repo, 30.0),
        profile=_dolly(monthly_budget=cheap),
    )
    for ev in capped["package_options"]["essential"] + capped["package_options"]["balanced"]:
        assert ev["monthly_cost"] <= cheap + 1e-6
        assert ev["budget_status"] == "WITHIN_BUDGET"


def test_l_optimal_ignores_customer_budget_ceiling(demo_repo):
    open_search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    cheap = min(ev["monthly_cost"] for ev in open_search["package_options"]["essential"])
    capped = run_package_search(
        candidates=load_candidate_products(demo_repo, 30.0),
        profile=_dolly(monthly_budget=cheap),
    )
    assert capped["provenance"]["tier_semantics"]["optimal"]["budget_is_hard_ceiling"] is False
    assert capped["package_options"]["optimal"]
    assert any(ev["monthly_cost"] > cheap for ev in capped["package_options"]["optimal"]) or all(
        ev["monthly_cost"] <= cheap for ev in open_search["package_options"]["optimal"]
    )


def test_m_optimal_still_respects_nutrient_maximums(search):
    for ev in search["package_options"]["optimal"]:
        assert not ev.get("exceeded_maximums")
        for row in ev["nutrient_rows"]:
            if row.get("maximum_specified") and row.get("actual") is not None:
                assert float(row["actual"]) <= float(row["allowed_maximum"]) + 1e-9


def test_n_breed_specific_pathways_appear_in_balanced_optimal(search):
    assert "joint" in search["care_priorities"]
    assert "skin" in search["care_priorities"]
    for tier in ("balanced", "optimal"):
        covered = {p["pathway"] for ev in search["package_options"][tier] for p in ev.get("preventative_pathways") or []}
        assert "joint" in covered or "skin" in covered


def test_o_no_breed_specific_disease_diagnosis_is_claimed(search, demo_client: TestClient):
    assert search["care_model"].get("diagnosis_claim") is False
    blob = str(search["care_model"]).lower()
    for phrase in DIAGNOSIS_PHRASES:
        assert phrase not in blob
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly_json()).json()
    briefing = str(body["roles"]["customer"]["preventative_briefing"]).lower()
    for phrase in DIAGNOSIS_PHRASES:
        assert phrase not in briefing
    assert body["roles"]["customer"]["preventative_briefing"]["diagnosis_claim"] is False


def test_p_frontend_displays_product_names_rather_than_sku_ids():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    customer = js[js.index("function renderCustomer") : js.index("function renderGroomer")]
    assert "productNamesLine" in customer or "productListHtml" in js
    assert "product_name" in js
    options = js[js.index("function renderOptions") : js.index("function renderCompare")]
    assert "product_ids || []).join" not in options
    assert "Nutrition Facts" in options or "View nutrition" in options
    assert "Why this bundle" in options
    assert "data-open-nutrition" in js


def test_q_nutrition_table_marks_only_modeled_preventative_nutrients(search):
    stars = set(search["care_model"].get("star_nutrients") or [])
    for ev in search["package_options"]["balanced"]:
        for row in ev["nutrient_rows"]:
            if row.get("breed_recommended"):
                assert row["nutrient"] in stars
            else:
                assert row["nutrient"] not in stars or not row.get("star")
    for ev in search["package_options"]["essential"]:
        assert all(not row.get("breed_recommended") for row in ev["nutrient_rows"])


def test_r_same_bundle_ids_across_roles(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly_json()).json()
    roles = body["roles"]

    def ids(options):
        out = []
        for tier in ("essential", "balanced", "optimal"):
            out.extend([row["bundle_id"] for row in (options or {}).get(tier) or []])
        return out

    customer = ids(roles["customer"]["wellness"]["package_options"])
    groomer = ids(roles["groomer"]["package_options"])
    business = ids(roles["business"]["portfolio"]["package_options"])
    developer = ids(roles["developer"]["package_optimization"]["package_options"])
    assert customer and customer == groomer == business == developer


def test_s_role_switching_does_not_trigger_another_engine_run():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    start = js.index("function switchRole")
    end = js.index("function emptyState")
    body = js[start:end]
    assert "fetch(" not in body
    assert "runAnalysis" not in body


def test_t_no_frontend_hardcoded_sku_product_or_breed_reasoning():
    for path in (WORKBENCH_JS, WORKBENCH_HTML, WORKBENCH_CSS):
        text = path.read_text(encoding="utf-8")
        for sku in FORBIDDEN_SKUS:
            assert sku not in text
        assert "Demo Fresh Beef Bowl" not in text
        assert "Demo Fresh Chicken Bowl" not in text
        assert "Labs have joint" not in text
        assert "your dog has" not in text.lower()
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "preventative_briefing" in js
    assert "health-analysis" in js
    assert demo_product_ids()


def test_customer_projection_exposes_names_briefing_and_reasoning(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly_json()).json()
    customer = body["roles"]["customer"]
    opt = customer["wellness"]["package_options"]["balanced"][0]
    assert opt["display_product_names"]
    assert all(name not in FORBIDDEN_SKUS for name in opt["display_product_names"])
    assert opt["products"][0]["product_name"]
    assert opt["bundle_reasoning"]["baseline_nutrition"]
    assert customer["preventative_briefing"]["pathways"]
    assert customer["health_analysis"]["anchor"] == "health-analysis"
    facts = opt["nutrition_facts"]
    assert any(row.get("status_label") for row in facts)
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert 'id="nutrition-modal"' in html
    assert "workbench.css?v=" in html
    assert "workbench.js?v=" in html
