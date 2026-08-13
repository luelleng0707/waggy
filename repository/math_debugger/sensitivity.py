"""Parameter sensitivity analysis for audit-only usage."""

from __future__ import annotations

from dataclasses import dataclass

from .independent_replay import IndependentFormulaReplay
from .models import FormulaTrace, VariableTrace


@dataclass(frozen=True)
class SensitivityRow:
    trace_id: str
    formula_id: str
    parameter_name: str
    baseline_parameter: float
    baseline_result: float
    minus_10_result: float
    plus_10_result: float
    absolute_change_minus: float
    absolute_change_plus: float
    relative_change_minus: float
    relative_change_plus: float


class SensitivityAnalyzer:
    def __init__(self):
        self.replay = IndependentFormulaReplay()

    def analyze(self, trace: FormulaTrace) -> tuple[SensitivityRow, ...]:
        baseline = self.replay.replay_formula(trace)
        if baseline.status == "SKIP":
            return tuple()
        rows: list[SensitivityRow] = []
        for parameter in trace.parameter_variables:
            try:
                p_value = float(parameter.value)
            except Exception:
                continue
            minus_trace = _replace_parameter(trace, parameter.variable_name, p_value * 0.9)
            plus_trace = _replace_parameter(trace, parameter.variable_name, p_value * 1.1)
            minus = self.replay.replay_formula(minus_trace)
            plus = self.replay.replay_formula(plus_trace)
            baseline_value = baseline.replay_output
            rows.append(
                SensitivityRow(
                    trace_id=trace.trace_id,
                    formula_id=trace.formula_id,
                    parameter_name=parameter.variable_name,
                    baseline_parameter=p_value,
                    baseline_result=baseline_value,
                    minus_10_result=minus.replay_output,
                    plus_10_result=plus.replay_output,
                    absolute_change_minus=minus.replay_output - baseline_value,
                    absolute_change_plus=plus.replay_output - baseline_value,
                    relative_change_minus=((minus.replay_output - baseline_value) / baseline_value) if baseline_value else 0.0,
                    relative_change_plus=((plus.replay_output - baseline_value) / baseline_value) if baseline_value else 0.0,
                )
            )
        return tuple(rows)


def _replace_parameter(trace: FormulaTrace, name: str, value: float) -> FormulaTrace:
    params: list[VariableTrace] = []
    for item in trace.parameter_variables:
        if item.variable_name == name:
            params.append(
                VariableTrace(
                    variable_name=item.variable_name,
                    variable_type="float",
                    unit=item.unit,
                    value=value,
                    source=item.source,
                    allowed_range=item.allowed_range,
                    meaning=item.meaning,
                )
            )
        else:
            params.append(item)
    return FormulaTrace(
        trace_id=trace.trace_id,
        formula_id=trace.formula_id,
        formula_version=trace.formula_version,
        formula_name=trace.formula_name,
        status=trace.status,
        equation=trace.equation,
        substituted_equation=trace.substituted_equation,
        intermediate_calculations=trace.intermediate_calculations,
        output_variable=trace.output_variable,
        output_value=trace.output_value,
        unit=trace.unit,
        input_variables=trace.input_variables,
        parameter_variables=tuple(params),
        code_reference=trace.code_reference,
        warehouse_trace_rows=trace.warehouse_trace_rows,
        upstream_trace_ids=trace.upstream_trace_ids,
        warnings=trace.warnings,
    )
