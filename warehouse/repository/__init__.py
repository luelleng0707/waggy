"""Warehouse repository package — entity models + scientific accessors."""

from warehouse.repository.entities import (
    Breed,
    BreedConditionRel,
    Condition,
    Ingredient,
    Paper,
    Product,
    Trait,
    TraitConditionRel,
    entity_to_row,
    slug_id,
)
from warehouse.repository.scientific import ScientificRepository, get_scientific_repository
from warehouse.repository.domains import (
    BreedRepository,
    ConditionRepository,
    DomainWarehouse,
    EvidenceRepository,
    IngredientRepository,
    InteractionRepository,
    NutritionRepository,
    PhysiologyRepository,
    PreventionRepository,
    ProductRepository,
)

__all__ = [
    "Breed",
    "BreedConditionRel",
    "Condition",
    "Ingredient",
    "Paper",
    "Product",
    "Trait",
    "TraitConditionRel",
    "ScientificRepository",
    "DomainWarehouse",
    "BreedRepository",
    "ConditionRepository",
    "EvidenceRepository",
    "IngredientRepository",
    "NutritionRepository",
    "ProductRepository",
    "PreventionRepository",
    "PhysiologyRepository",
    "InteractionRepository",
    "entity_to_row",
    "get_scientific_repository",
    "slug_id",
]
