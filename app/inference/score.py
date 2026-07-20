"""Score inference — wraps package weights; CONDITION_SUPPORT kept separate."""

from __future__ import annotations

from typing import Any

from app.inference.config import (
    DEFAULT_SCORE_WEIGHTS,
    essential_coverage_floor,
    score_weights,
    surplus_penalty_weight,
)
from app.inference.models import InferredValue

FORMULA_PACKAGE = "PACKAGE_OPTIMIZER_V2_1"


def package_score_weights(profile_id: str = "default") -> dict[str, float]:
    """CSV-backed weights with identical default profile."""
    return score_weights(profile_id)


def package_score_meta(profile_id: str = "default") -> dict[str, Any]:
    return {
        "formula_id": FORMULA_PACKAGE,
        "profile_id": profile_id,
        "weights": package_score_weights(profile_id),
        "surplus_penalty_weight": surplus_penalty_weight(profile_id),
        "essential_coverage_floor": essential_coverage_floor(profile_id),
        "defaults_identical": package_score_weights(profile_id) == DEFAULT_SCORE_WEIGHTS,
    }


def wrap_overall_score(raw_score: float, *, profile_id: str = "default") -> InferredValue:
    """Envelope around an already-computed package overall score (no recompute)."""
    return InferredValue(
        value=raw_score,
        confidence=1.0,
        formula_id=FORMULA_PACKAGE,
        source="package_optimizer._overall_score",
        reason="Existing PACKAGE_OPTIMIZER_V2_1 result wrapped for explainability",
        enabled=True,
        trace=({"weights": package_score_weights(profile_id)},),
    )
