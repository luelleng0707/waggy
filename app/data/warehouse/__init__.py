"""Warehouse helpers retained after Phase Σ (parity hashing, units, parameters).

Canonical loading: app.data.native_loader + warehouse/repository.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "UnitNormalizer",
    "ParameterRepository",
    "IngredientRecord",
    "IngredientRepository",
    "PaperAdapter",
    "stable_hash",
    "deep_diff",
    "canonicalize",
]


def __getattr__(name: str) -> Any:
    if name == "UnitNormalizer":
        from app.data.warehouse.units import UnitNormalizer

        return UnitNormalizer
    if name == "ParameterRepository":
        from app.data.warehouse.parameters import ParameterRepository

        return ParameterRepository
    if name in ("IngredientRecord", "IngredientRepository"):
        from app.data.warehouse import ingredients

        return getattr(ingredients, name)
    if name == "PaperAdapter":
        from app.data.warehouse.papers import PaperAdapter

        return PaperAdapter
    if name in ("stable_hash", "deep_diff", "canonicalize"):
        from app.data.warehouse.parity import canonicalize, deep_diff, stable_hash

        return {"stable_hash": stable_hash, "deep_diff": deep_diff, "canonicalize": canonicalize}[
            name
        ]
    raise AttributeError(
        f"app.data.warehouse.{name} was removed in Phase Σ "
        "(no LegacyCompatibilityLayer / WarehouseDataPlatform / adapters)."
    )
