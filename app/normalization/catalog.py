"""Read-only catalog of warehouse identity rows + explicit Ω12 alias files."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.normalization.enums import EntityKind
from app.normalization.text import fold_lookup_key

REPO_ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE = REPO_ROOT / "warehouse"
MAPPING_DIR = WAREHOUSE / "mapping"

ALIAS_FILES: dict[EntityKind, str] = {
    EntityKind.BREED: "breed_aliases.csv",
    EntityKind.CONDITION: "condition_aliases.csv",
    EntityKind.PRODUCT: "product_aliases.csv",
    EntityKind.OBSERVATION: "observation_aliases.csv",
    EntityKind.SEX: "sex_aliases.csv",
}


@dataclass(frozen=True)
class EntityRecord:
    canonical_id: str
    canonical_name: str


@dataclass
class KindIndex:
    by_id: dict[str, EntityRecord] = field(default_factory=dict)
    by_name_key: dict[str, EntityRecord] = field(default_factory=dict)
    aliases: dict[str, list[EntityRecord]] = field(default_factory=dict)
    name_tokens: dict[str, list[EntityRecord]] = field(default_factory=dict)


@dataclass
class MappingCatalog:
    kinds: dict[EntityKind, KindIndex]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _add_alias(index: KindIndex, alias: str, record: EntityRecord) -> None:
    key = fold_lookup_key(alias)
    if not key:
        return
    bucket = index.aliases.setdefault(key, [])
    if all(existing.canonical_id != record.canonical_id for existing in bucket):
        bucket.append(record)


def _index_identity(records: list[EntityRecord]) -> KindIndex:
    index = KindIndex()
    for record in records:
        index.by_id[record.canonical_id] = record
        name_key = fold_lookup_key(record.canonical_name)
        if name_key:
            index.by_name_key[name_key] = record
            _add_alias(index, record.canonical_name, record)
        _add_alias(index, record.canonical_id, record)
        for token in fold_lookup_key(record.canonical_name).split(" "):
            if len(token) < 3:
                continue
            index.name_tokens.setdefault(token, [])
            if all(existing.canonical_id != record.canonical_id for existing in index.name_tokens[token]):
                index.name_tokens[token].append(record)
    return index


def _load_alias_file(index: KindIndex, path: Path) -> None:
    df = _read_csv(path)
    if df.empty:
        return
    for _, row in df.iterrows():
        canonical_id = str(row.get("canonical_id") or "").strip()
        alias = str(row.get("alias") or "").strip()
        if not canonical_id or not alias:
            continue
        record = index.by_id.get(canonical_id)
        if record is None:
            raise ValueError(
                f"Ω12 alias {alias!r} in {path.name} points at unknown id {canonical_id!r}"
            )
        _add_alias(index, alias, record)


def _breeds() -> list[EntityRecord]:
    df = _read_csv(WAREHOUSE / "biology" / "breeds.csv")
    out: list[EntityRecord] = []
    for _, row in df.iterrows():
        cid = str(row.get("breed_id") or "").strip()
        name = str(row.get("breed_name") or "").strip()
        if cid and name:
            out.append(EntityRecord(canonical_id=cid, canonical_name=name))
    return out


def _conditions() -> list[EntityRecord]:
    df = _read_csv(WAREHOUSE / "biology" / "conditions.csv")
    out: list[EntityRecord] = []
    for _, row in df.iterrows():
        cid = str(row.get("condition_id") or "").strip()
        name = str(row.get("condition_name") or "").strip()
        if cid and name:
            out.append(EntityRecord(canonical_id=cid, canonical_name=name))
    return out


def _products() -> list[EntityRecord]:
    df = _read_csv(WAREHOUSE / "commercial" / "product_master.csv")
    out: list[EntityRecord] = []
    for _, row in df.iterrows():
        cid = str(row.get("product_id") or "").strip()
        name = str(row.get("product_name") or "").strip()
        if cid and name:
            out.append(EntityRecord(canonical_id=cid, canonical_name=name))
    return out


def _brands() -> list[EntityRecord]:
    df = _read_csv(WAREHOUSE / "commercial" / "product_master.csv")
    seen: dict[str, EntityRecord] = {}
    for _, row in df.iterrows():
        brand = str(row.get("brand") or "").strip()
        if not brand:
            continue
        key = fold_lookup_key(brand)
        seen.setdefault(key, EntityRecord(canonical_id=brand, canonical_name=brand))
    return list(seen.values())


def _observations() -> list[EntityRecord]:
    df = _read_csv(MAPPING_DIR / "observation_aliases.csv")
    seen: dict[str, EntityRecord] = {}
    for _, row in df.iterrows():
        cid = str(row.get("canonical_id") or "").strip()
        name = str(row.get("canonical_name") or cid).strip()
        if cid:
            seen[cid] = EntityRecord(canonical_id=cid, canonical_name=name)
    return list(seen.values())


def _sexes() -> list[EntityRecord]:
    return [
        EntityRecord(canonical_id="male", canonical_name="male"),
        EntityRecord(canonical_id="female", canonical_name="female"),
    ]


_LOADERS = {
    EntityKind.BREED: _breeds,
    EntityKind.CONDITION: _conditions,
    EntityKind.PRODUCT: _products,
    EntityKind.BRAND: _brands,
    EntityKind.OBSERVATION: _observations,
    EntityKind.SEX: _sexes,
}


@lru_cache(maxsize=1)
def load_catalog() -> MappingCatalog:
    kinds: dict[EntityKind, KindIndex] = {}
    for kind, loader in _LOADERS.items():
        index = _index_identity(loader())
        alias_name = ALIAS_FILES.get(kind)
        if alias_name:
            _load_alias_file(index, MAPPING_DIR / alias_name)
        kinds[kind] = index
    return MappingCatalog(kinds=kinds)


def reset_catalog_cache() -> None:
    load_catalog.cache_clear()
