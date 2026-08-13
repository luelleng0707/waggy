"""Load every CSV declared in the data manifest."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from app.data.schemas import FileSpec, Manifest, load_manifest

logger = logging.getLogger(__name__)

PATH_ALIASES = {
    "breed_analysis/2_evolutionary_traits": "breed_analysis/2_evolutionary_profiles",
    "breed_analysis/4_preventative_management": "breed_analysis/4_preventative_interventions",
    "breed_analysis/product_portfolio": "product_portfolio",
}


def resolve_csv_path(data_root: Path, relative: str) -> Path:
    rel = relative.replace("\\", "/")
    candidates = [data_root / rel]
    for alias_from, alias_to in PATH_ALIASES.items():
        if rel.startswith(alias_from):
            candidates.append(data_root / rel.replace(alias_from, alias_to, 1))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    # 1-based file line number (header = line 1) — observability only
    if len(df):
        df = df.copy()
        df["_csv_row"] = list(range(2, len(df) + 2))
        df["_csv_file"] = path.name
    return df


def load_all_tables(data_root: str | Path) -> tuple[Manifest, dict[str, pd.DataFrame], list[Path]]:
    root = Path(data_root)

    # Repository-native: in-memory formula views (no disk projections)
    from app.data.native_loader import is_native_warehouse, load_native_warehouse

    if is_native_warehouse(root):
        return load_native_warehouse(root)

    if (root / "breed_analysis").exists():
        base = root
    elif root.name == "breed_analysis":
        base = root.parent
    else:
        base = root

    manifest = load_manifest(base)
    tables: dict[str, pd.DataFrame] = {}
    paths: list[Path] = []

    for spec in manifest.files:
        path = resolve_csv_path(base, spec.path)
        if not path.exists():
            if spec.allow_empty:
                logger.warning("Optional CSV missing (empty table): %s", spec.path)
                tables[spec.table] = pd.DataFrame(columns=list(spec.required_columns))
                continue
            raise FileNotFoundError(f"Required CSV missing: {path}")
        df = _read_csv(path)
        tables[spec.table] = df
        paths.append(path)
        logger.info("Loaded %s rows from %s → table=%s", len(df), path.name, spec.table)

    return manifest, tables, paths
