"""Phase Σ — entity-first scientific warehouse (storage format ≠ formula views)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


def slug_id(prefix: str, *parts: str) -> str:
    raw = "_".join(str(p or "").strip().lower() for p in parts if str(p or "").strip())
    raw = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return f"{prefix}_{raw}" if raw else f"{prefix}_unknown"


@dataclass
class Breed:
    breed_id: str
    name: str
    size: str = ""
    body_type: str = ""
    coat_type: str = ""
    energy: str = ""
    weakness_group: str = ""
    skull_type: str = ""
    climate: str = ""
    lifespan: str = ""
    function_group: str = ""


@dataclass
class Condition:
    condition_id: str
    name: str
    domain: str = ""


@dataclass
class Trait:
    trait_id: str
    category: str
    value: str


@dataclass
class Ingredient:
    ingredient_id: str
    name: str


@dataclass
class Product:
    product_id: str  # commercial SKU kept as id for parity
    brand: str = ""
    category: str = ""
    subcategory: str = ""
    product_name: str = ""
    status: str = "active"
    props: dict[str, Any] = field(default_factory=dict)


@dataclass
class Paper:
    paper_id: str
    title: str = ""
    url: str = ""
    year: str = ""
    evidence_level: str = ""


@dataclass
class BreedConditionRel:
    breed_id: str
    condition_id: str
    prevalence: str = ""
    evidence_level: str = ""
    confidence: str = ""
    paper_id: str = ""
    sample_population: str = ""
    sample_size: str = ""
    source_quote: str = ""
    source_name: str = ""
    source_url: str = ""
    year: str = ""
    notes: str = ""


@dataclass
class TraitConditionRel:
    trait_id: str
    condition_id: str
    prevalence: str = ""
    evidence_level: str = ""
    confidence: str = ""
    paper_id: str = ""
    sample_population: str = ""
    sample_size: str = ""
    source_quote: str = ""
    source_name: str = ""
    source_url: str = ""
    year: str = ""
    notes: str = ""


def entity_to_row(obj: Any) -> dict[str, Any]:
    d = asdict(obj)
    props = d.pop("props", None)
    if isinstance(props, dict):
        d.update({k: v for k, v in props.items() if k not in d})
    return {k: ("" if v is None else v) for k, v in d.items()}
