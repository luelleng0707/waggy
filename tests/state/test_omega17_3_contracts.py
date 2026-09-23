"""Ω17.3 recalculation provenance. No engine. No warehouse writes."""

from __future__ import annotations

from pathlib import Path

from app.state.recalculation import explain_from_envelopes, recommendation_snapshot
from app.state.version import (
    WAGGY_RECALCULATION_EXPLANATION_SCHEMA,
    WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA,
)

ROOT = Path(__file__).resolve().parents[2]


def _envelope(signature: str, *, products: list[dict], removed: list[str] | None = None) -> dict:
    exclusions = ["chicken"] if removed else []
    return {
        "analysis_signature": signature,
        "engine_version": "2.1.0",
        "effective_preferences": {
            "scientific": False,
            "ingredient_exclusions": exclusions,
            "monthly_budget": None,
        },
        "canonical": {
            "scientific_analysis": {
                "findings": [{"title": "Joints"}],
                "nutrient_targets": [{"nutrient": "protein", "min": 40, "max": 90}],
            },
            "package_optimization": {
                "package_options": {
                    "essential": [
                        {"bundle_id": "e1", "monthly_cost": 50, "products": products},
                    ],
                    "balanced": [
                        {"bundle_id": "b1", "monthly_cost": 80, "products": products},
                    ],
                    "optimal": [
                        {"bundle_id": "o1", "monthly_cost": 120, "products": products},
                    ],
                },
                "search": {
                    "preference_eligibility": {
                        "scientific": False,
                        "applied": bool(removed),
                        "ingredient_exclusions": exclusions,
                        "removed_product_ids": removed or [],
                        "removed": [
                            {"product_id": pid, "reason": "ingredient_exclusion:chicken"}
                            for pid in (removed or [])
                        ],
                    }
                },
            },
        },
    }


def test_recalculation_module_stays_outside_engine_and_warehouse():
    source = (ROOT / "app" / "state" / "recalculation.py").read_text(encoding="utf-8")
    assert "generate_reproducible_report" not in source
    assert "app.agent.engine" not in source
    assert "app.data.scientific_care" not in source
    assert "gemini" not in source.lower()
    assert "from app.ai" not in source
    assert "import warehouse" not in source


def test_chicken_exclusion_is_catalog_eligibility_not_science():
    previous = _envelope(
        "sig-a",
        products=[
            {"product_id": "SF001", "product_name": "Demo Fresh Beef Bowl"},
            {"product_id": "SF002", "product_name": "Demo Fresh Chicken Bowl"},
        ],
    )
    current = _envelope(
        "sig-b",
        products=[{"product_id": "SF001", "product_name": "Demo Fresh Beef Bowl"}],
        removed=["SF002"],
    )
    snap = recommendation_snapshot(current)
    assert snap["schema"] == WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA
    assert snap["scientific"] is False
    explanation = explain_from_envelopes(
        previous,
        current,
        preference_changes=[{"category": "ingredient_exclusion", "value": "chicken", "action": "added"}],
    )
    assert explanation["schema"] == WAGGY_RECALCULATION_EXPLANATION_SCHEMA
    assert explanation["llm_used"] is False
    assert explanation["scientific"] is False
    assert explanation["science_changed"] is False
    assert explanation["analysis_changed"] is True
    kinds = [item["kind"] for item in explanation["causes"]]
    assert "CATALOG_ELIGIBILITY" in kinds
    assert "SCIENCE_INPUT_CHANGE" not in kinds
    catalog = next(item for item in explanation["causes"] if item["kind"] == "CATALOG_ELIGIBILITY")
    assert catalog["scientific"] is False
    assert "SF002" in catalog["ineligible_product_ids"]
    assert explanation["recommendation_changes"]["balanced"]["removed_product_ids"] == ["SF002"]
    facts = " ".join(explanation["summary_facts"])
    assert "not a scientific finding" in facts.lower()
    assert "LLM did not select products" in facts
    assert "unchanged" in facts.lower()


def test_incomplete_previous_digest_does_not_invent_added_products():
    current = _envelope(
        "sig-b",
        products=[{"product_id": "SF001", "name": "Beef"}],
        removed=["SF002"],
    )
    from app.state.recalculation import explain_recalculation, recommendation_snapshot

    explanation = explain_recalculation(
        previous_snapshot=None,
        new_snapshot=recommendation_snapshot(current),
        previous_signature="sig-a",
        new_signature="sig-b",
        preference_changes=[{"category": "ingredient_exclusion", "value": "chicken", "action": "added"}],
        engine_version="2.1.0",
    )
    assert explanation["previous_snapshot_status"] == "INCOMPLETE"
    assert explanation["recommendation_changes"]["balanced"]["added_product_ids"] == []
    assert explanation["science_changed"] is False
    kinds = [item["kind"] for item in explanation["causes"]]
    assert "INCOMPLETE_PREVIOUS_SNAPSHOT" in kinds
    assert "CATALOG_ELIGIBILITY" in kinds


def test_identical_snapshots_are_no_material_change():
    envelope = _envelope(
        "sig-a",
        products=[{"product_id": "SF001", "name": "Beef"}],
    )
    explanation = explain_from_envelopes(envelope, envelope)
    kinds = [item["kind"] for item in explanation["causes"]]
    assert "NO_MATERIAL_CHANGE" in kinds
    assert explanation["science_changed"] is False
    assert explanation["analysis_changed"] is False
