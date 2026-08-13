"""Single-method contracts for Ω5.5 ingredient source planning."""

from __future__ import annotations

from typing import Protocol

from repository.mechanisms.models import MechanismPlan
from repository.objectives.models import IngredientPlan, IngredientSourcePlan


class IngredientSourceResolver(Protocol):
    def resolve(self, mechanism_plan: tuple[MechanismPlan, ...]) -> tuple[IngredientPlan, ...]:
        """Resolve mechanism plans into ingredient demand plans."""


class SourcePlanner(Protocol):
    def plan(self, ingredient_plan: tuple[IngredientPlan, ...]) -> tuple[IngredientSourcePlan, ...]:
        """Map ingredient demand to observed ingredient sources."""


class BioavailabilityAnalyzer(Protocol):
    def analyze(self, source_plan: tuple[IngredientSourcePlan, ...]) -> tuple[IngredientSourcePlan, ...]:
        """Apply deterministic bioavailability and coverage normalization."""
