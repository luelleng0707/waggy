"""Immutable Ω7 scientific knowledge graph models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScientificNode:
    node_id: str
    node_type: str
    node_name: str
    warehouse_row_id: str


@dataclass(frozen=True)
class ScientificEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    warehouse_row_id: str
    scientific_quote: str
    paper_name: str
    paper_link: str
    formula_ids: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceNode:
    evidence_id: str
    warehouse_row_id: str
    scientific_quote: str
    paper_name: str
    paper_link: str


@dataclass(frozen=True)
class EvidenceEdge:
    evidence_edge_id: str
    edge_id: str
    evidence_id: str


@dataclass(frozen=True)
class KnowledgeGraph:
    nodes: tuple[ScientificNode, ...] = field(default_factory=tuple)
    edges: tuple[ScientificEdge, ...] = field(default_factory=tuple)
    evidence_nodes: tuple[EvidenceNode, ...] = field(default_factory=tuple)
    evidence_edges: tuple[EvidenceEdge, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ConditionGraph:
    condition_node_ids: tuple[str, ...] = field(default_factory=tuple)
    condition_edge_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class MechanismGraph:
    mechanism_node_ids: tuple[str, ...] = field(default_factory=tuple)
    mechanism_edge_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IngredientGraph:
    ingredient_node_ids: tuple[str, ...] = field(default_factory=tuple)
    ingredient_edge_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ProductGraph:
    product_node_ids: tuple[str, ...] = field(default_factory=tuple)
    product_edge_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GraphTraversal:
    query: str
    start_node_id: str
    path_node_ids: tuple[str, ...]
    path_edge_ids: tuple[str, ...]
    scientific_quotes: tuple[str, ...]
    paper_names: tuple[str, ...]
    paper_links: tuple[str, ...]
    formula_ids: tuple[str, ...]


@dataclass(frozen=True)
class GraphValidationIssue:
    issue_code: str
    severity: str
    detail: str
    warehouse_row_id: str


@dataclass(frozen=True)
class GraphStatistics:
    total_nodes: int
    total_edges: int
    conditions: int
    objectives: int
    mechanisms: int
    ingredients: int
    sources: int
    recipes: int
    products: int
    average_evidence_per_edge: float
    missing_evidence_edges: int
    duplicate_concepts: int
    disconnected_components: int


@dataclass(frozen=True)
class GraphValidation:
    ok: bool
    issues: tuple[GraphValidationIssue, ...]
    duplicate_concepts: tuple[tuple[str, str], ...]
    statistics: GraphStatistics
    formula_ids: tuple[str, ...]


@dataclass(frozen=True)
class GraphTraceStage:
    stage_name: str
    formula_ids: tuple[str, ...]
    input_summary: str
    output_summary: str
    warehouse_row_ids: tuple[str, ...]
    elapsed_ms: float


@dataclass(frozen=True)
class GraphTrace:
    run_id: str
    stages: tuple[GraphTraceStage, ...]
