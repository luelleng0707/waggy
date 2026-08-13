"""Explainability service skeleton."""

from __future__ import annotations

from .models import ExplainabilityContext


class ExplainabilityEngineService:
    def build_trace(self, optimization_context: dict) -> dict:
        # Ω1 skeleton only.
        return ExplainabilityContext().__dict__
