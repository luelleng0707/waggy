"""Presentation-only formatting helpers."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any


def fmt_rmb(value: float | int) -> str:
    return f"¥{float(value):,.0f}"


def fmt_percentage(value: float | int) -> str:
    return f"{int(round(float(value)))}%"


def fmt_mass(value: float | int, unit: str = "g") -> str:
    amount = float(value)
    if unit in ("g", "gram", "grams") and amount >= 1000:
        return f"{amount / 1000:.1f} kg"
    return f"{int(round(amount))} {unit}"


def fmt_mass_monthly(daily_amount: float, unit: str) -> str:
    monthly = daily_amount * 30
    if unit in ("g", "gram", "grams"):
        if monthly >= 1000:
            return f"{monthly / 1000:.1f} kg/month"
        return f"{monthly:.0f} g/month"
    return f"{monthly:.0f} {unit}/month"


def vm_to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: vm_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [vm_to_dict(i) for i in obj]
    return obj
