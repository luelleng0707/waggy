"""Warehouse adapter layer — Phase 2.

Formulas still run against legacy-shaped DataFrames.
This package only changes *where* those frames come from.
"""

from __future__ import annotations

from app.data.warehouse.legacy import LegacyCompatibilityLayer
from app.data.warehouse.platform import WarehouseDataPlatform
from app.data.warehouse.repository import WarehouseRepository
from app.data.warehouse.units import UnitNormalizer
from app.data.warehouse.parameters import ParameterRepository
from app.data.warehouse.ingredients import IngredientRecord, IngredientRepository
from app.data.warehouse.papers import PaperAdapter
from app.data.warehouse.traits import TraitConditionAdapter

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
