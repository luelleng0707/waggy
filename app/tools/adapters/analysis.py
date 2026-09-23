"""Read stored analysis records. Does not run the engine."""

from __future__ import annotations

from app.state.models import AnalysisRecord
from app.state.recalculation import snapshot_from_digest
from app.state.store import analyses_for
from app.tools.auth import require_safe_id
from app.tools.errors import (
    ANALYSIS_NOT_FOUND,
    COMPARISON_UNAVAILABLE,
    INVALID_ANALYSIS_REFERENCE,
    ToolFailure,
)


def resolve_analysis(
    dog_id: str,
    *,
    analysis_id: str | None = None,
    analysis_signature: str | None = None,
) -> AnalysisRecord:
    rows = analyses_for(dog_id)
    if analysis_id and analysis_signature:
        aid = require_safe_id(analysis_id, field="analysis_id")
        sig = str(analysis_signature).strip()
        matches = [row for row in rows if row.analysis_id == aid]
        if not matches:
            raise ToolFailure(ANALYSIS_NOT_FOUND, "analysis_id was not found", field="analysis_id", status=404)
        if matches[-1].analysis_signature != sig:
            raise ToolFailure(
                INVALID_ANALYSIS_REFERENCE,
                "analysis_id and analysis_signature do not refer to the same stored analysis",
                field="analysis_signature",
            )
        return matches[-1]
    if analysis_id:
        aid = require_safe_id(analysis_id, field="analysis_id")
        matches = [row for row in rows if row.analysis_id == aid]
        if not matches:
            raise ToolFailure(ANALYSIS_NOT_FOUND, "analysis_id was not found", field="analysis_id", status=404)
        return matches[-1]
    if analysis_signature:
        sig = str(analysis_signature).strip()
        if not sig:
            raise ToolFailure(INVALID_ANALYSIS_REFERENCE, "analysis_signature is empty", field="analysis_signature")
        matches = [row for row in rows if row.analysis_signature == sig]
        if not matches:
            raise ToolFailure(
                ANALYSIS_NOT_FOUND,
                "analysis_signature was not found",
                field="analysis_signature",
                status=404,
            )
        return matches[-1]
    if not rows:
        raise ToolFailure(
            ANALYSIS_NOT_FOUND,
            "no stored analysis exists for this dog",
            field="dog_id",
            status=404,
        )
    return rows[-1]


def resolve_pair(
    dog_id: str,
    *,
    previous_analysis_id: str | None = None,
    new_analysis_id: str | None = None,
    previous_signature: str | None = None,
    new_signature: str | None = None,
) -> tuple[AnalysisRecord, AnalysisRecord]:
    rows = analyses_for(dog_id)

    def by_id(analysis_id: str | None) -> AnalysisRecord | None:
        if not analysis_id:
            return None
        aid = require_safe_id(analysis_id, field="analysis_id")
        matches = [row for row in rows if row.analysis_id == aid]
        return matches[-1] if matches else None

    def by_signature(signature: str | None) -> AnalysisRecord | None:
        if not signature:
            return None
        matches = [row for row in rows if row.analysis_signature == str(signature).strip()]
        return matches[-1] if matches else None

    previous = None
    current = None
    if previous_analysis_id:
        previous = by_id(previous_analysis_id)
        if previous is None:
            raise ToolFailure(
                ANALYSIS_NOT_FOUND,
                "previous_analysis_id was not found",
                field="previous_analysis_id",
                status=404,
            )
    elif previous_signature:
        previous = by_signature(previous_signature)
        if previous is None:
            raise ToolFailure(
                ANALYSIS_NOT_FOUND,
                "previous_signature was not found",
                field="previous_signature",
                status=404,
            )
    if new_analysis_id:
        current = by_id(new_analysis_id)
        if current is None:
            raise ToolFailure(
                ANALYSIS_NOT_FOUND,
                "new_analysis_id was not found",
                field="new_analysis_id",
                status=404,
            )
    elif new_signature:
        current = by_signature(new_signature)
        if current is None:
            raise ToolFailure(
                ANALYSIS_NOT_FOUND,
                "new_signature was not found",
                field="new_signature",
                status=404,
            )
    if previous is None and current is None and len(rows) >= 2:
        previous, current = rows[-2], rows[-1]
    if previous is None or current is None:
        raise ToolFailure(
            COMPARISON_UNAVAILABLE,
            "two stored analyses are required to explain a recommendation change",
            field="previous_analysis_id",
        )
    return previous, current


def analysis_provenance(record: AnalysisRecord) -> dict:
    snap = snapshot_from_digest(record.result_digest) or {}
    return {
        "analysis_id": record.analysis_id,
        "analysis_signature": record.analysis_signature,
        "engine_version": record.engine_version,
        "warehouse_version": record.warehouse_version,
        "optimizer_version": snap.get("optimizer_version") or "PACKAGE_OPTIMIZER_V2_1",
        "source": "stored_analysis_digest",
        "llm_used": False,
        "scientific": False,
    }
