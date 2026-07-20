"""Unit normalization — Phase 2.

Formulas must not change. Adapters may attach canonical_* columns but
LegacyCompatibilityLayer always returns original dose_unit / amount strings
so calculate_dose() and friends see identical inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

# Default multipliers (also seeded in warehouse/runtime/unit_conversion.csv)
_DEFAULT_ROWS = [
    ("mg", "mg", 1.0),
    ("g", "mg", 1000.0),
    ("kg", "mg", 1_000_000.0),
    ("ug", "mg", 0.001),
    ("mcg", "mg", 0.001),
    ("iu", "iu", 1.0),
    ("kcal", "kcal", 1.0),
    ("kcal/kg", "kcal/kg", 1.0),
    ("mg/kg", "mg/kg", 1.0),
    ("mg/100g", "mg/100g", 1.0),
    ("g/100g", "mg/100g", 1000.0),
    ("%", "fraction", 0.01),
    ("percent", "fraction", 0.01),
    ("fraction", "fraction", 1.0),
]


@dataclass(frozen=True)
class CanonicalAmount:
    amount: float
    unit: str
    source_amount: float
    source_unit: str


class UnitNormalizer:
    """Maps source units → canonical units used by future engine phases."""

    def __init__(self, conversion_df: pd.DataFrame | None = None):
        self._map: dict[str, tuple[str, float]] = {}
        rows = _DEFAULT_ROWS
        if conversion_df is not None and not conversion_df.empty:
            rows = []
            for _, r in conversion_df.iterrows():
                unit = str(r.get("unit", "")).strip()
                canon = str(r.get("canonical_unit", "")).strip()
                try:
                    mult = float(r.get("multiplier", 1))
                except (TypeError, ValueError):
                    mult = 1.0
                if unit:
                    rows.append((unit, canon, mult))
        for unit, canon, mult in rows:
            self._map[unit.lower()] = (canon, float(mult))

    @classmethod
    def from_warehouse(cls, warehouse_root: str | Path) -> "UnitNormalizer":
        path = Path(warehouse_root) / "runtime" / "unit_conversion.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
            return cls(df)
        return cls()

    def normalize(self, amount: Any, unit: Any) -> CanonicalAmount:
        try:
            src_amt = float(amount)
        except (TypeError, ValueError):
            src_amt = 0.0
        src_unit = str(unit or "").strip()
        key = src_unit.lower()
        if key in self._map:
            canon, mult = self._map[key]
            return CanonicalAmount(src_amt * mult, canon, src_amt, src_unit)
        # Unknown unit: pass through unchanged (parity-safe)
        return CanonicalAmount(src_amt, src_unit or "unknown", src_amt, src_unit)

    def to_canonical_columns(
        self,
        df: pd.DataFrame,
        *,
        amount_col: str,
        unit_col: str,
        out_amount: str = "canonical_amount",
        out_unit: str = "canonical_unit",
    ) -> pd.DataFrame:
        """Attach canonical columns; never mutates original amount/unit columns."""
        if df.empty or amount_col not in df.columns or unit_col not in df.columns:
            return df.copy()
        out = df.copy()
        amts: list[str] = []
        units: list[str] = []
        for _, row in out.iterrows():
            c = self.normalize(row.get(amount_col), row.get(unit_col))
            amts.append(str(c.amount))
            units.append(c.unit)
        out[out_amount] = amts
        out[out_unit] = units
        return out
