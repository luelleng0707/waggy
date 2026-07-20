"""Clinical Report V3 builder smoke tests."""

import asyncio

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.clinical_report_builder import build_clinical_report


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


def test_clinical_report_has_fourteen_sections(dolly_profile):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(dolly_profile))
    report = build_clinical_report(DataRepository("data"), analyze)
    assert report["version"] == "3.0.0"
    assert len(report["sections"]) == 14
    ids = {s["id"] for s in report["sections"]}
    assert ids == {f"s{i}" for i in range(1, 15)}


def test_biological_profile_from_csv(dolly_profile):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(dolly_profile))
    report = build_clinical_report(DataRepository("data"), analyze)
    s1 = next(s for s in report["sections"] if s["id"] == "s1")
    assert len(s1["cards"]) >= 1
    card = s1["cards"][0]
    assert card["derived_from"]["source_csv"]
    assert card["explanation"]


def test_evidence_placeholder_when_no_url(dolly_profile):
    analyze = asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(dolly_profile))
    report = build_clinical_report(DataRepository("data"), analyze)
    s7 = next(s for s in report["sections"] if s["id"] == "s7")
    placeholders = [i for i in s7["items"] if i["citation"]["status"] == "placeholder"]
    published = [i for i in s7["items"] if i["citation"]["status"] == "published"]
    assert published or placeholders
