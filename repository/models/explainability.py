"""Explainability placeholder contracts for future recommendation traceability."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScientificCitation:
    citation_id: str
    paper_name: str
    paper_link: str
    scientific_quote: str
    fact_id: str


@dataclass(frozen=True)
class EvidenceNode:
    node_id: str
    condition_id: str
    condition_name: str
    summary: str
    observed_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    trait_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    environment_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    interaction_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    life_stage_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    activity_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    ingredient_evidence: tuple[dict[str, str], ...] = field(default_factory=tuple)
    citations: tuple[ScientificCitation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceEdge:
    edge_id: str
    from_node_id: str
    to_node_id: str
    evidence_type: str
    effect: str
    source_dataset: str
    citation: ScientificCitation | None = None


@dataclass(frozen=True)
class EvidenceChain:
    chain_id: str
    condition_id: str
    nodes: tuple[EvidenceNode, ...] = field(default_factory=tuple)
    edges: tuple[EvidenceEdge, ...] = field(default_factory=tuple)
