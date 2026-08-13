from app.core.paths import clinical_root_str, resolve_clinical_root
"""Phase 21 EngineTrace — debug-gated calculation audit (no formula changes)."""

import asyncio
import os

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.clinical_assessment import build_clinical_assessment
from app.debug.clinical_execution_debug import (
    build_engine_trace,
    is_engine_debug,
    run_consistency_checks,
)


@pytest.fixture
def dolly_analyze():
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
    return asyncio.run(PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(profile))


def test_debug_flag_env(monkeypatch):
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    monkeypatch.delenv("DEBUG_ENGINE", raising=False)
    assert is_engine_debug() is False
    monkeypatch.setenv("PPIE_DEBUG", "true")
    assert is_engine_debug() is True
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    assert is_engine_debug(request_debug=True) is True


def test_engine_trace_sections(dolly_analyze):
    repo = DataRepository(clinical_root_str())
    assessment = build_clinical_assessment(repo, dolly_analyze)
    trace = build_engine_trace(repo, dolly_analyze, assessment, timings={"analyze": 1.0})
    assert trace["schema"] == "engine_trace.v1"
    assert trace["equation_policy"] == "formula_id_only"
    assert trace["debug"] is True
    for key in (
        "profile",
        "breed",
        "traits",
        "risks",
        "nutrition",
        "activity",
        "grooming",
        "products",
        "packages",
        "evidence",
        "validation",
    ):
        assert key in trace["sections"]
        sec = trace["sections"][key]
        assert sec.get("formula_id")
        assert sec.get("equation_exposed") is False
    risks = trace["sections"]["risks"]["outputs"]["risks"]
    assert risks
    assert risks[0]["formula_id"] == "RISK_V2_1"
    assert "final_risk_percent" in risks[0]["outputs"]
    # Must not invent proprietary equation strings
    blob = str(trace)
    assert "risk =" not in blob.lower() or "formula_id" in blob


def test_consistency_checks_run(dolly_analyze):
    warnings = run_consistency_checks(dolly_analyze, None)
    assert isinstance(warnings, list)
