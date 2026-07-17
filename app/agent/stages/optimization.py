"""Stage 6 & 7: inventory knapsack matching and feeding-plan optimization."""

from __future__ import annotations

import logging
import re
from typing import Any

import pandas as pd

from app.agent.state import (
    ActiveIntervention,
    DogProfileInput,
    PipelineTraceEntry,
    ProductFulfillment,
    WellnessReportPayload,
)
from app.agent.utils import (
    DataRepository,
    calculate_unit_economics,
    canonical_key,
    feeding_rule_for_product,
    ingredient_key,
    units_compatible,
)

logger = logging.getLogger(__name__)

LEGACY_MOCK_PATTERN = re.compile(r"^(SF00[1-5]|SP00[1-8]|TR00[1-2])$", re.I)


def _is_production_product_id(product_id: str) -> bool:
    return bool(product_id) and not LEGACY_MOCK_PATTERN.match(str(product_id))


INGREDIENT_ALIASES = {
    "omega_3": {"omega_3", "epa_dha"},
    "glucosamine": {"glucosamine", "joint_health_formula"},
    "probiotics": {"probiotics", "brady_yeast_probiotics"},
}


def _keys_match(target_key: str, component_key: str) -> bool:
    if target_key == component_key:
        return True
    for canonical, aliases in INGREDIENT_ALIASES.items():
        if target_key in aliases and component_key in aliases:
            return True
    return False


def _component_to_ingredient_key(name: str) -> str:
    key = ingredient_key(name.replace("+", "_").replace("EPA+DHA", "omega_3"))
    if key == "epa_dha":
        return "omega_3"
    if key == "joint_health_formula":
        return "glucosamine"
    if key == "brady_yeast_probiotics":
        return "probiotics"
    return key


def _active_components(components_df: pd.DataFrame) -> pd.DataFrame:
    if components_df.empty:
        return pd.DataFrame()
    active = components_df[components_df["component_type"] == "active_ingredient"].copy()
    active["ingredient_key"] = active["component_name"].map(_component_to_ingredient_key)
    active["amount_per_unit"] = pd.to_numeric(active["value"], errors="coerce").fillna(0.0)
    return active


def _match_products_for_target(
    target: dict[str, Any],
    catalog_df: pd.DataFrame,
    active_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    weight_kg: float,
) -> list[ProductFulfillment]:
    if active_df.empty or catalog_df.empty:
        return []

    target_key = target["ingredient_key"]
    matches = active_df[active_df["ingredient_key"].map(lambda k: _keys_match(target_key, k))]
    if matches.empty:
        return []

    fulfillments: list[ProductFulfillment] = []
    for _, comp in matches.iterrows():
        product_id = comp["product_id"]
        if not _is_production_product_id(product_id):
            continue
        if not units_compatible(target["dose_unit"], comp.get("unit", "")):
            continue

        amount = float(comp["amount_per_unit"])
        if amount <= 0:
            continue

        coverage = min(100.0, round((amount / target["target_daily_dose"]) * 100, 1))
        if coverage <= 0:
            continue

        catalog_row = catalog_df[catalog_df["product_id"] == product_id]
        if catalog_row.empty:
            continue

        product_name = catalog_row.iloc[0]["product_name"]
        purchase_url = catalog_row.iloc[0].get("purchase_url") or None
        feeding = feeding_rule_for_product(rules_df, product_id, weight_kg)
        standard_feeding = (
            f"{feeding['daily_amount']}{feeding['daily_unit']}/day"
            if feeding
            else "1 serving/day"
        )

        fulfillments.append(
            ProductFulfillment(
                product_id=product_id,
                product_name=product_name,
                standard_daily_feeding=standard_feeding,
                yielded_active_content=f"{amount}{comp.get('unit', '')} {comp['component_name']}",
                supplemental_boost_required=coverage < 70.0,
                therapeutic_shortfall=f"{max(0.0, target['target_daily_dose'] - amount)}{target['dose_unit']}"
                if coverage < 100.0
                else "0",
                purchase_url=purchase_url or None,
                unit_cost_per_bag=calculate_unit_economics(pricing_df, product_id),
                coverage_pct=coverage,
            )
        )

    fulfillments.sort(key=lambda f: f.coverage_pct, reverse=True)
    return fulfillments


