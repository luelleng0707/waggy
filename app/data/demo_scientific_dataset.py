"""SYNTHETIC demonstration product nutrient profiles.

Activated only with the demo catalog overlay. Values are NOT manufacturer
facts and NOT warehouse evidence.

    data_origin = "demo_synthetic"

Requirement numbers live in scientific_requirements.py (secondary AAFCO
summary). This module only describes DEMO COMMERCIAL product densities.
"""

from __future__ import annotations

from typing import Any

from app.data.scientific_requirements import (
    NUTRIENT_IDS,
    VITAMIN_D_MAX_IU_PER_KG_DM,
    build_requirement_profile,
    dog_size_band,
    life_stage_band,
)

SYNTHETIC_DEMO_FLAG = True
DATA_ORIGIN = "demo_synthetic"
REFERENCE_WEIGHT_KG = 30.0
# Back-compat alias used by existing tests.
SYNTHETIC_VITAMIN_D_MAX_IU_PER_KG_DM = VITAMIN_D_MAX_IU_PER_KG_DM

PCT_NUTRIENTS = (
    "protein_pct_dm",
    "fat_pct_dm",
    "calcium_pct_dm",
    "phosphorus_pct_dm",
    "magnesium_pct_dm",
    "potassium_pct_dm",
    "sodium_pct_dm",
    "chloride_pct_dm",
)
MG_NUTRIENTS = (
    "iron_mg_per_kg_dm",
    "copper_mg_per_kg_dm",
    "zinc_mg_per_kg_dm",
    "manganese_mg_per_kg_dm",
    "selenium_mg_per_kg_dm",
    "iodine_mg_per_kg_dm",
    "vitamin_b1_mg_per_kg_dm",
    "vitamin_b2_mg_per_kg_dm",
    "vitamin_b6_mg_per_kg_dm",
    "niacin_mg_per_kg_dm",
    "pantothenic_mg_per_kg_dm",
    "folic_mg_per_kg_dm",
    "choline_mg_per_kg_dm",
)
IU_NUTRIENTS = (
    "vitamin_a_iu_per_kg_dm",
    "vitamin_d_iu_per_kg_dm",
    "vitamin_e_iu_per_kg_dm",
)

# Map extra_per_serving keys → nutrient density ids.
EXTRA_TO_NUTRIENT = {
    "protein_g": "protein_pct_dm",
    "fat_g": "fat_pct_dm",
    "calcium_g": "calcium_pct_dm",
    "phosphorus_g": "phosphorus_pct_dm",
    "magnesium_g": "magnesium_pct_dm",
    "potassium_g": "potassium_pct_dm",
    "sodium_g": "sodium_pct_dm",
    "chloride_g": "chloride_pct_dm",
    "iron_mg": "iron_mg_per_kg_dm",
    "copper_mg": "copper_mg_per_kg_dm",
    "zinc_mg": "zinc_mg_per_kg_dm",
    "manganese_mg": "manganese_mg_per_kg_dm",
    "selenium_mg": "selenium_mg_per_kg_dm",
    "iodine_mg": "iodine_mg_per_kg_dm",
    "vitamin_b1_mg": "vitamin_b1_mg_per_kg_dm",
    "vitamin_b2_mg": "vitamin_b2_mg_per_kg_dm",
    "vitamin_b6_mg": "vitamin_b6_mg_per_kg_dm",
    "niacin_mg": "niacin_mg_per_kg_dm",
    "pantothenic_mg": "pantothenic_mg_per_kg_dm",
    "folic_mg": "folic_mg_per_kg_dm",
    "choline_mg": "choline_mg_per_kg_dm",
    "vitamin_a_iu": "vitamin_a_iu_per_kg_dm",
    "vitamin_d_iu": "vitamin_d_iu_per_kg_dm",
    "vitamin_e_iu": "vitamin_e_iu_per_kg_dm",
}


def _staple(*, protein: float, fat: float, calcium: float, phosphorus: float, choline: float, vitamin_d: float, **more: Any) -> dict[str, Any]:
    row = {
        "ingestible": True,
        "role": "staple",
        "data_origin": DATA_ORIGIN,
        "serving_size_g": 400.0,
        "servings_per_day": 1.0,
        "moisture_percent": 25.0,
        "dry_matter_percent": 75.0,
        "kcal_per_serving": 1100.0,
        "pathways": ("staple", "nutrition"),
        "protein_pct_dm": protein,
        "fat_pct_dm": fat,
        "calcium_pct_dm": calcium,
        "phosphorus_pct_dm": phosphorus,
        "magnesium_pct_dm": 0.08,
        "potassium_pct_dm": 0.7,
        "sodium_pct_dm": 0.35,
        "chloride_pct_dm": 0.5,
        "iron_mg_per_kg_dm": 100.0,
        "copper_mg_per_kg_dm": 15.0,
        "zinc_mg_per_kg_dm": 120.0,
        "manganese_mg_per_kg_dm": 10.0,
        "selenium_mg_per_kg_dm": 0.4,
        "iodine_mg_per_kg_dm": 1.5,
        "vitamin_a_iu_per_kg_dm": 8000.0,
        "vitamin_d_iu_per_kg_dm": vitamin_d,
        "vitamin_e_iu_per_kg_dm": 60.0,
        "vitamin_b1_mg_per_kg_dm": 3.0,
        "vitamin_b2_mg_per_kg_dm": 6.0,
        "vitamin_b6_mg_per_kg_dm": 2.0,
        "niacin_mg_per_kg_dm": 16.0,
        "pantothenic_mg_per_kg_dm": 14.0,
        "folic_mg_per_kg_dm": 0.3,
        "choline_mg_per_kg_dm": choline,
        "extra_per_serving": {},
    }
    row.update(more)
    return row


