"""Ingredient inference — NUTRIENT_EST_V1, ING_FRAC_ORDER_V1 (opt-in)."""

from __future__ import annotations

from typing import Any, Sequence

import pandas as pd

from app.inference.confidence import confidence_for_source
from app.inference.models import InferredValue
from app.inference.resolver import ingredient_key, normalize_label, resolve_canonical_ingredient

FORMULA_NUTRIENT_EST = "NUTRIENT_EST_V1"
FORMULA_FRAC_ORDER = "ING_FRAC_ORDER_V1"

DEFAULT_ORDER_PERCENTS = (35.0, 22.0, 16.0, 10.0, 6.0)


def order_profile_percents(df: pd.DataFrame | None = None, profile_id: str = "default") -> list[float]:
    """Order profile lives in Python (INGREDIENT_ORDER_PERCENTS). df ignored."""
    _ = (df, profile_id)
    try:
        from app.inference.config import INGREDIENT_ORDER_PERCENTS

        return list(INGREDIENT_ORDER_PERCENTS)
    except Exception:  # noqa: BLE001
        return list(DEFAULT_ORDER_PERCENTS)


def estimate_fractions_from_order(
    ingredients: Sequence[str],
    *,
    profile_percents: Sequence[float] | None = None,
    profile_df: pd.DataFrame | None = None,
    profile_id: str = "default",
) -> InferredValue:
    """
    ING_FRAC_ORDER_V1 — estimate mass fractions from descending ingredient order.
    Not wired into production scoring.
    """
    names = [normalize_label(x) for x in ingredients if normalize_label(x)]
    percents = list(profile_percents) if profile_percents is not None else order_profile_percents(profile_df, profile_id)
    n = len(names)
    if n == 0:
        return InferredValue(
            value=[],
            confidence=0.0,
            formula_id=FORMULA_FRAC_ORDER,
            source="empty",
            reason="No ingredients provided",
            enabled=False,
        )

    fixed = percents[: min(len(percents), n)]
    assigned = sum(fixed)
    remaining_slots = n - len(fixed)
    remainder = max(0.0, 100.0 - assigned)
    per_rest = (remainder / remaining_slots) if remaining_slots else 0.0

    fracs: list[dict[str, Any]] = []
    for i, name in enumerate(names):
        if i < len(fixed):
            pct = fixed[i]
        else:
            pct = per_rest
        fracs.append(
            {
                "ingredient": name,
                "ingredient_key": ingredient_key(name),
                "fraction": round(pct / 100.0, 6),
                "percent": round(pct, 4),
                "rank": i + 1,
            }
        )
    # Normalize in case of float drift
    total = sum(f["fraction"] for f in fracs) or 1.0
    for f in fracs:
        f["fraction"] = round(f["fraction"] / total, 6)
        f["percent"] = round(f["fraction"] * 100.0, 4)

    conf = confidence_for_source("ingredient_order") / 100.0
    return InferredValue(
        value=fracs,
        confidence=conf,
        formula_id=FORMULA_FRAC_ORDER,
        source=f"order_profile:{profile_id}",
        reason="Estimated from ingredient declaration order",
        unit="fraction",
        enabled=False,
        trace=tuple({"rank": f["rank"], "percent": f["percent"]} for f in fracs),
    )


def estimate_nutrient(
    fractions: Sequence[dict[str, Any]],
    nutrient: str,
    estimates_df: pd.DataFrame | None,
    *,
    taxonomy_df: pd.DataFrame | None = None,
) -> InferredValue:
    """
    NUTRIENT_EST_V1 — Σ(ingredient_fraction × nutrient_density per 100g).
    Not wired into production scoring.
    """
    if estimates_df is None or estimates_df.empty:
        return InferredValue(
            value=None,
            confidence=0.0,
            formula_id=FORMULA_NUTRIENT_EST,
            source="missing_estimates_table",
            reason="ingredient_nutrient_estimates unavailable",
            enabled=False,
        )

    nutrient_l = normalize_label(nutrient).lower()
    total = 0.0
    unit = "mg"
    steps: list[dict[str, Any]] = []
    confs: list[float] = []

    for item in fractions:
        name = normalize_label(item.get("ingredient") or item.get("name"))
        frac = float(item.get("fraction") or 0)
        if not name or frac <= 0:
            continue
        resolved = resolve_canonical_ingredient(name, taxonomy_df=taxonomy_df)
        canon = normalize_label(resolved.get("input"))
        # match rows
        mask = estimates_df["nutrient"].astype(str).str.strip().str.lower() == nutrient_l
        sub = estimates_df.loc[mask]
        if sub.empty:
            continue
        row = None
        for _, r in sub.iterrows():
            cand = normalize_label(r.get("canonical_ingredient") or r.get("ingredient"))
            if cand.lower() == name.lower() or cand.lower() == canon.lower():
                row = r
                break
            if ingredient_key(cand) == ingredient_key(name):
                row = r
                break
        if row is None:
            continue
        density = float(row.get("amount_per_100g") or 0)
        unit = str(row.get("unit") or unit)
        contrib = frac * density
        total += contrib
        try:
            confs.append(float(row.get("confidence") or 0.7))
        except (TypeError, ValueError):
            confs.append(0.7)
        steps.append(
            {
                "ingredient": name,
                "fraction": frac,
                "density_per_100g": density,
                "contribution": contrib,
                "source": str(row.get("source") or ""),
            }
        )

    if not steps:
        return InferredValue(
            value=None,
            confidence=0.0,
            formula_id=FORMULA_NUTRIENT_EST,
            source="no_matching_estimates",
            reason=f"No density rows for nutrient={nutrient}",
            enabled=False,
        )

    conf = min(confs) if confs else confidence_for_source("ingredient_percent") / 100.0
    return InferredValue(
        value=round(total, 6),
        confidence=conf,
        formula_id=FORMULA_NUTRIENT_EST,
        source="ingredient_nutrient_estimates",
        reason=f"Σ fraction×density for {nutrient}",
        unit=unit,
        enabled=False,
        trace=tuple(steps),
    )


def properties_for_ingredient(name: str, props_df: pd.DataFrame | None = None, estimates_df: pd.DataFrame | None = None) -> list[dict[str, str]]:
    """Prefer property_tags on ingredient_nutrient_estimates; optional legacy props_df ignored."""
    _ = props_df
    key = ingredient_key(name)
    out: list[dict[str, str]] = []
    if estimates_df is not None and not estimates_df.empty and "property_tags" in estimates_df.columns:
        for _, row in estimates_df.iterrows():
            if ingredient_key(row.get("ingredient")) != key and ingredient_key(
                row.get("canonical_ingredient")
            ) != key:
                continue
            tags = str(row.get("property_tags") or "")
            for tag in tags.split("|"):
                tag = tag.strip()
                if tag:
                    out.append({"property_key": tag, "property_label": tag.replace("_", " ").title()})
    return out
