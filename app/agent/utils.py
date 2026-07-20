"""Shared dataframe utilities and DataRepository re-export.

CSV loading lives in app.data — this module keeps engine-facing helpers
and a stable import path (app.agent.utils.DataRepository).
"""

from __future__ import annotations

import math
import re
from typing import Iterable, Optional

import pandas as pd

from app.data.repository import DataPlatform, DataRepository, feeding_rule_for_product
from app.data.repository import parse_prevalence, resolve_breed_rows as _resolve_breed_rows
from app.data.runtime import bootstrap, get_platform, get_repository

# Re-export for historical imports
__all__ = [
    "DataRepository",
    "DataPlatform",
    "canonical_key",
    "ingredient_key",
    "normalize_breed_name",
    "parse_prevalence",
    "js_round",
    "calculate_unit_economics",
    "units_compatible",
    "feeding_rule_for_product",
    "resolve_breed_rows",
    "bootstrap",
    "get_platform",
    "get_repository",
]


def canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def ingredient_key(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", str(value or "").lower()).strip("_")


def normalize_breed_name(name: str) -> str:
    """Resolve breed aliases from BREED_ALIASES.csv via the live platform."""
    try:
        return get_platform().normalize_breed_name(name)
    except RuntimeError:
        return str(name or "").strip()


def js_round(value: float | int) -> int:
    """Match JavaScript Math.round for non-negative values (half rounds away from zero)."""
    return int(math.floor(float(value) + 0.5))


def calculate_unit_economics(pricing_df: pd.DataFrame, product_id: str) -> float:
    """Unit cost per bag — mirrors JS unit_cost_per_bag = round((price/units)*100)/100."""
    product_row = pricing_df[pricing_df["product_id"] == product_id]
    if product_row.empty:
        return 0.0
    price = float(product_row["list_price_rmb"].values[0])
    units = float(product_row["package_units"].values[0])
    if units <= 0:
        return 0.0
    return round(price / units * 100) / 100


def units_compatible(target_unit: str, product_unit: str) -> bool:
    t = str(target_unit or "").lower().strip()
    p = str(product_unit or "").lower().strip()
    if not t or not p:
        return False
    if t == p:
        return True
    aliases = {
        "mg": {"mg"},
        "g": {"g", "mg"},
        "%": {"%"},
        "capsules": {"capsules", "capsule"},
        "billion cfu": {"billion cfu", "cfu"},
    }
    return p in aliases.get(t, set())


def resolve_breed_rows(breeds_df: pd.DataFrame, names: Iterable[str]) -> pd.DataFrame:
    return _resolve_breed_rows(breeds_df, names)
