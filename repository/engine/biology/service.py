"""Biology service skeleton."""

from __future__ import annotations

from .models import BiologyContext


class BiologyEngineService:
    def build_context(self, profile: dict) -> dict:
        # Ω1 skeleton only.
        return BiologyContext().__dict__
