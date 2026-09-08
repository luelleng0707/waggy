"""AAFCO-style nutrient requirements from a SECONDARY source citation.

These values summarize figures listed in project source material (PetMD-style
writeup of AAFCO nutrient profiles). They are NOT loaded from the scientific
warehouse and MUST NOT be presented as primary AAFCO tables or warehouse
evidence.

Senior-specific numeric minima are NOT_AVAILABLE in that source; adult
maintenance figures are reused with an explicit note.

Carbohydrate, fiber, and water are named as essential categories in the source
but have no numeric minima here → NOT_MODELED.
"""

from __future__ import annotations

from typing import Any

SOURCE = {
    "kind": "secondary_source",
    "standard": "AAFCO-style nutrient profiles",
    "source_type": "secondary_source",
    "label": "PetMD summary of AAFCO guidance (contextual citation)",
    "warehouse_authoritative": False,
    "primary_standard": False,
    "note": (
        "Numerical minima/maxima are transcribed from project source material "
        "that summarizes AAFCO-style complete-and-balanced commercial diet "
        "profiles. This is not a warehouse CSV and is not a primary AAFCO table."
    ),
}

# Exact figures from the provided secondary source. Do not invent extras.
# Keys: nutrient_id → (unit, basis, growth_min, growth_max, adult_min, adult_max)
# max=None means the source did not specify a maximum.
_PROFILE: dict[str, dict[str, Any]] = {
    "protein_pct_dm": {
        "display": "Protein",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 22.5,
        "growth_max": None,
        "adult_min": 18.0,
        "adult_max": None,
    },
    "fat_pct_dm": {
        "display": "Fat",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 8.5,
        "growth_max": None,
        "adult_min": 5.5,
        "adult_max": None,
    },
    "calcium_pct_dm": {
        "display": "Calcium",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 1.2,
        "growth_max": 2.5,
        "adult_min": 0.5,
        "adult_max": 2.5,
    },
    "phosphorus_pct_dm": {
        "display": "Phosphorus",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 1.0,
        "growth_max": 1.6,
        "adult_min": 0.4,
        "adult_max": 1.6,
    },
    "magnesium_pct_dm": {
        "display": "Magnesium",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 0.06,
        "growth_max": None,
        "adult_min": 0.06,
        "adult_max": None,
    },
    "potassium_pct_dm": {
        "display": "Potassium",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 0.6,
        "growth_max": None,
        "adult_min": 0.6,
        "adult_max": None,
    },
    "sodium_pct_dm": {
        "display": "Sodium",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 0.3,
        "growth_max": None,
        "adult_min": 0.08,
        "adult_max": None,
    },
    "chloride_pct_dm": {
        "display": "Chloride",
        "unit": "% DM",
        "basis": "percent_dry_matter",
        "kind": "pct_dm",
        "growth_min": 0.45,
        "growth_max": None,
        "adult_min": 0.12,
        "adult_max": None,
    },
    "iron_mg_per_kg_dm": {
        "display": "Iron",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 88.0,
        "growth_max": None,
        "adult_min": 40.0,
        "adult_max": None,
    },
    "copper_mg_per_kg_dm": {
        "display": "Copper",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 12.4,
        "growth_max": None,
        "adult_min": 7.3,
        "adult_max": None,
    },
    "zinc_mg_per_kg_dm": {
        "display": "Zinc",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 100.0,
        "growth_max": None,
        "adult_min": 80.0,
        "adult_max": None,
    },
    "manganese_mg_per_kg_dm": {
        "display": "Manganese",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 7.2,
        "growth_max": None,
        "adult_min": 5.0,
        "adult_max": None,
    },
    "selenium_mg_per_kg_dm": {
        "display": "Selenium",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 0.35,
        "growth_max": 2.0,
        "adult_min": 0.35,
        "adult_max": 2.0,
    },
    "iodine_mg_per_kg_dm": {
        "display": "Iodine",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 1.0,
        "growth_max": 11.0,
        "adult_min": 1.0,
        "adult_max": 11.0,
    },
    "vitamin_a_iu_per_kg_dm": {
        "display": "Vitamin A",
        "unit": "IU/kg DM",
        "basis": "iu_per_kg_dry_matter",
        "kind": "iu_kg_dm",
        "growth_min": 5000.0,
        "growth_max": 250000.0,
        "adult_min": 5000.0,
        "adult_max": 250000.0,
    },
    "vitamin_d_iu_per_kg_dm": {
        "display": "Vitamin D",
        "unit": "IU/kg DM",
        "basis": "iu_per_kg_dry_matter",
        "kind": "iu_kg_dm",
        "growth_min": 500.0,
        "growth_max": 3000.0,
        "adult_min": 500.0,
        "adult_max": 3000.0,
    },
    "vitamin_e_iu_per_kg_dm": {
        "display": "Vitamin E",
        "unit": "IU/kg DM",
        "basis": "iu_per_kg_dry_matter",
        "kind": "iu_kg_dm",
        "growth_min": 50.0,
        "growth_max": None,
        "adult_min": 50.0,
        "adult_max": None,
    },
    "vitamin_b1_mg_per_kg_dm": {
        "display": "Vitamin B1 (thiamine)",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 2.25,
        "growth_max": None,
        "adult_min": 2.25,
        "adult_max": None,
    },
    "vitamin_b2_mg_per_kg_dm": {
        "display": "Vitamin B2 (riboflavin)",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 5.2,
        "growth_max": None,
        "adult_min": 5.2,
        "adult_max": None,
    },
    "vitamin_b6_mg_per_kg_dm": {
        "display": "Vitamin B6",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 1.5,
        "growth_max": None,
        "adult_min": 1.5,
        "adult_max": None,
    },
    "niacin_mg_per_kg_dm": {
        "display": "Niacin (B3)",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 13.6,
        "growth_max": None,
        "adult_min": 13.6,
        "adult_max": None,
    },
    "pantothenic_mg_per_kg_dm": {
        "display": "Pantothenic acid (B5)",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 12.0,
        "growth_max": None,
        "adult_min": 12.0,
        "adult_max": None,
    },
    "folic_mg_per_kg_dm": {
        "display": "Folic acid (B9)",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 0.216,
        "growth_max": None,
        "adult_min": 0.216,
        "adult_max": None,
    },
    "choline_mg_per_kg_dm": {
        "display": "Choline",
        "unit": "mg/kg DM",
        "basis": "mg_per_kg_dry_matter",
        "kind": "mg_kg_dm",
        "growth_min": 1360.0,
        "growth_max": None,
        "adult_min": 1360.0,
        "adult_max": None,
    },
}

