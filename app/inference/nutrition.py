"""Nutrition inference wrappers — COVERAGE_V2_1 envelope (parity)."""

from __future__ import annotations

from typing import Any

from app.inference.confidence import confidence_for_source
from app.inference.models import InferredValue

FORMULA_COVERAGE = "COVERAGE_V2_1"
FORMULA_CONDITION_SUPPORT = "CONDITION_SUPPORT_V1"


def coverage_ratio(provided: float, recommended: float) -> InferredValue:
    """Wrap existing coverage math; does not change callers' numeric path."""
    try:
        p = float(provided)
        r = float(recommended)
    except (TypeError, ValueError):
        p, r = 0.0, 0.0
    if r <= 0:
        value = 0.0 if p <= 0 else 1.0
        return InferredValue(
            value=value,
            confidence=confidence_for_source("calculated_from_ga") / 100.0,
            formula_id=FORMULA_COVERAGE,
            source="coverage_ratio",
            reason="Zero or missing recommended amount",
            unit="ratio",
            enabled=True,
            trace=({"provided": p, "recommended": r},),
        )
    ratio = p / r
    return InferredValue(
        value=ratio,
        confidence=confidence_for_source("calculated_from_ga") / 100.0,
        formula_id=FORMULA_COVERAGE,
        source="coverage_ratio",
        reason="provided / recommended",
        unit="ratio",
        enabled=True,
        trace=({"provided": p, "recommended": r, "coverage": ratio},),
    )


def condition_support_score(
    terms: list[dict[str, Any]],
    *,
    enabled: bool = False,
) -> InferredValue:
    """
    CONDITION_SUPPORT_V1 — Σ(coverage × evidence_weight × priority).
    Disabled until explicitly approved for production wiring.
    """
    total = 0.0
    steps = []
    for t in terms:
        c = float(t.get("coverage") or 0)
        e = float(t.get("evidence_weight") or 0)
        p = float(t.get("priority") or 0)
        part = c * e * p
        total += part
        steps.append({"coverage": c, "evidence_weight": e, "priority": p, "product": part})
    return InferredValue(
        value=total,
        confidence=0.0 if not enabled else confidence_for_source("calculated_from_ga") / 100.0,
        formula_id=FORMULA_CONDITION_SUPPORT,
        source="condition_support",
        reason="Disabled — opt-in only" if not enabled else "Σ coverage×evidence×priority",
        enabled=enabled,
        trace=tuple(steps),
    )
