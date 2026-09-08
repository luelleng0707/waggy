"""Combinatorial constraint search used by PACKAGE_OPTIMIZER_V2_1."""

from __future__ import annotations

import hashlib
import itertools
from collections import Counter
from typing import Any, Iterable

from app.agent.utils import js_round
from app.data.demo_catalog import demo_mode_enabled
from app.data.scientific_care import PATHWAY_LABELS, resolve_care_model
from app.data.demo_scientific_dataset import (
    NUTRIENT_IDS,
    aggregate_contributions,
    build_demo_requirement_profile,
    demo_product_nutrient,
    product_daily_contribution,
)
from app.data.scientific_requirements import SOURCE as REQUIREMENT_SOURCE

EXHAUSTIVE_MAX_N = 14
BOUNDED_MAX_SIZE = 6
BOUNDED_ADJUNCT_CAP = 12
PACKAGE_DISPLAY_LIMIT = 20
OPTIONS_PER_TIER = PACKAGE_DISPLAY_LIMIT
MAX_BUNDLE_OPTIONS = 50
NEAR_MAXIMUM_RATIO = 0.80
LOW_MINIMUM_RATIO = 1.10

SCORE_WEIGHTS = {
    "essential": {
        "price": 0.55,
        "simplicity": 0.25,
        "nutrient_balance": 0.15,
        "redundancy_penalty": 0.05,
        "care": 0.0,
    },
    "balanced": {
        "care": 0.35,
        "nutrient_balance": 0.25,
        "budget_fit": 0.20,
        "simplicity": 0.10,
        "nutrition_adequacy": 0.10,
    },
    "optimal": {
        "nutrient_adequacy": 0.20,
        "nutrient_balance": 0.25,
        "care": 0.20,
        "complementarity": 0.10,
        "simplicity": 0.10,
        "excess_avoidance": 0.10,
        "budget_fit": 0.05,
    },
}

RANKING_RULES = {
    "essential": (
        "Hard nutritional validity already applied. "
        "Then lowest monthly cost, then fewest products, then overall_score, then bundle_id. "
        "Breed-care score is not used. Budget is a hard ceiling when supplied."
    ),
    "balanced": (
        "Hard nutritional validity already applied. Budget is a hard ceiling when supplied. "
        "Then highest care_coverage, then highest nutrition_balance, then lowest monthly cost, "
        "then fewest products, then bundle_id."
    ),
    "optimal": (
        "Hard nutritional validity already applied. No customer budget ceiling. "
        "Then highest overall_score, then nutrition_balance, then care_coverage, "
        "then fewest products, then lowest monthly cost (informational), then bundle_id."
    ),
}

TIER_SEMANTICS = {
    "essential": {
        "purpose": "Minimum viable nutritional care.",
        "uses_breed_care_for_eligibility": False,
        "uses_breed_care_for_ranking": False,
        "budget_is_hard_ceiling": True,
    },
    "balanced": {
        "purpose": "Baseline nutritional adequacy plus breed-specific preventive considerations.",
        "uses_breed_care_for_eligibility": True,
        "uses_breed_care_for_ranking": True,
        "budget_is_hard_ceiling": True,
        "eligibility_rule": "nutrient_valid AND (no care priorities OR care_coverage_score > 0)",
    },
    "optimal": {
        "purpose": "Best-scoring valid care package without a customer budget ceiling.",
        "uses_breed_care_for_eligibility": False,
        "uses_breed_care_for_ranking": True,
        "budget_is_hard_ceiling": False,
    },
}

NOT_SPECIFIED_COPY = "Not specified in modeled source"


def _status_label(ui_status: str, *, maximum_specified: bool) -> str:
    if ui_status == "FAIL_MINIMUM":
        return "BELOW MINIMUM"
    if ui_status == "FAIL_MAXIMUM":
        return "ABOVE MAXIMUM"
    if ui_status == "NOT_MODELED":
        return "NOT MODELED"
    if maximum_specified and ui_status in {"PASS", "NEAR_MAXIMUM"}:
        return "Within range"
    if ui_status in {"PASS", "LOW", "NO_MODELED_MAXIMUM"}:
        return "Meets minimum"
    return str(ui_status or "NOT MODELED")


def _bundle_id(product_ids: Iterable[str]) -> str:
    key = ",".join(sorted(product_ids))
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:10]
    return f"B-{digest}"


def _product_pathways(product: dict[str, Any]) -> list[str]:
    demo = demo_product_nutrient(str(product.get("product_id") or ""))
    if demo:
        return list(demo.get("pathways") or [])
    paths: list[str] = []
    for fn in product.get("functions") or []:
        text = str(fn.get("function") or "").lower()
        if "joint" in text:
            paths.append("joint")
        if "skin" in text or "coat" in text:
            paths.append("skin")
        if "dental" in text or "oral" in text:
            paths.append("dental")
        if "digest" in text or "gut" in text:
            paths.append("digestive")
        if "staple" in text or "nutrition" in text:
            paths.append("nutrition")
    if product.get("role") == "staple":
        paths.append("staple")
    return list(dict.fromkeys(paths))


def _is_staple(product: dict[str, Any]) -> bool:
    demo = demo_product_nutrient(str(product.get("product_id") or ""))
    if demo:
        return demo.get("role") == "staple"
    return product.get("role") == "staple"


def _aggregate_nutrients(products: list[dict[str, Any]], weight_kg: float) -> dict[str, Any]:
    synthetic = demo_mode_enabled()
    if not synthetic:
        missing = [str(p.get("product_id") or "") for p in products]
        return {
            "basis": None,
            "synthetic_demo_data": False,
            "staple_daily_dm_g": 0,
            "conversion": {"as_fed_percent_not_added": True, "reason": "No dry-matter product profiles."},
            "per_product": [
                {"product_id": pid, "status": "INSUFFICIENT_DATA", "reason": "Product DM nutrient data unavailable."}
                for pid in missing
            ],
            "missing_product_nutrient_data": missing,
            "daily_amounts": {},
            "densities": {},
        }
    contribs = [product_daily_contribution(str(p.get("product_id") or ""), weight_kg) for p in products]
    totals = aggregate_contributions(contribs)
    totals["missing_product_nutrient_data"] = [
        c["product_id"] for c in contribs if c.get("status") == "INSUFFICIENT_DATA"
    ]
    return totals


def _contributors(totals: dict[str, Any], nutrient_id: str) -> list[dict[str, Any]]:
    rows = []
    for contrib in totals.get("per_product") or []:
        amount = (contrib.get("daily_amounts") or {}).get(nutrient_id) or 0
        if amount:
            rows.append(
                {
                    "product_id": contrib.get("product_id"),
                    "daily_amount": round(float(amount), 6),
                    "daily_dm_g": contrib.get("daily_dm_g"),
                }
            )
    return rows


