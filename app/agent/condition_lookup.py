"""
Condition sibling/goal lookup — ports src/api/db/queries.js:
GOAL_CONDITION_MAP, conditionCandidates, conditionMatches, canonicalJoinKey.
"""

from __future__ import annotations

import re
from typing import Iterable

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

# Last write wins — mirrors JS Object.entries reduce order.
CONDITION_TO_GOAL: dict[str, str] = {}
for goal, conditions in GOAL_CONDITION_MAP.items():
    for condition in conditions:
        CONDITION_TO_GOAL[condition] = goal


def canonical_join_key(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def condition_key(name: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")


def condition_candidates(condition_name: str | None) -> list[str]:
    """Mirror queries.js conditionCandidates — include goal siblings."""
    normalized = condition_key(condition_name)
    direct_mapped = GOAL_CONDITION_MAP.get(normalized) or []
    goal = CONDITION_TO_GOAL.get(normalized)
    sibling_mapped = GOAL_CONDITION_MAP.get(goal, []) if goal else []
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


def ingredient_key(name: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")
