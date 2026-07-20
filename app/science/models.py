"""Typed science objects — EvidenceObject and related records."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceObject:
    id: str
    condition: str | None = None
    ingredient: str | None = None
    paper_id: str | None = None
    paper_title: str | None = None
    confidence: str | None = None
    effect_size: float | None = None
    reason: str | None = None
    citations: list[dict[str, Any]] = field(default_factory=list)
    source_table: str | None = None
    source_row: Any = None
    url: str | None = None
    year: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphNode:
    id: str
    type: str  # condition | breed | trait | ingredient | food | product | paper | activity | prevention
    label: str
    props: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "label": self.label, "props": self.props}


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    relation: str  # risk | supports | reduces | contains | studies | recommends | prevents | cites
    props: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "props": self.props,
        }
