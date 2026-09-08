"""Adapt Node-style analyze payloads to DogProfileInput (contract-preserving)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from app.agent.state import DogProfileInput


def age_years_from_birthday(birthday: str) -> float:
    """Mirror JS riskEngine.getAgeStage: round to 1 decimal using 365.25-day years."""
    birth = datetime.strptime(birthday, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    years = (now - birth).total_seconds() / (365.25 * 24 * 60 * 60)
    return round(years * 10) / 10


def profile_from_analyze_body(body: dict[str, Any]) -> DogProfileInput:
    """
    Accept either:
    - Python DogProfileInput fields (primary_breed, age_years, weight_kg, ...)
    - Node analyze fields (breeds[], birthday, weight, pet_name, ...)
    """
    breeds = body.get("breeds") or []
    if isinstance(breeds, str):
        breeds = [b.strip() for b in breeds.split(",") if b.strip()]

    primary = body.get("primary_breed") or (breeds[0] if breeds else None)
    secondary = body.get("secondary_breed")
    if secondary is None and len(breeds) > 1:
        secondary = breeds[1]

    name = (
        body.get("name")
        or body.get("pet_name")
        or body.get("petName")
        or body.get("dogName")
        or "Pet"
    )

    birthday = body.get("birthday")
    age_years = body.get("age_years")
    if age_years is None and birthday:
        age_years = age_years_from_birthday(str(birthday))
    if age_years is None:
        age_years = 5.0

    weight = body.get("weight_kg")
    if weight is None:
        weight = body.get("weight")
    if weight is None:
        weight = 20.0

    sex = body.get("sex") or body.get("gender")
    env = body.get("current_environment") or body.get("environment") or "Temperate Indoor"
    activity = body.get("activity_level") or body.get("activity") or "Moderate"

    split = body.get("breed_split_pct")
    if split is None:
        split = 50.0 if secondary else 100.0

    if not primary:
        raise ValueError("primary_breed or breeds[] is required")

    return DogProfileInput(
        name=str(name),
        primary_breed=str(primary),
        secondary_breed=str(secondary) if secondary else None,
        breed_split_pct=float(split),
        age_years=float(age_years),
        weight_kg=float(weight),
        current_environment=str(env),
        activity_level=str(activity),
        sex=str(sex) if sex else None,
        gender=str(sex) if sex else None,
        birthday=str(birthday) if birthday else None,
        height_cm=body.get("height_cm") if body.get("height_cm") is not None else body.get("height"),
        bcs=body.get("bcs"),
        observed_conditions=list(body.get("observed_conditions") or []),
        monthly_budget=(
            float(body["monthly_budget"])
            if body.get("monthly_budget") not in (None, "")
            else None
        ),
    )


def _legacy_priority_title(condition: Any) -> str:
    title = str(condition or "")
    title = re.sub(r"Dysplasia", "Protection", title, flags=re.I)
    title = re.sub(r"Ivdd", "Spine Care", title, flags=re.I)
    return title


def _parse_dose_int(daily_dose: Any) -> int:
    text = str(daily_dose or "0")
    digits = "".join(ch for ch in text if ch.isdigit())
    try:
        return int(digits) if digits else 0
    except ValueError:
        return 0


def map_legacy_response(r: dict[str, Any]) -> dict[str, Any]:
    """Port of src/api/routes.js mapLegacyResponse — identical field contract."""
    pet = r.get("pet") or {}
    risks = r.get("risks") or []
    ingredients = r.get("ingredients") or []
    products = r.get("products") or []
    monthly = r.get("monthly_plan") or {}
    yearly = r.get("yearly_plan") or {}
    evidence = r.get("evidence") or []
    groomer = r.get("groomer") or []
    weight = float(pet.get("weight_kg") or 0)

    return {
        "pet": {
            "dogName": pet.get("pet_name"),
            "breeds": pet.get("breeds"),
            "birthday": pet.get("birthday"),
            "ageYears": pet.get("age_years"),
            "ageStage": pet.get("age_stage"),
            "estimatedWeightKg": pet.get("weight_kg"),
            "sizeBracket": "medium" if weight < 18 else "large",
        },
        "wellnessScore": r.get("wellness_score"),
        "priorities": [
            {
                "id": risk.get("condition_key"),
                "title": _legacy_priority_title(risk.get("condition")),
                "priorityLevel": (
                    "High Priority"
                    if float(risk.get("risk_percent") or 0) >= 25
                    else "Moderate Priority"
                ),
                "priorityScore": risk.get("risk_percent"),
                "riskReasoning": risk.get("source_quote") or risk.get("why"),
                "whyProfile": {
                    "breeds": pet.get("breeds"),
                    "ageYears": pet.get("age_years"),
                    "weightKg": pet.get("weight_kg"),
                },
                "breedEvidence": (
                    {
                        "sourceName": risk.get("source_name"),
                        "quote": risk.get("source_quote"),
                        "url": risk.get("source_url"),
                    }
                    if risk.get("source_url")
                    else None
                ),
                "ingredients": [
                    {
                        "name": i.get("ingredient"),
                        "targetMgPerDay": _parse_dose_int(i.get("daily_dose")),
                        "evidenceQuote": i.get("evidence_quote"),
                        "sourceName": i.get("source_name"),
                        "sourceUrl": i.get("source_url"),
                    }
                    for i in ingredients
                    if risk.get("condition") in (i.get("for_conditions") or [])
                ],
                "products": [p for p in products if p.get("ingredient_name")][:2],
            }
            for risk in risks[:5]
        ],
        "healthRisks": [
            {
                "conditionName": x.get("condition"),
                "riskPercent": x.get("risk_percent"),
                "why": x.get("why"),
                "sources": [
                    {
                        "sourceName": x.get("source_name"),
                        "sourceQuote": x.get("source_quote"),
                        "sourceUrl": x.get("source_url"),
                    }
                ],
            }
            for x in risks
        ],
        "activeIngredients": ingredients,
        "recommendedProducts": products,
        "monthlyPack": {
            "title": monthly.get("title"),
            "items": monthly.get("items"),
            "totalCost": monthly.get("total_cost"),
            "schedule": monthly.get("items"),
            "productCount": monthly.get("product_count"),
        },
        "yearlyPack": {
            "title": yearly.get("title"),
            "items": yearly.get("items"),
            "totalCost": yearly.get("total_cost"),
            "monthlyEquivalent": yearly.get("monthly_equivalent"),
            "savings": yearly.get("savings"),
            "savingsPercent": yearly.get("savings_percent"),
            "kibbleUpgrade": yearly.get("kibble_upgrade"),
        },
        "evidenceLibrary": evidence,
        "groomerLive": groomer,
        "groomerNotes": [
            {"observation": g.get("key"), "severity": "moderate"}
            for g in groomer
            if g.get("status") == "flagged"
        ],
    }
