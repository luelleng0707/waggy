"""
Legacy response compatibility adapter (Phase 3).

The FormulaGraph ExportNode calls assemble_frontend_response so the public
analyze JSON contract stays identical for the frontend and Validation Console.

Clinical fields are produced by the same assembler + wrapped engines as before.
Additive debug keys (formula_graph, formula_execution_trace) are optional.
"""

from __future__ import annotations

from typing import Any

from app.agent.assessment_result import AssessmentResult


def assessment_to_legacy_json(result: AssessmentResult) -> dict[str, Any]:
    """Return the public analyze payload from an AssessmentResult."""
    return result.to_analyze_dict()


def strip_additive_debug(analyze: dict[str, Any]) -> dict[str, Any]:
    """Remove Phase-3-only debug keys for strict byte compares if needed."""
    out = dict(analyze)
    debug = dict(out.get("debug") or {})
    for key in ("formula_graph", "formula_execution_trace", "assessment_validation"):
        debug.pop(key, None)
    out["debug"] = debug
    return out
