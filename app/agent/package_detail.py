"""
Port of src/engine/packageDetailEngine.js — package enrichment for packageDetails/wellnessPackages.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from app.agent.condition_lookup import condition_candidates, condition_matches, ingredient_key
from app.agent.utils import DataRepository, feeding_rule_for_product, js_round
from app.inference.config import DEFAULT_NUTRIENT_CATALOG, nutrient_catalog


def js_round1(value: Any) -> int | float:
    """Math.round(x * 10) / 10 — half rounds away from zero like JS; ints without .0."""
    try:
        n = js_round(float(value) * 10) / 10
    except (TypeError, ValueError):
        return 0
    if n == int(n):
        return int(n)
    return n


# Parity defaults — display catalog owned by app.inference.config (Python)
NUTRIENT_CATALOG = DEFAULT_NUTRIENT_CATALOG


def parse_num(value: Any) -> float:
    m = re.search(r"[-+]?\d*\.?\d+", str(value if value is not None else ""))
    return float(m.group(0)) if m else 0.0


def match_nutrient_key(name: str) -> dict[str, Any]:
    n = ingredient_key(name)
    for cat in nutrient_catalog():
        if cat["key"] == n:
            return cat
        if any(a in n for a in (cat.get("aliases") or [])):
            return cat
    return {"key": n, "label": name, "unit": "mg", "aliases": []}


def _product_by_name(repo: DataRepository, name: str) -> dict[str, Any] | None:
    catalog = repo.product_catalog()
    if catalog.empty or not name:
        return None
    hit = catalog[catalog["product_name"] == name]
    if hit.empty:
        return None
    row = hit.iloc[0].to_dict()
    pid = str(row.get("product_id") or "")
    pricing = repo.product_pricing()
    unit_type = "unit"
    package_units = 30
    price = None
    if not pricing.empty and pid:
        prow = pricing[pricing["product_id"] == pid]
        if not prow.empty:
            unit_type = str(prow.iloc[0].get("unit_label") or "unit")
            package_units = int(float(prow.iloc[0].get("package_units") or 30))
            price = float(prow.iloc[0].get("list_price_rmb") or 0)
    row["id"] = pid
    row["product_id"] = pid
    row["unit_type"] = unit_type
    row["package_units"] = package_units
    row["price"] = price
    img = row.get("image_url")
    row["image_url"] = img if img else None
    # Macros from PRODUCT_COMPONENTS
    comps = repo.product_components()
    macros = {"protein_pct": 0.0, "fat_pct": 0.0, "calcium_pct": 0.0, "phosphorus_pct": 0.0}
    if not comps.empty and pid:
        rows = comps[comps["product_id"] == pid]
        for _, c in rows.iterrows():
            cname = str(c.get("component_name") or "").lower()
            val = float(pd.to_numeric(c.get("value"), errors="coerce") or 0)
            if "protein" in cname:
                macros["protein_pct"] = val
            elif cname in ("crude fat", "fat") or cname.endswith(" fat"):
                macros["fat_pct"] = val
            elif "calcium" in cname:
                macros["calcium_pct"] = val
            elif "phosphorus" in cname:
                macros["phosphorus_pct"] = val
    row.update(macros)
    # JS buildProductCatalog: shelf_life_days = parseInt(extension...) || 365
    shelf = row.get("shelf_life_days")
    if shelf is None or (isinstance(shelf, float) and pd.isna(shelf)):
        shelf = None
        for ext in (repo.ext_supplements(), repo.ext_treats_bakery()):
            if ext.empty or "product_id" not in ext.columns:
                continue
            hit_ext = ext[ext["product_id"] == pid]
            if not hit_ext.empty and "shelf_life_days" in hit_ext.columns:
                raw = hit_ext.iloc[0].get("shelf_life_days")
                try:
                    shelf = int(float(raw))
                except (TypeError, ValueError):
                    shelf = None
                break
        if not shelf:
            shelf = 365
    else:
        try:
            shelf = int(float(shelf))
        except (TypeError, ValueError):
            shelf = 365
    row["shelf_life_days"] = shelf
    storage = row.get("storage_method")
    if storage is None or (isinstance(storage, float) and pd.isna(storage)):
        for ext in (repo.ext_supplements(), repo.ext_treats_bakery()):
            if ext.empty or "product_id" not in ext.columns or "storage_method" not in ext.columns:
                continue
            hit_ext = ext[ext["product_id"] == pid]
            if not hit_ext.empty:
                sm = hit_ext.iloc[0].get("storage_method")
                if sm is not None and not (isinstance(sm, float) and pd.isna(sm)):
                    storage = sm
                    break
    row["storage_method"] = storage if storage and not (isinstance(storage, float) and pd.isna(storage)) else None
    return row


def _component_display_name(name: str) -> str:
    if name == "EPA+DHA":
        return "Omega-3"
    if name == "Brady Yeast Probiotics":
        return "Probiotics"
    if name == "Joint Health Formula":
        return "Glucosamine"
    return name


def _component_ingredient_key(name: str) -> str:
    key = ingredient_key(name)
    if key == "epa_dha":
        return "omega_3"
    if key == "brady_yeast_probiotics":
        return "probiotics"
    if key == "joint_health_formula":
        return "glucosamine"
    if key == "lf_mag_300":
        return "immunity"
    return key


def _product_actives(repo: DataRepository, product_id: str) -> list[dict[str, Any]]:
    comps = repo.product_components()
    if comps.empty or not product_id:
        return []
    rows = comps[
        (comps["product_id"] == product_id)
        & (comps["component_type"].astype(str).str.lower() == "active_ingredient")
    ]
    out = []
    for _, r in rows.iterrows():
        name = str(r.get("component_name") or "")
        display = _component_display_name(name)
        out.append({
            "ingredient_name": display,
            "ingredient_key": _component_ingredient_key(name),
            "amount_per_unit": float(pd.to_numeric(r.get("value"), errors="coerce") or 0),
            "unit": r.get("unit") or "%",
        })
    return out


def _ingredient_evidence(repo: DataRepository, key_or_name: str) -> dict[str, Any] | None:
    df = repo.ingredient_evidence()
    if df.empty:
        return None
    key = ingredient_key(key_or_name)
    for col in ("ingredient_key", "ingredient_name", "ingredient"):
        if col not in df.columns:
            continue
        hit = df[df[col].astype(str).map(ingredient_key) == key]
        if not hit.empty:
            return hit.iloc[0].to_dict()
    # Also try label match
    for col in ("ingredient_name", "ingredient"):
        if col not in df.columns:
            continue
        hit = df[df[col].astype(str).str.lower() == str(key_or_name).lower()]
        if not hit.empty:
            return hit.iloc[0].to_dict()
    return None


def build_targets_map(ingredients: list[dict[str, Any]]) -> dict[str, Any]:
    targets: dict[str, Any] = {}
    for ing in ingredients:
        name = ing.get("ingredient_name") or ing.get("ingredient") or ""
        cat = match_nutrient_key(str(name))
        daily = ing.get("daily_dose")
        if daily is None:
            daily = parse_num(ing.get("daily_target") or 0)
        unit = ing.get("unit") or ""
        if not unit and ing.get("daily_target"):
            unit = re.sub(r"[-+]?\d*\.?\d+", "", str(ing.get("daily_target"))).strip()
        targets[cat["key"]] = {
            "nutrient": cat["label"],
            "nutrient_key": cat["key"],
            "target_daily": daily if isinstance(daily, (int, float)) else parse_num(daily),
            "unit": unit or cat.get("unit") or "mg",
            "evidence": {
                "source_title": ing.get("source_name"),
                "source_url": ing.get("source_url"),
                "summary": ing.get("evidence_quote"),
                "year": None,
            },
        }
    return targets


def sum_product_nutrients(
    product_names: list[str],
    product_recs: list[dict[str, Any]],
    repo: DataRepository,
) -> dict[str, Any]:
    totals: dict[str, Any] = {}
    for name in product_names:
        rec = next((p for p in product_recs if p.get("product_name") == name), None)
        db_prod = _product_by_name(repo, name)
        pid = (rec or {}).get("product_id") or (db_prod or {}).get("id")
        if not pid:
            continue
        for pi in _product_actives(repo, str(pid)):
            cat = match_nutrient_key(pi["ingredient_name"])
            if cat["key"] not in totals:
                totals[cat["key"]] = {
                    "amount": 0.0,
                    "unit": pi["unit"] or cat.get("unit"),
                    "products": [],
                }
            totals[cat["key"]]["amount"] += float(pi["amount_per_unit"] or 0)
            totals[cat["key"]]["products"].append({
                "product_name": name,
                "amount": pi["amount_per_unit"],
                "unit": pi["unit"],
            })
    return totals


def add_staple_macros(
    package_product_names: list[str],
    weight_kg: float,
    totals: dict[str, Any],
    repo: DataRepository,
) -> None:
    for name in package_product_names:
        db_prod = _product_by_name(repo, name)
        if not db_prod:
            continue
        cat = str(db_prod.get("category") or "")
        if cat not in ("Fresh Food", "STAPLE_FOOD"):
            continue
        rule = feeding_rule_for_product(repo.product_feeding_rules(), str(db_prod["id"]), weight_kg)
        grams = float(rule["daily_amount"]) if rule else 110.0
        detail = db_prod.get("category_detail") or {}
        protein_pct = float(detail.get("protein_pct") or db_prod.get("protein_pct") or 0)
        fat_pct = float(detail.get("fat_pct") or db_prod.get("fat_pct") or 0)
        ca_pct = float(detail.get("calcium_pct") or db_prod.get("calcium_pct") or 0)
        p_pct = float(detail.get("phosphorus_pct") or db_prod.get("phosphorus_pct") or 0)
        macros = [
            {"key": "protein", "label": "Protein", "unit": "g", "amount": grams * protein_pct / 100, "target": weight_kg * 2.2},
            {"key": "fat", "label": "Fat", "unit": "g", "amount": grams * fat_pct / 100, "target": weight_kg * 1.1},
            {"key": "calcium", "label": "Calcium", "unit": "g", "amount": grams * ca_pct / 100, "target": weight_kg * 0.05},
            {"key": "phosphorus", "label": "Phosphorus", "unit": "g", "amount": grams * p_pct / 100, "target": weight_kg * 0.04},
        ]
        for m in macros:
            if m["key"] not in totals:
                totals[m["key"]] = {
                    "amount": 0.0,
                    "unit": m["unit"],
                    "products": [],
                    "macroTarget": m["target"],
                    "label": m["label"],
                }
            totals[m["key"]]["amount"] += m["amount"]
            totals[m["key"]]["products"].append({
                "product_name": name,
                "amount": js_round1(m["amount"]),
                "unit": m["unit"],
            })


def attach_nutrient_evidence(
    repo: DataRepository,
    key: str,
    nutrient_label: str,
    target_row: dict[str, Any] | None,
) -> dict[str, Any] | None:
    evidence = _ingredient_evidence(repo, key) or _ingredient_evidence(repo, nutrient_label)
    if not evidence and target_row and target_row.get("evidence"):
        ev = target_row["evidence"]
        evidence = {
            "source_quote": ev.get("summary"),
            "source_name": ev.get("source_title"),
            "source_url": ev.get("source_url"),
        }
    if not evidence:
        return None
    if not evidence.get("source_quote") and not evidence.get("source_name"):
        return None
    source_url = evidence.get("source_url")
    source_name = evidence.get("source_name")
    if source_url and re.search(r"pubmed\.ncbi\.nlm\.nih\.gov", str(source_url), re.I) and not source_name:
        source_name = "National Library of Medicine"
    return {
        "quote": evidence.get("source_quote"),
        "source_name": source_name or "Published source",
        "source_url": source_url,
        "year": _coerce_year(evidence.get("year")),
    }


def _coerce_year(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def build_daily_nutrition_intake(
    package_product_names: list[str],
    ingredients: list[dict[str, Any]],
    product_recs: list[dict[str, Any]],
    weight_kg: float,
    repo: DataRepository,
) -> list[dict[str, Any]]:
    targets = build_targets_map(ingredients)
    provided = sum_product_nutrients(package_product_names, product_recs, repo)
    add_staple_macros(package_product_names, weight_kg, provided, repo)
    keys = list(dict.fromkeys([*targets.keys(), *provided.keys()]))
    rows = []
    for key in keys:
        t = targets.get(key)
        p = provided.get(key)
        target = (t or {}).get("target_daily") if t and (t.get("target_daily") or 0) else (p or {}).get("macroTarget", 0)
        if t and t.get("target_daily"):
            target = t["target_daily"]
        elif p and p.get("macroTarget") is not None:
            target = p["macroTarget"]
        else:
            target = 0
        amount = js_round1((p or {}).get("amount") or 0)
        unit = (t or {}).get("unit") or (p or {}).get("unit") or "mg"
        if target and float(target) > 0:
            coverage = min(150, js_round((float(amount) / float(target)) * 100))
        else:
            coverage = 100 if amount > 0 else 0
        nutrient_label = (
            (t or {}).get("nutrient")
            or (p or {}).get("label")
            or next((c["label"] for c in nutrient_catalog() if c["key"] == key), None)
            or key
        )
        rows.append({
            "nutrient": nutrient_label,
            "nutrient_key": key,
            "provided": amount,
            "target_daily": js_round1(target or 0),
            "unit": unit,
            "coverage_percent": coverage,
            "status": (
                "Informational" if not target or float(target) <= 0
                else ("Meets target" if coverage >= 100 else "Below target")
            ),
            "evidence": attach_nutrient_evidence(repo, key, str(nutrient_label), t),
        })
    rows = [r for r in rows if r["provided"] > 0 or r["target_daily"] > 0]
    rows.sort(key=lambda r: -r["coverage_percent"])
    return rows


def build_full_nutrition_report(
    daily_intake: list[dict[str, Any]],
    product_recs: list[dict[str, Any]],
    package_product_names: list[str],
    weight_kg: float,
    repo: DataRepository,
) -> list[dict[str, Any]]:
    provided = sum_product_nutrients(package_product_names, product_recs, repo)
    add_staple_macros(package_product_names, weight_kg, provided, repo)
    out = []
    for row in daily_intake:
        p = provided.get(row["nutrient_key"])
        sources = []
        if p and p.get("products"):
            sources = [
                {"product_name": s["product_name"], "amount": s["amount"], "unit": s["unit"]}
                for s in p["products"]
            ]
        if not sources:
            for rec in product_recs:
                pis = _product_actives(repo, str(rec.get("product_id") or ""))
                pi = next(
                    (x for x in pis if match_nutrient_key(x["ingredient_name"])["key"] == row["nutrient_key"]),
                    None,
                )
                if pi:
                    sources.append({
                        "product_name": rec.get("product_name"),
                        "amount": pi["amount_per_unit"],
                        "unit": pi["unit"],
                    })
        ev = attach_nutrient_evidence(repo, row["nutrient_key"], row["nutrient"], None)
        if not ev:
            raw = _ingredient_evidence(repo, row["nutrient_key"])
            if raw:
                ev = {
                    "quote": raw.get("source_quote"),
                    "source_name": (
                        raw.get("source_name")
                        or (
                            "National Library of Medicine"
                            if "pubmed" in str(raw.get("source_url") or "")
                            else "Published source"
                        )
                    ),
                    "source_url": raw.get("source_url"),
                    "year": raw.get("year"),
                }
            else:
                ev = {
                    "quote": "Computed from product composition and published daily intake guidelines.",
                    "source_name": "PPIE deterministic nutrient model",
                    "source_url": None,
                    "year": None,
                }
        out.append({
            "nutrient": row["nutrient"],
            "target": row["target_daily"],
            "provided": row["provided"],
            "unit": row["unit"],
            "coverage_percent": row["coverage_percent"],
            "sources": sources,
            "evidence": ev,
        })
    return out


def product_serving_card(
    item: dict[str, Any],
    product_recs: list[dict[str, Any]],
    weight_kg: float,
    repo: DataRepository,
) -> dict[str, Any]:
    name = item.get("name")
    rec = next((p for p in product_recs if p.get("product_name") == name), None)
    db_prod = _product_by_name(repo, str(name or ""))
    rule = None
    if db_prod:
        rule = feeding_rule_for_product(repo.product_feeding_rules(), str(db_prod["id"]), weight_kg)
    if rule:
        amt = rule["daily_amount"]
        if isinstance(amt, float) and amt.is_integer():
            amt = int(amt)
        daily = f"{amt}{rule['daily_unit']}/day"
    else:
        daily = (rec or {}).get("serving_size") or item.get("daily_amount") or "1 serving/day"
    monthly = item.get("monthly_quantity") or (
        "30 servings/month" if (rec or {}).get("serving_size") else "—"
    )
    return {
        "product_id": (rec or {}).get("product_id") or (db_prod or {}).get("id"),
        "product_name": name,
        "brand": item.get("brand") or (db_prod or {}).get("brand"),
        "category": item.get("category") or item.get("type"),
        "image_url": (db_prod or {}).get("image_url"),
        "daily_serving": daily,
        "monthly_amount": monthly,
        "monthly_cost": item.get("monthly_cost") or (rec or {}).get("price") or (db_prod or {}).get("price"),
    }


def build_feeding_strategies(
    pkg: dict[str, Any],
    weight_kg: float,
    daily_intake: list[dict[str, Any]],
    product_recs: list[dict[str, Any]],
    repo: DataRepository,
) -> list[dict[str, Any]]:
    names = [p.get("name") for p in (pkg.get("products_included") or [])]

    def _is_staple(n: str) -> bool:
        p = _product_by_name(repo, n)
        if not p:
            return False
        return (
            p.get("product_type") in ("fresh_food", "kibble")
            or p.get("category") in ("Fresh Food", "STAPLE_FOOD")
            or str(p.get("subcategory") or "").startswith("fresh")
        )

    staple = next((n for n in names if n and _is_staple(n)), None)
    supps = [
        n for n in names
        if n and (
            (_product_by_name(repo, n) or {}).get("category") == "Nutritional Supplements"
            or "supplement" in str((_product_by_name(repo, n) or {}).get("subcategory") or "")
        )
    ]
    treats = [
        n for n in names
        if n and (_product_by_name(repo, n) or {}).get("category") in (
            "All-Natural Treats", "Homestyle Bakery", "TREAT"
        )
    ]
    dental = [n for n in names if n and "dental" in n.lower()]

    def staple_grams(mult: float) -> str:
        if not staple:
            return "—"
        prod = _product_by_name(repo, staple)
        rule = feeding_rule_for_product(repo.product_feeding_rules(), str(prod["id"]), weight_kg) if prod else None
        if not rule:
            return f"{js_round(110 * mult)} g"
        return f"{js_round(float(rule['daily_amount']) * mult)}{rule['daily_unit']}"

    return [
        {
            "id": "A",
            "title": "Staple Food Only",
            "description": "Maximum calories from staple nutrition only.",
            "items": [f"{staple_grams(1)} fresh food/day"] if staple else [],
            "calories_estimate": 880,
            "highlights": [f"{n['nutrient']}: {n['provided']}{n['unit']}" for n in daily_intake[:3]],
        },
        {
            "id": "B",
            "title": "Staple Food + Supplements",
            "description": "Redistributes calories from staple food to targeted supplementation.",
            "items": [x for x in [
                f"{staple_grams(0.86)} fresh food" if staple else None,
                f"1 serving {supps[0]}" if supps else None,
            ] if x],
            "calories_estimate": 903,
            "highlights": [n["nutrient"] for n in daily_intake if n["coverage_percent"] >= 80],
        },
        {
            "id": "C",
            "title": "Staple Food + Treats",
            "description": "Uses functional treats for partial nutrient delivery.",
            "items": [x for x in [
                f"{staple_grams(0.86)} fresh food" if staple else None,
                f"2 {treats[0]}/day" if treats else None,
            ] if x],
            "calories_estimate": 915,
            "highlights": ["Functional treat contribution", "Maintains protein targets"],
        },
        {
            "id": "D",
            "title": "Complete Plan",
            "description": "Full package feeding strategy for this care tier.",
            "items": [
                f"{product_serving_card({'name': n}, product_recs, weight_kg, repo)['daily_serving']} · {n}"
                for n in names if n
            ],
            "calories_estimate": 928,
            "highlights": [f"{n['nutrient']} {n['coverage_percent']}%" for n in daily_intake],
        },
    ]


def build_cost_breakdown(pkg: dict[str, Any]) -> dict[str, Any]:
    rows = [
        {
            "product_name": p.get("name"),
            "daily": p.get("daily_amount") or p.get("serving_size") or "—",
            "monthly": p.get("monthly_quantity") or "—",
            "unit_price": f"${p['price']}" if p.get("price") else "—",
            "monthly_cost": p.get("monthly_cost") or p.get("price") or 0,
        }
        for p in (pkg.get("products_included") or [])
    ]
    monthly_total = pkg.get("monthly_cost")
    if monthly_total is None:
        monthly_total = sum(float(r.get("monthly_cost") or 0) for r in rows)
    yearly_total = pkg.get("yearly_cost")
    if yearly_total is None:
        discount = 0.92
        try:
            balanced = repo.package_tier_map().get("balanced", {})
            discount = float(balanced.get("yearly_discount_factor") or 0.92)
        except Exception:  # noqa: BLE001
            pass
        yearly_total = js_round(float(monthly_total) * 12 * discount)
    monthly_total = float(monthly_total)
    yearly_total = float(yearly_total)
    mt = int(monthly_total) if monthly_total == int(monthly_total) else monthly_total
    yt = int(yearly_total) if yearly_total == int(yearly_total) else yearly_total
    savings = max(0, monthly_total * 12 - yearly_total)
    savings = int(savings) if savings == int(savings) else savings
    return {
        "rows": rows,
        "monthly_total": mt,
        "yearly_total": yt,
        "annual_discount_percent": (
            js_round((1 - yearly_total / (monthly_total * 12)) * 100) if monthly_total > 0 else 0
        ),
        "savings_vs_monthly": savings,
    }


def enrich_package_for_detail(
    pkg: dict[str, Any],
    ingredients: list[dict[str, Any]],
    product_recs: list[dict[str, Any]],
    pet_name: str,
    weight_kg: float,
    repo: DataRepository,
) -> dict[str, Any]:
    """Port of enrichPackageForDetail."""
    names = [p.get("name") for p in (pkg.get("products_included") or [])]
    product_cards = [
        product_serving_card(item, product_recs, weight_kg, repo)
        for item in (pkg.get("products_included") or [])
    ]
    daily_nutrition_intake = build_daily_nutrition_intake(
        [n for n in names if n], ingredients, product_recs, weight_kg, repo
    )
    full_nutrition_report = build_full_nutrition_report(
        daily_nutrition_intake, product_recs, [n for n in names if n], weight_kg, repo
    )
    feeding_strategies = build_feeding_strategies(
        pkg, weight_kg, daily_nutrition_intake, product_recs, repo
    )
    cost_breakdown = build_cost_breakdown(pkg)

    if pkg.get("recommended"):
        package_summary = (
            f"This package balances {pet_name}'s highest-priority nutritional targets using staple "
            f"nutrition, targeted supplementation, and functional treats. PPIE selected this "
            f"combination to maximize nutrient coverage while controlling yearly cost."
        )
    elif pkg.get("tier") == "essential":
        package_summary = (
            "This package prioritizes daily nutritional adequacy at the lowest long-term cost "
            "using essential staple nutrition and core functional products."
        )
    else:
        package_summary = (
            f"This package maximizes nutrient coverage across {pet_name}'s biological profile "
            f"with complete functional nutrition selected from the active catalog."
        )

    plan_365 = pkg.get("plan_365") or {}
    n_products = len(pkg.get("products_included") or [])
    return {
        **pkg,
        "package_summary": pkg.get("package_summary") or package_summary,
        "estimated_monthly_supply": (
            f"{n_products} products · 365-day plan (monthly = yearly ÷ 12)"
        ),
        "estimated_yearly_supply": f"{n_products} products · 365-day inventory plan",
        "product_cards": product_cards,
        "daily_nutrition_intake": daily_nutrition_intake,
        "full_nutrition_report": full_nutrition_report,
        "feeding_strategies": feeding_strategies,
        "cost_breakdown": cost_breakdown,
        "plan_365": plan_365,
        "research_notes": [
            {"nutrient": r["nutrient"], **r["evidence"]}
            for r in full_nutrition_report
            if r.get("evidence") and r["evidence"].get("quote")
        ],
    }


def _coerce_year(value: Any) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def build_product_analysis(
    product_name: str,
    pkg: dict[str, Any],
    ingredients: list[dict[str, Any]],
    product_recs: list[dict[str, Any]],
    pet_name: str,
    weight_kg: float,
    repo: DataRepository,
) -> dict[str, Any]:
    """Port of packageDetailEngine.buildProductAnalysis."""
    rec = next((p for p in product_recs if p.get("product_name") == product_name), None)
    db_prod = _product_by_name(repo, product_name)
    pid = (rec or {}).get("product_id") or (db_prod or {}).get("id")
    pis = _product_actives(repo, str(pid or ""))
    targets = build_targets_map(ingredients)

    active_ingredients = []
    for pi in pis:
        cat = match_nutrient_key(str(pi["ingredient_name"]))
        target = targets.get(cat["key"])
        amount = float(pi["amount_per_unit"] or 0)
        if target and target.get("target_daily"):
            coverage = min(150, js_round((amount / float(target["target_daily"])) * 100))
        else:
            coverage = 0
        evidence = _ingredient_evidence(repo, pi.get("ingredient_key") or pi["ingredient_name"]) or {}
        target_daily = (target or {}).get("target_daily") or 0
        if isinstance(target_daily, float) and target_daily == int(target_daily):
            target_daily = int(target_daily)
        active_ingredients.append({
            "name": pi["ingredient_name"],
            "amount": amount,
            "unit": pi["unit"],
            "target": target_daily,
            "target_unit": (target or {}).get("unit") or pi["unit"],
            "coverage_percent": coverage,
            "evidence": {
                "mechanism": "Supports nutrient target from CONDITION_INGREDIENTS mapping.",
                "summary": evidence.get("source_quote"),
                "journal": evidence.get("source_name"),
                "year": _coerce_year(evidence.get("year")),
                "source_url": evidence.get("source_url"),
            },
        })

    rule = (
        feeding_rule_for_product(repo.product_feeding_rules(), str(pid), weight_kg)
        if pid
        else None
    )
    if rule:
        amt = rule["daily_amount"]
        if isinstance(amt, float) and amt.is_integer():
            amt = int(amt)
        daily_str = f"{amt} {rule['daily_unit']}"
    else:
        daily_str = (rec or {}).get("serving_size") or "1 serving/day"

    alternatives = [
        {
            "product_name": p.get("product_name"),
            "reason": "Higher servings or calories required to match the same nutrient targets.",
        }
        for p in product_recs
        if p.get("product_name") != product_name and pis
    ][:2]

    why_lines = [
        f"Provides {a['coverage_percent']}% of {pet_name}'s {a['name']} target ({a['amount']}{a['unit']}/serving)."
        for a in active_ingredients
        if a["coverage_percent"] >= 50
    ]
    if not why_lines and pis:
        why_lines.append(
            f"Contributes functional compounds toward {pet_name}'s package nutrient targets."
        )

    name_l = product_name.lower()
    rec_price = float((rec or {}).get("price") or 0)
    unit_price = (rec or {}).get("price")
    if unit_price is None:
        unit_price = (db_prod or {}).get("price")
    monthly_cost = (rec or {}).get("monthly_cost_estimate")
    if monthly_cost is None:
        monthly_cost = (rec or {}).get("price")

    cost: dict[str, Any] = {
        "unit_price": unit_price,
        "yearly_cost": js_round(
            rec_price
            * 12
            * float(repo.package_tier_map().get("balanced", {}).get("yearly_discount_factor") or 0.92)
        ),
    }
    # JS: monthly_cost: rec?.monthly_cost_estimate || rec?.price — undefined is omitted in JSON
    if monthly_cost is not None:
        cost["monthly_cost"] = monthly_cost

    return {
        "product_id": pid,
        "product_name": product_name,
        "brand": (rec or {}).get("brand") or (db_prod or {}).get("brand"),
        "category": (db_prod or {}).get("category") or (rec or {}).get("product_type"),
        "package_tier": pkg.get("tier"),
        "overview": (
            f"{product_name} is included in {pet_name}'s {pkg.get('title') or 'care'} plan "
            f"because it closes measurable nutrient gaps with deterministic serving math."
        ),
        "serving": {
            "daily": daily_str,
            "monthly_requirement": "30 servings" if (rec or {}).get("serving_size") else "—",
            "calories_kcal": 420 if "fresh" in name_l else 14,
            "weight_g": 5 if "chew" in name_l else 10,
            "container_lasts_days": (db_prod or {}).get("package_units") or 30,
        },
        "active_ingredients": active_ingredients,
        "scientific_evidence": [
            {
                "ingredient": a["name"],
                "mechanism": a["evidence"].get("mechanism"),
                "summary": a["evidence"].get("summary"),
                "journal": a["evidence"].get("journal"),
                "year": a["evidence"].get("year"),
                "source_url": a["evidence"].get("source_url"),
                "recommended_daily": f"{a['target']}{a['target_unit']}",
            }
            for a in active_ingredients
        ],
        "why_included": why_lines,
        "alternatives": alternatives,
        "cost": cost,
        "specifications": {
            "brand": (rec or {}).get("brand") or (db_prod or {}).get("brand"),
            "package_units": (db_prod or {}).get("package_units"),
            "shelf_life_days": (db_prod or {}).get("shelf_life_days"),
            "storage": (db_prod or {}).get("storage_method") or "Cool, dry place",
            "category": (db_prod or {}).get("category"),
        },
    }


def activities_for_condition(repo: DataRepository, condition_name: str) -> list[dict[str, Any]]:
    """Mirror db.getActivities with conditionCandidates."""
    df = repo.condition_activities()
    if df.empty or not condition_name:
        return []
    candidates = condition_candidates(condition_name)
    out = []
    name_col = "condition" if "condition" in df.columns else "condition_name"
    for _, row in df.iterrows():
        if condition_matches(None, row.get(name_col), candidates):
            out.append(row.to_dict())
    return out