def _evaluate_constraints(
    totals: dict[str, Any],
    requirements: dict[str, Any],
    *,
    star_nutrients: list[str],
    apply_stars: bool,
) -> dict[str, Any]:
    failed_min: list[dict[str, Any]] = []
    exceeded_max: list[dict[str, Any]] = []
    missing_data: list[str] = []
    rows: list[dict[str, Any]] = []
    nutrients = (requirements or {}).get("nutrients") or {}
    densities = totals.get("densities") or {}
    daily_amounts = totals.get("daily_amounts") or {}
    dm_g = float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0)
    dm_kg = dm_g / 1000.0 if dm_g else 0.0
    min_pass = 0
    min_total = 0
    max_pass = 0
    max_total = 0
    for nid, spec in nutrients.items():
        actual = densities.get(nid)
        if actual is None:
            actual = totals.get(nid)
        minimum = spec.get("minimum")
        maximum = spec.get("maximum")
        kind = spec.get("kind") or ""
        status = "PASS"
        if actual is None:
            if minimum is not None or maximum is not None:
                status = "NOT_MODELED"
                missing_data.append(nid)
        else:
            if minimum is not None:
                min_total += 1
                if float(actual) + 1e-9 < float(minimum):
                    status = "DEFICIENT"
                    failed_min.append(
                        {
                            "nutrient": nid,
                            "required": minimum,
                            "actual": actual,
                            "unit": spec.get("unit"),
                            "deficit": round(float(minimum) - float(actual), 6),
                            "products_contributing": _contributors(totals, nid),
                        }
                    )
                else:
                    min_pass += 1
            if status == "PASS" and maximum is not None:
                max_total += 1
                if float(actual) - 1e-9 > float(maximum):
                    status = "EXCESS"
                    exceeded_max.append(
                        {
                            "nutrient": nid,
                            "maximum": maximum,
                            "actual": actual,
                            "unit": spec.get("unit"),
                            "margin": round(float(actual) - float(maximum), 6),
                            "products_contributing": _contributors(totals, nid),
                        }
                    )
                else:
                    max_pass += 1
            elif maximum is not None and status == "PASS":
                max_total += 1
                max_pass += 1
        min_margin = None
        max_margin = None
        pct_min = None
        pct_max = None
        daily_eq = daily_amounts.get(nid)
        daily_min = None
        daily_max = None
        if actual is not None and minimum is not None:
            min_margin = round(float(actual) - float(minimum), 6)
            pct_min = round(100.0 * float(actual) / float(minimum), 2) if minimum else None
        if actual is not None and maximum is not None:
            max_margin = round(float(maximum) - float(actual), 6)
            pct_max = round(100.0 * float(actual) / float(maximum), 2) if maximum else None
        if dm_g and minimum is not None:
            if kind == "pct_dm":
                daily_min = round(float(minimum) / 100.0 * dm_g, 6)
            elif kind in {"mg_kg_dm", "iu_kg_dm"} and dm_kg:
                daily_min = round(float(minimum) * dm_kg, 6)
        if dm_g and maximum is not None:
            if kind == "pct_dm":
                daily_max = round(float(maximum) / 100.0 * dm_g, 6)
            elif kind in {"mg_kg_dm", "iu_kg_dm"} and dm_kg:
                daily_max = round(float(maximum) * dm_kg, 6)
        if status == "DEFICIENT":
            ui_status = "FAIL_MINIMUM"
        elif status == "EXCESS":
            ui_status = "FAIL_MAXIMUM"
        elif status == "NOT_MODELED":
            ui_status = "NOT_MODELED"
        elif status == "PASS" and maximum is not None and pct_max is not None and pct_max >= NEAR_MAXIMUM_RATIO * 100:
            ui_status = "NEAR_MAXIMUM"
        elif status == "PASS" and pct_min is not None and pct_min < LOW_MINIMUM_RATIO * 100:
            ui_status = "LOW"
        elif status == "PASS" and maximum is None:
            ui_status = "NO_MODELED_MAXIMUM"
        else:
            ui_status = "PASS"
        daily_unit = {"pct_dm": "g/day", "mg_kg_dm": "mg/day", "iu_kg_dm": "IU/day"}.get(kind, "day")
        source = spec.get("source") or REQUIREMENT_SOURCE
        breed_on = bool(apply_stars and nid in star_nutrients)
        rows.append(
            {
                "nutrient": nid,
                "nutrient_id": nid,
                "nutrient_name": spec.get("display") or nid,
                "display": spec.get("display") or nid,
                "unit": spec.get("unit"),
                "daily_unit": daily_unit,
                "actual_density_dm": actual,
                "actual_per_day": daily_eq,
                "required_density_min_dm": minimum,
                "required_daily_min": daily_min,
                "maximum_density_dm": maximum,
                "maximum_daily_amount": daily_max,
                "required_minimum": minimum,
                "allowed_maximum": maximum,
                "maximum_specified": maximum is not None,
                "actual": actual,
                "daily_amount": daily_eq,
                "daily_minimum_equivalent": daily_min,
                "daily_maximum_equivalent": daily_max,
                "daily_dm_g": round(dm_g, 6),
                "daily_dm_kg": round(dm_kg, 6),
                "basis": spec.get("basis"),
                "kind": kind,
                "source": source,
                "source_type": (source or {}).get("source_type"),
                "source_reference": (source or {}).get("label"),
                "minimum_status": "FAIL_MINIMUM" if status == "DEFICIENT" else ("PASS" if minimum is not None and status != "NOT_MODELED" else "NO_MODELED_MINIMUM"),
                "maximum_status": "FAIL_MAXIMUM" if status == "EXCESS" else ("PASS" if maximum is not None and status != "NOT_MODELED" else "NO_MODELED_MAXIMUM"),
                "minimum_margin": min_margin,
                "maximum_margin": max_margin,
                "headroom_to_maximum": max_margin,
                "percent_of_minimum": pct_min,
                "percent_of_maximum": pct_max,
                "status": ui_status,
                "status_label": _status_label(ui_status, maximum_specified=maximum is not None),
                "maximum_copy": NOT_SPECIFIED_COPY if maximum is None else None,
                "minimum_copy": NOT_SPECIFIED_COPY if minimum is None else None,
                "star": breed_on,
                "breed_recommended": breed_on,
                "breed_recommendation_reason": (
                    "Warehouse preventative ingredient mapping from this dog's Health Analysis."
                    if breed_on
                    else None
                ),
                "products_contributing": _contributors(totals, nid),
                "synthetic_demo_data": False,
                "requirement_origin": "secondary_source_aafco_summary",
                "product_data_origin": totals.get("data_origin"),
            }
        )
    if failed_min:
        constraint_status = "FAIL_MINIMUM"
    elif exceeded_max:
        constraint_status = "FAIL_MAXIMUM"
    elif missing_data:
        constraint_status = "INSUFFICIENT_DATA"
    else:
        constraint_status = "VALID"
    return {
        "constraint_status": constraint_status,
        "nutrient_rows": rows,
        "failed_minimums": failed_min,
        "exceeded_maximums": exceeded_max,
        "missing_nutrient_data": missing_data,
        "minimums_passed": min_pass,
        "minimums_total": min_total,
        "maximums_passed": max_pass,
        "maximums_total": max_total,
        "daily_dm_g": round(dm_g, 6),
        "daily_dm_kg": round(dm_kg, 6),
    }


def _coverage_summary(rows: list[dict[str, Any]], *, daily_dm_g: float, daily_dm_kg: float) -> dict[str, Any]:
    pass_like = {"PASS", "LOW", "NEAR_MAXIMUM", "NO_MODELED_MAXIMUM"}
    return {
        "daily_dm_g": daily_dm_g,
        "daily_dm_kg": daily_dm_kg,
        "fully_covered": [r["nutrient"] for r in rows if r.get("status") in pass_like and r.get("required_minimum") is not None],
        "near_minimum": [r["nutrient"] for r in rows if r.get("status") == "LOW"],
        "near_maximum": [r["nutrient"] for r in rows if r.get("status") == "NEAR_MAXIMUM"],
        "no_modeled_maximum": [
            r["nutrient"]
            for r in rows
            if r.get("required_minimum") is not None and r.get("allowed_maximum") is None
        ],
        "no_modeled_minimum": [r["nutrient"] for r in rows if r.get("required_minimum") is None and r.get("status") != "NOT_MODELED"],
        "not_modeled": [r["nutrient"] for r in rows if r.get("status") == "NOT_MODELED"],
        "failed_minimum": [r["nutrient"] for r in rows if r.get("status") == "FAIL_MINIMUM"],
        "failed_maximum": [r["nutrient"] for r in rows if r.get("status") == "FAIL_MAXIMUM"],
    }


def _nutrition_ledger(rows: list[dict[str, Any]], *, daily_dm_g: float, daily_dm_kg: float) -> dict[str, Any]:
    return {
        "nutrients": rows,
        "daily_dm_g": daily_dm_g,
        "daily_dm_kg": daily_dm_kg,
        "basis": "dry_matter_diet_density",
        "daily_requirement_note": (
            "Derived daily amounts = source density × dog daily dry-matter intake. "
            "Source values are nutrient concentrations per kg dry matter, not standalone daily grams."
        ),
    }


def _care_score(products: list[dict[str, Any]], priorities: list[str]) -> tuple[float, list[str], list[str]]:
    have: set[str] = set()
    for product in products:
        have.update(_product_pathways(product))
    covered = [path for path in priorities if path in have]
    if not priorities:
        return (0.0, sorted(have), [])
    return (len(covered) / len(priorities), covered, [p for p in priorities if p not in have])


