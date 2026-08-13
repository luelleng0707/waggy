"""Contracts for prevention services."""

from __future__ import annotations

from typing import Protocol


class PreventionService(Protocol):
    def derive_prevention_inputs(self, estimation_context: dict) -> dict:
        """Return prevention context placeholders."""
