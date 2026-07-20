"""LegacyCompatibilityLayer — warehouse frames → exact legacy DataPlatform tables."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.data.warehouse.papers import PaperAdapter
from app.data.warehouse.traits import TRAIT_SOURCES, TraitConditionAdapter


def _frames_equal(a: pd.DataFrame, b: pd.DataFrame) -> tuple[bool, str]:
    if a is None and b is None:
        return True, ""
    if a is None or b is None:
        return False, "one frame is None"
    if list(a.columns) != list(b.columns):
        return False, f"columns differ: {list(a.columns)} vs {list(b.columns)}"
    if len(a) != len(b):
        return False, f"row count {len(a)} vs {len(b)}"
    # Compare as strings for dtype=str parity
    aa = a.fillna("").astype(str).reset_index(drop=True)
    bb = b.fillna("").astype(str).reset_index(drop=True)
    if not aa.equals(bb):
        # Find first mismatch
        for col in aa.columns:
            if not aa[col].equals(bb[col]):
                for i in range(len(aa)):
                    if aa.at[i, col] != bb.at[i, col]:
                        return False, f"mismatch col={col} row={i}: {aa.at[i, col]!r} vs {bb.at[i, col]!r}"
        return False, "content mismatch"
    return True, ""


class LegacyCompatibilityLayer:
    """
    Adapters produce the SAME objects the formulas already consume.

    Old CSV → (materialize) warehouse → (this layer) → old object → existing formula
    """

    def __init__(self, warehouse: dict[str, pd.DataFrame]):
        self.warehouse = warehouse
        papers = warehouse.get("papers", pd.DataFrame())
        self.papers = PaperAdapter(papers)
        self.traits = TraitConditionAdapter(self.papers)

    def to_legacy_tables(self) -> dict[str, pd.DataFrame]:
        tables: dict[str, pd.DataFrame] = {}

        # Trait virtual tables from collapsed warehouse fact
        trait_df = self.warehouse.get("trait_condition_risk", pd.DataFrame())
        tables.update(self.traits.expand(trait_df))

        # Breed conditions
        breed = self.warehouse.get("breed_condition_risk", pd.DataFrame()).copy()
        if not breed.empty:
            breed = self.papers.inject_metadata(breed)
            breed = breed.drop(columns=["paper_id"], errors="ignore")
        tables["breed_conditions"] = breed

        # Identity passthrough
        for key, df in self.warehouse.items():
            if key.startswith("legacy::"):
                name = key.split("::", 1)[1]
                tables[name] = df.copy()

        return tables

    def compare_to_legacy(
        self, legacy_tables: dict[str, pd.DataFrame]
    ) -> dict[str, Any]:
        rebuilt = self.to_legacy_tables()
        report: dict[str, Any] = {"ok": True, "tables": {}, "missing": [], "extra": []}
        for name, expected in legacy_tables.items():
            if name not in rebuilt:
                report["missing"].append(name)
                report["ok"] = False
                continue
            ok, msg = _frames_equal(expected, rebuilt[name])
            report["tables"][name] = {"ok": ok, "detail": msg, "rows": len(expected)}
            if not ok:
                report["ok"] = False
        for name in rebuilt:
            if name not in legacy_tables:
                report["extra"].append(name)
        return report
