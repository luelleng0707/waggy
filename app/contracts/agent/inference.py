"""Derived scientific inference. Engine output, not warehouse truth."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import AvailabilityStatus, DomainKind, EvidenceStatus
from app.contracts.agent.evidence import ScientificEvidence
from app.contracts.agent.provenance import ProvenanceRecord


class PrevalenceValue(BaseModel):
    """Numeric prevalence or an explicit NOT_AVAILABLE.

    NOT_AVAILABLE must not be encoded as 0 or an average.
    """

    model_config = ConfigDict(extra="forbid")

    status: AvailabilityStatus
    percent: float | None = None
    ratio: float | None = None
    unit: str | None = None

    @property
    def is_numeric(self) -> bool:
        return self.status == AvailabilityStatus.AVAILABLE and (
            self.percent is not None or self.ratio is not None
        )


class BreedPrevalence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    breed: str
    percent: float | None = None
    ratio: float | None = None


class ScientificInference(BaseModel):
    """Generic derived result: input facts → engine → value + evidence."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.SCIENTIFIC_INFERENCE
    inference_type: str
    subject: str
    result_status: EvidenceStatus
    observed_prevalence: PrevalenceValue | None = None
    estimated_prevalence: PrevalenceValue | None = None
    priority: int | None = None
    supporting_evidence: list[ScientificEvidence] = Field(default_factory=list)
    contributing_traits: list[str] = Field(default_factory=list)
    source_fact_ids: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    reasoning: str | None = Field(
        default=None,
        description="Engine-emitted rationale already present on the analysis, not LLM text.",
    )
