"""Pipeline-level trace assembly utilities."""

from __future__ import annotations

from repository.mathematics.models import MathematicsRuntimeResult

from .execution_tree import build_execution_tree
from .formula_trace import build_formula_trace
from .models import CodeReference, ExecutionTrace, FormulaTrace, WarehouseTraceRow


def build_pipeline_trace(result: MathematicsRuntimeResult) -> ExecutionTrace:
    all_formula_traces: list[FormulaTrace] = []
    for assessment in result.assessments:
        condition_id = assessment.condition_id
        upstream: tuple[str, ...] = tuple()
        for idx, raw_trace in enumerate(assessment.formula_traces):
            item = build_formula_trace(condition_id=condition_id, trace_idx=idx, formula_trace=raw_trace, upstream_trace_ids=upstream)
            upstream = upstream + (item.trace_id,)
            all_formula_traces.append(item)

    tree = build_execution_tree(tuple(all_formula_traces))
    warnings = tuple(sorted(set([warning for trace in all_formula_traces for warning in trace.warnings if warning])))
    final_outputs = {
        assessment.condition_id: assessment.estimated_prevalence for assessment in result.assessments
    }
    warehouse_rows: list[WarehouseTraceRow] = []
    code_refs: list[CodeReference] = []
    for trace in all_formula_traces:
        warehouse_rows.extend(list(trace.warehouse_trace_rows))
        if trace.code_reference is not None:
            code_refs.append(trace.code_reference)
    return ExecutionTrace(
        run_id=result.trace.run_id,
        input_summary="EvidenceGraph -> MathematicalAssessment[]",
        formula_traces=tuple(all_formula_traces),
        execution_tree=tree,
        warehouse_trace=tuple(warehouse_rows),
        code_references=tuple(code_refs),
        final_outputs=final_outputs,
        warnings=warnings,
        errors=tuple(),
    )
