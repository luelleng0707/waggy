"""Phase C offline comparison tests. Do not migrate consumers."""

from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path

from app.agent.execution_context import ExecutionContext
from app.agent.nodes.breed_node import BreedNode
from app.agent.state import DogProfileInput
from app.agent.version import ALGORITHM_VERSION
from app.core.paths import clinical_root_str
from app.data.repository import DataRepository
from app.normalization.enums import MappingStatus
from app.normalization.identity import breed_identity_provider
from app.normalization.resolver import resolve_breed
from app.normalization.version import MAPPING_CONFIG_VERSION
from app.offline.breed_identity_compare import (
    AMBIGUOUS,
    CLASSIFICATIONS,
    EXPECTED_ALIAS_COUNT,
    EXPECTED_CANONICAL_COUNT,
    REGRESSION,
    SAME,
    UNRESOLVED,
    ComparisonReport,
    LegacyOutcome,
    Omega12Outcome,
    build_corpus,
    classify,
    comparison_notes,
    legacy_resolve_breed_for_comparison,
    omega12_resolve_breed_for_comparison,
    render_report,
    run_comparison,
)

ROOT = Path(__file__).resolve().parents[2]
COMPARE_PATH = ROOT / "app" / "offline" / "breed_identity_compare.py"
BREEDS_CSV = ROOT / "warehouse" / "biology" / "breeds.csv"
ALIAS_CSV = ROOT / "warehouse" / "mapping" / "breed_aliases.csv"
RESOLVER_PATH = ROOT / "app" / "normalization" / "resolver.py"

BASELINE_SINGLE_PRIMARY = (
    "Labrador Retriever",
    "Lab",
    "GSD",
    "Golden",
    "labrador retriever",
    "NotARealBreed_xyz",
    "Retriever",
    "",
)


def _repo() -> DataRepository:
    return DataRepository(clinical_root_str())


def _items(category: str):
    return [item for item in build_corpus() if item.category == category]


def _outcome(
    *,
    status: str,
    selected: bool,
    oid: str | None = None,
    lid: str | None = None,
    oname: str | None = None,
    lname: str | None = None,
    candidates: tuple[tuple[str, str | None], ...] = (),
) -> tuple[LegacyOutcome, Omega12Outcome]:
    legacy = LegacyOutcome(
        selected=selected,
        canonical_name=lname,
        canonical_id=lid,
        resolved_count=int(selected),
    )
    omega = Omega12Outcome(
        status=status,
        canonical_name=oname,
        canonical_id=oid,
        mapping_rule="test",
        mapping_source="test",
        candidates=candidates,
        components=(),
    )
    return legacy, omega


def test_canonical_identity_corpus_generation():
    items = _items("canonical")
    assert len(items) == EXPECTED_CANONICAL_COUNT
    names = [item.input for item in items]
    assert len(names) == len(set(names))
    assert all(item.source == "warehouse_identity" for item in items)
    provider_names = [record.canonical_name for record in breed_identity_provider().identities()]
    assert names == provider_names


def test_approved_alias_corpus_generation():
    items = _items("approved_alias")
    assert len(items) == EXPECTED_ALIAS_COUNT
    assert [item.input for item in items] == [
        "Lab",
        "Labrador",
        "Golden",
        "German Shepherd",
        "GSD",
    ]
    assert all(item.source == "omega12_mapping" for item in items)
    assert items[0].related_canonical_names == ("Labrador Retriever",)
    assert items[2].related_canonical_names == ("Golden Retriever",)
    assert items[4].related_canonical_names == ("German Shepherd Dog",)


def test_shared_token_corpus_generation():
    items = _items("shared_token")
    assert items, "shared-token cases must be derived from live canonical names"
    assert all(item.source == "derived_from_warehouse_identity" for item in items)
    assert [item.input for item in items] == sorted(item.input for item in items)
    for item in items:
        assert len(item.related_canonical_names) >= 2
        result = resolve_breed(item.input)
        assert result.status == MappingStatus.AMBIGUOUS
        assert result.canonical_id is None
        assert {candidate.canonical_name for candidate in result.candidates} == set(
            item.related_canonical_names
        )


def test_unique_token_boundary():
    items = _items("unique_token")
    assert [item.input for item in items] == ["Corgi", "Husky", "Bulldog"]
    for item in items:
        result = resolve_breed(item.input)
        assert result.status == MappingStatus.UNRESOLVED
        assert result.canonical_id is None
        assert result.candidates == []
        assert len(item.related_canonical_names) == 1


def test_blank_boundary():
    items = _items("blank")
    assert [item.input for item in items] == ["", "   "]
    for item in items:
        assert resolve_breed(item.input).status == MappingStatus.UNRESOLVED


