"""Forensic intern-data recovery. Does not delete or overwrite populated rows.

Read-only originals land in warehouse/recovery_original/. Canonical tables are
appended only when empty or when intern rows are absent from the destination.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "warehouse" / "recovery_original"
INTERN_COMMIT = "a122a83"
SNAPSHOT_COMMIT = "d6384a0"
CANONICAL_SNAPSHOT = RECOVERY / "canonical_before_recovery"
INTERN_DIR = RECOVERY / f"intern_{INTERN_COMMIT}"
SNAPSHOT_DIR = RECOVERY / f"snapshot_{SNAPSHOT_COMMIT}"
MAPPING_PATH = RECOVERY / "RECOVERY_MAPPING.csv"
INVENTORY_PATH = ROOT / "docs" / "DATA_RECOVERY_INVENTORY.md"
REPORT_PATH = ROOT / "docs" / "DATA_RECOVERY_REPORT.md"

INTERN_PATHS = [
    "data/breed_analysis",
    "data/preventative_ingredients",
    "data/product_portfolio",
    "archive/data/legacy-parity-csv",
]
SNAPSHOT_PATHS = ["operations/snapshots/2026.07.20-omega/warehouse"]

QUOTE_COLS = (
    "scientific_quote",
    "source_quote",
    "quote",
    "excerpt",
)
PAPER_NAME_COLS = (
    "paper_name",
    "source_name",
    "title",
    "journal",
    "citation",
)
PAPER_LINK_COLS = (
    "paper_link",
    "source_url",
    "url",
    "doi",
    "pmid",
)
BREED_COLS = ("breed", "breed_name", "primary_breed")
CONDITION_COLS = ("condition", "condition_name")
PREVALENCE_COLS = ("prevalence", "value_number", "effect_value", "observed_prevalence")
NUTRIENT_COLS = ("nutrient", "nutrient_name", "ingredient", "ingredient_name")

TRAIT_COLUMNS = (
    "size",
    "body_type",
    "coat_type",
    "energy",
    "weakness_group",
    "skull_type",
    "climate",
    "lifespan",
    "function_group",
)

SKIP_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}


def _git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def _extract_commit(commit: str, paths: list[str], dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    zip_path = RECOVERY / f"{commit}.zip"
    cmd = ["archive", "--format=zip", "-o", str(zip_path), commit, "--", *paths]
    _git(cmd)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    return zip_path


def _copy_canonical_snapshot() -> None:
    if CANONICAL_SNAPSHOT.exists():
        return
    CANONICAL_SNAPSHOT.mkdir(parents=True, exist_ok=True)
    for folder in ("biology", "prevention", "commercial", "nutrition", "reference"):
        src = ROOT / "warehouse" / folder
        if src.exists():
            shutil.copytree(src, CANONICAL_SNAPSHOT / folder, dirs_exist_ok=True)
    for name in ("MIGRATION_REPORT.csv", "MIGRATION_SUMMARY.csv", "CANONICAL_MANIFEST.json", "DOMAIN_REGISTRY.json"):
        src = ROOT / "warehouse" / name
        if src.exists():
            shutil.copy2(src, CANONICAL_SNAPSHOT / name)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin-1")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _nonempty_mask(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=bool)
    return df.apply(lambda row: any(str(v).strip() for v in row.values), axis=1)


def _col_hit(df: pd.DataFrame, names: tuple[str, ...]) -> int:
    if df.empty:
        return 0
    cols = [c for c in df.columns if c.lower() in {n.lower() for n in names} or any(n.lower() in c.lower() for n in names)]
    if not cols:
        return 0
    n = 0
    for _, row in df.iterrows():
        if any(str(row.get(c) or "").strip() for c in cols):
            n += 1
    return n


def _classify(path: Path, df: pd.DataFrame, quotes: int, papers: int, links: int, breed: int, cond: int, prev: int, nut: int) -> str:
    rel = str(path).replace("\\", "/")
    rows = 0 if df.empty else int(_nonempty_mask(df).sum())
    if rows == 0:
        return "EMPTY TEMPLATE"
    if "recovery_original" in rel and "canonical_before_recovery" not in rel:
        if "product" in rel.lower() or "commercial" in rel.lower() or "PRODUCT" in path.name:
            return "POPULATED COMMERCIAL DATA" if nut or "product" in rel.lower() else "POPULATED LEGACY DATA"
        if quotes or papers or links or prev:
            return "POPULATED SCIENTIFIC DATA"
        return "POPULATED LEGACY DATA"
    if "legacy" in rel:
        if quotes or papers or prev:
            return "POPULATED LEGACY DATA"
        return "POPULATED LEGACY DATA" if rows else "EMPTY TEMPLATE"
    if any(x in rel for x in ("formulas/", "optimization/", "objectives/", "mechanisms/")):
        return "DERIVED DATA"
    if path.name.endswith("_NEEDS_VALIDATION.csv"):
        return "POPULATED LEGACY DATA" if rows else "EMPTY TEMPLATE"
    if "commercial" in rel:
        return "POPULATED COMMERCIAL DATA" if rows else "EMPTY TEMPLATE"
    if quotes or papers or links or prev:
        return "POPULATED SCIENTIFIC DATA"
    if breed or cond or nut:
        return "POPULATED SCIENTIFIC DATA" if "biology" in rel or "prevention" in rel or "nutrition" in rel else "POPULATED LEGACY DATA"
    return "UNKNOWN"


def _likely_origin(path: Path) -> str:
    rel = str(path).replace("\\", "/")
    if f"intern_{INTERN_COMMIT}" in rel:
        return f"git {INTERN_COMMIT} intern tree (deleted from working tree by 76984c5)"
    if f"snapshot_{SNAPSHOT_COMMIT}" in rel:
        return f"git {SNAPSHOT_COMMIT} operations snapshot (deleted from working tree by 76984c5)"
    if "canonical_before_recovery" in rel:
        return "canonical warehouse snapshot taken before this recovery run"
    if "legacy/warehouse" in rel:
        return "legacy authoring staging (on disk)"
    if "warehouse/" in rel:
        return "current canonical warehouse"
    if "legacy/" in rel:
        return "legacy UI / ontology / drafts (on disk)"
    return "working tree"


def _iter_candidate_files() -> list[Path]:
    files: list[Path] = []
    roots = [
        ROOT / "warehouse",
        ROOT / "legacy",
        ROOT / "data",
        ROOT / "archive",
        ROOT / "operations",
        ROOT / "docs",
        ROOT / "repository",
    ]
    suffixes = {".csv", ".json", ".md", ".txt", ".xlsx", ".xls", ".pdf", ".docx", ".sql"}
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix.lower() not in suffixes:
                continue
            files.append(path)
    return sorted(set(files))


def _scan_text_file(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    keys = (
        "scientific_quote",
        "source_quote",
        "paper_name",
        "paper_link",
        "prevalence",
        "PubMed",
        "DOI",
        "Labrador",
        "Golden Retriever",
    )
    hits = {k: text.lower().count(k.lower()) for k in keys}
    return {"chars": len(text), "hits": hits, "any": any(hits.values())}


def inventory_rows() -> list[dict]:
    rows: list[dict] = []
    for path in _iter_candidate_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() == ".csv":
            df = _read_csv(path)
            nonempty = 0 if df.empty else int(_nonempty_mask(df).sum())
            rec = {
                "file": rel,
                "rows": 0 if df.empty else len(df),
                "columns": "" if df.empty else ", ".join(df.columns.tolist()),
                "column_count": 0 if df.empty else len(df.columns),
                "nonempty_rows": nonempty,
                "scientific_quotes": _col_hit(df, QUOTE_COLS),
                "paper_names": _col_hit(df, PAPER_NAME_COLS),
                "paper_links": _col_hit(df, PAPER_LINK_COLS),
                "breed_data": _col_hit(df, BREED_COLS),
                "condition_data": _col_hit(df, CONDITION_COLS),
                "prevalence_data": _col_hit(df, PREVALENCE_COLS),
                "nutrient_data": _col_hit(df, NUTRIENT_COLS),
            }
            rec["nonempty_evidence_rows"] = max(rec["scientific_quotes"], rec["paper_names"], rec["paper_links"])
            rec["status"] = _classify(
                path,
                df,
                rec["scientific_quotes"],
                rec["paper_names"],
                rec["paper_links"],
                rec["breed_data"],
                rec["condition_data"],
                rec["prevalence_data"],
                rec["nutrient_data"],
            )
            rec["likely_origin"] = _likely_origin(path)
            rows.append(rec)
        else:
            meta = _scan_text_file(path)
            if not meta.get("any") and path.suffix.lower() not in {".xlsx", ".pdf", ".docx", ".sql"}:
                continue
            rows.append(
                {
                    "file": rel,
                    "rows": "",
                    "columns": f"non-csv; keyword_hits={meta.get('hits')}",
                    "column_count": "",
                    "nonempty_rows": meta.get("chars", ""),
                    "nonempty_evidence_rows": "",
                    "scientific_quotes": (meta.get("hits") or {}).get("scientific_quote", 0),
                    "paper_names": (meta.get("hits") or {}).get("paper_name", 0),
                    "paper_links": (meta.get("hits") or {}).get("paper_link", 0),
                    "breed_data": (meta.get("hits") or {}).get("Labrador", 0),
                    "condition_data": "",
                    "prevalence_data": (meta.get("hits") or {}).get("prevalence", 0),
                    "nutrient_data": "",
                    "status": "UNKNOWN" if path.suffix.lower() != ".json" else "POPULATED LEGACY DATA",
                    "likely_origin": _likely_origin(path),
                }
            )
    return rows


def _fact_id(*parts: str) -> str:
    raw = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:6].upper()
    return f"FACT_{digest}"


def _breed_id(name: str) -> str:
    digest = hashlib.sha1(name.strip().lower().encode("utf-8")).hexdigest()[:8].upper()
    return f"BREED_{digest}"


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def _mapping_rows() -> list[dict]:
    if not MAPPING_PATH.exists():
        return []
    return list(csv.DictReader(MAPPING_PATH.open(encoding="utf-8")))


def _save_mapping(rows: list[dict]) -> None:
    if not rows:
        return
    fields = [
        "source_legacy_file",
        "source_legacy_row",
        "canonical_file",
        "canonical_fact_id",
        "recovery_status",
        "note",
    ]
    with MAPPING_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def recover_breeds_and_traits(mapping: list[dict]) -> dict:
    intern_breeds = _read_csv(INTERN_DIR / "data/breed_analysis/1_biological_traits/BREEDS.csv")
    dest_breeds = ROOT / "warehouse/biology/breeds.csv"
    dest_traits = ROOT / "warehouse/biology/breed_traits.csv"
    breeds = _read_csv(dest_breeds)
    traits = _read_csv(dest_traits)
    existing_names = {str(x).strip().lower() for x in breeds.get("breed_name", pd.Series(dtype=str))}
    name_to_id = {
        str(r.get("breed_name") or "").strip().lower(): str(r.get("breed_id") or "")
        for _, r in breeds.iterrows()
    }
    added_breeds = 0
    added_traits = 0
    trait_header = [
        "fact_id",
        "breed_id",
        "breed_name",
        "trait_name",
        "trait_value",
        "value_number",
        "unit",
        "population_description",
        "scientific_quote",
        "paper_name",
        "paper_link",
        "publication_year",
        "study_type",
        "species",
        "status",
    ]
    if traits.empty:
        traits = pd.DataFrame(columns=trait_header)
    existing_trait_keys = {
        (
            str(r.get("breed_id") or ""),
            str(r.get("trait_name") or ""),
            str(r.get("trait_value") or ""),
        )
        for _, r in traits.iterrows()
    }
    new_breed_rows = []
    new_trait_rows = []
    intern_path = "data/breed_analysis/1_biological_traits/BREEDS.csv"
    for i, row in intern_breeds.iterrows():
        name = str(row.get("breed") or "").strip()
        if not name:
            continue
        key = name.lower()
        bid = name_to_id.get(key)
        if not bid:
            bid = _breed_id(name)
            used = set(name_to_id.values())
            n = 1
            while bid in used:
                n += 1
                bid = _breed_id(f"{name}:{n}")
            name_to_id[key] = bid
            new_breed_rows.append(
                {
                    "breed_id": bid,
                    "breed_name": name,
                    "breed_group": str(row.get("function_group") or ""),
                    "external_standard": "",
                    "external_id": "",
                    "scientific_quote": "",
                    "paper_name": "",
                    "paper_link": "",
                    "publication_year": "",
                    "study_type": "",
                    "species": "Canis lupus familiaris",
                    "status": "MISSING_PROVENANCE",
                }
            )
            added_breeds += 1
            mapping.append(
                {
                    "source_legacy_file": intern_path,
                    "source_legacy_row": str(i + 2),
                    "canonical_file": "warehouse/biology/breeds.csv",
                    "canonical_fact_id": bid,
                    "recovery_status": "MISSING_PROVENANCE",
                    "note": "identity only; intern phenotype moved to breed_traits.csv",
                }
            )
        for trait_name in TRAIT_COLUMNS:
            value = str(row.get(trait_name) or "").strip()
            if not value:
                continue
            tkey = (bid, trait_name, value)
            if tkey in existing_trait_keys:
                continue
            existing_trait_keys.add(tkey)
            fid = _fact_id(bid, trait_name, value)
            new_trait_rows.append(
                {
                    "fact_id": fid,
                    "breed_id": bid,
                    "breed_name": name,
                    "trait_name": trait_name,
                    "trait_value": value,
                    "value_number": "",
                    "unit": "",
                    "population_description": "Intern BREEDS.csv phenotype column; no study citation in source row",
                    "scientific_quote": "",
                    "paper_name": "",
                    "paper_link": "",
                    "publication_year": "",
                    "study_type": "",
                    "species": "Canis lupus familiaris",
                    "status": "MISSING_PROVENANCE",
                }
            )
            added_traits += 1
            mapping.append(
                {
                    "source_legacy_file": intern_path,
                    "source_legacy_row": str(i + 2),
                    "canonical_file": "warehouse/biology/breed_traits.csv",
                    "canonical_fact_id": fid,
                    "recovery_status": "MISSING_PROVENANCE",
                    "note": f"trait {trait_name}={value}",
                }
            )
    if new_breed_rows:
        breeds = pd.concat([breeds, pd.DataFrame(new_breed_rows)], ignore_index=True)
        _write_csv(dest_breeds, breeds)
    if new_trait_rows:
        traits = pd.concat([traits, pd.DataFrame(new_trait_rows)], ignore_index=True)
        _write_csv(dest_traits, traits)
    return {"added_breeds": added_breeds, "added_traits": added_traits, "intern_breed_rows": len(intern_breeds)}


def _evidence_tuple(row: pd.Series, breed_col: str, cond_col: str) -> tuple:
    return (
        str(row.get(breed_col) or "").strip().lower(),
        str(row.get(cond_col) or "").strip().lower(),
        str(row.get("paper_link") or row.get("source_url") or "").strip().lower(),
        str(row.get("value_number") or row.get("prevalence") or "").strip(),
        str(row.get("scientific_quote") or row.get("source_quote") or "").strip()[:80],
    )


def recover_observed_conditions(mapping: list[dict]) -> dict:
    intern = _read_csv(INTERN_DIR / "data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv")
    dest = ROOT / "warehouse/biology/observed_breed_conditions.csv"
    current = _read_csv(dest)
    existing = {_evidence_tuple(r, "breed_name", "condition_name") for _, r in current.iterrows()}
    breed_ids = {
        str(r.get("breed_name") or "").strip().lower(): str(r.get("breed_id") or "")
        for _, r in _read_csv(ROOT / "warehouse/biology/breeds.csv").iterrows()
    }
    cond_ids = {
        str(r.get("condition_name") or "").strip().lower(): str(r.get("condition_id") or "")
        for _, r in _read_csv(ROOT / "warehouse/biology/conditions.csv").iterrows()
    }
    added = 0
    skipped = 0
    new_rows = []
    intern_path = "data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv"
    for i, row in intern.iterrows():
        key = _evidence_tuple(row, "breed", "condition")
        if key in existing:
            skipped += 1
            continue
        breed = str(row.get("breed") or "").strip()
        condition = str(row.get("condition") or "").strip()
        same_pair = any(
            str(r.get("breed_name") or "").strip().lower() == breed.lower()
            and str(r.get("condition_name") or "").strip().lower() == condition.lower()
            for _, r in current.iterrows()
        )
        status = "CONFLICT_REQUIRES_VALIDATION" if same_pair else "NEEDS_VALIDATION"
        if not str(row.get("source_name") or row.get("source_url") or row.get("source_quote") or "").strip():
            status = "MISSING_PROVENANCE" if status != "CONFLICT_REQUIRES_VALIDATION" else status
        fid = _fact_id("obs", breed, condition, str(row.get("source_url") or ""), str(i))
        new_rows.append(
            {
                "fact_id": fid,
                "breed_id": breed_ids.get(breed.lower(), ""),
                "breed_name": breed,
                "condition_id": cond_ids.get(condition.lower(), ""),
                "condition_name": condition,
                "measure_type": "prevalence",
                "value_number": str(row.get("prevalence") or ""),
                "unit": "ratio",
                "numerator_count": "",
                "denominator_count": str(row.get("sample_size") or ""),
                "population_description": str(row.get("sample_population") or ""),
                "observation_period": "",
                "scientific_quote": str(row.get("source_quote") or ""),
                "paper_name": str(row.get("source_name") or ""),
                "paper_link": str(row.get("source_url") or ""),
                "publication_year": str(row.get("year") or ""),
                "study_type": "",
                "species": "Canis lupus familiaris",
                "status": status,
            }
        )
        existing.add(key)
        added += 1
        mapping.append(
            {
                "source_legacy_file": intern_path,
                "source_legacy_row": str(i + 2),
                "canonical_file": "warehouse/biology/observed_breed_conditions.csv",
                "canonical_fact_id": fid,
                "recovery_status": status,
                "note": "intern BREED_CONDITIONS row not present in canonical observed table",
            }
        )
    if new_rows:
        current = pd.concat([current, pd.DataFrame(new_rows)], ignore_index=True)
        _write_csv(dest, current)
    return {"intern_rows": len(intern), "already_present": skipped, "appended": added}


def recover_trait_associations(mapping: list[dict]) -> dict:
    intern_files = {
        "size": INTERN_DIR / "data/breed_analysis/3_management_considerations/SIZE_CONDITIONS.csv",
        "body_type": INTERN_DIR / "data/breed_analysis/3_management_considerations/BODYTYPE_CONDITIONS.csv",
        "coat_type": INTERN_DIR / "data/breed_analysis/3_management_considerations/COATTYPE_CONDITIONS.csv",
        "energy": INTERN_DIR / "data/breed_analysis/3_management_considerations/ENERGY_CONDITIONS.csv",
        "skull_type": INTERN_DIR / "data/breed_analysis/3_management_considerations/SKULLTYPE_CONDITIONS.csv",
        "climate": INTERN_DIR / "data/breed_analysis/3_management_considerations/CLIMATE_CONDITIONS.csv",
        "lifespan": INTERN_DIR / "data/breed_analysis/3_management_considerations/LIFESPAN_CONDITIONS.csv",
        "weakness_group": INTERN_DIR / "data/breed_analysis/3_management_considerations/WEAKNESSGROUP_CONDITIONS.csv",
        "function_group": INTERN_DIR / "data/breed_analysis/3_management_considerations/FUNCTIONGROUP_CONDITIONS.csv",
    }
    dest = ROOT / "warehouse/biology/trait_condition_associations.csv"
    current = _read_csv(dest)
    existing = {
        (
            str(r.get("trait_name") or "").strip().lower(),
            str(r.get("trait_value") or "").strip().lower(),
            str(r.get("condition_name") or "").strip().lower(),
            str(r.get("paper_link") or "").strip().lower(),
            str(r.get("effect_value") or "").strip(),
        )
        for _, r in current.iterrows()
    }
    cond_ids = {
        str(r.get("condition_name") or "").strip().lower(): str(r.get("condition_id") or "")
        for _, r in _read_csv(ROOT / "warehouse/biology/conditions.csv").iterrows()
    }
    trait_value_col = {
        "size": "size",
        "body_type": "body_type",
        "coat_type": "coat_type",
        "energy": "energy",
        "skull_type": "skull_type",
        "climate": "climate",
        "lifespan": "lifespan",
        "weakness_group": "weakness_group",
        "function_group": "function_group",
    }
    added = 0
    skipped = 0
    intern_total = 0
    new_rows = []
    for trait_name, path in intern_files.items():
        df = _read_csv(path)
        intern_total += len(df)
        value_col = trait_value_col[trait_name]
        if df.empty:
            continue
        if value_col not in df.columns:
            candidates = [c for c in df.columns if c.lower() not in {"condition", "prevalence", "source_name", "source_quote", "source_url", "year"}]
            value_col = candidates[0] if candidates else df.columns[0]
        rel = path.relative_to(INTERN_DIR).as_posix()
        for i, row in df.iterrows():
            value = str(row.get(value_col) or "").strip()
            condition = str(row.get("condition") or "").strip()
            if not value or not condition:
                continue
            key = (
                trait_name.lower(),
                value.lower(),
                condition.lower(),
                str(row.get("source_url") or "").strip().lower(),
                str(row.get("prevalence") or "").strip(),
            )
            if key in existing:
                skipped += 1
                continue
            same_pair = any(
                str(r.get("trait_name") or "").strip().lower() == trait_name.lower()
                and str(r.get("trait_value") or "").strip().lower() == value.lower()
                and str(r.get("condition_name") or "").strip().lower() == condition.lower()
                for _, r in current.iterrows()
            )
            status = "CONFLICT_REQUIRES_VALIDATION" if same_pair else "NEEDS_VALIDATION"
            quote = str(row.get("source_quote") or "")
            paper = str(row.get("source_name") or "")
            link = str(row.get("source_url") or "")
            if not (quote or paper or link) and status != "CONFLICT_REQUIRES_VALIDATION":
                status = "MISSING_PROVENANCE"
            fid = _fact_id("trait", trait_name, value, condition, str(i))
            new_rows.append(
                {
                    "fact_id": fid,
                    "trait_name": trait_name,
                    "trait_value": value,
                    "modifier_trait_name": "",
                    "modifier_trait_value": "",
                    "condition_id": cond_ids.get(condition.lower(), ""),
                    "condition_name": condition,
                    "association_type": "associated_with",
                    "effect_direction": "positive",
                    "effect_measure_type": "prevalence",
                    "effect_value": str(row.get("prevalence") or ""),
                    "effect_unit": "ratio",
                    "population_description": str(row.get("sample_population") or ""),
                    "scientific_quote": quote,
                    "paper_name": paper,
                    "paper_link": link,
                    "publication_year": str(row.get("year") or ""),
                    "study_type": "",
                    "species": "Canis lupus familiaris",
                    "status": status,
                }
            )
            existing.add(key)
            added += 1
            mapping.append(
                {
                    "source_legacy_file": rel,
                    "source_legacy_row": str(i + 2),
                    "canonical_file": "warehouse/biology/trait_condition_associations.csv",
                    "canonical_fact_id": fid,
                    "recovery_status": status,
                    "note": f"{trait_name}={value} → {condition}",
                }
            )
    if new_rows:
        current = pd.concat([current, pd.DataFrame(new_rows)], ignore_index=True)
        _write_csv(dest, current)
    return {"intern_rows": intern_total, "already_present": skipped, "appended": added}


def recover_ingredients(mapping: list[dict]) -> dict:
    intern = _read_csv(INTERN_DIR / "data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv")
    dest = ROOT / "warehouse/prevention/condition_ingredients.csv"
    current = _read_csv(dest)
    existing = {
        (
            str(r.get("condition_name") or "").strip().lower(),
            str(r.get("ingredient_name") or "").strip().lower(),
            str(r.get("paper_link") or "").strip().lower(),
        )
        for _, r in current.iterrows()
    }
    cond_ids = {
        str(r.get("condition_name") or "").strip().lower(): str(r.get("condition_id") or "")
        for _, r in _read_csv(ROOT / "warehouse/biology/conditions.csv").iterrows()
    }
    added = 0
    skipped = 0
    new_rows = []
    intern_path = "data/breed_analysis/5_scientific_nutrition/CONDITION_INGREDIENTS.csv"
    name_col = "ingredient_name" if "ingredient_name" in intern.columns else ("ingredient" if "ingredient" in intern.columns else intern.columns[0])
    for i, row in intern.iterrows():
        condition = str(row.get("condition") or row.get("condition_name") or "").strip()
        ingredient = str(row.get(name_col) or "").strip()
        if not condition or not ingredient:
            continue
        key = (condition.lower(), ingredient.lower(), str(row.get("source_url") or "").strip().lower())
        if key in existing:
            skipped += 1
            continue
        status = "NEEDS_VALIDATION"
        quote = str(row.get("source_quote") or row.get("scientific_quote") or "")
        paper = str(row.get("source_name") or row.get("paper_name") or "")
        link = str(row.get("source_url") or row.get("paper_link") or "")
        if not (quote or paper or link):
            status = "MISSING_PROVENANCE"
        fid = _fact_id("ing", condition, ingredient, str(i))
        new_rows.append(
            {
                "fact_id": fid,
                "condition_id": cond_ids.get(condition.lower(), ""),
                "condition_name": condition,
                "ingredient_id": "",
                "ingredient_name": ingredient,
                "exposure_amount": str(row.get("recommended_daily_dose") or row.get("dose") or ""),
                "exposure_unit": str(row.get("dose_unit") or row.get("unit") or ""),
                "exposure_basis": "daily",
                "observed_effect_name": "condition support",
                "effect_direction": "positive",
                "effect_measure_type": "",
                "effect_value": "",
                "effect_unit": "",
                "population_description": "",
                "safety_note": "",
                "scientific_quote": quote,
                "paper_name": paper,
                "paper_link": link,
                "publication_year": str(row.get("year") or row.get("publication_year") or ""),
                "study_type": "",
                "species": "Canis lupus familiaris",
                "status": status,
            }
        )
        existing.add(key)
        added += 1
        mapping.append(
            {
                "source_legacy_file": intern_path,
                "source_legacy_row": str(i + 2),
                "canonical_file": "warehouse/prevention/condition_ingredients.csv",
                "canonical_fact_id": fid,
                "recovery_status": status,
                "note": f"{ingredient} → {condition}",
            }
        )
    if new_rows:
        current = pd.concat([current, pd.DataFrame(new_rows)], ignore_index=True)
        _write_csv(dest, current)
    return {"intern_rows": len(intern), "already_present": skipped, "appended": added}


def recover_papers(mapping: list[dict]) -> dict:
    intern = _read_csv(
        SNAPSHOT_DIR / "operations/snapshots/2026.07.20-omega/warehouse/reference/papers.csv"
    )
    dest = ROOT / "warehouse/reference/papers.csv"
    if dest.exists() and not _read_csv(dest).empty:
        return {"intern_rows": len(intern), "already_present": len(_read_csv(dest)), "appended": 0, "created": False}
    if intern.empty:
        return {"intern_rows": 0, "already_present": 0, "appended": 0, "created": False}
    out_cols = [
        "paper_id",
        "paper_name",
        "authors",
        "journal",
        "publication_year",
        "doi",
        "pmid",
        "paper_link",
        "sample_size",
        "study_type",
        "country",
        "species",
        "scientific_quote",
        "status",
        "source_legacy_file",
        "source_legacy_row",
    ]
    rows = []
    rel = "operations/snapshots/2026.07.20-omega/warehouse/reference/papers.csv"
    for i, row in intern.iterrows():
        status = "NEEDS_VALIDATION"
        quote = str(row.get("quote") or "")
        title = str(row.get("title") or "")
        url = str(row.get("url") or "")
        if not (quote or title or url):
            status = "MISSING_PROVENANCE"
        pid = str(row.get("paper_id") or _fact_id("paper", title, str(i)))
        rows.append(
            {
                "paper_id": pid,
                "paper_name": title,
                "authors": str(row.get("authors") or ""),
                "journal": str(row.get("journal") or ""),
                "publication_year": str(row.get("year") or ""),
                "doi": str(row.get("doi") or ""),
                "pmid": str(row.get("pmid") or ""),
                "paper_link": url,
                "sample_size": str(row.get("sample_size") or ""),
                "study_type": str(row.get("study_type") or ""),
                "country": str(row.get("country") or ""),
                "species": str(row.get("species") or ""),
                "scientific_quote": quote,
                "status": status,
                "source_legacy_file": rel,
                "source_legacy_row": str(i + 2),
            }
        )
        mapping.append(
            {
                "source_legacy_file": rel,
                "source_legacy_row": str(i + 2),
                "canonical_file": "warehouse/reference/papers.csv",
                "canonical_fact_id": pid,
                "recovery_status": status,
                "note": "paper identity catalog; quotes stay on papers.csv, not conditions.csv",
            }
        )
    _write_csv(dest, pd.DataFrame(rows, columns=out_cols))
    return {"intern_rows": len(intern), "already_present": 0, "appended": len(rows), "created": True}


def recover_commercial(mapping: list[dict]) -> dict:
    catalog = _read_csv(INTERN_DIR / "data/product_portfolio/PRODUCT_CATALOG.csv")
    dest = ROOT / "warehouse/commercial/product_master.csv"
    current = _read_csv(dest)
    if not current.empty:
        return {"intern_rows": len(catalog), "already_present": len(current), "appended": 0}
    rows = []
    intern_path = "data/product_portfolio/PRODUCT_CATALOG.csv"
    for i, row in catalog.iterrows():
        pid = str(row.get("product_id") or "").strip()
        if not pid:
            continue
        rows.append(
            {
                "product_id": pid,
                "product_name": str(row.get("product_name") or ""),
                "brand": str(row.get("brand") or ""),
                "product_category": str(row.get("category") or ""),
                "recipe_version": str(row.get("subcategory") or ""),
                "product_status": str(row.get("status") or ""),
                "product_url": str(row.get("purchase_url") or row.get("image_url") or ""),
                "manufacturer_declaration_source": "",
                "manufacturer_declaration_url": "",
                "effective_date": "",
                "scientific_quote": "",
                "paper_name": "",
                "paper_link": "",
                "publication_year": "",
                "study_type": "",
                "species": "",
                "status": "NEEDS_VALIDATION",
            }
        )
        mapping.append(
            {
                "source_legacy_file": intern_path,
                "source_legacy_row": str(i + 2),
                "canonical_file": "warehouse/commercial/product_master.csv",
                "canonical_fact_id": pid,
                "recovery_status": "NEEDS_VALIDATION",
                "note": "commercial identity only; intern catalog had no scientific quotes",
            }
        )
    if rows:
        header = _read_csv(dest)
        out = pd.DataFrame(rows)
        if not header.empty:
            out = pd.concat([header, out], ignore_index=True)
        _write_csv(dest, out)

    functions = _read_csv(INTERN_DIR / "data/product_portfolio/PRODUCT_FUNCTIONS.csv")
    fn_dest = ROOT / "warehouse/commercial/product_functions_NEEDS_VALIDATION.csv"
    fn_current = _read_csv(fn_dest)
    fn_added = 0
    if fn_current.empty and not functions.empty:
        fn_rows = []
        for i, row in functions.iterrows():
            rec = {c: str(row.get(c) or "") for c in functions.columns}
            rec.setdefault("status", "NEEDS_VALIDATION")
            rec["source_legacy_file"] = "data/product_portfolio/PRODUCT_FUNCTIONS.csv"
            rec["source_legacy_row"] = str(i + 2)
            fn_rows.append(rec)
            mapping.append(
                {
                    "source_legacy_file": "data/product_portfolio/PRODUCT_FUNCTIONS.csv",
                    "source_legacy_row": str(i + 2),
                    "canonical_file": "warehouse/commercial/product_functions_NEEDS_VALIDATION.csv",
                    "canonical_fact_id": str(row.get("product_id") or ""),
                    "recovery_status": "NEEDS_VALIDATION",
                    "note": "intern product function row; marketing/inference not treated as science",
                }
            )
        _write_csv(fn_dest, pd.DataFrame(fn_rows))
        fn_added = len(fn_rows)

    feeding = _read_csv(INTERN_DIR / "data/product_portfolio/PRODUCT_FEEDING_RULES.csv")
    feed_dest = ROOT / "warehouse/commercial/product_feeding_guide.csv"
    feed_current = _read_csv(feed_dest)
    feed_added = 0
    if feed_current.empty and not feeding.empty:
        feed_rows = []
        for i, row in feeding.iterrows():
            rec = {c: str(row.get(c) or "") for c in feeding.columns}
            rec["source_legacy_file"] = "data/product_portfolio/PRODUCT_FEEDING_RULES.csv"
            rec["source_legacy_row"] = str(i + 2)
            rec.setdefault("status", "NEEDS_VALIDATION")
            feed_rows.append(rec)
            mapping.append(
                {
                    "source_legacy_file": "data/product_portfolio/PRODUCT_FEEDING_RULES.csv",
                    "source_legacy_row": str(i + 2),
                    "canonical_file": "warehouse/commercial/product_feeding_guide.csv",
                    "canonical_fact_id": str(row.get("product_id") or ""),
                    "recovery_status": "NEEDS_VALIDATION",
                    "note": "manufacturer feeding rule recovered as commercial declaration",
                }
            )
        _write_csv(feed_dest, pd.DataFrame(feed_rows))
        feed_added = len(feed_rows)

    return {
        "intern_rows": len(catalog),
        "already_present": 0 if current.empty else len(current),
        "appended": len(rows),
        "functions_appended": fn_added,
        "feeding_appended": feed_added,
    }


def recover_mixed_breed(mapping: list[dict]) -> dict:
    intern = _read_csv(INTERN_DIR / "data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv")
    dest = ROOT / "warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv"
    current = _read_csv(dest)
    existing = {
        (
            str(r.get("trait_a") or "").strip().lower(),
            str(r.get("trait_b") or "").strip().lower(),
            str(r.get("condition") or "").strip().lower(),
        )
        for _, r in current.iterrows()
    }
    added = 0
    skipped = 0
    new_rows = []
    intern_path = "data/breed_analysis/1_biological_traits/MIXED_BREED_INTERACTIONS.csv"

    def _intern_key(row: pd.Series) -> tuple[str, str, str]:
        if "trait_a" in intern.columns:
            return (
                str(row.get("trait_a") or "").strip().lower(),
                str(row.get("trait_b") or "").strip().lower(),
                str(row.get("condition") or "").strip().lower(),
            )
        cols = intern.columns.tolist()[:3]
        vals = [str(row.get(c) or "").strip().lower() for c in cols]
        while len(vals) < 3:
            vals.append("")
        return (vals[0], vals[1], vals[2])

    for i, row in intern.iterrows():
        key = _intern_key(row)
        if key in existing:
            skipped += 1
            continue
        rec = {c: str(row.get(c) or "") for c in current.columns if c in intern.columns}
        for c in intern.columns:
            rec.setdefault(c, str(row.get(c) or ""))
        rec.setdefault("status", "NEEDS_VALIDATION")
        if not str(rec.get("scientific_quote") or rec.get("paper_name") or rec.get("paper_link") or "").strip():
            rec["status"] = "MISSING_PROVENANCE"
        fid = rec.get("fact_id") or _fact_id("mixed", *key, str(i))
        rec["fact_id"] = fid
        new_rows.append(rec)
        existing.add(key)
        added += 1
        mapping.append(
            {
                "source_legacy_file": intern_path,
                "source_legacy_row": str(i + 2),
                "canonical_file": "warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv",
                "canonical_fact_id": fid,
                "recovery_status": rec["status"],
                "note": "intern mixed-breed interaction; left in NEEDS_VALIDATION table",
            }
        )
    if new_rows:
        aligned = pd.DataFrame(new_rows)
        for c in current.columns:
            if c not in aligned.columns:
                aligned[c] = ""
        aligned = aligned[list(current.columns) + [c for c in aligned.columns if c not in current.columns]]
        current = pd.concat([current, aligned[current.columns]], ignore_index=True)
        _write_csv(dest, current)
    return {"intern_rows": len(intern), "already_present": skipped, "appended": added}


def write_inventory(rows: list[dict], recovery_stats: dict) -> None:
    by_status = defaultdict(int)
    for rec in rows:
        by_status[str(rec.get("status") or "UNKNOWN")] += 1
    lines = [
        "# Data recovery inventory",
        "",
        "Forensic inventory of intern / legacy / canonical datasets. **Nothing was deleted.**",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Preservation copies (read-only; do not edit):",
        "",
        f"- `warehouse/recovery_original/intern_{INTERN_COMMIT}/` — git `{INTERN_COMMIT}` intern trees",
        f"- `warehouse/recovery_original/snapshot_{SNAPSHOT_COMMIT}/` — git `{SNAPSHOT_COMMIT}` warehouse snapshot",
        "- `warehouse/recovery_original/canonical_before_recovery/` — canonical CSVs as they existed before append-only recovery",
        "- `warehouse/recovery_original/RECOVERY_MAPPING.csv` — every recovered row with `source_legacy_file` / `source_legacy_row`",
        "",
        "## Classification counts",
        "",
        "| STATUS | FILES |",
        "|---|---:|",
    ]
    for status, n in sorted(by_status.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {status} | {n} |")
    lines += [
        "",
        "## How intern data disappeared from the working tree",
        "",
        "The intern CSVs were **not missing from git**. They were deleted from the working tree by commit `76984c5` (`full architecture reconstruction`).",
        "",
        "| Commit | What it contained |",
        "|---|---|",
        f"| `{INTERN_COMMIT}` | `data/breed_analysis/**`, `data/preventative_ingredients/**`, `data/product_portfolio/**`, `archive/data/legacy-parity-csv/**` |",
        f"| `{SNAPSHOT_COMMIT}` | `operations/snapshots/2026.07.20-omega/warehouse/**` including `reference/papers.csv` |",
        "| `76984c5` | Removed those paths from the working tree during architecture reconstruction |",
        "",
        "Canonical `warehouse/biology/observed_breed_conditions.csv` already held the intern Labrador/Golden prevalence rows. Runtime still looked at missing `warehouse/science/` (`CANONICAL_MANIFEST.json` / `is_native_warehouse`), so Health Analysis never loaded them.",
        "",
        "## Dataset inventory",
        "",
        "For every scanned CSV (and keyword-matching JSON/MD/TXT/SQL):",
        "",
        "| FILE | ROWS | COLUMNS | NONEMPTY_ROWS | NONEMPTY_EVIDENCE_ROWS | SCIENTIFIC_QUOTES | PAPER_NAMES | PAPER_LINKS | BREED_DATA | CONDITION_DATA | PREVALENCE_DATA | NUTRIENT_DATA | STATUS | LIKELY_ORIGIN |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for rec in rows:
        cols = str(rec.get("columns") or "").replace("|", "/")
        if len(cols) > 180:
            cols = cols[:177] + "..."
        lines.append(
            "| `{file}` | {rows} | {column_count} | {nonempty_rows} | {nonempty_evidence_rows} | {scientific_quotes} | {paper_names} | {paper_links} | {breed_data} | {condition_data} | {prevalence_data} | {nutrient_data} | {status} | {likely_origin} |".format(
                file=rec.get("file"),
                rows=rec.get("rows"),
                column_count=rec.get("column_count"),
                nonempty_rows=rec.get("nonempty_rows"),
                nonempty_evidence_rows=rec.get("nonempty_evidence_rows"),
                scientific_quotes=rec.get("scientific_quotes"),
                paper_names=rec.get("paper_names"),
                paper_links=rec.get("paper_links"),
                breed_data=rec.get("breed_data"),
                condition_data=rec.get("condition_data"),
                prevalence_data=rec.get("prevalence_data"),
                nutrient_data=rec.get("nutrient_data"),
                status=rec.get("status"),
                likely_origin=str(rec.get("likely_origin") or "").replace("|", "/"),
            )
        )
        lines.append(f"<!-- columns: {cols} -->")
    lines += [
        "",
        "## Recovery actions this run",
        "",
        "```json",
        json.dumps(recovery_stats, indent=2),
        "```",
        "",
        "No files were deleted. Existing populated canonical scientific rows were not overwritten.",
        "",
    ]
    INVENTORY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def intern_csv_stats() -> list[dict]:
    stats = []
    intern_root = INTERN_DIR
    if not intern_root.exists():
        return stats
    for path in sorted(intern_root.rglob("*.csv")):
        df = _read_csv(path)
        stats.append(
            {
                "file": path.relative_to(intern_root).as_posix(),
                "rows": 0 if df.empty else len(df),
                "quotes": _col_hit(df, QUOTE_COLS),
                "papers": _col_hit(df, PAPER_NAME_COLS),
                "links": _col_hit(df, PAPER_LINK_COLS),
                "prevalence": _col_hit(df, PREVALENCE_COLS),
            }
        )
    return stats


def write_report(recovery_stats: dict, inventory: list[dict], mapping: list[dict]) -> None:
    intern_stats = intern_csv_stats()
    intern_rows = sum(s["rows"] for s in intern_stats)
    intern_files = len(intern_stats)
    snap_papers = _read_csv(
        SNAPSHOT_DIR / "operations/snapshots/2026.07.20-omega/warehouse/reference/papers.csv"
    )
    canonical_sci = [
        ROOT / "warehouse/biology/observed_breed_conditions.csv",
        ROOT / "warehouse/biology/trait_condition_associations.csv",
        ROOT / "warehouse/biology/breed_traits.csv",
        ROOT / "warehouse/biology/breeds.csv",
        ROOT / "warehouse/biology/conditions.csv",
        ROOT / "warehouse/prevention/condition_ingredients.csv",
        ROOT / "warehouse/prevention/condition_activities.csv",
        ROOT / "warehouse/biology/environment_facts.csv",
        ROOT / "warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv",
        ROOT / "warehouse/reference/papers.csv",
    ]
    sci_rows = 0
    quote_rows = 0
    for path in canonical_sci:
        df = _read_csv(path)
        sci_rows += 0 if df.empty else len(df)
        quote_rows += _col_hit(df, QUOTE_COLS)
    validation = sum(1 for m in mapping if m.get("recovery_status") == "NEEDS_VALIDATION")
    missing_prov = sum(1 for m in mapping if m.get("recovery_status") == "MISSING_PROVENANCE")
    conflict = sum(1 for m in mapping if m.get("recovery_status") == "CONFLICT_REQUIRES_VALIDATION")
    recovered = len(mapping)
    populated = sum(1 for r in inventory if str(r.get("status") or "").startswith("POPULATED"))
    lines = [
        "# Data recovery report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "This is a **recovery** report, not a scientific reinterpretation. Conflicting or incomplete intern rows were preserved and flagged. Nothing was deleted.",
        "",
        "## Totals",
        "",
        f"- **TOTAL LEGACY DATASETS** (intern `{INTERN_COMMIT}` CSVs restored to `warehouse/recovery_original/`): {intern_files}",
        f"- **TOTAL LEGACY ROWS** (those intern CSVs): {intern_rows}",
        f"- **TOTAL POPULATED DATASETS** (inventory STATUS starts with POPULATED): {populated}",
        f"- **TOTAL SCIENTIFIC ROWS** (canonical biology/prevention/reference fact tables after recovery): {sci_rows}",
        f"- **TOTAL ROWS RECOVERED this run** (mapping entries): {recovered}",
        f"- **TOTAL ROWS REQUIRING VALIDATION** (`NEEDS_VALIDATION` in mapping): {validation}",
        f"- **TOTAL ROWS WITH MISSING PROVENANCE** (`MISSING_PROVENANCE` in mapping): {missing_prov}",
        f"- **TOTAL CONFLICT ROWS** (`CONFLICT_REQUIRES_VALIDATION` in mapping): {conflict}",
        f"- **TOTAL ROWS NOT MAPPABLE**: see migration matrix (runtime policy / empty source / already discarded by prior migration notes, **not deleted**)",
        f"- Snapshot papers.csv rows: {0 if snap_papers.empty else len(snap_papers)}",
        f"- Canonical rows with a scientific quote (post-recovery fact tables): {quote_rows}",
        "",
        "## 1. Where the intern data was found",
        "",
        "Intern research was **in git**, not lost.",
        "",
        f"1. **Working-tree canonical warehouse** already contained migrated intern prevalence and trait-condition facts in `warehouse/biology/` and `warehouse/prevention/`. `breeds.csv` was identity-only (9 breeds). `breed_traits.csv` was header-only. Commercial tables were header-only.",
        f"2. **Deleted intern trees** at commit `{INTERN_COMMIT}`: `data/breed_analysis/**` (biological traits, management conditions, scientific nutrition), `data/preventative_ingredients/**`, `data/product_portfolio/**`, `archive/data/legacy-parity-csv/**`.",
        f"3. **Deleted snapshot** at commit `{SNAPSHOT_COMMIT}`: `operations/snapshots/2026.07.20-omega/warehouse/**`, including `reference/papers.csv`.",
        "4. **On-disk leftover**: `legacy/warehouse/draft/authoring_staging/papers.csv` and `ingredient_evidence.csv` — staging/test EPA drafts, not the intern corpus.",
        "5. **Why Health Analysis looked empty**: `app/data/loader.py` treated `warehouse/` as a native science warehouse because `CANONICAL_MANIFEST.json` contains `science_only`. `warehouse/science/` does not exist, so formula views were empty. `warehouse_biology.merge_biology_into` existed but was never called.",
        "",
        "Read-only copies now live in `warehouse/recovery_original/`. Original git blobs were not modified.",
        "",
        "## 2. How much was recovered",
        "",
        "```json",
        json.dumps(recovery_stats, indent=2),
        "```",
        "",
        "Already-migrated intern Labrador / Golden Retriever prevalence rows in `observed_breed_conditions.csv` were **left in place** (not overwritten). Mapping entries are only for rows appended or newly created this run.",
        "",
        "## 3. Canonical tables populated (append-only)",
        "",
        "| Canonical table | Role |",
        "|---|---|",
        "| `warehouse/biology/breeds.csv` | Extra intern breed **identities** (no papers stuffed onto the entity) |",
        "| `warehouse/biology/breed_traits.csv` | Intern phenotype columns (`size`, `body_type`, `coat_type`, …) with `MISSING_PROVENANCE` |",
        "| `warehouse/biology/observed_breed_conditions.csv` | Intern `BREED_CONDITIONS.csv` facts not already present |",
        "| `warehouse/biology/trait_condition_associations.csv` | Intern SIZE/BODYTYPE/COAT/ENERGY/… condition tables |",
        "| `warehouse/prevention/condition_ingredients.csv` | Intern condition–ingredient facts not already present |",
        "| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | Intern mixed-breed interactions still lacking citations |",
        "| `warehouse/reference/papers.csv` | Snapshot paper catalog (identity + intern quote/URL; **not** copied onto `conditions.csv`) |",
        "| `warehouse/commercial/product_master.csv` | Intern product catalog identity |",
        "| `warehouse/commercial/product_functions_NEEDS_VALIDATION.csv` | Intern product functions |",
        "| `warehouse/commercial/product_feeding_guide.csv` | Intern feeding rules |",
        "",
        "`conditions.csv` remains identity-only. Evidence stays on relationship/fact tables.",
        "",
        "## 4. Which scientific facts remain missing",
        "",
        "- Intern `BREEDS.csv` phenotype has **no paper/quote/URL**. Recovered as traits with `MISSING_PROVENANCE` — not turned into fake citations.",
        "- Mixed-breed interaction rows still have no scientific quotes (flagged `MISSING_PROVENANCE` / `needs_validation`).",
        "- Life-stage and size-risk intern notes remain in `*_NEEDS_VALIDATION.csv` without papers.",
        "- `warehouse/science/` still does not exist; runtime now merges biology views instead of inventing a science tree.",
        "- No intern prevalence was estimated. No DEMO_SYNTHETIC_BREED_CARE_MODEL rows were written into the warehouse.",
        "",
        "## 5. Which rows need validation",
        "",
        f"See `warehouse/recovery_original/RECOVERY_MAPPING.csv` ({recovered} rows). Counts: NEEDS_VALIDATION={validation}, MISSING_PROVENANCE={missing_prov}, CONFLICT_REQUIRES_VALIDATION={conflict}.",
        "",
        "Existing canonical rows already marked `migrated` / `needs_validation` / `active` were not rewritten.",
        "",
        "## 6. Files now safe to archive (NOT deleted)",
        "",
        "Do **not** delete yet. After review, candidates to *archive in place* (copy, not destroy):",
        "",
        "- Git history already holds intern trees; `warehouse/recovery_original/*.zip` is the portable copy.",
        "- `legacy/warehouse/draft/authoring_staging/*` staging EPA drafts (not intern corpus).",
        "",
        "Nothing in this list has been removed.",
        "",
        "## 7. Files that must remain",
        "",
        "- `warehouse/recovery_original/` (entire tree)",
        "- `warehouse/biology/*` including `*_NEEDS_VALIDATION.csv`",
        "- `warehouse/prevention/*`",
        "- `warehouse/reference/papers.csv`",
        "- `warehouse/commercial/*` recovered intern catalog rows",
        "- git commits `a122a83`, `d6384a0` (source of intern/snapshot blobs)",
        "",
        "## Migration matrix",
        "",
        "| Legacy dataset | Canonical dataset | Rows available | Rows migrated before this run | Rows missing then recovered | Evidence preserved? | Recovery action |",
        "|---|---|---:|---:|---:|---|---|",
        f"| intern BREEDS.csv | breeds.csv + breed_traits.csv | {recovery_stats.get('breeds', {}).get('intern_breed_rows', '')} | 9 identities, 0 traits | breeds +{recovery_stats.get('breeds', {}).get('added_breeds', 0)}; traits +{recovery_stats.get('breeds', {}).get('added_traits', 0)} | quotes were never on intern BREEDS | append identity; traits MISSING_PROVENANCE |",
        f"| intern BREED_CONDITIONS.csv | observed_breed_conditions.csv | {recovery_stats.get('observed', {}).get('intern_rows', '')} | {recovery_stats.get('observed', {}).get('already_present', '')} | {recovery_stats.get('observed', {}).get('appended', '')} | yes (source_name/quote/url/year → paper_name/scientific_quote/paper_link/publication_year) | append only if not already present |",
        f"| intern *TYPE*_CONDITIONS.csv | trait_condition_associations.csv | {recovery_stats.get('traits', {}).get('intern_rows', '')} | {recovery_stats.get('traits', {}).get('already_present', '')} | {recovery_stats.get('traits', {}).get('appended', '')} | yes when intern had citations | append missing; flag conflicts |",
        f"| intern CONDITION_INGREDIENTS.csv | prevention/condition_ingredients.csv | {recovery_stats.get('ingredients', {}).get('intern_rows', '')} | {recovery_stats.get('ingredients', {}).get('already_present', '')} | {recovery_stats.get('ingredients', {}).get('appended', '')} | yes when intern had citations | append missing |",
        f"| intern MIXED_BREED_INTERACTIONS.csv | mixed_breed_NEEDS_VALIDATION.csv | {recovery_stats.get('mixed', {}).get('intern_rows', '')} | {recovery_stats.get('mixed', {}).get('already_present', '')} | {recovery_stats.get('mixed', {}).get('appended', '')} | intern had no quotes | keep flagged |",
        f"| snapshot papers.csv | reference/papers.csv | {recovery_stats.get('papers', {}).get('intern_rows', '')} | {recovery_stats.get('papers', {}).get('already_present', '')} | {recovery_stats.get('papers', {}).get('appended', '')} | yes (title/url/quote/year) | created catalog; not copied onto conditions.csv |",
        f"| intern PRODUCT_CATALOG.csv | commercial/product_master.csv | {recovery_stats.get('commercial', {}).get('intern_rows', '')} | {recovery_stats.get('commercial', {}).get('already_present', '')} | {recovery_stats.get('commercial', {}).get('appended', '')} | N/A (commercial identity) | fill empty commercial table |",
        f"| intern PRODUCT_FUNCTIONS.csv | product_functions_NEEDS_VALIDATION.csv | — | 0 | {recovery_stats.get('commercial', {}).get('functions_appended', 0)} | N/A | fill empty |",
        f"| intern PRODUCT_FEEDING_RULES.csv | product_feeding_guide.csv | — | 0 | {recovery_stats.get('commercial', {}).get('feeding_appended', 0)} | N/A | fill empty |",
        "| intern CLINICAL_EVIDENCE_BASE / ACTIVITY_* / GROOMING_* | not auto-merged into identity tables | preserved in recovery_original | prior migration discarded schedules/recommendations | 0 this run | originals preserved | do not reinterpret into facts until review |",
        "| snapshot papers (prior MIGRATION_REPORT: no paper lookup) | reference/papers.csv now exists | recovered | previously skipped as lookup | recovered this run | yes | catalog restored without stuffing conditions.csv |",
        "",
        "## Exact intern scientific records for Labrador Retriever / Golden Retriever",
        "",
        "These rows were already in `warehouse/biology/observed_breed_conditions.csv` (intern `BREED_CONDITIONS.csv` migrated earlier). They are the recovered facts that must drive Health Analysis once the loader merges biology views:",
        "",
    ]
    obs = _read_csv(ROOT / "warehouse/biology/observed_breed_conditions.csv")
    if not obs.empty:
        mask = obs["breed_name"].astype(str).str.lower().isin(["labrador retriever", "golden retriever"])
        subset = obs[mask]
        lines += [
            "| breed | condition | prevalence | paper_name | paper_link | scientific_quote | status |",
            "|---|---|---|---|---|---|---|",
        ]
        for _, row in subset.iterrows():
            quote = str(row.get("scientific_quote") or "").replace("|", "/")
            if len(quote) > 140:
                quote = quote[:137] + "..."
            lines.append(
                f"| {row.get('breed_name')} | {row.get('condition_name')} | {row.get('value_number')} | {row.get('paper_name')} | {row.get('paper_link')} | {quote} | {row.get('status')} |"
            )
    lines += [
        "",
        "## Runtime wiring (so recovered facts are visible)",
        "",
        "`load_all_tables` now merges `warehouse/biology` + `warehouse/prevention` into empty native science views. `run_package_search` uses `resolve_care_model(repo, …)` when a repository is passed, so Health Analysis reads intern warehouse rows instead of `DEMO_SYNTHETIC_BREED_CARE_MODEL`. Demo synthetic care remains a labeled fallback only when the warehouse has **no** matching breed-condition rows.",
        "",
        "## Stop for review",
        "",
        "Repository cleanup and documentation consolidation must wait until this report is reviewed. DATA FIRST. CLEANUP SECOND.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme() -> None:
    text = """# recovery_original — read-only intern preservation

