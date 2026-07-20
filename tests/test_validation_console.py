"""Phase 5 Validation Console — observatory payload tests."""

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.clinical_assessment import build_clinical_assessment
from app.data.validation_console import NOT_TRACEABLE, build_validation_console, console_to_markdown
from app.inference.formula_registry import FORMULA_REGISTRY, FORMULA_RISK


@pytest.fixture
def dolly():
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
    repo = DataRepository("data")
    assessment = build_clinical_assessment(repo, analyze)
    return repo, analyze, assessment


def test_analyze_debug_observatory(dolly):
    _, analyze, _ = dolly
    debug = analyze.get("debug") or {}
    assert debug.get("schema") == "analyze_debug.v3"
    assert debug.get("risk_traces")
    assert debug.get("formula_executions")
    assert debug.get("provenance_index") is not None
    assert debug.get("decision_ledger") is not None
    assert debug.get("stage_timings_ms")
    assert "health_risk" in debug["stage_timings_ms"]
    assert "total_pipeline" in debug["stage_timings_ms"]
    first = debug["risk_traces"][0]
    assert first.get("steps")
    assert any(s.get("traceable") for s in first["steps"])
    # Applied modifiers present; activity/weight/climate marked not applied
    statuses = {s.get("status") for s in first["steps"]}
    assert "NOT_APPLIED_IN_RISK_V2_1" in statuses
    # At least one RISK + one NUTRIENT or PACKAGE execution
    fids = {fx.get("formula_id") for fx in debug["formula_executions"] if isinstance(fx, dict)}
    assert FORMULA_RISK in fids
    fx = next(fx for fx in debug["formula_executions"] if fx.get("formula_id") == FORMULA_RISK)
    assert fx.get("schema") == "formula_execution.v2"
    assert fx.get("steps")
    assert fx.get("confidence") or fx.get("confidence_steps")
    assert any(s.get("before") is not None or s.get("after") is not None for s in fx["steps"])
    assert fx.get("outputs", {}).get("final_risk_percent") is not None
    lookups = fx.get("lookups") or []
    assert lookups
    assert any(lu.get("csv_row") not in (None, "") for lu in lookups)
    assert any(lu.get("row_id") for lu in lookups)


def test_validation_console_v5_schema(dolly):
    repo, analyze, assessment = dolly
    doc = build_validation_console(repo, analyze, assessment, raw_request={"name": "Dolly"})
    assert doc["schema"] == "validation_console.v7"
    assert doc.get("single_page") is True
    assert doc.get("primary_view") == "developer_report"
    assert doc["nav"][0]["id"] == "s0"
    assert doc["formula_executions"]
    assert len(doc["formula_registry"]) == len(FORMULA_REGISTRY)
    first_fx = next(fx for fx in doc["formula_executions"] if fx.get("formula_id") == FORMULA_RISK)
    assert first_fx.get("steps")
    assert first_fx.get("lookups")


def test_risk_ledger_uses_observatory(dolly):
    repo, analyze, assessment = dolly
    doc = build_validation_console(repo, analyze, assessment)
    assert doc["risk_ledgers"]
    first = doc["risk_ledgers"][0]
    chain = first.get("expanded_chain") or first.get("steps") or []
    assert any(s.get("traceable") and s.get("op") in ("baseline", "multiply", "set") for s in chain)
    assert first.get("complete") is True
    assert first.get("formula_execution")
    explain = doc["explain_why"][0]
    assert explain.get("complete_modifier_chain") is True
    assert explain.get("formula_execution")


def test_package_rejects_visible(dolly):
    repo, analyze, assessment = dolly
    doc = build_validation_console(repo, analyze, assessment)
    products = doc["products"]
    assert isinstance(products.get("rejected"), list)
    tiers = (doc["packages"] or {}).get("tiers") or []
    assert tiers
    # At least one tier should expose rejected list (may be empty for tiny catalogs)
    assert "removed_products" in tiers[0]


def test_stage_timings_on_performance(dolly):
    repo, analyze, assessment = dolly
    doc = build_validation_console(repo, analyze, assessment)
    perf = doc["performance"]
    assert isinstance(perf.get("stage_timings_ms"), dict)
    assert perf["stage_timings_ms"].get("health_risk") is not None
    timeline = doc["pipeline_timeline"]
    risk_row = next((t for t in timeline if t.get("id") == "health_risk"), None)
    assert risk_row is not None
    assert risk_row["elapsed_ms"] != NOT_TRACEABLE


def test_markdown_export(dolly):
    repo, analyze, assessment = dolly
    doc = build_validation_console(repo, analyze, assessment)
    md = console_to_markdown(doc)
    assert "Formula explorer" in md
    assert "Formula executions" in md
    assert "Package rejects" in md