NOT_MODELED_CATEGORIES = (
    {
        "id": "water",
        "display": "Water",
        "status": "NOT_MODELED",
        "reason": "Source names water as essential but provides no numeric minimum/maximum.",
    },
    {
        "id": "carbohydrate_fiber",
        "display": "Carbohydrate / fiber",
        "status": "NOT_MODELED",
        "reason": "Source names carbohydrate/fiber as essential but provides no numeric minimum/maximum.",
    },
)

NUTRIENT_IDS = tuple(_PROFILE.keys())
VITAMIN_D_MAX_IU_PER_KG_DM = 3000.0


def dog_size_band(weight_kg: float) -> str:
    w = float(weight_kg)
    if w < 4:
        return "toy"
    if w < 10:
        return "small"
    if w < 25:
        return "medium"
    if w < 45:
        return "large"
    return "giant"


def life_stage_band(age_years: float) -> str:
    age = float(age_years)
    if age < 1.0:
        return "puppy/growth"
    if age >= 7.0:
        return "senior"
    return "adult maintenance"


def build_requirement_profile(*, weight_kg: float, age_years: float) -> dict[str, Any]:
    """Size is recorded and used for DMI scaling; numeric AAFCO-style %/density
    minima depend on life stage only. Breed is not used."""
    size = dog_size_band(weight_kg)
    stage = life_stage_band(age_years)
    growth = stage == "puppy/growth"
    senior = stage == "senior"
    nutrients: dict[str, Any] = {}
    for nid, spec in _PROFILE.items():
        minimum = spec["growth_min"] if growth else spec["adult_min"]
        maximum = spec["growth_max"] if growth else spec["adult_max"]
        nutrients[nid] = {
            "id": nid,
            "display": spec["display"],
            "minimum": minimum,
            "maximum": maximum,
            "unit": spec["unit"],
            "basis": spec["basis"],
            "kind": spec["kind"],
            "source": SOURCE,
            "life_stage": "puppy/growth" if growth else "adult maintenance",
            "maximum_specified": maximum is not None,
        }
    return {
        "synthetic_demo_data": False,
        "requirement_data_origin": "secondary_source_aafco_summary",
        "dog_size": size,
        "life_stage": stage,
        "weight_kg": float(weight_kg),
        "age_years": float(age_years),
        "basis": "dry_matter_diet_density",
        "size_used_for_nutrient_minima": False,
        "size_used_for": "estimated dry-matter intake / serving scale (reference 30 kg)",
        "breed_used_for_nutrient_minima": False,
        "senior_specific_minima": (
            "NOT_AVAILABLE — source does not provide senior-specific nutrient minima; adult maintenance used."
            if senior
            else "NOT_APPLICABLE"
        ),
        "complete_diet_claim": False,
        "claim_wording": "Meets modeled baseline nutrient constraints.",
        "not_modeled": list(NOT_MODELED_CATEGORIES),
        "source": SOURCE,
        "nutrients": nutrients,
        "reference_weight_kg": 30.0,
    }
