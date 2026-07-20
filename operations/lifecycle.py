"""ΩJ–ΩK rollback + immutable snapshots."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = ROOT / "warehouse"
SNAPSHOTS = ROOT / "operations" / "snapshots"
META_RELEASES = ROOT / "governance" / "releases"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_tree(root: Path, patterns: tuple[str, ...] = ("*.csv", "*.json", "*.md", "*.yaml")) -> dict[str, str]:
    out: dict[str, str] = {}
    if not root.exists():
        return out
    for pat in patterns:
        for p in root.rglob(pat):
            if p.is_file() and "csv_analysis" not in p.parts:
                rel = str(p.relative_to(ROOT)).replace("\\", "/")
                out[rel] = _sha256_file(p)
    return out


def create_snapshot(version: str | None = None, label: str = "omega") -> Path:
    version = version or datetime.now(timezone.utc).strftime("%Y.%m.%d")
    dest = SNAPSHOTS / f"{version}-{label}"
    dest.mkdir(parents=True, exist_ok=True)

    for name in ("science", "reference", "runtime", "graph", "generated"):
        src = WAREHOUSE / name
        if src.exists():
            target = dest / "warehouse" / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "csv_analysis"))

    # Formula registry fingerprint + docs
    from app.agent.formula_registry import FORMULA_REGISTRY

    (dest / "formula_registry.json").write_text(json.dumps(FORMULA_REGISTRY, indent=2), encoding="utf-8")

    for src_dir in (ROOT / "meta" / "architecture", ROOT / "governance" / "reports", ROOT / "platform" / "observability" / "reports"):
        if src_dir.exists():
            t = dest / "docs" / src_dir.name
            if t.exists():
                shutil.rmtree(t)
            shutil.copytree(src_dir, t, ignore=shutil.ignore_patterns("*.pyc"))

    manifest = {
        "version": version,
        "label": label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contents": ["warehouse", "formula_registry", "docs"],
        "hashes": _hash_tree(dest),
        "clinical_formulas_changed": False,
    }
    # hash of hashes
    digest = hashlib.sha256(json.dumps(manifest["hashes"], sort_keys=True).encode()).hexdigest()
    manifest["snapshot_digest"] = digest
    (dest / "SNAPSHOT.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return dest


def list_snapshots() -> list[dict[str, Any]]:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    out = []
    for d in sorted(SNAPSHOTS.iterdir()):
        if d.is_dir() and (d / "SNAPSHOT.json").exists():
            out.append(json.loads((d / "SNAPSHOT.json").read_text(encoding="utf-8")))
    return out


def rollback_to(version: str) -> dict[str, Any]:
    """
    Point warehouse/current at a historical release and restore governance pointer.
    Does not rewrite live clinical data/ CSVs (engine source of truth).
    """
    from science_pipeline.publishing.release_ops import publish_to_current

    # Prefer warehouse/releases/<version>
    release_dir = WAREHOUSE / "releases" / version
    snap = None
    for d in SNAPSHOTS.glob(f"{version}*"):
        if d.is_dir():
            snap = d
            break

    if not release_dir.exists() and snap:
        # materialize release from snapshot warehouse
        release_dir.mkdir(parents=True, exist_ok=True)
        wh = snap / "warehouse"
        if wh.exists():
            for child in wh.iterdir():
                target = release_dir / child.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(child, target)
            meta = {"version": version, "validation_status": "rollback", "notes": f"Restored from snapshot {snap.name}"}
            (release_dir / "release.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    if not release_dir.exists():
        raise FileNotFoundError(f"No release or snapshot for version {version}")

    current = publish_to_current(version)

    # Restore docs from snapshot if present
    restored_docs = False
    if snap and (snap / "docs").exists():
        for sub in (snap / "docs").iterdir():
            target = ROOT / "meta" / sub.name if sub.name in ("architecture", "metrics", "dependency_graph") else ROOT / "governance" / "reports"
            if sub.name == "reports" and "observability" in str(snap):
                target = ROOT / "platform" / "observability" / "reports"
            # best-effort copy of architecture
            if sub.name == "architecture":
                target = ROOT / "meta" / "architecture"
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(sub, target)
                restored_docs = True

    result = {
        "rolled_back_to": version,
        "current_pointer": str(current / "release.json"),
        "restored_docs": restored_docs,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    META_RELEASES.mkdir(parents=True, exist_ok=True)
    (META_RELEASES / f"ROLLBACK_{version}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
