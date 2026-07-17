"""Wellness goal grouping — mirrors src/engine/wellnessMap.js for JS contract parity."""

from __future__ import annotations

import re

WELLNESS_GOALS: dict[str, dict] = {
    "joint_health": {
        "title": "Joint Health",
        "why_template": (
            "elevated lifetime joint-support needs based on body conformation, size, "
            "and published veterinary prevalence studies"
        ),
        "conditions": [
            "hip_dysplasia", "hip dysplasia", "ivdd", "cruciate_ligament_rupture",
            "osteoarthritis", "luxating_patella", "elbow_dysplasia",
        ],
    },
    "skin_health": {
        "title": "Skin Health",
        "why_template": (
            "additional skin-barrier and coat support may provide long-term comfort "
            "based on coat biology and dermatology evidence"
        ),
        "conditions": [
            "atopic_dermatitis", "atopic dermatitis", "dry_skin", "hot_spots",
            "immune_mediated_dermatosis", "pyoderma", "skin_barrier",
        ],
    },
    "dental_health": {
        "title": "Dental Health",
        "why_template": (
            "preventative oral care may reduce plaque burden common in companion breeds "
            "with compact dentition"
        ),
        "conditions": ["dental_disease", "periodontal_disease"],
    },
    "digestive_health": {
        "title": "Digestive Health",
        "why_template": (
            "digestive resilience support aligns with breed GI sensitivity patterns "
            "in published cohort studies"
        ),
        "conditions": ["chronic_enteropathy", "ibd", "food_sensitivities", "colitis"],
    },
    "weight_management": {
        "title": "Weight Management",
        "why_template": (
            "metabolic and activity biology suggests proactive weight management "
            "may improve long-term mobility"
        ),
        "conditions": ["obesity"],
    },
    "immune_support": {
        "title": "Immune Support",
        "why_template": (
            "immune-modulating nutrition may support breeds with documented "
            "immune-mediated predispositions"
        ),
        "conditions": ["immune_mediated_dermatosis"],
    },
    "respiratory_comfort": {
        "title": "Respiratory Comfort",
        "why_template": (
            "airway-friendly lifestyle and nutrition may benefit brachycephalic or "
            "heat-sensitive conformation"
        ),
        "conditions": ["boas", "heat_stress_syndrome", "tracheal_collapse"],
    },
    "eye_health": {
        "title": "Eye Health",
        "why_template": (
            "ocular antioxidant support may benefit breeds with documented eye-health "
            "prevalence patterns"
        ),
        "conditions": ["cataracts", "tear_stains", "tear_staining", "corneal_ulceration"],
    },
    "cardiac_support": {
        "title": "Cardiac Support",
        "why_template": (
            "cardiovascular nutritional support may benefit breeds with elevated cardiac "
            "prevalence in registry data"
        ),
        "conditions": ["degenerative_valve_disease", "dilated_cardiomyopathy", "heart_murmur"],
    },
    "activity_support": {
        "title": "Activity Support",
        "why_template": (
            "structured activity and recovery nutrition may support high-drive "
            "working and sporting biology"
        ),
        "conditions": ["exercise_induced_collapse", "cruciate_ligament_rupture"],
    },
}

PRIORITY_LABELS: dict[str, str] = {
    "joint_health": "Joint Support",
    "skin_health": "Skin Health",
    "dental_health": "Dental Care",
    "weight_management": "Healthy Weight",
    "digestive_health": "Digestive Support",
    "immune_support": "Immune Support",
    "activity_support": "Activity Support",
    "cardiac_support": "Cardiac Support",
    "eye_health": "Eye Health",
    "respiratory_comfort": "Respiratory Comfort",
    "general_wellness": "General Wellness",
}


def _condition_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")


CONDITION_TO_GOAL: dict[str, str] = {}
for goal_id, goal in WELLNESS_GOALS.items():
    for condition in goal["conditions"]:
        CONDITION_TO_GOAL[_condition_key(condition)] = goal_id


def goal_for_condition(condition_name: str) -> str:
    return CONDITION_TO_GOAL.get(_condition_key(condition_name), "general_wellness")


def priority_label(goal_id: str, fallback_title: str | None = None) -> str:
    return PRIORITY_LABELS.get(goal_id, fallback_title or "Wellness Support")


def friendly_trait_label(category: str, value: str) -> str:
    """Mirror src/engine/wellnessMap.js friendlyTraitLabel."""
    labels = {
        "size": "Large body",
        "body_type": f"{value} build",
        "weakness_group": f"{value} genetic architecture",
        "energy": f"{value} activity biology",
        "function_group": f"{value} working lineage",
        "coat_type": f"{value} coat",
        "climate": f"{value} climate adaptation",
        "lifespan": f"{value} lifespan profile",
        "skull_type": f"{value} skull conformation",
    }
    if category == "size" and value == "Large":
        return "Large body"
    if category == "size" and value == "Medium":
        return "Medium frame"
    if category == "body_type" and value == "Athletic":
        return "Sporting build"
    if category == "body_type" and value == "Chondrodysplastic":
        return "Long-spine conformation"
    return labels.get(category, str(value))
