"""
Port of src/engine/bundleEngine.js — monthly_plan and yearly_plan assembly.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from app.agent.utils import DataRepository, calculate_unit_economics, feeding_rule_for_product, js_round

STAPLE_TYPES = frozenset({"fresh_food", "staple_food", "kibble"})


def _product_type_from_category(category: str, subcategory: str = "") -> str:
    if category == "Fresh Food":
        return "fresh_food"
    if category == "Nutritional Supplements":
        return "supplement"
    if category in ("Homestyle Bakery", "All-Natural Treats"):
        return "treat"
    category_l = str(category or "").lower()
    sub = str(subcategory or "").lower()
    if "fresh" in sub or "fresh" in category_l:
        return "fresh_food"
    if "supplement" in category_l:
        return "supplement"
    if "treat" in category_l or "bakery" in category_l:
        return "treat"
    return sub or "product"


def _all_products(repo: DataRepository) -> list[dict[str, Any]]:
    """Mirror db.getAllProducts() from csvLoader.buildProductCatalog."""
    catalog = repo.product_catalog()
    if catalog.empty:
        return []
    pricing = repo.product_pricing()
    products: list[dict[str, Any]] = []
    for _, row in catalog.iterrows():
        rec = row.to_dict()
        if str(rec.get("status") or "active") not in ("active", ""):
            continue
        pid = str(rec.get("product_id") or "")
        price = 0.0
        package_units = 1.0
        unit_type = "unit"
        if not pricing.empty and pid:
            prow = pricing[pricing["product_id"] == pid]
            if not prow.empty:
                price = float(prow.iloc[0].get("list_price_rmb") or 0)
                package_units = float(prow.iloc[0].get("package_units") or 1)
                unit_type = str(prow.iloc[0].get("unit_label") or "unit")
        unit_cost = calculate_unit_economics(pricing, pid) if pid else price
        category = str(rec.get("category") or "")
        subcategory = str(rec.get("subcategory") or "")
        shelf_life_days = 365
        for ext_path in (
            "product_portfolio/EXT_SUPPLEMENTS.csv",
            "product_portfolio/EXT_TREATS_BAKERY.csv",
        ):
            ext = repo.load_csv(ext_path)
            if ext.empty or "product_id" not in ext.columns:
                continue
            hit = ext[ext["product_id"] == pid]
            if not hit.empty and "shelf_life_days" in hit.columns:
                try:
                    shelf_life_days = int(float(hit.iloc[0].get("shelf_life_days") or 365))
                except (TypeError, ValueError):
                    shelf_life_days = 365
                break
        products.append({
            "id": pid,
            "product_id": pid,
            "product_name": rec.get("product_name"),
            "brand": rec.get("brand"),
            "category": category,
            "subcategory": subcategory,
            "product_type": _product_type_from_category(category, subcategory),
            "price": price,
            "list_price_rmb": price,
            "package_units": package_units,
            "unit_type": unit_type,
            "unit_cost_per_bag": unit_cost,
            "shelf_life_days": shelf_life_days,
        })
    return products


def _is_staple_product(product: dict[str, Any]) -> bool:
    return str(product.get("product_type") or "") in STAPLE_TYPES


def get_staple_products(repo: DataRepository) -> list[dict[str, Any]]:
    return [p for p in _all_products(repo) if _is_staple_product(p)]


def get_feeding_amount(
    product: dict[str, Any],
    weight_kg: float,
    repo: DataRepository,
) -> dict[str, Any]:
    """Port of bundleEngine.getFeedingAmount."""
    pid = str(product.get("id") or product.get("product_id") or "")
    rule = feeding_rule_for_product(repo.product_feeding_rules(), pid, weight_kg) if pid else None
    if rule:
        daily = rule["daily_amount"]
        if isinstance(daily, float) and daily == int(daily):
            daily = int(daily)
        return {"daily": daily, "unit": rule["daily_unit"]}
    if _is_staple_product(product):
        return {"daily": js_round(weight_kg * 20), "unit": "g"}
    return {"daily": 1, "unit": product.get("unit_type") or "unit"}


def build_monthly_plan(
    products: list[dict[str, Any]],
    weight_kg: float,
    age_stage: str,
    repo: DataRepository,
) -> dict[str, Any]:
    """Port of bundleEngine.buildMonthlyPlan."""
    del age_stage
    staples = get_staple_products(repo)
    supps = [p for p in products if str(p.get("product_type") or "") == "supplement"][:2]
    treats = [
        p for p in products
        if str(p.get("product_type") or "") in ("treat", "homestyle_bakery")
    ][:2]

    best_staple = next(
        (p for p in staples if p.get("brand") == "Wagtopia" and p.get("subcategory") == "fresh_combo"),
        None,
    )
    if not best_staple:
        best_staple = next((p for p in staples if p.get("brand") == "Wagtopia"), None)
    if not best_staple and staples:
        best_staple = staples[0]

    items: list[dict[str, Any]] = []
    if best_staple:
        feed = get_feeding_amount(best_staple, weight_kg, repo)
        daily = float(feed["daily"])
        monthly_total = daily * 30
        grams_per_bag = 200
        bags = max(1, math.ceil(monthly_total / grams_per_bag))
        unit_cost = best_staple.get("unit_cost_per_bag") or (
            float(best_staple.get("price") or 0) / float(best_staple.get("package_units") or 1)
        )
        shelf = int(best_staple.get("shelf_life_days") or 365)
        items.append({
            "product_name": best_staple.get("product_name"),
            "product_type": best_staple.get("product_type"),
            "daily": f"{feed['daily']}{feed['unit']}/day",
            "monthly": f"{int(monthly_total) if monthly_total == int(monthly_total) else monthly_total}{feed['unit']}",
            "depletion": f"{bags} bag(s) exactly",
            "quantity": bags,
            "cost": js_round(bags * float(unit_cost)),
            "unit_cost_per_bag": unit_cost,
            "fresh_warning": f"Shelf life: {shelf} days" if shelf <= 60 else None,
        })

    for s in supps:
        feed = get_feeding_amount(s, weight_kg, repo)
        monthly_units = min(30, int(float(s.get("package_units") or 30)))
        items.append({
            "product_name": s.get("product_name"),
            "product_type": "supplement",
            "daily": s.get("suggested_usage") or f"{feed['daily']} {feed['unit']}/day",
            "monthly": f"{monthly_units}/month",
            "depletion": "1 jar exactly",
            "quantity": 1,
            "cost": s.get("price"),
            "fresh_warning": None,
        })

    for t in treats:
        feed = get_feeding_amount(t, weight_kg, repo)
        daily = feed["daily"] or 2
        monthly = float(daily) * 30
        packs = math.ceil(monthly / float(t.get("package_units") or 30))
        shelf = int(t.get("shelf_life_days") or 365)
        items.append({
            "product_name": t.get("product_name"),
            "product_type": t.get("product_type"),
            "daily": f"{daily}/day",
            "monthly": f"{int(monthly)}/month",
            "depletion": f"{packs} pack(s)",
            "quantity": packs,
            "cost": packs * float(t.get("price") or 0),
            "fresh_warning": (
                f"Shelf life: {shelf} days · Use within {shelf - 2} days"
                if shelf <= 30
                else None
            ),
        })

    total = js_round(sum(float(i.get("cost") or 0) for i in items))
    return {
        "title": "Monthly Wellness Plan",
        "duration_days": 30,
        "items": items,
        "total_cost": total,
        "product_count": len(items),
    }


def build_yearly_plan(
    monthly_plan: dict[str, Any],
    repo: DataRepository,
) -> dict[str, Any]:
    """Port of bundleEngine.buildYearlyPlan."""
    staples = get_staple_products(repo)
    basic = next(
        (p for p in staples if p.get("subcategory") == "fresh_single" or p.get("product_id") == "FF001"),
        None,
    )
    premium = next(
        (p for p in staples if p.get("subcategory") == "fresh_combo" and p.get("product_id") == "FF003"),
        None,
    )
    if not premium:
        premium = next((p for p in staples if p.get("subcategory") == "fresh_combo"), None)

    staple_upgrade = None
    if basic and premium:
        staple_upgrade = {
            "current": basic.get("product_name"),
            "recommended": premium.get("product_name"),
            "reason": "Higher variety combo pack · optimized omega profile for annual bundling",
        }

    items: list[dict[str, Any]] = []
    for item in monthly_plan.get("items") or []:
        qty = item.get("quantity") or 1
        cost = float(item.get("cost") or 0)
        yearly_qty = math.ceil(365 / 60) if item.get("product_type") == "supplement" else qty * 12
        yearly_cost = js_round(yearly_qty * (cost / qty)) if qty else 0
        items.append({
            **item,
            "quantity": yearly_qty,
            "duration": "365 days",
            "cost": yearly_cost,
        })

    total = sum(int(i.get("cost") or 0) for i in items)
    naive = float(monthly_plan.get("total_cost") or 0) * 12
    savings = max(0, naive - total)
    return {
        "title": "Annual Optimized Plan",
        "duration_days": 365,
        "items": items,
        "total_cost": total,
        "monthly_equivalent": js_round(total / 12),
        "savings": int(savings) if savings == int(savings) else savings,
        "savings_percent": js_round((savings / naive) * 100) if naive > 0 else 0,
        "kibble_upgrade": staple_upgrade,
        "staple_upgrade": staple_upgrade,
        "bulk_notes": "Supplement bottles optimized · combo fresh food packs · treat renewal schedule",
    }
