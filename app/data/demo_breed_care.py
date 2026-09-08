"""Retired Ω10. Not part of the Health Analysis runtime.

Use app.data.scientific_care.resolve_care_model.
This module remains only so accidental imports fail loudly instead of
silently restoring synthetic Labrador/Golden joint/skin pathways.
"""

from __future__ import annotations

from typing import Any

DEMO_BREED_CARE_FLAG = False
EVIDENCE_LABEL = "RETIRED_DEMO_SYNTHETIC_BREED_CARE_MODEL"


def care_model_for_breeds(
    breeds: list[str],
    observations: list[str] | None = None,
) -> dict[str, Any]:
    raise RuntimeError(
        "demo_breed_care is retired. Use app.data.scientific_care.resolve_care_model."
    )
