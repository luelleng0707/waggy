"""Markdown reporting for execution traces and audits."""

from __future__ import annotations

from .models import ExecutionTrace, FormulaConstantAuditRow


def render_execution_trace_markdown(trace: ExecutionTrace) -> str:
    lines = [
        "# Mathematical Execution Trace",
        "",
        f"- Run ID: `{trace.run_id}`",
        f"- Input summary: {trace.input_summary}",
        "",
        "## Final Outputs",
    ]
    for key, value in sorted(trace.final_outputs.items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Formula Chain"])
    for item in trace.formula_traces:
        lines.extend(
            [
                f"- `{item.formula_id}:{item.formula_version}` ({item.formula_name})",
                f"  - Status: `{item.status}`",
                f"  - Equation: `{item.equation}`",
                f"  - Substitution: `{item.substituted_equation}`",
                f"  - Output: `{item.output_variable} = {item.output_value}`",
            ]
        )
    if trace.warnings:
        lines.extend(["", "## Warnings"])
        for warning in trace.warnings:
            lines.append(f"- `{warning}`")
    if trace.errors:
        lines.extend(["", "## Errors"])
        for error in trace.errors:
            lines.append(f"- `{error}`")
    return "\n".join(lines)


def render_constant_audit_markdown(rows: tuple[FormulaConstantAuditRow, ...]) -> str:
    lines = ["# FORMULA_CONSTANT_AUDIT", ""]
    if not rows:
        lines.append("- No constants flagged.")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            (
                f"- constant={row.constant} file={row.file} function={row.function or 'n/a'} "
                f"line={row.line} formula={row.formula} classification={row.classification or 'UNKNOWN'} "
                f"provenance={row.provenance or 'UNSPECIFIED'} status={row.status}"
            )
        )
    return "\n".join(lines)
