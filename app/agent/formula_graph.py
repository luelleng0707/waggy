"""FormulaGraph — declarative DAG executor for FormulaNodes."""

from __future__ import annotations

from typing import Iterable

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class FormulaGraph:
    """Only the graph controls execution order. Nodes never call each other."""

    def __init__(self, nodes: Iterable[FormulaNode]):
        self._nodes: dict[str, FormulaNode] = {}
        for node in nodes:
            if not node.id:
                raise ValueError(f"Node {type(node).__name__} missing id")
            if node.id in self._nodes:
                raise ValueError(f"Duplicate node id: {node.id}")
            self._nodes[node.id] = node

    @property
    def nodes(self) -> dict[str, FormulaNode]:
        return dict(self._nodes)

    def order(self) -> list[str]:
        """Kahn topological sort; raises on cycles / missing deps."""
        indeg = {nid: 0 for nid in self._nodes}
        children: dict[str, list[str]] = {nid: [] for nid in self._nodes}
        for nid, node in self._nodes.items():
            for dep in node.dependencies:
                if dep not in self._nodes:
                    raise KeyError(f"Node {nid} depends on unknown node {dep}")
                indeg[nid] += 1
                children[dep].append(nid)
        queue = [nid for nid, d in indeg.items() if d == 0]
        ordered: list[str] = []
        while queue:
            # Stable: alphabetical among ready nodes for determinism when parallel
            queue.sort()
            nid = queue.pop(0)
            ordered.append(nid)
            for child in children[nid]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    queue.append(child)
        if len(ordered) != len(self._nodes):
            raise RuntimeError("FormulaGraph has a cycle or unresolved dependency")
        return ordered

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        context.runtime["graph_order"] = self.order()
        for nid in context.runtime["graph_order"]:
            self._nodes[nid].run(context)
        context.runtime["graph_complete"] = True
        return context

    def describe(self) -> list[dict]:
        return [
            {
                "id": n.id,
                "formula_id": n.formula_id,
                "dependencies": list(n.dependencies),
                "produces": list(n.produces),
                "consumes": list(n.consumes),
                "tables": list(n.tables),
                "version": n.version,
            }
            for n in self._nodes.values()
        ]
