"""Adapt HTTP payloads to DogProfileInput.

Two adapters:

- profile_from_analyze_body: legacy compatibility (silent age/weight/activity defaults).
- profile_from_workbench_body: canonical workbench contract (fail-closed).

Neither adapter calculates prevalence, nutrition, packages, or evidence.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from app.agent.state import DogProfileInput
from app.contracts.agent.enums import InputState
from app.contracts.agent.errors import ToolError, invalid_input, missing_required_input
from app.contracts.agent.input import FieldValue, provided, unknown


class WorkbenchInputError(ValueError):
    """Fail-closed workbench validation. HTTP 400 `{error: ...}`."""

    def __init__(self, error: ToolError, *, field: str | None = None) -> None:
        self.error = error
        self.field = field if field is not None else (error.fields[0] if error.fields else None)
        super().__init__(error.message)

    def to_http_body(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.error.code.value,
                "message": self.error.message,
                "field": self.field,
                "fields": list(self.error.fields),
            }
        }


def age_years_from_birthday(birthday: str, as_of: datetime | None = None) -> float:
    """Mirror JS riskEngine.getAgeStage: round to 1 decimal using 365.25-day years.

    When as_of is omitted, uses datetime.now (documented non-determinism for
    birthday-only age). Engine formulas consume the resulting age_years only.
    """
    birth = datetime.strptime(birthday, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    now = as_of if as_of is not None else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    years = (now - birth).total_seconds() / (365.25 * 24 * 60 * 60)
    return round(years * 10) / 10


def _missing(field: str, message: str | None = None) -> WorkbenchInputError:
    return WorkbenchInputError(missing_required_input([field], message=message), field=field)


def _invalid(fields: list[str], message: str | None = None, *, field: str | None = None) -> WorkbenchInputError:
    return WorkbenchInputError(invalid_input(fields, message=message), field=field or fields[0])


def _blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _parse_as_of(raw: Any) -> datetime | None:
    if _blank(raw):
        return None
    text = str(raw).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise _invalid(["as_of_date"], "as_of_date must be YYYY-MM-DD") from exc


def _breeds_list(body: dict[str, Any]) -> list[str]:
    breeds = body.get("breeds") or []
    if isinstance(breeds, str):
        breeds = [item.strip() for item in breeds.split(",") if item.strip()]
    elif isinstance(breeds, list):
        breeds = [str(item).strip() for item in breeds if str(item).strip()]
    else:
        breeds = []
    return breeds


def _display_name(body: dict[str, Any], *, default: str | None) -> str:
    for key in ("name", "pet_name", "petName", "dogName"):
        value = body.get(key)
        if value is None:
            continue
        return str(value).strip()
    return default if default is not None else ""


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _split_pct(body: dict[str, Any], secondary: str | None) -> float:
    split = body.get("breed_split_pct")
    if split is None or split == "":
        return 50.0 if secondary else 100.0
    return float(split)


def _normalize_workbench_breed_input_state(raw: Any) -> str | None:
    """Reuse persist rule: omitted, or exactly UNKNOWN. Not an Ω12 status."""
    if raw is None or (isinstance(raw, str) and raw.strip() == ""):
        return None
    text = str(raw).strip()
    if text == InputState.UNKNOWN:
        return InputState.UNKNOWN
    raise _invalid(
        ["breed_input_state"],
        "breed_input_state may be omitted or UNKNOWN; it is not an Ω12 mapping status",
    )


def workbench_breed_field(body: dict[str, Any]) -> FieldValue[str]:
    """Customer breed presence on the workbench body.

    UNKNOWN is InputState.UNKNOWN. It is not Ω12 UNRESOLVED or AMBIGUOUS.
    Omitted or blank primary_breed without UNKNOWN remains missing, not UNKNOWN.
    """
    state = _normalize_workbench_breed_input_state(body.get("breed_input_state"))
    breeds = _breeds_list(body)
    primary = body.get("primary_breed") or (breeds[0] if breeds else None)
    secondary = body.get("secondary_breed")
    if state == InputState.UNKNOWN:
        if not _blank(primary) or not _blank(secondary) or breeds:
            raise _invalid(["primary_breed"], "UNKNOWN breed cannot carry a breed string")
        return unknown()
    if _blank(primary):
        raise _missing("primary_breed", "primary_breed or breeds[] is required")
    return provided(str(primary).strip())


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


def _request_observations(body: dict[str, Any]) -> list[str]:
    observed = [str(item) for item in (body.get("observed_conditions") or []) if item]
    role_context = body.get("role_context") if isinstance(body.get("role_context"), dict) else {}
    groomer = role_context.get("groomer") if isinstance(role_context.get("groomer"), dict) else {}
    extra = groomer.get("observed_conditions")
    if isinstance(extra, list) and extra:
        observed = list(dict.fromkeys([*observed, *[str(item) for item in extra if item]]))
    return observed


def profile_from_workbench_body(body: dict[str, Any]) -> DogProfileInput:
    """Canonical workbench adapter: validate and map. No silent scientific defaults.

    Does not merge process-global groomer sessions. Role-context observations on
    this request may be appended to observed_conditions.
    Explicit breed_input_state=UNKNOWN is accepted as InputState.UNKNOWN and
    fails closed before DogProfileInput / Core. Blank breed is not UNKNOWN.
    """
    breed_field = workbench_breed_field(body)
    if breed_field.state == InputState.UNKNOWN:
        raise _invalid(
            ["breed_input_state"],
            "UNKNOWN breed cannot enter breed-dependent analysis",
        )
    breeds = _breeds_list(body)
    primary = breed_field.value
    if _blank(primary):
        raise _missing("primary_breed", "primary_breed or breeds[] is required")
    secondary = body.get("secondary_breed")
    if _blank(secondary) and len(breeds) > 1:
        secondary = breeds[1]
    if _blank(secondary):
        secondary = None

    name = _display_name(body, default="")

    birthday = body.get("birthday")
    age_raw = body.get("age_years")
    as_of = _parse_as_of(body.get("as_of_date"))
    if _blank(age_raw) and _blank(birthday):
        raise _missing("age_years", "age_years or birthday is required")

    age_years: float | None = None
    if not _blank(age_raw):
        parsed_age = _float_or_none(age_raw)
        if parsed_age is None:
            raise _invalid(["age_years"], "age_years must be a number")
        if parsed_age <= 0:
            raise _invalid(["age_years"], "age_years must be greater than 0")
        age_years = parsed_age
    elif not _blank(birthday):
        try:
            age_years = age_years_from_birthday(str(birthday).strip(), as_of=as_of)
        except ValueError as exc:
            raise _invalid(["birthday"], "birthday must be YYYY-MM-DD") from exc
        if age_years < 0:
            raise _invalid(["birthday"], "birthday produces a negative age")

    weight_raw = body.get("weight")
    weight_kg_raw = body.get("weight_kg")
    weight_supplied = not _blank(weight_raw)
    weight_kg_supplied = not _blank(weight_kg_raw)
    if not weight_supplied and not weight_kg_supplied:
        raise _missing("weight", "weight or weight_kg is required")

    weight_value: float | None = None
    weight_kg_value: float | None = None
    if weight_supplied:
        weight_value = _float_or_none(weight_raw)
        if weight_value is None:
            raise _invalid(["weight"], "weight must be a number")
    if weight_kg_supplied:
        weight_kg_value = _float_or_none(weight_kg_raw)
        if weight_kg_value is None:
            raise _invalid(["weight_kg"], "weight_kg must be a number")
    if weight_value is not None and weight_kg_value is not None and weight_value != weight_kg_value:
        raise _invalid(
            ["weight", "weight_kg"],
            "weight and weight_kg must match; the API does not pick one",
        )
    weight = weight_value if weight_value is not None else weight_kg_value
    if weight is None or weight <= 0:
        raise _invalid(["weight"], "weight must be greater than 0")

    activity = body.get("activity_level")
    if _blank(activity):
        activity = body.get("activity")
    if _blank(activity):
        raise _missing("activity_level", "activity_level is required")

    env = body.get("current_environment")
    if _blank(env):
        env = body.get("environment")
    if _blank(env):
        raise _missing("current_environment", "current_environment is required")

    sex = body.get("sex") or body.get("gender")
    split = _split_pct(body, str(secondary) if secondary else None)

    monthly = body.get("monthly_budget")
    monthly_budget = None
    if not _blank(monthly):
        monthly_budget = _float_or_none(monthly)
        if monthly_budget is None:
            raise _invalid(["monthly_budget"], "monthly_budget must be a number")

    return DogProfileInput(
        name=str(name),
        primary_breed=str(primary),
        secondary_breed=str(secondary) if secondary else None,
        breed_split_pct=float(split),
        age_years=float(age_years) if age_years is not None else 0.0,
        weight_kg=float(weight),
        current_environment=str(env).strip(),
        activity_level=str(activity).strip(),
        sex=str(sex) if sex else None,
        gender=str(sex) if sex else None,
        birthday=str(birthday).strip() if not _blank(birthday) else None,
        height_cm=body.get("height_cm") if body.get("height_cm") is not None else body.get("height"),
        bcs=body.get("bcs"),
        observed_conditions=_request_observations(body),
        monthly_budget=monthly_budget,
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
