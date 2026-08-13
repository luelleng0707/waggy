"""Contracts for explainability services."""

from __future__ import annotations

from typing import Protocol


class ExplainabilityService(Protocol):
    def build_trace(self, optimization_context: dict) -> dict:
        """Return explainability placeholders."""