def test_mixed_expressions():
    items = _items("mixed")
    inputs = [item.input for item in items]
    assert "Lab x Golden" in inputs
    assert "Lab × Golden" in inputs
    assert "Lab / Golden" in inputs
    assert "Beagle x French Bulldog" in inputs
    assert not any(" mix " in value.lower() or "cross" in value.lower() for value in inputs)
    for item in items:
        result = resolve_breed(item.input)
        assert result.status == MappingStatus.MIXED
        assert result.canonical_id is None
        assert [component.canonical_id for component in result.components]
        assert "50" not in (result.canonical_name or "")


def test_intra_word_x():
    items = _items("intra_word_x")
    assert [item.input for item in items] == ["Foxhound"]
    result = resolve_breed("Foxhound")
    assert result.status == MappingStatus.RESOLVED
    assert result.status != MappingStatus.MIXED


def test_unknown_input():
    items = _items("unknown")
    assert [item.input for item in items] == ["__unknown_breed_phase_c__"]
    assert items[0].source == "synthetic_test_input"
    assert resolve_breed(items[0].input).status == MappingStatus.UNRESOLVED


def test_deterministic_corpus_ordering():
    left = build_corpus()
    right = build_corpus()
    assert left == right
    categories = list(dict.fromkeys(item.category for item in left))
    assert categories == [
        "canonical",
        "approved_alias",
        "shared_token",
        "unique_token",
        "blank",
        "mixed",
        "intra_word_x",
        "punctuation_boundary",
        "unknown",
        "normalization",
    ]


def test_deterministic_comparison_output():
    repo = _repo()
    left = run_comparison(repository=repo)
    right = run_comparison(repository=repo)
    assert left == right
    text = render_report(left)
    assert text == render_report(right)
    assert "IMPROVED" not in text
    assert "winner" not in text.lower()
    assert "accuracy" not in text.lower()
    assert "Ω12 is smarter" not in text
    assert "legacy is wrong" not in text.lower()


def test_candidate_permutation_does_not_affect_semantic_classification():
    golden = ("BREED_4C2466ED", "Golden Retriever")
    lab = ("BREED_B02F1BE9", "Labrador Retriever")
    legacy = LegacyOutcome(
        selected=True,
        canonical_name="Golden Retriever",
        canonical_id="BREED_4C2466ED",
        resolved_count=1,
    )
    forward = Omega12Outcome(
        status="AMBIGUOUS",
        canonical_name=None,
        canonical_id=None,
        mapping_rule="shared_name_token",
        mapping_source="canonical_name_token_index",
        candidates=(golden, lab),
        components=(),
    )
    reverse = Omega12Outcome(
        status="AMBIGUOUS",
        canonical_name=None,
        canonical_id=None,
        mapping_rule="shared_name_token",
        mapping_source="canonical_name_token_index",
        candidates=(lab, golden),
        components=(),
    )
    assert classify(legacy, forward) == classify(legacy, reverse) == AMBIGUOUS
    assert classify(*_outcome(status="RESOLVED", selected=True, oid="A", lid="A", oname="n", lname="n")) == SAME
    assert classify(*_outcome(status="UNRESOLVED", selected=False)) == SAME
    assert classify(*_outcome(status="UNRESOLVED", selected=True, lid="A", lname="Beagle")) == UNRESOLVED
    assert classify(*_outcome(status="MIXED", selected=True, lid="A", lname="Beagle")) == AMBIGUOUS
    assert classify(*_outcome(status="RESOLVED", selected=True, oid="A", lid="B", oname="a", lname="b")) == AMBIGUOUS
    assert REGRESSION not in {
        classify(legacy, forward),
        classify(*_outcome(status="UNRESOLVED", selected=True, lid="A", lname="Beagle")),
        classify(*_outcome(status="RESOLVED", selected=False, oid="A", oname="a")),
    }


def test_legacy_adapter_matches_current_breed_node():
    repo = _repo()
    for primary in BASELINE_SINGLE_PRIMARY:
        context = ExecutionContext(
            profile=DogProfileInput(
                name="PhaseC",
                primary_breed=primary,
                secondary_breed=None,
                age_years=5.4,
                weight_kg=30.0,
                current_environment="Temperate Outdoor",
                activity_level="Moderate",
            ),
            repository=repo,
        )
        BreedNode().run(context)
        payload = context.get_output("breed")
        adapted = legacy_resolve_breed_for_comparison(primary, repository=repo)
        if payload["resolved_count"] == 0:
            assert adapted.selected is False
            assert adapted.canonical_id is None
            continue
        row = payload["breed_rows"][0]
        assert adapted.selected is True
        assert adapted.canonical_id == str(row["breed_id"])
        assert adapted.canonical_name == str(row["breed"])
        assert adapted.resolved_count == payload["resolved_count"]


