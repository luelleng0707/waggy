"""Resolve active and requested formula versions."""

from __future__ import annotations

from .models import FormulaConfiguration
from .registry import FormulaRegistry


class FormulaVersionResolver:
    def __init__(self, registry: FormulaRegistry):
        self.registry = registry

    def resolve(self, formula_id: str, requested_version: str | None = None) -> FormulaConfiguration:
        if requested_version:
            config = self.registry.configuration(formula_id, requested_version)
            if config is None:
                raise KeyError(f"Formula version not found: {formula_id}:{requested_version}")
            return config

        active_versions = [
            entry for entry in self.registry.versions if entry.formula_id == formula_id and entry.status == "active"
        ]
        if active_versions:
            active_versions = sorted(active_versions, key=lambda item: item.version, reverse=True)
            config = self.registry.configuration(formula_id, active_versions[0].version)
            if config is None:
                raise KeyError(f"Active formula configuration missing: {formula_id}:{active_versions[0].version}")
            return config

        latest = [entry for entry in self.registry.catalog if entry.formula_id == formula_id]
        if not latest:
            raise KeyError(f"Formula not found: {formula_id}")
        config = self.registry.configuration(formula_id, latest[0].latest_version)
        if config is None:
            raise KeyError(f"Latest formula configuration missing: {formula_id}:{latest[0].latest_version}")
        return config
