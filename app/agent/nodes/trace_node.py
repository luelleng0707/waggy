from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.formula_registry import FORMULA_REGISTRY


class TraceNode(FormulaNode):
    """Finalize automatic dependency graph + formula ledger bundle for the console."""

    id = "trace"
    formula_id = "TRACE_V1"
    # Soft deps: runs after validation so most node traces exist; also after core producers
    dependencies = ["validation", "confidence", "evidence", "grooming"]
    produces = ["trace_bundle"]
    consumes: list[str] = []
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        edges = []
        for nid, meta in context.dependency_graph.items():
            for dep in meta.get("depends_on") or []:
                edges.append({"from": dep, "to": nid})
            for prod in meta.get("produces") or []:
                edges.append({"from": nid, "produces": prod})
        bundle = {
            "graph_order": context.runtime.get("graph_order"),
            "dependency_graph": context.dependency_graph,
            "edges": edges,
            "execution_trace": context.execution_trace,
            "lookup_trace": context.lookup_trace,
            "formula_registry_ids": sorted(FORMULA_REGISTRY.keys()),
            "pipeline_trace": [e.model_dump() for e in context.pipeline_trace],
        }
        context.set_output(self.id, {"trace_bundle": bundle, **bundle})
        context.debug["formula_graph"] = {
            "order": bundle["graph_order"],
            "edges": edges,
            "node_count": len(context.execution_trace),
        }
        self.emit_step(
            context,
            name="seal_trace_bundle",
            result={"nodes": len(context.execution_trace), "lookups": len(context.lookup_trace)},
        )