def test_omega12_adapter_calls_resolve_breed(monkeypatch):
    source = inspect.getsource(omega12_resolve_breed_for_comparison)
    assert "resolve_breed(" in source
    assert "_resolve_identity" not in source
    called: list[str] = []
    real = resolve_breed

    def wrapped(raw_value, **kwargs):
        called.append(raw_value)
        return real(raw_value, **kwargs)

    monkeypatch.setattr("app.offline.breed_identity_compare.resolve_breed", wrapped)
    outcome = omega12_resolve_breed_for_comparison("Lab")
    assert called == ["Lab"]
    assert outcome.status == "RESOLVED"
    assert outcome.canonical_id == "BREED_B02F1BE9"
    resolver_text = RESOLVER_PATH.read_text(encoding="utf-8")
    assert "def _resolve_identity" in resolver_text
    assert ALGORITHM_VERSION == "2.1.0"
    assert MAPPING_CONFIG_VERSION == "1.0.0"


def test_comparison_harness_does_not_import_formula_graph():
    tree = ast.parse(COMPARE_PATH.read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    for mod in imported:
        assert mod != "app.agent.formula_graph"
        assert not mod.startswith("app.agent.formula_graph.")
        assert "pymongo" not in mod
        assert "bson" not in mod
        assert "requests" not in mod
        assert "urllib" not in mod
        assert "httpx" not in mod
        assert "openai" not in mod
        assert "google" not in mod
    text = COMPARE_PATH.read_text(encoding="utf-8")
    assert "from app.agent.formula_graph" not in text
    assert "import FormulaGraph" not in text
    assert 'return "IMPROVED"' not in text
    assert "IMPROVED" not in CLASSIFICATIONS


def test_no_network_or_database_mutation():
    before_breeds = hashlib.sha256(BREEDS_CSV.read_bytes()).hexdigest()
    before_aliases = hashlib.sha256(ALIAS_CSV.read_bytes()).hexdigest()
    report = run_comparison()
    assert hashlib.sha256(BREEDS_CSV.read_bytes()).hexdigest() == before_breeds
    assert hashlib.sha256(ALIAS_CSV.read_bytes()).hexdigest() == before_aliases
    assert report.mapping_config_version == "1.0.0"
    assert report.warehouse_version == "5.0.0-biology"
    counts = {label: 0 for label in CLASSIFICATIONS}
    for row in report.rows:
        counts[row.classification] += 1
        assert row.classification != REGRESSION
        assert "improved" not in row.notes.lower()
        assert "smarter" not in row.notes.lower()
        assert "more accurate" not in row.notes.lower()
        assert "legacy is wrong" not in row.notes.lower()
        assert "Ω12 wins" not in row.notes
        assert "50/50" not in row.notes
        assert "50%" not in row.notes
    assert counts[REGRESSION] == 0
    assert counts[SAME] >= 1
    retriever = next(row for row in report.rows if row.input == "Retriever")
    assert retriever.classification == AMBIGUOUS
    assert retriever.omega12.status == "AMBIGUOUS"
    assert retriever.legacy.selected is True
    blank = next(row for row in report.rows if row.input == "" and row.category == "blank")
    assert blank.classification == UNRESOLVED
    assert blank.omega12.status == "UNRESOLVED"
    assert blank.legacy.canonical_name == "Beagle"
    corgi = next(row for row in report.rows if row.input == "Corgi")
    assert corgi.classification == UNRESOLVED
    assert corgi.omega12.status == "UNRESOLVED"
    mixed = next(row for row in report.rows if row.input == "Lab x Golden")
    assert mixed.classification == AMBIGUOUS
    assert mixed.omega12.status == "MIXED"
    assert mixed.omega12.canonical_id is None
    fox = next(row for row in report.rows if row.category == "intra_word_x")
    assert fox.classification == SAME
    assert fox.omega12.status == "RESOLVED"
    text = render_report(report)
    assert "## Detailed results — disagreements" in text
    assert "Retriever" in text


def test_report_lists_every_disagreement():
    report = run_comparison()
    text = render_report(report)
    disagreements = [row for row in report.rows if row.classification != SAME]
    assert disagreements
    for row in disagreements:
        assert repr(row.input) in text
        assert f"Classification: {row.classification}" in text
    same_rows = [row for row in report.rows if row.classification == SAME]
    assert same_rows
    assert "SAME cases (compact)" in text


def test_comparison_notes_are_factual():
    legacy = LegacyOutcome(
        selected=True,
        canonical_name="Golden Retriever",
        canonical_id="G",
        resolved_count=1,
    )
    omega = Omega12Outcome(
        status="AMBIGUOUS",
        canonical_name=None,
        canonical_id=None,
        mapping_rule="shared_name_token",
        mapping_source="canonical_name_token_index",
        candidates=(("G", "Golden Retriever"), ("L", "Labrador Retriever")),
        components=(),
    )
    notes = comparison_notes(legacy, omega, AMBIGUOUS)
    assert "multiple canonical candidates" in notes
    assert "legacy returned a single result" in notes
    assert "improved" not in notes.lower()
    assert "smarter" not in notes.lower()
