"""Canonical analysis envelope — one engine run, multiple slices."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.bundles import BundleSearchResult
from app.contracts.agent.enums import DomainKind
from app.contracts.agent.health import HealthAnalysisResult
from app.contracts.agent.ids import TraceabilityIds
from app.contracts.agent.input import CanonicalDogInput
from app.contracts.agent.nutrition import NutritionAnalysisResult
from app.contracts.agent.products import ProductRecord
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.versions import VersionStamp


class CanonicalAnalysis(BaseModel):
    """Role-neutral derived analysis. No HTML, debug blobs, or UI aliases."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.DERIVED_ANALYSIS
    ids: TraceabilityIds = Field(default_factory=TraceabilityIds)
    dog: CanonicalDogInput
    health: HealthAnalysisResult | None = None
    nutrition: NutritionAnalysisResult | None = None
    products: list[ProductRecord] = Field(
        default_factory=list,
        description="Eligibility/recommendation records from the same run. Not a match_products tool.",
    )
    bundles: BundleSearchResult | None = None
    versions: VersionStamp
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
