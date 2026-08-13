"""Epidemiology service skeleton."""

from __future__ import annotations

from .models import EpidemiologyContext


class EpidemiologyEngineService:
    def evaluate(self, biology_context: dict) -> dict:
        # Ω1 skeleton only.
        return EpidemiologyContext().__dict__
