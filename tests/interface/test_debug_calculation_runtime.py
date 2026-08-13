from __future__ import annotations

from fastapi.testclient import TestClient
from pathlib import Path
import pytest

from app.api.main import app
from app.debug.clinical_execution_debug import get_preset_body


@pytest.fixture
def debug_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("PPIE_DEBUG", "true")
    return TestClient(app)


def test_debug_calculation_route_registered_in_openapi(debug_client: TestClient):
    openapi = debug_client.get("/openapi.json")
    assert openapi.status_code == 200
    paths = openapi.json().get("paths", {})
    assert "/debug/calculation" in paths


def test_debug_calculation_route_returns_html(debug_client: TestClient):
    response = debug_client.get("/debug/calculation")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Clinical Execution Explorer" in response.text


def test_debug_calculation_route_with_query_returns_html(debug_client: TestClient):
    response = debug_client.get("/debug/calculation?debug=1")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Clinical Execution Explorer" in response.text


def test_debug_page_data_contract_emits_runtime_trace(debug_client: TestClient):
    payload = get_preset_body("mixed_breed")
    response = debug_client.post(
        "/api/v1/ppie/validation-console?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc.get("schema")
    assert doc.get("profile_inspector")
    assert doc.get("formula_executions")
    assert len(doc["formula_executions"]) > 0
    assert doc.get("runtime_stage_flow")

    formula_ids = [fx.get("formula_id") for fx in doc["formula_executions"] if fx.get("formula_id")]
    assert formula_ids
    assert len(set(formula_ids)) > 1
    assert "PACKAGE_OPTIMIZER_V2_1" in set(formula_ids)
    assert any(fid in set(formula_ids) for fid in ("RISK_V2_1", "NUTRIENT_TARGET_V2_1", "PRODUCT_MATCH_V2_1"))

    first = doc["formula_executions"][0]
    assert "inputs" in first
    assert "outputs" in first
    assert "lookups" in first
    assert "timing" in first
    assert "formula_expression" in first
    assert "code" in first
    assert "dependencies" in first

    stage = doc["runtime_stage_flow"][0]
    assert "input" in stage
    assert "process" in stage
    assert "output" in stage

    assert "numerical_provenance" in doc
    assert "publication_risk" in doc
    assert "replay" in doc
    assert "sensitivity" in doc
    assert all("status" in fx.get("replay", {"status": "NOT_AVAILABLE"}) for fx in doc["formula_executions"])

    for fx in doc["formula_executions"]:
        assert fx.get("execution_id")
        loc = fx.get("source_location") or {}
        assert "status" in loc
        if loc.get("status") == "SOURCE_LOCATED":
            src = Path("c:/Users/Admin/Downloads/waggy") / str(loc.get("file"))
            assert src.exists()
            line_start = int(loc.get("line_start"))
            line_end = int(loc.get("line_end"))
            assert line_start > 0
            assert line_end >= line_start
        expr = str(fx.get("formula_expression") or "")
        if expr == "FORMULA DOCUMENTATION MISSING":
            assert fx.get("documentation_status") == "NOT_DOCUMENTED"

        for lu in fx.get("lookups") or []:
            if lu.get("csv_row") in (None, ""):
                assert lu.get("warehouse_row_status") == "NOT_AVAILABLE"
            else:
                assert lu.get("warehouse_row_status") == "AVAILABLE"

        replay = fx.get("replay") or {}
        assert replay.get("status") in {"NOT_IMPLEMENTED", "MATCH", "MISMATCH", "SKIP"}
        sens = fx.get("sensitivity") or {}
        assert sens.get("status") in {"NOT_IMPLEMENTED", "AVAILABLE", "INSUFFICIENT_TRACE"}


def test_execution_record_endpoint_returns_cached_record(debug_client: TestClient):
    payload = get_preset_body("mixed_breed")
    response = debug_client.post(
        "/api/v1/ppie/validation-console?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert response.status_code == 200
    doc = response.json()
    execution_id = next(
        (fx.get("execution_id") for fx in doc.get("formula_executions") or [] if isinstance(fx, dict) and fx.get("execution_id")),
        None,
    )
    assert execution_id
    detail = debug_client.get(
        f"/api/v1/ppie/validation-console/execution/{execution_id}?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
    )
    assert detail.status_code == 200
    payload = detail.json()
    assert payload.get("schema") == "execution_record.v1"
    assert (payload.get("execution") or {}).get("execution_id") == execution_id


def test_execution_trace_structure_deterministic(debug_client: TestClient):
    payload = get_preset_body("mixed_breed")
    a = debug_client.post(
        "/api/v1/ppie/validation-console?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    b = debug_client.post(
        "/api/v1/ppie/validation-console?debug=1",
        headers={"x-api-key": "wagtopia-demo-key"},
        json=payload,
    )
    assert a.status_code == 200
    assert b.status_code == 200
    left_ids = [x.get("execution_id") for x in (a.json().get("formula_executions") or []) if isinstance(x, dict)]
    right_ids = [x.get("execution_id") for x in (b.json().get("formula_executions") or []) if isinstance(x, dict)]
    assert left_ids == right_ids
