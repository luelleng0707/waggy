"""Future calculate_nutrition output. Does not invent nutrient requirements."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, EvidenceStatus
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.versions import VersionStamp


class NutrientRequirement(BaseModel):
    """One modeled nutrient constraint.

    Density minima (percent / mg per kg DM) are not the same as absolute
    daily feeding amounts. daily_requirement may be NOT_AVAILABLE when the
    engine only has a density basis.
    """

    model_config = ConfigDict(extra="forbid")

    nutrient_id: str
    display: str
    daily_requirement: float | None = None
    daily_requirement_status: EvidenceStatus = EvidenceStatus.NOT_AVAILABLE
    minimum: float | None = None
    maximum: float | None = None
    unit: str
    basis: str
    breed_recommended: bool = False
    source: str | None = None
    life_stage: str | None = None
    status: EvidenceStatus = EvidenceStatus.WAREHOUSE_EVIDENCE
    provenance: list[ProvenanceRecord] = Field(default_factory=list)


class NutritionAnalysisResult(BaseModel):
    """Canonical nutrition slice for the future calculate_nutrition tool."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.DERIVED_ANALYSIS
    capability: str = "calculate_nutrition"
    dog_size: str | None = None
    life_stage: str | None = None
    basis: str = "dry_matter_diet_density"
    nutrients: list[NutrientRequirement] = Field(default_factory=list)
    not_modeled: list[str] = Field(default_factory=list)
    senior_specific_minima: EvidenceStatus = EvidenceStatus.NOT_APPLICABLE
    senior_specific_minima_note: str | None = None
    complete_diet_claim: bool = False
    breed_used_for_nutrient_minima: bool = False
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    versions: VersionStamp
