"""Focused BreedKnowledge / BiologyCsvBreedCatalog parity tests.

Compares the typed catalog to the existing DataPlatform projection.
Does not invent scientific trait or condition expectations.
Does not replace FormulaGraph lookup semantics.
"""

from __future__ import annotations

import ast
import json
from dataclasses import fields
from pathlib import Path

from app.agent.state import DogProfileInput
from app.core.paths import clinical_root_str
from app.data.breed_catalog import BiologyCsvBreedCatalog
from app.data.breed_knowledge import TRAIT_NAMES, BreedKnowledge, BreedTraitFact
from app.data.native_loader import TRAIT_TABLES
from app.data.repository import DataRepository
from app.formulas.stages.health_risk import _breed_records, compute_risks


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_FILES = (
    ROOT / "app" / "data" / "breed_knowledge.py",
    ROOT / "app" / "data" / "breed_catalog.py",
)


def _repo() -> DataRepository:
    return DataRepository(clinical_root_str())


def _present(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    text = str(value)
    if text.lower() == "nan":
        return ""
    return text


def test_trait_names_match_existing_pivot_columns():
    assert TRAIT_NAMES == tuple(col for _cat, _table, col in TRAIT_TABLES)


def test_contract_modules_stay_storage_agnostic():
    forbidden = (
        "pandas",
        "pymongo",
        "motor",
        "bson",
        "fastapi",
        "app.normalization",
        "app.api",
        "warehouse.science",
    )
    for path in CONTRACT_FILES:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        for mod in imported:
            for token in forbidden:
                assert token not in mod, f"{path.name} imports {mod}"
        assert "ObjectId" not in text
        assert "read_csv" not in text


def test_trait_fact_does_not_carry_discarded_provenance_fields():
    names = {item.name for item in fields(BreedTraitFact)}
    assert names == {"trait_name", "trait_value"}


def test_known_breed_and_alias_resolve_identically():
    repo = _repo()
    frame = repo.breeds()
    catalog = repo.breed_catalog()
    lab_rows = frame[frame["breed"].astype(str) == "Labrador Retriever"]
    assert not lab_rows.empty
    lab = catalog.get_by_canonical_name("Labrador Retriever")
    assert lab is not None
    assert lab.canonical_name == "Labrador Retriever"
    assert lab.breed_id == _present(lab_rows.iloc[0]["breed_id"])
    assert catalog.normalize_name("Lab") == repo.platform.normalize_breed_name("Lab")
    assert catalog.normalize_name("Labrador") == repo.platform.normalize_breed_name("Labrador")
    via_alias = catalog.get_by_canonical_name(catalog.normalize_name("Lab"))
    assert via_alias == lab
    assert catalog.get_by_canonical_name("Lab") is None
    assert catalog.normalize_name("GSD") == repo.platform.normalize_breed_name("GSD")
    assert catalog.normalize_name("Golden") == repo.platform.normalize_breed_name("Golden")


def test_unknown_and_missing_breed_preserve_current_normalize_behavior():
    repo = _repo()
    platform = repo.platform
    catalog = repo.breed_catalog()
    raw = "NotARealBreed_xyz"
    assert catalog.normalize_name(raw) == platform.normalize_breed_name(raw) == raw
    assert catalog.get_by_canonical_name(raw) is None
    assert catalog.get_by_canonical_name("") is None
    assert catalog.normalize_name("  Lab  ") == platform.normalize_breed_name("  Lab  ")


def test_traits_and_status_match_existing_projection_for_all_rows():
    repo = _repo()
    frame = repo.breeds()
    catalog = repo.breed_catalog()
    assert catalog.warehouse_version == repo.version
    assert len(catalog.all_breeds()) == len(frame)
    for fact, (_, row) in zip(catalog.all_breeds(), frame.iterrows(), strict=True):
        assert fact.canonical_name == _present(row["breed"])
        assert fact.breed_id == _present(row["breed_id"])
        assert fact.status == _present(row["status"])
        assert fact.species == _present(row["species"])
        assert fact.breed_group == _present(row["breed_group"])
        expected = {
            name: _present(row[name])
            for name in TRAIT_NAMES
            if name in row.index and _present(row[name])
        }
        assert fact.trait_map() == expected
        assert "fact_id" not in fact.trait_map()
        assert "papers" not in fact.trait_map()
    lab = catalog.get_by_canonical_name("Labrador Retriever")
    assert lab is not None
    assert all(isinstance(t, BreedTraitFact) for t in lab.traits)


def test_mixed_breed_catalog_does_not_blend_rows():
    catalog = _repo().breed_catalog()
    lab = catalog.get_by_canonical_name("Labrador Retriever")
    golden = catalog.get_by_canonical_name("Golden Retriever")
    assert lab is not None and golden is not None
    assert lab.breed_id != golden.breed_id
    assert lab.canonical_name != golden.canonical_name
    assert catalog.get_by_canonical_name("Labrador Retriever × Golden Retriever") is None


def test_serialization_is_deterministic():
    lab = _repo().breed_catalog().get_by_canonical_name("Labrador Retriever")
    assert lab is not None
    first = json.dumps(lab.to_dict(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(lab.to_dict(), sort_keys=True, separators=(",", ":"))
    assert first == second
    clone = BreedKnowledge(
        breed_id=lab.breed_id,
        canonical_name=lab.canonical_name,
        status=lab.status,
        species=lab.species,
        breed_group=lab.breed_group,
        traits=lab.traits,
    )
    assert clone == lab


def test_risk_dataframe_path_still_matches_catalog_without_using_it_as_matcher():
    """RISK still uses DataRepository.breeds(); catalog must mirror that projection."""
    repo = _repo()
    catalog = repo.breed_catalog()
    records = _breed_records(repo, ["Lab", "Golden"])
    assert [r["breed_name"] for r in records] == ["Labrador Retriever", "Golden Retriever"]
    for record in records:
        fact = catalog.get_by_canonical_name(str(record["breed_name"]))
        assert fact is not None
        assert fact.canonical_name == record["breed_name"]
        traits = fact.trait_map()
        assert traits.get("size") == record.get("size_class")
        assert traits.get("body_type") == record.get("body_type")
        assert traits.get("energy") == record.get("energy_level")
        assert traits.get("lifespan") == record.get("lifespan_class")
        assert "breed_id" not in record


def test_compute_risks_mixed_dolly_still_resolves_both_canonical_names():
    repo = _repo()
    profile = DogProfileInput(
        name="Dolly",
        primary_breed="Labrador Retriever",
        secondary_breed="Golden Retriever",
        breed_split_pct=50.0,
        age_years=5.4,
        weight_kg=30.0,
        current_environment="Temperate Outdoor",
        activity_level="Moderate",
        sex="Female",
        birthday="2021-04-15",
        observed_conditions=["joint_stiffness", "itching"],
    )
    result = compute_risks(repo, profile)
    assert [b["breed_name"] for b in result["resolved_breeds"]] == [
        "Labrador Retriever",
        "Golden Retriever",
    ]
    assert result.get("risks")


def test_adapter_is_biology_csv_catalog_and_not_wired_into_formula_graph():
    repo = _repo()
    catalog = repo.breed_catalog()
    assert isinstance(catalog, BiologyCsvBreedCatalog)
    consumers = (
        ROOT / "app" / "agent" / "formula_graph.py",
        ROOT / "app" / "agent" / "nodes" / "breed_node.py",
        ROOT / "app" / "formulas" / "stages" / "health_risk.py",
        ROOT / "app" / "formulas" / "stages" / "biological.py",
        ROOT / "app" / "formulas" / "stages" / "epidemiology.py",
        ROOT / "app" / "data" / "scientific_care.py",
    )
    for path in consumers:
        text = path.read_text(encoding="utf-8")
        assert "breed_catalog" not in text
        assert "BreedKnowledge" not in text
        assert "BiologyCsvBreedCatalog" not in text
