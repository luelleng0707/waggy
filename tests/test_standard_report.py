from app.core.paths import clinical_root_str, resolve_clinical_root
"""Standardized Clinical Report (schema v4) smoke tests."""

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.report_generator import build_standard_report
from app.data.report_schema import SCHEMA_VERSION, WIDGET_TYPES


EXPECTED_SECTIONS = {
    "summary",
    "breed_analysis",
    "trait_analysis",
    "environment_analysis",
    "risk_analysis",
    "nutrition_analysis",
    "activity_analysis",
    "package_analysis",
    "grooming_analysis",
}


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
def standard_report(dolly_profile):
    analyze = asyncio.run(
        PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(dolly_profile)
    )
    return analyze, build_standard_report(DataRepository(clinical_root_str()), analyze)


def test_standard_report_schema_and_sections(standard_report):
    _, report = standard_report
    assert report["schema_version"] == SCHEMA_VERSION
    assert report["algorithm_version"]
    assert report["data_version"]
    assert report["csv_hash"]
    assert report["generated_at"]
    ids = {s["id"] for s in report["sections"]}
    assert ids == EXPECTED_SECTIONS


def test_section_shape_and_widget_types(standard_report):
    _, report = standard_report
    for section in report["sections"]:
        assert set(section.keys()) >= {
            "id",
            "title",
            "priority",
            "summary",
            "score",
            "widgets",
            "references",
        }
        for widget in section["widgets"]:
            assert widget["type"] in WIDGET_TYPES


def test_package_and_product_nested_reports(standard_report):
    _, report = standard_report
    assert report["package_reports"]
    for tier, nested in report["package_reports"].items():
        assert nested["schema_version"] == SCHEMA_VERSION
        assert nested["sections"]
        assert nested.get("hero")
    # Product reports may be empty if analyze has no product analyses; if present, validate.
    for pid, nested in (report.get("product_reports") or {}).items():
        assert nested["schema_version"] == SCHEMA_VERSION
        assert nested["sections"]


def test_citations_never_invented(standard_report):
    _, report = standard_report
    for section in report["sections"]:
        for ref in section.get("references") or []:
            if ref.get("status") == "published":
                assert ref.get("source_url")
            else:
                assert "Awaiting" in (ref.get("label") or "") or ref.get("status") == "placeholder"
        for widget in section.get("widgets") or []:
            for ref in widget.get("references") or []:
                if ref.get("status") == "published":
                    assert ref.get("source_url")
