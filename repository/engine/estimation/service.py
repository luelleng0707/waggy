"""Estimation service skeleton."""

from __future__ import annotations

from .models import EstimationContext


class EstimationEngineService:
    def estimate(self, epidemiology_context: dict) -> dict:
        # Ω1 skeleton only.
        return EstimationContext().__dict__
