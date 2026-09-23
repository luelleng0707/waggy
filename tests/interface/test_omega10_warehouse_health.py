"""Ω10: warehouse Health Analysis, no synthetic breed-care fallback."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.api.main import app
from app.core.paths import clinical_root_str
from app.data.scientific_care import resolve_care_model


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def demo_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)


@pytest.fixture
def demo_repo(demo_env) -> DataRepository:
    return DataRepository(clinical_root_str())


def test_demo_breed_care_module_is_retired():
    from app.data.demo_breed_care import care_model_for_breeds

    with pytest.raises(RuntimeError, match="retired"):
        care_model_for_breeds(["Labrador Retriever"])


def test_developer_funnel_is_visible():
    js = (WORKBENCH_JS).read_text(encoding="utf-8")
    assert "wb-funnel" in js
    assert "structurally eligible" in js
    assert "minimum failures" in js
    assert "maximum failures" in js
    assert "non-dominated" in js


def test_warehouse_care_model_uses_intern_prevalence(demo_repo):
    model = resolve_care_model(demo_repo, ["Labrador Retriever", "Golden Retriever"])
    assert model["warehouse_evidence"] is True
    assert model["demo_synthetic"] is False
    assert "DEMO_SYNTHETIC" not in str(model.get("evidence_status"))
    records = model["condition_records"]
    names = {row["condition"] for row in records}
    assert "Hip Dysplasia" in names
    hip = next(row for row in records if row["condition"] == "Hip Dysplasia")
    percents = {item["breed"]: item["percent"] for item in hip["prevalence"]["observed_by_breed"]}
    assert percents["Labrador Retriever"] == 12.7
    assert percents["Golden Retriever"] == 14.9
    assert hip["scientific_quote"]
    assert "pmc.ncbi.nlm.nih.gov" in str(hip["paper_link"])
    assert "does not claim that a supplement reduces" in hip["preventative_implication"]


def test_resolve_care_model_does_not_use_demo_breed_care(demo_repo):
    empty = resolve_care_model(demo_repo, ["Unknown Breed X"], demo=True)
    assert empty["warehouse_evidence"] is False
    assert empty["demo_synthetic"] is False
    assert empty["pathways"] == []


def test_workbench_health_analysis_is_warehouse_backed(demo_env):
    client = TestClient(app)
    body = client.post(
        "/api/v1/presentation/workbench",
        json={
            "name": "Dolly",
            "breeds": ["Labrador Retriever", "Golden Retriever"],
            "birthday": "2021-04-15",
            "weight": 30,
            "activity_level": "Moderate",
            "current_environment": "Temperate Outdoor",
            "observed_conditions": ["joint_stiffness", "itching"],
        },
    ).json()
    report = body["roles"]["customer"]["health_analysis"]
    assert report["warehouse_status"] == "Warehouse evidence present"
    assert report["demo_synthetic"] is False
    labels = {row.get("condition") or row.get("label") for row in report["findings"]}
    assert "Hip Dysplasia" in labels
    hip = next(row for row in report["findings"] if row.get("condition") == "Hip Dysplasia")
    assert hip["paper_link"]
    assert hip["scientific_quote"]
    ids = []
    for role in ("customer", "groomer", "business", "developer"):
        options = (
            ((body["roles"][role].get("wellness") or {}).get("package_options"))
            or body["roles"][role].get("package_options")
            or ((body["roles"][role].get("portfolio") or {}).get("package_options"))
            or ((body["roles"][role].get("package_optimization") or {}).get("package_options"))
        )
        ids.append([row["bundle_id"] for tier in ("essential", "balanced", "optimal") for row in (options or {}).get(tier) or []])
    assert ids[0] and ids[0] == ids[1] == ids[2] == ids[3]


def test_nutrition_modal_is_not_inline_in_package_card():
    js = (WORKBENCH_JS).read_text(encoding="utf-8")
    html = (WORKBENCH_HTML).read_text(encoding="utf-8")
    assert "data-open-nutrition" in js
    assert "nutrition-modal" in html
    assert "wb-modal-backdrop" in html
    customer = js[js.index("function renderOptions") : js.index("function renderCompare")]
    assert "wb-facts-table" not in customer
    assert "View nutrition" in customer
    facts = js[js.index("function renderNutritionFacts") : js.index("function closeNutritionModal")]
    assert "currentRole === \"developer\"" in facts


def test_optimizer_attaches_condition_records(demo_repo):
    search = run_package_search(
        candidates=load_candidate_products(demo_repo, 30.0),
        profile=DogProfileInput(
            name="Dolly",
            primary_breed="Labrador Retriever",
            secondary_breed="Golden Retriever",
            current_environment="Temperate Outdoor",
            weight_kg=30,
            age_years=4.3,
        ),
        repo=demo_repo,
    )
    row = search["package_options"]["balanced"][0]
    assert row["care_pathway_records"]
    assert any(item.get("condition") == "Hip Dysplasia" for item in row["care_pathway_records"])
    assert row["bundle_reasoning"].get("health_fit")
