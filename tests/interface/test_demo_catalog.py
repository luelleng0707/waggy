from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pandas as pd
import pytest

from app.api.main import app
from app.data.demo_catalog import (
    CANONICAL_PRODUCT_COLUMNS,
    DEMO_TABLES,
    demo_mode_enabled,
    demo_product_ids,
    demo_table_frames,
    overlay_frame,
)


ROOT = Path(__file__).resolve().parents[2]


def test_demo_mode_is_off_by_default():
    assert demo_mode_enabled() is False


def test_production_overlay_does_not_replace_empty_catalog():
    empty = pd.DataFrame(columns=list(CANONICAL_PRODUCT_COLUMNS))
    out = overlay_frame("products", empty)
    assert out.empty
    assert list(out.columns) == list(empty.columns)


def test_demo_catalog_loads_when_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    assert demo_mode_enabled() is True
    frames = demo_table_frames()
    products = frames["products"]
    assert 8 <= len(products) <= 15
    assert set(CANONICAL_PRODUCT_COLUMNS).issubset(set(products.columns))
    ids = set(products["product_id"].astype(str))
    assert ids == demo_product_ids()
    overlaid = overlay_frame("products", pd.DataFrame())
    assert len(overlaid) == len(products)
    assert set(overlaid["product_id"].astype(str)) == ids


def test_demo_products_conform_to_canonical_catalog_schema():
    products = demo_table_frames()["products"]
    for column in CANONICAL_PRODUCT_COLUMNS:
        assert column in products.columns
        assert products[column].notna().all()
    pricing = demo_table_frames()["product_pricing"]
    for column in ("product_id", "list_price_rmb", "package_units", "unit_label"):
        assert column in pricing.columns
    feeding = demo_table_frames()["product_feeding_rules"]
    for column in ("product_id", "weight_min_kg", "weight_max_kg", "daily_amount", "daily_unit"):
        assert column in feeding.columns


def test_demo_catalog_api_is_gated(monkeypatch: pytest.MonkeyPatch):
    off = TestClient(app)
    off_body = off.get("/api/v1/catalog").json()
    assert off_body.get("demo_catalog") is False
    assert off_body.get("catalog_source") == "warehouse"
    production_ids = {str(row.get("product_id")) for row in off_body.get("products") or []}

    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    on = TestClient(app)
    health = on.get("/health").json()
    assert health.get("demo_catalog") is True
    assert health.get("catalog_count") == len(demo_product_ids())
    catalog = on.get("/api/v1/catalog").json()
    assert catalog.get("demo_catalog") is True
    assert catalog.get("count") == len(demo_product_ids())
    demo_ids = {str(row.get("product_id")) for row in catalog.get("products") or []}
    assert demo_ids == demo_product_ids()
    if not production_ids:
        assert demo_ids != production_ids


def test_launchers_document_demo_mode_and_surface_urls():
    dev = (ROOT / "scripts" / "run_dev.py").read_text(encoding="utf-8")
    local = (ROOT / "scripts" / "run_wagtopia_local.py").read_text(encoding="utf-8")
    for source in (dev, local):
        assert "CUSTOMER:" in source
        assert "BUSINESS:" in source
        assert "DEVELOPER:" in source
        assert "API:" in source
        assert "HEALTH:" in source
        assert "WAGTOPIA_DEMO_MODE" in source


def test_no_scientific_warehouse_csv_is_modified():
    master = ROOT / "warehouse" / "commercial" / "product_master.csv"
    assert master.exists()
    warehouse_blob = ""
    for path in (ROOT / "warehouse").rglob("*.csv"):
        if "recovery_original" in path.as_posix():
            continue
        warehouse_blob += path.read_text(encoding="utf-8", errors="ignore")
    for name in demo_table_frames()["products"]["product_name"].astype(str):
        assert name not in warehouse_blob
    assert "Demo Fresh Beef Bowl" not in warehouse_blob
    assert DEMO_TABLES == {
        "products",
        "product_pricing",
        "product_components",
        "product_feeding_rules",
        "product_functions",
    }
