"""Scientific evidence and approved facts. LLM cannot create these."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, EvidenceStatus
from app.contracts.agent.provenance import ProvenanceRecord


class ScientificEvidence(BaseModel):
    """Externally sourced scientific material (paper / study / quote).

    Evidence lives on the fact/relationship, not as a single paper glued
    onto a condition entity. Multiple records per entity are allowed.
    """

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.SCIENTIFIC_EVIDENCE
    paper_id: str | None = None
    paper_name: str | None = None
    paper_link: str | None = None
    publication_year: str | None = None
    study_type: str | None = None
    species: str | None = None
    scientific_quote: str | None = None
    status: EvidenceStatus
    warehouse_version: str | None = None
    source_table: str | None = None
    relationship_ref: str | None = Field(
        default=None,
        description="fact_id or other relationship id this evidence supports",
    )


class ScientificFact(BaseModel):
    """Approved structured relationship supported by evidence.

    Conceptual: subject — relationship — object + value/unit + status.
    Domain-specific warehouse tables remain the storage source of truth.
    """

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.SCIENTIFIC_FACT
    fact_id: str | None = None
    subject: str
    relationship: str
    object: str
    value: float | str | None = None
    unit: str | None = None
    status: EvidenceStatus
    evidence: list[ScientificEvidence] = Field(default_factory=list)
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    warehouse_version: str | None = None

    @property
    def is_scientifically_usable(self) -> bool:
        return self.status in {EvidenceStatus.APPROVED, EvidenceStatus.WAREHOUSE_EVIDENCE}
