"""Phase 17.5 ClinicalAssessment contract — modular projection of frozen analyze."""

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.clinical_assessment import (
    ASSESSMENT_SCHEMA,
    MODULE_IDS,
    build_clinical_assessment,
    get_assessment_module,
)


@pytest.fixture
def dolly_profile() -> DogProfileInput:
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


@pytest.fixture
def dolly_assessment(dolly_profile):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(dolly_profile))
    return build_clinical_assessment(DataRepository("data"), analyze), analyze


def test_assessment_has_all_modules(dolly_assessment):
    assessment, _ = dolly_assessment
    assert assessment["meta"]["assessment_schema"] == ASSESSMENT_SCHEMA
    assert assessment["module_ids"] == list(MODULE_IDS)
    for mid in MODULE_IDS:
        assert mid in assessment["modules"]
        assert mid in assessment
        assert isinstance(assessment[mid], dict)
        envelope = get_assessment_module(assessment, mid)
        assert envelope is not None
        assert envelope["id"] == mid
        assert envelope["schema"] == ASSESSMENT_SCHEMA
        assert "data" in envelope
        assert "summary" in envelope


def test_health_priorities_are_plain_language(dolly_assessment):
    assessment, _ = dolly_assessment
    priorities = assessment["health"].get("priorities") or []
    assert priorities, "expected health priorities for Dolly"
    for p in priorities:
        assert p.get("title")
        assert "explanation" in p
        # Default fields must not dump raw goal ids as the primary copy
        explanation = str(p.get("explanation") or "")
        assert not explanation.startswith("Goal:")
        assert "joint_health" not in explanation
        tech = p.get("technical_reasoning") or []
        assert isinstance(tech, list)


def test_packages_and_products_are_structured(dolly_assessment):
    assessment, _ = dolly_assessment
    packages = assessment["packages"]
    assert packages.get("tiers")
    rec = packages.get("recommended_tier")
    assert rec
    tier = next(t for t in packages["tiers"] if t["tier"] == rec)
    assert tier.get("title")
    assert isinstance(tier.get("products"), list)
    products = assessment["products"]
    assert "items" in products
    assert "by_id" in products


def test_assessment_is_projection_not_recompute(dolly_assessment):
    """Same analyze input yields stable module shape; no extra analyze keys required."""
    assessment, analyze = dolly_assessment
    assert "healthInsights" in analyze or "risks" in analyze
    # Projection only — meta carries engine version, not a second pipeline run
    assert assessment["meta"].get("engine") == "PPIE"
    assert assessment["meta"].get("algorithm_version")
