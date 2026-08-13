"""Domain repositories — joins live here; FormulaGraph only calculates."""

from __future__ import annotations

import csv
from pathlib import Path

from app.data.native_loader import PACKAGE_TIERS, PRODUCT_DEFAULTS


def _wh(root: Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    from app.core.paths import WAREHOUSE

    return WAREHOUSE


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class BreedRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "breed"

    def breeds(self) -> list[dict[str, str]]:
        return _rows(self.sci / "breeds.csv")

    def get_breed(self, breed_id_or_name: str) -> dict[str, str] | None:
        key = str(breed_id_or_name or "").strip().lower()
        for r in self.breeds():
            if r.get("breed_id", "").lower() == key:
                return r
            name = (r.get("breed_name") or r.get("name") or "").lower()
            if name == key:
                return r
        return None

    def breed_conditions(self, breed_id: str | None = None) -> list[dict[str, str]]:
        rows = _rows(self.sci / "breed_conditions.csv")
        if breed_id:
            rows = [r for r in rows if r.get("breed_id") == breed_id]
        return rows

    def breed_traits(self, breed_id: str | None = None) -> list[dict[str, str]]:
        breeds = self.breeds()
        traits = _rows(self.root / "science" / "physiology" / "traits.csv")
        tid = {(r.get("category", ""), r.get("value", "")): r.get("trait_id", "") for r in traits}
        cat_cols = (
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
        rows: list[dict[str, str]] = []
        for b in breeds:
            bid = b.get("breed_id", "")
            if breed_id and bid != breed_id:
                continue
            for col in cat_cols:
                val = (b.get(col) or "").strip()
                if not val:
                    continue
                trait_id = tid.get((col, val), "")
                if trait_id:
                    rows.append({"breed_id": bid, "trait_id": trait_id})
        return rows

    def trait_conditions(self, trait_id: str | None = None) -> list[dict[str, str]]:
        rows = _rows(self.sci / "trait_conditions.csv")
        if trait_id:
            rows = [r for r in rows if r.get("trait_id") == trait_id]
        return rows


class IngredientRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "ingredient"

    def ingredients(self) -> list[dict[str, str]]:
        return _rows(self.sci / "ingredients.csv")

    def condition_links(self) -> list[dict[str, str]]:
        return _rows(self.sci / "condition_ingredients.csv")

    def mechanisms(self) -> list[dict[str, str]]:
        return _rows(self.sci / "ingredient_mechanisms.csv")

    def aliases(self) -> list[dict[str, str]]:
        return _rows(self.sci / "ingredient_aliases.csv")


class NutritionRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "nutrition"

    def food_nutrients(self) -> list[dict[str, str]]:
        return _rows(self.sci / "food_nutrients.csv")

    def food_sources(self) -> list[dict[str, str]]:
        return _rows(self.sci / "food_sources.csv")

    def nutrient_priorities(self) -> list[dict[str, str]]:
        return _rows(self.sci / "nutrient_priorities.csv")


class ProductRepository:
    """Reads ONLY production product tables under science/product/."""

    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "product"

    def products(self) -> list[dict[str, str]]:
        return _rows(self.sci / "PRODUCT_CATALOG.csv")

    def catalog(self) -> list[dict[str, str]]:
        return self.products()

    def components(self) -> list[dict[str, str]]:
        return _rows(self.sci / "PRODUCT_COMPONENTS.csv")

    def pricing(self) -> list[dict[str, str]]:
        return _rows(self.sci / "PRODUCT_PRICING.csv")

    def feeding(self) -> list[dict[str, str]]:
        return _rows(self.sci / "PRODUCT_FEEDING_RULES.csv")

    def functions(self) -> list[dict[str, str]]:
        return _rows(self.sci / "PRODUCT_FUNCTIONS.csv")

    def treat_bakery(self) -> list[dict[str, str]]:
        return _rows(self.sci / "TREAT_BAKERY.csv")

    def package_tiers(self) -> list[dict[str, str]]:
        return PACKAGE_TIERS.to_dict(orient="records")

    def product_defaults(self) -> dict[str, str]:
        return {str(r["key"]): str(r["product_id"]) for _, r in PRODUCT_DEFAULTS.iterrows()}


class ConditionRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "condition"

    def conditions(self) -> list[dict[str, str]]:
        return _rows(self.sci / "conditions.csv")

    def protocols(self) -> list[dict[str, str]]:
        return _rows(self.sci / "condition_protocols.csv")

    def timelines(self) -> list[dict[str, str]]:
        return _rows(self.sci / "clinical_timelines.csv")

    def grooming(self) -> list[dict[str, str]]:
        return _rows(self.sci / "grooming_observations.csv")


# Back-compat name used by DomainWarehouse
PreventionRepository = ConditionRepository


class PhysiologyRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "physiology"

    def traits(self) -> list[dict[str, str]]:
        return _rows(self.sci / "traits.csv")

    def trait_purposes(self) -> list[dict[str, str]]:
        return [r for r in _rows(self.sci / "trait_science.csv") if r.get("record_kind") == "purpose"]

    def trait_benefits(self) -> list[dict[str, str]]:
        return _rows(self.sci / "trait_benefits.csv")

    def trait_interactions(self) -> list[dict[str, str]]:
        return _rows(self.root / "science" / "breed" / "mixed_breed_interactions.csv")


class InteractionRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "breed"

    def mixed_breed_interactions(self) -> list[dict[str, str]]:
        return _rows(self.sci / "mixed_breed_interactions.csv")

    def mixed_breed_matrix(self) -> list[dict[str, str]]:
        return _rows(self.sci / "mixed_breed_matrix.csv")


class EvidenceRepository:
    def __init__(self, warehouse_root: Path | str | None = None):
        self.root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.sci = self.root / "science" / "evidence"

    def papers(self) -> list[dict[str, str]]:
        return _rows(self.sci / "papers.csv")

    def clinical_evidence(self) -> list[dict[str, str]]:
        return _rows(self.sci / "clinical_evidence.csv")


class DomainWarehouse:
    """Facade over all domain repositories."""

    def __init__(self, warehouse_root: Path | str | None = None):
        root = _wh(Path(warehouse_root) if warehouse_root else None)
        self.breeds = BreedRepository(root)
        self.ingredients = IngredientRepository(root)
        self.nutrition = NutritionRepository(root)
        self.products = ProductRepository(root)
        self.conditions = ConditionRepository(root)
        self.prevention = self.conditions
        self.physiology = PhysiologyRepository(root)
        self.interactions = InteractionRepository(root)
        self.evidence = EvidenceRepository(root)
