"""Epidemiology engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EpidemiologyContext:
    conditions: tuple[dict, ...] = field(default_factory=tuple)
