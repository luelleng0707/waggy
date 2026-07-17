"""
Assembles PPIE pipeline state into the JavaScript frontend contract (FRONTEND_LAYOUT_SPEC.md).
All monetary fields are raw numbers (RMB yuan); the JS shell applies fmtMoney().
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pandas as pd

from app.agent.condition_lookup import (
    condition_candidates,
    condition_matches,
    ingredient_key,
)
from app.agent.ingredient_engine import map_ingredients
from app.agent.calculation_trace import build_calculation_trace
from app.agent.bundle_engine import build_monthly_plan, build_yearly_plan
from app.agent.package_detail import (
    activities_for_condition,
    build_product_analysis,
    enrich_package_for_detail,
)
from app.agent.pipeline_trace import build_pipeline_trace
from app.agent.variable_map import PIPELINE_STAGES, VARIABLE_MAP
from app.agent.state import DogProfileInput, WellnessReportPayload
from app.agent.utils import (
    DataRepository,
    calculate_unit_economics,
    feeding_rule_for_product,
    js_round,
)
from app.agent.wellness_map import (
    friendly_trait_label,
    goal_for_condition,
    priority_label,
    WELLNESS_GOALS,
)
from app.agent.version import ALGORITHM_VERSION as ENGINE_VERSION

LEGACY_MOCK_PATTERN = re.compile(r"^(SF00[1-5]|SP00[1-8]|TR00[1-2])$", re.I)

VERIFIED_STAPLES = {
    "essential": "FF001",
    "balanced": "FF002_CHICKEN",
    "optimal": "FF003",
}
DEFAULT_TREAT = "TR003"
DEFAULT_SUPPLEMENT = "SP011"
FALLBACK_SUPPLEMENTS = ["SP013", "SP014", "SP015"]


def _is_verified_product(product_id: str) -> bool:
    return bool(product_id) and not LEGACY_MOCK_PATTERN.match(str(product_id))


def _size_bracket(weight_kg: float) -> str:
    if weight_kg < 8:
        return "small"
    if weight_kg < 18:
        return "medium"
    if weight_kg < 35:
        return "large"
    return "giant"


def _age_stage(age_years: float) -> str:
    if age_years < 1:
        return "puppy"
    if age_years >= 7:
        return "senior"
    return "adult"


def _time_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def _list_price_rmb(pricing_df: pd.DataFrame, product_id: str) -> float:
    row = pricing_df[pricing_df["product_id"] == product_id]
    if row.empty:
        return 0.0
    return float(row.iloc[0]["list_price_rmb"])


def _catalog_row(catalog_df: pd.DataFrame, product_id: str) -> dict[str, Any]:
    row = catalog_df[catalog_df["product_id"] == product_id]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def _product_type_from_catalog(row: dict[str, Any]) -> str:
    """Mirror JS categoryToProductType for Fresh Food / Supplements / Treats."""
    category = str(row.get("category", ""))
    if category == "Fresh Food":
        return "fresh_food"
    if category == "Nutritional Supplements":
        return "supplement"
    if category in ("Homestyle Bakery", "All-Natural Treats"):
        return "treat"
    category_l = category.lower()
    sub = str(row.get("subcategory", "")).lower()
    if "fresh" in sub or "fresh" in category_l:
        return "fresh_food"
    if "supplement" in category_l:
        return "supplement"
    if "treat" in category_l or "bakery" in category_l:
        return "treat"
    return sub or "product"


def _staple_monthly_cost(pricing_df: pd.DataFrame, product_id: str) -> int:
    """JS: Math.round(unit_cost_per_bag * 7.5)."""
    unit_cost = calculate_unit_economics(pricing_df, product_id)
    return js_round(unit_cost * 7.5)


def _catalog_staples(catalog_df: pd.DataFrame, pricing_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Fresh-food staples with pricing fields — mirrors db.getAllProducts() filter."""
    staples = []
    for _, row in catalog_df.iterrows():
        rec = row.to_dict()
        if _product_type_from_catalog(rec) != "fresh_food":
            continue
        pid = str(rec.get("product_id", ""))
        if not _is_verified_product(pid):
            continue
        price = _list_price_rmb(pricing_df, pid)
        unit_cost = calculate_unit_economics(pricing_df, pid)
        staples.append({
            **rec,
            "product_id": pid,
            "product_type": "fresh_food",
            "price": price,
            "unit_cost_per_bag": unit_cost,
        })
    return staples


def _pick_staple(staples: list[dict[str, Any]], tier: str) -> dict[str, Any] | None:
    """Mirror wellnessEngine makePackage staple selection."""
    if not staples:
        return None
    if tier == "essential":
        return next(
            (p for p in staples if str(p.get("subcategory", "")) == "fresh_single"),
            staples[-1],
        )
    return next(
        (
            p for p in staples
            if str(p.get("brand", "")) == "Wagtopia" and str(p.get("subcategory", "")) == "fresh_combo"
        ),
        staples[0],
    )


