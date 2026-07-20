"""Phase 4 knowledge graph & explainability tests."""

from __future__ import annotations

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.data.repository import DataPlatform
from app.data.warehouse.parity import stable_hash
from app.science.audit import ScientificAudit
from app.science.builder import KnowledgeGraphBuilder
from app.science.confidence import build_confidence_bundle
from app.science.coverage import KnowledgeCoverageReport
from app.science.diff_engine import ScientificDiffEngine
from app.science.explanations import build_formula_explanations, build_recommendation_chain
from app.science.repository import GraphRepository
from app.science.validator import DataValidator
from app.science.versioning import current_science_versions


@pytest.fixture(scope="module")
def platform() -> DataPlatform:
    return DataPlatform("data", strict=True)


@pytest.fixture(scope="module")
def graph_repo(platform: DataPlatform) -> GraphRepository:
    return GraphRepository.from_platform(platform)


def test_knowledge_graph_builds(platform: DataPlatform):
    g = KnowledgeGraphBuilder(platform).build()
    assert g.summary()["nodes"] > 10
    assert g.summary()["edges"] > 10
    assert g.by_type("condition")
    assert g.by_type("paper")


def test_graph_repository_condition(graph_repo: GraphRepository):
    hit = graph_repo.condition("Hip Dysplasia")
    assert hit is not None
    assert hit["type"] == "condition"
    assert hit["outgoing"] or hit["incoming"]


def test_why_reverse_lookup(graph_repo: GraphRepository):
    why = graph_repo.why("Glucosamine", kind="ingredient")
    assert why["found"] is True
    assert why["paths"] or why["evidence"]


def test_evidence_objects(platform: DataPlatform):
    ev = KnowledgeGraphBuilder(platform).evidence_objects()
    assert ev
    assert ev[0].id.startswith("EV_")


def test_confidence_dimensions():
    bundle = build_confidence_bundle(
        execution_ok=True,
        evidence_rows=[{"paper_id": "P1", "confidence": "high"}],
        coverage={"has_papers": True, "has_ingredients": True, "has_foods": False, "has_products": False, "has_prevention": False},
    )
    assert bundle["execution"]["percent"] == 100.0
    assert bundle["study_quality"]["grade"] == "A"
    assert "recommendation" in bundle


def test_formula_and_chain_explanations():
    fx = build_formula_explanations("RISK_V2_1")
    assert fx["developer"]["expression"]
    chain = build_recommendation_chain(
        condition="Hip Dysplasia",
        breed="Golden Retriever",
        ingredient="Omega-3",
        paper={"paper_id": "PAPER_x", "title": "Study"},
    )
    assert "Hip Dysplasia" in chain["render"]


def test_coverage_and_audit(platform: DataPlatform):
    g = KnowledgeGraphBuilder(platform).build()
    cov = KnowledgeCoverageReport(g).build()
    assert cov["conditions"] >= 1
    audit = ScientificAudit(platform).build()
    assert "versions" in audit
    assert audit["graph"]["nodes"] >= 1


def test_validator(platform: DataPlatform):
    report = DataValidator(platform).validate()
    assert "ok" in report
    assert "stats" in report


def test_diff_engine(platform: DataPlatform):
    g1 = KnowledgeGraphBuilder(platform).build()
    g2 = KnowledgeGraphBuilder(platform).build()
    diff = ScientificDiffEngine().diff_graphs(g1, g2)
    assert diff["added_edges"] == 0
    assert diff["removed_edges"] == 0
    effect = ScientificDiffEngine().diff_effect_size(subject="Omega-3", before=0.2, after=0.28)
    assert effect["delta"] == pytest.approx(0.08)


def test_versions():
    v = current_science_versions()
    assert v.algorithm
    assert v.knowledge_graph == "4.0.0"


@pytest.mark.asyncio
async def test_analyze_includes_science_additive():
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
    analyze = await PPIEWellnessAgent("data").generate_reproducible_report(profile)
    assert analyze.get("healthInsights")
    assert (analyze.get("debug") or {}).get("science")
    assert analyze.get("scientificExplainability")
    # Clinical fingerprint still present
    assert stable_hash({"r": [h.get("title") for h in analyze["healthInsights"]]})
