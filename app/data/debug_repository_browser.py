"""Read-only repository browser for Validation Console (debug only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.data.loader import resolve_csv_path
from app.data.repository import DataRepository

NOT_TRACEABLE = "NOT CURRENTLY TRACEABLE"


def list_repository_tables(repo: DataRepository) -> dict[str, Any]:
    """Catalog every manifest CSV with metadata (no edits)."""
    platform = repo.platform
    manifest = platform.manifest
    tables = []
    for spec in manifest.files:
        path = resolve_csv_path(platform.data_root, spec.path)
        try:
            df = platform.table(spec.table)
            row_count = int(len(df))
            columns = [str(c) for c in df.columns.tolist()]
            loaded = True
        except Exception as exc:  # noqa: BLE001
            row_count = 0
            columns = list(spec.required_columns)
            loaded = False
            err = str(exc)
        else:
            err = None

        mtime = None
        if path.exists():
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = None

        tables.append(
            {
                "table": spec.table,
                "path": spec.path,
                "absolute_path": str(path) if path.exists() else None,
                "row_count": row_count,
                "columns": columns,
                "primary_key": list(spec.primary_key),
                "required_columns": list(spec.required_columns),
                "allow_empty": bool(spec.allow_empty),
                "last_modified": mtime,
                "loaded": loaded,
                "load_error": err,
                "manifest_version": manifest.version,
                "platform_csv_hash": platform.csv_hash,
                "cache_status": "IN_MEMORY" if loaded else "MISSING",
                "per_row_cache": NOT_TRACEABLE,
            }
        )

    return {
        "schema": "repository_browser.v1",
        "read_only": True,
        "manifest_version": manifest.version,
        "csv_hash": platform.csv_hash,
        "loaded_at": platform.loaded_at,
        "file_count": platform.file_count,
        "data_root": str(platform.data_root),
        "tables": tables,
    }


def preview_table(
    repo: DataRepository,
    table: str,
    *,
    limit: int = 25,
    offset: int = 0,
    q: str | None = None,
) -> dict[str, Any]:
    """Preview rows from a loaded table (read-only)."""
    platform = repo.platform
    by = platform.manifest.by_table()
    if table not in by:
        raise KeyError(f"Unknown table: {table}")
    spec = by[table]
    df = platform.table(table)
    total = int(len(df))

    if q:
        needle = q.strip().lower()
        if needle:
            mask = df.astype(str).apply(
                lambda col: col.str.lower().str.contains(needle, na=False)
            ).any(axis=1)
            df = df.loc[mask]
    filtered = int(len(df))
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))
    slice_df = df.iloc[offset : offset + limit]
    rows = slice_df.fillna("").to_dict(orient="records")

    path = resolve_csv_path(platform.data_root, spec.path)
    return {
        "schema": "repository_table_preview.v1",
        "read_only": True,
        "table": table,
        "path": spec.path,
        "absolute_path": str(path) if path.exists() else None,
        "columns": [str(c) for c in slice_df.columns.tolist()] or list(spec.required_columns),
        "primary_key": list(spec.primary_key),
        "total_rows": total,
        "filtered_rows": filtered,
        "offset": offset,
        "limit": limit,
        "rows": rows,
        "cache_status": "IN_MEMORY",
        "platform_csv_hash": platform.csv_hash,
        "note": "Preview only — never edit repository data from this browser.",
    }
