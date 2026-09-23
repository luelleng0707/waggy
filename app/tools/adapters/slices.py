"""Health, nutrition, and package slices from stored analysis digests."""

from __future__ import annotations

from typing import Any

from app.state.recalculation import snapshot_from_digest
from app.tools.adapters.analysis import analysis_provenance, resolve_analysis
from app.tools.auth import authorize_dog
from app.tools.models import AnalysisScopedInput, ToolCaller

NOT_AVAILABLE = "NOT_AVAILABLE"


def _record(payload: AnalysisScopedInput, caller: ToolCaller):
    authorize_dog(caller, payload.dog_id)
    return resolve_analysis(
        payload.dog_id,
        analysis_id=payload.analysis_id,
        analysis_signature=payload.analysis_signature,
    )


def analyze_health(payload: AnalysisScopedInput, caller: ToolCaller) -> dict:
    record = _record(payload, caller)
    digest = record.result_digest if isinstance(record.result_digest, dict) else {}
    snap = snapshot_from_digest(digest) or {}
    science = snap.get("science") if isinstance(snap.get("science"), dict) else {}
    titles = list(science.get("finding_titles") or digest.get("finding_titles") or [])
    findings = [{"title": title, "status": NOT_AVAILABLE if not title else "STORED"} for title in titles]
    evidence_status = NOT_AVAILABLE
    return {
        "findings": findings,
        "evidence": [],
        "evidence_status": evidence_status,
        "trait_associations": [],
        "warehouse_status": {
            "evidence": evidence_status,
            "note": "Persisted analyses store recommendation digests, not full evidence quotes.",
        },
        "engine_ran": False,
        "not_available": [] if findings else ["findings"],
        "provenance": analysis_provenance(record),
    }


def calculate_nutrition(payload: AnalysisScopedInput, caller: ToolCaller) -> dict:
    record = _record(payload, caller)
    digest = record.result_digest if isinstance(record.result_digest, dict) else {}
    snap = snapshot_from_digest(digest) or {}
    science = snap.get("science") if isinstance(snap.get("science"), dict) else {}
    rows: list[dict[str, Any]] = []
    for item in science.get("nutrients") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "nutrient": item.get("nutrient") or NOT_AVAILABLE,
                "required_amount": NOT_AVAILABLE,
                "min": item.get("min") if item.get("min") is not None else NOT_AVAILABLE,
                "max": item.get("max") if item.get("max") is not None else NOT_AVAILABLE,
                "unit": NOT_AVAILABLE,
                "basis": NOT_AVAILABLE,
                "source": "stored_recommendation_snapshot",
                "breed_recommended": NOT_AVAILABLE,
            }
        )
    return {
        "nutrient_targets": rows,
        "engine_ran": False,
        "not_available": [] if rows else ["nutrient_targets"],
        "provenance": analysis_provenance(record),
    }


def get_package_options(payload: AnalysisScopedInput, caller: ToolCaller) -> dict:
    record = _record(payload, caller)
    digest = record.result_digest if isinstance(record.result_digest, dict) else {}
    snap = snapshot_from_digest(digest) or {}
    recs = snap.get("recommendations") if isinstance(snap.get("recommendations"), dict) else {}
    packages: dict[str, list[dict[str, Any]]] = {}
    for tier, row in recs.items():
        if not isinstance(row, dict):
            continue
        packages[str(tier)] = [
            {
                "bundle_id": row.get("bundle_id"),
                "tier": tier,
                "product_ids": list(row.get("product_ids") or []),
                "product_names": list(row.get("product_names") or []),
                "monthly_cost": row.get("monthly_cost"),
            }
        ]
    if not packages:
        raw = digest.get("package_product_ids") if isinstance(digest.get("package_product_ids"), dict) else {}
        for tier, ids in raw.items():
            packages[str(tier)] = [
                {
                    "bundle_id": None,
                    "tier": tier,
                    "product_ids": list(ids or []),
                    "product_names": [],
                    "monthly_cost": NOT_AVAILABLE,
                }
            ]
    return {
        "package_options": packages,
        "optimizer_version": "PACKAGE_OPTIMIZER_V2_1",
        "engine_ran": False,
        "llm_used": False,
        "provenance": analysis_provenance(record),
    }
