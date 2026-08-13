"""Immutable stage models for the permanent Waggy runtime pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DogProfile:
    dog_id: str
    name: str
    breeds: tuple[str, ...] = field(default_factory=tuple)
    age_years: float | None = None
    date_of_birth: str = ""
    weight_kg: float | None = None
    sex: str = ""
    activity_level: str = ""
    environment: str = ""
    city: str = ""
    country: str = ""
    climate: str = ""
    urbanicity: str = ""
    season: str = ""
    housing: str = ""
    walking_environment: str = ""
    observed_conditions: tuple[str, ...] = field(default_factory=tuple)
    groomer_observations: tuple[dict[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ResolvedDog:
    dog_id: str
    breed: str
    breed_id: str
    date_of_birth: str
    age_days: int | None
    age_months: float | None
    age_years: float | None
    weight: float | None
    environment: str
    life_stage: str
    breed_metadata: dict[str, str] = field(default_factory=dict)
    runtime_metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class LifeStage:
    stage: str
    source_fact_id: str = ""
    rationale: str = ""


@dataclass(frozen=True)
class ResolvedEnvironment:
    environment_name: str
    city: str
    country: str
    climate: str
    urbanicity: str
    season: str
    housing: str
    walking_environment: str
    environment_id: str = ""
    environment_metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedTraits:
    dog_id: str
    traits: tuple[dict[str, str], ...] = field(default_factory=tuple)
    conflicts: tuple[dict[str, str], ...] = field(default_factory=tuple)
    provenance: tuple[dict[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ConditionEvidence:
    dog_id: str
    condition_id: str
    condition_name: str
    observed_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    trait_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    environment_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    interaction_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    life_stage_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    activity_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    ingredient_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    citations: tuple[dict[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceCollection:
    dog_id: str
    condition_evidence: tuple[ConditionEvidence, ...] = field(default_factory=tuple)
    collected_fact_ids: tuple[str, ...] = field(default_factory=tuple)
    collection_metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceGraph:
    dog_id: str
    nodes: tuple[dict[str, str], ...] = field(default_factory=tuple)
    edges: tuple[dict[str, str], ...] = field(default_factory=tuple)
    citations: tuple[dict[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ValidationError:
    code: str
    field: str
    detail: str
    severity: str = "error"


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[ValidationError, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ScientificReport:
    dog_id: str
    summary: str
