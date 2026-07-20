"""Materialize warehouse tables from the live legacy DataPlatform (in-memory)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.data.repository import DataPlatform
from app.data.warehouse.papers import PaperAdapter
from app.data.warehouse.parameters import ParameterRepository, seed_parameter_rows
from app.data.warehouse.traits import TRAIT_SOURCES, TraitConditionAdapter
from app.data.warehouse.units import UnitNormalizer


def materialize_warehouse(legacy: DataPlatform) -> dict[str, pd.DataFrame]:
    """
    Build warehouse-shaped frames from legacy tables.

    Trait prevalence CSVs collapse into trait_condition_risk.
    Citations are indexed into papers (paper_id stamped on science rows).
    All other legacy tables pass through under their legacy keys for identity adapters.
    """
    paper_adapter = PaperAdapter.extract_from_frames(list(legacy._tables.values()))
    trait_adapter = TraitConditionAdapter(paper_adapter)

    trait_risk = trait_adapter.collapse(legacy._tables)

    breed_cond = legacy._tables.get("breed_conditions", pd.DataFrame()).copy()
    if not breed_cond.empty:
        breed_cond = paper_adapter.stamp_paper_ids(breed_cond)

    warehouse: dict[str, pd.DataFrame] = {
        "papers": paper_adapter.papers,
        "trait_condition_risk": trait_risk,
        "breed_condition_risk": breed_cond,
        "parameter_defaults": pd.DataFrame(seed_parameter_rows()),
        "unit_conversion": _unit_conversion_frame(),
    }

    # Identity passthrough for every non-collapsed legacy table
    collapsed = {t[1] for t in TRAIT_SOURCES}
    for name, df in legacy._tables.items():
        if name in collapsed:
            continue
        if name == "breed_conditions":
            continue  # represented as breed_condition_risk
        warehouse[f"legacy::{name}"] = df.copy()

    return warehouse


def _unit_conversion_frame() -> pd.DataFrame:
    n = UnitNormalizer()
    rows = [
        {"unit": u, "canonical_unit": c, "multiplier": str(m), "notes": ""}
        for u, (c, m) in sorted(n._map.items())
    ]
    return pd.DataFrame(rows)


def persist_warehouse(warehouse: dict[str, pd.DataFrame], warehouse_root: str | Path) -> None:
    """Write materialized frames into warehouse/ (science/reference/runtime)."""
    root = Path(warehouse_root)
    mapping = {
        "papers": root / "reference" / "papers.csv",
        "trait_condition_risk": root / "science" / "trait_condition_risk.csv",
        "breed_condition_risk": root / "science" / "breed_condition_risk.csv",
        "parameter_defaults": root / "runtime" / "parameter_defaults.csv",
        "unit_conversion": root / "runtime" / "unit_conversion.csv",
    }
    for key, path in mapping.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        df = warehouse.get(key, pd.DataFrame())
        df.to_csv(path, index=False)

    mirror = root / "runtime" / "legacy_mirror"
    mirror.mkdir(parents=True, exist_ok=True)
    for key, df in warehouse.items():
        if key.startswith("legacy::"):
            name = key.split("::", 1)[1]
            df.to_csv(mirror / f"{name}.csv", index=False)


def load_persisted_warehouse(warehouse_root: str | Path) -> dict[str, pd.DataFrame] | None:
    root = Path(warehouse_root)
    required = [
        root / "science" / "trait_condition_risk.csv",
        root / "reference" / "papers.csv",
    ]
    if not all(p.exists() for p in required):
        return None
    out: dict[str, pd.DataFrame] = {}
    out["trait_condition_risk"] = pd.read_csv(
        root / "science" / "trait_condition_risk.csv", dtype=str, keep_default_na=False
    )
    breed_path = root / "science" / "breed_condition_risk.csv"
    if breed_path.exists():
        out["breed_condition_risk"] = pd.read_csv(breed_path, dtype=str, keep_default_na=False)
    out["papers"] = pd.read_csv(root / "reference" / "papers.csv", dtype=str, keep_default_na=False)
    params = root / "runtime" / "parameter_defaults.csv"
    if params.exists():
        out["parameter_defaults"] = pd.read_csv(params, dtype=str, keep_default_na=False)
    units = root / "runtime" / "unit_conversion.csv"
    if units.exists():
        out["unit_conversion"] = pd.read_csv(units, dtype=str, keep_default_na=False)

    mirror = root / "runtime" / "legacy_mirror"
    if mirror.exists():
        for path in mirror.glob("*.csv"):
            out[f"legacy::{path.stem}"] = pd.read_csv(path, dtype=str, keep_default_na=False)
    return out
