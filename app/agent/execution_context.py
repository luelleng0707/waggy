"""ExecutionContext — shared blackboard for FormulaGraph nodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agent.state import DogProfileInput, PipelineTraceEntry
from app.agent.utils import DataRepository
from app.data.warehouse.parameters import ParameterRepository
from app.data.warehouse.units import UnitNormalizer


@dataclass
class ExecutionContext:
    profile: DogProfileInput
    repository: DataRepository
    parameters: ParameterRepository = field(default_factory=ParameterRepository)
    units: UnitNormalizer = field(default_factory=UnitNormalizer)

    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    runtime: dict[str, Any] = field(default_factory=dict)

    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    lookup_trace: list[dict[str, Any]] = field(default_factory=list)
    pipeline_trace: list[PipelineTraceEntry] = field(default_factory=list)
    dependency_graph: dict[str, Any] = field(default_factory=dict)

    debug: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # Internal: active node trace envelope (set by FormulaNode.run)
    _current_node_trace: dict[str, Any] | None = field(default=None, repr=False)

    def set_output(self, node_id: str, payload: dict[str, Any]) -> None:
        self.outputs[node_id] = payload

    def get_output(self, node_id: str, default: Any = None) -> Any:
        return self.outputs.get(node_id, default)

    def require_output(self, node_id: str) -> dict[str, Any]:
        out = self.outputs.get(node_id)
        if not isinstance(out, dict):
            raise KeyError(f"Missing required node output: {node_id}")
        return out

    def append_pipeline(self, entry: PipelineTraceEntry) -> None:
        self.pipeline_trace.append(entry)

    def register_dependency(
        self,
        node_id: str,
        depends_on: list[str],
        produces: list[str],
    ) -> None:
        self.dependency_graph[node_id] = {
            "depends_on": list(depends_on),
            "produces": list(produces),
        }

    def normalize_amount(self, amount: Any, unit: Any) -> Any:
        """Expose UnitNormalizer; formulas still receive original values via wrappers."""
        return self.units.normalize(amount, unit)

    def param(self, group: str, key: str, default: Any = None) -> Any:
        return self.parameters.get(group, key, default)
