"""
Algorithmic constants for the inference layer.

Science lives in data/** CSVs.
Algorithms, weights, ladders, and display catalogs live here.

Do NOT load algorithmic config from CSV.
"""

from __future__ import annotations

from typing import Any

# ── Trait evidence weights (RISK_V2_1 parity) ─────────────────────────

CATEGORY_WEIGHTS: dict[str, float] = {
    "weakness_group": 3.0,
    "body_type": 2.5,
    "skull_type": 2.5,
    "function_group": 2.0,
    "size": 2.0,
    "energy": 1.5,
    "lifespan": 1.5,
    "coat_type": 1.0,
    "climate": 1.0,
}
# Back-compat aliases
DEFAULT_CATEGORY_WEIGHTS = CATEGORY_WEIGHTS

# ── Groomer free-text → condition (heuristic, not literature rows) ─────

GROOMER_MAP: dict[str, str] = {
    "tear_stains": "Tear Staining",
    "limping": "Hip Dysplasia",
    "limps": "Cruciate Ligament Rupture",
    "itching": "Atopic Dermatitis",
    "scratching": "Atopic Dermatitis",
    "dry_skin": "Dry Skin",
    "eye_discharge": "Cataracts",
    "eyes": "Tear Staining",
    "bad_breath": "Dental Disease",
    "teeth": "Dental Disease",
    "ears": "Ear Infection",
    "shedding": "Dry Skin",
    "anal_gland": "Anal Gland Impaction",
    "skin": "Dry Skin",
    "odor": "Ear Infection",
}
DEFAULT_GROOMER_MAP = GROOMER_MAP

# ── Package optimizer weights (PACKAGE_OPTIMIZER_V2_1 parity) ─────────

SCORE_WEIGHTS: dict[str, float] = {
    "coverage": 0.35,
    "clinical_function": 0.25,
    "evidence": 0.20,
    "cost_efficiency": 0.15,
    "diversity": 0.05,
}
DEFAULT_SCORE_WEIGHTS = SCORE_WEIGHTS
SURPLUS_PENALTY_WEIGHT = 0.02
ESSENTIAL_COVERAGE_FLOOR = 0.55
DEFAULT_SURPLUS_PENALTY_WEIGHT = SURPLUS_PENALTY_WEIGHT
DEFAULT_ESSENTIAL_COVERAGE_FLOOR = ESSENTIAL_COVERAGE_FLOOR

# ── Nutrient display catalog (labels/units — not prevalence science) ──

NUTRIENT_CATALOG: list[dict[str, Any]] = [
    {"key": "glucosamine", "label": "Glucosamine", "unit": "mg", "aliases": []},
    {"key": "omega_3", "label": "EPA+DHA", "unit": "mg", "aliases": ["omega-3", "epa", "dha"]},
    {"key": "msm", "label": "MSM", "unit": "mg", "aliases": []},
    {
        "key": "chondroitin_sulfate",
        "label": "Chondroitin",
        "unit": "mg",
        "aliases": ["chondroitin"],
    },
    {"key": "l_carnitine", "label": "L-Carnitine", "unit": "mg", "aliases": []},
    {"key": "taurine", "label": "Taurine", "unit": "mg", "aliases": []},
    {"key": "lutein", "label": "Lutein", "unit": "mg", "aliases": []},
    {"key": "probiotics", "label": "Probiotics", "unit": "billion CFU", "aliases": []},
    {"key": "seaweed_blend", "label": "Seaweed Bioactives", "unit": "mg", "aliases": ["seaweed"]},
    {"key": "zinc", "label": "Zinc", "unit": "mg", "aliases": []},
]
DEFAULT_NUTRIENT_CATALOG = NUTRIENT_CATALOG

# ── Ingredient order estimation profile (ING_FRAC_ORDER_V1) ───────────

INGREDIENT_ORDER_PERCENTS: tuple[float, ...] = (35.0, 22.0, 16.0, 10.0, 6.0)

# ── Confidence ladder (CONF_V1) — see confidence.py ───────────────────
# Kept in confidence.DEFAULT_LADDER


def category_weights() -> dict[str, float]:
    return dict(CATEGORY_WEIGHTS)


def groomer_map() -> dict[str, str]:
    return dict(GROOMER_MAP)


def score_weights(profile_id: str = "default") -> dict[str, float]:
    _ = profile_id  # reserved for future named profiles in code, not CSV
    return dict(SCORE_WEIGHTS)


def surplus_penalty_weight(profile_id: str = "default") -> float:
    _ = profile_id
    return SURPLUS_PENALTY_WEIGHT


def essential_coverage_floor(profile_id: str = "default") -> float:
    _ = profile_id
    return ESSENTIAL_COVERAGE_FLOOR


def nutrient_catalog() -> list[dict[str, Any]]:
    return [dict(x) for x in NUTRIENT_CATALOG]


def goal_condition_map() -> dict[str, list[str]]:
    """Always empty — goal maps live in agent.condition_lookup / wellness_map."""
    return {}


def wellness_goals_from_csv() -> dict[str, dict[str, Any]]:
    """Deprecated stub — wellness goals live in agent.wellness_map."""
    return {}


def clear_config_cache() -> None:
    return None
