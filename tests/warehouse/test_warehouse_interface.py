from __future__ import annotations

from repository.warehouse import WarehouseInterface


def test_load_all_canonical_datasets():
    interface = WarehouseInterface()
    tables = interface.load_all()
    assert "biology.breeds" in tables
    assert "biology.conditions" in tables
    assert "commercial.product_master" in tables


def test_validation_report_shape():
    interface = WarehouseInterface()
    report = interface.validate()
    assert hasattr(report, "ok")
    assert hasattr(report, "issues")
