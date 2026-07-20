"""Warehouse adapter layer — Phase 2.

Formulas still run against legacy-shaped DataFrames.
This package only changes *where* those frames come from.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "LegacyCompatibilityLayer",
    "WarehouseDataPlatform",
    "WarehouseRepository",
    "UnitNormalizer",
    "ParameterRepository",
    "IngredientRecord",
    "IngredientRepository",
    "PaperAdapter",
    "TraitConditionAdapter",
]


def __getattr__(name: str) -> Any:
    if name == "LegacyCompatibilityLayer":
        from app.data.warehouse.legacy import LegacyCompatibilityLayer

        return LegacyCompatibilityLayer
    if name == "WarehouseDataPlatform":
        from app.data.warehouse.platform import WarehouseDataPlatform

        return WarehouseDataPlatform
    if name == "WarehouseRepository":
        from app.data.warehouse.repository import WarehouseRepository

        return WarehouseRepository
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
    if name == "TraitConditionAdapter":
        from app.data.warehouse.traits import TraitConditionAdapter

        return TraitConditionAdapter
    raise AttributeError(name)