def _nutrition_balance(constraint: dict[str, Any]) -> float:
    rows = [r for r in (constraint.get("nutrient_rows") or []) if r.get("status") != "NOT_MODELED"]
    if not rows:
        return 0.0
    scores = []
    for row in rows:
        if row.get("status") in {"FAIL_MINIMUM", "FAIL_MAXIMUM", "DEFICIENT", "EXCESS", "NOT_MODELED"}:
            return 0.0
        actual = row.get("actual")
        minimum = row.get("required_minimum")
        maximum = row.get("allowed_maximum")
        if actual is None:
            continue
        if minimum is not None and maximum is None:
            ratio = float(actual) / max(float(minimum), 1e-6)
            # Prefer modest surplus, not megadose. Cap the bonus.
            scores.append(min(1.0, 0.65 + 0.35 * min(max(ratio - 1.0, 0.0), 0.5) / 0.5))
        elif maximum is not None:
            cap = float(maximum) or 1.0
            room = float(row.get("maximum_margin") or 0)
            scores.append(max(0.0, min(1.0, 0.5 + 0.5 * (room / cap))))
        else:
            scores.append(1.0)
    return round(sum(scores) / max(len(scores), 1), 4)


def _redundancy(products: list[dict[str, Any]], covered: list[str]) -> float:
    """1.0 = no wasted products; lower if hygiene/supplements add no pathway or nutrient mass."""
    if not products:
        return 1.0
    useful = 0
    for product in products:
        paths = set(_product_pathways(product))
        if _is_staple(product):
            useful += 1
            continue
        if paths & set(covered) or (paths - {"hygiene", "coat"}):
            if demo_product_nutrient(str(product.get("product_id") or "")):
                extras = (demo_product_nutrient(str(product.get("product_id"))) or {}).get("extra_per_serving") or {}
                if extras or (paths & {"joint", "skin", "dental", "digestive", "nutrition"}):
                    useful += 1
                    continue
        # unused hygiene
    return round(useful / len(products), 4)


def _bundle_cost(products: list[dict[str, Any]]) -> tuple[float, float]:
    yearly = sum(float(p.get("yearly_cost") or 0) for p in products)
    monthly = sum(float(p.get("monthly_cost") or 0) for p in products)
    return js_round(monthly), js_round(yearly)


def evaluate_bundle(
    products: list[dict[str, Any]],
    *,
    requirements: dict[str, Any],
    care_priorities: list[str],
    monthly_budget: float | None,
    structurally_ok: bool,
    structural_reason: str | None,
    star_nutrients: list[str] | None = None,
    apply_stars: bool = False,
) -> dict[str, Any]:
    ids = [str(p.get("product_id")) for p in products]
    weight = float((requirements or {}).get("weight_kg") or 30)
    totals = _aggregate_nutrients(products, weight)
    constraint = _evaluate_constraints(
        totals,
        requirements,
        star_nutrients=star_nutrients or [],
        apply_stars=apply_stars,
    )
    monthly, yearly = _bundle_cost(products)
    budget_status = "NOT_PROVIDED"
    if monthly_budget is not None:
        budget_status = "WITHIN_BUDGET" if monthly <= float(monthly_budget) + 1e-6 else "OVER_BUDGET"
    care_score, covered, missing_care = _care_score(products, care_priorities)
    if not structurally_ok:
        constraint_status = "FAIL_CATEGORY"
        rejection = structural_reason or "missing_required_category"
        nutrient_valid = False
    else:
        constraint_status = constraint["constraint_status"]
        rejection = None
        if constraint_status != "VALID":
            rejection = {
                "FAIL_MINIMUM": "minimum_nutrient_failure",
                "FAIL_MAXIMUM": "maximum_nutrient_exceeded",
                "INSUFFICIENT_DATA": "missing_nutrient_data",
            }.get(constraint_status, constraint_status)
        nutrient_valid = constraint_status == "VALID"
    # Budget is applied per-tier later. Nutrient validity ignores budget.
    valid = nutrient_valid
    if nutrient_valid and budget_status == "OVER_BUDGET":
        rejection = rejection or "budget_exceeded"
    balance = _nutrition_balance(constraint) if constraint["constraint_status"] == "VALID" else 0.0
    simplicity = max(0.0, 1.0 - (len(products) - 1) / 10.0)
    redundancy = _redundancy(products, covered)
    min_total = constraint["minimums_total"]
    max_total = constraint["maximums_total"]
    coverage_pct = round(100.0 * constraint["minimums_passed"] / min_total, 2) if min_total else None
    return {
        "bundle_id": _bundle_id(ids),
        "product_ids": ids,
        "product_count": len(products),
        "monthly_cost": monthly,
        "annual_cost": yearly,
        "nutrient_totals": totals,
        "requirement_profile": {
            "dog_size": requirements.get("dog_size"),
            "life_stage": requirements.get("life_stage"),
            "basis": requirements.get("basis"),
            "claim_wording": requirements.get("claim_wording"),
            "complete_diet_claim": False,
            "source": requirements.get("source"),
        },
        "constraint_status": constraint_status if not nutrient_valid else "VALID",
        "failed_minimums": constraint["failed_minimums"],
        "exceeded_maximums": constraint["exceeded_maximums"],
        "missing_nutrient_data": constraint["missing_nutrient_data"],
        "nutrient_rows": constraint["nutrient_rows"],
        "nutrition_facts": constraint["nutrient_rows"],
        "nutrition_ledger": _nutrition_ledger(
            constraint["nutrient_rows"],
            daily_dm_g=float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0),
            daily_dm_kg=float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0) / 1000.0,
        ),
        "coverage_summary": _coverage_summary(
            constraint["nutrient_rows"],
            daily_dm_g=float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0),
            daily_dm_kg=float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0) / 1000.0,
        ),
        "daily_dm_g": float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0),
        "daily_dm_kg": float(totals.get("daily_dm_g") or totals.get("staple_daily_dm_g") or 0) / 1000.0,
        "minimums_passed": constraint["minimums_passed"],
        "minimums_total": min_total,
        "maximums_passed": constraint["maximums_passed"],
        "maximums_total": max_total,
        "nutrient_coverage_percent": coverage_pct,
        "budget_status": budget_status,
        "care_pathways": covered,
        "care_pathways_missing": missing_care,
        "care_coverage_score": round(care_score, 4),
        "nutrition_balance_score": balance,
        "simplicity": round(simplicity, 4),
        "redundancy_score": redundancy,
        "supplement_count": sum(1 for p in products if not _is_staple(p)),
        "rejection_reason": None if nutrient_valid else rejection,
        "structurally_eligible": structurally_ok,
        "nutrient_valid": nutrient_valid,
        "valid": valid,
        "synthetic_demo_data": True,
        "product_data_origin": "demo_synthetic",
    }


def _structural(products: list[dict[str, Any]]) -> tuple[bool, str | None]:
    if not any(_is_staple(p) for p in products):
        return False, "missing_required_category"
    return True, None


def _bounded_index_sets(products: list[dict[str, Any]]) -> list[tuple[int, ...]]:
    staple_i = [i for i, p in enumerate(products) if _is_staple(p)]
    others = [i for i, p in enumerate(products) if not _is_staple(p)][:BOUNDED_ADJUNCT_CAP]
    out: list[tuple[int, ...]] = []
    max_extra = max(0, BOUNDED_MAX_SIZE - 1)
    for staple in staple_i:
        out.append((staple,))
        for rank in range(1, min(max_extra, len(others)) + 1):
            for combo in itertools.combinations(others, rank):
                out.append((staple, *combo))
    uniq: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for combo in out:
        key = tuple(sorted(combo))
        if key not in seen:
            seen.add(key)
            uniq.append(key)
    return uniq


