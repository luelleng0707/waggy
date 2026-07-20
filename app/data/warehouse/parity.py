"""Parity helpers — deep equality + stable JSON hashes."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonicalize(obj: Any) -> Any:
    """Strip volatile fields that are allowed to differ (timings, loaded_at)."""
    VOLATILE_KEYS = {
        "loaded_at",
        "elapsed_ms",
        "duration_ms",
        "timing_ms",
        "stage_timings_ms",
        "generated_at",
        "timestamp",
        "request_id",
        "server_time",
        "greeting",  # time-of-day
    }

    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in VOLATILE_KEYS:
                continue
            # Nested timing bags
            if k.endswith("_ms") and isinstance(v, (int, float)):
                continue
            out[k] = canonicalize(v)
        return out
    if isinstance(obj, list):
        return [canonicalize(x) for x in obj]
    return obj


def stable_hash(obj: Any) -> str:
    blob = json.dumps(canonicalize(obj), sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def deep_diff(a: Any, b: Any, path: str = "$") -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    if type(a) is not type(b) and not (
        isinstance(a, (int, float)) and isinstance(b, (int, float))
    ):
        diffs.append({"path": path, "kind": "type", "left": type(a).__name__, "right": type(b).__name__})
        return diffs
    if isinstance(a, dict):
        keys = set(a) | set(b)
        for k in sorted(keys):
            p = f"{path}.{k}"
            if k not in a:
                diffs.append({"path": p, "kind": "missing_left", "right": b[k]})
            elif k not in b:
                diffs.append({"path": p, "kind": "missing_right", "left": a[k]})
            else:
                diffs.extend(deep_diff(a[k], b[k], p))
        return diffs
    if isinstance(a, list):
        if len(a) != len(b):
            diffs.append({"path": path, "kind": "len", "left": len(a), "right": len(b)})
        for i in range(min(len(a), len(b))):
            diffs.extend(deep_diff(a[i], b[i], f"{path}[{i}]"))
        return diffs
    if isinstance(a, float) and isinstance(b, float):
        if a != b:
            diffs.append({"path": path, "kind": "float", "left": a, "right": b})
        return diffs
    if a != b:
        diffs.append({"path": path, "kind": "value", "left": a, "right": b})
    return diffs
