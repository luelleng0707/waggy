"""Shared read-only adapter for customer/business/developer presentations."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.data.demo_catalog import demo_mode_enabled

CANONICAL_PIPELINE_STAGES = (
    "INPUT",
    "PROFILE_NORMALIZE_V2_1",
    "BREED_RESOLVE_V2_1",
    "TRAIT_BLEND_V2_1",
    "RISK_V2_1",
    "NUTRIENT_TARGET_V2_1",
    "ACTIVITY_V2_1",
    "PRODUCT_MATCH_V2_1",
    "PACKAGE_OPTIMIZER_V2_1",
    "EVIDENCE_RANK_V2_1",
    "VALIDATION_V2_1",
    "OUTPUT",
)

NA = "NOT AVAILABLE FROM RUNTIME"

_TIMING_KEYS = frozenset(
    {
        "elapsed_ms",
        "timing_ms",
        "timing",
        "assembly_ms",
        "stage_timings_ms",
        "total_ms",
        "total_pipeline",
    }
)


def _without_runtime_timing(value: Any) -> Any:
    """Drop wall-clock timing so analysis_signature is scientific, not request-duration."""
    if isinstance(value, dict):
        return {
            key: _without_runtime_timing(item)
            for key, item in value.items()
            if key not in _TIMING_KEYS
        }
    if isinstance(value, list):
        return [_without_runtime_timing(item) for item in value]
    return value


def analysis_signature(analyze: dict[str, Any]) -> str:
    """Stable signature proving all surfaces came from one analysis payload.

    Timing / elapsed_ms fields are metadata and must not change scientific identity.
    """
    payload = _without_runtime_timing(
        {
            "profile": analyze.get("profile"),
            "healthInsights": analyze.get("healthInsights"),
            "nutritionalTargets": analyze.get("nutritionalTargets"),
            "productRecommendations": analyze.get("productRecommendations"),
            "wellnessPackages": analyze.get("wellnessPackages"),
            "scientificEvidence": analyze.get("scientificEvidence"),
        }
    )
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def runtime_or_na(value: Any) -> Any:
    if value is None or value == "":
        return NA
    if value == [] or value == {}:
        return NA
    return value


def package_product_rows(pkg: dict[str, Any]) -> list[dict[str, Any]]:
    """Preserve optimizer composition. Prefer products_included, then product_cards."""
    raw = pkg.get("products_included")
    if not isinstance(raw, list) or not raw:
        raw = pkg.get("product_cards")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def project_package_product(item: dict[str, Any]) -> dict[str, Any]:
    yearly_plan = item.get("yearly_plan") if isinstance(item.get("yearly_plan"), dict) else {}
    daily = (
        yearly_plan.get("daily_serving")
        or item.get("daily_amount")
        or item.get("serving_size")
        or item.get("serving")
        or item.get("daily_serving")
    )
    packages_needed = yearly_plan.get("packages_needed")
    monthly_quantity = item.get("monthly_quantity")
    return {
        "product_id": runtime_or_na(item.get("product_id")),
        "name": runtime_or_na(item.get("name") or item.get("product_name")),
        "brand": runtime_or_na(item.get("brand")),
        "category": runtime_or_na(item.get("category") or item.get("type") or item.get("subcategory")),
        "quantity": runtime_or_na(monthly_quantity or daily),
        "consumption": {
            "daily_serving": runtime_or_na(daily),
            "monthly_quantity": runtime_or_na(monthly_quantity),
            "packages_needed": runtime_or_na(packages_needed),
        },
        "list_price": runtime_or_na(item.get("price") or item.get("list_price_rmb")),
        "monthly_cost": runtime_or_na(item.get("monthly_cost")),
        "yearly_cost": runtime_or_na(item.get("yearly_cost")),
        "why_selected": runtime_or_na(item.get("why_selected") or item.get("reason")),
        "selection_reasons": runtime_or_na(item.get("selection_reasons")),
    }


def project_package_economics(pkg: dict[str, Any]) -> dict[str, Any]:
    monthly = pkg.get("monthly_cost")
    yearly = pkg.get("yearly_cost")
    discount_factor = pkg.get("yearly_discount_factor")
    savings: Any = NA
    discount_percent: Any = NA
    regular_yearly: Any = NA
    try:
        if monthly is not None and yearly is not None:
            savings = round(float(monthly) * 12.0 - float(yearly), 2)
        if discount_factor is not None:
            factor = float(discount_factor)
            discount_percent = round((1.0 - factor) * 100.0, 2)
            if yearly is not None and factor:
                regular_yearly = round(float(yearly) / factor, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return {
        "monthly_cost": runtime_or_na(monthly),
        "yearly_cost": runtime_or_na(yearly),
        "regular_yearly_cost": regular_yearly,
        "savings": savings,
        "discount_percent": discount_percent,
        "yearly_discount_factor": runtime_or_na(discount_factor),
    }


def project_package_composition(pkg: dict[str, Any]) -> dict[str, Any]:
    rows = package_product_rows(pkg)
    economics = project_package_economics(pkg)
    return {
        "tier": pkg.get("tier") or pkg.get("package_id"),
        "package_id": pkg.get("package_id") or pkg.get("tier"),
        "title": runtime_or_na(pkg.get("title")),
        "purpose": runtime_or_na(
            pkg.get("best_for") or pkg.get("tagline") or pkg.get("why_fits") or pkg.get("package_summary")
        ),
        "recommended": bool(pkg.get("recommended")),
        "composition_status": "AVAILABLE" if rows else NA,
        "products": [project_package_product(item) for item in rows],
        "coverage_score": runtime_or_na(pkg.get("coverage_score")),
        **economics,
    }


def project_recommended_product(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_id": runtime_or_na(item.get("product_id")),
        "name": runtime_or_na(item.get("product_name") or item.get("name")),
        "brand": runtime_or_na(item.get("brand")),
        "category": runtime_or_na(item.get("category") or item.get("product_type") or item.get("type")),
        "reason": runtime_or_na(item.get("why_selected") or item.get("reason") or item.get("short_description")),
        "price": runtime_or_na(item.get("price") or item.get("list_price_rmb")),
        "monthly_cost": runtime_or_na(
            item.get("monthly_cost") or item.get("monthly_cost_estimate") or item.get("unit_cost")
        ),
        "serving": runtime_or_na(item.get("serving_size") or item.get("serving") or item.get("daily_amount")),
    }


_CUSTOMER_BUSINESS_PACKAGE_DROP = {
    "formula_execution",
    "observatory",
    "coverage_matrix",
    "optimizer_provenance",
    "requirement_profile",
    "package_options",
    "_search_envelope",
}

_CUSTOMER_INTERNAL_KEYS = {
    "formula_execution",
    "independent_of_product_match",
    "build_optimized_packages",
}

_HTTP_ANALYZE_DROP = {
    "debug",
    "packageDetails",
    "wellnessPackages",
}


def _strip_internal_keys(obj: Any, keys: set[str] = _CUSTOMER_INTERNAL_KEYS) -> Any:
    """Drop developer-only keys from a customer/business copy. Does not mutate analyze."""
    if isinstance(obj, dict):
        return {key: _strip_internal_keys(value, keys) for key, value in obj.items() if key not in keys}
    if isinstance(obj, list):
        return [_strip_internal_keys(item, keys) for item in obj]
    return obj


def _http_analyze_view(analyze: dict[str, Any]) -> dict[str, Any]:
    """Workbench HTTP envelope. Keeps version/profile/raw extraction fields; drops huge internals."""
    return {key: value for key, value in analyze.items() if key not in _HTTP_ANALYZE_DROP}


def _surface_safe_packages(packages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    safe = []
    for pkg in packages:
        row = {key: value for key, value in pkg.items() if key not in _CUSTOMER_BUSINESS_PACKAGE_DROP}
        safe.append(row)
    return safe


def _wellness_packages(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    packages = analyze.get("wellnessPackages") or []
    return [pkg for pkg in packages if isinstance(pkg, dict)]


def _product_recommendations(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    products = analyze.get("productRecommendations") or analyze.get("products") or []
    return [item for item in products if isinstance(item, dict)]


def _customer_nutrition_facts(ev: dict[str, Any]) -> list[dict[str, Any]]:
    facts = []
    for row in ev.get("nutrition_facts") or ev.get("nutrient_rows") or []:
        if not isinstance(row, dict):
            continue
        facts.append(
            {
                "nutrient": row.get("nutrient"),
                "nutrient_id": row.get("nutrient_id") or row.get("nutrient"),
                "display": row.get("display") or row.get("nutrient_name") or row.get("nutrient"),
                "unit": row.get("unit"),
                "daily_unit": row.get("daily_unit"),
                "actual": row.get("actual"),
                "actual_density_dm": row.get("actual_density_dm", row.get("actual")),
                "actual_per_day": row.get("actual_per_day", row.get("daily_amount")),
                "daily_amount": row.get("daily_amount"),
                "required_density_min_dm": row.get("required_density_min_dm", row.get("required_minimum")),
                "required_daily_min": row.get("required_daily_min", row.get("daily_minimum_equivalent")),
                "required_minimum": row.get("required_minimum"),
                "maximum_density_dm": row.get("maximum_density_dm", row.get("allowed_maximum")),
                "maximum_daily_amount": row.get("maximum_daily_amount", row.get("daily_maximum_equivalent")),
                "allowed_maximum": row.get("allowed_maximum"),
                "maximum_specified": row.get("maximum_specified"),
                "percent_of_minimum": row.get("percent_of_minimum"),
                "percent_of_maximum": row.get("percent_of_maximum"),
                "headroom_to_maximum": row.get("headroom_to_maximum", row.get("maximum_margin")),
                "daily_dm_g": row.get("daily_dm_g"),
                "daily_dm_kg": row.get("daily_dm_kg"),
                "basis": row.get("basis"),
                "kind": row.get("kind"),
                "status": row.get("status"),
                "status_label": row.get("status_label"),
                "maximum_copy": row.get("maximum_copy"),
                "minimum_copy": row.get("minimum_copy"),
                "minimum_status": row.get("minimum_status"),
                "maximum_status": row.get("maximum_status"),
                "star": bool(row.get("star") or row.get("breed_recommended")),
                "breed_recommended": bool(row.get("breed_recommended") or row.get("star")),
                "breed_recommendation_reason": row.get("breed_recommendation_reason"),
                "source_type": row.get("source_type"),
                "source_reference": row.get("source_reference"),
                "source": row.get("source"),
                "requirement_label": "Required for modeled daily ration",
                "density_label": "Source requirement is nutrient density per kg dry matter",
            }
        )
    return facts


def _customer_products(ev: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for item in ev.get("products") or []:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "product_id": item.get("product_id"),
                "product_name": item.get("product_name") or item.get("name"),
                "brand": item.get("brand"),
                "category": item.get("category"),
                "short_description": item.get("short_description"),
                "primary_function": item.get("primary_function"),
                "role": item.get("role"),
                "daily_amount": item.get("daily_amount"),
                "daily_dm_g": item.get("daily_dm_g"),
                "monthly_cost": item.get("monthly_cost"),
                "selection_reason": item.get("selection_reason"),
                "care_pathways": item.get("care_pathways") or [],
                "nutrient_contributions": item.get("nutrient_contributions") or {},
            }
        )
    if out:
        return out
    for item in ev.get("product_provenance") or []:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "product_id": item.get("product_id"),
                "product_name": item.get("product_name") or item.get("name"),
                "role": item.get("role"),
                "selection_reason": item.get("selection_reason"),
                "care_pathways": item.get("care_pathways") or [],
                "nutrient_contributions": item.get("nutrient_contributions") or {},
            }
        )
    return out


def _search_stats(analyze: dict[str, Any]) -> dict[str, Any]:
    p = _optimizer_provenance(analyze)
    return {
        "algorithm": p.get("algorithm") or "PACKAGE_OPTIMIZER_V2_1",
        "search_method": p.get("search_method"),
        "candidate_count": p.get("candidate_count"),
        "total_possible_subsets": p.get("total_possible_subsets"),
        "evaluated_count": p.get("evaluated_count"),
        "structurally_eligible": p.get("structurally_eligible"),
        "valid_count": p.get("valid_count"),
        "rejected_count": p.get("rejected_count"),
        "non_dominated_count": p.get("non_dominated_count"),
        "tier_valid_counts": p.get("tier_valid_counts") or {},
        "displayed_count": p.get("displayed_count") or p.get("returned_options") or {},
        "display_limit": p.get("display_limit") or p.get("top_n"),
        "constraint_failures": p.get("constraint_failures") or {},
        "failures_by_nutrient": p.get("failures_by_nutrient") or {},
        "ranking_rules": p.get("ranking_rules") or {},
        "tier_semantics": p.get("tier_semantics") or {},
        "dominance_is_display_filter": bool(p.get("dominance_is_display_filter")),
        "llm_used": False,
        "synthetic_demo_data": p.get("synthetic_demo_data"),
        "complete_diet_claim": False,
    }


def project_customer_bundle_option(ev: dict[str, Any]) -> dict[str, Any]:
    facts = _customer_nutrition_facts(ev)
    return {
        "bundle_id": ev.get("bundle_id"),
        "tier": ev.get("tier"),
        "rank": ev.get("rank"),
        "rank_among_valid": ev.get("rank_among_valid"),
        "product_ids": ev.get("product_ids") or [],
        "product_count": ev.get("product_count"),
        "products": _customer_products(ev),
        "monthly_cost": ev.get("monthly_cost"),
        "annual_cost": ev.get("annual_cost"),
        "constraint_status": ev.get("constraint_status"),
        "care_pathways": ev.get("care_pathways") or [],
        "care_coverage_score": ev.get("care_coverage_score"),
        "nutrition_balance_score": ev.get("nutrition_balance_score"),
        "overall_score": ev.get("overall_score"),
        "why_selected": ev.get("why_selected") or [],
        "why_ranked": ev.get("why_ranked") or [],
        "why_ranked_here": ev.get("why_ranked_here"),
        "why_outranked": ev.get("why_outranked") or [],
        "bundle_reasoning": ev.get("bundle_reasoning") or {},
        "preventative_pathways": ev.get("preventative_pathways") or [],
        "display_product_names": ev.get("display_product_names")
        or [
            str(item.get("product_name") or item.get("name"))
            for item in _customer_products(ev)
            if item.get("product_name") or item.get("name")
        ],
        "ranking_rule": ev.get("ranking_rule"),
        "score": ev.get("overall_score"),
        "score_components": ev.get("score_components") or {},
        "score_breakdown": ev.get("score_components") or {},
        "budget_fit": ev.get("budget_status") == "WITHIN_BUDGET",
        "budget_status": ev.get("budget_status"),
        "minimums_passed": ev.get("minimums_passed"),
        "minimums_total": ev.get("minimums_total"),
        "maximums_passed": ev.get("maximums_passed"),
        "maximums_total": ev.get("maximums_total"),
        "nutrient_coverage_percent": ev.get("nutrient_coverage_percent"),
        "coverage_summary": ev.get("coverage_summary") or {},
        "nutrition_facts": facts,
        "nutrition_ledger": {
            "nutrients": facts,
            "daily_dm_g": ev.get("daily_dm_g"),
            "daily_dm_kg": ev.get("daily_dm_kg"),
            "basis": "dry_matter_diet_density",
            "daily_requirement_note": (ev.get("nutrition_ledger") or {}).get("daily_requirement_note"),
        },
        "daily_dm_g": ev.get("daily_dm_g"),
        "daily_dm_kg": ev.get("daily_dm_kg"),
        "breed_recommendations": ev.get("breed_recommendations") or [],
        "claim": ev.get("requirement_profile", {}).get("claim_wording")
        or "Meets modeled baseline nutrient constraints.",
        "complete_diet_claim": False,
        "synthetic_demo_data": ev.get("synthetic_demo_data"),
        "optimizer_version": ev.get("optimizer_version") or "PACKAGE_OPTIMIZER_V2_1",
        "search_provenance": ev.get("search_provenance") or {},
        "tier_valid_count": ev.get("tier_valid_count"),
        "displayed_count": ev.get("displayed_count"),
    }


def project_developer_bundle_option(ev: dict[str, Any]) -> dict[str, Any]:
    return {
        **project_customer_bundle_option(ev),
        "nutrient_totals": ev.get("nutrient_totals") or {},
        "nutrient_rows": ev.get("nutrient_rows") or [],
        "failed_minimums": ev.get("failed_minimums") or [],
        "exceeded_maximums": ev.get("exceeded_maximums") or [],
        "product_provenance": ev.get("product_provenance") or [],
        "why_not_included": ev.get("why_not_included") or [],
        "requirement_profile": ev.get("requirement_profile") or {},
        "scoring_weights": ev.get("scoring_weights") or {},
        "synthetic_demo_data": ev.get("synthetic_demo_data"),
        "product_data_origin": ev.get("product_data_origin"),
        "rank": ev.get("rank"),
    }


def _package_options(analyze: dict[str, Any], *, developer: bool = False) -> dict[str, list[dict[str, Any]]]:
    raw = analyze.get("packageOptions") or {}
    projector = project_developer_bundle_option if developer else project_customer_bundle_option
    out: dict[str, list[dict[str, Any]]] = {}
    for tier in ("essential", "balanced", "optimal"):
        rows = raw.get(tier) or []
        out[tier] = [projector(ev) for ev in rows if isinstance(ev, dict)]
    return out


def _optimizer_provenance(analyze: dict[str, Any]) -> dict[str, Any]:
    return analyze.get("optimizerProvenance") or {}


def _preventative_briefing(analyze: dict[str, Any]) -> dict[str, Any]:
    care = analyze.get("careModel") or {}
    profile = analyze.get("profile") or analyze.get("pet") or {}
    req = analyze.get("requirementProfile") or {}
    return {
        "title": "WHY BALANCED CARE?",
        "dog_name": profile.get("pet_name") or profile.get("name"),
        "breeds": profile.get("breeds") or [],
        "life_stage": req.get("life_stage"),
        "pathways": care.get("pathway_briefs") or [],
        "disclaimer": care.get("disclaimer")
        or "These are preventative considerations — they do not mean the dog currently has these conditions.",
        "evidence_status": care.get("label") or care.get("evidence_status"),
        "demo_synthetic": bool(care.get("demo_synthetic")),
        "diagnosis_claim": False,
        "warehouse_evidence": bool(care.get("warehouse_evidence")),
        "health_analysis_anchor": "#health-analysis",
        "health_analysis_label": "View Health Analysis →",
    }


def _health_analysis(analyze: dict[str, Any]) -> dict[str, Any]:
    care = analyze.get("careModel") or {}
    warehouse_note = "Not available from current scientific warehouse."
    findings: list[dict[str, Any]] = []
    records = care.get("condition_records") or []
    if not records:
        for brief in care.get("pathway_briefs") or []:
            if isinstance(brief, dict):
                records = records or brief.get("condition_records") or []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        prev = rec.get("prevalence") or {}
        findings.append(
            {
                "condition": rec.get("condition"),
                "label": rec.get("label") or rec.get("condition"),
                "pathway": rec.get("pathway"),
                "breeds": rec.get("breeds") or [],
                "why_this_matters": rec.get("why_this_matters"),
                "observed_prevalence": prev.get("observed") or warehouse_note,
                "observed_by_breed": prev.get("observed_by_breed") or [],
                "estimated_prevalence": prev.get("estimated") or "NOT_AVAILABLE",
                "estimated_associations": prev.get("estimated_associations") or [],
                "evidence": rec.get("evidence") or [],
                "paper_name": rec.get("paper_name"),
                "scientific_quote": rec.get("scientific_quote"),
                "paper_link": rec.get("paper_link"),
                "publication_year": rec.get("publication_year"),
                "preventative_implication": rec.get("preventative_implication"),
                "preventative_targets": rec.get("preventative_targets") or [],
                "warehouse_evidence": True,
                "diagnosis_claim": False,
            }
        )
    mixed = [item for item in (care.get("mixed_breed_flagged") or []) if isinstance(item, dict)]
    insights = [item for item in (analyze.get("healthInsights") or []) if isinstance(item, dict)]
    return {
        "anchor": "health-analysis",
        "title": "Health Analysis",
        "warehouse_status": "Warehouse evidence present" if care.get("warehouse_evidence") else warehouse_note,
        "diagnosis_claim": False,
        "disclaimer": care.get("disclaimer")
        or "These are preventative considerations. They do not mean your dog currently has these conditions.",
        "findings": findings,
        "mixed_breed_flagged": mixed,
        "insights": insights,
        "demo_synthetic": False,
        "care_model_label": care.get("label") or care.get("evidence_status"),
    }


def _recommended_products_for_surface(
    products: list[dict[str, Any]],
    composition: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recommended = [project_recommended_product(item) for item in products]
    if recommended:
        return recommended
    seen: set[str] = set()
    fallback: list[dict[str, Any]] = []
    for pkg in composition:
        for item in pkg.get("products") or []:
            pid = str(item.get("product_id") or "")
            if pid and pid in seen:
                continue
            if pid:
                seen.add(pid)
            fallback.append(item)
    return fallback


def build_customer_presentation(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    profile = analyze.get("profile") or analyze.get("pet") or {}
    products = _product_recommendations(analyze)
    packages = _wellness_packages(analyze)
    surface_packages = _surface_safe_packages(packages)
    composition = [project_package_composition(pkg) for pkg in packages]
    monthly = analyze.get("monthly_plan") or {}
    yearly = analyze.get("yearly_plan") or {}
    health = analyze.get("healthInsights") or []
    nutrition = analyze.get("nutritionalTargets") or []
    activity = analyze.get("activityRecommendations") or {}
    grooming = analyze.get("groomer") or {}
    payload = {
        "surface": "customer",
        "demo_catalog": demo_mode_enabled(),
        "dog": {
            "name": runtime_or_na(profile.get("pet_name") or profile.get("name")),
            "breeds": profile.get("breeds") or [],
            "weight_kg": runtime_or_na(profile.get("weight_kg")),
            "age_years": runtime_or_na(profile.get("age_years")),
            "life_stage": runtime_or_na((analyze.get("requirementProfile") or {}).get("life_stage")),
            "activity_level": runtime_or_na(profile.get("activity_level")),
        },
        "wellness": {
            "health_insights": health,
            "nutrition_targets": nutrition,
            "activity": activity if activity else NA,
            "grooming": grooming if grooming else NA,
            "products": products,
            "recommended_products": _recommended_products_for_surface(products, composition),
            "packages": surface_packages,
            "package_composition": composition,
            "package_options": _package_options(analyze, developer=False),
            "package_search": _search_stats(analyze),
            "monthly_plan": monthly if monthly else NA,
            "yearly_plan": yearly if yearly else NA,
            "evidence": analyze.get("scientificEvidence") or [],
        },
        "preventative_briefing": _preventative_briefing(analyze),
        "health_analysis": _health_analysis(analyze),
        "assessment_summary": (assessment or {}).get("summary") or {},
        "scientific_boundary": {
            "matcher_available": bool(products),
            "catalog_source": "demo" if demo_mode_enabled() else "warehouse",
            "science_status": (
                "SCIENCE AVAILABLE" if products else "SCIENTIFIC PRODUCT MATCHING UNAVAILABLE"
            ),
            "science_copy": (
                "Scientific product matching produced recommendations from nutrient targets."
                if products
                else "Scientific product matching unavailable in demo runtime."
            ),
            "package_copy": (
                "Care bundles enumerated from the demo catalog and ranked after hard nutrient constraints. "
                "They meet modeled baseline nutrient constraints; they are not a guaranteed complete diet."
                if demo_mode_enabled()
                else "Care packages algorithmically composed from the active commercial catalog."
            ),
        },
    }
    return _strip_internal_keys(payload)


def build_business_presentation(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    products = _product_recommendations(analyze)
    packages = _wellness_packages(analyze)
    surface_packages = _surface_safe_packages(packages)
    monthly = analyze.get("monthly_plan") or {}
    yearly = analyze.get("yearly_plan") or {}
    health = analyze.get("healthInsights") or []
    composition = [project_package_composition(pkg) for pkg in packages]
    recommended = _recommended_products_for_surface(products, composition)
    brands = sorted(
        {
            str(item.get("brand"))
            for item in products
            if item.get("brand")
        }
        | {
            str(prod.get("brand"))
            for pkg in packages
            for prod in package_product_rows(pkg)
            if prod.get("brand")
        }
    )
    categories = sorted(
        {
            str(item.get("category") or item.get("product_type") or item.get("type"))
            for item in products
            if item.get("category") or item.get("product_type") or item.get("type")
        }
        | {
            str(prod.get("category") or prod.get("type"))
            for pkg in packages
            for prod in package_product_rows(pkg)
            if prod.get("category") or prod.get("type")
        }
    )
    return {
        "surface": "business",
        "demo_catalog": demo_mode_enabled(),
        "overview": {
            "dogs_analyzed": 1,
            "priority_health_opportunities": len(health),
            "product_count": len(recommended) or len(products),
            "package_count": len(packages),
            "evidence_count": len(analyze.get("scientificEvidence") or []),
            "estimated_business_opportunity": runtime_or_na(monthly.get("total_cost") if isinstance(monthly, dict) else None),
        },
        "portfolio": {
            "products": products,
            "recommended_products": recommended,
            "packages": surface_packages,
            "package_composition": composition,
            "package_options": _package_options(analyze, developer=False),
            "package_search": _search_stats(analyze),
            "brands": brands or NA,
            "categories": categories or NA,
            "product_gaps": NA,
            "portfolio_expansion": NA,
        },
        "health_opportunities": [
            {
                "condition": item.get("title") or item.get("condition"),
                "observed_prevalence": item.get("observed_breed_prevalence_percent")
                if item.get("observed_breed_prevalence_percent") is not None
                else NA,
                "estimated_prevalence": item.get("biological_risk_percent")
                if item.get("biological_risk_percent") is not None
                else NA,
                "evidence_status": "AVAILABLE"
                if item.get("evidence_count") or item.get("source_count")
                else NA,
                "breed_relevance": item.get("breed_relevance") or NA,
                "business_relevance": item.get("priority_score") or NA,
            }
            for item in health
            if isinstance(item, dict)
        ],
        "financial_model": {
            "monthly_total": runtime_or_na(monthly.get("total_cost") if isinstance(monthly, dict) else None),
            "yearly_total": runtime_or_na(yearly.get("total_cost") if isinstance(yearly, dict) else None),
            "discount": runtime_or_na(
                (monthly.get("discount") if isinstance(monthly, dict) else None)
                or (yearly.get("discount") if isinstance(yearly, dict) else None)
            ),
            "margin": NA,
            "recurring_price": runtime_or_na(
                monthly.get("monthly_equivalent") if isinstance(monthly, dict) else None
            ),
            "package_pricing": [
                {
                    "tier": pkg.get("tier"),
                    "title": runtime_or_na(pkg.get("title")),
                    "composition_status": item.get("composition_status"),
                    "product_count": len(item.get("products") or []),
                    "monthly_cost": item.get("monthly_cost"),
                    "yearly_cost": item.get("yearly_cost"),
                    "savings": item.get("savings"),
                    "discount_percent": item.get("discount_percent"),
                    "products": item.get("products") or [],
                }
                for pkg, item in zip(packages, composition)
            ],
        },
        "preventative_briefing": _preventative_briefing(analyze),
        "health_analysis": _health_analysis(analyze),
        "assessment_summary": (assessment or {}).get("summary") or {},
        "commercial_dataset": {
            "loaded": False,
            "status": "Demo commercial dataset not loaded",
            "customer_snapshot": NA,
            "breed_distribution": NA,
            "package_adoption": NA,
            "sales": NA,
            "note": (
                "This view projects ONE analysis. Aggregate sales, customer counts, "
                "and adoption rates are not invented when no commercial dataset is loaded."
            ),
        },
    }


def _developer_package_trace(pkg: dict[str, Any]) -> dict[str, Any]:
    fx = pkg.get("formula_execution") if isinstance(pkg.get("formula_execution"), dict) else {}
    observatory = pkg.get("observatory") if isinstance(pkg.get("observatory"), dict) else {}
    rows = package_product_rows(pkg)
    return {
        "tier": pkg.get("tier"),
        "title": runtime_or_na(pkg.get("title")),
        "formula_id": runtime_or_na(fx.get("formula_id") or observatory.get("formula_id")),
        "stage": runtime_or_na(fx.get("stage")),
        "parameters": runtime_or_na(fx.get("inputs")),
        "dependencies": runtime_or_na(fx.get("dependencies") or observatory.get("code_file")),
        "selected_product_ids": observatory.get("selected_ids")
        or [item.get("product_id") for item in rows if item.get("product_id")]
        or NA,
        "products_included": rows or NA,
        "outputs": runtime_or_na(fx.get("outputs")),
        "provenance": runtime_or_na(fx.get("provenance")),
        "decisions": runtime_or_na(fx.get("decisions")),
    }


def _developer_product_trace(item: dict[str, Any]) -> dict[str, Any]:
    fx = item.get("formula_execution") if isinstance(item.get("formula_execution"), dict) else {}
    return {
        "product_id": runtime_or_na(item.get("product_id")),
        "name": runtime_or_na(item.get("product_name") or item.get("name")),
        "formula_id": runtime_or_na(fx.get("formula_id")),
        "brand": runtime_or_na(item.get("brand")),
        "category": runtime_or_na(item.get("category") or item.get("product_type")),
        "why_selected": runtime_or_na(item.get("why_selected")),
        "price": runtime_or_na(item.get("price")),
        "outputs": runtime_or_na(fx.get("outputs")),
    }


def build_developer_presentation(
    validation_console: dict[str, Any] | None,
    analyze: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doc = validation_console or {}
    analyze = analyze or {}
    products = _product_recommendations(analyze)
    packages = _wellness_packages(analyze)
    composition = [project_package_composition(pkg) for pkg in packages]
    selected_ids: list[str] = []
    for pkg in packages:
        for item in package_product_rows(pkg):
            pid = str(item.get("product_id") or "")
            if pid:
                selected_ids.append(pid)
    matcher_count = len(products)
    return {
        "surface": "developer",
        "demo_catalog": demo_mode_enabled(),
        "pipeline": list(CANONICAL_PIPELINE_STAGES),
        "catalog_input": {
            "source": "demo" if demo_mode_enabled() else "warehouse",
            "demo_catalog": demo_mode_enabled(),
            "product_match_count": matcher_count,
            "package_selected_ids": sorted(set(selected_ids)),
            "scientific_matcher_available": matcher_count > 0,
        },
        "summary": doc.get("execution_status_summary") or {},
        "execution_records": doc.get("execution_records") or doc.get("formula_executions") or [],
        "runtime_stage_flow": doc.get("runtime_stage_flow") or [],
        "product_match": {
            "source": "analyze.productRecommendations",
            "formula_id": "PRODUCT_MATCH_V2_1",
            "products": [_developer_product_trace(item) for item in products],
            "empty_means": (
                "No nutrient-target matcher recommendations. "
                "This does not imply package composition failed."
            ),
        },
        "package_optimization": {
            "source": "analyze.wellnessPackages",
            "formula_id": "PACKAGE_OPTIMIZER_V2_1",
            "code_file": "app/agent/package_optimizer.py",
            "function": "build_optimized_packages",
            "catalog_loader": "load_candidate_products",
            "consumes": "active commercial catalog",
            "does_not_consume": "analyze.productRecommendations",
            "independent_of_product_match": True,
            "mode": "combinatorial_constraint_search",
            "search": _optimizer_provenance(analyze),
            "package_options": _package_options(analyze, developer=True),
            "requirement_profile": analyze.get("requirementProfile") or {},
            "care_model": analyze.get("careModel") or {},
            "scoring_weights": analyze.get("scoringWeights") or {},
            "tier_budget": analyze.get("tierBudget") or {},
            "scientific_personalization": False if matcher_count == 0 else "partial",
            "scientific_boundary": (
                "PRODUCT_MATCH_V2_1 emits productRecommendations from nutrient targets. "
                "PACKAGE_OPTIMIZER_V2_1 selects packages from the active catalog even when "
                "productRecommendations is empty. Empty matcher output is commercial-input "
                "composition, not scientific personalization."
            ),
            "packages": [_developer_package_trace(pkg) for pkg in packages],
            "composition": composition,
        },
        "validation": runtime_or_na(doc.get("validation") or doc.get("validation_console")),
        "evidence": runtime_or_na(doc.get("evidence")),
    }


def build_three_surface_presentations(
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    validation_console: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    signature = analysis_signature(analyze)
    return {
        "schema": "three_surface_presentation.v1",
        "analysis_signature": signature,
        "presentation_correlation_id": correlation_id or NA,
        "demo_catalog": demo_mode_enabled(),
        "catalog_source": "demo" if demo_mode_enabled() else "warehouse",
        "customer": build_customer_presentation(analyze, assessment),
        "business": build_business_presentation(analyze, assessment),
        "developer": build_developer_presentation(validation_console, analyze),
    }


def build_groomer_presentation(
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    role_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Staff projection of the same analyze payload. Does not re-optimize packages."""
    profile = analyze.get("profile") or analyze.get("pet") or {}
    packages = _wellness_packages(analyze)
    composition = [project_package_composition(pkg) for pkg in packages]
    recs = _product_recommendations(analyze)
    staff = (role_context or {}).get("groomer") if isinstance(role_context, dict) else {}
    staff = staff if isinstance(staff, dict) else {}
    recommended = next((pkg for pkg in composition if pkg.get("recommended")), composition[0] if composition else {})
    flags = []
    for item in analyze.get("healthInsights") or []:
        if isinstance(item, dict):
            flags.append(
                {
                    "title": runtime_or_na(item.get("title") or item.get("condition")),
                    "explanation": runtime_or_na(item.get("explanation") or item.get("why")),
                }
            )
    return {
        "surface": "groomer",
        "demo_catalog": demo_mode_enabled(),
        "dog": {
            "name": runtime_or_na(profile.get("pet_name") or profile.get("name")),
            "breeds": profile.get("breeds") or [],
            "weight_kg": runtime_or_na(profile.get("weight_kg")),
            "age_years": runtime_or_na(profile.get("age_years")),
            "sex": runtime_or_na(profile.get("sex") or profile.get("gender")),
            "activity_level": runtime_or_na(profile.get("activity_level")),
            "environment": runtime_or_na(profile.get("current_environment")),
            "observed_conditions": profile.get("observed_conditions") or analyze.get("observed_conditions") or [],
        },
        "observations": {
            "groomer_observations": runtime_or_na(staff.get("observations") or staff.get("notes")),
            "notes": runtime_or_na(staff.get("notes")),
            "source": "role_context.groomer — stored with the analysis request, not invented",
        },
        "findings": analyze.get("healthInsights") or [],
        "flags": flags or NA,
        "package_recommendation": recommended or NA,
        "package_composition": composition,
        "package_options": _package_options(analyze, developer=False),
        "package_search": _search_stats(analyze),
        "product_rationale": [
            {
                "product_id": item.get("product_id"),
                "name": item.get("name") or item.get("product_name"),
                "product_name": item.get("product_name") or item.get("name"),
                "why_selected": item.get("why_selected"),
            }
            for pkg in composition
            for item in (pkg.get("products") or [])
        ],
        "matcher_recommendations": recs,
        "preventative_briefing": _preventative_briefing(analyze),
        "health_analysis": _health_analysis(analyze),
        "assessment_summary": (assessment or {}).get("summary") or {},
        "follow_up": NA,
    }


