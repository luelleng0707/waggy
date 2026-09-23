"""Typed breed/trait knowledge contract.

Storage-agnostic. No pandas, CSV paths, MongoDB, FastAPI, or Ω12.

Core join identity remains the canonical display name. `breed_id` is the
warehouse key only and is not used as a FormulaGraph join key here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

# Column names that survive the current biology pivot onto each breed row.
# Must match app.data.native_loader.TRAIT_TABLES value columns.
TRAIT_NAMES: tuple[str, ...] = (
    "size",
    "body_type",
    "coat_type",
    "energy",
    "skull_type",
    "climate",
    "lifespan",
    "weakness_group",
    "function_group",
)


@dataclass(frozen=True, slots=True)
class BreedTraitFact:
    """One pivoted trait that already exists on the runtime breed row.

    Does not carry discarded CSV fact_id / papers / per-trait status.
    Empty values are omitted by the adapter, not stored as invented facts.
    """

    trait_name: str
    trait_value: str


@dataclass(frozen=True, slots=True)
class BreedKnowledge:
    """Projected breed knowledge as currently used by Core (name-join)."""

    breed_id: str
    canonical_name: str
    status: str
    species: str
    breed_group: str
    traits: tuple[BreedTraitFact, ...]

    def trait_map(self) -> dict[str, str]:
        return {item.trait_name: item.trait_value for item in self.traits}

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BreedCatalog(Protocol):
    """Knowledge provider. Not a universal breed matcher.

    `get_by_canonical_name` is exact/casefold on canonical_name only.
    Callers that currently use substring matching must keep that logic.
    """

    @property
    def warehouse_version(self) -> str: ...

    def normalize_name(self, raw: str) -> str: ...

    def all_breeds(self) -> tuple[BreedKnowledge, ...]: ...

    def get_by_canonical_name(self, name: str) -> BreedKnowledge | None: ...
