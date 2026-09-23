"""Unified demo workbench: one analysis, four role projections, one URL."""

from __future__ import annotations

import re

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


from tests.interface.frontend_paths import (
    CLIENT_JS,
    CONFIG_JS,
    WORKBENCH_CSS,
    WORKBENCH_HTML,
    WORKBENCH_JS,
)

WORKBENCH_PATH_TOKEN = "/api/v1/presentation/workbench"


def _dolly_payload() -> dict:
    return {
        "name": "Dolly",
        "pet_name": "Dolly",
        "breeds": ["Golden Retriever", "Labrador Retriever"],
        "birthday": "2021-03-15",
        "weight": 30.1,
        "sex": "Female",
        "activity_level": "High",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
        "correlation_id": "omega97-demo-001",
        "role_context": {"groomer": {"observations": "coat dryness noted at shoulders"}},
    }


def _package_ids(role_payload: dict) -> list[str]:
    packages = (
        role_payload.get("package_composition")
        or (role_payload.get("wellness") or {}).get("package_composition")
        or (role_payload.get("portfolio") or {}).get("package_composition")
        or (role_payload.get("package_optimization") or {}).get("composition")
        or []
    )
    ids: list[str] = []
    for pkg in packages:
        for item in pkg.get("products") or []:
            pid = item.get("product_id")
            if pid and pid != "NOT AVAILABLE FROM RUNTIME":
                ids.append(str(pid))
    return ids


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_unified_demo_loads(demo_client: TestClient):
    response = demo_client.get("/")
    assert response.status_code == 200
    text = response.text
    assert "Personalized Wellness Analysis" in text
    assert "workbench.js" in text
    assert "Load Demo Dog" in text
    assert "module-analyze" in text
    assert "page-module" in text
    demo = demo_client.get("/demo")
    assert demo.status_code == 200
    assert "role-selector" in demo.text


def test_role_selector_exists():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    for role in ("customer", "groomer", "business", "developer"):
        assert f'data-role="{role}"' in html


def test_customer_view_renders(demo_client: TestClient):
    html = demo_client.get("/").text
    assert 'data-view="customer"' in html
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function renderCustomer" in js
    assert "Care packages" in js


def test_groomer_view_renders():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert 'data-view="groomer"' in html
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function renderGroomer" in js
    assert "Observations" in js


def test_business_view_renders():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert 'data-view="business"' in html
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function renderBusiness" in js
    assert "Demo commercial dataset not loaded" in js


def test_developer_view_renders():
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert 'data-view="developer"' in html
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "function renderDeveloper" in js
    assert "PACKAGE_OPTIMIZER_V2_1" in js
    assert "PRODUCT_MATCH_V2_1" in js


def test_role_switching_does_not_regenerate_analysis():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    start = js.index("function switchRole")
    end = js.index("function emptyState")
    body = js[start:end]
    assert "fetch(" not in body
    assert "runAnalysis" not in body
    assert "currentRole = role" in body


def test_workbench_one_analysis_shared_across_roles(demo_client: TestClient):
    response = demo_client.post("/api/v1/presentation/workbench", json=_dolly_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "workbench_presentation.v1"
    assert body["presentation_correlation_id"] == "omega97-demo-001"
    roles = body["roles"]
    assert set(roles) == {"customer", "groomer", "business", "developer"}
    assert roles["customer"]["surface"] == "customer"
    assert roles["groomer"]["surface"] == "groomer"
    assert roles["business"]["surface"] == "business"
    assert roles["developer"]["surface"] == "developer"
    assert roles["developer"]["correlation_id"] == "omega97-demo-001"
    assert body["canonical"]["correlation_id"] == "omega97-demo-001"
    customer_ids = _package_ids(roles["customer"])
    assert customer_ids
    assert customer_ids == _package_ids(roles["groomer"])
    assert customer_ids == _package_ids(roles["business"])
    assert customer_ids == _package_ids(roles["developer"])
    assert body["canonical"]["package_optimization"]["algorithm"] == "PACKAGE_OPTIMIZER_V2_1"
    assert body["canonical"]["product_matching"]["algorithm"] == "PRODUCT_MATCH_V2_1"
    assert body["canonical"]["system"]["ai"]["llm_used"] is False
    assert body["demo_catalog"] is True


def _json_contains_token(obj: object, token: str, *, _depth: int = 0) -> bool:
    """Walk keys and string values. Do not str() the whole customer blob."""
    if _depth > 48:
        return False
    if isinstance(obj, dict):
        for key, value in obj.items():
            if token in str(key):
                return True
            if _json_contains_token(value, token, _depth=_depth + 1):
                return True
        return False
    if isinstance(obj, list):
        return any(_json_contains_token(item, token, _depth=_depth + 1) for item in obj)
    if isinstance(obj, str):
        return token in obj
    return False


def test_customer_does_not_expose_developer_internals(demo_client: TestClient):
    html = demo_client.get("/").text
    assert "formula_execution.v2" not in html
    assert "warehouse_row_status" not in html
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly_payload()).json()
    customer = body["roles"]["customer"]
    assert not _json_contains_token(customer, "formula_execution")
    assert not _json_contains_token(customer, "independent_of_product_match")
    assert not _json_contains_token(customer, "build_optimized_packages")
    developer = body["roles"]["developer"]
    assert developer["package_optimization"]["formula_id"] == "PACKAGE_OPTIMIZER_V2_1"
    assert developer["package_optimization"]["independent_of_product_match"] is True
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    cust_start = js.index("function renderCustomer")
    cust_end = js.index("function renderGroomer")
    assert "formula_execution" not in js[cust_start:cust_end]
    assert "PACKAGE_OPTIMIZER_V2_1" not in js[cust_start:cust_end]


