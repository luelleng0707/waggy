from __future__ import annotations

from pathlib import Path

import pandas as pd

from repository.formulas.loader import FORMULA_DATASETS, register_formula_datasets
from repository.warehouse.warehouse_interface import CANONICAL_DATASETS, WarehouseInterface


def test_canonical_dataset_registration_includes_formula_registry_tables():
    register_formula_datasets()
    for dataset_name in FORMULA_DATASETS:
        assert dataset_name in CANONICAL_DATASETS


def test_load_dataset_returns_copy_and_preserves_cache_immutability():
    warehouse = WarehouseInterface()
    ds = "biology.breeds"
    first = warehouse.load_dataset(ds)
    first["_temp_mutation"] = "mutated"
    second = warehouse.load_dataset(ds)
    assert "_temp_mutation" not in second.columns


def test_unknown_dataset_fails_explicitly():
    warehouse = WarehouseInterface()
    try:
        warehouse.load_dataset("unknown.dataset")
    except KeyError:
        return
    assert False, "unknown dataset should raise KeyError"


def test_warehouse_validation_reports_known_blockers_without_mutating_data():
    warehouse = WarehouseInterface()
    before = warehouse.load_dataset("mechanisms.condition_mechanisms")
    report = warehouse.validate()
    after = warehouse.load_dataset("mechanisms.condition_mechanisms")
    assert isinstance(report.ok, bool)
    assert len(report.issues) >= 8
    details = [issue.detail for issue in report.issues]
    assert any("condition_mechanisms" in issue.dataset for issue in report.issues)
    assert any("food_mechanisms" in issue.dataset for issue in report.issues)
    pd.testing.assert_frame_equal(before, after)


def test_known_noncanonical_csv_readers_are_explicitly_tracked():
    root = Path(__file__).resolve().parents[2]
    known = {
        "app/data/loader.py",
        "app/data/native_loader.py",
        "app/data/repository.py",
        "app/data/warehouse/parameters.py",
        "app/data/warehouse/units.py",
        "app/data/warehouse_biology.py",
        # Ω12 mapping catalog reader (pre-existing tracker omission; not on the engine path).
        "app/normalization/catalog.py",
        "repository/validation/runtime.py",
        "scripts/recover_intern_warehouse.py",
    }
    found = set()
    for path in root.rglob("*.py"):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(("tests/", "legacy/")):
            continue
        if rel == "repository/warehouse/warehouse_interface.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "read_csv(" in text:
            found.add(rel)
    assert found == known
