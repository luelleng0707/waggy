from __future__ import annotations

import csv
from pathlib import Path

from app.ui.cstc.suite_utils import default_demo_profile
from scripts.run_wagtopia_local import LocalInterfaceSuite
from scripts.run_wagtopia_remote import (
    CUSTOMER_ALLOWED_API_PREFIXES,
    CUSTOMER_BLOCKED_PREFIXES,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _suite():
    class _Args:
        api_host = "127.0.0.1"
        api_port = 8000
        ui_port = 8080
        api_key = "wagtopia-demo-key"
        no_browser = True
        no_desktop = True
        demo_mode = True
        api_debug = True
        smoke_seconds = 0

    return LocalInterfaceSuite(_Args())


def test_customer_route():
    suite = _suite()
    assert suite.customer_url == "http://127.0.0.1:8080/"


def test_calculation_route():
    suite = _suite()
    assert suite.developer_url == "http://127.0.0.1:8080/developer"
    assert "calculavtion" not in suite.developer_url


def test_customer_api_proxy():
    source = (_repo_root() / "scripts" / "run_wagtopia_local.py").read_text(encoding="utf-8")
    assert "self.path.startswith(\"/api/\")" in source
    assert "self.path.startswith(\"/health\")" in source


def test_demo_profile():
    key, profile = default_demo_profile()
    assert key == "mixed_lab_golden"
    assert profile.name == "Dolly"
    assert profile.primary_breed == "Labrador Retriever"
    assert profile.secondary_breed == "Golden Retriever"
    assert profile.breed_split_pct == 50.0


def test_customer_claim_coverage():
    path = _repo_root() / "docs" / "interface" / "CUSTOMER_UI_CLAIM_COVERAGE.csv"
    assert path.exists()
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    assert rows
    required = {
        "claim",
        "runtime_source",
        "ui_section",
        "status",
        "evidence_source",
        "missing_reason",
        "implementation_required",
    }
    assert required.issubset(rows[0].keys())


def test_remote_launcher_configuration():
    assert "/api/v1/clinical-report" in CUSTOMER_ALLOWED_API_PREFIXES
    assert "/api/v1/presentation/catalog" in CUSTOMER_ALLOWED_API_PREFIXES
    assert "/api/v1/store" in CUSTOMER_ALLOWED_API_PREFIXES
    assert "/debug/" in CUSTOMER_BLOCKED_PREFIXES
    assert "/api/v1/ppie/" in CUSTOMER_BLOCKED_PREFIXES


def test_presentation_contract():
    contract = (_repo_root() / "docs" / "WAGGY_SYSTEM.md").read_text(
        encoding="utf-8"
    )
    for idx in range(1, 13):
        assert f"{idx}." in contract

    customer_sources = [
        _repo_root() / "legacy" / "app.js",
        _repo_root() / "legacy" / "ppie-shell.js",
        _repo_root() / "legacy" / "ppie-ui.js",
        _repo_root() / "legacy" / "ppie-sheets.js",
    ]
    forbidden_runtime = (
        "repository.mathematics",
        "repository.formulas",
        "repository.optimization",
        "repository.science_graph",
        "repository.warehouse_qa",
    )
    forbidden_data_reads = (
        "fetch('/warehouse/",
        "fetch(\"/warehouse/",
        "fetch('/data/",
        "fetch(\"/data/",
        "read_csv(",
    )
    app_js = (_repo_root() / "legacy" / "app.js").read_text(encoding="utf-8")
    assert "/api/v1/clinical-report" in app_js
    for src in customer_sources:
        text = src.read_text(encoding="utf-8")
        for mod in forbidden_runtime:
            assert mod not in text
        for marker in forbidden_data_reads:
            assert marker not in text

    adapter_source = (_repo_root() / "app" / "ui" / "cstc" / "adapter.py").read_text(encoding="utf-8")
    assert "self.client.analyze(" in adapter_source
    assert "self.client.assess(" in adapter_source
    assert "build_presentation(" in adapter_source
    for prohibited in ("numpy", "pandas", "scipy", "equation", "optimize"):
        assert prohibited not in adapter_source
