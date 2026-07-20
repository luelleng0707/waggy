"""Trait condition adapter — 9 legacy tables <-> one warehouse table."""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from app.data.warehouse.papers import PaperAdapter

# (trait_category, legacy_table_key, trait_value_column, legacy_filename)
TRAIT_SOURCES: tuple[tuple[str, str, str, str], ...] = (
    ("size", "size_conditions", "size", "SIZE_CONDITIONS.csv"),
    ("body_type", "bodytype_conditions", "body_type", "BODYTYPE_CONDITIONS.csv"),
    ("coat_type", "coattype_conditions", "coat_type", "COATTYPE_CONDITIONS.csv"),
    ("energy", "energy_conditions", "energy", "ENERGY_CONDITIONS.csv"),
    ("skull_type", "skulltype_conditions", "skull_type", "SKULLTYPE_CONDITIONS.csv"),
    ("climate", "climate_conditions", "climate", "CLIMATE_CONDITIONS.csv"),
    ("lifespan", "lifespan_conditions", "lifespan", "LIFESPAN_CONDITIONS.csv"),
    ("weakness_group", "weaknessgroup_conditions", "weakness_group", "WEAKNESSGROUP_CONDITIONS.csv"),
    ("function_group", "functiongroup_conditions", "function_group", "FUNCTIONGROUP_CONDITIONS.csv"),
)

TRAIT_BY_TABLE = {t[1]: t for t in TRAIT_SOURCES}
TRAIT_BY_CATEGORY = {t[0]: t for t in TRAIT_SOURCES}


class TraitConditionAdapter:
    """One warehouse table → nine virtual legacy tables (exact column layouts)."""

    def __init__(self, paper_adapter: PaperAdapter | None = None):
        self.papers = paper_adapter or PaperAdapter()

    def collapse(self, legacy_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for category, table, trait_col, filename in TRAIT_SOURCES:
            df = legacy_tables.get(table)
            if df is None or df.empty:
                continue
            part = df.copy()
            part["trait_category"] = category
            part["trait_value"] = part[trait_col].astype(str)
            # Drop trait-specific column so concat stays long (not wide)
            part = part.drop(columns=[trait_col])
            if "_csv_file" not in part.columns or part["_csv_file"].astype(str).eq("").all():
                part["_csv_file"] = filename
            part = self.papers.stamp_paper_ids(part)
            frames.append(part)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def expand(self, warehouse_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """Rebuild legacy tables. Values/columns match original (incl. _csv_*)."""
        out: dict[str, pd.DataFrame] = {}
        if warehouse_df is None or warehouse_df.empty:
            for _, table, _, _ in TRAIT_SOURCES:
                out[table] = pd.DataFrame()
            return out

        df = self.papers.inject_metadata(warehouse_df)
        for category, table, trait_col, filename in TRAIT_SOURCES:
            subset = df[df["trait_category"].astype(str) == category].copy()
            if subset.empty:
                out[table] = pd.DataFrame()
                continue
            subset[trait_col] = subset["trait_value"].astype(str)
            drop_cols = [
                c
                for c in (
                    "trait_category",
                    "trait_value",
                    "paper_id",
                    "population",
                    "observed_percent",
                )
                if c in subset.columns
            ]
            legacy = subset.drop(columns=drop_cols, errors="ignore")
            if "_csv_file" not in legacy.columns:
                legacy["_csv_file"] = filename
            # Canonical legacy column order
            preferred = [
                trait_col,
                "condition",
                "prevalence",
                "sample_population",
                "sample_size",
                "source_name",
                "source_quote",
                "source_url",
                "year",
                "confidence_level",
                "_csv_row",
                "_csv_file",
            ]
            ordered = [c for c in preferred if c in legacy.columns]
            ordered += [c for c in legacy.columns if c not in ordered]
            out[table] = legacy[ordered].reset_index(drop=True)
        return out

    def virtual_table(self, warehouse_df: pd.DataFrame, legacy_table: str) -> pd.DataFrame:
        return self.expand(warehouse_df).get(legacy_table, pd.DataFrame())

    @staticmethod
    def legacy_table_names() -> Iterable[str]:
        return [t[1] for t in TRAIT_SOURCES]
