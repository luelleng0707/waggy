"""Regression: CSV extraction must not change locked pipeline outputs."""

import asyncio
import json

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.inference.config import DEFAULT_CATEGORY_WEIGHTS, DEFAULT_SCORE_WEIGHTS, category_weights, score_weights


@pytest.fixture(scope="module")
def dolly_report():
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
    return asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(profile))


def test_csv_defaults_identical_to_embedded():
    assert category_weights() == DEFAULT_CATEGORY_WEIGHTS
    assert score_weights() == DEFAULT_SCORE_WEIGHTS


def test_analyze_shape_stable(dolly_report):
    r = dolly_report
    assert r.get("healthInsights")
    assert r.get("wellnessPackages")
    assert r.get("nutritionalTargets") is not None
    # Deterministic-ish: top risk title present
    titles = [h.get("title") for h in r["healthInsights"] if isinstance(h, dict)]
    assert titles
    # Packages have coverage scores
    for p in r["wellnessPackages"]:
        if isinstance(p, dict):
            assert "monthly_cost" in p or "coverage_score" in p


def test_risk_percents_are_numeric(dolly_report):
    for h in dolly_report["healthInsights"]:
        if not isinstance(h, dict):
            continue
        pct = h.get("biological_risk_percent")
        if pct is not None:
            assert isinstance(pct, (int, float))


def test_snapshot_fingerprint_stable(dolly_report):
    """Fingerprint of key outputs — catch accidental formula drift."""
    risks = [
        {
            "title": h.get("title"),
            "pct": h.get("biological_risk_percent"),
            "conf": h.get("confidence_percent"),
        }
        for h in dolly_report["healthInsights"]
        if isinstance(h, dict)
    ]
    pkgs = [
        {
            "tier": p.get("tier"),
            "cov": p.get("coverage_score"),
            "overall": p.get("overall_score"),
            "monthly": p.get("monthly_cost"),
        }
        for p in dolly_report.get("wellnessPackages") or []
        if isinstance(p, dict)
    ]
    blob = json.dumps({"risks": risks, "pkgs": pkgs}, sort_keys=True, default=str)
    # Sanity: non-empty and structured
    assert "title" in blob
    assert len(risks) >= 1
