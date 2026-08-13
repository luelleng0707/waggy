"""Single-interface contracts for the biological runtime stages."""

from __future__ import annotations

from typing import Protocol

from repository.models.runtime import (
    DogProfile, EvidenceCollection, EvidenceGraph, LifeStage,
    ResolvedDog, ResolvedEnvironment, ResolvedTraits, ValidationResult,
)
from repository.models.explainability import EvidenceChain


class DogResolver(Protocol):
    def resolve(self, profile: DogProfile) -> ResolvedDog:
        """Resolve raw profile into canonical dog identity and biological metadata."""


class LifeStageResolver(Protocol):
    def resolve(self, resolved_dog: ResolvedDog) -> LifeStage:
        """Resolve life stage from warehouse lifespan facts only."""


class EnvironmentResolver(Protocol):
    def resolve(self, profile: DogProfile) -> ResolvedEnvironment:
        """Normalize environment fields using warehouse environment facts."""


class TraitResolver(Protocol):
    def resolve(self, resolved_dog: ResolvedDog) -> ResolvedTraits:
        """Resolve expected biological traits from canonical warehouse facts."""


class ObservationResolver(Protocol):
    def merge(
        self,
        profile: DogProfile,
        resolved_traits: ResolvedTraits,
    ) -> ResolvedTraits:
        """Merge groomer observations into trait set with provenance."""


class ResolvedDogValidator(Protocol):
    def validate(
        self,
        resolved_dog: ResolvedDog,
        environment: ResolvedEnvironment,
        traits: ResolvedTraits,
    ) -> ValidationResult:
        """Return structured validation errors without silent repair."""


class EvidenceCollector(Protocol):
    def collect(
        self,
        resolved_dog: ResolvedDog,
        life_stage: LifeStage,
        environment: ResolvedEnvironment,
        resolved_traits: ResolvedTraits,
    ) -> EvidenceCollection:
        """Collect all relevant scientific facts for the resolved biology profile."""


class EvidenceGraphBuilder(Protocol):
    def build(self, evidence_collection: EvidenceCollection) -> EvidenceGraph:
        """Build in-memory evidence graph nodes/edges grouped by condition."""


class ScientificExplainability(Protocol):
    def build_chain(self, evidence_graph: EvidenceGraph) -> EvidenceChain:
        """Build explainability chain placeholders from evidence graph."""
