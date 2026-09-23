"""Read/normalization layer over persisted physical observations.

Source of truth remains ProfileEvent / events. This module does not write
PersistentDog, does not import Ω12 or Core, and does not fuse breed knowledge.
"""

from __future__ import annotations

from app.contracts.agent.evidence_profile import (
    SOURCE_PRECEDENCE,
    EvidenceProfile,
    EvidenceRecord,
    EvidenceSeries,
)
from app.contracts.agent.observations import (
    is_breed_derived_trait_name,
    is_physical_observation_type,
)
from app.state.observations import observation_from_event
from app.state.store import events_for, require_dog

_PRECEDENCE_RANK = {role: index for index, role in enumerate(SOURCE_PRECEDENCE)}


def _stamp_key(value: str | None) -> tuple[int, str]:
    """Missing stamps sort as unknown, never as a fabricated time."""
    if value:
        return (1, value)
    return (0, "")


def _history_sort_key(record: EvidenceRecord) -> tuple:
    """Dated rows chronological first; unknown observed_at last; then recorded_at, event_id."""
    has_observed, observed = _stamp_key(record.observed_at)
    has_recorded, recorded = _stamp_key(record.recorded_at)
    return (
        0 if has_observed else 1,
        observed,
        0 if has_recorded else 1,
        recorded,
        record.event_id,
    )


def _canonical_sort_key(record: EvidenceRecord) -> tuple:
    """Higher tuple wins: role precedence, then known observed_at recency, then recorded_at, event_id."""
    has_observed, observed = _stamp_key(record.observed_at)
    has_recorded, recorded = _stamp_key(record.recorded_at)
    return (
        _PRECEDENCE_RANK.get(record.observer_role, -1),
        has_observed,
        observed,
        has_recorded,
        recorded,
        record.event_id,
    )


def _records_from_events(dog_id: str) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    for event in events_for(dog_id):
        observation_type = (event.payload or {}).get("observation_type")
        if not isinstance(observation_type, str):
            continue
        if not is_physical_observation_type(observation_type):
            continue
        if is_breed_derived_trait_name(observation_type):
            continue
        observation = observation_from_event(event)
        records.append(
            EvidenceRecord(
                observation_id=str(observation.observation_id or event.event_id),
                dog_id=event.dog_id,
                observation_type=observation_type,
                value=event.value,
                unit=observation.unit,
                observer_role=observation.observer_role,
                source=str(event.source),
                observed_at=event.observed_at,
                recorded_at=event.recorded_at,
                source_session_id=event.session_id or observation.source_session_id,
                event_id=event.event_id,
            )
        )
    return records


def get_evidence_history(dog_id: str, observation_type: str | None = None) -> list[EvidenceRecord]:
    """Complete physical-evidence history. Empty for unknown or breed-derived types."""
    require_dog(dog_id)
    if observation_type is not None:
        if is_breed_derived_trait_name(observation_type) or not is_physical_observation_type(observation_type):
            return []
    records = _records_from_events(dog_id)
    if observation_type is not None:
        records = [item for item in records if item.observation_type == observation_type]
    return sorted(records, key=_history_sort_key)


def select_canonical_observation(records: list[EvidenceRecord]) -> EvidenceRecord | None:
    """Deterministic read selection. Does not mutate history."""
    if not records:
        return None
    return max(records, key=_canonical_sort_key)


def get_canonical_observation(dog_id: str, observation_type: str) -> EvidenceRecord | None:
    history = get_evidence_history(dog_id, observation_type=observation_type)
    return select_canonical_observation(history)


def build_evidence_profile(dog_id: str) -> EvidenceProfile:
    """InBody-style structured read: canonical + full history per type with evidence."""
    require_dog(dog_id)
    history = get_evidence_history(dog_id)
    by_type: dict[str, list[EvidenceRecord]] = {}
    for record in history:
        by_type.setdefault(record.observation_type, []).append(record)
    series: list[EvidenceSeries] = []
    for observation_type in sorted(by_type):
        rows = by_type[observation_type]
        series.append(
            EvidenceSeries(
                observation_type=observation_type,
                observations=rows,
                canonical_observation=select_canonical_observation(rows),
            )
        )
    return EvidenceProfile(dog_id=dog_id, series=series)


def evidence_profile_payload(profile: EvidenceProfile) -> dict:
    """JSON for an EvidenceProfile. Not the Phase N EvidenceReport contract."""
    blocks: list[dict] = []
    for series in profile.series:
        canonical = series.canonical_observation
        blocks.append(
            {
                "observation_type": series.observation_type,
                "canonical": None
                if canonical is None
                else canonical.model_dump(mode="json"),
                "history": [item.model_dump(mode="json") for item in series.observations],
            }
        )
    return {"dog_id": profile.dog_id, "physical_evidence": blocks}
