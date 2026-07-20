"""Parameter defaults repository — mirror of current hardcoded constants.

Phase 2: expose values; do NOT rewire health_risk / package_optimizer yet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.inference.config import (
    CATEGORY_WEIGHTS,
    ESSENTIAL_COVERAGE_FLOOR,
    SCORE_WEIGHTS,
    SURPLUS_PENALTY_WEIGHT,
)

# Mirrored from health_risk.py — do not diverge; Phase 3 may centralize.
INTERACTION_MIN = 0.80
INTERACTION_MAX = 1.20


def seed_parameter_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = [
        {"param_group": "risk_interaction", "key": "INTERACTION_MIN", "value": str(INTERACTION_MIN), "unit": "factor", "notes": "health_risk clamp"},
        {"param_group": "risk_interaction", "key": "INTERACTION_MAX", "value": str(INTERACTION_MAX), "unit": "factor", "notes": "health_risk clamp"},
        {"param_group": "package_optimizer", "key": "SURPLUS_PENALTY_WEIGHT", "value": str(SURPLUS_PENALTY_WEIGHT), "unit": "weight", "notes": ""},
        {"param_group": "package_optimizer", "key": "ESSENTIAL_COVERAGE_FLOOR", "value": str(ESSENTIAL_COVERAGE_FLOOR), "unit": "fraction", "notes": ""},
    ]
    for k, v in CATEGORY_WEIGHTS.items():
        rows.append(
            {
                "param_group": "category_weights",
                "key": k,
                "value": str(v),
                "unit": "weight",
                "notes": "RISK_V2_1",
            }
        )
    for k, v in SCORE_WEIGHTS.items():
        rows.append(
            {
                "param_group": "score_weights",
                "key": k,
                "value": str(v),
                "unit": "weight",
                "notes": "PACKAGE_OPTIMIZER_V2_1",
            }
        )
    return rows


class ParameterRepository:
    def __init__(self, df: pd.DataFrame | None = None):
        self._df = df.copy() if df is not None else pd.DataFrame(seed_parameter_rows())
        self._index: dict[tuple[str, str], str] = {}
        for _, r in self._df.iterrows():
            self._index[(str(r["param_group"]), str(r["key"]))] = str(r["value"])

    @classmethod
    def from_warehouse(cls, warehouse_root: str | Path) -> "ParameterRepository":
        path = Path(warehouse_root) / "runtime" / "parameter_defaults.csv"
        if path.exists():
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
            if not df.empty:
                return cls(df)
        return cls()

    def get(self, group: str, key: str, default: Any = None) -> Any:
        raw = self._index.get((group, key))
        if raw is None:
            return default
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw

    def group(self, group: str) -> dict[str, Any]:
        return {
            k: self.get(group, k)
            for (g, k) in self._index
            if g == group
        }

    def to_frame(self) -> pd.DataFrame:
        return self._df.copy()
