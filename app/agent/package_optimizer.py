"""
Phase 11 — Data-driven clinical package optimizer.

Dog → Clinical Needs → Target Nutrients → Candidate Products → Optimization
    → 3 Packages → 365-day plans → Package reports

Reads ACTIVE catalog + joins only. No hardcoded product IDs.
Does not alter parity nutrition/risk/trait formulas — consumes their outputs.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from app.agent.formula_trace import (
    decision,
    empty_execution,
    seal_execution,
    start_timer,
    step,
)
from app.agent.utils import DataRepository, feeding_rule_for_product, ingredient_key, js_round
from app.inference.config import (
    DEFAULT_ESSENTIAL_COVERAGE_FLOOR,
    DEFAULT_SCORE_WEIGHTS,
    DEFAULT_SURPLUS_PENALTY_WEIGHT,
    essential_coverage_floor,
    score_weights,
    surplus_penalty_weight,
)

# Parity defaults — runtime uses CSV-backed loaders (identical seed values).
SCORE_WEIGHTS = DEFAULT_SCORE_WEIGHTS
SURPLUS_PENALTY_WEIGHT = DEFAULT_SURPLUS_PENALTY_WEIGHT
ESSENTIAL_COVERAGE_FLOOR = DEFAULT_ESSENTIAL_COVERAGE_FLOOR


def _norm(s: Any) -> str:
    return str(s or "").strip().lower()


def _component_to_ingredient_key(name: str) -> str:
    key = ingredient_key(name.replace("+", "_").replace("EPA+DHA", "omega_3"))
    if key == "epa_dha":
        return "omega_3"
    if key == "joint_health_formula":
        return "glucosamine"
    if key == "brady_yeast_probiotics":
        return "probiotics"
    return key


def _keys_match(target_key: str, component_key: str, alias_groups: dict[str, set[str]]) -> bool:
    if target_key == component_key:
        return True
    for aliases in alias_groups.values():
        if target_key in aliases and component_key in aliases:
            return True
    return False


def _is_staple_category(category: str) -> bool:
    c = _norm(category)
    return c in {"staple_food", "fresh food", "fresh_food", "kibble"} or "staple" in c


def _is_supplement_category(category: str) -> bool:
    return "supplement" in _norm(category)


def _is_treat_category(category: str) -> bool:
    c = _norm(category)
    return c in {"treat", "homestyle bakery", "all-natural treats"} or "treat" in c or "bakery" in c


def _product_role(category: str) -> str:
    if _is_staple_category(category):
        return "staple"
    if _is_supplement_category(category):
        return "supplement"
    if _is_treat_category(category):
        return "treat"
    return "product"


def _mass_to_grams(amount: float, unit: str) -> float | None:
    u = _norm(unit)
    if u in {"g", "gram", "grams"}:
        return amount
    if u in {"kg", "kilogram", "kilograms"}:
        return amount * 1000.0
    if u in {"mg"}:
        return amount / 1000.0
    return None


def _goal_tokens(goal_id: str, title: str) -> set[str]:
    text = f"{goal_id} {title}".lower().replace("_", " ")
    tokens = set(text.split())
    if "joint" in text or "ortho" in text:
        tokens |= {"joint", "cartilage", "omega", "glucosamine", "inflammatory"}
    if "skin" in text or "derm" in text or "coat" in text:
        tokens |= {"skin", "coat", "derm", "omega"}
    if "dental" in text or "oral" in text:
        tokens |= {"dental", "chew", "teeth"}
    if "digest" in text or "gut" in text:
        tokens |= {"digest", "fiber", "probiotic", "gut"}
    if "weight" in text or "obes" in text:
        tokens |= {"weight", "tear", "stain", "lean"}
    if "cardio" in text or "heart" in text:
        tokens |= {"heart", "cardio", "taurine"}
    if "activity" in text or "muscle" in text:
        tokens |= {"activity", "muscle", "energy"}
    if "immune" in text:
        tokens |= {"immune", "omega"}
    return tokens


def _function_match_score(function_text: str, goals: list[dict[str, Any]]) -> float:
    if not function_text or not goals:
        return 0.0
    ftoks = set(_norm(function_text).replace("&", " ").replace("/", " ").split())
    best = 0.0
    for g in goals:
        gtoks = _goal_tokens(str(g.get("goal_id") or ""), str(g.get("title") or ""))
        if not gtoks:
            continue
        overlap = len(ftoks & gtoks)
        if overlap:
            conf = _norm(g.get("confidence") or "medium")
            conf_w = 1.0 if conf == "high" else (0.7 if conf == "medium" else 0.4)
            best = max(best, min(1.0, (overlap / max(len(gtoks), 1)) * 3) * conf_w)
    return best


def _evidence_score_for_components(comps: list[dict[str, Any]]) -> float:
    if not comps:
        return 0.0
    levels = {_norm(c.get("evidence_level")) for c in comps}
    if "pubmed" in levels or "peer_reviewed" in levels:
        return 1.0
    if "declaredlabel" in levels or "declared_label" in levels:
        return 0.55
    if "ingredientorderestimate" in levels:
        return 0.25
    return 0.15


def _feeding_for_product(rules: pd.DataFrame, pid: str, weight_kg: float, role: str) -> dict[str, Any]:
    """Resolve feeding from PRODUCT_FEEDING_RULES; clamp to nearest bracket when out of range."""
    feed = feeding_rule_for_product(rules, pid, weight_kg) if not rules.empty else None
    if feed:
        return feed
    if rules.empty:
        if role == "staple":
            return {"daily_amount": max(1.0, float(weight_kg) * 20.0), "daily_unit": "g"}
        return {"daily_amount": 1.0, "daily_unit": "serving"}
    subset = rules[rules["product_id"].astype(str) == pid]
    if subset.empty:
        if role == "staple":
            return {"daily_amount": max(1.0, float(weight_kg) * 20.0), "daily_unit": "g"}
        return {"daily_amount": 1.0, "daily_unit": "serving"}
    # Prefer highest bracket when dog exceeds chart (common for small-breed kibble CSVs)
    wmax = pd.to_numeric(subset.get("weight_max_kg", subset.get("max_weight_kg")), errors="coerce")
    wmin = pd.to_numeric(subset.get("weight_min_kg", subset.get("min_weight_kg")), errors="coerce")
    if wmax is not None and float(weight_kg) > float(wmax.max()):
        row = subset.loc[wmax.idxmax()]
    elif wmin is not None and float(weight_kg) < float(wmin.min()):
        row = subset.loc[wmin.idxmin()]
    else:
        row = subset.iloc[0]
    return {
        "daily_amount": float(row.get("daily_amount") or 1),
        "daily_unit": str(row.get("daily_unit") or "serving"),
    }


def _yearly_plan_for_product(
    *,
    daily_amount: float,
    daily_unit: str,
    package_units: float,
    unit_label: str,
    list_price: float,
    weight_g: float | None,
    shelf_life_days: int | None,
) -> dict[str, Any]:
    """365-day inventory math. Monthly = yearly / 12."""
    daily_g = _mass_to_grams(daily_amount, daily_unit)
    pack_g = _mass_to_grams(package_units, unit_label)
    if pack_g is None and weight_g:
        pack_g = float(weight_g)

    if daily_g is not None and pack_g and pack_g > 0:
        yearly_mass_g = daily_g * 365.0
        packages_needed = max(1, int(math.ceil(yearly_mass_g / pack_g)))
        return {
            "basis": "mass",
            "daily_serving": f"{daily_amount:g}{daily_unit}",
            "yearly_mass_g": js_round(yearly_mass_g * 10) / 10,
            "yearly_mass_kg": js_round((yearly_mass_g / 1000.0) * 100) / 100,
            "package_size": f"{package_units:g}{unit_label}",
            "packages_needed": packages_needed,
            "yearly_cost": js_round(packages_needed * list_price),
            "monthly_cost": js_round((packages_needed * list_price) / 12.0),
        }

    servings_per_pack = None
    # Only treat package_units as serving count when the pack unit is discrete (not mass).
    if _mass_to_grams(package_units, unit_label) is None and package_units > 1:
        servings_per_pack = package_units
    if servings_per_pack is None and weight_g and weight_g > 0 and daily_g:
        servings_per_pack = max(1.0, weight_g / max(daily_g, 0.1))
    if servings_per_pack is None:
        cycle = shelf_life_days if shelf_life_days and shelf_life_days > 0 else 30
        packages_needed = max(1, int(math.ceil(365.0 / cycle)))
        return {
            "basis": "cycle",
            "daily_serving": f"{daily_amount:g} {daily_unit}",
            "yearly_mass_g": None,
            "yearly_mass_kg": None,
            "package_size": f"{package_units:g} {unit_label}",
            "packages_needed": packages_needed,
            "cycle_days": cycle,
            "yearly_cost": js_round(packages_needed * list_price),
            "monthly_cost": js_round((packages_needed * list_price) / 12.0),
        }

    yearly_servings = daily_amount * 365.0
    packages_needed = max(1, int(math.ceil(yearly_servings / float(servings_per_pack))))
    return {
        "basis": "servings",
        "daily_serving": f"{daily_amount:g} {daily_unit}",
        "yearly_servings": js_round(yearly_servings),
        "servings_per_pack": servings_per_pack,
        "yearly_mass_g": None,
        "yearly_mass_kg": None,
        "package_size": f"{package_units:g} {unit_label}",
        "packages_needed": packages_needed,
        "yearly_cost": js_round(packages_needed * list_price),
        "monthly_cost": js_round((packages_needed * list_price) / 12.0),
    }


def load_candidate_products(repo: DataRepository, weight_kg: float) -> list[dict[str, Any]]:
    """ACTIVE catalog ⨝ pricing ⨝ components ⨝ functions ⨝ feeding ⨝ ext tables."""
    catalog = repo.active_products()
    if catalog.empty:
        return []
    pricing = repo.product_pricing()
    components = repo.product_components()
    functions = repo.product_functions()
    rules = repo.product_feeding_rules()
    bakery = repo.ext_treats_bakery()
    supplements = repo.ext_supplements()
    alias_groups = repo.ingredient_alias_groups()

    out: list[dict[str, Any]] = []
    for _, row in catalog.iterrows():
        pid = str(row.get("product_id") or "")
        if not pid:
            continue
        category = str(row.get("category") or "")
        role = _product_role(category)

        price = 0.0
        package_units = 1.0
        unit_label = "unit"
        if not pricing.empty:
            prow = pricing[pricing["product_id"].astype(str) == pid]
            if not prow.empty:
                price = float(prow.iloc[0].get("list_price_rmb") or 0)
                package_units = float(prow.iloc[0].get("package_units") or 1)
                unit_label = str(prow.iloc[0].get("unit_label") or "unit")

        comps: list[dict[str, Any]] = []
        actives: list[dict[str, Any]] = []
        if not components.empty:
            hits = components[components["product_id"].astype(str) == pid]
            for _, c in hits.iterrows():
                rec = {k: (None if pd.isna(v) else v) for k, v in c.items()}
                comps.append(rec)
                if _norm(rec.get("component_type")) == "active_ingredient":
                    amount = float(pd.to_numeric(rec.get("value"), errors="coerce") or 0)
                    actives.append(
                        {
                            "ingredient_key": _component_to_ingredient_key(str(rec.get("component_name") or "")),
                            "name": rec.get("component_name"),
                            "amount_per_serving": amount,
                            "unit": rec.get("unit") or "",
                        }
                    )

        funcs: list[dict[str, Any]] = []
        if not functions.empty:
            fhits = functions[functions["product_id"].astype(str) == pid]
            for _, f in fhits.iterrows():
                funcs.append(
                    {
                        "function": str(f.get("function") or ""),
                        "confidence": str(f.get("confidence") or ""),
                    }
                )

        feed = _feeding_for_product(rules, pid, weight_kg, role)
        daily_amount = float((feed or {}).get("daily_amount") or 1)
        daily_unit = str((feed or {}).get("daily_unit") or "serving")

        ext: dict[str, Any] = {}
        if not bakery.empty:
            b = bakery[bakery["product_id"].astype(str) == pid]
            if not b.empty:
                ext = {k: (None if pd.isna(v) else v) for k, v in b.iloc[0].items()}
        if not supplements.empty:
            s = supplements[supplements["product_id"].astype(str) == pid]
            if not s.empty:
                ext = {**ext, **{k: (None if pd.isna(v) else v) for k, v in s.iloc[0].items()}}

        weight_g = None
        if ext.get("weight_g") not in (None, ""):
            try:
                weight_g = float(ext.get("weight_g"))
            except (TypeError, ValueError):
                weight_g = None
        shelf = None
        if ext.get("shelf_life_days") not in (None, ""):
            try:
                shelf = int(float(ext.get("shelf_life_days")))
            except (TypeError, ValueError):
                shelf = None

        yearly = _yearly_plan_for_product(
            daily_amount=daily_amount,
            daily_unit=daily_unit,
            package_units=package_units,
            unit_label=unit_label,
            list_price=price,
            weight_g=weight_g,
            shelf_life_days=shelf,
        )

        out.append(
            {
                "product_id": pid,
                "product_name": str(row.get("product_name") or pid),
                "brand": str(row.get("brand") or ""),
                "category": category,
                "subcategory": str(row.get("subcategory") or ""),
                "status": str(row.get("status") or "active"),
                "role": role,
                "product_type": (
                    "fresh_food"
                    if role == "staple"
                    else ("supplement" if role == "supplement" else "treat")
                ),
                "list_price_rmb": price,
                "price": js_round(price),
                "package_units": package_units,
                "unit_label": unit_label,
                "daily_amount": daily_amount,
                "daily_unit": daily_unit,
                "serving_size": f"{daily_amount:g} {daily_unit}/day",
                "components": comps,
                "active_ingredients": actives,
                "functions": funcs,
                "evidence_score": _evidence_score_for_components(comps),
                "alias_groups": alias_groups,
                "yearly": yearly,
                "yearly_cost": yearly["yearly_cost"],
                "monthly_cost": yearly["monthly_cost"],
                "ext": ext,
                "short_description": str(row.get("short_description") or ""),
                "tags": str(row.get("tags") or ""),
            }
        )
    return out


def _targets_from_ingredients(ingredients: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets = []
    for ing in ingredients or []:
        key = ing.get("ingredient_key") or _component_to_ingredient_key(str(ing.get("ingredient") or ""))
        dose = ing.get("daily_target_value")
        if dose is None:
            raw = str(ing.get("daily_target") or ing.get("target_daily_dose") or "")
            try:
                dose = float("".join(ch for ch in raw if ch.isdigit() or ch == "."))
            except ValueError:
                dose = 0
        unit = ing.get("dose_unit") or ing.get("unit") or ""
        if not unit and isinstance(ing.get("daily_target"), str):
            unit = "".join(ch for ch in str(ing["daily_target"]) if ch.isalpha())
        targets.append(
            {
                "ingredient_key": key,
                "nutrient": ing.get("ingredient") or ing.get("ingredient_name") or key,
                "target_daily": float(dose or 0),
                "unit": unit or "mg",
                "supports_goals": ing.get("supports_goals") or [],
            }
        )
    return [t for t in targets if t["ingredient_key"]]


def _provided_map(
    products: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    alias_groups: dict[str, set[str]],
) -> dict[str, float]:
    provided = {t["ingredient_key"]: 0.0 for t in targets}
    for p in products:
        for a in p.get("active_ingredients") or []:
            akey = a.get("ingredient_key")
            amount = float(a.get("amount_per_serving") or 0) * float(p.get("daily_amount") or 1)
            for t in targets:
                if _keys_match(t["ingredient_key"], str(akey), alias_groups):
                    provided[t["ingredient_key"]] = provided.get(t["ingredient_key"], 0.0) + amount
    return provided


def coverage_matrix(
    products: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    alias_groups: dict[str, set[str]],
) -> list[dict[str, Any]]:
    provided = _provided_map(products, targets, alias_groups)
    rows = []
    for t in targets:
        key = t["ingredient_key"]
        target = float(t.get("target_daily") or 0)
        prov = float(provided.get(key) or 0)
        if target > 0:
            cov = min(100.0, (prov / target) * 100.0)
            surplus = max(prov - target, 0.0)
        else:
            cov = 100.0 if prov > 0 else 0.0
            surplus = prov
        sources = []
        for p in products:
            for a in p.get("active_ingredients") or []:
                if _keys_match(key, str(a.get("ingredient_key")), alias_groups):
                    sources.append(p.get("product_name"))
        rows.append(
            {
                "nutrient": t.get("nutrient"),
                "ingredient_key": key,
                "target": target,
                "provided": js_round(prov * 10) / 10,
                "unit": t.get("unit") or "mg",
                "coverage_percent": js_round(cov),
                "surplus": js_round(surplus * 10) / 10,
                "primary_sources": list(dict.fromkeys(sources)),
            }
        )
    return rows


def _coverage_score(matrix: list[dict[str, Any]]) -> float:
    if not matrix:
        return 0.0
    total = 0.0
    for r in matrix:
        target = float(r.get("target") or 0)
        provided = float(r.get("provided") or 0)
        if target > 0:
            total += min(provided / target, 1.0)
        elif provided > 0:
            total += 1.0
    return total / len(matrix)


def _surplus_penalty(matrix: list[dict[str, Any]]) -> float:
    return sum(float(r.get("surplus") or 0) for r in matrix) * surplus_penalty_weight()


def _clinical_function_score(products: list[dict[str, Any]], goals: list[dict[str, Any]]) -> float:
    if not goals:
        return 0.5
    scores = []
    for g in goals:
        best = 0.0
        for p in products:
            for f in p.get("functions") or []:
                best = max(
                    best,
                    _function_match_score(
                        f.get("function") or "",
                        [{**g, "confidence": f.get("confidence")}],
                    ),
                )
        scores.append(best)
    return sum(scores) / len(scores) if scores else 0.0


def _overall_score(
    *,
    coverage: float,
    clinical: float,
    evidence: float,
    yearly_cost: float,
    diversity: float,
    surplus_penalty: float,
    ignore_cost: bool = False,
) -> float:
    w = score_weights()
    if ignore_cost:
        cost_eff = 1.0
        cov_w = w["coverage"] + w["cost_efficiency"] * 0.5
        clin_w = w["clinical_function"] + w["cost_efficiency"] * 0.5
        cost_w = 0.0
    else:
        cost_eff = max(0.0, 1.0 - min(yearly_cost, 15000) / 15000.0)
        cov_w, clin_w, cost_w = w["coverage"], w["clinical_function"], w["cost_efficiency"]
    return (
        cov_w * coverage
        + clin_w * clinical
        + w["evidence"] * evidence
        + cost_w * cost_eff
        + w["diversity"] * diversity
        - surplus_penalty
    )


def _clinical_coverage_by_goal(
    products: list[dict[str, Any]], goals: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows = []
    for g in goals:
        score = 0.0
        contributors = []
        for p in products:
            for f in p.get("functions") or []:
                s = _function_match_score(f.get("function") or "", [{**g, "confidence": f.get("confidence")}])
                if s > score:
                    score = s
                if s > 0.15:
                    contributors.append(p.get("product_name"))
        rows.append(
            {
                "goal_id": g.get("goal_id"),
                "title": g.get("title"),
                "coverage_percent": js_round(score * 100),
                "contributors": list(dict.fromkeys(contributors)),
            }
        )
    return rows


def _why_product_selected(
    product: dict[str, Any],
    matrix: list[dict[str, Any]],
    goals: list[dict[str, Any]],
) -> list[str]:
    reasons = []
    for a in product.get("active_ingredients") or []:
        for row in matrix:
            if row["ingredient_key"] == a.get("ingredient_key") and float(row.get("provided") or 0) > 0:
                reasons.append(
                    f"Provides {a.get('amount_per_serving')}{a.get('unit') or ''} {a.get('name')} "
                    f"toward {row.get('nutrient')} ({row.get('coverage_percent')}% coverage)."
                )
    for f in product.get("functions") or []:
        fn = f.get("function") or ""
        matched = [
            g.get("title")
            for g in goals
            if _function_match_score(fn, [{**g, "confidence": f.get("confidence")}]) > 0.2
        ]
        if matched:
            reasons.append(f"Clinical function «{fn}» supports {', '.join(str(m) for m in matched if m)}.")
    if product.get("role") == "staple":
        reasons.append("Selected as package staple from PACKAGE_TIERS.csv.")
    if not reasons:
        reasons.append("Eligible active catalog product contributing to pathway diversity.")
    return reasons


def _pick_staple(candidates: list[dict[str, Any]], repo: DataRepository, tier: str) -> dict[str, Any] | None:
    tier_map = repo.package_tier_map().get(tier) or {}
    staple_id = str(tier_map.get("staple_product_id") or "")
    staples = [c for c in candidates if c.get("role") == "staple"]
    if staple_id:
        hit = next((c for c in candidates if c["product_id"] == staple_id), None)
        if hit:
            return hit
    return staples[0] if staples else None


def _optimize_essential(
    candidates: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    staple: dict[str, Any] | None,
    alias_groups: dict[str, set[str]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    if staple:
        selected.append(staple)
    pool = [c for c in candidates if not staple or c["product_id"] != staple["product_id"]]
    pool.sort(key=lambda c: (c.get("yearly_cost") or 0, -c.get("evidence_score", 0)))

    has_actives = any(p.get("active_ingredients") for p in candidates)

    def ok(sel: list[dict[str, Any]]) -> bool:
        matrix = coverage_matrix(sel, targets, alias_groups)
        cov = _coverage_score(matrix)
        clinical = _clinical_function_score(sel, goals)
        if has_actives and any(t.get("target_daily", 0) > 0 for t in targets):
            return cov >= essential_coverage_floor()
        return clinical >= 0.35 or len(sel) >= 2

    for c in pool:
        if ok(selected):
            break
        before = _coverage_score(coverage_matrix(selected, targets, alias_groups)) + _clinical_function_score(
            selected, goals
        )
        trial = selected + [c]
        after = _coverage_score(coverage_matrix(trial, targets, alias_groups)) + _clinical_function_score(
            trial, goals
        )
        if after > before + 1e-6:
            selected.append(c)
        if len(selected) >= 4:
            break
    if not ok(selected):
        adjuncts = [c for c in pool if c.get("functions")]
        adjuncts.sort(key=lambda c: (-_clinical_function_score([c], goals), c.get("yearly_cost") or 0))
        for c in adjuncts[:2]:
            if c["product_id"] not in {x["product_id"] for x in selected}:
                selected.append(c)
    return selected


def _optimize_balanced(
    candidates: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    staple: dict[str, Any] | None,
    alias_groups: dict[str, set[str]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    if staple:
        selected.append(staple)
    pool = [c for c in candidates if not staple or c["product_id"] != staple["product_id"]]

    def score(sel: list[dict[str, Any]]) -> float:
        matrix = coverage_matrix(sel, targets, alias_groups)
        return _overall_score(
            coverage=_coverage_score(matrix),
            clinical=_clinical_function_score(sel, goals),
            evidence=sum(p.get("evidence_score", 0) for p in sel) / max(len(sel), 1),
            yearly_cost=sum(float(p.get("yearly_cost") or 0) for p in sel),
            diversity=min(1.0, len({p.get("role") for p in sel}) / 3.0),
            surplus_penalty=_surplus_penalty(matrix),
            ignore_cost=False,
        )

    improved = True
    while improved and len(selected) < 6:
        improved = False
        best_add = None
        best_score = score(selected)
        for c in pool:
            if c["product_id"] in {x["product_id"] for x in selected}:
                continue
            s = score(selected + [c])
            if s > best_score + 1e-6:
                best_score = s
                best_add = c
        if best_add:
            selected.append(best_add)
            improved = True
    return selected


def _optimize_optimal(
    candidates: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    staple: dict[str, Any] | None,
    alias_groups: dict[str, set[str]],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    if staple:
        selected.append(staple)
    pool = [c for c in candidates if not staple or c["product_id"] != staple["product_id"]]

    def score(sel: list[dict[str, Any]]) -> float:
        matrix = coverage_matrix(sel, targets, alias_groups)
        return _overall_score(
            coverage=_coverage_score(matrix),
            clinical=_clinical_function_score(sel, goals),
            evidence=sum(p.get("evidence_score", 0) for p in sel) / max(len(sel), 1),
            yearly_cost=0,
            diversity=min(1.0, len(sel) / 8.0),
            surplus_penalty=_surplus_penalty(matrix) * 0.25,
            ignore_cost=True,
        )

    improved = True
    while improved and len(selected) < 8:
        improved = False
        best_add = None
        best_score = score(selected)
        for c in pool:
            if c["product_id"] in {x["product_id"] for x in selected}:
                continue
            s = score(selected + [c])
            if s > best_score + 1e-6:
                best_score = s
                best_add = c
        if best_add:
            selected.append(best_add)
            improved = True
    return selected


def build_optimized_packages(
    *,
    repo: DataRepository,
    profile: Any,
    health_insights: list[dict[str, Any]],
    ingredients: list[dict[str, Any]],
    product_recs: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Compute essential / balanced / optimal packages from CSV inventory.
    Output shape stays compatible with enrich_package_for_detail + frontend.
    """
    del product_recs
    weight_kg = float(getattr(profile, "weight_kg", None) or 10)
    pet_name = getattr(profile, "name", None) or "Pet"
    candidates = load_candidate_products(repo, weight_kg)
    targets = _targets_from_ingredients(ingredients)
    goals = [{"goal_id": h.get("goal_id"), "title": h.get("title")} for h in (health_insights or [])]
    alias_groups = repo.ingredient_alias_groups()
    if candidates:
        alias_groups = candidates[0].get("alias_groups") or alias_groups

    tier_objectives = {
        "essential": {
            "objective": "Minimize yearly cost subject to required coverage.",
            "recommended": False,
        },
        "balanced": {
            "objective": "Maximize nutrient coverage, minimize surplus, reasonable cost.",
            "recommended": True,
        },
        "optimal": {
            "objective": "Maximize clinical, functional, and evidence coverage; ignore cost.",
            "recommended": False,
        },
    }

    packages: list[dict[str, Any]] = []
    for tier in ("essential", "balanced", "optimal"):
        t0 = start_timer()
        tier_row = repo.package_tier_map().get(tier) or {}
        title = str(tier_row.get("title") or f"{tier.title()} Care")
        discount = float(tier_row.get("yearly_discount_factor") or 0.92)
        staple = _pick_staple(candidates, repo, tier)
        meta = tier_objectives[tier]

        if tier == "essential":
            selected = _optimize_essential(candidates, targets, goals, staple, alias_groups)
        elif tier == "balanced":
            selected = _optimize_balanced(candidates, targets, goals, staple, alias_groups)
        else:
            selected = _optimize_optimal(candidates, targets, goals, staple, alias_groups)

        matrix = coverage_matrix(selected, targets, alias_groups)
        cov = _coverage_score(matrix)
        clinical = _clinical_function_score(selected, goals)
        evidence = sum(p.get("evidence_score", 0) for p in selected) / max(len(selected), 1)
        yearly_raw = sum(float(p.get("yearly_cost") or 0) for p in selected)
        yearly_cost = js_round(yearly_raw * discount)
        monthly_cost = js_round(yearly_cost / 12.0)
        diversity = min(1.0, len({p.get("role") for p in selected}) / 3.0)
        overall = _overall_score(
            coverage=cov,
            clinical=clinical,
            evidence=evidence,
            yearly_cost=yearly_raw,
            diversity=diversity,
            surplus_penalty=_surplus_penalty(matrix),
            ignore_cost=(tier == "optimal"),
        )

        clinical_rows = _clinical_coverage_by_goal(selected, goals)
        products_included = []
        for p in selected:
            reasons = _why_product_selected(p, matrix, goals)
            products_included.append(
                {
                    "type": p.get("product_type"),
                    "name": p.get("product_name"),
                    "product_id": p.get("product_id"),
                    "brand": p.get("brand"),
                    "category": p.get("category"),
                    "subcategory": p.get("subcategory"),
                    "monthly_cost": p.get("monthly_cost"),
                    "yearly_cost": p.get("yearly_cost"),
                    "price": p.get("price"),
                    "serving_size": p.get("serving_size"),
                    "daily_amount": p.get("serving_size"),
                    "monthly_quantity": f"{(p.get('yearly') or {}).get('packages_needed', 1)} packs/year",
                    "why_selected": " ".join(reasons),
                    "selection_reasons": reasons,
                    "active_ingredients": p.get("active_ingredients") or [],
                    "functions": p.get("functions") or [],
                    "yearly_plan": p.get("yearly"),
                    "coverage_percent": js_round(cov * 100),
                    "route": f"#/products/{p.get('product_id')}",
                }
            )

        selected_ids = {p["product_id"] for p in selected}
        rejected = []
        decisions = []
        for p in selected:
            decisions.append(
                decision(
                    "Accepted",
                    subject=str(p.get("product_name") or p.get("product_id")),
                    reasons=_why_product_selected(p, matrix, goals),
                    score=p.get("evidence_score"),
                )
            )
        for c in candidates:
            if c["product_id"] in selected_ids:
                continue
            if c.get("role") == "staple":
                reasons = [
                    "Alternate staple not chosen for this tier (PACKAGE_TIERS staple wins).",
                ]
                rejected.append(
                    {
                        "product_id": c["product_id"],
                        "product_name": c["product_name"],
                        "reason": reasons[0],
                        "reasons": reasons,
                        "decision": "Rejected",
                    }
                )
                decisions.append(
                    decision("Rejected", subject=str(c.get("product_name")), reasons=reasons)
                )
            elif c.get("functions") or c.get("active_ingredients"):
                reasons = [
                    "Did not improve tier objective enough versus cost/surplus/evidence trade-off.",
                ]
                # Enrich when matrix coverage for this candidate alone is knowable without re-optimizing
                if targets and cov < 1.0:
                    reasons.append(f"Tier coverage score currently {js_round(cov * 100)}%")
                rejected.append(
                    {
                        "product_id": c["product_id"],
                        "product_name": c["product_name"],
                        "reason": reasons[0],
                        "reasons": reasons,
                        "decision": "Rejected",
                    }
                )
                decisions.append(
                    decision("Rejected", subject=str(c.get("product_name")), reasons=reasons)
                )

        coverage_score = js_round(cov * 100)
        if coverage_score == 0 and clinical > 0:
            coverage_score = js_round(clinical * 100)

        nutrition_coverage = [
            {"goal_id": r["goal_id"], "title": r["title"], "coverage_percent": r["coverage_percent"]}
            for r in clinical_rows
        ] or [
            {
                "goal_id": r["ingredient_key"],
                "title": r["nutrient"],
                "coverage_percent": r["coverage_percent"],
            }
            for r in matrix
        ]

        score_breakdown = {
            "coverage": js_round(cov * 100),
            "clinical_function": js_round(clinical * 100),
            "evidence": js_round(evidence * 100),
            "diversity": js_round(diversity * 100),
            "weights": score_weights(),
            "overall_score": js_round(overall * 100),
        }

        fx = empty_execution("PACKAGE_OPTIMIZER_V2_1", subject=tier)
        fx["inputs"] = {
            "tier": tier,
            "candidate_count": len(candidates),
            "target_count": len(targets),
            "goals": [g.get("title") for g in goals],
            "objective": meta["objective"],
        }
        fx["steps"] = [
            step(
                1,
                "load_candidates",
                expression="ACTIVE PRODUCT_CATALOG + joins",
                inputs={"candidates": len(candidates)},
                result=len(candidates),
            ),
            step(
                2,
                "pick_staple",
                expression="PACKAGE_TIERS staple for tier",
                result=(staple or {}).get("product_name") if staple else None,
            ),
            step(
                3,
                "optimize_selection",
                expression=f"_optimize_{tier}(...)",
                inputs={"selected": len(selected)},
                result=[p.get("product_id") for p in selected],
                note="Per-candidate trial scores inside greedy loops still NOT CURRENTLY TRACEABLE",
            ),
            step(
                4,
                "coverage_matrix",
                expression="provided / recommended per nutrient",
                result=coverage_score,
                unit="%",
            ),
            step(
                5,
                "overall_score",
                expression="weighted(coverage, clinical, evidence, diversity, cost, surplus)",
                inputs=score_breakdown,
                result=js_round(overall * 100),
            ),
        ]
        fx["decisions"] = decisions
        fx["outputs"] = {
            "tier": tier,
            "overall_score": js_round(overall * 100),
            "coverage_score": coverage_score,
            "monthly_cost": monthly_cost,
            "yearly_cost": yearly_cost,
            "selected_count": len(selected),
            "rejected_count": len(rejected),
            "score_breakdown": score_breakdown,
        }
        seal_execution(fx, started=t0)

        packages.append(
            {
                "tier": tier,
                "package_id": tier,
                "title": title,
                "recommended": bool(meta["recommended"]),
                "best_for": meta["objective"],
                "tagline": meta["objective"],
                "description": (
                    f"{title} for {pet_name}: {meta['objective']} "
                    f"Overall score {js_round(overall * 100)}/100."
                ),
                "coverage_score": coverage_score,
                "overall_score": js_round(overall * 100),
                "monthly_cost": monthly_cost,
                "yearly_cost": yearly_cost,
                "yearly_discount_factor": discount,
                "includes_summary": [f"{p.get('product_name')} · {p.get('serving_size')}" for p in selected],
                "products_included": products_included,
                "nutrition_coverage": nutrition_coverage,
                "coverage_matrix": matrix,
                "clinical_coverage": clinical_rows,
                "products_rejected": rejected,
                "products_rejected_count": len(rejected),
                "candidates_evaluated_count": len(candidates),
                "score_breakdown": score_breakdown,
                "formula_execution": fx,
                "observatory": {
                    "formula_id": "PACKAGE_OPTIMIZER_V2_1",
                    "code_file": "app/agent/package_optimizer.py",
                    "function": "build_optimized_packages",
                    "selected_ids": sorted(selected_ids),
                    "rejected": rejected,
                    "formula_execution": fx,
                    "note": "Accept/reject decisions emitted; per-candidate greedy trial scores still NOT CURRENTLY TRACEABLE.",
                },
                "plan_365": {
                    "products": [
                        {
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "role": p.get("role"),
                            **(p.get("yearly") or {}),
                        }
                        for p in selected
                    ],
                    "yearly_cost": yearly_cost,
                    "monthly_cost_derived": monthly_cost,
                },
                "overview": (
                    f"Computed from ACTIVE PRODUCT_CATALOG + components/functions/pricing/feeding. "
                    f"Objective: {meta['objective']}"
                ),
                "activities_included": [],
                "why_fits": meta["objective"],
                "subscribe_cta": f"Start {title}",
                "optimization_objective": meta["objective"],
            }
        )

    return packages
