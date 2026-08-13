"""Variable trace extraction."""

from __future__ import annotations

from .models import VariableTrace


def build_variable_traces(values: dict[str, float | int | str], source: str, unit: str = "") -> tuple[VariableTrace, ...]:
    traces = []
    for key in sorted(values):
        traces.append(
            VariableTrace(
                variable_name=key,
                variable_type=type(values[key]).__name__,
                unit=unit,
                value=values[key],
                source=source,
            )
        )
    return tuple(traces)
