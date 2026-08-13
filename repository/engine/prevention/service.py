"""Prevention service skeleton."""

from __future__ import annotations

from .models import PreventionContext


class PreventionEngineService:
    def derive_prevention_inputs(self, estimation_context: dict) -> dict:
        # Ω1 skeleton only.
        return PreventionContext().__dict__
