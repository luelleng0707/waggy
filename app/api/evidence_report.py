"""Read-only HTTP adapter for the Phase M evidence report.

Transport only. Report construction stays in app.state.evidence_report.
"""

from __future__ import annotations

from app.state.evidence_report import build_evidence_report, evidence_report_payload


def read_evidence_report(
    dog_id: str,
    *,
    observation_type: str | None = None,
    as_of: str | None = None,
    generated_at: str | None = None,
) -> dict:
    """Serialize the Phase M report. Does not write events or PersistentDog."""
    report = build_evidence_report(
        dog_id,
        observation_type=observation_type,
        as_of=as_of,
        generated_at=generated_at,
    )
    return evidence_report_payload(report)