def _score_components(ev: dict[str, Any], monthly_budget: float | None, tier: str) -> dict[str, float]:
    nutrition_adeq = 1.0 if ev.get("nutrient_valid") else 0.0
    nutrition_safe = 1.0 if not ev.get("exceeded_maximums") and ev.get("constraint_status") == "VALID" else 0.0
    care = float(ev.get("care_coverage_score") or 0)
    if monthly_budget:
        if ev.get("budget_status") == "OVER_BUDGET":
            fit = 0.0
        else:
            fit = max(0.0, min(1.0, 1.0 - (float(ev["monthly_cost"]) / float(monthly_budget))))
    else:
        fit = 1.0 - min(1.0, float(ev["monthly_cost"]) / 2500.0)
    excess = 1.0
    if ev.get("nutrient_rows"):
        rooms = []
        for row in ev["nutrient_rows"]:
            if row.get("allowed_maximum") is not None and row.get("actual") is not None:
                cap = float(row["allowed_maximum"]) or 1.0
                rooms.append(max(0.0, min(1.0, float(row.get("maximum_margin") or 0) / cap)))
        if rooms:
            excess = sum(rooms) / len(rooms)
    complementarity = min(1.0, len(ev.get("care_pathways") or []) / 3.0)
    return {
        "nutrition_adequacy": round(nutrition_adeq, 4),
        "nutrition_safety": round(nutrition_safe, 4),
        "care_coverage": round(care, 4),
        "care_score": round(care, 4),
        "budget_fit": round(fit, 4),
        "budget_fit_score": round(fit, 4),
        "simplicity": round(float(ev.get("simplicity") or 0), 4),
        "simplicity_score": round(float(ev.get("simplicity") or 0), 4),
        "nutrition_balance": float(ev.get("nutrition_balance_score") or 0),
        "nutrient_score": float(ev.get("nutrition_balance_score") or 0),
        "redundancy_penalty": round(1.0 - float(ev.get("redundancy_score") or 1), 4),
        "excess_avoidance": round(excess, 4),
        "complementarity": round(complementarity, 4),
        "price_score": round(1.0 - min(1.0, float(ev["monthly_cost"]) / 2000.0), 4),
    }


def _overall(tier: str, parts: dict[str, float], ev: dict[str, Any]) -> float:
    w = SCORE_WEIGHTS[tier]
    if tier == "essential":
        return round(
            w["price"] * parts["price_score"]
            + w["simplicity"] * parts["simplicity"]
            + w["nutrient_balance"] * parts["nutrition_balance"]
            - w["redundancy_penalty"] * parts["redundancy_penalty"],
            4,
        )
    if tier == "balanced":
        return round(
            w["care"] * parts["care_coverage"]
            + w["nutrient_balance"] * parts["nutrition_balance"]
            + w["budget_fit"] * parts["budget_fit"]
            + w["simplicity"] * parts["simplicity"]
            + w["nutrition_adequacy"] * parts["nutrition_adequacy"],
            4,
        )
    return round(
        w["nutrient_adequacy"] * parts["nutrition_adequacy"]
        + w["nutrient_balance"] * parts["nutrition_balance"]
        + w["care"] * parts["care_coverage"]
        + w["complementarity"] * parts["complementarity"]
        + w["simplicity"] * parts["simplicity"]
        + w["excess_avoidance"] * parts["excess_avoidance"]
        + w["budget_fit"] * parts["budget_fit"],
        4,
    )


def _why(ev: dict[str, Any], tier: str, monthly_budget: float | None) -> list[str]:
    reasons = [
        "Meets all modeled minimum nutrient constraints" if ev.get("nutrient_valid") else f"Constraint status: {ev.get('constraint_status')}",
        "Does not exceed modeled nutrient maximums" if not ev.get("exceeded_maximums") else "Exceeded a modeled nutrient maximum",
        "Not a guaranteed complete diet",
        f"Modeled minimums {ev.get('minimums_passed')}/{ev.get('minimums_total')}",
        f"Modeled maximums {ev.get('maximums_passed')}/{ev.get('maximums_total')}",
        "Product nutrient data in this demo are synthetic." if ev.get("synthetic_demo_data") else "Product nutrient data origin is the active catalog.",
    ]
    if tier != "essential" and ev.get("care_pathways"):
        reasons.append(
            f"Covers {len(ev.get('care_pathways') or [])} modeled breed-care pathway(s): "
            + ", ".join(ev["care_pathways"])
            + " (preventive signal, not a diagnosis)"
        )
    if monthly_budget is not None and tier != "optimal":
        reasons.append(
            "Fits monthly budget" if ev.get("budget_status") == "WITHIN_BUDGET" else "Outside stated monthly budget"
        )
    if tier == "essential":
        reasons.append("Ranked for lowest cost among valid baseline bundles, then simplicity. Breed-care score is not used.")
    elif tier == "balanced":
        reasons.append("Ranked for care-pathway coverage, nutrient balance, then price among budget-eligible bundles.")
    else:
        reasons.append("Ranked for nutritional balance and care coverage; cost is secondary; budget is not a hard ceiling.")
    return reasons


def _why_ranked_list(row: dict[str, Any], tier: str, pool: list[dict[str, Any]]) -> list[str]:
    n = max(len(pool), 1)
    cheaper = sum(1 for p in pool if float(p["monthly_cost"]) > float(row["monthly_cost"]) + 1e-6)
    pct_cheaper = round(100.0 * cheaper / n, 1)
    parts = row.get("score_components") or {}
    lines = [
        "Meets all modeled minimum nutrient constraints",
        "Does not exceed modeled nutrient maximums",
        f"Rank {row.get('rank')} of {len(pool)} valid {tier} combinations",
    ]
    if tier == "essential":
        lines.append(f"Lower cost than {pct_cheaper}% of valid Essential bundles")
        lines.append(f"¥{row.get('monthly_cost')}/month · {row.get('product_count')} products")
    elif tier == "balanced":
        n_paths = len(row.get("care_pathways") or [])
        lines.append(f"Covers {n_paths} modeled breed-care pathways (care score {parts.get('care_coverage')})")
        lines.append(f"Nutrition balance {parts.get('nutrition_balance')}")
        if row.get("budget_status") == "WITHIN_BUDGET":
            lines.append("Fits monthly budget")
        lines.append(f"Lower cost than {pct_cheaper}% of valid Balanced bundles")
    else:
        lines.append(f"Nutrition balance {parts.get('nutrition_balance')}")
        lines.append(f"Care coverage {parts.get('care_coverage')}")
        lines.append("Budget is not a hard ceiling for Optimal")
        lines.append(f"Score {row.get('overall_score')}")
    return lines


def _why_ranked(ev: dict[str, Any], tier: str) -> str:
    parts = ev.get("score_components") or {}
    if tier == "essential":
        return (
            f"Rank {ev.get('rank')}: lowest-cost valid baseline "
            f"(¥{ev.get('monthly_cost')}/mo, {ev.get('product_count')} products, score {ev.get('overall_score')})"
        )
    if tier == "balanced":
        return (
            f"Rank {ev.get('rank')}: care {parts.get('care_coverage')} · "
            f"nutrient {parts.get('nutrition_balance')} · budget_fit {parts.get('budget_fit')} · "
            f"price ¥{ev.get('monthly_cost')}"
        )
    return (
        f"Rank {ev.get('rank')}: balance {parts.get('nutrition_balance')} · "
        f"care {parts.get('care_coverage')} · excess_avoidance {parts.get('excess_avoidance')} · "
        f"score {ev.get('overall_score')}"
    )


def _outrank_reasons(row: dict[str, Any], nxt: dict[str, Any] | None, tier: str) -> list[str]:
    if nxt is None:
        return ["No lower-ranked displayed alternative in this slice."]
    reasons: list[str] = []
    if float(row["monthly_cost"]) + 1e-6 < float(nxt["monthly_cost"]):
        reasons.append(
            f"Lower monthly cost than rank {nxt.get('rank')} "
            f"(¥{row.get('monthly_cost')} vs ¥{nxt.get('monthly_cost')})"
        )
    if int(row["product_count"]) < int(nxt["product_count"]):
        reasons.append(f"Fewer products than rank {nxt.get('rank')}")
    if float(row.get("care_coverage_score") or 0) > float(nxt.get("care_coverage_score") or 0) + 1e-9:
        reasons.append("Higher preventative pathway coverage than the next displayed bundle")
    if float(row.get("nutrition_balance_score") or 0) > float(nxt.get("nutrition_balance_score") or 0) + 1e-9:
        reasons.append("Better nutrient-balance score than the next displayed bundle")
    if tier == "optimal" and float(row.get("overall_score") or 0) > float(nxt.get("overall_score") or 0) + 1e-9:
        reasons.append("Higher overall completeness score than the next displayed bundle")
    if not reasons:
        reasons.append("Deterministic tie-break (cost, product count, or bundle_id) among equal rank keys")
    return reasons


