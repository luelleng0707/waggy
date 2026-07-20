"""
Condition sibling/goal lookup — ports src/api/db/queries.js:
GOAL_CONDITION_MAP, conditionCandidates, conditionMatches, canonicalJoinKey.

Maps are seeded in data/inference/GOAL_CONDITION_MAP.csv (identical defaults).
"""

from __future__ import annotations

from typing import Iterable

from app.inference.resolver import canonical_join_key, condition_key, ingredient_key

# Embedded parity defaults (mirrored in CSV)
GOAL_CONDITION_MAP: dict[str, list[str]] = {
    "joint_health": [
        "hip_dysplasia",
        "ivdd",
        "cruciate_ligament_rupture",
        "osteoarthritis",
        "luxating_patella",
        "elbow_dysplasia",
    ],
    "skin_health": [
        "atopic_dermatitis",
        "dry_skin",
        "hot_spots",
        "immune_mediated_dermatosis",
        "pyoderma",
        "otitis_externa",
    ],
    "dental_health": ["dental_disease", "periodontal_disease"],
    "digestive_health": ["chronic_enteropathy", "ibd", "food_sensitivities", "colitis"],
    "weight_management": ["obesity"],
    "immune_support": ["immune_mediated_dermatosis"],
    "respiratory_comfort": ["boas", "heat_stress_syndrome", "tracheal_collapse"],
    "eye_health": [
        "cataracts",
        "tear_staining",
        "corneal_ulceration",
        "progressive_retinal_atrophy",
    ],
    "cardiac_support": [
        "degenerative_valve_disease",
        "dilated_cardiomyopathy",
        "heart_murmur",
    ],
    "activity_support": [
        "exercise_induced_collapse",
        "cruciate_ligament_rupture",
        "hip_dysplasia",
    ],
}


def _active_goal_map() -> dict[str, list[str]]:
    return GOAL_CONDITION_MAP


def _condition_to_goal() -> dict[str, str]:
    # Last write wins — mirrors JS Object.entries reduce order.
    out: dict[str, str] = {}
    for goal, conditions in _active_goal_map().items():
        for condition in conditions:
            out[condition] = goal
    return out


def condition_candidates(condition_name: str | None) -> list[str]:
    """Mirror queries.js conditionCandidates — include goal siblings."""
    normalized = condition_key(condition_name)
    gmap = _active_goal_map()
    direct_mapped = gmap.get(normalized) or []
    goal = _condition_to_goal().get(normalized)
    sibling_mapped = gmap.get(goal, []) if goal else []
    return [normalized, *direct_mapped, *sibling_mapped]


def condition_matches(
    record_key: str | None,
    record_name: str | None,
    candidates: Iterable[str],
) -> bool:
    rk = canonical_join_key(record_key)
    rn = canonical_join_key(record_name)
    for c in candidates:
        ck = canonical_join_key(c)
        if ck and (rk == ck or rn == ck):
            return True
    return False


__all__ = [
    "GOAL_CONDITION_MAP",
    "canonical_join_key",
    "condition_key",
    "condition_candidates",
    "condition_matches",
    "ingredient_key",
]
