"""Phase 5.8.2 current-behavior capture for BreedNode.execute.

Does not migrate BreedNode. Compares live node output to the current
DataPlatform breeds projection using a literal copy of today's lookup.
Does not invent scientific trait or condition expectations.
"""

from __future__ import annotations

from typing import Any

from app.agent.execution_context import ExecutionContext
from app.agent.nodes.breed_node import BreedNode
from app.agent.state import DogProfileInput
from app.core.paths import clinical_root_str
from app.data.native_loader import TRAIT_TABLES
from app.data.repository import DataRepository


TRAIT_COLUMNS = tuple(col for _cat, _table, col in TRAIT_TABLES)
ROW_KEYS = (
    "breed",
    "breed_id",
    "breed_group",
    "species",
    "status",
    *TRAIT_COLUMNS,
    "_csv_row",
    "_csv_file",
)


def _repo() -> DataRepository:
    return DataRepository(clinical_root_str())


def _profile(primary: str, secondary: str | None = None) -> DogProfileInput:
    return DogProfileInput(
        name="Capture",
        primary_breed=primary,
        secondary_breed=secondary,
        age_years=5.4,
        weight_kg=30.0,
        current_environment="Temperate Outdoor",
        activity_level="Moderate",
    )


def _run(repo: DataRepository, primary: str, secondary: str | None = None) -> tuple[ExecutionContext, dict[str, Any]]:
    context = ExecutionContext(profile=_profile(primary, secondary), repository=repo)
    BreedNode().run(context)
    out = context.get_output("breed")
    assert isinstance(out, dict)
    return context, out


def _current_lookup_rows(repo: DataRepository, names: list[str]) -> list[dict[str, Any]]:
    """Literal replay of BreedNode.execute matching against the live projection."""
    breeds_df = repo.breeds()
    rows: list[dict[str, Any]] = []
    if breeds_df.empty or "breed" not in breeds_df.columns:
        return rows
    for name in names:
        key = repo.platform.normalize_breed_name(name) if hasattr(repo, "platform") else name
        hit = breeds_df[breeds_df["breed"].astype(str).str.lower() == str(key).lower()]
        if hit.empty:
            hit = breeds_df[breeds_df["breed"].astype(str).str.lower().str.contains(str(key).lower(), na=False)]
        if not hit.empty:
            rows.append(hit.iloc[0].to_dict())
    return rows


def test_output_keys_and_lookup_trace_shape():
    repo = _repo()
    context, out = _run(repo, "Labrador Retriever")
    assert sorted(out.keys()) == ["breed_names", "breed_rows", "resolved_count"]
    assert out["breed_names"] == ["Labrador Retriever"]
    assert out["resolved_count"] == 1
    row = out["breed_rows"][0]
    assert sorted(row.keys()) == sorted(ROW_KEYS)
    lookup = context.lookup_trace[0]
    assert lookup["table"] == "breeds"
    assert lookup["selection_rule"] == "normalize + match primary/secondary"
    assert lookup["rows"] == len(repo.breeds())
    assert lookup["columns"] == list(repo.breeds().columns)[:12]


def test_node_output_matches_live_projection_replay():
    repo = _repo()
    cases = [
        ("Labrador Retriever", None),
        ("Lab", None),
        ("GSD", None),
        ("Golden", None),
        ("labrador retriever", None),
        ("NotARealBreed_xyz", None),
        ("Labrador Retriever", "Golden Retriever"),
        ("Golden Retriever", "Labrador Retriever"),
        ("Retriever", None),
        ("", None),
        ("Labrador Retriever", ""),
        ("Labrador Retriever", " "),
    ]
    for primary, secondary in cases:
        names = [primary]
        if secondary:
            names.append(secondary)
        expected = _current_lookup_rows(repo, names)
        _, out = _run(repo, primary, secondary)
        assert out["breed_names"] == names
        assert out["resolved_count"] == len(expected)
        assert [r.get("breed") for r in out["breed_rows"]] == [r.get("breed") for r in expected]
        assert [r.get("breed_id") for r in out["breed_rows"]] == [r.get("breed_id") for r in expected]
        for actual, want in zip(out["breed_rows"], expected, strict=True):
            for key in ROW_KEYS:
                assert actual.get(key) == want.get(key), (primary, secondary, key)


