from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from scripts.run_wagtopia_local import LocalInterfaceSuite


def test_launcher_uses_canonical_interface_routes():
    suite = LocalInterfaceSuite(
        Namespace(
            api_host="127.0.0.1",
            api_port=8000,
            ui_port=8080,
            api_key="wagtopia-demo-key",
            no_browser=True,
            no_desktop=True,
            demo_mode=True,
            api_debug=True,
            smoke_seconds=0,
        )
    )
    assert suite.customer_url == "http://127.0.0.1:8080/"
    assert suite.business_url == "http://127.0.0.1:8080/business"
    assert suite.developer_url == "http://127.0.0.1:8080/developer"
    assert "calculavtion" not in suite.developer_url


def test_typo_route_reference_absent_in_active_interface_sources():
    root = Path(__file__).resolve().parents[2]
    active_paths = [
        root / "scripts" / "run_wagtopia_local.py",
        root / "app" / "ui" / "cstc" / "desktop.py",
        root / "app" / "ui" / "cstc" / "adapter.py",
        root / "app" / "ui" / "cstc" / "api_client.py",
        root / "legacy" / "archive" / "frontend" / "index.html",
        root / "legacy" / "archive" / "frontend" / "app.js",
        root / "legacy" / "archive" / "frontend" / "ppie-shell.js",
        root / "legacy" / "archive" / "frontend" / "ppie-dev-menu.js",
        root / "legacy" / "archive" / "frontend" / "ppie-trace.js",
        root / "legacy" / "debug" / "calculation.html",
    ]
    for path in active_paths:
        text = path.read_text(encoding="utf-8")
        assert "calculavtion" not in text, f"Typo route found in {path}"


def test_ui_layer_has_no_scientific_runtime_imports():
    root = Path(__file__).resolve().parents[2]
    cstc_dir = root / "app" / "ui" / "cstc"
    forbidden = (
        "repository.mathematics",
        "repository.optimization",
        "repository.formulas",
        "repository.science_graph",
        "repository.warehouse_qa",
    )
    for py in cstc_dir.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        for mod in forbidden:
            assert mod not in text, f"{py} imports forbidden module {mod}"
