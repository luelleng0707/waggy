"""Deterministic evidence weights used by mathematics engines."""

from __future__ import annotations

EVIDENCE_TYPE_WEIGHTS: dict[str, float] = {
    "observed": 1.00,
    "trait": 0.90,
    "environment": 0.70,
    "interaction": 0.80,
    "life_stage": 0.75,
    "activity": 0.65,
    "ingredient": 0.55,
}


def evidence_weight(evidence_type: str) -> float:
    return EVIDENCE_TYPE_WEIGHTS.get(evidence_type.strip().lower(), 0.50)