def test_canonical_alias_and_case_resolve_same_labrador_row():
    repo = _repo()
    frame = repo.breeds()
    lab = frame[frame["breed"].astype(str) == "Labrador Retriever"].iloc[0].to_dict()
    for raw in ("Labrador Retriever", "Lab", "labrador retriever"):
        _, out = _run(repo, raw)
        assert out["breed_names"] == [raw]
        assert out["resolved_count"] == 1
        row = out["breed_rows"][0]
        assert row["breed"] == "Labrador Retriever"
        assert row["breed_id"] == lab["breed_id"]
        assert row["status"] == lab["status"]
        assert row["species"] == lab["species"]
        assert row["breed_group"] == lab["breed_group"]
        for col in TRAIT_COLUMNS:
            assert row[col] == lab[col]


def test_unknown_breed_keeps_name_and_resolves_nothing():
    repo = _repo()
    raw = "NotARealBreed_xyz"
    assert repo.platform.normalize_breed_name(raw) == raw
    _, out = _run(repo, raw)
    assert out["breed_names"] == [raw]
    assert out["breed_rows"] == []
    assert out["resolved_count"] == 0


def test_contains_retriever_is_first_dataframe_contains_hit():
    repo = _repo()
    frame = repo.breeds()
    key = repo.platform.normalize_breed_name("Retriever")
    assert key == "Retriever"
    contains = frame[frame["breed"].astype(str).str.lower().str.contains("retriever", na=False)]
    assert not contains.empty
    _, out = _run(repo, "Retriever")
    assert out["resolved_count"] == 1
    assert out["breed_rows"][0]["breed"] == contains.iloc[0]["breed"]
    assert out["breed_rows"][0]["breed_id"] == contains.iloc[0]["breed_id"]


def test_mixed_breed_preserves_input_order_not_dataframe_order():
    repo = _repo()
    frame = repo.breeds()
    lab_idx = int(frame.index[frame["breed"].astype(str) == "Labrador Retriever"][0])
    golden_idx = int(frame.index[frame["breed"].astype(str) == "Golden Retriever"][0])
    assert golden_idx < lab_idx
    _, forward = _run(repo, "Labrador Retriever", "Golden Retriever")
    assert [r["breed"] for r in forward["breed_rows"]] == [
        "Labrador Retriever",
        "Golden Retriever",
    ]
    _, reverse = _run(repo, "Golden Retriever", "Labrador Retriever")
    assert [r["breed"] for r in reverse["breed_rows"]] == [
        "Golden Retriever",
        "Labrador Retriever",
    ]
    assert reverse["breed_names"] == ["Golden Retriever", "Labrador Retriever"]


def test_empty_primary_contains_all_and_takes_first_dataframe_row():
    repo = _repo()
    first = repo.breeds().iloc[0].to_dict()
    _, out = _run(repo, "")
    assert out["breed_names"] == [""]
    assert out["resolved_count"] == 1
    assert out["breed_rows"][0]["breed"] == first["breed"]
    assert out["breed_rows"][0]["breed_id"] == first["breed_id"]


def test_empty_secondary_is_omitted_whitespace_secondary_is_not():
    repo = _repo()
    _, empty = _run(repo, "Labrador Retriever", "")
    assert empty["breed_names"] == ["Labrador Retriever"]
    assert empty["resolved_count"] == 1
    _, space = _run(repo, "Labrador Retriever", " ")
    assert space["breed_names"] == ["Labrador Retriever", " "]
    assert space["resolved_count"] == 2
    assert space["breed_rows"][1]["breed"] == repo.breeds().iloc[0]["breed"]


def test_alias_normalize_values_are_current_platform_map():
    repo = _repo()
    assert repo.platform.normalize_breed_name("Lab") == "Labrador Retriever"
    assert repo.platform.normalize_breed_name("GSD") == "German Shepherd Dog"
    assert repo.platform.normalize_breed_name("Golden") == "Golden Retriever"
    assert repo.platform.normalize_breed_name("NotARealBreed_xyz") == "NotARealBreed_xyz"


def test_csv_annotations_present_on_resolved_rows():
    _, out = _run(_repo(), "Labrador Retriever")
    row = out["breed_rows"][0]
    assert "_csv_row" in row
    assert "_csv_file" in row
    assert row["_csv_file"]
    assert row["_csv_row"] is not None
