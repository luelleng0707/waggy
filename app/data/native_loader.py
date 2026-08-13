"""Repository-native loader — science-only warehouse → in-memory formula views.

Disk: warehouse/science/{breed,condition,ingredient,nutrition,product,physiology,evidence,runtime}
FormulaGraph never sees CSV paths.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from app.data.schemas import FileSpec, Manifest

logger = logging.getLogger(__name__)

TRAIT_TABLES = (
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

# Package policy — not product catalog facts; kept in Repository/loader (not CSVs).
PACKAGE_TIERS = pd.DataFrame(
    [
        {
            "tier_id": "essential",
            "title": "Essential Care",
            "yearly_discount_factor": "0.95",
            "staple_product_id": "SF001",
            "sort_order": "1",
        },
        {
            "tier_id": "balanced",
            "title": "Balanced Care",
            "yearly_discount_factor": "0.92",
            "staple_product_id": "SF001",
            "sort_order": "2",
        },
        {
            "tier_id": "optimal",
            "title": "Optimal Care",
            "yearly_discount_factor": "0.88",
            "staple_product_id": "SF001",
            "sort_order": "3",
        },
    ]
)

PRODUCT_DEFAULTS = pd.DataFrame(
    [
        {"key": "default_treat", "product_id": "TR001"},
        {"key": "default_supplement", "product_id": "TR011"},
        {"key": "fallback_supplement_1", "product_id": "TR003"},
        {"key": "fallback_supplement_2", "product_id": "TR007"},
        {"key": "fallback_supplement_3", "product_id": "TR008"},
    ]
)

EXT_SUPPLEMENTS_EMPTY = pd.DataFrame(
    columns=[
        "product_id",
        "supplement_type",
        "serving_size_g",
        "servings_per_pack",
        "storage_method",
        "shelf_life_days",
    ]
)


def is_native_warehouse(root: Path) -> bool:
    root = Path(root)
    if not (root / "science").exists():
        return False
    if (root / "science" / "_formula_ops").exists():
        return False
    if (root / "science" / "product" / "PRODUCT_CATALOG.csv").exists():
        return True
    if (root / "DOMAIN_REGISTRY.json").exists():
        return True
    manifest = root / "CANONICAL_MANIFEST.json"
    if manifest.exists():
        text = manifest.read_text(encoding="utf-8")
        if any(k in text for k in ("repository_native", "in_memory", "domain_driven", "science_only")):
            return True
    return (root / "science" / "breed" / "breed_conditions.csv").exists()


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _annotate(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["_csv_row"] = list(range(2, len(out) + 2))
    out["_csv_file"] = source_name
    return out


def _load_registry(root: Path) -> dict[str, str]:
    path = root / "DOMAIN_REGISTRY.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return dict(data.get("paths") or {})
    return {}


def _sci(root: Path, registry: dict[str, str], key: str, *fallback: str) -> Path:
    rel = registry.get(key)
    if rel:
        p = root / "science" / rel
        if p.exists() or not fallback:
            return p
    for fb in fallback:
        p = root / "science" / fb
        if p.exists():
            return p
    return root / "science" / (fallback[0] if fallback else key)


def _entity_name_col(df: pd.DataFrame, *candidates: str) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    return candidates[0]


def _project(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    if cols is None:
        return df
    out = df.copy() if not df.empty else pd.DataFrame(columns=cols)
    for c in cols:
        if c not in out.columns:
            out[c] = ""
    return out[cols] if len(out.columns) else pd.DataFrame(columns=cols)


def _filter_lane(df: pd.DataFrame, lane: str) -> pd.DataFrame:
    if df.empty:
        return df
    if "lane" in df.columns:
        return df[df["lane"].astype(str) == lane].drop(columns=["lane"])
    return df


def _filter_kind(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    if df.empty:
        return df
    if "record_kind" in df.columns:
        return df[df["record_kind"].astype(str) == kind].drop(columns=["record_kind"])
    return df


def build_formula_views(root: Path) -> dict[str, pd.DataFrame]:
    root = Path(root)
    sci = root / "science"
    registry = _load_registry(root)
    tables: dict[str, pd.DataFrame] = {}

    breeds = _read_csv(_sci(root, registry, "breeds", "breed/breeds.csv"))
    if not breeds.empty:
        name_col = _entity_name_col(breeds, "breed_name", "name", "breed")
        b = breeds.rename(columns={name_col: "breed"}).drop(columns=["breed_id"], errors="ignore")
        preferred = [
            "breed",
            "size",
            "body_type",
            "coat_type",
            "energy",
            "weakness_group",
            "skull_type",
            "climate",
            "lifespan",
            "function_group",
        ]
        cols = [c for c in preferred if c in b.columns] + [c for c in b.columns if c not in preferred]
        tables["breeds"] = _annotate(b[cols], "BREEDS.csv")

    products = _read_csv(
        _sci(root, registry, "products", "product/PRODUCT_CATALOG.csv", "product/products.csv")
    )
    if not products.empty:
        tables["products"] = _annotate(products, "PRODUCT_CATALOG.csv")

    aliases = _read_csv(sci / "runtime" / "aliases.csv")
    if not aliases.empty:
        a = pd.DataFrame(
            {
                "alias": aliases.get("alias", ""),
                "canonical_breed": aliases.get(
                    "canonical_name", aliases.get("canonical_breed", "")
                ),
            }
        )
        tables["breed_aliases"] = _annotate(a, "BREED_ALIASES.csv")

    breeds_ref = breeds
    conditions = _read_csv(_sci(root, registry, "conditions", "condition/conditions.csv"))
    bname = _entity_name_col(breeds_ref, "breed_name", "name") if not breeds_ref.empty else "name"
    cname = (
        _entity_name_col(conditions, "condition_name", "name") if not conditions.empty else "name"
    )
    bid_to_name = (
        {str(r["breed_id"]): str(r[bname]) for _, r in breeds_ref.iterrows()}
        if not breeds_ref.empty
        else {}
    )
    cid_to_name = (
        {str(r["condition_id"]): str(r[cname]) for _, r in conditions.iterrows()}
        if not conditions.empty
        else {}
    )

    bc = _read_csv(
        _sci(
            root,
            registry,
            "breed_conditions_entity",
            "breed/breed_conditions.csv",
            "breed/breed_condition.csv",
        )
    )
    if not bc.empty:
        rows = []
        for _, r in bc.iterrows():
            rows.append(
                {
                    "breed": bid_to_name.get(str(r.get("breed_id") or ""), ""),
                    "condition": cid_to_name.get(str(r.get("condition_id") or ""), ""),
                    "prevalence": r.get("prevalence", ""),
                    "sample_population": r.get("sample_population", ""),
                    "sample_size": r.get("sample_size", ""),
                    "source_name": r.get("source_name", ""),
                    "source_quote": r.get("source_quote", ""),
                    "source_url": r.get("source_url", ""),
                    "year": r.get("year", ""),
                    "confidence_level": r.get("evidence_level") or r.get("confidence") or "",
                }
            )
        tables["breed_conditions"] = _annotate(pd.DataFrame(rows), "BREED_CONDITIONS.csv")

    traits = _read_csv(_sci(root, registry, "traits", "physiology/traits.csv"))
    tc = _read_csv(
        _sci(
            root,
            registry,
            "trait_conditions_entity",
            "breed/trait_conditions.csv",
            "breed/trait_condition.csv",
        )
    )
    tid_meta = (
        {
            str(r["trait_id"]): (str(r["category"]), str(r["value"]))
            for _, r in traits.iterrows()
        }
        if not traits.empty
        else {}
    )
    if not tc.empty:
        by_cat: dict[str, list[dict]] = {cat: [] for cat, _, _ in TRAIT_TABLES}
        for _, r in tc.iterrows():
            meta = tid_meta.get(str(r.get("trait_id") or ""))
            if not meta:
                continue
            category, value = meta
            if category not in by_cat:
                continue
            col = next(c for cat, _t, c in TRAIT_TABLES if cat == category)
            by_cat[category].append(
                {
                    col: value,
                    "condition": cid_to_name.get(str(r.get("condition_id") or ""), ""),
                    "prevalence": r.get("prevalence", ""),
                    "sample_population": r.get("sample_population", ""),
                    "sample_size": r.get("sample_size", ""),
                    "source_name": r.get("source_name", ""),
                    "source_quote": r.get("source_quote", ""),
                    "source_url": r.get("source_url", ""),
                    "year": r.get("year", ""),
                    "confidence_level": r.get("evidence_level") or r.get("confidence") or "",
                }
            )
        file_map = {
            "size_conditions": "SIZE_CONDITIONS.csv",
            "bodytype_conditions": "BODYTYPE_CONDITIONS.csv",
            "coattype_conditions": "COATTYPE_CONDITIONS.csv",
            "energy_conditions": "ENERGY_CONDITIONS.csv",
            "skulltype_conditions": "SKULLTYPE_CONDITIONS.csv",
            "climate_conditions": "CLIMATE_CONDITIONS.csv",
            "lifespan_conditions": "LIFESPAN_CONDITIONS.csv",
            "weaknessgroup_conditions": "WEAKNESSGROUP_CONDITIONS.csv",
            "functiongroup_conditions": "FUNCTIONGROUP_CONDITIONS.csv",
        }
        for category, table, _col in TRAIT_TABLES:
            tables[table] = _annotate(pd.DataFrame(by_cat.get(category) or []), file_map[table])

    ci = _read_csv(
        _sci(
            root,
            registry,
            "condition_ingredients",
            "ingredient/condition_ingredients.csv",
        )
    )
    ci_cols = [
        "condition",
        "ingredient_name",
        "recommended_daily_dose",
        "dose_unit",
        "source_name",
        "source_quote",
        "source_url",
        "priority_rank",
        "evidence_type",
    ]
    ci_prev_cols = [c for c in ci_cols if c != "evidence_type"]
    tables["condition_ingredients_sci"] = _annotate(
        _project(_filter_lane(ci, "sci"), ci_cols), "CONDITION_INGREDIENTS.csv"
    )
    tables["condition_ingredients_prev"] = _annotate(
        _project(_filter_lane(ci, "prev"), ci_prev_cols), "CONDITION_INGREDIENTS.csv"
    )

    ie = _read_csv(
        _sci(root, registry, "ingredient_evidence", "ingredient/ingredient_evidence.csv")
    )
    ie_sci_cols = [
        "ingredient_name",
        "source_name",
        "source_quote",
        "source_url",
        "year",
        "supports_joint",
        "supports_skin",
        "supports_gut",
        "anti_inflammatory",
    ]
    ie_prev_cols = ["ingredient_name", "source_name", "source_quote", "source_url", "year"]
    tables["ingredient_evidence_sci"] = _annotate(
        _project(_filter_lane(ie, "sci"), ie_sci_cols), "INGREDIENT_EVIDENCE.csv"
    )
    tables["ingredient_evidence_prev"] = _annotate(
        _project(_filter_lane(ie, "prev"), ie_prev_cols), "INGREDIENT_EVIDENCE.csv"
    )

    # Product production tables
    tables["product_components"] = _annotate(
        _read_csv(
            _sci(root, registry, "product_components", "product/PRODUCT_COMPONENTS.csv")
        ),
        "PRODUCT_COMPONENTS.csv",
    )
    tables["product_functions"] = _annotate(
        _read_csv(_sci(root, registry, "product_functions", "product/PRODUCT_FUNCTIONS.csv")),
        "PRODUCT_FUNCTIONS.csv",
    )
    tables["product_pricing"] = _annotate(
        _read_csv(_sci(root, registry, "product_pricing", "product/PRODUCT_PRICING.csv")),
        "PRODUCT_PRICING.csv",
    )
    tables["product_feeding_rules"] = _annotate(
        _read_csv(
            _sci(root, registry, "product_feeding_rules", "product/PRODUCT_FEEDING_RULES.csv")
        ),
        "PRODUCT_FEEDING_RULES.csv",
    )
    tables["ext_treats_bakery"] = _annotate(
        _read_csv(_sci(root, registry, "ext_treats_bakery", "product/TREAT_BAKERY.csv")),
        "EXT_TREATS_BAKERY.csv",
    )
    tables["ext_supplements"] = _annotate(EXT_SUPPLEMENTS_EMPTY.copy(), "EXT_SUPPLEMENTS.csv")
    tables["package_tiers"] = _annotate(PACKAGE_TIERS.copy(), "PACKAGE_TIERS.csv")
    tables["product_defaults"] = _annotate(PRODUCT_DEFAULTS.copy(), "PRODUCT_DEFAULTS.csv")

    FACT_DISPLAY = {
        "mixed_breed_matrix": "MIXED_BREED_MATRIX.csv",
        "mixed_breed_interactions": "MIXED_BREED_INTERACTIONS.csv",
        "trait_purposes": "TRAIT_PURPOSES.csv",
        "environmental_matrices": "ENVIRONMENTAL_MATRICES.csv",
        "trait_attribute_explanations": "TRAIT_ATTRIBUTE_EXPLANATIONS.csv",
        "trait_contribution_weights": "TRAIT_CONTRIBUTION_WEIGHTS.csv",
        "clinical_risk_timeline": "CLINICAL_RISK_TIMELINE.csv",
        "activity_prescription_rules": "ACTIVITY_PRESCRIPTION_RULES.csv",
        "grooming_observation_defs": "GROOMING_OBSERVATION_DEFS.csv",
        "condition_activities": "CONDITION_ACTIVITIES.csv",
        "condition_protocols": "CONDITION_PROTOCOLS.csv",
        "ingredient_aliases": "INGREDIENT_ALIASES.csv",
        "ingredient_mechanisms": "INGREDIENT_MECHANISMS.csv",
        "ingredient_nutrient_estimates": "INGREDIENT_NUTRIENT_ESTIMATES.csv",
        "natural_food_sources": "NATURAL_FOOD_SOURCES.csv",
        "nutrient_priorities": "NUTRIENT_PRIORITIES.csv",
        "trait_benefits": "TRAIT_BENEFITS.csv",
        "trait_interactions": "TRAIT_INTERACTIONS.csv",
        "activity_evidence": "ACTIVITY_EVIDENCE.csv",
        "clinical_evidence_base": "CLINICAL_EVIDENCE_BASE.csv",
    }

    path_fallbacks: dict[str, tuple[str, ...]] = {
        "environmental_matrices": (
            "breed_environment",
            "breed/breed_environment.csv",
        ),
        "condition_activities": ("condition_activities", "breed/breed_activity.csv"),
        "clinical_risk_timeline": (
            "clinical_risk_timeline",
            "condition/clinical_timelines.csv",
        ),
        "clinical_evidence_base": (
            "clinical_evidence_base",
            "evidence/clinical_evidence.csv",
        ),
        "grooming_observation_defs": (
            "grooming_observation_defs",
            "condition/grooming_observations.csv",
        ),
        "ingredient_nutrient_estimates": (
            "ingredient_nutrient_estimates",
            "nutrition/food_nutrients.csv",
        ),
        "natural_food_sources": ("natural_food_sources", "nutrition/food_sources.csv"),
        "mixed_breed_interactions": (
            "mixed_breed_interactions",
            "breed/mixed_breed_interactions.csv",
        ),
        "mixed_breed_matrix": ("mixed_breed_matrix", "breed/mixed_breed_matrix.csv"),
        "trait_interactions": (
            "trait_interactions",
            "breed/mixed_breed_interactions.csv",
        ),
        "trait_purposes": ("trait_purposes", "physiology/trait_science.csv"),
        "trait_attribute_explanations": (
            "trait_attribute_explanations",
            "physiology/trait_science.csv",
        ),
        "trait_contribution_weights": (
            "trait_contribution_weights",
            "physiology/trait_science.csv",
        ),
        "activity_evidence": ("activity_evidence", "breed/activity_science.csv"),
        "activity_prescription_rules": (
            "activity_prescription_rules",
            "breed/activity_science.csv",
        ),
        "condition_protocols": ("condition_protocols", "condition/condition_protocols.csv"),
        "ingredient_aliases": ("ingredient_aliases", "ingredient/ingredient_aliases.csv"),
        "ingredient_mechanisms": (
            "ingredient_mechanisms",
            "ingredient/ingredient_mechanisms.csv",
        ),
        "nutrient_priorities": ("nutrient_priorities", "nutrition/nutrient_priorities.csv"),
        "trait_benefits": ("trait_benefits", "physiology/trait_benefits.csv"),
    }

    VIEW_PROJECT: dict[str, tuple[str, list[str]]] = {
        "trait_purposes": (
            "purpose",
            [
                "trait_category",
                "trait_value",
                "biological_purpose",
                "advantage_summary",
                "source_name",
                "source_quote",
                "source_url",
            ],
        ),
        "trait_attribute_explanations": (
            "explanation",
            [
                "trait_category",
                "trait_value",
                "card_title",
                "explanation",
                "related_conditions",
                "evidence_level",
                "evidence_id",
                "source_csv",
                "source_name",
                "source_url",
            ],
        ),
        "trait_contribution_weights": (
            "weight",
            [
                "trait_category",
                "trait_value",
                "condition",
                "risk_delta",
                "unit",
                "source_csv",
                "evidence_id",
                "mechanism_note",
            ],
        ),
        "activity_evidence": (
            "evidence",
            ["activity_name", "source_name", "source_quote", "source_url", "year"],
        ),
        "activity_prescription_rules": (
            "prescription",
            [
                "energy",
                "size",
                "body_type",
                "age_stage",
                "daily_km",
                "walk_morning_min",
                "walk_evening_min",
                "weekly_km",
                "mental_enrichment",
                "swimming",
                "fetch",
                "training",
                "recovery_note",
                "source_name",
                "source_url",
            ],
        ),
    }

    for table, csv_name in FACT_DISPLAY.items():
        if table in tables:
            continue
        fb = path_fallbacks.get(table)
        if fb:
            reg_key, *paths = fb
            path = _sci(root, registry, reg_key, *paths)
        else:
            path = _sci(root, registry, table, f"{table}.csv")
        df = _read_csv(path)
        if table in VIEW_PROJECT:
            kind, cols = VIEW_PROJECT[table]
            df = _filter_kind(df, kind)
            df = _project(df, cols)
        tables[table] = _annotate(df, csv_name)

    logger.info("Native formula views built: %s tables", len(tables))
    return tables


def load_native_warehouse(root: Path) -> tuple[Manifest, dict[str, pd.DataFrame], list[Path]]:
    root = Path(root)
    tables = build_formula_views(root)
    files: list[FileSpec] = []
    paths: list[Path] = []
    science = root / "science"
    if science.exists():
        for path in sorted(science.rglob("*.csv")):
            paths.append(path)
    for name, df in sorted(tables.items()):
        req = tuple(c for c in df.columns if not str(c).startswith("_"))[:1]
        files.append(
            FileSpec(
                path=f"memory://{name}",
                table=name,
                primary_key=(),
                required_columns=req,
                allow_empty=True,
            )
        )
    manifest = Manifest(version="5.0.0-science", modules=("science",), files=tuple(files))
    return manifest, tables, paths