def build_profile_block(
    profile: DogProfileInput,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Mirror src/engine/index.js analyze() profile block."""
    breeds = (meta or {}).get("breeds")
    if not breeds:
        breeds = [profile.primary_breed]
        if profile.secondary_breed:
            breeds.append(profile.secondary_breed)
    sex = profile.sex or profile.gender
    return {
        "pet_name": profile.name,
        "breeds": breeds,
        "birthday": profile.birthday,
        "gender": sex,
        "sex": sex,
        "bcs": profile.bcs,
        "activity_level": profile.activity_level,
        "current_environment": profile.current_environment,
        "weight_kg": float(profile.weight_kg),
        "height_cm": profile.height_cm,
        "age_years": round(float(profile.age_years), 1),
        "age_stage": _age_stage(profile.age_years),
    }


def collect_evidence(
    risks: list[dict[str, Any]],
    ingredients: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Port of evidenceEngine.collectEvidence."""
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()

    for risk in risks:
        source = risk.get("source")
        if source:
            key = f"{source.get('source_url')}{source.get('source_quote')}"
            if key not in seen:
                seen.add(key)
                evidence.append({
                    "type": "breed",
                    "condition": risk.get("condition_name"),
                    "breed": source.get("breed"),
                    "source_name": source.get("source_name"),
                    "quote": source.get("source_quote"),
                    "url": source.get("source_url"),
                })

    for ing in ingredients:
        key = f"{ing.get('source_url')}{ing.get('evidence_quote')}"
        if key not in seen:
            seen.add(key)
            evidence.append({
                "type": "ingredient",
                "condition": ing.get("ingredient_name"),
                "breed": None,
                "source_name": ing.get("source_name"),
                "quote": ing.get("evidence_quote"),
                "url": ing.get("source_url"),
            })

    return evidence


def build_biology_block(biology: dict[str, Any], profile: DogProfileInput) -> dict[str, Any]:
    """Port of wellnessEngine.buildBiologySummary — Set insertion order, filtered descriptors."""
    traits: list[str] = []
    seen: set[str] = set()
    descriptors = []
    for breed in biology.get("resolved_breeds", []):
        size = breed.get("size") or breed.get("size_class")
        body = breed.get("body_type")
        coat = breed.get("coat_type")
        energy = breed.get("energy") or breed.get("energy_level")
        weakness = breed.get("weakness_group")
        function = breed.get("function_group")
        for val in (size, body, coat, energy, weakness, function):
            if val and str(val) not in seen:
                seen.add(str(val))
                traits.append(str(val))
        descriptors.append({
            "breed": breed.get("breed") or breed.get("breed_name"),
            "size": size,
            "body_type": body,
            "coat_type": coat,
            "energy": energy,
            "weakness_group": weakness,
            "function_group": function,
        })
    breeds = [profile.primary_breed]
    if profile.secondary_breed:
        breeds.append(profile.secondary_breed)
    return {
        "breeds": breeds,
        "breed_count": len(biology.get("resolved_breeds", [])),
        "age_years": round(float(profile.age_years), 1),
        "age_stage": _age_stage(profile.age_years),
        "trait_summary": traits,
        "descriptors": descriptors,
    }


def build_health_insights(
    risks: list[dict[str, Any]],
    pet_name: str,
) -> list[dict[str, Any]]:
    """Mirror src/engine/wellnessEngine.js buildHealthInsights — no hardcoded confidence."""
    grouped: dict[str, dict[str, Any]] = {}

    for r in risks:
        goal_id = goal_for_condition(r.get("condition_key") or r.get("condition_name") or "")
        goal = WELLNESS_GOALS.get(
            goal_id,
            {"title": "General Wellness", "why_template": "overall preventative nutrition may support long-term vitality"},
        )
        if goal_id not in grouped:
            grouped[goal_id] = {
                "goal_id": goal_id,
                "title": goal["title"],
                "priority_score": 0.0,
                "biological_risk_percent": 0.0,
                "observed_prevalence_percent": None,
                "confidence_percent": 0.0,
                "evidence_count": 0,
                "supporting_conditions": [],
                "supporting_traits": [],
                "evidence_sources": [],
                "groomer_priority": False,
            }

        g = grouped[goal_id]
        bio = r.get("trait_risk_percent")
        if bio is None:
            bio = r.get("estimated_risk_percent")
        if bio is None:
            bio = r.get("risk_percent") or 0
        obs = r.get("breed_prevalence_percent")

        g["priority_score"] = max(g["priority_score"], float(r.get("risk_percent") or 0))
        g["biological_risk_percent"] = max(g["biological_risk_percent"], float(bio or 0))
        if obs is not None:
            g["observed_prevalence_percent"] = max(g["observed_prevalence_percent"] or 0, float(obs))
        g["confidence_percent"] = max(g["confidence_percent"], float(r.get("confidence_percent") or 0))
        g["evidence_count"] = max(g["evidence_count"], int(r.get("evidence_count") or 0))
        g["groomer_priority"] = g["groomer_priority"] or bool(r.get("groomer_boosted"))

        g["supporting_conditions"].append(r.get("condition_name"))
        for t in r.get("supporting_traits") or []:
            label = friendly_trait_label(str(t.get("category", "")), str(t.get("value", "")))
            if label not in g["supporting_traits"]:
                g["supporting_traits"].append(label)

        if r.get("source_name"):
            g["evidence_sources"].append({
                "source_name": r.get("source_name"),
                "source_quote": r.get("source_quote"),
                "source_url": r.get("source_url"),
            })

    insights = []
    for g in grouped.values():
        goal = WELLNESS_GOALS.get(g["goal_id"], {})
        observed = g["observed_prevalence_percent"]
        biological = g["biological_risk_percent"]
        difference = (
            js_round((biological - observed) * 10) / 10
            if observed is not None
            else None
        )
        title = goal.get("title", g["title"])
        why = goal.get("why_template", "preventative care may provide long-term benefit")
        insights.append({
            **g,
            "estimated_biological_risk_percent": js_round(biological * 10) / 10,
            "observed_breed_prevalence_percent": (
                js_round(observed * 10) / 10 if observed is not None else None
            ),
            "estimate_vs_observed_difference": difference,
            "explanation": (
                f"Our veterinary research team estimates {pet_name} may benefit from "
                f"preventative {title.lower()} support — {why}. This does NOT mean "
                f"{pet_name} will develop illness; it highlights areas where long-term "
                f"wellness care may help most."
            ),
            "why_this_matters": why,
            "peer_reviewed_study_count": len(g["evidence_sources"]),
        })

    insights.sort(
        key=lambda x: (-int(x["groomer_priority"]), -x["priority_score"])
    )
    return insights[:8]


def build_wellness_coverage(
    health_insights: list[dict[str, Any]],
    product_recs: list[dict[str, Any]] | None = None,
    ingredients: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Mirror src/engine/wellnessEngine.js buildWellnessCoverage."""
    product_recs = product_recs or []
    ingredients = ingredients or []
    default_goals = [
        "joint_health",
        "skin_health",
        "dental_health",
        "digestive_health",
        "weight_management",
        "immune_support",
        "activity_support",
    ]
    dimensions: dict[str, dict[str, Any]] = {
        gid: {
            "title": (WELLNESS_GOALS.get(gid) or {}).get("title", gid),
            "coverage_percent": 72,
        }
        for gid in default_goals
    }

    for insight in health_insights:
        products_for_goal = [p for p in product_recs if (p.get("coverage_percent") or 0) > 0]
        base = min(
            98,
            60 + insight["priority_score"] * 0.8 + (insight.get("confidence_percent") or 0) * 0.2,
        )
        product_boost = (
            min(15, products_for_goal[0]["coverage_percent"] * 0.1) if products_for_goal else 0
        )
        dimensions[insight["goal_id"]] = {
            "title": insight["title"],
            "coverage_percent": js_round(min(98, base + product_boost)),
        }

    if ingredients:
        avg_ing = min(95, 70 + len(ingredients) * 4)
        dimensions.setdefault(
            "digestive_health",
            {"title": "Digestive Health", "coverage_percent": avg_ing},
        )
        dimensions["digestive_health"]["coverage_percent"] = max(
            dimensions["digestive_health"]["coverage_percent"],
            avg_ing,
        )

    values = [d["coverage_percent"] for d in dimensions.values()]
    overall = js_round(sum(values) / len(values)) if values else 75
    return {
        "overall_score": overall,
        "max_score": 100,
        "label": "Overall Wellness Coverage",
        "subtitle": "Nutritional coverage across preventative health priorities",
        "dimensions": [
            {"goal_id": gid, "title": d["title"], "coverage_percent": d["coverage_percent"]}
            for gid, d in dimensions.items()
        ],
    }


def build_wellness_summary(
    pet_name: str,
    biology: dict[str, Any],
    health_insights: list[dict[str, Any]],
    wellness_coverage: dict[str, Any],
) -> dict[str, Any]:
    priorities = [priority_label(h["goal_id"], h["title"]) for h in health_insights[:4]]
    focus = priorities[:3]
    if len(focus) > 1:
        focus_text = ", ".join(focus[:-1]) + " and " + focus[-1]
    else:
        focus_text = focus[0] if focus else "core wellness"

    return {
        "greeting": _time_greeting(),
        "intro": (
            f"Based on {pet_name}'s breed, age, body size and biological characteristics, "
            f"our veterinary research team estimates that preventative {focus_text.lower()} "
            f"care will provide the greatest long-term health benefit."
        ),
        "closing": "We created several personalized wellness plans that balance health coverage and monthly cost.",
        "wellness_score": wellness_coverage["overall_score"],
        "score_label": "Estimated Wellness Score",
        "primary_priorities": priorities,
        "traits_analysed": biology.get("trait_summary", []),
        "analysis_detail": [
            {
                "goal_id": h["goal_id"],
                "title": priority_label(h["goal_id"], h["title"]),
                "biological_estimate_percent": h["estimated_biological_risk_percent"],
                "observed_prevalence_percent": h["observed_breed_prevalence_percent"],
                "difference_percent": h.get("estimate_vs_observed_difference"),
                "supporting_traits": h.get("supporting_traits", []),
                "explanation": h.get("explanation"),
            }
            for h in health_insights[:6]
        ],
    }


def build_product_recommendations(
    reports: list[WellnessReportPayload],
    repo: DataRepository,
    profile: DogProfileInput,
) -> list[dict[str, Any]]:
    catalog_df = repo.product_catalog()
    pricing_df = repo.product_pricing()
    rules_df = repo.product_feeding_rules()
    seen: set[str] = set()
    products: list[dict[str, Any]] = []

    for report in reports:
        for product_id, fulfillment in report.targeted_intervention.commercial_fulfillment.items():
            if product_id in seen or not _is_verified_product(product_id):
                continue
            seen.add(product_id)
            cat_row = _catalog_row(catalog_df, product_id)
            price = int(round(_list_price_rmb(pricing_df, product_id)))
            feeding = feeding_rule_for_product(rules_df, product_id, profile.weight_kg)
            serving = (
                f"{feeding['daily_amount']}{feeding['daily_unit']}/day"
                if feeding
                else fulfillment.standard_daily_feeding
            )
            products.append({
                "product_id": product_id,
                "product_name": fulfillment.product_name,
                "brand": cat_row.get("brand", "Wagtopia"),
                "product_type": _product_type_from_catalog(cat_row),
                "price": price,
                "serving_size": serving,
                "suggested_usage": serving,
                "coverage_percent": int(round(fulfillment.coverage_pct)),
                "monthly_cost_estimate": price,
                "active_ingredients": [
                    {"name": report.targeted_intervention.active_ingredient, "amount": fulfillment.yielded_active_content}
                ],
                "why_selected": (
                    f"This product supplies approximately {int(round(fulfillment.coverage_pct))}% "
                    f"of {profile.name}'s recommended daily nutritional targets for "
                    f"{report.targeted_intervention.active_ingredient}."
                ),
                "combined_coverage_note": (
                    f"Combined with {profile.name}'s daily diet this achieves "
                    f"{int(round(fulfillment.coverage_pct))}% of our recommended target."
                ),
                "advantages": ["Wagtopia curated formula"] if cat_row.get("brand") == "Wagtopia" else [],
            })

    products.sort(key=lambda p: p["coverage_percent"], reverse=True)
    return products


def _tier_product_ids(
    tier: str,
    product_recs: list[dict[str, Any]],
) -> list[str]:
    """Legacy helper retained for tests; package builder no longer forces defaults."""
    staple = VERIFIED_STAPLES[tier]
    ids = [staple]
    rec_ids = [p["product_id"] for p in product_recs if _is_verified_product(p["product_id"])]
    if tier == "essential":
        if rec_ids:
            ids.append(rec_ids[0])
    elif tier == "balanced":
        for pid in rec_ids[:2]:
            if pid not in ids:
                ids.append(pid)
    else:
        for pid in rec_ids[:3]:
            if pid not in ids:
                ids.append(pid)
    return [pid for pid in ids if _is_verified_product(pid)]


def _includes_summary_from_items(items: list[dict[str, Any]], tier: str) -> list[str]:
    """Mirror JS buildIncludesSummary."""
    counts: dict[str, int] = {}
    for item in items:
        t = str(item.get("type", ""))
        counts[t] = counts.get(t, 0) + 1
    lines: list[str] = []
    if counts.get("fresh_food") or counts.get("kibble") or counts.get("staple_food"):
        lines.append("1 fresh food" if tier == "essential" else "Premium fresh food")
    if counts.get("supplement"):
        n = counts["supplement"]
        lines.append(f"{n} supplement{'s' if n > 1 else ''}")
    if counts.get("treat"):
        n = counts["treat"]
        lines.append(f"{n} functional treat{'s' if n > 1 else ''}")
    if counts.get("dental"):
        lines.append("1 dental product" if tier == "essential" else "Dental support")
    if tier == "optimal" and counts.get("supplement", 0) >= 3:
        lines.append("Complete supplement stack")
    return lines


def _includes_summary(product_ids: list[str], catalog_df: pd.DataFrame, tier: str) -> list[str]:
    lines: list[str] = []
    counts = {"fresh_food": 0, "supplement": 0, "treat": 0}
    for pid in product_ids:
        row = _catalog_row(catalog_df, pid)
        ptype = _product_type_from_catalog(row)
        if ptype == "fresh_food":
            counts["fresh_food"] += 1
        elif ptype == "supplement":
            counts["supplement"] += 1
        elif ptype == "treat":
            counts["treat"] += 1
    if counts["fresh_food"]:
        lines.append("1 fresh food" if tier == "essential" else "Premium fresh food")
    if counts["supplement"]:
        n = counts["supplement"]
        lines.append(f"{n} supplement{'s' if n > 1 else ''}")
    if counts["treat"]:
        n = counts["treat"]
        lines.append(f"{n} functional treat{'s' if n > 1 else ''}")
    if tier == "optimal" and counts["supplement"] >= 3:
        lines.append("Complete supplement stack")
    return lines


def build_wellness_packages(
    product_recs: list[dict[str, Any]],
    health_insights: list[dict[str, Any]],
    profile: DogProfileInput,
    wellness_coverage: dict[str, Any],
    repo: DataRepository,
) -> list[dict[str, Any]]:
    """Mirror src/engine/wellnessEngine.js buildWellnessPackages pricing and selection."""
    catalog_df = repo.product_catalog()
    pricing_df = repo.product_pricing()
    rules_df = repo.product_feeding_rules()
    pet_name = profile.name
    top_goals = ", ".join(priority_label(h["goal_id"], h["title"]) for h in health_insights[:3])

    staples = _catalog_staples(catalog_df, pricing_df)
    supps = [p for p in product_recs if p.get("product_type") == "supplement"][:3]
    treats = [p for p in product_recs if p.get("product_type") == "treat"][:2]
    dental = [
        p for p in product_recs
        if p.get("subcategory") == "dental_chew" or "Dental" in str(p.get("product_name", ""))
    ][:1]

    tier_meta = {
        "essential": {
            "title": "Essential Care",
            "recommended": False,
            "best_for": "Budget-conscious owners.",
            "mult": 0.72,
            "coverage_floor": 72,
            "suppCount": 1,
            "treatCount": 1,
            "dental": True,
            "description": (
                f"Provides the minimum evidence-supported nutritional coverage for {pet_name}'s "
                f"biological needs while keeping monthly cost as low as possible."
            ),
            "includes_extra": [],
        },
        "balanced": {
            "title": "Balanced Care",
            "recommended": True,
            "best_for": None,
            "mult": 1.0,
            "coverage_floor": 88,
            "suppCount": 2,
            "treatCount": 2,
            "dental": True,
            "description": (
                f"Our recommended balance between health coverage and affordability. Provides "
                f"strong support for {pet_name}'s highest-priority health needs without unnecessary spending."
            ),
            "includes_extra": [],
        },
        "optimal": {
            "title": "Optimal Care",
            "recommended": False,
            "best_for": None,
            "mult": 1.08,
            "coverage_floor": 97,
            "suppCount": 3,
            "treatCount": 2,
            "dental": True,
            "description": (
                "Designed for owners who want the highest possible nutritional coverage with minimal compromises."
            ),
            "includes_extra": ["Skin support", "Joint support", "Digestive support"],
        },
    }

    packages = []
    for tier, meta in tier_meta.items():
        items: list[dict[str, Any]] = []
        staple = _pick_staple(staples, tier)
        if staple:
            pid = staple["product_id"]
            items.append({
                "type": "fresh_food",
                "name": staple.get("product_name", pid),
                "product_id": pid,
                "brand": staple.get("brand", "Wagtopia"),
                "category": staple.get("category"),
                "monthly_cost": _staple_monthly_cost(pricing_df, pid),
                "price": js_round(_list_price_rmb(pricing_df, pid)),
            })

        for s in supps[: meta["suppCount"]]:
            items.append({
                "type": "supplement",
                "name": s.get("product_name"),
                "product_id": s.get("product_id"),
                "brand": s.get("brand", "Wagtopia"),
                "category": s.get("product_type"),
                "monthly_cost": js_round(float(s.get("price") or 0)),
                "price": js_round(float(s.get("price") or 0)),
            })
        for t in treats[: meta["treatCount"]]:
            items.append({
                "type": "treat",
                "name": t.get("product_name"),
                "product_id": t.get("product_id"),
                "brand": t.get("brand", "Wagtopia"),
                "category": t.get("product_type"),
                "monthly_cost": js_round(float(t.get("price") or 0)),
                "price": js_round(float(t.get("price") or 0)),
            })
        if meta["dental"] and dental:
            d0 = dental[0]
            items.append({
                "type": "dental",
                "name": d0.get("product_name"),
                "product_id": d0.get("product_id"),
                "brand": d0.get("brand", "Wagtopia"),
                "category": d0.get("product_type"),
                "monthly_cost": js_round(float(d0.get("price") or 0)),
                "price": js_round(float(d0.get("price") or 0)),
            })

        products_included = []
        for item in items:
            # enrichPackageProduct (wellnessEngine.js) — serving from rec, not feeding rule.
            name = item.get("name")
            rec = next((p for p in product_recs if p.get("product_name") == name), None)
            cat_row = _catalog_row(catalog_df, str(item.get("product_id") or ""))
            pid = (rec or {}).get("product_id") or item.get("product_id") or cat_row.get("product_id")
            unit_type = "units"
            if pid:
                prow = pricing_df[pricing_df["product_id"] == pid] if not pricing_df.empty else None
                if prow is not None and not prow.empty and "unit_label" in prow.columns:
                    unit_type = str(prow.iloc[0].get("unit_label") or "units")
            daily = (rec or {}).get("serving_size") or "1 serving/day"
            units_daily = float((rec or {}).get("units_needed_daily") or 1)
            monthly_qty = js_round(units_daily * 30)
            products_included.append({
                **item,
                "product_id": pid,
                "brand": (rec or {}).get("brand") or item.get("brand") or cat_row.get("brand") or "Wagtopia",
                "category": item.get("type"),
                "serving_size": daily,
                "daily_amount": daily,
                "monthly_quantity": f"{monthly_qty} {unit_type}/month",
                "price": (rec or {}).get("price") if rec and rec.get("price") is not None else item.get("price"),
                "coverage_percent": (rec or {}).get("coverage_percent") or 0,
                "why_selected": (rec or {}).get("why_selected") or "",
                "combined_coverage_note": (rec or {}).get("combined_coverage_note") or "",
                "advantages": (rec or {}).get("advantages") or [],
                "active_ingredients": (rec or {}).get("active_ingredients") or [],
                "nutrition_contribution": (rec or {}).get("goal_coverage") or [],
            })

        monthly_raw = sum(float(i.get("monthly_cost") or 0) for i in products_included)
        monthly_cost = js_round(monthly_raw * meta["mult"])
        yearly_discount = 0.95 if tier == "essential" else (0.92 if tier == "balanced" else 0.88)
        yearly_cost = js_round(monthly_cost * 12 * yearly_discount)

        dims = wellness_coverage.get("dimensions", [])[:6]
        cov_mult = 0.82 if tier == "essential" else (1.12 if tier == "optimal" else 1.0)
        nutrition_coverage = [
            {
                "goal_id": d["goal_id"],
                "title": priority_label(d["goal_id"], d.get("title")),
                "coverage_percent": min(100, js_round(d["coverage_percent"] * cov_mult)),
            }
            for d in dims
        ]
        coverage_score = (
            js_round(sum(n["coverage_percent"] for n in nutrition_coverage) / max(len(nutrition_coverage), 1))
            if nutrition_coverage
            else meta["coverage_floor"]
        )
        coverage_score = min(100, max(meta["coverage_floor"], coverage_score))

        includes = _includes_summary_from_items(items, tier) + list(meta["includes_extra"])

        activities_included: list[str] = []
        for h in health_insights[:2]:
            conds = h.get("supporting_conditions") or []
            cond0 = conds[0] if conds else ""
            acts = activities_for_condition(repo, str(cond0 or ""))
            if acts:
                activities_included.append(
                    acts[0].get("activity_name") or acts[0].get("activity") or ""
                )

        packages.append({
            "tier": tier,
            "title": meta["title"],
            "recommended": meta["recommended"],
            "best_for": meta["best_for"],
            "tagline": meta["description"].split(".")[0] + ".",
            "description": meta["description"],
            "coverage_score": coverage_score,
            "monthly_cost": monthly_cost,
            "yearly_cost": yearly_cost,
            "includes_summary": includes,
            "products_included": products_included,
            "nutrition_coverage": nutrition_coverage,
            "overview": (
                f"Our biological model estimates that {pet_name} would benefit most from long-term "
                f"{top_goals.lower() or 'preventative wellness'} support. This plan provides "
                f"approximately {coverage_score}% nutritional coverage across those priority areas"
                f"{' while remaining budget-friendly' if tier == 'essential' else ''}"
                f"{' while remaining cost efficient' if tier == 'balanced' else ''}."
            ),
            "activities_included": [a for a in activities_included if a],
            "why_fits": (
                # JS: `Designed for ${weightKg}kg` — keep raw number (2.5 not Math.round)
                f"Designed for {profile.weight_kg if float(profile.weight_kg) != int(profile.weight_kg) else int(profile.weight_kg)}kg biology with focus on "
                f"{top_goals or 'core preventative wellness'}."
            ),
            "subscribe_cta": f"Subscribe to {meta['title'].replace(' Care', '')} Care",
        })

    return packages


def build_package_details(
    packages: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """JS: Object.fromEntries(wellnessPackages.map(p => [p.tier, p]))."""
    return {pkg["tier"]: pkg for pkg in packages}

def _js_dose_str(value: Any) -> str:
    """Match JS template `${number}` — integers without trailing .0."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value if value is not None else "")
    if num == int(num):
        return str(int(num))
    return str(num)


def build_nutritional_targets(ingredients: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Port of wellnessEngine.buildNutritionalTargets(ingredients, healthInsights)."""
    targets = []
    for ing in ingredients:
        supports_goals = []
        for c in ing.get("for_conditions") or []:
            goal_id = goal_for_condition(str(c))
            supports_goals.append((WELLNESS_GOALS.get(goal_id) or {}).get("title") or "General Wellness")
        unit = ing.get("unit") or ""
        targets.append({
            "ingredient": ing.get("ingredient_name"),
            "ingredient_key": ing.get("ingredient_key"),
            "daily_target": f"{_js_dose_str(ing.get('daily_dose'))}{unit}",
            "monthly_target": f"{_js_dose_str(ing.get('monthly_dose'))}{unit}",
            "supports_goals": supports_goals,
            "evidence_quote": ing.get("evidence_quote"),
            "source_name": ing.get("source_name"),
            "source_url": ing.get("source_url"),
        })
    return targets


def build_activity_recommendations(
    resolved_breeds: list[dict[str, Any]],
    meta: dict[str, Any],
    pet_name: str,
) -> dict[str, Any]:
    """Port of wellnessEngine.buildActivityPlan."""
    energy = [b.get("energy_level") or b.get("energy") for b in resolved_breeds]
    is_high_drive = any(str(e) in ("Extreme", "High") for e in energy if e)
    is_low = any(str(e) == "Low" for e in energy if e)
    has_working = any(
        b.get("function_group") in ("Working", "Sporting", "Herding")
        for b in resolved_breeds
    )

    if is_high_drive:
        daily_minutes = 75
    elif is_low:
        daily_minutes = 45
    else:
        daily_minutes = 60

    age_stage = meta.get("ageStage") or meta.get("age_stage")
    if age_stage == "senior":
        daily_minutes = js_round(daily_minutes * 0.75)
    elif age_stage == "puppy":
        daily_minutes = js_round(daily_minutes * 0.85)

    physical = (
        ["Walking", "Swimming", "Fetch", "Puzzle Toys"]
        if is_high_drive
        else ["Walking", "Gentle play", "Sniff walks"]
    )
    mental = ["Puzzle feeders", "Training", "Scent games", "Mental enrichment"]

    if has_working:
        lifestyle_tip = (
            f"Because {pet_name} has working-breed ancestry, regular exercise and "
            f"mental stimulation may support healthy weight and positive behaviour."
        )
    else:
        lifestyle_tip = (
            f"Regular activity tailored to {pet_name}'s energy level supports long-term "
            f"mobility and overall wellness."
        )

    return {
        "recommended_daily_exercise": f"{daily_minutes}–{daily_minutes + 15} minutes",
        "suggested_physical": physical,
        "suggested_mental": mental,
        "lifestyle_tip": lifestyle_tip,
        "condition_specific": [],
        "future_personalization_note": (
            "Once walking history and activity logs are available, recommendations will automatically adapt."
        ),
    }


def build_research_section(
    biology: dict[str, Any],
    health_insights: list[dict[str, Any]],
    scientific_evidence: list[Any] | None,
    nutritional_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    """Port of wellnessEngine.buildResearchSection."""
    return {
        "title": "Why did we recommend these products?",
        "biological_traits": biology.get("trait_summary", []),
        "health_priorities": [
            {
                "title": priority_label(h["goal_id"], h["title"]),
                "biological_estimate_percent": h["estimated_biological_risk_percent"],
                "observed_prevalence_percent": h["observed_breed_prevalence_percent"],
                "supporting_traits": h.get("supporting_traits", []),
            }
            for h in health_insights[:6]
        ],
        "ingredient_evidence": [
            {
                "ingredient": t.get("ingredient"),
                "supports": t.get("supports_goals"),
                "quote": t.get("evidence_quote"),
                "source_name": t.get("source_name"),
                "source_url": t.get("source_url"),
            }
            for t in (nutritional_targets or [])[:6]
        ],
        "literature": (scientific_evidence or [])[:8],
    }


def _parse_num(value: Any) -> float:
    m = re.search(r"[-+]?\d*\.?\d+", str(value if value is not None else ""))
    return float(m.group(0)) if m else 0.0


def _infer_climate_compatibility(
    resolved_breeds: list[dict[str, Any]],
    current_climate: str,
) -> list[dict[str, Any]]:
    climate = (current_climate or "").lower()
    rows = []
    for b in resolved_breeds:
        trait_climate = str(b.get("climate") or "").lower()
        score = 0.8
        if not climate:
            score = 0.75
        elif "cold" in trait_climate and "cold" in climate:
            score = 0.95
        elif "heat" in trait_climate and ("hot" in climate or "heat" in climate):
            score = 0.95
        elif "temperate" in trait_climate and ("temperate" in climate or "mild" in climate):
            score = 0.9
        elif "heat" in trait_climate and "cold" in climate:
            score = 0.62
        elif "cold" in trait_climate and ("hot" in climate or "heat" in climate):
            score = 0.6
        rows.append({
            "breed": b.get("breed_name") or b.get("breed"),
            "trait_climate": b.get("climate"),
            "current_climate": current_climate or "unspecified",
            "compatibility_score": js_round(score * 1000) / 1000,
        })
    return rows


def _js_number(value: Any) -> Any:
    """Coerce CSV/pandas values like JS parseInt/parseFloat output."""
    if value is None or value == "":
        return value
    try:
        f = float(value)
    except (TypeError, ValueError):
        return value
    if f != f:  # NaN
        return None
    if float(f).is_integer():
        return int(f)
    return f


def _df_rows_matching_condition(df: pd.DataFrame, condition_name: str) -> list[dict[str, Any]]:
    """Filter a condition-keyed CSV frame using JS conditionCandidates / conditionMatches."""
    if df is None or df.empty or not condition_name:
        return []
    candidates = condition_candidates(condition_name)
    rows: list[dict[str, Any]] = []
    has_key = "condition_key" in df.columns
    name_col = (
        "condition" if "condition" in df.columns
        else ("condition_name" if "condition_name" in df.columns else None)
    )
    if not name_col and not has_key:
        return []
    for _, row in df.iterrows():
        rec = row.to_dict()
        rk = rec.get("condition_key") if has_key else None
        rn = rec.get(name_col) if name_col else None
        if condition_matches(rk, rn, candidates):
            rows.append(rec)
    return rows


def build_preventative_nutrition_system(
    *,
    profile: DogProfileInput,
    biology: dict[str, Any],
    risks: list[dict[str, Any]],
    nutritional_targets: list[dict[str, Any]],
    health_insights: list[dict[str, Any]],
    repo: DataRepository,
) -> dict[str, Any]:
    """Port of src/engine/index.js buildPreventativeSystemOutput."""
    del health_insights
    name = profile.name
    resolved_breeds = biology.get("resolved_breeds") or []
    current_climate = profile.current_environment
    age_years = float(profile.age_years)
    age_stage = "puppy" if age_years < 1 else ("senior" if age_years >= 7 else "adult")
    sex = profile.sex or profile.gender

    priorities = [
        {
            "condition_name": r.get("condition_name"),
            "condition_key": r.get("condition_key"),
            "management_consideration": True,
            "prevalence_percent": (
                r.get("breed_prevalence_percent")
                if r.get("breed_prevalence_percent") is not None
                else r.get("risk_percent")
            ),
            "confidence_percent": r.get("confidence_percent"),
            "source_name": (r.get("source") or {}).get("source_name") if r.get("source") else None,
            "source_quote": (r.get("source") or {}).get("source_quote") if r.get("source") else None,
            "source_url": (r.get("source") or {}).get("source_url") if r.get("source") else None,
        }
        for r in risks[:8]
    ]

    disease_risk_modifiers = []
    for r in risks[:10]:
        explanation = r.get("trait_explanation") or {}
        evidence = explanation.get("trait_evidence") or []
        disease_risk_modifiers.append({
            "condition_name": r.get("condition_name"),
            "condition_key": r.get("condition_key"),
            "risk_percent": r.get("risk_percent"),
            "trait_risk_percent": r.get("trait_risk_percent"),
            "prevalence_percent": r.get("breed_prevalence_percent"),
            "interaction_factor": explanation.get("interaction_factor") or 1,
            "benefit_factor": explanation.get("benefit_factor") or 1,
            "mixed_breed_factor": r.get("mixed_breed_factor") or 1,
            "supporting_sources": [
                {
                    "trait_category": e.get("trait_category"),
                    "trait_value": e.get("trait_value"),
                    "prevalence": e.get("prevalence"),
                    "source_name": e.get("source_name"),
                    "source_quote": e.get("source_quote"),
                    "source_url": e.get("source_url"),
                }
                for e in evidence
            ],
        })

    activities_df = repo.condition_activities()
    lifestyle_requirements: list[dict[str, Any]] = []
    for p in priorities:
        cond = p["condition_name"]
        for a in _df_rows_matching_condition(activities_df, str(cond or "")):
            lifestyle_requirements.append({
                "condition_name": cond,
                "activity_name": a.get("activity_name") or a.get("activity"),
                "frequency": a.get("frequency"),
                "duration_minutes": _js_number(a.get("duration_minutes")),
                "source_name": a.get("source_name"),
                "source_quote": a.get("source_quote"),
                "source_url": a.get("source_url"),
                "requirement_type": "lifestyle_requirement",
            })

    nutrient_df = repo.nutrient_priorities()
    condition_ing = repo.condition_ingredients()
    mech_df = repo.ingredient_mechanisms()
    food_df = repo.natural_food_sources()

    def _mechanisms(nutrient_name: str) -> list[dict[str, Any]]:
        """Mirror queries.js getIngredientMechanisms (nutrient/ingredient key/name)."""
        if mech_df.empty or not nutrient_name:
            return []
        key = ingredient_key(nutrient_name)
        out: list[dict[str, Any]] = []
        for _, m in mech_df.iterrows():
            nname = str(m.get("nutrient_name") or "")
            iname = str(m.get("ingredient_name") or "")
            nkey = ingredient_key(nname) if nname else ""
            ikey = ingredient_key(iname) if iname else ""
            if key in (nkey, ikey) or nname.lower() == nutrient_name.lower() or iname.lower() == nutrient_name.lower():
                out.append({
                    "ingredient_name": m.get("ingredient_name"),
                    "amount_per_serving": _js_number(m.get("amount_per_serving")),
                    "unit": m.get("unit"),
                    "mechanism_summary": m.get("mechanism_summary"),
                    "source_product_id": m.get("source_product_id"),
                })
            if len(out) >= 4:
                break
        return out

    nutrition_priorities: list[dict[str, Any]] = []
    for p in priorities:
        cond = p["condition_name"]
        nutrient_rows = _df_rows_matching_condition(nutrient_df, str(cond or ""))
        if nutrient_rows:
            nutrient_rows = sorted(
                nutrient_rows,
                key=lambda n: int(_js_number(n.get("priority_rank")) or 999),
            )
            for n in nutrient_rows:
                nname = n.get("nutrient_name") or n.get("ingredient_name")
                nutrition_priorities.append({
                    "condition_name": cond,
                    "nutrient_name": nname,
                    "target_dose": _js_number(n.get("target_dose")),
                    "target_unit": n.get("target_unit"),
                    "priority_rank": int(_js_number(n.get("priority_rank")) or 999),
                    "evidence_level": n.get("evidence_level"),
                    "source_name": n.get("source_name"),
                    "source_quote": n.get("source_quote"),
                    "source_url": n.get("source_url"),
                    "mechanisms": _mechanisms(str(nname or "")),
                })
            continue

        condition_rows = _df_rows_matching_condition(condition_ing, str(cond or ""))
        if condition_rows:
            # JS getConditionIngredients preserves store/CSV encounter order (no sort).
            for t in condition_rows:
                nname = t.get("ingredient_name")
                nutrition_priorities.append({
                    "condition_name": cond,
                    "nutrient_name": nname,
                    "target_dose": _js_number(t.get("recommended_daily_dose") or t.get("target_dose")),
                    "target_unit": t.get("dose_unit") or t.get("target_unit"),
                    "priority_rank": int(_js_number(t.get("priority_rank")) or 999),
                    "evidence_level": "condition_specific",
                    "source_name": t.get("source_name"),
                    "source_quote": t.get("source_quote"),
                    "source_url": t.get("source_url"),
                    "mechanisms": _mechanisms(str(nname or "")),
                })
            continue

        for t in nutritional_targets:
            goals = t.get("supports_goals") or t.get("for_conditions") or []
            if any(str(cond).lower() in str(g).lower() for g in goals):
                nname = t.get("ingredient")
                nutrition_priorities.append({
                    "condition_name": cond,
                    "nutrient_name": nname,
                    "target_dose": t.get("daily_target"),
                    "target_unit": "",
                    "priority_rank": 999,
                    "evidence_level": None,
                    "source_name": t.get("source_name"),
                    "source_quote": t.get("evidence_quote"),
                    "source_url": t.get("source_url"),
                    "mechanisms": _mechanisms(str(nname or "")),
                })

    whole_food_contracts: list[dict[str, Any]] = []
    for idx, p in enumerate(priorities):
        nutrient = next(
            (n for n in nutrition_priorities if n["condition_name"] == p["condition_name"]),
            None,
        )
        activity = next(
            (a for a in lifestyle_requirements if a["condition_name"] == p["condition_name"]),
            None,
        )
        if not nutrient:
            continue
        target_dose_numeric = _parse_num(nutrient.get("target_dose"))
        natural_foods = []
        if not food_df.empty:
            nname = str(nutrient.get("nutrient_name") or "")
            nkey = ingredient_key(nname)
            for _, f in food_df.iterrows():
                fname = str(f.get("ingredient_name") or f.get("nutrient_name") or "")
                fkey = ingredient_key(fname) if fname else str(f.get("ingredient_key") or "")
                if fkey != nkey and fname.lower() != nname.lower():
                    continue
                amount = float(pd.to_numeric(f.get("amount_per_100g"), errors="coerce") or 0)
                if amount <= 0:
                    continue
                grams = js_round((target_dose_numeric / amount) * 100) if target_dose_numeric > 0 else 0
                natural_foods.append({
                    "food_item": f.get("food_source") or f.get("food_item"),
                    "estimated_yield_per_100g": f"{_js_number(amount)} {f.get('unit')}",
                    "calculated_daily_addition": f"{grams}g",
                    "clinical_note": f.get("bioavailability_notes"),
                })

        dose = nutrient.get("target_dose")
        unit = nutrient.get("target_unit")
        required = (
            f"{dose} {unit}".strip()
            if dose is not None and dose != "" and unit
            else str(dose if dose is not None else "")
        )
        whole_food_contracts.append({
            "condition": p["condition_name"],
            "priority_rank": idx + 1,
            "targeted_intervention": {
                "active_ingredient": nutrient.get("nutrient_name"),
                "required_dosage": required,
                "scientific_validation": {
                    "study": nutrient.get("source_name") or "Clinical evidence dataset",
                    "verbatim_finding": (
                        nutrient.get("source_quote")
                        or "Evidence-mapped nutrient support for condition management."
                    ),
                    "url": nutrient.get("source_url") or None,
                },
                "natural_food_alternatives": natural_foods,
                "lifestyle_requirement": (
                    {
                        "activity_name": activity.get("activity_name"),
                        "frequency": activity.get("frequency"),
                        "duration_minutes": activity.get("duration_minutes"),
                        "source_name": activity.get("source_name"),
                        "source_quote": activity.get("source_quote"),
                        "source_url": activity.get("source_url"),
                    }
                    if activity
                    else None
                ),
            },
        })

    primary = priorities[0] if priorities else None
    first_activity = next(
        (a for a in lifestyle_requirements if primary and a["condition_name"] == primary["condition_name"]),
        None,
    )
    first_nutrition = next(
        (n for n in nutrition_priorities if primary and n["condition_name"] == primary["condition_name"]),
        None,
    )
    first_breed = resolved_breeds[0] if resolved_breeds else {}
    first_trait = (
        first_breed.get("coat_type")
        or first_breed.get("body_type")
        or first_breed.get("size")
        or first_breed.get("size_class")
        or "biological trait"
    )
    sample_population = (
        ((risks[0].get("source") or {}).get("breed") if risks else None)
        or "breed-specific observational cohorts"
    )
    prevalence = (
        primary.get("prevalence_percent")
        if primary and primary.get("prevalence_percent") is not None
        else (risks[0].get("risk_percent") if risks else 0)
    )
    narrative = (
        f"{name} inherited a {first_trait} from their "
        f"{first_breed.get('breed') or first_breed.get('breed_name') or 'mixed-breed'} ancestry. "
        f"While advantageous for environmental adaptation and physiological resilience, in a "
        f"{current_climate or 'current'} environment, this trait presents specific management "
        f"considerations, such as a {prevalence}% incidence of "
        f"{(primary or {}).get('condition_name') or 'priority condition'} observed in "
        f"{sample_population} "
        f"(Source: {(primary or {}).get('source_name') or 'Veterinary comparative epidemiology dataset'}). "
        f"To proactively manage this, lifestyle modifications including "
        f"{(first_activity or {}).get('activity_name') or 'structured preventative exercise'} "
        f"are recommended. Furthermore, based on veterinary physiology, targeted nutritional "
        f"intervention with {(first_nutrition or {}).get('nutrient_name') or 'targeted nutrient support'} "
        f"is required at a dosage of {(first_nutrition or {}).get('target_dose') or 'clinically mapped dose'} "
        f"to support long-term health."
    )

    breed_names = [b.get("breed") or b.get("breed_name") for b in resolved_breeds]
    dog_profile = {
        "pet_name": name,
        "breeds": breed_names,
        "birthday": profile.birthday,
        "gender": profile.gender or sex,
        "sex": sex,
        "bcs": profile.bcs,
        "activity_level": profile.activity_level,
        "current_environment": current_climate,
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "age_years": age_years,
        "age_stage": age_stage,
    }

    return {
        "pipeline_flow": [
            "Dog Profile",
            "Biological Traits",
            "Management Considerations",
            "Lifestyle Interventions",
            "Nutritional Synthesis",
            "Whole-Food Feeding Equivalents",
        ],
        "dog_profile": dog_profile,
        "biological_traits": [
            {
                "breed": b.get("breed") or b.get("breed_name"),
                "size": b.get("size") or b.get("size_class"),
                "body_type": b.get("body_type"),
                "coat_type": b.get("coat_type"),
                "energy": b.get("energy") or b.get("energy_level"),
                "climate": b.get("climate"),
                "skull_type": b.get("skull_type"),
                "function_group": b.get("function_group"),
                "weakness_group": b.get("weakness_group"),
                "lifespan": b.get("lifespan") or b.get("lifespan_class"),
            }
            for b in resolved_breeds
        ],
        "management_considerations": priorities,
        "lifestyle_interventions": lifestyle_requirements,
        "nutritional_synthesis": nutrition_priorities,
        "whole_food_feeding_equivalents": whole_food_contracts,
        "trait_analysis": priorities,
        "preventative_health_priorities": priorities,
        "standardized_outputs": {
            "disease_risk_modifiers": disease_risk_modifiers,
            "environmental_compatibility_matrix": _infer_climate_compatibility(
                resolved_breeds, current_climate
            ),
            "lifestyle_requirements": lifestyle_requirements,
            "nutrition_priorities": nutrition_priorities,
        },
        "output_contracts": whole_food_contracts,
        "narrative_synthesis": narrative,
    }


def assemble_frontend_response(
    profile: DogProfileInput,
    biology: dict[str, Any],
    epidemiology: dict[str, Any],
    nutrition: dict[str, Any],
    reports: list[WellnessReportPayload],
    feeding_plan: dict[str, Any],
    management: dict[str, Any],
    pipeline_trace: list[dict[str, Any]],
    repo: DataRepository,
    health_risk: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Top-level envelope matching FRONTEND_LAYOUT_SPEC.md / JS analyze()."""
    pet_name = profile.name
    meta = (health_risk or {}).get("meta") or {}
    profile_block = build_profile_block(profile, meta)
    biology_block = build_biology_block(biology, profile)

    risks = (health_risk or {}).get("risks") or []
    health_insights = build_health_insights(risks, pet_name)
    product_recommendations = build_product_recommendations(reports, repo, profile)

    # rawIngredients from mapIngredients (ingredientEngine.js)
    raw_ingredients = map_ingredients(risks, profile.weight_kg, repo)

    wellness_coverage = build_wellness_coverage(
        health_insights, product_recommendations, raw_ingredients
    )
    wellness_summary = build_wellness_summary(pet_name, biology_block, health_insights, wellness_coverage)
    wellness_packages = build_wellness_packages(
        product_recommendations, health_insights, profile, wellness_coverage, repo
    )
    wellness_packages = [
        enrich_package_for_detail(
            pkg,
            raw_ingredients,
            product_recommendations,
            pet_name,
            profile.weight_kg,
            repo,
        )
        for pkg in wellness_packages
    ]
    package_details = build_package_details(wellness_packages)
    nutritional_targets = build_nutritional_targets(raw_ingredients)
    activity_recommendations = build_activity_recommendations(
        biology.get("resolved_breeds") or [],
        meta,
        pet_name,
    )
    scientific_evidence = collect_evidence(risks, raw_ingredients)
    research_section = build_research_section(
        biology_block, health_insights, scientific_evidence, nutritional_targets
    )
    calculation_trace = build_calculation_trace(
        profile=profile_block,
        biology=biology_block,
        health_insights=health_insights,
        nutritional_targets=nutritional_targets,
        product_recommendations=product_recommendations,
        repo=repo,
    )

    product_analyses: dict[str, Any] = {}
    for pkg in wellness_packages:
        for card in pkg.get("product_cards") or []:
            name = card.get("product_name") or card.get("name")
            pid = card.get("product_id") or name
            if not name:
                continue
            # Later packages overwrite (JS overwrites FF002_BEEF with optimal tier last).
            product_analyses[pid] = build_product_analysis(
                name, pkg, raw_ingredients, product_recommendations, pet_name, profile.weight_kg, repo
            )

    preventative = build_preventative_nutrition_system(
        profile=profile,
        biology=biology,
        risks=risks,
        nutritional_targets=nutritional_targets,
        health_insights=health_insights,
        repo=repo,
    )

    groomer_fields = [
        {"key": "eyes", "label": "Eyes", "match": ["eyes", "eye_discharge", "tear_stains"]},
        {"key": "ears", "label": "Ears", "match": ["ears", "ear_redness", "odor"]},
        {"key": "skin", "label": "Skin", "match": ["skin", "dry_skin", "scratching", "itching"]},
        {"key": "teeth", "label": "Teeth", "match": ["teeth", "bad_breath"]},
        {"key": "limps", "label": "Limps", "match": ["limps", "limping"]},
        {"key": "shedding", "label": "Shedding", "match": ["shedding"]},
        {"key": "anal_gland", "label": "Anal Gland", "match": ["anal_gland"]},
    ]
    observed = {re.sub(r"\s+", "_", c.lower()) for c in profile.observed_conditions}
    groomer = [
        {
            "key": f["key"],
            "label": f["label"],
            "match": f["match"],
            "status": "flagged" if any(m in observed for m in f["match"]) else "clear",
            "live": any(m in observed for m in f["match"]),
        }
        for f in groomer_fields
    ]

    legacy_risks = []
    for h in health_insights:
        row: dict[str, Any] = {
            "condition": h["title"],
            "condition_key": h["goal_id"],
            "risk_percent": h["priority_score"],
            "estimated_risk_percent": h["estimated_biological_risk_percent"],
            "trait_risk_percent": h["estimated_biological_risk_percent"],
            "breed_prevalence_percent": h["observed_breed_prevalence_percent"],
            "confidence_percent": h["confidence_percent"],
            "evidence_count": h.get("evidence_count", 0),
            "supporting_traits": [{"category": "trait", "value": t} for t in h.get("supporting_traits", [])],
            "logic": "wellness_insight",
            "groomer_boosted": h.get("groomer_priority"),
            "why": h.get("explanation"),
        }
        # JS: h.evidence_sources[0]?.source_name — undefined omitted from JSON
        src0 = (h.get("evidence_sources") or [None])[0] or {}
        if src0.get("source_name") is not None:
            row["source_name"] = src0.get("source_name")
        if src0.get("source_quote") is not None:
            row["source_quote"] = src0.get("source_quote")
        if src0.get("source_url") is not None:
            row["source_url"] = src0.get("source_url")
        legacy_risks.append(row)

    # JS pipelineEngine.buildPipelineTrace — not internal stage trace entries
    pipeline_trace = build_pipeline_trace(
        biology=biology,
        risks=risks,
        ingredients=raw_ingredients,
        raw_products=[],
        repo=repo,
    )

    monthly_plan = build_monthly_plan(
        [],
        profile.weight_kg,
        _age_stage(profile.age_years),
        repo,
    )
    yearly_plan = build_yearly_plan(monthly_plan, repo)

    return {
        "engine": "PPIE",
        "version": ENGINE_VERSION,
        "pipeline_flow": PIPELINE_STAGES,
        "variable_map": VARIABLE_MAP,
        "profile": profile_block,
        "biology": biology_block,
        "wellness_summary": wellness_summary,
        "wellness_coverage": wellness_coverage,
        "healthInsights": health_insights,
        "nutritionalTargets": nutritional_targets,
        "ingredientRequirements": nutritional_targets,
        "productRecommendations": product_recommendations,
        "wellnessPackages": wellness_packages,
        "packageDetails": package_details,
        "productAnalyses": product_analyses,
        "activityRecommendations": activity_recommendations,
        "scientificEvidence": scientific_evidence,
        "researchSection": research_section,
        "calculationTrace": calculation_trace,
        "groomer": groomer,
        "preventativeNutritionSystem": preventative,
        "monthly_plan": monthly_plan,
        "yearly_plan": yearly_plan,
        "wellness_score": wellness_coverage["overall_score"],
        "pipeline_trace": pipeline_trace,
        # Legacy JS aliases
        "pet": profile_block,
        "risks": legacy_risks,
        "ingredients": [
            {
                "ingredient": t.get("ingredient"),
                "ingredient_key": t.get("ingredient_key"),
                "daily_dose": t.get("daily_target"),
                "monthly_dose": t.get("monthly_target"),
                "for_conditions": t.get("supports_goals") or t.get("for_conditions") or [],
                "evidence_quote": t.get("evidence_quote"),
                "source_name": t.get("source_name"),
                "source_url": t.get("source_url"),
            }
            for t in nutritional_targets
        ],
        "products": product_recommendations,
        "activities": activity_recommendations.get("condition_specific", []),
        "evidence": scientific_evidence,
    }
