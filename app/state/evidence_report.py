"""Longitudinal reporting over Phase L evidence. Read-only derivation.

Does not write PersistentDog, does not import Ω12 or Core, and does not
fuse breed knowledge. Canonical selection is reused from Phase L.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.contracts.agent.evidence_profile import EvidenceRecord
from app.contracts.agent.evidence_report import (
    EvidenceDelta,
    EvidenceReport,
    EvidenceReportSeries,
    EvidenceTimelinePoint,
)
from app.state.evidence import get_evidence_history, select_canonical_observation

# Types whose values are already stored as numbers in existing persist scalars.
# activity_level, coat_density, and skin_appearance stay categorical.
_NUMERIC_OBSERVATION_TYPES = frozenset({"weight_kg", "height_cm", "bcs"})

# Established unit implied by the type name when a stored unit is absent.
# bcs is dimensionless in PersistentDog; no implied unit.
_ESTABLISHED_UNIT = {
    "weight_kg": "kg",
    "height_cm": "cm",
    "bcs": None,
}


def _parse_stamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _observed_at_or_before(observed_at: str, as_of: str) -> bool:
    observed_dt = _parse_stamp(observed_at)
    as_of_dt = _parse_stamp(as_of)
    if observed_dt is not None and as_of_dt is not None:
        return observed_dt <= as_of_dt
    return observed_at <= as_of


def filter_history_as_of(records: list[EvidenceRecord], as_of: str | None) -> list[EvidenceRecord]:
    """Strict replay: dated rows with observed_at <= as_of. Undated rows excluded.

    recorded_at is never used as a substitute for observed_at.
    """
    if as_of is None:
        return list(records)
    eligible: list[EvidenceRecord] = []
    for record in records:
        if not record.observed_at:
            continue
        if _observed_at_or_before(record.observed_at, as_of):
            eligible.append(record)
    return eligible


def _normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    text = unit.strip().casefold()
    return text or None


def _effective_unit(record: EvidenceRecord) -> str | None:
    stored = _normalize_unit(record.unit)
    if stored is not None:
        return stored
    established = _ESTABLISHED_UNIT.get(record.observation_type, None)
    return _normalize_unit(established) if established is not None else None


def _parse_number(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def evidence_delta(previous: EvidenceRecord, current: EvidenceRecord) -> EvidenceDelta | None:
    """Numeric delta only. No categorical ordering and no unit conversion."""
    if previous.observation_type != current.observation_type:
        return None
    if current.observation_type not in _NUMERIC_OBSERVATION_TYPES:
        return None
    previous_number = _parse_number(previous.value)
    current_number = _parse_number(current.value)
    if previous_number is None or current_number is None:
        return None
    previous_unit = _effective_unit(previous)
    current_unit = _effective_unit(current)
    if previous_unit != current_unit:
        return None
    return EvidenceDelta(
        previous_observation_id=previous.observation_id,
        current_observation_id=current.observation_id,
        previous_value=previous.value,
        current_value=current.value,
        delta=current_number - previous_number,
        unit=current.unit or _ESTABLISHED_UNIT.get(current.observation_type),
        observed_at_previous=previous.observed_at,
        observed_at_current=current.observed_at,
    )


def build_timeline(records: list[EvidenceRecord]) -> list[EvidenceTimelinePoint]:
    """History order from Phase L. First point has no delta."""
    points: list[EvidenceTimelinePoint] = []
    previous: EvidenceRecord | None = None
    for record in records:
        delta = evidence_delta(previous, record) if previous is not None else None
        points.append(EvidenceTimelinePoint(observation=record, delta_from_previous=delta))
        previous = record
    return points


def _units_for(records: list[EvidenceRecord]) -> list[str]:
    seen: list[str] = []
    for record in records:
        unit = (record.unit or "").strip()
        if unit and unit not in seen:
            seen.append(unit)
    return seen


def build_evidence_report(
    dog_id: str,
    observation_type: str | None = None,
    as_of: str | None = None,
    generated_at: str | None = None,
) -> EvidenceReport:
    """InBody-style report over Phase L history. Does not persist."""
    history = filter_history_as_of(
        get_evidence_history(dog_id, observation_type=observation_type),
        as_of,
    )
    by_type: dict[str, list[EvidenceRecord]] = {}
    for record in history:
        by_type.setdefault(record.observation_type, []).append(record)
    series: list[EvidenceReportSeries] = []
    for observation_type_name in sorted(by_type):
        rows = by_type[observation_type_name]
        series.append(
            EvidenceReportSeries(
                observation_type=observation_type_name,
                units=_units_for(rows),
                history=rows,
                canonical_observation=select_canonical_observation(rows),
                timeline=build_timeline(rows),
            )
        )
    stamp = generated_at or datetime.now(timezone.utc).isoformat()
    return EvidenceReport(dog_id=dog_id, generated_at=stamp, as_of=as_of, series=series)


def evidence_report_payload(report: EvidenceReport) -> dict:
    """JSON-ready longitudinal report. generated_at is report time only."""
    return report.model_dump(mode="json")
