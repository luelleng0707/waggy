"""
Port of src/engine/pipelineEngine.js buildPipelineTrace + variableMap labels/files.
"""

from __future__ import annotations

from typing import Any

from app.agent.condition_lookup import condition_candidates, condition_matches
from app.agent.ingredient_engine import _condition_ingredient_rows
from app.agent.package_detail import activities_for_condition
from app.agent.utils import DataRepository

PIPELINE_STAGES = [
    "biology",
    "health_risk",
    "management",
    "nutrition",
    "products",
    "feeding_plan",
]

VARIABLE_MAP: dict[str, dict[str, Any]] = {
    "biology": {
        "label": "Recognition Destructuring & Ancestry",
        "files": [
            "BREEDS",
            "MIXED_BREED_MATRIX",
            "MIXED_BREED_INTERACTIONS",
            "TRAIT_PURPOSES",
            "ENVIRONMENTAL_MATRICES",
        ],
    },
    "health_risk": {
        "label": "Epidemiology Pools & Interaction Codes",
        "files": [
            "BREED_CONDITIONS",
            "BODYTYPE_CONDITIONS",
            "COATTYPE_CONDITIONS",
            "TRAIT_INTERACTIONS",
        ],
    },
    "management": {
        "label": "Preventative Management",
        "files": [
            "TRAIT_BENEFITS",
            "CONDITION_ACTIVITIES",
            "ACTIVITY_EVIDENCE",
        ],
    },
    "nutrition": {
        "label": "Clinical Ingredient Conversion",
        "files": [
            "CONDITION_INGREDIENTS",
            "INGREDIENT_EVIDENCE",
            "INGREDIENT_MECHANISMS",
            "NATURAL_FOOD_SOURCES",
            "NUTRIENT_PRIORITIES",
        ],
    },
    "products": {
        "label": "Inventory Fulfillment",
        "files": [
            "PRODUCT_CATALOG",
            "PRODUCT_COMPONENTS",
            "PRODUCT_PRICING",
            "PRODUCT_FEEDING_RULES",
        ],
    },
    "feeding_plan": {
        "label": "Feeding Plan Assembly",
        "files": [],
    },
}

_STAPLE_TYPES = frozenset({"fresh_food", "staple_food", "kibble"})


def _management_lifestyle_count(risks: list[dict[str, Any]], repo: DataRepository) -> int:
    """stages.management.lifestyle_requirements.length — db.getActivities per risk."""
    total = 0
    for risk in risks:
        cond = risk.get("condition_name") or risk.get("condition_key")
        total += len(activities_for_condition(repo, str(cond or "")))
    return total


def _orphan_conditions(
    risks: list[dict[str, Any]],
    ingredients: list[dict[str, Any]],
    repo: DataRepository,
) -> list[str]:
    """Port of buildNutritionStage orphan_conditions."""
    orphans: list[str] = []
    for risk in risks:
        cname = str(risk.get("condition_name") or "")
        if not cname:
            continue
        has_ing = any(
            any(str(c).lower() == cname.lower() for c in (ing.get("for_conditions") or []))
            for ing in ingredients
        )
        has_db = bool(_condition_ingredient_rows(repo, cname))
        if not has_ing and not has_db:
            orphans.append(cname)
    return orphans


def _unmapped_ingredient_names(
    ingredients: list[dict[str, Any]],
    raw_products: list[dict[str, Any]],
) -> list[str]:
    """Port of buildProductsStage unmapped_ingredient_targets."""
    unmapped: list[str] = []
    for ing in ingredients:
        ikey = str(ing.get("ingredient_key") or "").lower()
        iname = str(ing.get("ingredient_name") or "").lower()
        matched = any(
            str(p.get("ingredient_key") or "").lower() == ikey
            or str(p.get("ingredient_name") or "").lower() == iname
            for p in raw_products
        )
        if not matched:
            unmapped.append(ing.get("ingredient_name"))
    return unmapped


def _staple_products(repo: DataRepository) -> list[dict[str, Any]]:
    catalog = repo.product_catalog()
    if catalog.empty:
        return []
    out = []
    for _, row in catalog.iterrows():
        rec = row.to_dict()
        ptype = str(rec.get("product_type") or rec.get("category") or "").lower().replace(" ", "_")
        cat = str(rec.get("category") or "").lower()
        if ptype in _STAPLE_TYPES or "fresh" in cat or cat == "staple_food":
            out.append(rec)
    return out


def _feeding_plan_record_count(
    repo: DataRepository,
    raw_products: list[dict[str, Any]],
) -> int:
    """buildMonthlyPlan(items).length — staple always added when staples exist."""
    staples = _staple_products(repo)
    count = 1 if staples else 0
    supps = [p for p in raw_products if str(p.get("product_type") or "") == "supplement"][:2]
    treats = [
        p for p in raw_products
        if str(p.get("product_type") or "") in ("treat", "homestyle_bakery")
    ][:2]
    return count + len(supps) + len(treats)


def _enriched_product_count(raw_products: list[dict[str, Any]]) -> int:
    """enrichProductRecommendations groups by product_name; empty raw → 0."""
    if not raw_products:
        return 0
    names: set[str] = set()
    for p in raw_products:
        name = p.get("product_name")
        if name:
            names.add(str(name))
    return len(names)


def build_pipeline_trace(
    *,
    biology: dict[str, Any],
    risks: list[dict[str, Any]],
    ingredients: list[dict[str, Any]],
    raw_products: list[dict[str, Any]],
    repo: DataRepository,
) -> list[dict[str, Any]]:
    """Port of pipelineEngine.buildPipelineTrace(stages)."""
    record_by_stage = {
        "biology": len(biology.get("resolved_breeds") or []),
        "health_risk": len(risks),
        "management": _management_lifestyle_count(risks, repo),
        "nutrition": len(ingredients),
        "products": _enriched_product_count(raw_products),
        "feeding_plan": _feeding_plan_record_count(repo, raw_products),
    }
    orphan_conditions = _orphan_conditions(risks, ingredients, repo)
    unmapped = _unmapped_ingredient_names(ingredients, raw_products)

    trace: list[dict[str, Any]] = []
    for stage in PIPELINE_STAGES:
        entry: dict[str, Any] = {
            "stage": stage,
            "label": VARIABLE_MAP.get(stage, {}).get("label", stage),
            "source_files": list(VARIABLE_MAP.get(stage, {}).get("files") or []),
            "record_counts": record_by_stage.get(stage),
        }
        # JS always attaches these keys for the stage (even when empty arrays).
        if stage == "nutrition":
            entry["orphan_conditions"] = orphan_conditions
        if stage == "products":
            entry["unmapped_ingredients"] = unmapped
        trace.append(entry)
    return trace
