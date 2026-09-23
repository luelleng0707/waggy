"""Phase A+B: breed identity provider + resolve_breed facade.

Does not rewrite Ω12 matching. Does not wire FormulaGraph.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.agent.version import ALGORITHM_VERSION
from app.normalization.catalog import load_catalog
from app.normalization.enums import EntityKind, MappingStatus
from app.normalization.identity import (
    VARIANT_ALIAS,
    VARIANT_CANONICAL_SELF,
    breed_identity_provider,
)
from app.normalization.resolver import resolve_breed, resolve_raw
from app.normalization.text import fold_lookup_key
from app.normalization.version import MAPPING_CONFIG_VERSION

ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = ROOT / "app" / "normalization" / "identity.py"
RESOLVER_PATH = ROOT / "app" / "normalization" / "resolver.py"
BREEDS_CSV = ROOT / "warehouse" / "biology" / "breeds.csv"

LABRADOR = "BREED_B02F1BE9"
GOLDEN = "BREED_4C2466ED"
GSD = "BREED_2E91411B"

APPROVED_DISPLAY_ALIASES = {
    "lab": LABRADOR,
    "labrador": LABRADOR,
    "golden": GOLDEN,
    "german shepherd": GSD,
    "gsd": GSD,
}


def _csv_identities() -> list[tuple[str, str]]:
    import csv

    with BREEDS_CSV.open(encoding="utf-8", newline="") as handle:
        return [
            (row["breed_id"].strip(), row["breed_name"].strip())
            for row in csv.DictReader(handle)
            if row.get("breed_id") and row.get("breed_name")
        ]


def test_provider_identities_match_warehouse_breeds():
    rows = _csv_identities()
    provider = breed_identity_provider()
    identities = provider.identities()
    assert len(identities) == 48
    assert len(identities) == len(rows)
    assert {(item.canonical_id, item.canonical_name) for item in identities} == set(rows)
    assert provider.knowledge_version() == MAPPING_CONFIG_VERSION == "1.0.0"


def test_provider_exposes_approved_display_aliases_only():
    provider = breed_identity_provider()
    for alias, canonical_id in APPROVED_DISPLAY_ALIASES.items():
        variants = provider.variants_for(alias)
        assert len(variants) == 1
        assert variants[0].canonical_id == canonical_id
        assert variants[0].variant_type == VARIANT_ALIAS
        assert variants[0].review_status == "approved"
    lab = provider.variants_for("labrador retriever")
    assert len(lab) == 1
    assert lab[0].canonical_id == LABRADOR
    assert lab[0].variant_type == VARIANT_CANONICAL_SELF


def test_provider_does_not_expose_split_tokens_as_variants():
    provider = breed_identity_provider()
    assert provider.variants_for("retriever") == ()
    assert provider.variants_for("corgi") == ()
    assert provider.variants_for("husky") == ()
    assert provider.variants_for("bulldog") == ()
    assert provider.variants_for("shepherd") == ()
    assert provider.variants_for("dog") == ()
    assert not hasattr(provider, "name_tokens")


def test_provider_returns_plain_values_not_storage_handles():
    import pandas as pd

    provider = breed_identity_provider()
    identities = provider.identities()
    variants = provider.variants_for("lab")
    assert not isinstance(identities, pd.DataFrame)
    assert not isinstance(variants, pd.DataFrame)
    for item in identities:
        assert isinstance(item.canonical_id, str)
        assert isinstance(item.canonical_name, str)
        assert not str(item.canonical_id).endswith(".csv")
    source = IDENTITY_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    for mod in imported:
        assert "pandas" not in mod
        assert "pymongo" not in mod
        assert "fastapi" not in mod
        assert "bson" not in mod


def test_resolve_breed_delegates_to_resolve_raw():
    source = inspect.getsource(resolve_breed)
    assert "resolve_raw" in source
    assert "_resolve_identity" not in source
    left = resolve_breed("Lab")
    right = resolve_raw("Lab", EntityKind.BREED)
    assert left == right


def test_resolve_breed_canonical_alias_case_and_unknown():
    canonical = resolve_breed("Labrador Retriever")
    folded = resolve_breed("  labrador retriever  ")
    alias = resolve_breed("Lab")
    assert canonical.status == MappingStatus.RESOLVED
    assert canonical.canonical_id == LABRADOR
    assert canonical.canonical_name == "Labrador Retriever"
    assert folded.canonical_id == alias.canonical_id == LABRADOR
    assert resolve_breed("Labrador").canonical_id == LABRADOR
    assert resolve_breed("Golden").canonical_id == GOLDEN
    assert resolve_breed("GSD").canonical_id == GSD
    unknown = resolve_breed("obviously_unknown_breed_name")
    assert unknown.status == MappingStatus.UNRESOLVED
    assert unknown.canonical_id is None


def test_resolve_breed_shared_token_ambiguous_and_unique_unresolved():
    result = resolve_breed("Retriever")
    assert result.status == MappingStatus.AMBIGUOUS
    assert result.canonical_id is None
    assert result.canonical_name is None
    names = {item.canonical_name for item in result.candidates}
    assert names == {"Golden Retriever", "Labrador Retriever"}
    reversed_ids = {item.canonical_id for item in reversed(result.candidates)}
    assert reversed_ids == {GOLDEN, LABRADOR}
    for token in ("Corgi", "Husky", "Bulldog"):
        row = resolve_breed(token)
        assert row.status == MappingStatus.UNRESOLVED
        assert row.canonical_id is None
        assert row.candidates == []


def test_resolve_breed_blank_mixed_hyphen_and_intra_word_x():
    blank = resolve_breed("")
    assert blank.status == MappingStatus.UNRESOLVED
    assert blank.canonical_id is None
    for expr in ("Labrador x Golden", "Labrador × Golden", "Labrador / Golden"):
        mixed = resolve_breed(expr)
        assert mixed.status == MappingStatus.MIXED
        assert mixed.canonical_id is None
        assert [item.canonical_id for item in mixed.components] == [LABRADOR, GOLDEN]
    boxer = resolve_breed("Boxer")
    assert boxer.status != MappingStatus.MIXED
    hyphen = resolve_breed("Lab-rador")
    compact = resolve_breed("Labrador")
    assert hyphen.status == MappingStatus.UNRESOLVED
    assert compact.status == MappingStatus.RESOLVED
    assert hyphen.canonical_id != compact.canonical_id


def test_facade_does_not_use_legacy_dataframe_contains_or_llm():
    resolver_text = RESOLVER_PATH.read_text(encoding="utf-8")
    identity_text = IDENTITY_PATH.read_text(encoding="utf-8")
    for text in (resolver_text, identity_text):
        assert "iloc" not in text
        assert "str.contains" not in text
        assert "PPIEWellnessAgent" not in text
        assert "FormulaGraph" not in text
        assert "openai" not in text.lower()
        assert "gemini" not in text.lower()
    assert ALGORITHM_VERSION == "2.1.0"
    assert "def _resolve_identity" in resolver_text
    catalog = load_catalog()
    assert fold_lookup_key("  Lab  ") == "lab"
    assert EntityKind.BREED in catalog.kinds
