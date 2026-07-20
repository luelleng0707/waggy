"""CSV content hashing and platform metadata."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class PlatformMeta:
    version: str
    loaded_at: str
    csv_hash: str
    file_count: int
    data_root: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_csv_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p).replace("\\", "/").lower()):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:16]


def build_meta(version: str, data_root: Path, csv_paths: list[Path]) -> PlatformMeta:
    return PlatformMeta(
        version=version,
        loaded_at=utc_now_iso(),
        csv_hash=hash_csv_files(csv_paths),
        file_count=len(csv_paths),
        data_root=str(data_root.resolve()),
    )
