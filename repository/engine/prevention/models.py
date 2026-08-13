"""Prevention engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PreventionContext:
    interventions: tuple[dict, ...] = field(default_factory=tuple)
