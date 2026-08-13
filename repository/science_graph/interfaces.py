"""Single-method interfaces for Ω7 scientific graph services."""

from __future__ import annotations

from typing import Protocol

from .models import GraphTrace, GraphTraversal, GraphValidation, KnowledgeGraph


class ScientificGraphBuilder(Protocol):
    def build(self) -> KnowledgeGraph:
        """Build deterministic scientific knowledge graph from warehouse datasets."""


class ScientificGraphValidator(Protocol):
    def validate(self, graph: KnowledgeGraph) -> GraphValidation:
        """Validate graph integrity, evidence completeness, and consistency."""


class ScientificTraversalEngine(Protocol):
    def traverse(self, graph: KnowledgeGraph, query: str, target_node_type: str) -> GraphTraversal:
        """Traverse shortest deterministic scientific path to target node type."""


class ScientificExplainability(Protocol):
    def explain(self, graph: KnowledgeGraph, traversal: GraphTraversal) -> GraphTraversal:
        """Aggregate path evidence into deterministic explainability payload."""


class GraphTraceBuilder(Protocol):
    def build(self, run_id: str, stages: tuple[dict[str, object], ...]) -> GraphTrace:
        """Build immutable graph trace."""
