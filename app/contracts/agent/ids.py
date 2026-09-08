"""Traceability identifiers. Reuse existing IDs; do not mint scientific IDs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TraceabilityIds(BaseModel):
    """References to existing or future identifiers.

    Existing today:
    - product_id (catalog / product_master)
    - paper_id, fact_id (warehouse)
    - bundle_id (package_search)
    - correlation_id (workbench header / body)
    - dog_id convention in repository.models.runtime: ``DOG::{name.lower()}``
      (unstable if the name changes — documented gap)

    Missing today (optional until Ω13):
    - analysis_id
    - tool_invocation_id
    """

    model_config = ConfigDict(extra="forbid")

    dog_id: str | None = None
    analysis_id: str | None = Field(
        default=None,
        description="Not emitted by the current engine. Reserved for one-run identity.",
    )
    tool_invocation_id: str | None = None
    correlation_id: str | None = Field(
        default=None,
        description="Reuses workbench x-wagtopia-correlation-id when present.",
    )
    evidence_id: str | None = None
    fact_id: str | None = None
    paper_id: str | None = None
    product_id: str | None = None
    bundle_id: str | None = None
    capability_id: str | None = Field(
        default=None,
        description="e.g. analyze_health or PACKAGE_OPTIMIZER_V2_1",
    )
