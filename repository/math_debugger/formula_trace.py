"""Formula trace conversion from mathematics runtime traces."""

from __future__ import annotations

from repository.mathematics.models import MathematicalFormulaTrace

from .code_reference import build_code_reference
from .models import FormulaTrace
from .variable_trace import build_variable_traces
from .warehouse_trace import build_warehouse_trace_rows


def build_formula_trace(
    condition_id: str,
    trace_idx: int,
    formula_trace: MathematicalFormulaTrace,
    upstream_trace_ids: tuple[str, ...],
) -> FormulaTrace:
    trace_id = f"{condition_id}:{formula_trace.formula_id}:{formula_trace.formula_version}:{trace_idx}"
    warehouse_rows = build_warehouse_trace_rows(
        warehouse_row_ids=formula_trace.warehouse_row_ids,
        evidence_ids=formula_trace.evidence_ids,
        paper_names=formula_trace.paper_names,
        paper_links=formula_trace.paper_links,
        scientific_quotes=formula_trace.scientific_quotes,
    )
    intermediate = tuple([f"{key} = {value}" for key, value in sorted(formula_trace.intermediate_values.items())])
    if not intermediate:
        intermediate = ("NO_INTERMEDIATE_VALUES_EXPOSED",)
    return FormulaTrace(
        trace_id=trace_id,
        formula_id=formula_trace.formula_id,
        formula_version=formula_trace.formula_version,
        formula_name=formula_trace.formula_name,
        status=formula_trace.status or "ACTIVE",
        equation=formula_trace.equation,
        substituted_equation=formula_trace.substituted_equation or "SUBSTITUTION_NOT_CAPTURED",
        intermediate_calculations=intermediate,
        output_variable=formula_trace.output_variable or "output",
        output_value=formula_trace.output,
        unit=formula_trace.unit,
        input_variables=build_variable_traces(formula_trace.inputs, source="formula_inputs"),
        parameter_variables=build_variable_traces(formula_trace.parameter_values, source="formula_parameters"),
        code_reference=build_code_reference(
            python_file=formula_trace.python_file,
            python_function=formula_trace.python_function,
            source_line_start=formula_trace.source_line_start,
            source_line_end=formula_trace.source_line_end,
        ),
        warehouse_trace_rows=warehouse_rows,
        upstream_trace_ids=upstream_trace_ids,
        warnings=tuple(),
    )
