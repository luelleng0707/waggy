"""Optimization engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OptimizationContext:
    candidates: tuple[dict, ...] = field(default_factory=tuple)
