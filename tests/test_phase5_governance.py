"""Phase 5 governance tooling — must not change clinical outputs."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.data.warehouse.parity import stable_hash
from science_pipeline.ingestion.provenance import PROVENANCE_COLUMNS, REVIEW_STATUSES
from science_pipeline.publishing.release_ops import default_release_metadata, release_id
from science_pipeline.validation.extended import ExtendedScienceValidator
from science_pipeline.validation.impact import ScientificImpactAnalyzer
from developer_tools.research.queries import ResearchAssistant
from developer_tools.dashboards.generators import generate_formula_stability, generate_data_health


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def dog() -> DogProfileInput:
    return DogProfileInput(
        name="Phase5Parity",
        primary_breed="Labrador Retriever",
        age_years=5.0,
        weight_kg=28.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )


def test_provenance_schema_complete():
    assert "created_by" in PROVENANCE_COLUMNS
    assert "review_status" in PROVENANCE_COLUMNS
    assert "draft" in REVIEW_STATUSES
    assert "production" in REVIEW_STATUSES


def test_release_metadata_flags_clinical_unchanged():
    meta = default_release_metadata(version=release_id(), author="test")
    assert meta["clinical_formulas_changed"] is False
    assert meta["recommendation_logic_changed"] is False
    assert "validation_status" in meta


def test_extended_validator_runs():
    result = ExtendedScienceValidator().validate()
    assert "ok" in result
    assert "sections" in result
    assert "evidence" in result["sections"]
    assert "biology" in result["sections"]
    assert "graph" in result["sections"]


def test_impact_analyzer_glucosamine():
    report = ScientificImpactAnalyzer().analyze(
        entity_type="ingredient",
        entity_id="Glucosamine",
        field="dose",
        old_value=800,
        new_value=900,
    )
    assert "affected_formulas" in report
    assert "counts" in report


def test_research_assistant_condition_query():
    rows = ResearchAssistant().papers_by_condition("Hip")
    assert isinstance(rows, list)


def test_doc_generators_write(tmp_path, monkeypatch):
    # write into tmp via monkeypatch of out paths
    stab = generate_formula_stability(out_dir=tmp_path)
    health = generate_data_health(out_dir=tmp_path)
    assert stab.exists()
    assert health.exists()


@pytest.mark.asyncio
async def test_clinical_hash_stable_under_governance_import(dog):
    """Importing Phase 5 modules must not alter AssessmentAgent clinical payload."""
    agent = PPIEWellnessAgent(data_dir="data")
    a = await agent.generate_reproducible_report(dog)
    from science_pipeline.validation.extended import ExtendedScienceValidator as EV

    EV()
    b = await agent.generate_reproducible_report(dog)
    assert stable_hash(a) == stable_hash(b)
