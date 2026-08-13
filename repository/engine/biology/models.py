"""Biology engine data models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BiologyContext:
    breed_ids: tuple[str, ...] = field(default_factory=tuple)
    traits: tuple[dict, ...] = field(default_factory=tuple)