def _bundle_reasoning(row: dict[str, Any], tier: str, nxt: dict[str, Any] | None) -> dict[str, Any]:
    nutrition: list[str] = []
    if row.get("nutrient_valid"):
        nutrition.append("Meets all modeled minimum requirements")
        nutrition.append("Exceeds no modeled maximum")
    else:
        nutrition.append(f"Constraint status: {row.get('constraint_status')}")
    for n_row in (row.get("nutrition_facts") or row.get("nutrient_rows") or [])[:4]:
        if not isinstance(n_row, dict):
            continue
        pct = n_row.get("percent_of_minimum")
        label = n_row.get("display") or n_row.get("nutrient")
        if pct is not None and label:
            nutrition.append(f"Provides {round(float(pct))}% of modeled {label} requirement")
    health: list[str] = []
    if tier != "essential":
        health.append("Supports the dog's breed-specific preventative priorities:")
        for path in row.get("care_pathways") or []:
            health.append(PATHWAY_LABELS.get(str(path), str(path)))
        records = row.get("care_pathway_records") or []
        for rec in records[:4]:
            if isinstance(rec, dict) and rec.get("condition"):
                health.append(str(rec.get("condition")))
    budget = []
    if tier == "optimal":
        budget.append("Optimal has no customer budget ceiling. Nutrient maximums remain hard constraints.")
        if row.get("budget_status") == "OVER_BUDGET":
            budget.append("Stated budget is informational only for Optimal.")
        elif row.get("budget_status") == "WITHIN_BUDGET":
            budget.append("Also happens to fit the stated monthly budget.")
    elif row.get("budget_status") == "WITHIN_BUDGET":
        budget.append("Within customer's monthly budget")
    elif row.get("budget_status") == "OVER_BUDGET":
        budget.append("Outside stated monthly budget")
    else:
        budget.append("No customer budget supplied")
    preventative: list[dict[str, Any]] = []
    if tier != "essential":
        for path in row.get("care_pathways") or []:
            contributors = [
                {
                    "product_id": item.get("product_id"),
                    "product_name": item.get("product_name"),
                    "role": item.get("role"),
                }
                for item in (row.get("products") or [])
                if path in (item.get("care_pathways") or [])
            ]
            preventative.append(
                {
                    "pathway": path,
                    "copy": f"Associated preventative pathway: {path}",
                    "contributing_products": contributors,
                }
            )
    return {
        "health_fit": health,
        "nutrition": nutrition,
        "baseline_nutrition": nutrition or [
            "Meets all modeled minimum nutrient requirements"
            if row.get("nutrient_valid")
            else f"Constraint status: {row.get('constraint_status')}"
        ],
        "preventative_care": preventative,
        "budget": budget,
        "ranking": [
            f"#{row.get('rank')} of {row.get('tier_valid_count')} valid {str(tier).title()} combinations",
            f"Showing {row.get('displayed_count')} of {row.get('tier_valid_count')} valid combinations",
        ],
        "why_outranked": _outrank_reasons(row, nxt, tier),
        "complete_diet_claim": False,
    }


def _jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(len(sa | sb), 1)


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    cost_le = float(a["monthly_cost"]) <= float(b["monthly_cost"]) + 1e-6
    care_ge = float(a.get("care_coverage_score") or 0) >= float(b.get("care_coverage_score") or 0) - 1e-9
    bal_ge = float(a.get("nutrition_balance_score") or 0) >= float(b.get("nutrition_balance_score") or 0) - 1e-9
    n_le = int(a["product_count"]) <= int(b["product_count"])
    strict = (
        float(a["monthly_cost"]) < float(b["monthly_cost"]) - 1e-6
        or float(a.get("care_coverage_score") or 0) > float(b.get("care_coverage_score") or 0) + 1e-9
        or float(a.get("nutrition_balance_score") or 0) > float(b.get("nutrition_balance_score") or 0) + 1e-9
        or int(a["product_count"]) < int(b["product_count"])
    )
    return cost_le and care_ge and bal_ge and n_le and strict


