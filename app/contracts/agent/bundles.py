"""Future optimize_bundles output. Optimizer result, not an AI product pick."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import BundleTier, DomainKind, ToolErrorCode
from app.contracts.agent.products import ProductIdentity
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.versions import VersionStamp

OPTIMIZER_ALGORITHM = "PACKAGE_OPTIMIZER_V2_1"


class NutrientLedgerRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nutrient_id: str
    display: str | None = None
    unit: str | None = None
    basis: str | None = None
    required_minimum: float | None = None
    allowed_maximum: float | None = None
    actual: float | None = None
    daily_amount: float | None = None
    status: str | None = None
    breed_recommended: bool = False


class NutrientLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nutrients: list[NutrientLedgerRow] = Field(default_factory=list)
    daily_dm_g: float | None = None
    daily_dm_kg: float | None = None
    basis: str = "dry_matter_diet_density"
    daily_requirement_note: str | None = None


class FilterFunnel(BaseModel):
    """Preserves the exhaustive 2^N−1 search accounting."""

    model_config = ConfigDict(extra="forbid")

    generated: int | None = None
    evaluated: int | None = None
    life_stage_species_structurally_eligible: int | None = None
    nutrient_calculated: int | None = None
    passed_minimum_filter: int | None = None
    passed_maximum_filter: int | None = None
    nutrient_valid: int | None = None
    non_dominated: int | None = None
    with_any_care_coverage: int | None = None
    full_care_coverage: int | None = None
    within_budget: int | None = None
    satisfy_essential: int | None = None
    satisfy_balanced: int | None = None
    satisfy_optimal: int | None = None
    displayed_essential: int | None = None
    displayed_balanced: int | None = None
    displayed_optimal: int | None = None
    note: str | None = None


class OptimizerProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    algorithm: str = OPTIMIZER_ALGORITHM
    search_method: str | None = None
    candidate_count: int | None = None
    total_possible_subsets: int | None = None
    evaluated_count: int | None = None
    valid_count: int | None = None
    rejected_count: int | None = None
    filter_funnel: FilterFunnel | None = None
    ranking_rules: list[str] = Field(default_factory=list)
    llm_used: bool = False
    constraint_failures: list[str] = Field(default_factory=list)


class BundleOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.RECOMMENDATION
    bundle_id: str
    tier: BundleTier
    products: list[ProductIdentity] = Field(default_factory=list)
    product_ids: list[str] = Field(default_factory=list)
    monthly_cost: float | None = None
    annual_cost: float | None = None
    constraint_status: str | None = None
    rejection_reason: str | None = None
    care_pathways: list[str] = Field(default_factory=list)
    ranking_rationale: str | None = None
    nutrient_ledger: NutrientLedger | None = None
    provenance: list[ProvenanceRecord] = Field(default_factory=list)


class BundleSearchResult(BaseModel):
    """Canonical bundle slice for the future optimize_bundles tool."""

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.DERIVED_ANALYSIS
    capability: str = "optimize_bundles"
    essential: list[BundleOption] = Field(default_factory=list)
    balanced: list[BundleOption] = Field(default_factory=list)
    optimal: list[BundleOption] = Field(default_factory=list)
    optimizer: OptimizerProvenance = Field(default_factory=OptimizerProvenance)
    status: ToolErrorCode | None = Field(
        default=None,
        description="NO_VALID_BUNDLES when every tier is empty; otherwise null.",
    )
    provenance: list[ProvenanceRecord] = Field(default_factory=list)
    versions: VersionStamp
