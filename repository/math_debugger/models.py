"""Immutable models for Ω9.2 mathematical audit tracing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VariableTrace:
    variable_name: str
    variable_type: str
    unit: str
    value: float | int | str
    source: str
    allowed_range: str = ""
    meaning: str = ""


@dataclass(frozen=True)
class CodeReference:
    python_file: str
    python_function: str
    source_line_start: int
    source_line_end: int


@dataclass(frozen=True)
class WarehouseTraceRow:
    warehouse_row_id: str
    evidence_id: str
    paper_name: str
    paper_link: str
    scientific_quote: str


@dataclass(frozen=True)
class FormulaTrace:
    trace_id: str
    formula_id: str
    formula_version: str
    formula_name: str
    status: str
    equation: str
    substituted_equation: str
    intermediate_calculations: tuple[str, ...]
    output_variable: str
    output_value: float | int | str
    unit: str
    input_variables: tuple[VariableTrace, ...] = field(default_factory=tuple)
    parameter_variables: tuple[VariableTrace, ...] = field(default_factory=tuple)
    code_reference: CodeReference | None = None
    warehouse_trace_rows: tuple[WarehouseTraceRow, ...] = field(default_factory=tuple)
    upstream_trace_ids: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutionTreeNode:
    node_id: str
    title: str
    value: str
    children: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ExecutionTree:
    root_node_id: str
    nodes: tuple[ExecutionTreeNode, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FormulaConstantAuditRow:
    file: str
    line: int
    constant: str
    formula: str
    status: str
    function: str = ""
    classification: str = ""
    provenance: str = ""


@dataclass(frozen=True)
class ExecutionTrace:
    run_id: str
    input_summary: str
    formula_traces: tuple[FormulaTrace, ...]
    execution_tree: ExecutionTree
    warehouse_trace: tuple[WarehouseTraceRow, ...]
    code_references: tuple[CodeReference, ...]
    final_outputs: dict[str, float | int | str]
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
