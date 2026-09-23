"""Ω17.3: AI consumes recalculation provenance and cannot invent it."""

from __future__ import annotations

from app.ai.agent import WaggyExplanationAgent
from app.ai.context import build_explanation_context
from app.ai.models import ExplainRequest
from app.ai.providers.fake import FakeProvider
from app.state.version import WAGGY_RECALCULATION_EXPLANATION_SCHEMA


def _canonical(signature: str, product_id: str) -> dict:
    return {
        "schema": "canonical_analysis.v1",
        "analysis_id": signature,
        "input": {"dog_profile": {"name": "Dolly"}},
        "scientific_analysis": {
            "findings": [{"title": "Joints"}],
            "nutrient_targets": [{"nutrient": "protein", "min": 40, "max": 90}],
            "evidence": [
                {
                    "paper_name": "Example Paper",
                    "paper_link": "https://example.invalid/paper",
                    "status": "APPROVED",
                }
            ],
            "warehouse_status": {},
        },
        "product_matching": {"recommendations": []},
        "package_optimization": {
            "algorithm": "PACKAGE_OPTIMIZER_V2_1",
            "package_options": {
                "balanced": [
                    {
                        "bundle_id": "bundle-a",
                        "products": [{"product_id": product_id, "name": "Staple"}],
                    }
                ]
            },
            "search": {
                "llm_used": False,
                "preference_eligibility": {
                    "scientific": False,
                    "applied": product_id != "SF002",
                    "ingredient_exclusions": ["chicken"] if product_id != "SF002" else [],
                    "removed_product_ids": ["SF002"] if product_id != "SF002" else [],
                    "removed": (
                        [{"product_id": "SF002", "reason": "ingredient_exclusion:chicken"}]
                        if product_id != "SF002"
                        else []
                    ),
                },
            },
        },
        "system": {"warnings": []},
    }


def test_context_uses_system_recalculation_when_previous_canonical_present():
    ctx = build_explanation_context(
        _canonical("sig-b", "SF001"),
        analysis_signature="sig-b",
        previous_canonical=_canonical("sig-a", "SF002"),
    )
    assert ctx.recalculation is not None
    assert ctx.recalculation["schema"] == WAGGY_RECALCULATION_EXPLANATION_SCHEMA
    assert ctx.recalculation["llm_used"] is False
    assert ctx.package_difference is not None
    assert ctx.package_difference["source"] == "system_recalculation"


def test_model_cannot_overwrite_system_recalculation():
    canned = {
        "schema": "waggy_ai_response.v1",
        "message": "The model invented a scientific cause.",
        "recalculation": {
            "schema": WAGGY_RECALCULATION_EXPLANATION_SCHEMA,
            "causes": [{"kind": "INVENTED_SCIENCE", "scientific": True}],
            "summary_facts": ["Chicken was removed because of a warehouse finding."],
            "llm_used": True,
        },
        "evidence_refs": [{"paper_name": "Invented Citation", "paper_link": "https://fake.invalid"}],
    }
    result = WaggyExplanationAgent(FakeProvider(canned)).explain(
        ExplainRequest(
            analysis_signature="sig-b",
            canonical=_canonical("sig-b", "SF001"),
            previous_canonical=_canonical("sig-a", "SF002"),
            user_message="Why did my recommendation change?",
        )
    )
    assert result.recalculation is not None
    kinds = [item["kind"] for item in result.recalculation.get("causes") or []]
    assert "INVENTED_SCIENCE" not in kinds
    assert result.recalculation["llm_used"] is False
    facts = " ".join(result.recalculation.get("summary_facts") or [])
    assert "warehouse finding" not in facts.lower()
    assert all(ref.paper_name != "Invented Citation" for ref in result.evidence_refs)


def test_fake_provider_verbalizes_supplied_summary_facts():
    result = WaggyExplanationAgent(FakeProvider()).explain(
        ExplainRequest(
            analysis_signature="sig-b",
            canonical=_canonical("sig-b", "SF001"),
            previous_canonical=_canonical("sig-a", "SF002"),
            user_message="Why did my recommendation change?",
        )
    )
    assert "LLM did not select products" in result.message
    assert result.recalculation["science_changed"] is False


def test_supplied_recalculation_is_used_without_previous_canonical():
    contract = {
        "schema": WAGGY_RECALCULATION_EXPLANATION_SCHEMA,
        "scientific": False,
        "llm_used": False,
        "causes": [{"kind": "CATALOG_ELIGIBILITY", "scientific": False, "preference_value": "chicken"}],
        "summary_facts": [
            "User preference excluded ingredient 'chicken'. This is not a scientific finding.",
            "PACKAGE_OPTIMIZER_V2_1 recomputed packages. An LLM did not select products.",
        ],
        "science_changed": False,
    }
    result = WaggyExplanationAgent(FakeProvider()).explain(
        ExplainRequest(
            analysis_signature="sig-b",
            canonical=_canonical("sig-b", "SF001"),
            user_message="Why did the package change?",
            recalculation=contract,
        )
    )
    assert result.recalculation["causes"][0]["kind"] == "CATALOG_ELIGIBILITY"
    assert "not a scientific finding" in result.message.lower()
