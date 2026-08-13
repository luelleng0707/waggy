"""Phase Σ scientific repository — entity accessors over canonical warehouse CSVs.

CSV is a storage format. Callers ask for entities / relationships, not file paths.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from warehouse.repository.entities import (
    Breed,
    BreedConditionRel,
    Condition,
    Ingredient,
    Paper,
    Product,
    Trait,
    TraitConditionRel,
)


def _warehouse_root(root: Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    from app.core.paths import WAREHOUSE

    return WAREHOUSE


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class ScientificRepository:
    """Entity-first API over warehouse/science/{domain}."""

    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _warehouse_root(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science"
        self.run = self.sci / "runtime"

    def breeds(self) -> list[Breed]:
        return [
            Breed(
                breed_id=r.get("breed_id", ""),
                name=r.get("breed_name") or r.get("name", ""),
                size=r.get("size", ""),
                body_type=r.get("body_type", ""),
                coat_type=r.get("coat_type", ""),
                energy=r.get("energy", ""),
                weakness_group=r.get("weakness_group", ""),
                skull_type=r.get("skull_type", ""),
                climate=r.get("climate", ""),
                lifespan=r.get("lifespan", ""),
                function_group=r.get("function_group", ""),
            )
            for r in _read_rows(self.sci / "breed" / "breeds.csv")
            if r.get("breed_id") or r.get("breed_name") or r.get("name")
        ]

    def conditions(self) -> list[Condition]:
        return [
            Condition(
                condition_id=r.get("condition_id", ""),
                name=r.get("condition_name") or r.get("name", ""),
                domain=r.get("body_system") or r.get("domain", ""),
            )
            for r in _read_rows(self.sci / "condition" / "conditions.csv")
            if r.get("condition_id")
        ]

    def traits(self) -> list[Trait]:
        return [
            Trait(
                trait_id=r.get("trait_id", ""),
                category=r.get("category", ""),
                value=r.get("value", ""),
            )
            for r in _read_rows(self.sci / "physiology" / "traits.csv")
            if r.get("trait_id")
        ]

    def ingredients(self) -> list[Ingredient]:
        return [
            Ingredient(
                ingredient_id=r.get("ingredient_id", ""),
                name=r.get("ingredient_name") or r.get("name", ""),
            )
            for r in _read_rows(self.sci / "ingredient" / "ingredients.csv")
            if r.get("ingredient_id")
        ]

    def products(self) -> list[Product]:
        return [
            Product(
                product_id=r.get("product_id", ""),
                brand=r.get("brand", ""),
                category=r.get("category", ""),
                subcategory=r.get("subcategory", ""),
                product_name=r.get("product_name", ""),
                status=r.get("status", "active"),
            )
            for r in _read_rows(self.sci / "product" / "PRODUCT_CATALOG.csv")
            if r.get("product_id")
        ]

    def papers(self) -> list[Paper]:
        return [
            Paper(
                paper_id=r.get("paper_id", ""),
                title=r.get("title", ""),
                url=r.get("url", ""),
                year=r.get("year", ""),
                evidence_level=r.get("evidence_level", ""),
            )
            for r in _read_rows(self.sci / "evidence" / "papers.csv")
            if r.get("paper_id")
        ]

    def get_breed(self, breed_id_or_name: str) -> Breed | None:
        key = str(breed_id_or_name or "").strip().lower()
        for b in self.breeds():
            if b.breed_id.lower() == key or b.name.lower() == key:
                return b
        return None

    def get_condition(self, condition_id_or_name: str) -> Condition | None:
        key = str(condition_id_or_name or "").strip().lower()
        for c in self.conditions():
            if c.condition_id.lower() == key or c.name.lower() == key:
                return c
        return None

    def get_trait(self, trait_id: str) -> Trait | None:
        key = str(trait_id or "").strip().lower()
        for t in self.traits():
            if t.trait_id.lower() == key:
                return t
        return None

    def get_ingredient(self, ingredient_id_or_name: str) -> Ingredient | None:
        key = str(ingredient_id_or_name or "").strip().lower()
        for i in self.ingredients():
            if i.ingredient_id.lower() == key or i.name.lower() == key:
                return i
        return None

    def get_product(self, product_id: str) -> Product | None:
        key = str(product_id or "").strip()
        for p in self.products():
            if p.product_id == key:
                return p
        return None

    def get_condition_relationship(
        self, *, breed_id: str | None = None, condition_id: str | None = None
    ) -> list[BreedConditionRel]:
        path = self.sci / "breed" / "breed_conditions.csv"
        if not path.exists():
            path = self.sci / "breed_condition.csv"
        rows = _read_rows(path)
        out: list[BreedConditionRel] = []
        for r in rows:
            if breed_id and r.get("breed_id") != breed_id:
                continue
            if condition_id and r.get("condition_id") != condition_id:
                continue
            out.append(
                BreedConditionRel(
                    breed_id=r.get("breed_id", ""),
                    condition_id=r.get("condition_id", ""),
                    prevalence=r.get("prevalence", ""),
                    evidence_level=r.get("evidence_level", ""),
                    confidence=r.get("confidence", ""),
                    paper_id=r.get("paper_id", ""),
                    sample_population=r.get("sample_population", ""),
                    sample_size=r.get("sample_size", ""),
                    source_quote=r.get("source_quote", ""),
                    source_name=r.get("source_name", ""),
                    source_url=r.get("source_url", ""),
                    year=r.get("year", ""),
                    notes=r.get("notes", ""),
                )
            )
        return out

    def get_trait_condition_relationship(
        self, *, trait_id: str | None = None, condition_id: str | None = None
    ) -> list[TraitConditionRel]:
        path = self.sci / "breed" / "trait_conditions.csv"
        if not path.exists():
            path = self.sci / "trait_condition.csv"
        rows = _read_rows(path)
        out: list[TraitConditionRel] = []
        for r in rows:
            if trait_id and r.get("trait_id") != trait_id:
                continue
            if condition_id and r.get("condition_id") != condition_id:
                continue
            out.append(
                TraitConditionRel(
                    trait_id=r.get("trait_id", ""),
                    condition_id=r.get("condition_id", ""),
                    prevalence=r.get("prevalence", ""),
                    evidence_level=r.get("evidence_level", ""),
                    confidence=r.get("confidence", ""),
                    paper_id=r.get("paper_id", ""),
                    sample_population=r.get("sample_population", ""),
                    sample_size=r.get("sample_size", ""),
                    source_quote=r.get("source_quote", ""),
                    source_name=r.get("source_name", ""),
                    source_url=r.get("source_url", ""),
                    year=r.get("year", ""),
                    notes=r.get("notes", ""),
                )
            )
        return out

    def get_relationship(self, kind: str, **filters: str) -> list[dict[str, Any]]:
        """Generic relationship fetch by science CSV stem or domain path."""
        candidates = [
            self.sci / f"{kind}.csv",
            self.sci / "breed" / f"{kind}.csv",
            self.sci / "condition" / f"{kind}.csv",
            self.sci / "ingredient" / f"{kind}.csv",
            self.sci / "nutrition" / f"{kind}.csv",
            self.sci / "product" / f"{kind}.csv",
            self.sci / "product" / f"{kind.upper()}.csv",
            self.sci / "physiology" / f"{kind}.csv",
            self.sci / "evidence" / f"{kind}.csv",
            self.sci / "runtime" / f"{kind}.csv",
        ]
        path = next((p for p in candidates if p.exists()), candidates[0])
        rows = _read_rows(path)
        if not filters:
            return rows
        out = []
        for r in rows:
            if all(str(r.get(k, "")) == str(v) for k, v in filters.items()):
                out.append(r)
        return out

    def get_parameter(self, key: str, default: str = "") -> str:
        for r in _read_rows(self.run / "parameters.csv"):
            if r.get("key") == key or r.get("parameter") == key:
                return str(r.get("value") or r.get("default") or default)
        return default


@lru_cache(maxsize=1)
def get_scientific_repository() -> ScientificRepository:
    return ScientificRepository()