def test_developer_exposes_optimizer_provenance(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly_payload()).json()
    opt = body["roles"]["developer"]["package_optimization"]
    assert opt["code_file"] == "app/agent/package_optimizer.py"
    assert opt["function"] == "build_optimized_packages"
    assert opt["packages"]
    assert any(pkg.get("selected_product_ids") for pkg in opt["packages"])
    composition = opt["composition"]
    assert any((item.get("why_selected") for pkg in composition for item in pkg.get("products") or []))


def test_frontend_does_not_calculate_or_hardcode_packages():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    css = WORKBENCH_CSS.read_text(encoding="utf-8")
    for text in (js, html, css):
        assert "SF001" not in text
        assert "TR007" not in text
        assert "TR011" not in text
        assert "Demo Fresh Beef Bowl" not in text
        assert "monthly_cost *" not in text
        assert "products_included = [" not in text
    client = CLIENT_JS.read_text(encoding="utf-8")
    config = CONFIG_JS.read_text(encoding="utf-8")
    assert "JSON.stringify(json)" in client
    assert WORKBENCH_PATH_TOKEN in js
    assert "location.origin" in config
    assert "127.0.0.1:8000" not in js
    assert "localhost:8000" not in js
    assert "127.0.0.1:8000" not in client
    assert "localhost:8000" not in client


def test_api_failure_has_explicit_ui_state():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert "API failure" in js
    assert "response.status" in js
    assert "Network failure" in js
    assert "Retry the analysis when the service is available." in js
    assert "workbench-error" in WORKBENCH_HTML.read_text(encoding="utf-8")


def test_demo_mode_clearly_identifies_synthetic_catalog(demo_client: TestClient):
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    assert "DEMO CATALOG" in html
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly_payload()).json()
    assert body["catalog_source"] == "demo"
    boundary = body["roles"]["customer"]["scientific_boundary"]
    assert "Scientific product matching unavailable" in boundary["science_copy"] or boundary["matcher_available"] is True
    assert "modeled baseline nutrient constraints" in boundary["package_copy"].lower()
    business = body["roles"]["business"]
    assert business["commercial_dataset"]["loaded"] is False
    assert "not loaded" in business["commercial_dataset"]["status"].lower()


def test_workbench_is_browser_safe_when_api_keys_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    import app.api.main as api_main

    monkeypatch.setattr(api_main, "VALID_KEYS", {"locked-key"})
    client = TestClient(app)
    response = client.post("/api/v1/presentation/workbench", json=_dolly_payload())
    assert response.status_code == 200
    assert client.post("/api/v1/analyze", json=_dolly_payload()).status_code == 401


def test_classic_customer_route_preserved(demo_client: TestClient):
    classic = demo_client.get("/classic")
    assert classic.status_code == 200
    assert "workbench.js" in classic.text
    assert "role-selector" in classic.text
    assert "catalog-service.js" not in classic.text


def test_switch_role_function_present_without_sku_literals():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    assert re.search(r"function switchRole\s*\(", js)
    assert "currentAnalysis" in js
    assert "WagtopiaWorkbench" in js