def _support(*, role: str, pathways: tuple[str, ...], extras: dict[str, float] | None = None, ingestible: bool = True) -> dict[str, Any]:
    empty = {nid: None for nid in NUTRIENT_IDS}
    return {
        **empty,
        "ingestible": ingestible,
        "role": role,
        "data_origin": DATA_ORIGIN,
        "serving_size_g": 2.0 if ingestible else 0.0,
        "servings_per_day": 1.0,
        "moisture_percent": 0.0,
        "dry_matter_percent": 100.0 if ingestible else 0.0,
        "kcal_per_serving": 10.0 if ingestible else 0.0,
        "pathways": pathways,
        "extra_per_serving": extras or {},
    }


# Daily DM at 30 kg: 400 g as-fed × 75% = 300 g DM.
# SF001 vitamin D 1333.33 IU/kg × 0.3 kg = 400 IU/day (same as prior demo).
# SF002 1250 IU/kg × 0.3 kg = 375 IU/day.
# SF002 choline 1200 < 1360 so adult SF002-only fails choline minimum.
_DEMO_PRODUCT_NUTRIENTS: dict[str, dict[str, Any]] = {
    "SF001": _staple(protein=26.0, fat=10.0, calcium=1.4, phosphorus=1.1, choline=1500.0, vitamin_d=1333.3333),
    "SF002": _staple(
        protein=20.0,
        fat=9.0,
        calcium=0.8,
        phosphorus=0.6,
        choline=1200.0,
        vitamin_d=1250.0,
        sodium_pct_dm=0.12,
        chloride_pct_dm=0.2,
        iron_mg_per_kg_dm=45.0,
        copper_mg_per_kg_dm=8.0,
        zinc_mg_per_kg_dm=85.0,
        manganese_mg_per_kg_dm=5.5,
    ),
    "TR011": _support(role="care_support", pathways=("joint",)),
    "TR001": _support(role="care_support", pathways=("dental",)),
    "TR003": _support(
        role="care_support",
        pathways=("skin", "coat"),
        extras={"vitamin_d_iu": 800.0, "vitamin_e_iu": 40.0},
    ),
    "TR007": _support(
        role="nutritional_support",
        pathways=("nutrition",),
        extras={"vitamin_d_iu": 200.0, "choline_mg": 80.0, "vitamin_a_iu": 500.0},
    ),
    "TR008": _support(role="care_support", pathways=("digestive",)),
    "JB001": _support(
        role="care_support",
        pathways=("joint",),
        extras={"vitamin_d_iu": 120.0, "calcium_g": 0.15},
    ),
    "HY001": _support(role="care_support", pathways=("hydration",), extras={"sodium_g": 0.02}),
    "HG001": _support(role="hygiene", pathways=("hygiene",), ingestible=False),
    "SK001": _support(role="hygiene", pathways=("coat",), ingestible=False),
    "DN001": _support(role="hygiene", pathways=("dental",), ingestible=False),
}


def demo_product_nutrient(product_id: str) -> dict[str, Any] | None:
    row = _DEMO_PRODUCT_NUTRIENTS.get(str(product_id))
    if not row:
        return None
    return {
        **row,
        "synthetic_demo_data": SYNTHETIC_DEMO_FLAG,
        "data_origin": DATA_ORIGIN,
        "product_id": str(product_id),
        # Back-compat fields used by older tests / traces.
        "daily_dm_g": round(
            float(row.get("serving_size_g") or 0)
            * float(row.get("servings_per_day") or 0)
            * float(row.get("dry_matter_percent") or 0)
            / 100.0,
            4,
        ),
        "vitamin_d_iu_per_serving": float((row.get("extra_per_serving") or {}).get("vitamin_d_iu") or 0)
        + (
            float(row["vitamin_d_iu_per_kg_dm"])
            * (
                float(row.get("serving_size_g") or 0)
                * float(row.get("servings_per_day") or 0)
                * float(row.get("dry_matter_percent") or 0)
                / 100.0
                / 1000.0
            )
            if row.get("vitamin_d_iu_per_kg_dm") is not None
            else 0.0
        ),
    }


