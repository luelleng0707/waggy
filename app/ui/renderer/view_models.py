"""Shared view-model helpers."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any


def vm_to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: vm_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [vm_to_dict(i) for i in obj]
    return obj
