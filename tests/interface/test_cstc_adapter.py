from __future__ import annotations

import pytest

from app.ui.cstc.adapter import WagtopiaPresentationAdapter
from app.ui.cstc.demo_profiles import SYNTHETIC_DEMO_PROFILES
from app.ui.cstc.errors import ApiResponseError
from app.ui.cstc.models import AnalyzeDogRequest
from app.ui.cstc.view_models import build_presentation


class _FakeClient:
    def __init__(self):
        self.last_payload = None
        self.fail = False

    def health(self):
        return {"status": "ok"}

    def breeds(self, query=None):
        del query
        return ["Golden Retriever", "Labrador Retriever"]

    def analyze(self, payload):
        if self.fail:
            raise ApiResponseError(500, "boom")
        self.last_payload = payload
        return {
            "profile": {
                "pet_name": payload.get("pet_name"),
                "breeds": payload.get("breeds"),
                "age_years": payload.get("age_years"),
                "birthday": payload.get("birthday"),
                "weight_kg": payload.get("weight"),
                "height_cm": payload.get("height"),
                "sex": payload.get("sex"),
                "activity_level": payload.get("activity"),
                "current_environment": payload.get("environment"),
                "observed_conditions": payload.get("observed_conditions") or [],
            },
            "biology": {"age_stage": "adult", "trait_summary": ["athletic"], "descriptors": []},
            "healthInsights": [{"title": "Joint Health", "priority_score": 72.0}],
            "productRecommendations": [{"product_name": "Demo Product"}],
            "wellnessPackages": [{"tier": "essential", "price_rmb": 320}],
            "monthly_plan": {"total_cost": 300},
            "yearly_plan": {"total_cost": 3200},
            "scientificEvidence": [{"type": "ingredient", "source_name": "Study"}],
            "calculationTrace": [{"stage": "risk", "value": 72.0}],
            "debug": {"formula_executions": [{"formula_id": "MAT-1005"}]},
            "wellness_score": 78.5,
            "risks": [{"condition": "Joint"}],
            "groomer": [],
            "nutritionalTargets": [],
            "activityRecommendations": {},
        }

    def assess(self, payload):
        return {"validation": {"ok": True}, "confidence": {"score": 0.8}, "meta": {"schema": "clinical_assessment.v1"}}

    def trace(self, payload):
        del payload
        return {"trace": "ok"}


def test_demo_profiles_available():
    assert set(SYNTHETIC_DEMO_PROFILES.keys()) == {"golden_retriever", "husky", "mixed_lab_golden"}


def test_request_maps_to_existing_api_shape():
    client = _FakeClient()
    adapter = WagtopiaPresentationAdapter(client=client)
    req = AnalyzeDogRequest(
        name="Demo",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        age_years=4.2,
        birthday="2022-01-01",
        weight_kg=26.5,
        height_cm=58.0,
        sex="female",
        activity_level="Moderate",
        current_environment="Temperate Indoor",
        bcs=5.0,
        observed_conditions=("itching",),
    )
    payload = adapter.to_api_payload(req)
    assert payload["pet_name"] == "Demo"
    assert payload["breeds"] == ["Golden Retriever", "Labrador Retriever"]
    assert payload["weight"] == 26.5
    assert payload["height"] == 58.0
    assert payload["observed_conditions"] == ["itching"]


def test_run_analysis_maps_response_to_presentation_model():
    client = _FakeClient()
    adapter = WagtopiaPresentationAdapter(client=client)
    result = adapter.run_analysis(SYNTHETIC_DEMO_PROFILES["golden_retriever"])
    assert result.dog.name == "Demo Golden"
    assert result.products.products
    assert result.packages.packages
    assert result.evidence.evidence
    assert result.trace.debug_formula_executions
    assert adapter.analysis_count == 1


def test_missing_fields_do_not_crash_mapping():
    analyze = {"profile": {"pet_name": "Sparse", "breeds": ["Unknown"]}}
    result = build_presentation(analyze, assessment={})
    assert result.dog.name == "Sparse"
    assert result.financial.monthly_plan == {}
    assert result.trace.trace == ()


def test_api_failure_propagates_for_visible_ui_handling():
    client = _FakeClient()
    client.fail = True
    adapter = WagtopiaPresentationAdapter(client=client)
    with pytest.raises(ApiResponseError):
        adapter.run_analysis(SYNTHETIC_DEMO_PROFILES["golden_retriever"])
