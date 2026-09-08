"""Typed Ω12 input/output. Mapping is not inference, evidence, or recommendation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind, InputState
from app.normalization.enums import EntityKind, MappingStatus
from app.normalization.version import MAPPING_CONFIG_VERSION


class MappingCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    canonical_id: str
    canonical_name: str | None = None


class NormalizationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_value: str | None = None
    entity_kind: EntityKind
    source: str | None = Field(
        default=None,
        description="e.g. customer, groomer — copied through, not inferred scientifically.",
    )


class NormalizationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_value: str | None
    normalized_value: str | None
    canonical_id: str | None = None
    canonical_name: str | None = None
    entity_kind: EntityKind
    domain_kind: DomainKind
    status: MappingStatus
    mapping_source: str | None = None
    mapping_rule: str | None = None
    candidates: list[MappingCandidate] = Field(default_factory=list)
    components: list[NormalizationResult] = Field(default_factory=list)
    numeric_value: float | None = None
    unit: str | None = None
    input_state: InputState | None = None
    mapping_config_version: str = MAPPING_CONFIG_VERSION
    source: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
