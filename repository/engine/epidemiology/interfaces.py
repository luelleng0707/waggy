"""Contracts for epidemiology reasoning services."""

from __future__ import annotations

from typing import Protocol


class EpidemiologyService(Protocol):
    def evaluate(self, biology_context: dict) -> dict:
        """Return epidemiological view for downstream layers."""
