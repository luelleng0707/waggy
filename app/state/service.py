"""Application-side persistence around existing analysis. Does not run the engine."""

from __future__ import annotations

from typing import Any

from app.agent.state import DogProfileInput
from app.state.models import AnalysisRecord
from app.state.projection import analysis_input_snapshot, result_digest
from app.state.recalculation import explain_from_digests
from app.state.store import record_event, save_analysis


def persist_workbench_run(
    *,
    dog_id: str,
    profile: DogProfileInput,
    envelope: dict[str, Any],
    role_context: dict[str, Any] | None,
    engine_version: str | None,
    warehouse_version: str | None,
    input_snapshot: dict[str, Any] | None = None,
    previous: AnalysisRecord | None = None,
    preference_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    digest = result_digest(envelope)
    explanation = explain_from_digests(
        previous.result_digest if previous is not None else None,
        digest,
        previous_signature=previous.analysis_signature if previous is not None else None,
        new_signature=str(envelope.get("analysis_signature") or ""),
        preference_changes=preference_changes,
        engine_version=engine_version,
    )
    digest["recalculation_explanation"] = explanation
    save_analysis(
        dog_id=dog_id,
        analysis_signature=str(envelope.get("analysis_signature") or ""),
        engine_version=engine_version,
        warehouse_version=warehouse_version,
        input_snapshot=input_snapshot if input_snapshot is not None else analysis_input_snapshot(profile),
        result_digest=digest,
        correlation_id=envelope.get("presentation_correlation_id"),
    )
    groomer = role_context.get("groomer") if isinstance(role_context, dict) else None
    if isinstance(groomer, dict):
        notes = str(groomer.get("observations") or "").strip()
        if notes:
            record_event(
                dog_id=dog_id,
                source="GROOMER",
                kind="observation",
                value=notes,
                event_type="GROOMER_OBSERVATION",
                payload={"observation": notes, "category": "unspecified"},
                status="recorded",
            )
        for token in groomer.get("observed_conditions") or []:
            text = str(token).strip()
            if not text:
                continue
            record_event(
                dog_id=dog_id,
                source="GROOMER",
                kind="observation",
                value=text,
                event_type="GROOMER_OBSERVATION",
                payload={"observed_condition": text, "observation": text},
                status="recorded",
            )
    return explanation
