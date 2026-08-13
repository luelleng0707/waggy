"""Contracts for nutrition services."""

from __future__ import annotations

from typing import Protocol


class NutritionService(Protocol):
    def build_nutrition_context(self, prevention_context: dict) -> dict:
        """Return nutrition context placeholders."""
