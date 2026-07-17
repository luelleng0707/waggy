"""
Port of wellnessEngine.buildCalculationTrace.
"""

from __future__ import annotations

import re
from typing import Any

from app.agent.condition_lookup import condition_key
from app.agent.utils import DataRepository, js_round
from app.agent.wellness_map import goal_for_condition


def _parse_dose_value(raw: Any) -> float:
    m = re.search(r"[-+]?[0-9]*\.?[0-9]+", str(raw or ""))
    return float(m.group(0)) if m else 0.0


def _parse_dose_unit(raw: Any) -> str:
    m = re.search(r"[a-zA-Z%]+(?:\s?[a-zA-Z%]+)?$", str(raw or ""))
    return m.group(0) if m else ""


def _breed_observed_risks(repo: DataRepository, breed_names: list[str]) -> list[dict[str, Any]]:
    df = repo.breed_conditions()
    if df.empty:
        return []
    names_l = {n.lower() for n in breed_names}
    hits = df[df["breed"].astype(str).str.lower().isin(names_l)]
    out = []
    for _, r in hits.iterrows():
        prev = float(r.get("prevalence") or 0)
        if prev > 1:
            prev = prev / 100.0
        try:
            year = int(float(r.get("year"))) if r.get("year") not in (None, "") else None
        except (TypeError, ValueError):
            year = None
        try:
            sample_size = int(float(r.get("sample_size"))) if r.get("sample_size") not in (None, "") else None
        except (TypeError, ValueError):
            sample_size = None
        out.append({
            "breed_name": r.get("breed"),
            "condition_name": r.get("condition"),
            "condition_key": condition_key(str(r.get("condition"))),
            "prevalence": prev,
            "sample_population": r.get("sample_population"),
            "sample_size": sample_size,
            "source_name": r.get("source_name"),
            "source_url": r.get("source_url"),
            "year": year,
        })
    return out


def build_calculation_trace(
    *,
    profile: dict[str, Any],
    biology: dict[str, Any],
    health_insights: list[dict[str, Any]],
    nutritional_targets: list[dict[str, Any]],
    product_recommendations: list[dict[str, Any]],
    repo: DataRepository,
) -> list[dict[str, Any]]:
    """Port of wellnessEngine.buildCalculationTrace."""
    breeds = profile.get("breeds") or []
    breed_evidence_all = _breed_observed_risks(repo, breeds)
    descriptors = (biology.get("descriptors") or [{}])
    desc0 = descriptors[0] if descriptors else {}
    weight_kg = profile.get("weight_kg")
    if isinstance(weight_kg, float) and weight_kg == int(weight_kg):
        weight_kg = int(weight_kg)
    age_years = profile.get("age_years")
    if isinstance(age_years, float) and age_years == int(age_years):
        age_years = int(age_years)

    trace = []
    for insight in health_insights[:6]:
        observed_inputs = {
            "age": f"{age_years} years",
            "weight": f"{weight_kg}kg",
            "body_size": desc0.get("size"),
            "body_type": desc0.get("body_type"),
            "coat_type": desc0.get("coat_type"),
            "skull": desc0.get("skull_type"),
            "activity": desc0.get("energy"),
            "breed_mix": breeds,
        }

        published_evidence = []
        for row in breed_evidence_all:
            goal_id = goal_for_condition(row.get("condition_key") or condition_key(str(row.get("condition_name"))))
            if goal_id != insight.get("goal_id"):
                continue
            published_evidence.append({
                "breed": row.get("breed_name"),
                "condition": row.get("condition_name"),
                "observed_prevalence_percent": js_round(float(row.get("prevalence") or 0) * 1000) / 10,
                "study_population": row.get("sample_population"),
                "sample_size": row.get("sample_size"),
                "source_title": row.get("source_name"),
                "source_journal": row.get("source_name"),
                "source_year": row.get("year"),
                "source_url": row.get("source_url"),
            })

        trait_contributions = [
            {
                "trait": trait,
                "role": "primary" if idx < 2 else "supporting",
                "explanation": (
                    "Matched against normalized epidemiology tables in deterministic trait aggregation."
                ),
            }
            for idx, trait in enumerate(insight.get("supporting_traits") or [])
        ]

        nutrient_targets = []
        for t in nutritional_targets:
            if insight.get("title") not in (t.get("supports_goals") or []):
                continue
            nutrient_targets.append({
                "nutrient": t.get("ingredient"),
                "target_daily_value": _parse_dose_value(t.get("daily_target")),
                "unit": _parse_dose_unit(t.get("daily_target")),
                "reason": (
                    f"Supports {str(insight.get('title', '')).lower()} requirements from "
                    f"deterministic profile-to-nutrient mapping."
                ),
                "evidence": {
                    "source_title": t.get("source_name"),
                    "source_url": t.get("source_url"),
                    "summary": t.get("evidence_quote"),
                },
            })

        product_contributions = []
        for p in product_recommendations or []:
            actives = p.get("active_ingredients") or []
            matching = [
                ai for ai in actives
                if any(
                    str(ai.get("name") or "").lower() == str(t.get("nutrient") or "").lower()
                    for t in nutrient_targets
                )
            ]
            nutrient_lines = []
            for ai in matching:
                target = next(
                    (
                        t for t in nutrient_targets
                        if str(t.get("nutrient") or "").lower() == str(ai.get("name") or "").lower()
                    ),
                    None,
                )
                amount = float(ai.get("amount") or ai.get("amount_per_serving") or 0)
                target_val = float((target or {}).get("target_daily_value") or 0)
                pct = js_round((amount / target_val) * 100) if target and target_val > 0 else 0
                nutrient_lines.append({
                    "nutrient": ai.get("name"),
                    "provided_value": amount,
                    "unit": ai.get("unit") or (target or {}).get("unit") or "",
                    "target_value": target_val,
                    "target_unit": (target or {}).get("unit") or "",
                    "percent_of_target": pct,
                    "source_title": ((target or {}).get("evidence") or {}).get("source_title"),
                    "source_url": ((target or {}).get("evidence") or {}).get("source_url"),
                })
            if nutrient_lines:
                product_contributions.append({
                    "product_id": p.get("product_id"),
                    "product_name": p.get("product_name"),
                    "serving_size": p.get("serving_size"),
                    "daily_amount": p.get("serving_size"),
                    "active_ingredient_count": len(actives),
                    "active_ingredients": [
                        {"name": ai.get("name"), "amount": ai.get("amount"), "unit": ai.get("unit")}
                        for ai in actives
                    ],
                    "nutrient_lines": nutrient_lines,
                })

        title_lower = str(insight.get("title", "")).lower()
        decision_log = [
            f"PPIE compared {profile.get('pet_name')}'s observed profile with deterministic trait-risk tables.",
            f"Published breed epidemiology for {title_lower} was matched across {len(breeds)} breed input(s).",
            "Nutrient targets were generated from CONDITION_INGREDIENTS and INGREDIENT_EVIDENCE mappings.",
            (
                f"Selected products close key nutrient gaps for {title_lower} with serving-feasible daily use."
                if product_contributions
                else "No direct nutrient-mapped product was selected for this priority."
            ),
        ]

        trace.append({
            "condition": insight.get("title"),
            "observed_inputs": observed_inputs,
            "published_evidence": published_evidence,
            "trait_contributions": trait_contributions,
            "nutrient_targets": nutrient_targets,
            "product_contributions": product_contributions,
            "decision_log": decision_log,
        })

    return trace
