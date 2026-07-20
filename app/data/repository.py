"""Canonical data repository — no calculations, load/index/serve only."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable, Optional

import pandas as pd

from app.data.cache import PlatformMeta, build_meta
from app.data.loader import load_all_tables, resolve_csv_path
from app.data.schemas import Manifest
from app.data.validators import DataValidationError, validate_tables

logger = logging.getLogger(__name__)


def parse_prevalence(raw) -> float:
    if pd.isna(raw):
        return 0.0
    text = str(raw).replace("%", "").strip()
    try:
        val = float(text)
    except ValueError:
        return 0.0
    return val / 100.0 if val > 1.0 else val


TRAIT_CONDITION_SOURCES = (
    ("size", "size_conditions", "size"),
    ("body_type", "bodytype_conditions", "body_type"),
    ("coat_type", "coattype_conditions", "coat_type"),
    ("energy", "energy_conditions", "energy"),
    ("skull_type", "skulltype_conditions", "skull_type"),
    ("climate", "climate_conditions", "climate"),
    ("lifespan", "lifespan_conditions", "lifespan"),
    ("weakness_group", "weaknessgroup_conditions", "weakness_group"),
    ("function_group", "functiongroup_conditions", "function_group"),
)


class DataPlatform:
    """In-memory relational snapshot of every CSV under data/."""

    def __init__(
        self,
        data_root: str | Path,
        *,
        strict: bool = True,
    ):
        self.data_root = Path(data_root)
        manifest, tables, paths = load_all_tables(self.data_root)
        report = validate_tables(manifest, tables)
        if strict and not report.ok:
            raise DataValidationError(report)
        self.manifest = manifest
        self._tables = tables
        self.meta = build_meta(manifest.version, self.data_root, paths)
        self._indexes: dict[str, Any] = {}
        self._build_indexes()

    # ── metadata ──────────────────────────────────────────────
    @property
    def version(self) -> str:
        return self.meta.version

    @property
    def loaded_at(self) -> str:
        return self.meta.loaded_at

    @property
    def csv_hash(self) -> str:
        return self.meta.csv_hash

    @property
    def file_count(self) -> int:
        return self.meta.file_count

    def table(self, name: str) -> pd.DataFrame:
        if name not in self._tables:
            raise KeyError(f"Unknown table: {name}")
        return self._tables[name].copy()

    def _frame(self, name: str) -> pd.DataFrame:
        return self._tables.get(name, pd.DataFrame()).copy()

    def _build_indexes(self) -> None:
        aliases = self._frame("breed_aliases")
        mapping: dict[str, str] = {}
        if not aliases.empty:
            for _, row in aliases.iterrows():
                mapping[str(row["alias"]).strip().lower()] = str(row["canonical_breed"]).strip()
        self._indexes["breed_aliases"] = mapping

        ing = self._frame("ingredient_aliases")
        groups: dict[str, set[str]] = {}
        if not ing.empty:
            for _, row in ing.iterrows():
                canon = str(row["canonical_key"]).strip().lower()
                alias = str(row["alias_key"]).strip().lower()
                groups.setdefault(canon, set()).update({canon, alias})
        self._indexes["ingredient_alias_groups"] = groups

        defaults = self._frame("product_defaults")
        self._indexes["product_defaults"] = {
            str(r["key"]): str(r["product_id"])
            for _, r in defaults.iterrows()
        } if not defaults.empty else {}

    # ── public domain accessors (engine-facing) ───────────────
    @property
    def products(self) -> pd.DataFrame:
        return self.product_catalog()

    @property
    def breeds(self) -> pd.DataFrame:
        return self._frame("breeds")

    @property
    def conditions(self) -> pd.DataFrame:
        return self.breed_conditions()

    @property
    def ingredients(self) -> pd.DataFrame:
        return self.condition_ingredients()

    @property
    def activities(self) -> pd.DataFrame:
        return self.condition_activities()

    @property
    def protocols(self) -> pd.DataFrame:
        return self._frame("condition_protocols")

    def breed_alias_map(self) -> dict[str, str]:
        return dict(self._indexes["breed_aliases"])

    def ingredient_alias_groups(self) -> dict[str, set[str]]:
        return {k: set(v) for k, v in self._indexes["ingredient_alias_groups"].items()}

    def product_defaults(self) -> dict[str, str]:
        return dict(self._indexes["product_defaults"])

    def package_tiers(self) -> pd.DataFrame:
        df = self._frame("package_tiers")
        if df.empty:
            return df
        df = df.copy()
        df["yearly_discount_factor"] = pd.to_numeric(
            df["yearly_discount_factor"], errors="coerce"
        ).fillna(1.0)
        df["sort_order"] = pd.to_numeric(df["sort_order"], errors="coerce").fillna(0)
        return df.sort_values("sort_order")

    def package_tier_map(self) -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for _, row in self.package_tiers().iterrows():
            tier = str(row["tier_id"])
            out[tier] = {
                "tier_id": tier,
                "title": str(row["title"]),
                "yearly_discount_factor": float(row["yearly_discount_factor"]),
                "staple_product_id": str(row["staple_product_id"]),
                "sort_order": int(row["sort_order"]),
            }
        return out

    def normalize_breed_name(self, name: str) -> str:
        key = str(name or "").strip().lower()
        return self.breed_alias_map().get(key, str(name or "").strip())

    def breeds_df(self) -> pd.DataFrame:
        return self._frame("breeds")

    def breed_conditions(self) -> pd.DataFrame:
        df = self._frame("breed_conditions")
        if not df.empty and "prevalence" in df.columns:
            df = df.copy()
            df["prevalence"] = df["prevalence"].map(parse_prevalence)
        return df

    def trait_condition_tables(self) -> pd.DataFrame:
        frames = []
        for trait_category, table, trait_col in TRAIT_CONDITION_SOURCES:
            df = self._frame(table)
            if df.empty:
                continue
            df = df.copy()
            df["trait_category"] = trait_category
            df["trait_value"] = df[trait_col]
            if "prevalence" in df.columns:
                df["prevalence"] = df["prevalence"].map(parse_prevalence)
            if "_csv_file" not in df.columns or df["_csv_file"].eq("").all():
                df["_csv_file"] = f"{table.upper()}.csv".replace("CONDITIONS", "CONDITIONS")
                # Prefer human filenames for known tables
                file_map = {
                    "size_conditions": "SIZE_CONDITIONS.csv",
                    "bodytype_conditions": "BODYTYPE_CONDITIONS.csv",
                    "coattype_conditions": "COATTYPE_CONDITIONS.csv",
                    "energy_conditions": "ENERGY_CONDITIONS.csv",
                    "skulltype_conditions": "SKULLTYPE_CONDITIONS.csv",
                    "climate_conditions": "CLIMATE_CONDITIONS.csv",
                    "functiongroup_conditions": "FUNCTIONGROUP_CONDITIONS.csv",
                    "weaknessgroup_conditions": "WEAKNESSGROUP_CONDITIONS.csv",
                    "lifespan_conditions": "LIFESPAN_CONDITIONS.csv",
                }
                df["_csv_file"] = file_map.get(table, f"{table}.csv")
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def trait_interactions(self) -> pd.DataFrame:
        df = self._frame("trait_interactions")
        if not df.empty and "factor" in df.columns:
            df = df.copy()
            df["factor"] = pd.to_numeric(df["factor"], errors="coerce").fillna(1.0)
        return df

    def mixed_breed_matrix(self) -> pd.DataFrame:
        return self._frame("mixed_breed_matrix")

    def mixed_breed_interactions(self) -> pd.DataFrame:
        return self._frame("mixed_breed_interactions")

    def condition_ingredients(self) -> pd.DataFrame:
        sci = self._frame("condition_ingredients_sci")
        prev = self._frame("condition_ingredients_prev")
        if sci.empty:
            return prev
        if prev.empty:
            return sci
        return pd.concat([sci, prev], ignore_index=True).drop_duplicates(
            subset=["condition", "ingredient_name"], keep="first"
        )

    def product_catalog(self) -> pd.DataFrame:
        return self._frame("products")

    def active_products(self) -> pd.DataFrame:
        df = self.product_catalog()
        if df.empty:
            return df
        status = df.get("status", pd.Series(["active"] * len(df))).astype(str).str.lower()
        return df[status.isin(["active", ""])].copy()

    def product_components(self) -> pd.DataFrame:
        return self._frame("product_components")

    def product_pricing(self) -> pd.DataFrame:
        df = self._frame("product_pricing")
        if not df.empty:
            df = df.copy()
            df["list_price_rmb"] = pd.to_numeric(df["list_price_rmb"], errors="coerce").fillna(0.0)
            df["package_units"] = pd.to_numeric(df["package_units"], errors="coerce").fillna(1.0)
        return df

    def product_feeding_rules(self) -> pd.DataFrame:
        df = self._frame("product_feeding_rules")
        if df.empty:
            return df
        wmin = df.get("weight_min_kg", df.get("min_weight_kg"))
        wmax = df.get("weight_max_kg", df.get("max_weight_kg"))
        df = df.copy()
        df["weight_min_kg"] = pd.to_numeric(wmin, errors="coerce")
        df["weight_max_kg"] = pd.to_numeric(wmax, errors="coerce")
        df["daily_amount"] = pd.to_numeric(df["daily_amount"], errors="coerce")
        return df

    def ext_supplements(self) -> pd.DataFrame:
        return self._frame("ext_supplements")

    def ext_treats_bakery(self) -> pd.DataFrame:
        return self._frame("ext_treats_bakery")

    def product_functions(self) -> pd.DataFrame:
        return self._frame("product_functions")

    def condition_activities(self) -> pd.DataFrame:
        return self._frame("condition_activities")

    def trait_purposes(self) -> pd.DataFrame:
        return self._frame("trait_purposes")

    def environmental_matrices(self) -> pd.DataFrame:
        return self._frame("environmental_matrices")

    def trait_benefits(self) -> pd.DataFrame:
        df = self._frame("trait_benefits")
        if not df.empty and "reduction_factor" in df.columns:
            df = df.copy()
            df["reduction_factor"] = pd.to_numeric(df["reduction_factor"], errors="coerce").fillna(1.0)
        return df

    def ingredient_evidence(self) -> pd.DataFrame:
        sci = self._frame("ingredient_evidence_sci")
        prev = self._frame("ingredient_evidence_prev")
        if sci.empty:
            return prev
        if prev.empty:
            return sci
        return pd.concat([sci, prev], ignore_index=True)

    def ingredient_mechanisms(self) -> pd.DataFrame:
        return self._frame("ingredient_mechanisms")

    def natural_food_sources(self) -> pd.DataFrame:
        return self._frame("natural_food_sources")

    def nutrient_priorities(self) -> pd.DataFrame:
        return self._frame("nutrient_priorities")

    def activity_evidence(self) -> pd.DataFrame:
        return self._frame("activity_evidence")

    def clinical_evidence_base(self) -> pd.DataFrame:
        return self._frame("clinical_evidence_base")

    def trait_attribute_explanations(self) -> pd.DataFrame:
        return self._frame("trait_attribute_explanations")

    def trait_contribution_weights(self) -> pd.DataFrame:
        return self._frame("trait_contribution_weights")

    def clinical_risk_timeline(self) -> pd.DataFrame:
        return self._frame("clinical_risk_timeline")

    def activity_prescription_rules(self) -> pd.DataFrame:
        return self._frame("activity_prescription_rules")

    def grooming_observation_defs(self) -> pd.DataFrame:
        return self._frame("grooming_observation_defs")

    def condition_protocols(self) -> pd.DataFrame:
        return self._frame("condition_protocols")

    def is_active_product_id(self, product_id: str) -> bool:
        pid = str(product_id or "")
        if not pid:
            return False
        catalog = self.active_products()
        if catalog.empty:
            return False
        return pid in set(catalog["product_id"].astype(str))

    def catalog_api_rows(self) -> list[dict[str, Any]]:
        """Shop / catalog payload — entirely from PRODUCT_CATALOG ⨝ PRODUCT_PRICING."""
        catalog = self.active_products()
        pricing = self.product_pricing()
        rows: list[dict[str, Any]] = []
        for _, rec in catalog.iterrows():
            pid = str(rec.get("product_id") or "")
            price = 0.0
            package_units = 1.0
            unit_label = "unit"
            if not pricing.empty and pid:
                prow = pricing[pricing["product_id"] == pid]
                if not prow.empty:
                    price = float(prow.iloc[0].get("list_price_rmb") or 0)
                    package_units = float(prow.iloc[0].get("package_units") or 1)
                    unit_label = str(prow.iloc[0].get("unit_label") or "unit")
            product_name = str(rec.get("product_name") or pid)
            # Pass through every catalog column so new CSV fields appear without code changes.
            row: dict[str, Any] = {
                str(k): ("" if v is None else str(v)) for k, v in rec.items()
            }
            row.update({
                "product_id": pid,
                "product_name": product_name,
                "name": product_name,  # alias for older clients
                "brand": str(rec.get("brand") or ""),
                "category": str(rec.get("category") or "General"),
                "subcategory": str(rec.get("subcategory") or ""),
                "status": str(rec.get("status") or "active"),
                "image_url": str(rec.get("image_url") or ""),
                "purchase_url": str(rec.get("purchase_url") or ""),
                "list_price_rmb": price,
                "price_rmb": price,
                "package_units": package_units,
                "unit_label": unit_label,
                "currency": "CNY",
            })
            rows.append(row)
        return rows

    def store_api_rows(self, weight_kg: float | None = None) -> list[dict[str, Any]]:
        """
        Full storefront records: catalog ⨝ pricing ⨝ components ⨝ feeding
        ⨝ EXT_SUPPLEMENTS ⨝ EXT_TREATS_BAKERY ⨝ PRODUCT_FUNCTIONS.
        """
        base_rows = self.catalog_api_rows()
        components = self.product_components()
        feeding = self.product_feeding_rules()
        supplements = self.ext_supplements()
        bakery = self.ext_treats_bakery()
        functions = self.product_functions()

        out: list[dict[str, Any]] = []
        for row in base_rows:
            pid = str(row.get("product_id") or "")
            comps: list[dict[str, Any]] = []
            if not components.empty and pid:
                hits = components[components["product_id"] == pid]
                for _, c in hits.iterrows():
                    comps.append({
                        "component_type": str(c.get("component_type") or ""),
                        "component_name": str(c.get("component_name") or ""),
                        "value": str(c.get("value") or ""),
                        "unit": str(c.get("unit") or ""),
                        "evidence_level": str(c.get("evidence_level") or ""),
                        "notes": str(c.get("notes") or ""),
                    })

            rules: list[dict[str, Any]] = []
            feeding_for_weight: dict[str, Any] | None = None
            if not feeding.empty and pid:
                hits = feeding[feeding["product_id"] == pid]
                for _, f in hits.iterrows():
                    wmin = float(f.get("weight_min_kg") or f.get("min_weight_kg") or 0)
                    wmax = float(f.get("weight_max_kg") or f.get("max_weight_kg") or 0)
                    amount = float(f.get("daily_amount") or 0)
                    unit = str(f.get("daily_unit") or "")
                    rule = {
                        "min_weight_kg": wmin,
                        "max_weight_kg": wmax,
                        "daily_amount": amount,
                        "daily_unit": unit,
                        "display": f"{amount:g}{unit}/day",
                    }
                    rules.append(rule)
                    if (
                        weight_kg is not None
                        and feeding_for_weight is None
                        and wmin <= float(weight_kg) <= wmax
                    ):
                        feeding_for_weight = rule

            supp = None
            if not supplements.empty and pid:
                hit = supplements[supplements["product_id"] == pid]
                if not hit.empty:
                    s = hit.iloc[0]
                    supp = {str(k): ("" if v is None else str(v)) for k, v in s.items()}

            treat = None
            if not bakery.empty and pid:
                hit = bakery[bakery["product_id"] == pid]
                if not hit.empty:
                    t = hit.iloc[0]
                    treat = {str(k): ("" if v is None else str(v)) for k, v in t.items()}

            funcs: list[dict[str, Any]] = []
            if not functions.empty and pid:
                hits = functions[functions["product_id"] == pid]
                for _, fn in hits.iterrows():
                    funcs.append({
                        "function": str(fn.get("function") or ""),
                        "confidence": str(fn.get("confidence") or ""),
                    })

            enriched = {
                **row,
                "components": comps,
                "feeding_rules": rules,
                "feeding_for_weight": feeding_for_weight,
                "supplement": supp,
                "bakery": treat,
                "functions": funcs,
            }
            out.append(enriched)
        return out


class DataRepository:
    """
    Engine-facing facade.

    Preserves historical method names used by app.agent.* while delegating
    every CSV read to the live DataPlatform (hot-reload safe).
    """

    def __init__(self, data_root: str | Path, platform: DataPlatform | None = None):
        self.data_root = Path(data_root)
        self._pinned = platform
        if platform is None:
            try:
                from app.data.runtime import get_platform

                get_platform()
            except RuntimeError:
                from app.data.runtime import bootstrap

                bootstrap(self.data_root, strict=True)

    @property
    def platform(self) -> DataPlatform:
        if self._pinned is not None:
            return self._pinned
        from app.data.runtime import get_platform

        return get_platform()

    @property
    def version(self) -> str:
        return self.platform.version

    @property
    def loaded_at(self) -> str:
        return self.platform.loaded_at

    @property
    def csv_hash(self) -> str:
        return self.platform.csv_hash

    @property
    def file_count(self) -> int:
        return self.platform.file_count

    # Compatibility: some call sites used load_csv / resolve_path
    def resolve_path(self, relative: str) -> Path:
        return resolve_csv_path(self.data_root, relative)

    def load_csv(self, relative_path: str) -> pd.DataFrame:
        """Legacy path-based load — prefer typed accessors. Reads via platform tables when known."""
        rel = relative_path.replace("\\", "/")
        for spec in self.platform.manifest.files:
            if spec.path == rel:
                return self.platform.table(spec.table)
        # Fallback for unexpected paths (should not happen if manifest is complete)
        path = self.resolve_path(rel)
        if not path.exists():
            logger.warning("Missing CSV: %s", path)
            return pd.DataFrame()
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        df.columns = [c.strip() for c in df.columns]
        return df

    def breeds(self) -> pd.DataFrame:
        return self.platform.breeds_df()

    def breed_conditions(self) -> pd.DataFrame:
        return self.platform.breed_conditions()

    def trait_condition_tables(self) -> pd.DataFrame:
        return self.platform.trait_condition_tables()

    def trait_interactions(self) -> pd.DataFrame:
        return self.platform.trait_interactions()

    def mixed_breed_matrix(self) -> pd.DataFrame:
        return self.platform.mixed_breed_matrix()

    def mixed_breed_interactions(self) -> pd.DataFrame:
        return self.platform.mixed_breed_interactions()

    def condition_ingredients(self) -> pd.DataFrame:
        return self.platform.condition_ingredients()

    def product_catalog(self) -> pd.DataFrame:
        return self.platform.product_catalog()

    def active_products(self) -> pd.DataFrame:
        return self.platform.active_products()

    def product_components(self) -> pd.DataFrame:
        return self.platform.product_components()

    def product_pricing(self) -> pd.DataFrame:
        return self.platform.product_pricing()

    def product_feeding_rules(self) -> pd.DataFrame:
        return self.platform.product_feeding_rules()

    def condition_activities(self) -> pd.DataFrame:
        return self.platform.condition_activities()

    def trait_purposes(self) -> pd.DataFrame:
        return self.platform.trait_purposes()

    def environmental_matrices(self) -> pd.DataFrame:
        return self.platform.environmental_matrices()

    def trait_benefits(self) -> pd.DataFrame:
        return self.platform.trait_benefits()

    def ingredient_evidence(self) -> pd.DataFrame:
        return self.platform.ingredient_evidence()

    def ingredient_mechanisms(self) -> pd.DataFrame:
        return self.platform.ingredient_mechanisms()

    def natural_food_sources(self) -> pd.DataFrame:
        return self.platform.natural_food_sources()

    def nutrient_priorities(self) -> pd.DataFrame:
        return self.platform.nutrient_priorities()

    def activity_evidence(self) -> pd.DataFrame:
        return self.platform.activity_evidence()

    def clinical_evidence_base(self) -> pd.DataFrame:
        return self.platform.clinical_evidence_base()

    def trait_attribute_explanations(self) -> pd.DataFrame:
        return self.platform.trait_attribute_explanations()

    def trait_contribution_weights(self) -> pd.DataFrame:
        return self.platform.trait_contribution_weights()

    def clinical_risk_timeline(self) -> pd.DataFrame:
        return self.platform.clinical_risk_timeline()

    def activity_prescription_rules(self) -> pd.DataFrame:
        return self.platform.activity_prescription_rules()

    def grooming_observation_defs(self) -> pd.DataFrame:
        return self.platform.grooming_observation_defs()

    def condition_protocols(self) -> pd.DataFrame:
        return self.platform.condition_protocols()

    def ext_supplements(self) -> pd.DataFrame:
        return self.platform.ext_supplements()

    def ext_treats_bakery(self) -> pd.DataFrame:
        return self.platform.ext_treats_bakery()

    def product_functions(self) -> pd.DataFrame:
        return self.platform.product_functions()

    def package_tiers(self) -> pd.DataFrame:
        return self.platform.package_tiers()

    def package_tier_map(self) -> dict[str, dict[str, Any]]:
        return self.platform.package_tier_map()

    def product_defaults(self) -> dict[str, str]:
        return self.platform.product_defaults()

    def ingredient_alias_groups(self) -> dict[str, set[str]]:
        return self.platform.ingredient_alias_groups()

    def is_active_product_id(self, product_id: str) -> bool:
        return self.platform.is_active_product_id(product_id)

    def catalog_api_rows(self) -> list[dict[str, Any]]:
        return self.platform.catalog_api_rows()

    def store_api_rows(self, weight_kg: float | None = None) -> list[dict[str, Any]]:
        return self.platform.store_api_rows(weight_kg=weight_kg)


def feeding_rule_for_product(
    rules_df: pd.DataFrame, product_id: str, weight_kg: float
) -> Optional[dict]:
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


def resolve_breed_rows(breeds_df: pd.DataFrame, names: Iterable[str], platform: DataPlatform | None = None) -> pd.DataFrame:
    if platform is not None:
        normalized = [platform.normalize_breed_name(n) for n in names if n]
    else:
        from app.data.runtime import get_platform

        try:
            plat = get_platform()
            normalized = [plat.normalize_breed_name(n) for n in names if n]
        except RuntimeError:
            normalized = [str(n).strip() for n in names if n]
    if breeds_df.empty or not normalized:
        return pd.DataFrame()
    breed_col = "breed" if "breed" in breeds_df.columns else breeds_df.columns[0]
    mask = breeds_df[breed_col].isin(normalized)
    if not mask.any():
        mask = breeds_df[breed_col].str.lower().isin([n.lower() for n in normalized])
    return breeds_df[mask].copy()
