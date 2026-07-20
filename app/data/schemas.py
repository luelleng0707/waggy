"""Manifest schema types for the PPIE data platform."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ForeignKeySpec:
    column: str
    ref_table: str
    ref_column: str


@dataclass(frozen=True)
class FileSpec:
    path: str
    table: str
    primary_key: tuple[str, ...]
    required_columns: tuple[str, ...]
    foreign_keys: tuple[ForeignKeySpec, ...] = ()
    allow_empty: bool = False


@dataclass(frozen=True)
class Manifest:
    version: str
    modules: tuple[str, ...]
    files: tuple[FileSpec, ...]

    def by_table(self) -> dict[str, FileSpec]:
        return {f.table: f for f in self.files}

    def by_path(self) -> dict[str, FileSpec]:
        return {f.path: f for f in self.files}


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(v) for v in value)


def load_manifest(data_root: str | Path) -> Manifest:
    root = Path(data_root)
    path = root / "manifest.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing data manifest: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    files: list[FileSpec] = []
    for rel, cfg in (raw.get("files") or {}).items():
        fks: list[ForeignKeySpec] = []
        for col, ref in (cfg.get("foreign_keys") or {}).items():
            fks.append(
                ForeignKeySpec(
                    column=str(col),
                    ref_table=str(ref["table"]),
                    ref_column=str(ref["column"]),
                )
            )
        files.append(
            FileSpec(
                path=str(rel).replace("\\", "/"),
                table=str(cfg["table"]),
                primary_key=_as_tuple(cfg.get("primary_key")),
                required_columns=_as_tuple(cfg.get("required_columns")),
                foreign_keys=tuple(fks),
                allow_empty=bool(cfg.get("allow_empty", False)),
            )
        )
    return Manifest(
        version=str(raw.get("version", "0.0.0")),
        modules=tuple(str(m) for m in (raw.get("modules") or [])),
        files=tuple(files),
    )
