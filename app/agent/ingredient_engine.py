"""Port of src/engine/ingredientEngine.js + dosageEngine.js calculateDose."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.agent.condition_lookup import (
    condition_candidates,
    condition_matches,
    ingredient_key,
)
from app.agent.formula_trace import (
    decision,
    empty_execution,
    lookup_competition,
    lookup_row,
    seal_execution,
    start_timer,
    step,
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
    """Port of ingredientEngine.mapIngredients — feed enrichPackageForDetail.

    Additive: attaches formula_execution ledgers; does not change doses.
    """
    ingredient_map: dict[str, dict[str, Any]] = {}
    for risk in risks:
        cond_name = risk.get("condition_name") or risk.get("condition_key")
        t0 = start_timer()
        links = _condition_ingredient_rows(repo, str(cond_name or ""))
        link_lookups = []
        for link in links:
            dose = calculate_dose(link, weight_kg)
            key = link.get("ingredient_key") or ingredient_key(str(link.get("ingredient_name") or ""))
            evidence = _ingredient_evidence(repo, str(key))
            mechanisms = _ingredient_mechanisms(repo, str(key))
            lu = lookup_row(
                table=str(link.get("_csv_file") or "CONDITION_INGREDIENTS.csv"),
                primary_key={
                    "condition": link.get("condition") or link.get("condition_name") or cond_name,
                    "ingredient": link.get("ingredient_name") or key,
                },
                columns={
                    "recommended_daily_dose": link.get("recommended_daily_dose") or link.get("dose_min"),
                    "dose_unit": link.get("dose_unit") or link.get("unit"),
                    "dose_basis": link.get("dose_basis"),
                    "computed_daily": dose["daily"],
                },
                csv_row=link.get("_csv_row"),
                csv_file=str(link.get("_csv_file") or "CONDITION_INGREDIENTS.csv"),
                evidence_id=(evidence or {}).get("source_name") or link.get("source_name"),
                decision="mapped",
            )
            link_lookups.append(lu)
            if key not in ingredient_map:
                fx = empty_execution("NUTRIENT_TARGET_V2_1", subject=str(key), condition=str(cond_name or ""))
                fx["inputs"] = {"weight_kg": weight_kg, "source_conditions": [cond_name]}
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
                    "formula_execution": fx,
                    "_link_lookups": [],
                    "_dose_candidates": [],
                }
            ing = ingredient_map[key]
            ing["_link_lookups"].append(lu)
            ing["_dose_candidates"].append(
                {"condition": cond_name, "daily": dose["daily"], "lookup": lu}
            )
            cond = risk.get("condition_name") or risk.get("condition_key")
            if cond and cond not in ing["for_conditions"]:
                ing["for_conditions"].append(cond)
            before = ing["daily_dose"]
            daily = max(ing["daily_dose"], dose["daily"])
            ing["daily_dose"] = int(daily) if float(daily) == int(float(daily)) else daily
            ing["monthly_dose"] = ing["daily_dose"] * 30
            ing["yearly_dose"] = ing["daily_dose"] * 365
            fx = ing["formula_execution"]
            if cond and cond not in (fx.get("inputs") or {}).get("source_conditions", []):
                fx.setdefault("inputs", {}).setdefault("source_conditions", []).append(cond)
            if dose["daily"] > before:
                fx.setdefault("decisions", []).append(
                    decision(
                        "Selected",
                        subject=str(key),
                        reasons=[
                            f"Higher daily dose from condition `{cond_name}` ({dose['daily']} > {before})",
                        ],
                        score=dose["daily"],
                    )
                )

        # condition-level competition note when multiple ingredients mapped
        if len(link_lookups) > 1:
            # attach competition onto each ingredient that came from this condition
            for link in links:
                key = link.get("ingredient_key") or ingredient_key(str(link.get("ingredient_name") or ""))
                if key in ingredient_map:
                    ingredient_map[key]["formula_execution"].setdefault("competitions", []).append(
                        lookup_competition(
                            purpose=f"CONDITION_INGREDIENTS for `{cond_name}`",
                            candidates=link_lookups,
                            selected=None,
                            reason="All matching ingredient rows are mapped; dose uses max across conditions",
                        )
                    )

    # Seal per-ingredient ledgers
    out = []
    for key, ing in ingredient_map.items():
        fx = ing.get("formula_execution") or empty_execution("NUTRIENT_TARGET_V2_1", subject=str(key))
        lookups = list(ing.pop("_link_lookups", []) or [])
        dose_cands = list(ing.pop("_dose_candidates", []) or [])
        fx["lookups"] = lookups
        if evidence_lu := next((d.get("lookup") for d in dose_cands if d.get("daily") == ing["daily_dose"]), None):
            selected = evidence_lu
        else:
            selected = lookups[0] if lookups else None
        if len(dose_cands) > 1:
            fx.setdefault("competitions", []).append(
                lookup_competition(
                    purpose=f"max daily dose for `{key}`",
                    candidates=[d.get("lookup") for d in dose_cands if d.get("lookup")],
                    selected=selected,
                    reason="max(daily_dose across supporting conditions)",
                )
            )
        fx["steps"] = [
            step(
                1,
                "condition_ingredient_lookup",
                expression="CONDITION_INGREDIENTS match on condition candidates",
                inputs={"conditions": ing.get("for_conditions"), "rows": len(lookups)},
                result=len(lookups),
                lookups=lookups,
            ),
            step(
                2,
                "calculate_dose",
                expression="mg_per_kg ? weight_kg * dose : dose",
                inputs={"weight_kg": weight_kg, "candidates": [d.get("daily") for d in dose_cands]},
                result=ing["daily_dose"],
                unit=ing.get("unit"),
            ),
            step(
                3,
                "select_max_daily",
                expression="max(daily_dose across conditions)",
                inputs=[d.get("daily") for d in dose_cands],
                result=ing["daily_dose"],
                unit=ing.get("unit"),
            ),
        ]
        if not fx.get("decisions"):
            fx["decisions"] = [
                decision(
                    "Accepted",
                    subject=str(key),
                    reasons=[f"Mapped from conditions: {', '.join(str(c) for c in (ing.get('for_conditions') or []))}"],
                    score=ing["daily_dose"],
                )
            ]
        fx["outputs"] = {
            "ingredient_key": key,
            "daily_dose": ing["daily_dose"],
            "monthly_dose": ing["monthly_dose"],
            "unit": ing.get("unit"),
            "for_conditions": ing.get("for_conditions"),
        }
        seal_execution(fx)
        ing["formula_execution"] = fx
        out.append(ing)

    return sorted(out, key=lambda a: -float(a["daily_dose"]))
