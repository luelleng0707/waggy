"""Structured tool failures. Never leak stack traces, SQL, or filesystem paths."""

from __future__ import annotations

from typing import Any


class ToolFailure(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        field: str | None = None,
        status: int = 400,
    ) -> None:
        self.code = code
        self.field = field
        self.status = status
        super().__init__(message)

    def as_error_item(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "field": self.field,
        }


UNKNOWN_TOOL = "UNKNOWN_TOOL"
INVALID_TOOL_INPUT = "INVALID_TOOL_INPUT"
TOOL_NOT_ALLOWED = "TOOL_NOT_ALLOWED"
DOG_NOT_FOUND = "DOG_NOT_FOUND"
DOG_ACCESS_DENIED = "DOG_ACCESS_DENIED"
ANALYSIS_NOT_FOUND = "ANALYSIS_NOT_FOUND"
INVALID_ANALYSIS_REFERENCE = "INVALID_ANALYSIS_REFERENCE"
NOT_AVAILABLE = "NOT_AVAILABLE"
MISSING_EVIDENCE = "MISSING_EVIDENCE"
INVALID_PREFERENCE = "INVALID_PREFERENCE"
TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
COMPARISON_UNAVAILABLE = "COMPARISON_UNAVAILABLE"

HTTP_STATUS_BY_CODE = {
    UNKNOWN_TOOL: 400,
    INVALID_TOOL_INPUT: 400,
    TOOL_NOT_ALLOWED: 403,
    DOG_NOT_FOUND: 404,
    DOG_ACCESS_DENIED: 403,
    ANALYSIS_NOT_FOUND: 404,
    INVALID_ANALYSIS_REFERENCE: 400,
    NOT_AVAILABLE: 404,
    MISSING_EVIDENCE: 404,
    INVALID_PREFERENCE: 400,
    TOOL_EXECUTION_ERROR: 500,
    COMPARISON_UNAVAILABLE: 400,
}


def http_status_for_envelope(status: str, errors: list[Any] | None) -> int:
    if status == "ok":
        return 200
    if not errors:
        return 400
    first = errors[0]
    code = first.code if hasattr(first, "code") else first.get("code")
    return HTTP_STATUS_BY_CODE.get(str(code or ""), 400)
