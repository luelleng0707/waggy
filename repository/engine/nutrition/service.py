"""Nutrition service skeleton."""

from __future__ import annotations

from .models import NutritionContext


class NutritionEngineService:
    def build_nutrition_context(self, prevention_context: dict) -> dict:
        # Ω1 skeleton only.
        return NutritionContext().__dict__
