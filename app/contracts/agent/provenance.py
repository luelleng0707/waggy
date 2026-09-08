"""Reusable provenance. One format for fact → evidence → computation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.agent.version import ALGORITHM_VERSION
from app.contracts.agent.enums import EvidenceStatus


class ProvenanceRecord(BaseModel):
    """RESULT → DERIVATION → FACT → EVIDENCE.

    Field names follow warehouse/engine: paper_id, paper_name, paper_link,
    publication_year, scientific_quote, fact_id, status, warehouse version, csv_hash.
    Unavailable fields stay null with an explicit status — never invented.
    """

    model_config = ConfigDict(extra="forbid")

    source_type: str = Field(
        description="paper | warehouse_row | catalog | computation | observation | user_input",
    )
    source_id: str | None = None
    evidence_id: str | None = None
    fact_id: str | None = None
    paper_id: str | None = None
    source_name: str | None = Field(default=None, description="paper_name or table name")
    source_link: str | None = Field(default=None, description="paper_link")
    publication_year: str | None = None
    quote: str | None = Field(default=None, description="scientific_quote")
    study_type: str | None = None
    species: str | None = None
    status: EvidenceStatus
    warehouse_version: str | None = None
    csv_hash: str | None = None
    engine_version: str = Field(default=ALGORITHM_VERSION)
    capability_id: str | None = None
    source_table: str | None = None
    source_row: str | None = None
