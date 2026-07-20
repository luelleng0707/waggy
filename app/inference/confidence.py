"""Confidence ladder (CONF_V1) — does not overwrite production confidence."""

from __future__ import annotations

from typing import Any

# Embedded defaults identical to confidence_source_classes.csv
DEFAULT_LADDER: dict[str, float] = {
    "lab_measured": 100.0,
    "guaranteed_analysis": 95.0,
    "calculated_from_ga": 90.0,
    "ingredient_percent": 80.0,
    "ingredient_order": 70.0,
    "taxonomy": 60.0,
    "similarity": 45.0,
    "unknown": 0.0,
}

FORMULA_ID = "CONF_V1"


def confidence_for_source(source_class: str, ladder: dict[str, float] | None = None) -> float:
    table = ladder or DEFAULT_LADDER
    key = str(source_class or "unknown").strip().lower()
    if key in table:
        return float(table[key])
    # fuzzy aliases
    aliases = {
        "lab": "lab_measured",
        "laboratory": "lab_measured",
        "ga": "guaranteed_analysis",
        "guaranteed": "guaranteed_analysis",
        "calculated": "calculated_from_ga",
        "order": "ingredient_order",
        "percent": "ingredient_percent",
    }
    mapped = aliases.get(key)
    if mapped and mapped in table:
        return float(table[mapped])
    return float(table.get("unknown", 0.0))


def load_ladder_from_frame(df) -> dict[str, float]:
    if df is None or getattr(df, "empty", True):
        return dict(DEFAULT_LADDER)
    out: dict[str, float] = {}
    for _, row in df.iterrows():
        cls = str(row.get("source_class") or "").strip().lower()
        try:
            out[cls] = float(row.get("confidence_percent"))
        except (TypeError, ValueError):
            continue
    return out or dict(DEFAULT_LADDER)


def attach_confidence(value: Any, source_class: str, **meta: Any) -> dict[str, Any]:
    """Wrap a raw value with confidence metadata (opt-in for callers)."""
    conf = confidence_for_source(source_class, meta.get("ladder"))
    return {
        "value": value,
        "confidence": conf,
        "confidence_source_class": source_class,
        "formula_id": FORMULA_ID,
        **{k: v for k, v in meta.items() if k != "ladder"},
    }
