"""Future analyze_health output. Preventative findings, not an AI diagnosis."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, EvidenceStatus
from app.contracts.agent.evidence import ScientificEvidence
from app.contracts.agent.inference import BreedPrevalence, PrevalenceValue
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.versions import VersionStamp


class PreventativeTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingredient_name: str | None = None
    ingredient_id: str | None = None
    nutrient_id: str | None = None
    display: str
    kind: str | None = None
    breed_recommended: bool = False
    fact_id: str | None = None
    status: EvidenceStatus | None = None
    paper_name: str | None = None
    scientific_quote: str | None = None
    paper_link: str | None = None
    condition: str | None = None


class ConditionFinding(BaseModel):
    """Preventative condition priority / risk association. Not a diagnosis."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.SCIENTIFIC_INFERENCE
    condition: str
    pathway: str | None = None
    status: EvidenceStatus
    observed_prevalence: PrevalenceValue
    estimated_prevalence: PrevalenceValue
    observed_by_breed: list[BreedPrevalence] = Field(default_factory=list)
    contributing_traits: list[str] = Field(default_factory=list)
    preventative_targets: list[PreventativeTarget] = Field(default_factory=list)
    supporting_evidence: list[ScientificEvidence] = Field(default_factory=list)
    source_fact_ids: list[str] = Field(default_factory=list)
    diagnosis_claim: bool = False


class HealthAnalysisResult(BaseModel):
    """Canonical health slice for the future analyze_health tool."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.DERIVED_ANALYSIS
    capability: str = "analyze_health"
    findings: list[ConditionFinding] = Field(default_factory=list)
    trait_associations: list[str] = Field(
        default_factory=list,
        description="Listed separately; never summed into a fake estimated prevalence.",
    )
    preventative_targets: list[PreventativeTarget] = Field(default_factory=list)
    evidence_status: EvidenceStatus
    prevalence_available: bool = False
    diagnosis_claim: bool = False
    supporting_evidence: list[ScientificEvidence] = Field(default_factory=list)
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    versions: VersionStamp
    note: str | None = None
