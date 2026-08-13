"""HTML rendering for execution trace."""

from __future__ import annotations

from .models import ExecutionTrace


def render_execution_trace_html(trace: ExecutionTrace) -> str:
    rows = []
    for item in trace.formula_traces:
        rows.append(
            "<tr>"
            f"<td>{item.formula_id}</td>"
            f"<td>{item.formula_version}</td>"
            f"<td>{item.output_variable}</td>"
            f"<td>{item.output_value}</td>"
            f"<td>{item.status}</td>"
            "</tr>"
        )
    table_rows = "".join(rows)
    return (
        "<html><body>"
        f"<h1>Execution Trace {trace.run_id}</h1>"
        "<table border='1'>"
        "<thead><tr><th>Formula</th><th>Version</th><th>Output Variable</th><th>Output</th><th>Status</th></tr></thead>"
        f"<tbody>{table_rows}</tbody>"
        "</table>"
        "</body></html>"
    )
