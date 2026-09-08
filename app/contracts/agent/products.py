"""Product facts and commercial configuration. Not medical evidence."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, EvidenceStatus
from app.contracts.agent.provenance import ProvenanceRecord


class ProductIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str
    product_name: str
    category: str | None = None
    brand: str | None = None


class ProductCommercialData(BaseModel):
    """Advertising ≠ inventory ≠ scientific approval ≠ efficacy."""

    model_config = ConfigDict(extra="forbid")

    price: float | None = None
    currency: str | None = None
    catalog_status: str | None = Field(default=None, description="product_status from catalog")
    availability_status: str | None = None
    advertising_status: str | None = None
    fulfillment_status: str | None = None


class ProductNutrientAmount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nutrient: str
    amount: float | None = None
    unit: str | None = None
    basis: str | None = None
    serving: str | None = None
    status: EvidenceStatus | None = None


class ProductEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: EvidenceStatus
    source: str | None = None
    paper_id: str | None = None
    paper_name: str | None = None
    paper_link: str | None = None


class ProductEligibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eligible: bool
    rejection_reasons: list[str] = Field(default_factory=list)
    supporting_constraints: list[str] = Field(default_factory=list)
    supporting_fact_ids: list[str] = Field(default_factory=list)


class ProductRecord(BaseModel):
    """Canonical product for agent use. Not a treatment guarantee."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.PRODUCT_FACT
    identity: ProductIdentity
    commercial: ProductCommercialData = Field(default_factory=ProductCommercialData)
    nutrition: list[ProductNutrientAmount] = Field(default_factory=list)
    evidence: list[ProductEvidence] = Field(default_factory=list)
    eligibility: ProductEligibility | None = None
    provenance: list[ProvenanceRecord] = Field(default_factory=list)


class BusinessConfiguration(BaseModel):
    """Commercial search space. Must not alter scientific truth."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.COMMERCIAL_CONFIGURATION
    allowed_product_ids: list[str] | None = None
    allowed_brands: list[str] | None = None
    package_eligible_categories: list[str] | None = None
    advertising_only_product_ids: list[str] | None = None
    in_store_product_ids: list[str] | None = None
    online_product_ids: list[str] | None = None
    external_fulfillment_product_ids: list[str] | None = None
    monthly_budget_limit: float | None = None
    package_policy: str | None = None
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
