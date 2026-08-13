"""Contracts for estimation services."""

from __future__ import annotations

from typing import Protocol


class EstimationService(Protocol):
    def estimate(self, epidemiology_context: dict) -> dict:
        """Return estimated state placeholders."""
