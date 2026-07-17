"""CSV loading, path resolution, and shared dataframe utilities."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

logger = logging.getLogger(__name__)

PATH_ALIASES = {
    "breed_analysis/2_evolutionary_traits": "breed_analysis/2_evolutionary_profiles",
    "breed_analysis/4_preventative_management": "breed_analysis/4_preventative_interventions",
    "breed_analysis/product_portfolio": "product_portfolio",
}

BREED_ALIASES = {
    "labrador": "Labrador Retriever",
    "golden": "Golden Retriever",
    "golden retriever": "Golden Retriever",
    "lab": "Labrador Retriever",
}


def canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def ingredient_key(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", str(value or "").lower()).strip("_")


def normalize_breed_name(name: str) -> str:
    key = str(name or "").strip().lower()
    return BREED_ALIASES.get(key, str(name or "").strip())


def parse_prevalence(raw) -> float:
    if pd.isna(raw):
        return 0.0
    text = str(raw).replace("%", "").strip()
    try:
        val = float(text)
    except ValueError:
        return 0.0
    return val / 100.0 if val > 1.0 else val


class DataRepository:
    """Loads canonical PPIE CSV matrices into pandas DataFrames."""

    def __init__(self, data_root: str | Path):
        self.data_root = Path(data_root)
        if (self.data_root / "breed_analysis").exists():
            self.base = self.data_root
        elif self.data_root.name == "breed_analysis":
            self.base = self.data_root.parent
        else:
            self.base = self.data_root
        self._cache: dict[str, pd.DataFrame] = {}

    def resolve_path(self, relative: str) -> Path:
        rel = relative.replace("\\", "/")
        candidates = [self.base / rel]
        for alias_from, alias_to in PATH_ALIASES.items():
            if rel.startswith(alias_from):
                candidates.append(self.base / rel.replace(alias_from, alias_to, 1))
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def load_csv(self, relative_path: str) -> pd.DataFrame:
        if relative_path in self._cache:
            return self._cache[relative_path].copy()
        path = self.resolve_path(relative_path)
        if not path.exists():
            logger.warning("Missing CSV: %s", path)
            return pd.DataFrame()
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df.columns = [c.strip() for c in df.columns]
        self._cache[relative_path] = df
        logger.info("Loaded %s rows from %s", len(df), path.name)
        return df.copy()

    def breeds(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/1_biological_traits/BREEDS.csv")

    def breed_conditions(self) -> pd.DataFrame:
        df = self.load_csv("breed_analysis/3_management_considerations/BREED_CONDITIONS.csv")
        if not df.empty and "prevalence" in df.columns:
            df["prevalence"] = df["prevalence"].map(parse_prevalence)
        return df

    def trait_condition_tables(self) -> pd.DataFrame:
        tables = [
            ("size", "breed_analysis/3_management_considerations/SIZE_CONDITIONS.csv", "size"),
            ("body_type", "breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv", "body_type"),
            ("coat_type", "breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv", "coat_type"),
            ("energy", "breed_analysis/3_management_considerations/ENERGY_CONDITIONS.csv", "energy"),
            ("skull_type", "breed_analysis/3_management_considerations/SKULLTYPE_CONDITIONS.csv", "skull_type"),
            ("climate", "breed_analysis/3_management_considerations/CLIMATE_CONDITIONS.csv", "climate"),
            ("lifespan", "breed_analysis/3_management_considerations/LIFESPAN_CONDITIONS.csv", "lifespan"),
            ("weakness_group", "breed_analysis/3_management_considerations/WEAKNESSGROUP_CONDITIONS.csv", "weakness_group"),
            ("function_group", "breed_analysis/3_management_considerations/FUNCTIONGROUP_CONDITIONS.csv", "function_group"),
        ]
        frames = []
        for trait_category, path, trait_col in tables:
            df = self.load_csv(path)
            if df.empty:
                continue
            df = df.copy()
            df["trait_category"] = trait_category
            df["trait_value"] = df[trait_col]
            df["prevalence"] = df["prevalence"].map(parse_prevalence)
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def trait_interactions(self) -> pd.DataFrame:
        df = self.load_csv("breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv")
        if not df.empty and "factor" in df.columns:
            df["factor"] = pd.to_numeric(df["factor"], errors="coerce").fillna(1.0)
        return df

    def mixed_breed_matrix(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/1_biological_traits/MIXED_BREED_MATRIX.csv")

    def condition_ingredients(self) -> pd.DataFrame:
        sci = self.load_csv("breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv")
        prev = self.load_csv("preventative_ingredients/CONDITION_INGREDIENTS.csv")
        if sci.empty:
            return prev
        if prev.empty:
            return sci
        return pd.concat([sci, prev], ignore_index=True).drop_duplicates(
            subset=["condition", "ingredient_name"], keep="first"
        )

    def product_catalog(self) -> pd.DataFrame:
        return self.load_csv("product_portfolio/PRODUCT_CATALOG.csv")

    def product_components(self) -> pd.DataFrame:
        return self.load_csv("product_portfolio/PRODUCT_COMPONENTS.csv")

    def product_pricing(self) -> pd.DataFrame:
        df = self.load_csv("product_portfolio/PRODUCT_PRICING.csv")
        if not df.empty:
            df["list_price_rmb"] = pd.to_numeric(df["list_price_rmb"], errors="coerce").fillna(0.0)
            df["package_units"] = pd.to_numeric(df["package_units"], errors="coerce").fillna(1.0)
        return df

    def product_feeding_rules(self) -> pd.DataFrame:
        df = self.load_csv("product_portfolio/PRODUCT_FEEDING_RULES.csv")
        if df.empty:
            return df
        wmin = df.get("weight_min_kg", df.get("min_weight_kg"))
        wmax = df.get("weight_max_kg", df.get("max_weight_kg"))
        df = df.copy()
        df["weight_min_kg"] = pd.to_numeric(wmin, errors="coerce")
        df["weight_max_kg"] = pd.to_numeric(wmax, errors="coerce")
        df["daily_amount"] = pd.to_numeric(df["daily_amount"], errors="coerce")
        return df

    def condition_activities(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/4_preventative_interventions/CONDITION_ACTIVITIES.csv")

    def trait_purposes(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv")

    def environmental_matrices(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv")

    def trait_benefits(self) -> pd.DataFrame:
        df = self.load_csv("breed_analysis/4_preventative_interventions/TRAIT_BENEFITS.csv")
        if not df.empty and "reduction_factor" in df.columns:
            df["reduction_factor"] = pd.to_numeric(df["reduction_factor"], errors="coerce").fillna(1.0)
        return df

    def mixed_breed_interactions(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv")

    def ingredient_evidence(self) -> pd.DataFrame:
        sci = self.load_csv("breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv")
        prev = self.load_csv("preventative_ingredients/INGREDIENT_EVIDENCE.csv")
        if sci.empty:
            return prev
        if prev.empty:
            return sci
        return pd.concat([sci, prev], ignore_index=True)

    def ingredient_mechanisms(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/5_scientific_nutrition/INGREDIENT_MECHANISMS.csv")

    def natural_food_sources(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/5_scientific_nutrition/NATURAL_FOOD_SOURCES.csv")

    def nutrient_priorities(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/5_scientific_nutrition/NUTRIENT_PRIORITIES.csv")

    def activity_evidence(self) -> pd.DataFrame:
        return self.load_csv("breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv")


def js_round(value: float | int) -> int:
    """Match JavaScript Math.round for non-negative values (half rounds away from zero)."""
    import math

    return int(math.floor(float(value) + 0.5))


def calculate_unit_economics(pricing_df: pd.DataFrame, product_id: str) -> float:
    """Unit cost per bag — mirrors JS unit_cost_per_bag = round((price/units)*100)/100."""
    product_row = pricing_df[pricing_df["product_id"] == product_id]
    if product_row.empty:
        return 0.0
    price = float(product_row["list_price_rmb"].values[0])
    units = float(product_row["package_units"].values[0])
    if units <= 0:
        return 0.0
    return round(price / units * 100) / 100


def units_compatible(target_unit: str, product_unit: str) -> bool:
    t = str(target_unit or "").lower().strip()
    p = str(product_unit or "").lower().strip()
    if not t or not p:
        return False
    if t == p:
        return True
    aliases = {
        "mg": {"mg"},
        "g": {"g", "mg"},
        "%": {"%"},
        "capsules": {"capsules", "capsule"},
        "billion cfu": {"billion cfu", "cfu"},
    }
    return p in aliases.get(t, set())


def feeding_rule_for_product(rules_df: pd.DataFrame, product_id: str, weight_kg: float) -> Optional[dict]:
    if rules_df.empty:
        return None
    subset = rules_df[
        (rules_df["product_id"] == product_id)
        & (rules_df["weight_min_kg"] <= weight_kg)
        & (rules_df["weight_max_kg"] >= weight_kg)
    ]
    if subset.empty:
        return None
    row = subset.iloc[0]
    return {
        "daily_amount": float(row["daily_amount"]),
        "daily_unit": str(row["daily_unit"]),
    }


def resolve_breed_rows(breeds_df: pd.DataFrame, names: Iterable[str]) -> pd.DataFrame:
    normalized = [normalize_breed_name(n) for n in names if n]
    if breeds_df.empty or not normalized:
        return pd.DataFrame()
    breed_col = "breed" if "breed" in breeds_df.columns else breeds_df.columns[0]
    mask = breeds_df[breed_col].isin(normalized)
    if not mask.any():
        mask = breeds_df[breed_col].str.lower().isin([n.lower() for n in normalized])
    return breeds_df[mask].copy()