def serving_scale(weight_kg: float) -> float:
    return max(float(weight_kg), 0.5) / REFERENCE_WEIGHT_KG


def product_daily_contribution(product_id: str, weight_kg: float) -> dict[str, Any]:
    """Daily DM mass and nutrient amounts for one product at this body weight.

    Percent nutrients contribute grams/day = (% DM / 100) × daily_dm_g.
    Density nutrients contribute amount/day = density × daily_dm_kg.
    extra_per_serving is an absolute daily addend (scaled by servings × weight).
    """
    spec = demo_product_nutrient(product_id)
    if spec is None:
        return {
            "product_id": product_id,
            "status": "INSUFFICIENT_DATA",
            "daily_dm_g": 0.0,
            "daily_amounts": {},
            "data_origin": DATA_ORIGIN,
        }
    scale = serving_scale(weight_kg)
    ingestible = bool(spec.get("ingestible"))
    servings = float(spec.get("servings_per_day") or 0) * scale
    serving_g = float(spec.get("serving_size_g") or 0) * servings
    dm_frac = float(spec.get("dry_matter_percent") or 0) / 100.0
    daily_dm_g = serving_g * dm_frac if ingestible else 0.0
    daily_dm_kg = daily_dm_g / 1000.0
    amounts: dict[str, float] = {nid: 0.0 for nid in NUTRIENT_IDS}
    if ingestible:
        for nid in PCT_NUTRIENTS:
            pct = spec.get(nid)
            if pct is not None:
                amounts[nid] = float(pct) / 100.0 * daily_dm_g  # grams/day
        for nid in MG_NUTRIENTS:
            dens = spec.get(nid)
            if dens is not None:
                amounts[nid] = float(dens) * daily_dm_kg  # mg/day
        for nid in IU_NUTRIENTS:
            dens = spec.get(nid)
            if dens is not None:
                amounts[nid] = float(dens) * daily_dm_kg  # IU/day
        extras = spec.get("extra_per_serving") or {}
        for extra_key, nid in EXTRA_TO_NUTRIENT.items():
            extra = extras.get(extra_key)
            if extra:
                amounts[nid] = amounts.get(nid, 0.0) + float(extra) * servings
    return {
        "product_id": product_id,
        "role": spec.get("role"),
        "ingestible": ingestible,
        "pathways": list(spec.get("pathways") or []),
        "daily_dm_g": round(daily_dm_g, 6),
        "serving_g_as_fed": round(serving_g, 6),
        "servings": round(servings, 6),
        "daily_amounts": {k: round(v, 8) for k, v in amounts.items()},
        "synthetic_demo_data": True,
        "data_origin": DATA_ORIGIN,
        "status": "OK",
    }


def aggregate_contributions(contribs: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert summed daily amounts into diet DM densities for comparison."""
    total_dm_g = sum(float(c.get("daily_dm_g") or 0) for c in contribs)
    total_dm_kg = total_dm_g / 1000.0 if total_dm_g else 0.0
    summed: dict[str, float] = {nid: 0.0 for nid in NUTRIENT_IDS}
    for contrib in contribs:
        for nid, val in (contrib.get("daily_amounts") or {}).items():
            summed[nid] = summed.get(nid, 0.0) + float(val or 0)
    densities: dict[str, float | None] = {}
    conversion = {
        "pct_dm": "100 * sum(grams_per_day) / staple_and_ingestible_daily_dm_g",
        "mg_or_iu_per_kg_dm": "sum(amount_per_day) / (daily_dm_g / 1000)",
        "as_fed_percent_not_added": True,
        "weight_scale": f"servings × (weight_kg / {REFERENCE_WEIGHT_KG})",
        "synthetic_demo_data": True,
        "data_origin": DATA_ORIGIN,
    }
    if total_dm_g <= 0:
        for nid in NUTRIENT_IDS:
            densities[nid] = None
    else:
        for nid in PCT_NUTRIENTS:
            densities[nid] = round(100.0 * summed[nid] / total_dm_g, 6)
        for nid in MG_NUTRIENTS + IU_NUTRIENTS:
            densities[nid] = round(summed[nid] / total_dm_kg, 6)
    return {
        "basis": "dry_matter_diet_density",
        "synthetic_demo_data": True,
        "data_origin": DATA_ORIGIN,
        "staple_daily_dm_g": round(total_dm_g, 6),
        "daily_dm_g": round(total_dm_g, 6),
        "daily_amounts": {k: round(v, 8) for k, v in summed.items()},
        "densities": densities,
        "conversion": conversion,
        "per_product": contribs,
        # Back-compat keys for tests that read totals["protein_pct_dm"]
        **{nid: densities.get(nid) for nid in NUTRIENT_IDS},
    }


def build_demo_requirement_profile(*, weight_kg: float, age_years: float) -> dict[str, Any]:
    profile = build_requirement_profile(weight_kg=weight_kg, age_years=age_years)
    profile["synthetic_demo_product_data"] = True
    profile["product_data_origin"] = DATA_ORIGIN
    return profile
