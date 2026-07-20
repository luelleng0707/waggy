"""GraphRepository — linked lookups over KnowledgeGraph (+ EvidenceObjects)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.data.repository import DataPlatform
from app.data.runtime import get_platform
from app.science.builder import KnowledgeGraphBuilder
from app.science.graph import KnowledgeGraph
from app.science.models import EvidenceObject, GraphNode


class GraphRepository:
    def __init__(self, graph: KnowledgeGraph, evidence: list[EvidenceObject] | None = None):
        self.graph = graph
        self.evidence = evidence or []
        self._evidence_by_condition: dict[str, list[EvidenceObject]] = {}
        self._evidence_by_ingredient: dict[str, list[EvidenceObject]] = {}
        self._evidence_by_paper: dict[str, list[EvidenceObject]] = {}
        for ev in self.evidence:
            if ev.condition:
                self._evidence_by_condition.setdefault(ev.condition.lower(), []).append(ev)
            if ev.ingredient:
                self._evidence_by_ingredient.setdefault(ev.ingredient.lower(), []).append(ev)
            if ev.paper_id:
                self._evidence_by_paper.setdefault(ev.paper_id, []).append(ev)

    @classmethod
    def from_platform(cls, platform: DataPlatform | None = None) -> "GraphRepository":
        plat = platform or get_platform()
        builder = KnowledgeGraphBuilder(plat)
        return cls(builder.build(), builder.evidence_objects())

    def condition(self, name: str) -> dict[str, Any] | None:
        node = self.graph.get(f"condition:{name.strip().lower().replace(' ', '_')}")
        # fuzzy: search labels
        if node is None:
            node = self._find("condition", name)
        if node is None:
            return None
        return self._enrich(node)

    def ingredient(self, name: str) -> dict[str, Any] | None:
        node = self._find("ingredient", name)
        return self._enrich(node) if node else None

    def paper(self, paper_id: str) -> dict[str, Any] | None:
        node = self.graph.get(f"paper:{paper_id.strip().lower().replace(' ', '_')}")
        if node is None:
            # paper ids often PAPER_xxxx
            node = self.graph.nodes.get(f"paper:{paper_id}") or self._find("paper", paper_id)
        return self._enrich(node) if node else None

    def food(self, name: str) -> dict[str, Any] | None:
        node = self._find("food", name)
        return self._enrich(node) if node else None

    def product(self, product_id: str) -> dict[str, Any] | None:
        node = self._find("product", product_id)
        return self._enrich(node) if node else None

    def prevention(self, name: str) -> dict[str, Any] | None:
        node = self._find("activity", name) or self._find("prevention", name)
        return self._enrich(node) if node else None

    def breed(self, name: str) -> dict[str, Any] | None:
        node = self._find("breed", name)
        return self._enrich(node) if node else None

    def why(self, subject: str, *, kind: str = "ingredient") -> dict[str, Any]:
        """Automatic reverse lookup: Why Fish Oil? → chain through graph."""
        node = self._find(kind, subject)
        if node is None:
            # try any type
            for t in ("ingredient", "product", "food", "condition", "breed"):
                node = self._find(t, subject)
                if node:
                    break
        if node is None:
            return {"subject": subject, "found": False, "paths": []}
        paths = self.graph.explain_path(
            node.id,
            max_depth=5,
            relations=("contains", "supports", "reduces", "risk", "supported_by", "cites", "prevents", "recommends"),
        )
        return {
            "subject": subject,
            "node": node.to_dict(),
            "found": True,
            "paths": paths,
            "evidence": [e.to_dict() for e in self._evidence_for_node(node)][:20],
        }

    def explanation(self, recommendation_id: str) -> dict[str, Any]:
        """
        recommendation_id forms:
          condition:<name>
          ingredient:<name>
          product:<id>
        """
        if ":" in recommendation_id:
            kind, key = recommendation_id.split(":", 1)
        else:
            kind, key = "condition", recommendation_id
        kind = kind.strip().lower()
        key = key.strip()
        if kind == "condition":
            payload = self.condition(key) or {}
            why = self.why(key, kind="condition")
        elif kind == "ingredient":
            payload = self.ingredient(key) or {}
            why = self.why(key, kind="ingredient")
        elif kind == "product":
            payload = self.product(key) or {}
            why = self.why(key, kind="product")
        else:
            payload = {}
            why = self.why(key, kind=kind)
        return {
            "recommendation_id": recommendation_id,
            "entity": payload,
            "reasoning_chain": why,
        }

    def _find(self, kind: str, name: str) -> GraphNode | None:
        key = str(name or "").strip().lower().replace(" ", "_")
        direct = self.graph.get(f"{kind}:{key}")
        if direct:
            return direct
        # also try raw id
        direct = self.graph.get(f"{kind}:{name}")
        if direct:
            return direct
        needle = str(name or "").strip().lower()
        for n in self.graph.by_type(kind):
            if n.label.lower() == needle or n.id.endswith(":" + key):
                return n
            if needle and needle in n.label.lower():
                return n
        return None

    def _enrich(self, node: GraphNode) -> dict[str, Any]:
        out_edges = [e.to_dict() for e in self.graph.neighbors(node.id, direction="out")]
        in_edges = [e.to_dict() for e in self.graph.neighbors(node.id, direction="in")]
        return {
            **node.to_dict(),
            "outgoing": out_edges,
            "incoming": in_edges,
            "evidence": [e.to_dict() for e in self._evidence_for_node(node)][:30],
        }

    def _evidence_for_node(self, node: GraphNode) -> list[EvidenceObject]:
        if node.type == "condition":
            return self._evidence_by_condition.get(node.label.lower(), [])
        if node.type == "ingredient":
            return self._evidence_by_ingredient.get(node.label.lower(), [])
        if node.type == "paper":
            pid = node.props.get("paper_id") or node.id.split(":", 1)[-1]
            return self._evidence_by_paper.get(str(pid), [])
        return []


@lru_cache(maxsize=1)
def get_graph_repository() -> GraphRepository:
    return GraphRepository.from_platform()


def reset_graph_cache() -> None:
    get_graph_repository.cache_clear()
