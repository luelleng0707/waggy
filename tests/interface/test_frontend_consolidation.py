"""Active product UI is one workbench; old pages are archived, not competing apps."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from tests.interface.frontend_paths import WORKBENCH_HTML, WORKBENCH_JS

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "legacy" / "archive" / "frontend"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_workbench_is_the_only_active_product_html():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert "Waggy Workbench" in html
    assert "one workbench" in html
    assert "Health → Nutrition → Products → Packages" in html
    assert 'href="/classic"' not in html
    assert "Classic customer" not in html
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert js.count('"/api/v1/presentation/workbench"') >= 1
    assert "/api/v1/analyze/customer" not in js
    assert not (ROOT / "legacy" / "workbench.html").exists()
    assert not (ROOT / "legacy" / "workbench.js").exists()
    assert not (ROOT / "legacy" / "workbench.css").exists()
    assert (ROOT / "waggy-frontend" / "index.html").is_file()


def test_canonical_and_alias_routes_all_serve_workbench(client: TestClient):
    for route in ("/", "/demo", "/classic", "/business", "/developer"):
        response = client.get(route)
        assert response.status_code == 200, route
        text = response.text
        assert "workbench.js" in text
        assert "role-selector" in text
        assert "Waggy Workbench" in text
        assert "catalog-service.js" not in text
        assert "Wagtopia Business Dashboard" not in text
        assert "Clinical Execution Explorer" not in text


def test_debug_console_remains_separate_from_workbench(client: TestClient):
    debug = client.get("/debug/calculation")
    assert debug.status_code == 200
    assert "Clinical Execution Explorer" in debug.text
    assert "ppie-validation-console.js" in debug.text
    workbench = client.get("/developer")
    assert "Clinical Execution Explorer" not in workbench.text
    assert "workbench.js" in workbench.text


def test_archived_classic_and_business_uis_exist_on_disk():
    for name in (
        "index.html",
        "app.js",
        "business.html",
        "business.js",
        "catalog-service.js",
        "ppie-shell.js",
        "README.md",
    ):
        assert (ARCHIVE / name).is_file(), name
    assert not (ROOT / "legacy" / "index.html").exists()
    assert not (ROOT / "legacy" / "business.html").exists()


def test_archive_reference_route_is_not_the_product_home(client: TestClient):
    archived = client.get("/archive/frontend/index.html")
    assert archived.status_code == 200
    assert "catalog-service.js" in archived.text or "ppie-shell" in archived.text
    home = client.get("/")
    assert home.text != archived.text
    assert "workbench.js" in home.text


def test_html_surface_keys_do_not_gate_workbench_aliases(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WAGTOPIA_BUSINESS_ACCESS_KEY", "biz-key")
    monkeypatch.setenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", "dev-key")
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/business").status_code == 200
    assert client.get("/developer").status_code == 200
    assert client.get("/debug/calculation").status_code == 401
    assert client.get(
        "/debug/calculation",
        headers={"x-wagtopia-access-key": "dev-key"},
    ).status_code == 200


def test_role_boot_reads_query_or_path_without_fetch():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function roleFromLocation" in js
    start = js.index("function switchRole")
    end = js.index("function emptyState")
    body = js[start:end]
    assert "fetch(" not in body
    assert "runAnalysis" not in body
    assert "persistRole(role)" in body
