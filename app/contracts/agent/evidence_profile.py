"""Read-only physical evidence profile. Not scientific evidence and not persistence.

Normalized view over Observation / ProfileEvent history. Does not import Ω12,
Core, scientific_care, or product/package code.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import ObserverRole

# Read-policy source precedence. Not a confidence or diagnostic score.
# SYSTEM is below CUSTOMER so it cannot outrank an individual observer.
SOURCE_PRECEDENCE = (
    ObserverRole.SYSTEM,
    ObserverRole.CUSTOMER,
    ObserverRole.GROOMER,
    ObserverRole.VETERINARIAN,
)


class EvidenceRecord(BaseModel):
    """One normalized physical observation with full provenance.

    In-memory read contract. Not a second event log.
    """

    model_config = ConfigDict(extra="forbid")

    observation_id: str
    dog_id: str
    observation_type: str
    value: str
    unit: str | None = None
    observer_role: ObserverRole
    source: str
    observed_at: str | None = None
    recorded_at: str | None = None
    source_session_id: str | None = None
    event_id: str


class EvidenceSeries(BaseModel):
    """Complete history for one observation type, plus a selected canonical row."""

    model_config = ConfigDict(extra="forbid")

    observation_type: str
    observations: list[EvidenceRecord] = Field(default_factory=list)
    canonical_observation: EvidenceRecord | None = None


class EvidenceProfile(BaseModel):
    """Canonical evidence profile for one pet.

    Canonical means the observation selected by the documented read policy.
    History remains the complete evidence record. This object is not stored.
    """

    model_config = ConfigDict(extra="forbid")

    dog_id: str
    series: list[EvidenceSeries] = Field(default_factory=list)

    def series_for(self, observation_type: str) -> EvidenceSeries | None:
        for item in self.series:
            if item.observation_type == observation_type:
                return item
        return None