def _build_wellness_reports(
    nutrition: dict[str, Any],
    catalog_df: pd.DataFrame,
    active_df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    rules_df: pd.DataFrame,
    profile: DogProfileInput,
) -> list[WellnessReportPayload]:
    reports: list[WellnessReportPayload] = []
    for target in nutrition.get("nutrient_targets", []):
        options = _match_products_for_target(
            target, catalog_df, active_df, pricing_df, rules_df, profile.weight_kg
        )
        best = options[0] if options else None
        fulfillment_map = {}
        if best:
            fulfillment_map[best.product_id] = best

        reports.append(
            WellnessReportPayload(
                condition=target["condition"],
                weighted_priority_score=float(target.get("weighted_priority_score", 0)),
                targeted_intervention=ActiveIntervention(
                    active_ingredient=target["ingredient_name"],
                    required_dosage=f"{target['target_daily_dose']}{target['dose_unit']}",
                    commercial_fulfillment=fulfillment_map,
                ),
            )
        )
    reports.sort(key=lambda r: r.weighted_priority_score, reverse=True)
    return reports


def _build_feeding_plan(
    reports: list[WellnessReportPayload],
    pricing_df: pd.DataFrame,
) -> dict[str, Any]:
    selected = []
    total_cost = 0.0
    seen_products: set[str] = set()

    for report in reports:
        for product_id, fulfillment in report.targeted_intervention.commercial_fulfillment.items():
            if product_id in seen_products:
                continue
            seen_products.add(product_id)
            unit_cost = fulfillment.unit_cost_per_bag or calculate_unit_economics(pricing_df, product_id)
            selected.append({
                "product_id": product_id,
                "product_name": fulfillment.product_name,
                "standard_daily_feeding": fulfillment.standard_daily_feeding,
                "unit_cost_per_bag": unit_cost,
            })
            total_cost += unit_cost

    return {
        "items": selected,
        "monthly_cost_rmb": round(total_cost, 2),
        "product_count": len(selected),
    }


def run_optimization_stage(
    repo: DataRepository,
    profile: DogProfileInput,
    nutrition: dict[str, Any],
) -> tuple[dict[str, Any], list[WellnessReportPayload], PipelineTraceEntry]:
    catalog_df = repo.product_catalog()
    components_df = repo.product_components()
    pricing_df = repo.product_pricing()
    rules_df = repo.product_feeding_rules()
    active_df = _active_components(components_df)

    reports = _build_wellness_reports(
        nutrition, catalog_df, active_df, pricing_df, rules_df, profile
    )
    feeding_plan = _build_feeding_plan(reports, pricing_df)

    fulfilled = sum(1 for r in reports if r.targeted_intervention.commercial_fulfillment)
    payload = {
        "wellness_reports": [r.model_dump() for r in reports],
        "feeding_plan": feeding_plan,
        "inventory_rows": len(catalog_df),
        "active_component_rows": len(active_df),
        "fulfilled_interventions": fulfilled,
    }

    trace = PipelineTraceEntry(
        stage="optimization",
        message="Matched nutrient targets against real inventory with unit economics",
        record_count=len(reports),
        metadata={
            "fulfilled": fulfilled,
            "monthly_cost_rmb": feeding_plan["monthly_cost_rmb"],
        },
    )
    logger.info(
        "[Stage 6-7] optimization reports=%s fulfilled=%s monthly_cost=%s",
        len(reports),
        fulfilled,
        feeding_plan["monthly_cost_rmb"],
    )
    return payload, reports, trace
