"""Phase 6 authoring — clinical engine untouched."""

from __future__ import annotations

from app.core.paths import clinical_root_str, resolve_clinical_root

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.data.warehouse.parity import stable_hash
from authoring.models import EvidenceDraft, save_draft, write_templates
from authoring.builder import validate_draft, create_evidence_interactive, materialize_draft
from ontology import condition_path, ingredient_path, export_ontology_artifacts
from curation.evidence_ranking import score_study_type
from curation.conflict_resolution import detect_conflicts
from curation.duplicate_detection import suggest_condition_duplicates


def test_templates_and_draft_validation():
    write_templates()
    draft = EvidenceDraft(
        paper_title="Test paper",
        conditions=["Hip Dysplasia"],
        ingredients=["Omega-3"],
        study_type="rct",
        year=2024,
        author="test",
    )
    path = save_draft(draft)
    assert path.exists()
    v = validate_draft(draft)
    assert v["ok"] is True
    assert v["evidence_quality_score"] >= 90


def test_evidence_builder_staging_only(tmp_path):
    out = create_evidence_interactive(
        {
            "paper_title": "Staging EPA study",
            "year": 2023,
            "study_type": "observational",
            "conditions": ["Hip Dysplasia"],
            "ingredients": ["EPA"],
            "author": "test",
            "submit": True,
        }
    )
    assert out["validation"]["ok"] is True
    assert out["materialize"]["published"] is True
    assert "authoring_staging" in out["materialize"]["staging_dir"]
    # live clinical evidence must remain loadable via formula projection
    from pathlib import Path
    from app.data.repository import DataPlatform

    plat = DataPlatform(clinical_root_str(), strict=True)
    assert "clinical_evidence_base" in plat._tables
    assert not plat._tables["clinical_evidence_base"].empty


def test_ontology_paths():
    assert "Musculoskeletal" in condition_path("Hip Dysplasia")
    assert "Lipid" in ingredient_path("EPA")
    paths = export_ontology_artifacts()
    assert "conditions" in paths


def test_ranking_and_curation_run():
    assert score_study_type("meta-analysis")["score"] == 100
    assert isinstance(detect_conflicts(), list)
    assert isinstance(suggest_condition_duplicates(), list)


def test_authoring_apis():
    client = TestClient(app)
    h = {"x-api-key": "wagtopia-demo-key"}
    assert client.get("/api/v1/authoring/ontology", headers=h).status_code == 200
    assert client.get("/api/v1/authoring/conflicts", headers=h).status_code == 200
    assert client.get("/api/v1/research/condition/Hip%20Dysplasia", headers=h).status_code == 200
    assert client.get("/api/v1/research/gaps", headers=h).status_code == 200


@pytest.mark.asyncio
async def test_clinical_unchanged_by_phase6():
    agent = PPIEWellnessAgent(data_dir=clinical_root_str())
    dog = DogProfileInput(
        name="P6Parity",
        primary_breed="Labrador Retriever",
        age_years=5.0,
        weight_kg=28.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )
    a = await agent.generate_reproducible_report(dog)
    from authoring.portal import ResearchPortal

    ResearchPortal().evidence_for_condition("Hip Dysplasia")
    b = await agent.generate_reproducible_report(dog)
    assert stable_hash(a) == stable_hash(b)
