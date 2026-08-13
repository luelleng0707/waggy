# TRACE_ARCHITECTURE_AUDIT

## Runtime trace
- `repository/models/trace.py` (`RuntimeTrace`, `StageTrace`)
- Used by orchestrator execution tracing.

## Formula trace
- `repository/mathematics/models.py` (`MathematicalFormulaTrace`)
- Used by MAT-1001..MAT-1008 stage traces.

## Warehouse provenance trace
- `repository/math_debugger/warehouse_trace.py` and debugger models.
- Maps formula traces to fact/citation provenance.

## Optimization trace
- `repository/math_debugger/runtime.py::trace_optimization`
- Exposes optimization component traces for audit.

## Developer debugger trace
- `app/agent/calculation_trace.py`
- `app/agent/nodes/trace_node.py`
- `app/debug/clinical_execution_debug.py`

## Hierarchy recommendation
- Keep separate contracts for runtime, formula, provenance, optimization, and developer-debug traces.
- Consolidate through adapters, not class deletion, during later migration phases.
