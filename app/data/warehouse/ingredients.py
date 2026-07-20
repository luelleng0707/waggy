"""Joined ingredient view — Phase 2 convenience API (formulas still use DataRepository)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app.agent.condition_lookup import ingredient_key
from app.data.repository import DataPlatform


@dataclass
class IngredientRecord:
    ingredient_name: str
    ingredient_key: str
    evidence: dict[str, Any] | None = None
    mechanisms: list[dict[str, Any]] = field(default_factory=list)
    foods: list[dict[str, Any]] = field(default_factory=list)
    nutrient_values: list[dict[str, Any]] = field(default_factory=list)
    studies: list[dict[str, Any]] = field(default_factory=list)
    condition_links: list[dict[str, Any]] = field(default_factory=list)


class IngredientRepository:
    """Already-joined ingredient records. Does not alter formula math."""

    def __init__(self, platform: DataPlatform):
        self.platform = platform

    def get(self, name_or_key: str) -> IngredientRecord | None:
        key = ingredient_key(name_or_key)
        name = str(name_or_key or "").strip()
        evidence = None
        ev = self.platform.ingredient_evidence()
        if not ev.empty:
            for col in ("ingredient_key", "ingredient_name", "ingredient"):
                if col not in ev.columns:
                    continue
                hit = ev[ev[col].astype(str).map(ingredient_key) == key]
                if hit.empty:
                    hit = ev[ev[col].astype(str).str.lower() == name.lower()]
                if not hit.empty:
                    evidence = hit.iloc[0].to_dict()
                    name = str(evidence.get("ingredient_name") or name)
                    break

        mechanisms: list[dict[str, Any]] = []
        mech = self.platform.ingredient_mechanisms()
        if not mech.empty:
            for _, m in mech.iterrows():
                nname = str(m.get("nutrient_name") or "")
                iname = str(m.get("ingredient_name") or "")
                if key in (ingredient_key(nname), ingredient_key(iname)) or nname.lower() == name.lower() or iname.lower() == name.lower():
                    mechanisms.append(m.to_dict())

        foods: list[dict[str, Any]] = []
        nat = self.platform.natural_food_sources()
        if not nat.empty:
            for col in ("ingredient_name", "nutrient_name", "ingredient"):
                if col not in nat.columns:
                    continue
                hit = nat[nat[col].astype(str).map(ingredient_key) == key]
                if hit.empty:
                    hit = nat[nat[col].astype(str).str.lower() == name.lower()]
                for _, r in hit.iterrows():
                    foods.append(r.to_dict())

        nutrients: list[dict[str, Any]] = []
        est = self.platform._frame("ingredient_nutrient_estimates")
        if not est.empty:
            for col in ("ingredient_name", "ingredient", "ingredient_key"):
                if col not in est.columns:
                    continue
                hit = est[est[col].astype(str).map(ingredient_key) == key]
                for _, r in hit.iterrows():
                    nutrients.append(r.to_dict())

        links: list[dict[str, Any]] = []
        ci = self.platform.condition_ingredients()
        if not ci.empty and "ingredient_name" in ci.columns:
            hit = ci[ci["ingredient_name"].astype(str).map(ingredient_key) == key]
            links = [r.to_dict() for _, r in hit.iterrows()]

        studies: list[dict[str, Any]] = []
        if evidence:
            studies.append(
                {
                    "source_name": evidence.get("source_name"),
                    "source_quote": evidence.get("source_quote"),
                    "source_url": evidence.get("source_url"),
                    "year": evidence.get("year"),
                }
            )

        if evidence is None and not mechanisms and not foods and not links:
            return None
        return IngredientRecord(
            ingredient_name=name,
            ingredient_key=key,
            evidence=evidence,
            mechanisms=mechanisms,
            foods=foods,
            nutrient_values=nutrients,
            studies=studies,
            condition_links=links,
        )