def _non_dominated(valid: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keep = []
    for ev in valid:
        if any(_dominates(other, ev) for other in valid if other is not ev):
            continue
        keep.append(ev)
    return keep


def _diverse(ranked: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for ev in ranked:
        if len(kept) >= limit:
            break
        distinct = True
        for prev in kept:
            jac = _jaccard(ev["product_ids"], prev["product_ids"])
            cost_close = abs(float(ev["monthly_cost"]) - float(prev["monthly_cost"])) < max(40.0, 0.12 * float(prev["monthly_cost"]))
            if jac >= 0.8 and cost_close and ev["product_count"] == prev["product_count"]:
                distinct = False
                break
        if distinct:
            kept.append(ev)
    return kept or ranked[:limit]


def _eligible_for_tier(ev: dict[str, Any], tier: str, care_priorities: list[str]) -> bool:
    if not ev.get("nutrient_valid"):
        return False
    if tier == "balanced" and care_priorities:
        return float(ev.get("care_coverage_score") or 0) > 0
    return True


def _rank_tier(
    valid: list[dict[str, Any]],
    tier: str,
    monthly_budget: float | None,
    *,
    apply_budget: bool,
    option_limit: int,
    care_priorities: list[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    eligible = [ev for ev in valid if _eligible_for_tier(ev, tier, care_priorities or [])]
    pool = []
    over = []
    for ev in eligible:
        over_budget = monthly_budget is not None and ev.get("budget_status") == "OVER_BUDGET"
        if apply_budget and over_budget:
            over.append(ev)
            continue
        budget_for_score = monthly_budget if apply_budget else None
        if tier == "optimal":
            budget_for_score = None
        parts = _score_components(ev, budget_for_score, tier)
        overall = _overall(tier, parts, ev)
        row = {
            **ev,
            "tier": tier,
            "score_components": {**parts, "total_score": overall},
            "overall_score": overall,
            "scoring_weights": SCORE_WEIGHTS[tier],
            "why_selected": _why(ev, tier, monthly_budget if apply_budget else None),
        }
        pool.append(row)
    meta = {
        "valid_count": len(pool),
        "eligible_before_budget": len(eligible),
        "within_budget_count": len(pool) if apply_budget else len(eligible),
        "over_budget_count": len(over) if apply_budget else 0,
        "budget_status": "NOT_PROVIDED",
        "ranking_rule": RANKING_RULES[tier],
        "displayed_count": 0,
    }
    if apply_budget and monthly_budget is not None:
        meta["budget_status"] = "WITHIN_BUDGET" if pool else "NO_VALID_BUNDLE_WITHIN_BUDGET"
    if not pool and apply_budget and over:
        over.sort(key=lambda e: (e["monthly_cost"], e["product_count"], e["bundle_id"]))
        meta["least_over_budget_alternatives"] = [
            {"bundle_id": e["bundle_id"], "product_ids": e["product_ids"], "monthly_cost": e["monthly_cost"]}
            for e in over[:5]
        ]
    if tier == "essential":
        pool.sort(key=lambda e: (e["monthly_cost"], e["product_count"], -e["overall_score"], e["bundle_id"]))
    elif tier == "balanced":
        pool.sort(
            key=lambda e: (
                -e["score_components"]["care_coverage"],
                -e["score_components"]["nutrition_balance"],
                e["monthly_cost"],
                e["product_count"],
                e["bundle_id"],
            )
        )
    else:
        pool.sort(
            key=lambda e: (
                -e["overall_score"],
                -e["nutrition_balance_score"],
                -e["care_coverage_score"],
                e["product_count"],
                e["monthly_cost"],
                e["bundle_id"],
            )
        )
    displayed = pool[:option_limit]
    meta["displayed_count"] = len(displayed)
    for i, row in enumerate(displayed):
        row["rank"] = i + 1
        row["rank_among_valid"] = i + 1
        row["tier_valid_count"] = len(pool)
        row["displayed_count"] = len(displayed)
        nxt = displayed[i + 1] if i + 1 < len(displayed) else None
        row["why_ranked"] = _why_ranked_list(row, tier, pool)
        row["why_ranked_here"] = _why_ranked(row, tier)
        row["why_outranked"] = _outrank_reasons(row, nxt, tier)
    return displayed, meta


def _counterfactual(
    ev: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    requirements: dict[str, Any],
    care_priorities: list[str],
    monthly_budget: float | None,
    star_nutrients: list[str],
) -> list[dict[str, Any]]:
    products = [by_id[pid] for pid in ev["product_ids"] if pid in by_id]
    out = []
    for pid in ev["product_ids"]:
        remaining = [p for p in products if p.get("product_id") != pid]
        if not remaining:
            out.append(
                {
                    "product_id": pid,
                    "still_valid": False,
                    "why_this_product_matters": "Removing this product leaves an empty bundle.",
                }
            )
            continue
        ok, reason = _structural(remaining)
        alt = evaluate_bundle(
            remaining,
            requirements=requirements,
            care_priorities=care_priorities,
            monthly_budget=monthly_budget,
            structurally_ok=ok,
            structural_reason=reason,
            star_nutrients=star_nutrients,
        )
        notes = []
        if ev.get("nutrient_valid") and not alt["nutrient_valid"]:
            notes.append(f"Without {pid} the bundle is no longer valid ({alt['constraint_status']}).")
        if alt["care_coverage_score"] < ev.get("care_coverage_score", 0):
            notes.append(f"Care coverage {ev.get('care_coverage_score')} → {alt['care_coverage_score']}")
        if alt["monthly_cost"] < ev["monthly_cost"]:
            notes.append(f"Monthly cost {ev['monthly_cost']} → {alt['monthly_cost']}")
        for row in ev.get("nutrient_rows") or []:
            nid = row.get("nutrient")
            match = next((r for r in alt.get("nutrient_rows") or [] if r.get("nutrient") == nid), None)
            if row.get("minimum_margin") is not None and match and match.get("minimum_margin") is not None:
                if match["minimum_margin"] < row["minimum_margin"]:
                    notes.append(f"{nid} minimum margin {row['minimum_margin']} → {match['minimum_margin']}")
        if not notes:
            notes.append("Removing this product does not change validity; retained for ranked coverage/cost tradeoff.")
        demo = demo_product_nutrient(pid)
        contrib = next((c for c in (ev.get("nutrient_totals") or {}).get("per_product") or [] if c.get("product_id") == pid), {})
        score_delta = round(float(ev.get("overall_score") or 0) - float(alt.get("nutrition_balance_score") or 0), 4)
        life = (requirements or {}).get("life_stage") or "adult"
        weight = (requirements or {}).get("weight_kg")
        if _is_staple(by_id[pid]):
            selection = f"Provides baseline staple nutrition required for {life} {weight} kg dog."
        elif ev.get("nutrient_valid") and not alt["nutrient_valid"] and (alt.get("failed_minimums") or []):
            fail = alt["failed_minimums"][0]
            nid = fail.get("nutrient")
            match = next((r for r in ev.get("nutrient_rows") or [] if r.get("nutrient") == nid), None)
            name = (match or {}).get("display") or nid
            selection = (
                f"Raises modeled {name} density above the {life} minimum "
                f"({fail.get('actual')} → {(match or {}).get('actual')} {fail.get('unit')}; "
                f"required {fail.get('required')})."
            )
        else:
            selection = notes[0]
        out.append(
                {
                    "product_id": pid,
                    "product_name": (by_id.get(pid) or {}).get("product_name") or (by_id.get(pid) or {}).get("name"),
                    "role": (demo or {}).get("role") or by_id[pid].get("role"),
                "contribution": contrib,
                "nutrient_contributions": contrib.get("daily_amounts") or {},
                "care_pathways": _product_pathways(by_id[pid]),
                "selection_reason": selection,
                "marginal_contribution": notes,
                "cost_contribution": round(float(ev["monthly_cost"]) - float(alt["monthly_cost"]), 4),
                "ranking_effect": score_delta,
                "bundle_without_product": alt["product_ids"],
                "still_valid": alt["nutrient_valid"],
                "without_constraint_status": alt["constraint_status"],
                "without_failed_minimums": alt.get("failed_minimums") or [],
                "without_exceeded_maximums": alt.get("exceeded_maximums") or [],
                "without_care_coverage": alt["care_coverage_score"],
                "without_monthly_cost": alt["monthly_cost"],
                "synthetic_demo_data": bool(demo),
            }
        )
    return out


def _why_not(
    ev: dict[str, Any],
    candidates: list[dict[str, Any]],
    requirements: dict[str, Any],
    care_priorities: list[str],
    monthly_budget: float | None,
) -> list[dict[str, Any]]:
    in_ids = set(ev["product_ids"])
    by_id = {str(p.get("product_id")): p for p in candidates}
    current = [by_id[i] for i in ev["product_ids"] if i in by_id]
    out = []
    for product in candidates:
        pid = str(product.get("product_id"))
        if pid in in_ids:
            continue
        combo = current + [product]
        ok, reason = _structural(combo)
        alt = evaluate_bundle(
            combo,
            requirements=requirements,
            care_priorities=care_priorities,
            monthly_budget=monthly_budget,
            structurally_ok=ok,
            structural_reason=reason,
        )
        reasons = []
        if ev.get("nutrient_valid") and not alt.get("nutrient_valid"):
            reasons.append(f"Adding {pid} violates {alt.get('constraint_status')}")
            if alt.get("exceeded_maximums"):
                reasons.append("caused nutrient maximum violation")
            if alt.get("failed_minimums"):
                reasons.append("did not repair a minimum (or created a new failure)")
        else:
            if alt["monthly_cost"] > ev["monthly_cost"] and alt["care_coverage_score"] <= ev["care_coverage_score"] + 1e-9:
                reasons.append("higher cost without improving care coverage")
            if alt["nutrition_balance_score"] <= ev["nutrition_balance_score"] + 1e-9 and alt["product_count"] > ev["product_count"]:
                reasons.append("did not improve nutrient balance; extra product is redundant")
            if _dominates(ev, alt):
                reasons.append("dominated by the selected bundle (cost/care/balance/simplicity)")
        if not reasons:
            reasons.append("did not improve optimality score enough to enter the returned set")
        out.append(
            {
                "product_id": pid,
                "reasons": reasons,
                "constraint_status": alt.get("constraint_status"),
                "monthly_cost_if_added": alt.get("monthly_cost"),
                "care_if_added": alt.get("care_coverage_score"),
                "valid_if_added": alt.get("nutrient_valid"),
            }
        )
    return out


def run_package_search(
    *,
    candidates: list[dict[str, Any]],
    profile: Any,
    monthly_budget: float | None = None,
    option_limit: int | None = None,
    repo: Any | None = None,
) -> dict[str, Any]:
    observations = list(getattr(profile, "observed_conditions", None) or [])
    weight = float(getattr(profile, "weight_kg", None) or 10)
    age = float(getattr(profile, "age_years", None) or 5)
    if monthly_budget is None:
        raw_budget = getattr(profile, "monthly_budget", None)
        if raw_budget not in (None, ""):
            try:
                monthly_budget = float(raw_budget)
            except (TypeError, ValueError):
                monthly_budget = None
    limit = OPTIONS_PER_TIER if option_limit is None else max(1, min(int(option_limit), MAX_BUNDLE_OPTIONS))
    demo = demo_mode_enabled()
    if demo:
        requirements = build_demo_requirement_profile(weight_kg=weight, age_years=age)
        nutrient_mode = "synthetic_demo_products + secondary_source_requirements"
    else:
        requirements = {
            "synthetic_demo_data": False,
            "dog_size": None,
            "life_stage": None,
            "basis": None,
            "weight_kg": weight,
            "claim_wording": "nutrient validation incomplete — product dry-matter data unavailable",
            "complete_diet_claim": False,
            "nutrients": {},
        }
        nutrient_mode = "insufficient_product_nutrient_data"
    breeds = [
        str(getattr(profile, "primary_breed", "") or ""),
        str(getattr(profile, "secondary_breed", "") or ""),
    ]
    if repo is not None:
        care_model = resolve_care_model(repo, breeds, observations, demo=demo)
    else:
        care_model = resolve_care_model(None, breeds, observations, demo=demo)
    care_priorities = list(care_model.get("pathways") or [])
    star_nutrients = list(care_model.get("star_nutrients") or [])
    n = len(candidates)
    by_id = {str(p.get("product_id")): p for p in candidates}
    if n <= EXHAUSTIVE_MAX_N:
        method = "EXHAUSTIVE_ENUMERATION"
        index_sets = [tuple(i for i in range(n) if mask & (1 << i)) for mask in range(1, 1 << n)]
    else:
        method = "BOUNDED_ENUMERATION_MAX_SIZE"
        index_sets = _bounded_index_sets(candidates)
    total_subsets = (1 << n) - 1 if n else 0
    counts = {
        "minimum_nutrient_failure": 0,
        "maximum_nutrient_exceeded": 0,
        "missing_nutrient_data": 0,
        "missing_required_category": 0,
        "budget_exceeded": 0,
    }
    structurally_eligible = 0
    evaluated = 0
    passed_min = 0
    passed_max = 0
    nutrient_valid_list: list[dict[str, Any]] = []
    example_rejections: list[dict[str, Any]] = []
    examples_by_reason: dict[str, int] = {}
    min_fail_by_nutrient: Counter[str] = Counter()
    max_fail_by_nutrient: Counter[str] = Counter()
    explorer_samples: dict[str, list[dict[str, Any]]] = {
        "minimum_failures": [],
        "maximum_failures": [],
        "missing_staple": [],
        "budget_failures": [],
    }

    for idxs in index_sets:
        products = [candidates[i] for i in idxs]
        ok, reason = _structural(products)
        if ok:
            structurally_eligible += 1
        evaluated += 1
        ev = evaluate_bundle(
            products,
            requirements=requirements,
            care_priorities=care_priorities,
            monthly_budget=monthly_budget,
            structurally_ok=ok,
            structural_reason=reason,
            star_nutrients=star_nutrients,
            apply_stars=False,
        )
        if ok and ev["constraint_status"] not in {"FAIL_MINIMUM", "INSUFFICIENT_DATA", "FAIL_CATEGORY"}:
            passed_min += 1
        if ok and ev["constraint_status"] not in {"FAIL_MAXIMUM", "FAIL_MINIMUM", "INSUFFICIENT_DATA", "FAIL_CATEGORY"}:
            passed_max += 1
        if ev["nutrient_valid"]:
            nutrient_valid_list.append(ev)
            if ev.get("budget_status") == "OVER_BUDGET":
                counts["budget_exceeded"] += 1
                if len(explorer_samples["budget_failures"]) < 8:
                    explorer_samples["budget_failures"].append(
                        {
                            "product_ids": ev["product_ids"],
                            "reason": "budget_exceeded",
                            "monthly_cost": ev["monthly_cost"],
                            "constraint_status": ev["constraint_status"],
                        }
                    )
        else:
            key = ev.get("rejection_reason") or "missing_nutrient_data"
            if key in counts:
                counts[key] += 1
            for fail in ev.get("failed_minimums") or []:
                min_fail_by_nutrient[str(fail.get("nutrient"))] += 1
            for fail in ev.get("exceeded_maximums") or []:
                max_fail_by_nutrient[str(fail.get("nutrient"))] += 1
            sample_key = {
                "minimum_nutrient_failure": "minimum_failures",
                "maximum_nutrient_exceeded": "maximum_failures",
                "missing_required_category": "missing_staple",
            }.get(key)
            if sample_key and len(explorer_samples[sample_key]) < 8:
                explorer_samples[sample_key].append(
                    {
                        "product_ids": ev["product_ids"],
                        "reason": key,
                        "constraint_status": ev["constraint_status"],
                        "failed_minimums": ev["failed_minimums"][:3],
                        "exceeded_maximums": ev["exceeded_maximums"][:3],
                        "decision": "REMOVED FROM CANDIDATE SET",
                    }
                )
            n_ex = examples_by_reason.get(key, 0)
            if n_ex < 8:
                examples_by_reason[key] = n_ex + 1
                example_rejections.append(
                    {
                        "product_ids": ev["product_ids"],
                        "reason": key,
                        "constraint_status": ev["constraint_status"],
                        "failed_minimums": ev["failed_minimums"][:3],
                        "exceeded_maximums": ev["exceeded_maximums"][:3],
                        "nutrient_row_count": len(ev.get("nutrient_rows") or []),
                        "decision": "REMOVED FROM CANDIDATE SET",
                    }
                )

    non_dom = _non_dominated(nutrient_valid_list)
    with_care = sum(1 for ev in nutrient_valid_list if (ev.get("care_coverage_score") or 0) > 0)
    full_care = sum(1 for ev in nutrient_valid_list if (ev.get("care_coverage_score") or 0) >= 1.0 - 1e-9)
    within_budget = sum(1 for ev in nutrient_valid_list if ev.get("budget_status") != "OVER_BUDGET")

    essential, ess_meta = _rank_tier(
        nutrient_valid_list,
        "essential",
        monthly_budget,
        apply_budget=monthly_budget is not None,
        option_limit=limit,
        care_priorities=care_priorities,
    )
    balanced, bal_meta = _rank_tier(
        nutrient_valid_list,
        "balanced",
        monthly_budget,
        apply_budget=True,
        option_limit=limit,
        care_priorities=care_priorities,
    )
    optimal, opt_meta = _rank_tier(
        nutrient_valid_list,
        "optimal",
        monthly_budget,
        apply_budget=False,
        option_limit=limit,
        care_priorities=care_priorities,
    )

    if not nutrient_valid_list and not demo:
        fallback = []
        for idxs in index_sets:
            products = [candidates[i] for i in idxs]
            ok, _reason = _structural(products)
            if not ok:
                continue
            monthly, yearly = _bundle_cost(products)
            ids = [str(p.get("product_id")) for p in products]
            fallback.append(
                {
                    "bundle_id": _bundle_id(ids),
                    "product_ids": ids,
                    "product_count": len(products),
                    "monthly_cost": monthly,
                    "annual_cost": yearly,
                    "valid": False,
                    "nutrient_valid": False,
                    "constraint_status": "INSUFFICIENT_DATA",
                    "care_coverage_score": 0.0,
                    "nutrition_balance_score": 0.0,
                    "simplicity": max(0.0, 1.0 - (len(products) - 1) / 10.0),
                    "redundancy_score": 1.0,
                    "failed_minimums": [],
                    "exceeded_maximums": [],
                    "missing_nutrient_data": list(NUTRIENT_IDS[:2]),
                    "nutrient_rows": [],
                    "nutrition_facts": [],
                    "nutrient_totals": {"synthetic_demo_data": False},
                    "budget_status": "NOT_PROVIDED",
                    "care_pathways": [],
                    "supplement_count": sum(1 for p in products if p.get("role") != "staple"),
                    "requirement_profile": requirements,
                    "structurally_eligible": True,
                    "rejection_reason": "missing_nutrient_data",
                    "minimums_passed": 0,
                    "minimums_total": 0,
                    "maximums_passed": 0,
                    "maximums_total": 0,
                }
            )
        fallback.sort(key=lambda e: (e["monthly_cost"], e["product_count"]))
        essential, ess_meta = _rank_tier(
            fallback, "essential", monthly_budget, apply_budget=False, option_limit=limit, care_priorities=care_priorities
        )
        balanced, bal_meta = _rank_tier(
            fallback, "balanced", monthly_budget, apply_budget=False, option_limit=limit, care_priorities=care_priorities
        )
        optimal, opt_meta = _rank_tier(
            fallback, "optimal", monthly_budget, apply_budget=False, option_limit=limit, care_priorities=care_priorities
        )

    def decorate(options: list[dict[str, Any]], *, stars: bool, tier_valid: int) -> list[dict[str, Any]]:
        decorated = []
        for i, ev in enumerate(options):
            row = dict(ev)
            ledger_rows = [dict(r) for r in (row.get("nutrient_rows") or [])]
            for nutrient_row in ledger_rows:
                flagged = bool(stars and nutrient_row.get("nutrient") in star_nutrients)
                nutrient_row["star"] = flagged
                nutrient_row["breed_recommended"] = flagged
                nutrient_row["breed_recommendation_reason"] = (
                    "Warehouse preventative ingredient mapping from this dog's Health Analysis."
                    if flagged
                    else None
                )
            row["nutrient_rows"] = ledger_rows
            row["nutrition_facts"] = ledger_rows
            if isinstance(row.get("nutrition_ledger"), dict):
                row["nutrition_ledger"] = {
                    **row["nutrition_ledger"],
                    "nutrients": ledger_rows,
                }
            row["product_provenance"] = _counterfactual(
                ev, by_id, requirements, care_priorities, monthly_budget, star_nutrients
            )
            prov_by = {p["product_id"]: p for p in row["product_provenance"]}
            per_prod = {
                str(c.get("product_id")): c
                for c in (ev.get("nutrient_totals") or {}).get("per_product") or []
            }
            products_out = []
            for pid in ev.get("product_ids") or []:
                product = by_id.get(pid) or {}
                demo_row = demo_product_nutrient(pid) or {}
                contrib = per_prod.get(pid) or {}
                pv = prov_by.get(pid) or {}
                products_out.append(
                    {
                        "product_id": pid,
                        "product_name": product.get("product_name") or product.get("name"),
                        "brand": product.get("brand"),
                        "category": product.get("category") or demo_row.get("role"),
                        "short_description": product.get("short_description"),
                        "primary_function": next(
                            (
                                str(fn.get("function"))
                                for fn in (product.get("functions") or [])
                                if isinstance(fn, dict) and fn.get("function")
                            ),
                            None,
                        ),
                        "role": demo_row.get("role") or product.get("role"),
                        "daily_amount": contrib.get("daily_dm_g") or contrib.get("serving_g_as_fed"),
                        "daily_dm_g": contrib.get("daily_dm_g"),
                        "monthly_cost": product.get("monthly_cost"),
                        "nutrient_contributions": contrib.get("daily_amounts") or {},
                        "care_pathways": _product_pathways(product),
                        "selection_reason": pv.get("selection_reason"),
                    }
                )
            row["products"] = products_out
            row["display_product_names"] = [
                str(item.get("product_name"))
                for item in products_out
                if item.get("product_name")
            ]
            row["ranking_rule"] = RANKING_RULES.get(str(row.get("tier") or ""), "")
            row["care_pathway_records"] = list(care_model.get("condition_records") or []) if stars else []
            nxt = options[i + 1] if i + 1 < len(options) else None
            row["bundle_reasoning"] = _bundle_reasoning(row, row.get("tier") or "", nxt)
            briefs = list(care_model.get("pathway_briefs") or [])
            covered = set(row.get("care_pathways") or [])
            row["preventative_pathways"] = (
                [brief for brief in briefs if brief.get("pathway") in covered]
                if stars
                else []
            )
            reasoning = row["bundle_reasoning"]
            if stars and briefs:
                reasoning["preventative_care"] = [
                    {
                        **item,
                        "contributing_products": [
                            {
                                "product_id": prod.get("product_id"),
                                "product_name": prod.get("product_name"),
                                "role": prod.get("role"),
                            }
                            for prod in products_out
                            if item.get("pathway") in (prod.get("care_pathways") or [])
                        ],
                    }
                    for item in briefs
                    if item.get("pathway") in covered
                ]
            row["breed_recommendations"] = (
                [
                    {
                        "nutrient": nid,
                        "star": True,
                        "reason": "Based on warehouse preventative ingredient–condition evidence for this dog.",
                    }
                    for nid in star_nutrients
                ]
                if stars
                else []
            )
            row["optimizer_version"] = "PACKAGE_OPTIMIZER_V2_1"
            row["search_provenance"] = {
                "algorithm": "PACKAGE_OPTIMIZER_V2_1",
                "search_method": method,
                "evaluated_count": evaluated,
                "valid_count": len(nutrient_valid_list),
                "tier_valid_count": tier_valid,
                "displayed_count": len(options),
                "non_dominated_count": len(non_dom),
                "rank": row.get("rank"),
            }
            row["why_not_included"] = (
                _why_not(ev, candidates, requirements, care_priorities, monthly_budget) if i < 2 else []
            )
            decorated.append(row)
        return decorated

    essential_o = decorate(essential, stars=False, tier_valid=ess_meta.get("valid_count") or 0)
    balanced_o = decorate(balanced, stars=True, tier_valid=bal_meta.get("valid_count") or 0)
    optimal_o = decorate(optimal, stars=True, tier_valid=opt_meta.get("valid_count") or 0)
    funnel = {
        "generated": total_subsets,
        "evaluated": evaluated,
        "life_stage_species_structurally_eligible": structurally_eligible,
        "nutrient_calculated": evaluated,
        "passed_minimum_filter": passed_min,
        "passed_maximum_filter": passed_max,
        "nutrient_valid": len(nutrient_valid_list),
        "non_dominated": len(non_dom),
        "with_any_care_coverage": with_care,
        "full_care_coverage": full_care,
        "within_budget": within_budget,
        "satisfy_essential": ess_meta.get("valid_count") or 0,
        "satisfy_balanced": bal_meta.get("valid_count") or 0,
        "satisfy_optimal": opt_meta.get("valid_count") or 0,
        "displayed": {
            "essential": len(essential_o),
            "balanced": len(balanced_o),
            "optimal": len(optimal_o),
        },
        "note": (
            "Dominance is an audit statistic. Ranking and display use all tier-eligible "
            "nutrient-valid combinations, truncated only at PACKAGE_DISPLAY_LIMIT."
        ),
    }
    return {
        "requirement_profile": requirements,
        "care_priorities": care_priorities,
        "care_model": care_model,
        "nutrient_mode": nutrient_mode,
        "scoring_weights": SCORE_WEIGHTS,
        "package_options": {"essential": essential_o, "balanced": balanced_o, "optimal": optimal_o},
        "tier_budget": {"essential": ess_meta, "balanced": bal_meta, "optimal": opt_meta},
        "provenance": {
            "algorithm": "PACKAGE_OPTIMIZER_V2_1",
            "search_method": method,
            "candidate_count": n,
            "total_possible_subsets": total_subsets,
            "structurally_eligible": structurally_eligible,
            "evaluated_count": evaluated,
            "valid_count": len(nutrient_valid_list),
            "rejected_count": evaluated - len(nutrient_valid_list),
            "non_dominated_count": len(non_dom),
            "raw_candidates": total_subsets,
            "valid_candidates": len(nutrient_valid_list),
            "non_dominated_candidates": len(non_dom),
            "display_limit": limit,
            "top_n": limit,
            "max_bundle_options": MAX_BUNDLE_OPTIONS,
            "tier_valid_counts": {
                "essential": ess_meta.get("valid_count") or 0,
                "balanced": bal_meta.get("valid_count") or 0,
                "optimal": opt_meta.get("valid_count") or 0,
            },
            "displayed_count": {
                "essential": len(essential_o),
                "balanced": len(balanced_o),
                "optimal": len(optimal_o),
            },
            "filter_funnel": funnel,
            "constraint_failures": counts,
            "failures_by_nutrient": {
                "minimum": dict(min_fail_by_nutrient),
                "maximum": dict(max_fail_by_nutrient),
            },
            "example_rejections": example_rejections,
            "explorer": explorer_samples,
            "non_dominated_sample": [
                {"bundle_id": e["bundle_id"], "product_ids": e["product_ids"], "monthly_cost": e["monthly_cost"]}
                for e in non_dom[:20]
            ],
            "returned_options": {
                "essential": len(essential_o),
                "balanced": len(balanced_o),
                "optimal": len(optimal_o),
            },
            "ranking_rules": RANKING_RULES,
            "tier_semantics": TIER_SEMANTICS,
            "balanced_budget_status": bal_meta.get("budget_status"),
            "llm_used": False,
            "synthetic_demo_data": demo,
            "complete_diet_claim": False,
            "scoring_weights": SCORE_WEIGHTS,
            "requirement_source": REQUIREMENT_SOURCE,
            "dominance_is_display_filter": False,
        },
    }
