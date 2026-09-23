"""Compare and recalculation tools. Wrap explain_from_digests only."""

from __future__ import annotations

from app.state.recalculation import explain_from_digests
from app.state.version import WAGGY_RECALCULATION_EXPLANATION_SCHEMA
from app.tools.adapters.analysis import resolve_pair
from app.tools.auth import authorize_dog
from app.tools.models import CompareAnalysesInput, ToolCaller


def _pair(payload: CompareAnalysesInput, caller: ToolCaller):
    authorize_dog(caller, payload.dog_id)
    return resolve_pair(
        payload.dog_id,
        previous_analysis_id=payload.previous_analysis_id,
        new_analysis_id=payload.new_analysis_id,
        previous_signature=payload.previous_signature,
        new_signature=payload.new_signature,
    )


def compare_analyses(payload: CompareAnalysesInput, caller: ToolCaller) -> dict:
    previous, current = _pair(payload, caller)
    explanation = explain_from_digests(
        previous.result_digest,
        current.result_digest,
        previous_signature=previous.analysis_signature,
        new_signature=current.analysis_signature,
        engine_version=current.engine_version,
    )
    return {
        "schema": "analysis_compare.v1",
        "dog_id": payload.dog_id,
        "previous_analysis_id": previous.analysis_id,
        "new_analysis_id": current.analysis_id,
        "previous_digest": {
            "analysis_signature": previous.analysis_signature,
            "finding_titles": (previous.result_digest or {}).get("finding_titles") or [],
            "package_product_ids": (previous.result_digest or {}).get("package_product_ids") or {},
        },
        "new_digest": {
            "analysis_signature": current.analysis_signature,
            "finding_titles": (current.result_digest or {}).get("finding_titles") or [],
            "package_product_ids": (current.result_digest or {}).get("package_product_ids") or {},
        },
        "scientific": False,
        "llm_used": False,
        "engine_ran": False,
        "explanation": explanation,
    }


def get_recalculation_explanation(payload: CompareAnalysesInput, caller: ToolCaller) -> dict:
    result = compare_analyses(payload, caller)
    explanation = result["explanation"]
    if explanation.get("schema") != WAGGY_RECALCULATION_EXPLANATION_SCHEMA:
        explanation = {**explanation, "schema": WAGGY_RECALCULATION_EXPLANATION_SCHEMA}
    return {
        "explanation": explanation,
        "engine_ran": False,
        "llm_used": False,
        "scientific": False,
        "previous_analysis_id": result["previous_analysis_id"],
        "new_analysis_id": result["new_analysis_id"],
    }
