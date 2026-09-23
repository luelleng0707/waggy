"""Read-only longitudinal evidence report. Not persistence and not diagnosis.

Composes Phase L EvidenceRecord history. Does not import Ω12, Core,
scientific_care, or product/package code.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.evidence_profile import EvidenceRecord


class EvidenceDelta(BaseModel):
    """Numeric comparison between two timeline points. Not a health judgment."""

    model_config = ConfigDict(extra="forbid")

    previous_observation_id: str
    current_observation_id: str
    previous_value: str
    current_value: str
    delta: float | None = None
    unit: str | None = None
    observed_at_previous: str | None = None
    observed_at_current: str | None = None


class EvidenceTimelinePoint(BaseModel):
    """One report point: the observation plus optional delta from the previous point."""

    model_config = ConfigDict(extra="forbid")

    observation: EvidenceRecord
    delta_from_previous: EvidenceDelta | None = None


class EvidenceReportSeries(BaseModel):
    """Longitudinal series for one established physical observation type."""

    model_config = ConfigDict(extra="forbid")

    observation_type: str
    units: list[str] = Field(default_factory=list)
    history: list[EvidenceRecord] = Field(default_factory=list)
    canonical_observation: EvidenceRecord | None = None
    timeline: list[EvidenceTimelinePoint] = Field(default_factory=list)


class EvidenceReport(BaseModel):
    """InBody-style structured report. In-memory only. Not stored."""

    model_config = ConfigDict(extra="forbid")

    dog_id: str
    generated_at: str
    as_of: str | None = None
    series: list[EvidenceReportSeries] = Field(default_factory=list)

    def series_for(self, observation_type: str) -> EvidenceReportSeries | None:
        for item in self.series:
            if item.observation_type == observation_type:
                return item
        return None
