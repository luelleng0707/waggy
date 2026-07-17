"""Port of src/engine/ingredientEngine.js + dosageEngine.js calculateDose."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.agent.condition_lookup import (
    condition_candidates,
    condition_matches,
    ingredient_key,
)
from app.agent.utils import DataRepository, js_round


def calculate_dose(link: dict[str, Any], weight_kg: float) -> dict[str, Any]:
    """Port of dosageEngine.calculateDose."""
    raw = link.get("recommended_daily_dose")
    if raw is None:
        raw = link.get("dose_min")
    try:
        dose = float(raw)
    except (TypeError, ValueError):
        dose = 0.0
    unit = link.get("dose_unit") or link.get("unit")
    if link.get("dose_basis") == "mg_per_kg":
        daily = js_round(weight_kg * dose)
    else:
        daily = js_round(dose)
    return {"daily": daily, "monthly": daily * 30, "yearly": daily * 365, "unit": unit}


def _condition_ingredient_rows(repo: DataRepository, condition_name: str) -> list[dict[str, Any]]:
    df = repo.condition_ingredients()
    if df.empty or not condition_name:
        return []
    candidates = condition_candidates(condition_name)
    name_col = "condition" if "condition" in df.columns else "condition_name"
    rows = []
    for _, row in df.iterrows():
        rec = row.to_dict()
        if condition_matches(rec.get("condition_key"), rec.get(name_col), candidates):
            # Normalize keys to match JS csvLoader link shape
            if "ingredient_key" not in rec or pd.isna(rec.get("ingredient_key")):
                rec["ingredient_key"] = ingredient_key(str(rec.get("ingredient_name") or ""))
            rows.append(rec)
    return rows


def _ingredient_evidence(repo: DataRepository, key_or_name: str) -> dict[str, Any] | None:
    df = repo.ingredient_evidence()
    if df.empty:
        return None
    key = ingredient_key(key_or_name)
    for col in ("ingredient_key", "ingredient_name", "ingredient"):
        if col not in df.columns:
            continue
        hit = df[df[col].astype(str).map(ingredient_key) == key]
        if not hit.empty:
            return hit.iloc[0].to_dict()
        hit = df[df[col].astype(str).str.lower() == str(key_or_name).lower()]
        if not hit.empty:
            return hit.iloc[0].to_dict()
    return None


def _ingredient_mechanisms(repo: DataRepository, key_or_name: str) -> list[dict[str, Any]]:
    df = repo.ingredient_mechanisms()
    if df.empty:
        return []
    key = ingredient_key(key_or_name)
    out = []
    for _, m in df.iterrows():
        nname = str(m.get("nutrient_name") or "")
        iname = str(m.get("ingredient_name") or "")
        if key in (ingredient_key(nname), ingredient_key(iname)) or nname.lower() == str(key_or_name).lower() or iname.lower() == str(key_or_name).lower():
            out.append(m.to_dict())
    return out


def map_ingredients(risks: list[dict[str, Any]], weight_kg: float, repo: DataRepository) -> list[dict[str, Any]]:
    """Port of ingredientEngine.mapIngredients — feed enrichPackageForDetail."""
    ingredient_map: dict[str, dict[str, Any]] = {}
    for risk in risks:
        cond_name = risk.get("condition_name") or risk.get("condition_key")
        links = _condition_ingredient_rows(repo, str(cond_name or ""))
        for link in links:
            dose = calculate_dose(link, weight_kg)
            key = link.get("ingredient_key") or ingredient_key(str(link.get("ingredient_name") or ""))
            evidence = _ingredient_evidence(repo, str(key))
            mechanisms = _ingredient_mechanisms(repo, str(key))
            if key not in ingredient_map:
                ingredient_map[key] = {
                    "ingredient_name": link.get("ingredient_name"),
                    "ingredient_key": key,
                    "for_conditions": [],
                    "daily_dose": dose["daily"],
                    "monthly_dose": dose["monthly"],
                    "yearly_dose": dose["yearly"],
                    "unit": link.get("dose_unit") or link.get("unit"),
                    "dose_basis": link.get("dose_basis"),
                    "evidence_quote": (evidence or {}).get("source_quote") or link.get("source_quote"),
                    "source_name": (evidence or {}).get("source_name") or link.get("source_name"),
                    "source_url": (evidence or {}).get("source_url") or link.get("source_url"),
                    "mechanism_summary": (
                        (mechanisms[0].get("mechanism_summary") if mechanisms else None)
                        or (evidence or {}).get("mechanism")
                    ),
                }
            ing = ingredient_map[key]
            cond = risk.get("condition_name") or risk.get("condition_key")
            if cond and cond not in ing["for_conditions"]:
                ing["for_conditions"].append(cond)
            daily = max(ing["daily_dose"], dose["daily"])
            ing["daily_dose"] = int(daily) if float(daily) == int(float(daily)) else daily
            ing["monthly_dose"] = ing["daily_dose"] * 30
            ing["yearly_dose"] = ing["daily_dose"] * 365

    return sorted(ingredient_map.values(), key=lambda a: -float(a["daily_dose"]))
