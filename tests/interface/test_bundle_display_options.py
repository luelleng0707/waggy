"""Display truncation is not the valid-combination universe."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.agent.package_optimizer import load_candidate_products
from app.agent.package_search import OPTIONS_PER_TIER, PACKAGE_DISPLAY_LIMIT, run_package_search
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.api.main import app
from app.core.paths import clinical_root_str
from app.data.demo_catalog import demo_product_ids


ROOT = Path(__file__).resolve().parents[2]


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


def test_display_counts_are_not_valid_counts(demo_repo):
    search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    prov = search["provenance"]
    assert prov["evaluated_count"] == 4095
    assert prov["valid_count"] > PACKAGE_DISPLAY_LIMIT
    assert prov["non_dominated_count"] <= prov["valid_count"]
    assert prov["dominance_is_display_filter"] is False
    for tier in ("essential", "balanced", "optimal"):
        valid_n = prov["tier_valid_counts"][tier]
        shown = len(search["package_options"][tier])
        assert shown <= valid_n
        assert shown <= OPTIONS_PER_TIER
        assert shown == prov["displayed_count"][tier]
        assert valid_n >= shown
        assert valid_n > shown or valid_n <= OPTIONS_PER_TIER


def test_bundle_ids_unique_and_in_catalog(demo_repo):
    search = run_package_search(candidates=load_candidate_products(demo_repo, 30.0), profile=_dolly())
    catalog = demo_product_ids()
    for tier, rows in search["package_options"].items():
        ids = [ev["bundle_id"] for ev in rows]
        assert len(ids) == len(set(ids))
        for ev in rows:
            assert ev["optimizer_version"] == "PACKAGE_OPTIMIZER_V2_1"
            for pid in ev["product_ids"]:
                assert pid in catalog
            assert ev["search_provenance"]["evaluated_count"] == 4095


def test_surfaces_share_displayed_bundle_ids(demo_env):
    client = TestClient(app)
    body = client.post(
        "/api/v1/presentation/workbench",
        json={
            "name": "Dolly",
            "pet_name": "Dolly",
            "breeds": ["Labrador Retriever", "Golden Retriever"],
            "birthday": "2021-04-15",
            "weight": 30,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Outdoor",
            "correlation_id": "omega10-display-001",
        },
    )
    assert body.status_code == 200
    payload = body.json()
    cust = payload["roles"]["customer"]["wellness"]["package_options"]
    gro = payload["roles"]["groomer"]["package_options"]
    biz = payload["roles"]["business"]["portfolio"]["package_options"]
    dev = payload["roles"]["developer"]["package_optimization"]["package_options"]
    stats = payload["roles"]["customer"]["wellness"]["package_search"]
    assert stats["evaluated_count"] == 4095
    assert stats["valid_count"] > stats["display_limit"]
    for tier in ("essential", "balanced", "optimal"):
        cids = [row["bundle_id"] for row in cust[tier]]
        assert cids
        assert cids == [row["bundle_id"] for row in gro[tier]]
        assert cids == [row["bundle_id"] for row in biz[tier]]
        assert cids == [row["bundle_id"] for row in dev[tier]]
        assert len(cids) == len(set(cids))
        for row in cust[tier]:
            assert "nutrient_rows" not in row
            assert row.get("nutrition_facts")
            assert row.get("nutrition_ledger")
        assert len(cids) <= stats["tier_valid_counts"][tier]


def test_frontend_does_not_generate_packages():
    js = (WORKBENCH_JS).read_text(encoding="utf-8")
    assert "SF001" not in js
    assert "SF002" not in js
    assert "TR007" not in js
    assert "4095" not in js
    assert "2 ** " not in js
    assert "package_options" in js
    py = (ROOT / "app" / "agent" / "package_search.py").read_text(encoding="utf-8")
    assert "openai" not in py.lower()
    assert "gemini" not in py.lower()
