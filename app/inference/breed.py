"""Breed inference helpers — thin wrappers; BREED_RESOLVE_V2_1 stays in agent stage."""

from __future__ import annotations

from typing import Any

from app.inference.models import InferredValue

FORMULA_BREED = "BREED_RESOLVE_V2_1"
FORMULA_TRAIT = "TRAIT_BLEND_V2_1"


def wrap_resolved_breeds(biology: dict[str, Any] | None) -> InferredValue:
    breeds = (biology or {}).get("resolved_breeds") or []
    return InferredValue(
        value=breeds,
        confidence=1.0 if breeds else 0.0,
        formula_id=FORMULA_BREED,
        source="stages.biological",
        reason="Projection of existing biological stage output",
        enabled=True,
    )


def wrap_trait_summary(biology: dict[str, Any] | None) -> InferredValue:
    traits = (biology or {}).get("trait_summary") or (biology or {}).get("traits") or {}
    return InferredValue(
        value=traits,
        confidence=1.0 if traits else 0.0,
        formula_id=FORMULA_TRAIT,
        source="stages.biological",
        reason="Projection of existing trait blend output",
        enabled=True,
    )
