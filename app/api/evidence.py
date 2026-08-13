"""Evidence and product lookup helpers — ports src/engine/evidenceEngine.js."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from app.agent.condition_lookup import condition_key, condition_matches
from app.agent.ingredient_engine import map_ingredients
from app.formulas.stages.optimization import _keys_match
from app.agent.utils import DataRepository, feeding_rule_for_product, ingredient_key, units_compatible

INGREDIENT_PRODUCT_TYPES = {
    "supplement",
    "treat",
    "homestyle_bakery",
    "fresh_food",
    "staple_food",
    "kibble",
}


def get_evidence_for_condition(repo: DataRepository, condition_name: str) -> list[dict[str, Any]]:
    key = condition_key(condition_name)
    results: list[dict[str, Any]] = []

    breed_df = repo.breed_conditions()
    if not breed_df.empty:
        for _, row in breed_df.iterrows():
            cond = str(row.get("condition") or "")
            ck = condition_key(cond)
            if ck == key or cond.lower() == condition_name.lower():
                results.append({
                    "type": "breed_observed",
                    "condition_key": ck,
                    "condition_name": cond,
                    "breed": row.get("breed"),
                    "prevalence": row.get("prevalence"),
                    "source_name": row.get("source_name"),
                    "source_quote": row.get("source_quote"),
                    "source_url": row.get("source_url"),
                })

    ci_df = repo.condition_ingredients()
    if not ci_df.empty:
        for _, row in ci_df.iterrows():
            cond = str(row.get("condition") or "")
            ck = condition_key(cond)
            if ck == key or cond.lower() == condition_name.lower():
                results.append({
                    "type": "ingredient_dose",
                    "condition_key": ck,
                    "condition_name": cond,
                    "ingredient_name": row.get("ingredient_name"),
                    "dose_per_kg": row.get("dose_per_kg"),
                    "unit": row.get("unit"),
                    "source_name": row.get("source_name"),
                    "source_quote": row.get("source_quote"),
                    "source_url": row.get("source_url"),
                })

    return results


def match_products_for_ingredients(
    repo: DataRepository,
    ingredients: list[dict[str, Any]],
    weight_kg: float = 20.0,
    past_products: list[Any] | None = None,
) -> list[dict[str, Any]]:
    """Port of src/engine/productEngine.js matchProducts."""
    catalog = repo.product_catalog()
    components = repo.product_components()
    pricing = repo.product_pricing()
    rules = repo.product_feeding_rules()
    if catalog.empty:
        return []

    past_names = {
        str(p.get("product_name") if isinstance(p, dict) else p).lower()
        for p in (past_products or [])
    }

    active = components[components["component_type"] == "active_ingredient"].copy() if not components.empty else pd.DataFrame()
    if not active.empty:
        active["ingredient_key"] = active["component_name"].map(
            lambda n: ingredient_key(str(n).replace("+", "_").replace("EPA+DHA", "omega_3"))
        )
        active["amount_per_unit"] = pd.to_numeric(active["value"], errors="coerce").fillna(0.0)

    results: list[dict[str, Any]] = []
    for ing in ingredients:
        ing_key = ingredient_key(str(ing.get("ingredient_key") or ing.get("ingredient_name") or ""))
        daily_dose = float(ing.get("daily_dose") or 0)
        target_unit = ing.get("unit") or "mg"

        for _, product in catalog.iterrows():
            ptype = str(product.get("product_type") or "").lower()
            if ptype not in INGREDIENT_PRODUCT_TYPES:
                continue
            pid = str(product.get("id") or product.get("product_id") or "")
            if active.empty:
                continue
            pis = active[active["product_id"] == pid]
            pi_row = None
            for _, pi in pis.iterrows():
                if _keys_match(ing_key, str(pi.get("ingredient_key") or "")):
                    pi_row = pi
                    break
            if pi_row is None:
                continue
            amount = float(pi_row.get("amount_per_unit") or 0)
            if amount <= 0:
                continue
            if not units_compatible(target_unit, pi_row.get("unit", "")):
                continue

            coverage = min(100, round((amount / daily_dose) * 100)) if daily_dose else 0
            if coverage <= 0:
                continue

            rule = feeding_rule_for_product(rules, pid, weight_kg)
            units_needed = math.ceil(daily_dose / amount) if amount else 1
            package_units = float(product.get("package_units") or 0)
            if package_units <= 0 and not pricing.empty:
                hit = pricing[pricing["product_id"] == pid]
                if not hit.empty:
                    package_units = float(hit.iloc[0].get("package_units") or 0)
            days_to_finish = package_units / max(units_needed, 1) if package_units > 0 else 0
            shelf = float(product.get("shelf_life_days") or 365)
            brand = str(product.get("brand") or "")
            name = str(product.get("product_name") or product.get("name") or "")
            score = coverage / 100.0
            if days_to_finish > shelf:
                score *= 0.6
            if "Wagtopia" in brand:
                score += 0.15
            is_past = name.lower() in past_names
            if is_past and coverage >= 70:
                score += 0.25

            results.append({
                "product_id": pid,
                "product_name": name,
                "brand": brand,
                "product_type": ptype,
                "ingredient_name": ing.get("ingredient_name") or ing.get("ingredient"),
                "ingredient_key": ing_key,
                "active_ingredients": [
                    {
                        "name": r.get("component_name"),
                        "amount": float(r.get("amount_per_unit") or 0),
                        "unit": r.get("unit"),
                    }
                    for _, r in pis.sort_values(
                        by="ingredient_order_rank" if "ingredient_order_rank" in pis.columns else pis.columns[0]
                    ).iterrows()
                ] if not pis.empty else [],
                "units_needed_daily": units_needed,
                "suggested_usage": (
                    f"{rule['daily_amount']} {rule['daily_unit']}/day"
                    if rule
                    else f"{units_needed}/{product.get('unit_type') or 'unit'}/day"
                ),
                "days_to_finish": round(days_to_finish),
                "coverage_percent": coverage,
                "score": round(score * 1000) / 1000,
                "recommendation_note": (
                    "Based on your previous purchase — maintaining proven coverage."
                    if is_past and coverage >= 70
                    else (
                        "For optimal coverage, we recommend this upgraded formula."
                        if coverage < 70
                        else "Best match for your dog's profile."
                    )
                ),
            })

    seen: set[str] = set()
    deduped = []
    for r in results:
        k = f"{r['product_name']}{r['ingredient_name']}"
        if k in seen:
            continue
        seen.add(k)
        deduped.append(r)
    deduped.sort(key=lambda x: -x["score"])
    return deduped


def get_products_for_condition(
    repo: DataRepository,
    condition_name: str,
    weight_kg: float = 20.0,
) -> list[dict[str, Any]]:
    fake_risk = [{
        "condition_name": condition_name,
        "condition_key": condition_key(condition_name),
        "risk_percent": 50,
    }]
    ings = map_ingredients(fake_risk, weight_kg, repo)
    return match_products_for_ingredients(repo, ings, weight_kg)
