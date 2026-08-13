"""Contracts for optimization services."""

from __future__ import annotations

from typing import Protocol


class OptimizationService(Protocol):
    def optimize(self, product_context: dict) -> dict:
        """Return optimization placeholders."""
