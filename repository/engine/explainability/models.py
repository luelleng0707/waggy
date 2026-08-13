"""Explainability engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExplainabilityContext:
    trace_items: tuple[dict, ...] = field(default_factory=tuple)
