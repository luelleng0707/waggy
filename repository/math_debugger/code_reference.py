"""Code reference extraction for formula traces."""

from __future__ import annotations

from .models import CodeReference


def build_code_reference(
    python_file: str,
    python_function: str,
    source_line_start: int,
    source_line_end: int,
) -> CodeReference:
    return CodeReference(
        python_file=python_file,
        python_function=python_function,
        source_line_start=source_line_start,
        source_line_end=source_line_end,
    )
