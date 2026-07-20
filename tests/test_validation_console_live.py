"""Phase 22 live Validation Console — presets, repo browser, compare."""

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.assessment_diff import compare_analyses
from app.data.clinical_assessment import build_clinical_assessment
from app.data.debug_boot import developer_banner
from app.data.debug_presets import DEFAULT_PRESET_ID, get_preset_body, list_presets
from app.data.debug_repository_browser import list_repository_tables, preview_table
from app.data.validation_console import NOT_TRACEABLE, build_validation_console


@pytest.fixture
def repo():
    return DataRepository("data")


def test_presets_cover_requested_dogs():
    labels = {p["label"] for p in list_presets()}
    for need in (
        "Golden Retriever",
        "German Shepherd",
        "Border Collie",
        "French Bulldog",
        "Mixed Breed",
        "Senior Labrador",
        "Large Breed Puppy",
    ):
        assert need in labels
    body = get_preset_body(DEFAULT_PRESET_ID)
    assert body["name"] == "Dolly"


def test_repository_browser_read_only(repo):
    cat = list_repository_tables(repo)
    assert cat["read_only"] is True
    assert cat["tables"]
    table = cat["tables"][0]["table"]
    prev = preview_table(repo, table, limit=5)
    assert prev["read_only"] is True
    assert prev["rows"] is not None


def test_compare_golden_weight_delta(repo):
    left_body = get_preset_body("golden_20kg")
    right_body = get_preset_body("golden_25kg")

    async def run():
        agent = PPIEWellnessAgent(data_dir="data")
        left_p = DogProfileInput(
            name=left_body["name"],
            primary_breed=left_body["breeds"][0],
            age_years=5.0,
            weight_kg=float(left_body["weight"]),
            activity_level=left_body["activity_level"],
            current_environment=left_body["current_environment"],
        )
        right_p = DogProfileInput(
            name=right_body["name"],
            primary_breed=right_body["breeds"][0],
            age_years=5.0,
            weight_kg=float(right_body["weight"]),
            activity_level=right_body["activity_level"],
            current_environment=right_body["current_environment"],
        )
        left = await agent.generate_reproducible_report(left_p)
        right = await agent.generate_reproducible_report(right_p)
        return left, right

    left, right = asyncio.run(run())
    diff = compare_analyses(
        left, right, left_raw=left_body, right_raw=right_body, left_label="20kg", right_label="25kg"
    )
    assert diff["schema"] == "assessment_compare.v1"
    assert any(d["field"] == "weight_kg" for d in diff["input_deltas"])
    for ch in diff["changes"]:
        why = ch.get("why") or {}
        if why.get("modifier_chain"):
            assert why["modifier_chain"] == NOT_TRACEABLE


def test_banner_text():
    text = developer_banner()
    assert "Validation Console" in text
    assert "/debug/calculation" in text
    assert "Engine Trace" in text


def test_debug_gate_403_without_flag(monkeypatch):
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    monkeypatch.delenv("DEBUG_ENGINE", raising=False)
    monkeypatch.delenv("PPIE_DEV_BOOT", raising=False)
    from fastapi.testclient import TestClient

    from app.data.engine_trace import is_engine_debug

    assert is_engine_debug() is False
    from app.api import main as api_main

    client = TestClient(api_main.app)
    r = client.post(
        "/api/v1/ppie/validation-console",
        headers={"x-api-key": "wagtopia-demo-key"},
        json={
            "name": "x",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-01-01",
            "weight": 10,
            "activity_level": "High",
            "current_environment": "Temperate Suburban",
        },
    )
    assert r.status_code == 403
    r2 = client.get("/debug/calculation")
    assert r2.status_code in (403, 302)


def test_console_nav_includes_compare_and_repo(repo):
    profile = DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=4.3,
        weight_kg=30.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )
    analyze = asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(profile))
    assessment = build_clinical_assessment(repo, analyze)
    doc = build_validation_console(repo, analyze, assessment)
    ids = {n["id"] for n in doc["nav"]}
    assert "repository" in ids
    assert "compare" in ids
    assert "formulas" in ids
    assert "graph" in ids
    assert doc["schema"] == "validation_console.v3"
    assert "reverse" in ids
