"""FormulaNode base — every graph node implements the same contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any, ClassVar

from app.agent.execution_context import ExecutionContext


class FormulaNode(ABC):
    """No custom APIs. Graph calls execute(context) only."""

    id: ClassVar[str] = ""
    formula_id: ClassVar[str] = ""
    dependencies: ClassVar[list[str]] = []
    produces: ClassVar[list[str]] = []
    consumes: ClassVar[list[str]] = []
    tables: ClassVar[list[str]] = []
    version: ClassVar[str] = "2.1.0"

    def run(self, context: ExecutionContext) -> None:
        """Graph entry — wraps execute with automatic timing + trace envelope."""
        started = perf_counter()
        node_trace: dict[str, Any] = {
            "node": self.id,
            "formula_id": self.formula_id,
            "version": self.version,
            "dependencies": list(self.dependencies),
            "produces": list(self.produces),
            "consumes": list(self.consumes),
            "tables": list(self.tables),
            "inputs_snapshot": self._input_snapshot(context),
            "steps": [],
            "lookups": [],
            "outputs_keys": [],
            "warnings": [],
            "errors": [],
            "timing_ms": None,
        }
        context._current_node_trace = node_trace
        try:
            self.execute(context)
        except Exception as exc:  # noqa: BLE001 — record then re-raise
            node_trace["errors"].append(str(exc))
            context.execution_trace.append(node_trace)
            raise
        finally:
            context._current_node_trace = None
        node_trace["timing_ms"] = round((perf_counter() - started) * 1000, 3)
        outs = context.outputs.get(self.id) or {}
        if isinstance(outs, dict):
            node_trace["outputs_keys"] = sorted(outs.keys())
        context.execution_trace.append(node_trace)
        context.metrics[f"node.{self.id}.ms"] = node_trace["timing_ms"]
        context.register_dependency(self.id, self.dependencies, self.produces)

    @abstractmethod
    def execute(self, context: ExecutionContext) -> None:
        """Read context, write context.outputs[self.id]. No cross-node calls."""

    def _input_snapshot(self, context: ExecutionContext) -> dict[str, Any]:
        snap: dict[str, Any] = {"profile_name": getattr(context.profile, "name", None)}
        for dep in self.dependencies:
            out = context.outputs.get(dep)
            if isinstance(out, dict):
                snap[dep] = {"keys": sorted(out.keys())[:40]}
            elif out is not None:
                snap[dep] = type(out).__name__
        return snap

    def emit_step(
        self,
        context: ExecutionContext,
        *,
        name: str,
        expression: str | None = None,
        inputs: dict[str, Any] | None = None,
        result: Any = None,
        before: Any = None,
        after: Any = None,
    ) -> None:
        trace = getattr(context, "_current_node_trace", None)
        if not isinstance(trace, dict):
            return
        trace.setdefault("steps", []).append(
            {
                "name": name,
                "expression": expression,
                "inputs": inputs or {},
                "before": before,
                "after": after,
                "result": result,
            }
        )

    def emit_lookup(
        self,
        context: ExecutionContext,
        *,
        table: str,
        row_id: Any = None,
        paper_id: Any = None,
        columns: list[str] | None = None,
        selection_rule: str | None = None,
        rows: int | None = None,
    ) -> None:
        entry = {
            "node": self.id,
            "table": table,
            "row_id": row_id,
            "paper_id": paper_id,
            "columns": columns or [],
            "selection_rule": selection_rule,
            "rows": rows,
        }
        context.lookup_trace.append(entry)
        trace = getattr(context, "_current_node_trace", None)
        if isinstance(trace, dict):
            trace.setdefault("lookups", []).append(entry)