def build_canonical_result(
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    *,
    correlation_id: str | None = None,
    role_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One analysis envelope. Projections must read this, not regenerate packages."""
    packages = _wellness_packages(analyze)
    recs = _product_recommendations(analyze)
    nutrition = analyze.get("nutritionalTargets") or []
    matcher_available = bool(recs)
    warnings: list[str] = []
    if not matcher_available:
        warnings.append("Scientific product matching unavailable: nutrient targets produced no matcher recommendations.")
    if demo_mode_enabled():
        warnings.append("Catalog source is the isolated DEMO CATALOG (synthetic commercial input).")
    composition = [project_package_composition(pkg) for pkg in packages]
    signature = analysis_signature(analyze)
    return {
        "schema": "canonical_analysis.v1",
        "analysis_id": signature,
        "correlation_id": correlation_id or NA,
        "input": {
            "dog_profile": analyze.get("profile") or analyze.get("pet") or {},
            "role_context": role_context or {},
        },
        "scientific_analysis": {
            "findings": analyze.get("healthInsights") or [],
            "nutrient_targets": nutrition,
            "evidence": analyze.get("scientificEvidence") or [],
            "warehouse_status": {
                "demo_catalog": demo_mode_enabled(),
                "matcher_available": matcher_available,
                "target_count": len(nutrition) if isinstance(nutrition, list) else 0,
            },
        },
        "product_matching": {
            "algorithm": "PRODUCT_MATCH_V2_1",
            "recommendations": recs,
            "limitations": (
                None
                if matcher_available
                else "No nutrient-target matcher recommendations. Packages are commercial catalog composition."
            ),
        },
        "package_optimization": {
            "algorithm": "PACKAGE_OPTIMIZER_V2_1",
            "code_file": "app/agent/package_optimizer.py",
            "function": "build_optimized_packages",
            "tiers": composition,
            "package_options": _package_options(analyze, developer=True),
            "search": _optimizer_provenance(analyze),
            "requirement_profile": analyze.get("requirementProfile") or {},
            "care_model": analyze.get("careModel") or {},
            "scoring_weights": analyze.get("scoringWeights") or {},
            "provenance": {
                "consumes": "active commercial catalog + labeled demo scientific dataset when enabled",
                "does_not_consume": "analyze.productRecommendations",
                "mode": "combinatorial_constraint_search",
                "search_method": (_optimizer_provenance(analyze) or {}).get("search_method"),
            },
        },
        "system": {
            "catalog_source": "demo" if demo_mode_enabled() else "warehouse",
            "demo_mode": demo_mode_enabled(),
            "warnings": warnings,
            "errors": [],
            "ai": {
                "package_membership": "deterministic PACKAGE_OPTIMIZER_V2_1",
                "llm_used": False,
                "explanation_layer": "optional POST /api/v1/ai/explain — not on the analysis path",
            },
        },
        "analyze": _http_analyze_view(analyze),
        "assessment_summary": (assessment or {}).get("summary") or {},
    }


def build_workbench_presentations(
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    validation_console: dict[str, Any] | None = None,
    correlation_id: str | None = None,
    role_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """ONE analysis → customer / groomer / business / developer projections."""
    three = build_three_surface_presentations(
        analyze,
        assessment,
        validation_console,
        correlation_id=correlation_id,
    )
    canonical = build_canonical_result(
        analyze,
        assessment,
        correlation_id=correlation_id,
        role_context=role_context,
    )
    developer = dict(three["developer"])
    developer["correlation_id"] = three["presentation_correlation_id"]
    developer["analysis_signature"] = three["analysis_signature"]
    return {
        "schema": "workbench_presentation.v1",
        "analysis_signature": three["analysis_signature"],
        "presentation_correlation_id": three["presentation_correlation_id"],
        "demo_catalog": three["demo_catalog"],
        "catalog_source": three["catalog_source"],
        "canonical": canonical,
        "roles": {
            "customer": three["customer"],
            "groomer": build_groomer_presentation(analyze, assessment, role_context),
            "business": three["business"],
            "developer": developer,
        },
    }
