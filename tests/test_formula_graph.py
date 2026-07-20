"""Phase 3 FormulaGraph / AssessmentAgent tests."""

from __future__ import annotations

import asyncio

import pytest

from app.agent.assessment_agent import AssessmentAgent
from app.agent.engine import PPIEWellnessAgent
from app.agent.formula_graph import FormulaGraph
from app.agent.formula_registry import FORMULA_REGISTRY, list_formulas
from app.agent.nodes import default_nodes
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, bootstrap
from app.data.warehouse.parity import stable_hash


@pytest.fixture(scope="module")
def repo() -> DataRepository:
    bootstrap("data", strict=True)
    return DataRepository("data")


@pytest.fixture
def dolly() -> DogProfileInput:
    return DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=4.3,
        weight_kg=30.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )


def test_formula_registry_has_risk():
    assert "RISK_V2_1" in FORMULA_REGISTRY
    assert "EXPORT_LEGACY_V1" in list_formulas()


def test_graph_toposort_deterministic():
    g = FormulaGraph(default_nodes())
    a = g.order()
    b = g.order()
    assert a == b
    assert a[0] == "profile"
    assert a[-1] == "export"
    assert a.index("risk") < a.index("nutrition")
    assert a.index("product") < a.index("export")


def test_assessment_agent_returns_typed_result(repo: DataRepository, dolly: DogProfileInput):
    result = AssessmentAgent(repo).assess(dolly)
    assert result.legacy_json
    assert result.health.get("risks")
    assert result.trace.get("execution")
    assert result.trace.get("dependency_graph")
    assert result.validation.get("ok") is True
    assert len(result.trace["execution"]) == len(default_nodes())


@pytest.mark.asyncio
async def test_engine_delegates_to_formula_graph(dolly: DogProfileInput):
    agent = PPIEWellnessAgent("data")
    analyze = await agent.generate_reproducible_report(dolly)
    assert analyze.get("healthInsights")
    assert analyze.get("wellnessPackages")
    debug = analyze.get("debug") or {}
    assert debug.get("formula_graph", {}).get("order")
    assert len(debug.get("formula_execution_trace") or []) >= 10


@pytest.mark.asyncio
async def test_assess_matches_generate_hash(dolly: DogProfileInput):
    agent = PPIEWellnessAgent("data")
    via_assess = agent.assess(dolly).to_analyze_dict()
    via_gen = await agent.generate_reproducible_report(dolly)

    def clinical(d: dict) -> dict:
        return {
            "healthInsights": d.get("healthInsights"),
            "wellnessPackages": [
                {
                    "tier": p.get("tier"),
                    "coverage_score": p.get("coverage_score"),
                    "overall_score": p.get("overall_score"),
                    "monthly_cost": p.get("monthly_cost"),
                }
                for p in (d.get("wellnessPackages") or [])
                if isinstance(p, dict)
            ],
            "nutritionalTargets": d.get("nutritionalTargets"),
        }

    assert stable_hash(clinical(via_assess)) == stable_hash(clinical(via_gen))
