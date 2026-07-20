"""In-memory KnowledgeGraph — pure relationships, no AI."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from app.science.models import GraphEdge, GraphNode


def _nid(kind: str, key: str) -> str:
    safe = str(key or "").strip().lower().replace(" ", "_")
    return f"{kind}:{safe}"


class KnowledgeGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self._out: dict[str, list[GraphEdge]] = defaultdict(list)
        self._in: dict[str, list[GraphEdge]] = defaultdict(list)
        self._edge_ids: set[str] = set()

    def upsert_node(self, kind: str, key: str, label: str | None = None, **props: Any) -> str:
        nid = _nid(kind, key)
        if nid in self.nodes:
            self.nodes[nid].props.update({k: v for k, v in props.items() if v is not None})
            if label:
                self.nodes[nid].label = label
        else:
            self.nodes[nid] = GraphNode(
                id=nid,
                type=kind,
                label=label or str(key),
                props={k: v for k, v in props.items() if v is not None},
            )
        return nid

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        *,
        edge_id: str | None = None,
        **props: Any,
    ) -> str:
        eid = edge_id or f"{source}|{relation}|{target}"
        if eid in self._edge_ids:
            return eid
        edge = GraphEdge(
            id=eid,
            source=source,
            target=target,
            relation=relation,
            props={k: v for k, v in props.items() if v is not None},
        )
        self.edges.append(edge)
        self._edge_ids.add(eid)
        self._out[source].append(edge)
        self._in[target].append(edge)
        return eid

    def get(self, node_id: str) -> GraphNode | None:
        return self.nodes.get(node_id)

    def by_type(self, kind: str) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.type == kind]

    def neighbors(self, node_id: str, *, direction: str = "out", relation: str | None = None) -> list[GraphEdge]:
        pool = self._out.get(node_id, []) if direction == "out" else self._in.get(node_id, [])
        if relation:
            return [e for e in pool if e.relation == relation]
        return list(pool)

    def explain_path(
        self,
        start_id: str,
        *,
        max_depth: int = 4,
        relations: Iterable[str] | None = None,
    ) -> list[list[dict[str, Any]]]:
        """BFS path enumeration for reverse lookup explanations."""
        allowed = set(relations) if relations else None
        paths: list[list[dict[str, Any]]] = []
        queue: list[tuple[str, list[dict[str, Any]]]] = [(start_id, [])]
        seen_depth: dict[str, int] = {start_id: 0}
        while queue:
            nid, path = queue.pop(0)
            if len(path) >= max_depth:
                if path:
                    paths.append(path)
                continue
            advanced = False
            for edge in self._out.get(nid, []):
                if allowed and edge.relation not in allowed:
                    continue
                nxt = edge.target
                depth = len(path) + 1
                if seen_depth.get(nxt, 999) < depth:
                    continue
                seen_depth[nxt] = depth
                step = {
                    "from": nid,
                    "to": nxt,
                    "relation": edge.relation,
                    "props": edge.props,
                    "from_label": (self.nodes.get(nid) or GraphNode(nid, "?", nid)).label,
                    "to_label": (self.nodes.get(nxt) or GraphNode(nxt, "?", nxt)).label,
                }
                new_path = path + [step]
                queue.append((nxt, new_path))
                advanced = True
            if not advanced and path:
                paths.append(path)
        return paths[:50]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "types": sorted({n.type for n in self.nodes.values()}),
            "relations": sorted({e.relation for e in self.edges}),
        }

    def summary(self) -> dict[str, Any]:
        by_type: dict[str, int] = defaultdict(int)
        by_rel: dict[str, int] = defaultdict(int)
        for n in self.nodes.values():
            by_type[n.type] += 1
        for e in self.edges:
            by_rel[e.relation] += 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "by_type": dict(by_type),
            "by_relation": dict(by_rel),
        }
