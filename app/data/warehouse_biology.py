"""Project warehouse/biology + warehouse/prevention CSVs into RISK_V2_1 tables.

ROOT CAUSE (OMEGA 10):
    Runtime previously required warehouse/science/ (native_loader.is_native_warehouse).
    Canonical scientific rows live in warehouse/biology/ and warehouse/prevention/.
    warehouse/manifest.yaml points at warehouse/science, which does not exist, so
    DataPlatform loaded empty tables. RISK_V2_1 then returned no healthInsights.
    The presentation adapter previously filled Health Analysis from a synthetic
    demo breed-care table. That path is retired. Health Analysis now reads
    these warehouse tables via app.data.scientific_care.resolve_care_model.

This module is the production loader for those biology CSVs. It does not invent
prevalence, citations, or IDs. Intern phenotype in breed_traits.csv is loaded
as-is (MISSING_PROVENANCE where intern had no study).

Audit answers (see also docs/WAGGY_SYSTEM.md):

1. Loaded here from warehouse/biology and warehouse/prevention, via
   app.data.loader.load_all_tables → load_native_warehouse, then
   merge_biology_into when warehouse/biology/breeds.csv exists.
2. Modules:
   - breeds: biology/breeds.csv
   - breed-condition associations / observed prevalence: biology/observed_breed_conditions.csv
   - body-type / coat / size associations: biology/trait_condition_associations.csv
   - condition activities: prevention/condition_activities.csv
   - condition/nutrient and condition/ingredient: prevention/condition_ingredients.csv
   - estimated prevalence: trait tables + breed_traits (currently header-only)
3. Canonical CSVs are loaded at runtime when biology/breeds.csv exists.
4. Application root is resolve_clinical_root() → warehouse/.
5. IDs: breed_id / condition_id are preserved as columns; RISK_V2_1 matches on
   breed_name / condition_name after projection.
6. Aliases: German Shepherd → German Shepherd Dog (warehouse canonical name).
7. Mixed breed: RISK_V2_1 apply_significance_logic unions observed rows.
8. No species/status/year filter is applied here (migrated rows are kept).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from app.data.native_loader import (
    PACKAGE_TIERS,
    PRODUCT_DEFAULTS,
    TRAIT_TABLES,
    _annotate,
)
from app.data.schemas import FileSpec, Manifest

logger = logging.getLogger(__name__)

TRAIT_COL = {cat: col for cat, _table, col in TRAIT_TABLES}
TRAIT_TABLE = {cat: table for cat, table, _col in TRAIT_TABLES}

# Display aliases only — not scientific facts.
_BREED_ALIASES = (
    ("German Shepherd", "German Shepherd Dog"),
    ("GSD", "German Shepherd Dog"),
    ("Lab", "Labrador Retriever"),
    ("Labrador", "Labrador Retriever"),
    ("Golden", "Golden Retriever"),
)


def is_biology_warehouse(root: Path) -> bool:
    return (Path(root) / "biology" / "breeds.csv").exists()


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _col(df: pd.DataFrame, *names: str, default: str = "") -> pd.Series:
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


def _apply_breed_traits(breeds: pd.DataFrame, traits: pd.DataFrame) -> pd.DataFrame:
    """Copy warehouse breed_traits onto breed rows. Does not invent missing traits."""
    out = breeds.copy()
    for _, _, col in TRAIT_TABLES:
        if col not in out.columns:
            out[col] = ""
    if traits.empty or "breed_id" not in traits.columns:
        return out
    by_id = {str(r.get("breed_id") or ""): i for i, r in out.iterrows()}
    for _, row in traits.iterrows():
        bid = str(row.get("breed_id") or "")
        idx = by_id.get(bid)
        if idx is None:
            continue
        cat = str(row.get("trait_name") or "").strip()
        col = TRAIT_COL.get(cat)
        value = str(row.get("trait_value") or "").strip()
        if col and value:
            out.at[idx, col] = value
    return out


def _project_breeds(root: Path) -> pd.DataFrame:
    raw = _read_csv(root / "biology" / "breeds.csv")
    if raw.empty:
        return raw
    name = _col(raw, "breed_name", "breed", "name")
    out = pd.DataFrame(
        {
            "breed": name,
            "breed_id": _col(raw, "breed_id"),
            "breed_group": _col(raw, "breed_group"),
            "species": _col(raw, "species"),
            "status": _col(raw, "status"),
        }
    )
    traits = _read_csv(root / "biology" / "breed_traits.csv")
    out = _apply_breed_traits(out, traits)
    return _annotate(out, "biology/breeds.csv")


def _project_breed_conditions(root: Path) -> pd.DataFrame:
    raw = _read_csv(root / "biology" / "observed_breed_conditions.csv")
    if raw.empty:
        return raw
    out = pd.DataFrame(
        {
            "breed": _col(raw, "breed_name", "breed"),
            "condition": _col(raw, "condition_name", "condition"),
            "prevalence": _col(raw, "value_number", "prevalence"),
            "sample_population": _col(raw, "population_description", "sample_population"),
            "sample_size": _col(raw, "denominator_count", "sample_size"),
            "source_name": _col(raw, "paper_name", "source_name"),
            "source_quote": _col(raw, "scientific_quote", "source_quote"),
            "source_url": _col(raw, "paper_link", "source_url"),
            "year": _col(raw, "publication_year", "year"),
            "study_type": _col(raw, "study_type"),
            "species": _col(raw, "species"),
            "status": _col(raw, "status"),
            "fact_id": _col(raw, "fact_id"),
            "breed_id": _col(raw, "breed_id"),
            "condition_id": _col(raw, "condition_id"),
            "unit": _col(raw, "unit"),
            "measure_type": _col(raw, "measure_type"),
            "confidence": _col(raw, "confidence_level", "confidence"),
        }
    )
    return _annotate(out, "biology/observed_breed_conditions.csv")


def _project_trait_tables(root: Path) -> dict[str, pd.DataFrame]:
    raw = _read_csv(root / "biology" / "trait_condition_associations.csv")
    buckets: dict[str, list[dict[str, str]]] = {table: [] for _c, table, _col in TRAIT_TABLES}
    if not raw.empty:
        for _, row in raw.iterrows():
            cat = str(row.get("trait_name") or "").strip()
            table = TRAIT_TABLE.get(cat)
            if not table:
                continue
            col = TRAIT_COL[cat]
            buckets[table].append(
                {
                    col: str(row.get("trait_value") or ""),
                    "condition": str(row.get("condition_name") or ""),
                    "prevalence": str(row.get("effect_value") or ""),
                    "sample_population": str(row.get("population_description") or ""),
                    "source_name": str(row.get("paper_name") or ""),
                    "source_quote": str(row.get("scientific_quote") or ""),
                    "source_url": str(row.get("paper_link") or ""),
                    "year": str(row.get("publication_year") or ""),
                    "study_type": str(row.get("study_type") or ""),
                    "species": str(row.get("species") or ""),
                    "status": str(row.get("status") or ""),
                    "fact_id": str(row.get("fact_id") or ""),
                    "condition_id": str(row.get("condition_id") or ""),
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
    return {
        table: _annotate(pd.DataFrame(rows), file_map[table])
        for table, rows in buckets.items()
    }


def _project_condition_ingredients(root: Path) -> pd.DataFrame:
    raw = _read_csv(root / "prevention" / "condition_ingredients.csv")
    if raw.empty:
        return raw
    out = pd.DataFrame(
        {
            "condition": _col(raw, "condition_name", "condition"),
            "ingredient_name": _col(raw, "ingredient_name"),
            "ingredient_id": _col(raw, "ingredient_id"),
            "recommended_daily_dose": _col(raw, "exposure_amount", "recommended_daily_dose"),
            "dose_unit": _col(raw, "exposure_unit", "dose_unit"),
            "source_name": _col(raw, "paper_name", "source_name"),
            "source_quote": _col(raw, "scientific_quote", "source_quote"),
            "source_url": _col(raw, "paper_link", "source_url"),
            "year": _col(raw, "publication_year", "year"),
            "study_type": _col(raw, "study_type"),
            "species": _col(raw, "species"),
            "status": _col(raw, "status"),
            "fact_id": _col(raw, "fact_id"),
            "condition_id": _col(raw, "condition_id"),
            "priority_rank": "",
            "evidence_type": _col(raw, "observed_effect_name"),
        }
    )
    return _annotate(out, "prevention/condition_ingredients.csv")


def _project_condition_activities(root: Path) -> pd.DataFrame:
    raw = _read_csv(root / "prevention" / "condition_activities.csv")
    if raw.empty:
        return raw
    out = pd.DataFrame(
        {
            "condition": _col(raw, "condition_name", "condition"),
            "activity_name": _col(raw, "activity_name"),
            "source_name": _col(raw, "paper_name", "source_name"),
            "source_quote": _col(raw, "scientific_quote", "source_quote"),
            "source_url": _col(raw, "paper_link", "source_url"),
            "year": _col(raw, "publication_year", "year"),
            "fact_id": _col(raw, "fact_id"),
            "condition_id": _col(raw, "condition_id"),
            "status": _col(raw, "status"),
            "species": _col(raw, "species"),
        }
    )
    return _annotate(out, "prevention/condition_activities.csv")


def _project_aliases(breeds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    if not breeds.empty:
        for _, row in breeds.iterrows():
            name = str(row.get("breed") or "").strip()
            if not name:
                continue
            key = (name.lower(), name)
            if key not in seen:
                seen.add(key)
                rows.append({"alias": name, "canonical_breed": name})
    for alias, canon in _BREED_ALIASES:
        key = (alias.lower(), canon)
        if key not in seen:
            seen.add(key)
            rows.append({"alias": alias, "canonical_breed": canon})
    return _annotate(pd.DataFrame(rows), "biology/breed_aliases")


def _csv_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for folder in ("biology", "prevention"):
        base = root / folder
        if not base.exists():
            continue
        paths.extend(sorted(base.glob("*.csv")))
    return paths


def build_biology_views(root: Path) -> dict[str, pd.DataFrame]:
    root = Path(root)
    tables: dict[str, pd.DataFrame] = {}
    breeds = _project_breeds(root)
    tables["breeds"] = breeds
    tables["breed_conditions"] = _project_breed_conditions(root)
    tables.update(_project_trait_tables(root))
    ingredients = _project_condition_ingredients(root)
    tables["condition_ingredients_sci"] = ingredients.copy()
    tables["condition_ingredients_prev"] = ingredients.copy()
    tables["condition_activities"] = _project_condition_activities(root)
    tables["breed_aliases"] = _project_aliases(breeds)
    conditions = _read_csv(root / "biology" / "conditions.csv")
    if not conditions.empty:
        tables["warehouse_conditions"] = _annotate(conditions, "biology/conditions.csv")
    tables["package_tiers"] = _annotate(PACKAGE_TIERS.copy(), "PACKAGE_TIERS.csv")
    tables["product_defaults"] = _annotate(PRODUCT_DEFAULTS.copy(), "PRODUCT_DEFAULTS.csv")
    mixed = _read_csv(root / "biology" / "mixed_breed_NEEDS_VALIDATION.csv")
    if not mixed.empty:
        tables["mixed_breed_interactions"] = _annotate(mixed, "biology/mixed_breed_NEEDS_VALIDATION.csv")
    logger.info(
        "Biology warehouse views: breeds=%s breed_conditions=%s ingredients=%s",
        0 if breeds.empty else len(breeds),
        0 if tables["breed_conditions"].empty else len(tables["breed_conditions"]),
        0 if ingredients.empty else len(ingredients),
    )
    return tables


def _manifest_for(tables: dict[str, pd.DataFrame], version: str) -> Manifest:
    files: list[FileSpec] = []
    for name, df in sorted(tables.items()):
        files.append(
            FileSpec(
                path=f"memory://{name}",
                table=name,
                primary_key=(),
                # Incomplete intern rows (empty condition mapping, missing provenance)
                # must still load. Do not treat the first column as required-nonblank.
                required_columns=(),
                allow_empty=True,
            )
        )
    return Manifest(version=version, modules=("biology", "prevention"), files=tuple(files))


def load_biology_warehouse(root: Path) -> tuple[Manifest, dict[str, pd.DataFrame], list[Path]]:
    root = Path(root)
    tables = build_biology_views(root)
    return _manifest_for(tables, "5.0.0-biology"), tables, _csv_paths(root)


def merge_biology_into(
    root: Path,
    manifest: Manifest,
    tables: dict[str, pd.DataFrame],
    paths: list[Path],
) -> tuple[Manifest, dict[str, pd.DataFrame], list[Path]]:
    """Fill empty native/science tables from biology CSVs. Do not overwrite populated science rows."""
    bio = build_biology_views(root)
    merged = dict(tables)
    for name, df in bio.items():
        existing = merged.get(name)
        if existing is None or existing.empty:
            merged[name] = df
    extra_paths = [p for p in _csv_paths(root) if p not in paths]
    return _manifest_for(merged, manifest.version or "5.0.0-biology"), merged, [*paths, *extra_paths]