Do not edit files in this directory. They are forensic copies.

- intern_a122a83/ — intern CSVs extracted from git commit a122a83
- snapshot_d6384a0/ — warehouse snapshot extracted from git commit d6384a0
- canonical_before_recovery/ — canonical warehouse folders copied before append-only recovery
- *.zip — git archive blobs used for the extract
- RECOVERY_MAPPING.csv — source_legacy_file / source_legacy_row for every recovered row

Originals in git were not modified. Canonical warehouse files outside this folder
were only appended when empty or when intern rows were absent.
"""
    (RECOVERY / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    RECOVERY.mkdir(parents=True, exist_ok=True)
    write_readme()
    _copy_canonical_snapshot()
    if not INTERN_DIR.exists():
        _extract_commit(INTERN_COMMIT, INTERN_PATHS, INTERN_DIR)
    if not SNAPSHOT_DIR.exists():
        _extract_commit(SNAPSHOT_COMMIT, SNAPSHOT_PATHS, SNAPSHOT_DIR)

    mapping: list[dict] = []
    recovery_stats = {
        "breeds": recover_breeds_and_traits(mapping),
        "observed": recover_observed_conditions(mapping),
        "traits": recover_trait_associations(mapping),
        "ingredients": recover_ingredients(mapping),
        "mixed": recover_mixed_breed(mapping),
        "papers": recover_papers(mapping),
        "commercial": recover_commercial(mapping),
    }
    _save_mapping(mapping)
    inventory = inventory_rows()
    write_inventory(inventory, recovery_stats)
    write_report(recovery_stats, inventory, mapping)
    print(json.dumps({"recovery_stats": recovery_stats, "mapping_rows": len(mapping), "inventory_files": len(inventory)}, indent=2))


if __name__ == "__main__":
    main()
