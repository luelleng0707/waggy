"""Contracts for biology reasoning services."""

from __future__ import annotations

from typing import Protocol


class BiologyService(Protocol):
    def build_context(self, profile: dict) -> dict:
        """Return biology context for downstream layers."""
