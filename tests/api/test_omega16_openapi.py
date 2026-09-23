"""Ω16 OpenAPI describes the two HTTP contracts separately."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.http_models import DEVELOPER_JSON_PATHS, HTTP_API_VERSION
from app.api.main import app
from app.agent.version import ALGORITHM_VERSION


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_openapi_separates_analyze_and_workbench(client: TestClient):
    spec = client.get("/openapi.json").json()
    assert spec["info"]["version"] == HTTP_API_VERSION
    assert spec["info"]["version"] != ALGORITHM_VERSION
    paths = spec["paths"]
    assert "/api/v1/analyze" in paths
    assert "/api/v1/presentation/workbench" in paths
    analyze = paths["/api/v1/analyze"]["post"]
    workbench = paths["/api/v1/presentation/workbench"]["post"]
    assert analyze["requestBody"]["content"]["application/json"]["schema"]
    assert workbench["requestBody"]["content"]["application/json"]["schema"]
    analyze_ref = str(analyze.get("responses", {}).get("200", {}))
    workbench_ref = str(workbench.get("responses", {}).get("200", {}))
    assert analyze_ref != workbench_ref
    assert "400" in workbench["responses"]
    description = spec["info"].get("description") or ""
    assert "/api/v1/analyze" in description
    assert "workbench" in description.lower()


def test_openapi_workbench_error_schema(client: TestClient):
    spec = client.get("/openapi.json").json()
    workbench = spec["paths"]["/api/v1/presentation/workbench"]["post"]
    err = workbench["responses"]["400"]
    assert "ApiErrorResponse" in str(err) or "error" in str(err).lower()


def test_openapi_documents_request_fields(client: TestClient):
    spec = client.get("/openapi.json").json()
    schemas = spec.get("components", {}).get("schemas", {})
    assert "WorkbenchRequest" in schemas
    assert "AnalyzeRequest" in schemas
    workbench_props = schemas["WorkbenchRequest"]["properties"]
    assert "weight" in workbench_props
    assert "weight_kg" in workbench_props
    assert "as_of_date" in workbench_props
    assert "role_context" in workbench_props
    analyze_props = schemas["AnalyzeRequest"]["properties"]
    assert "weight" in analyze_props
    assert DEVELOPER_JSON_PATHS["packages"] == "canonical.package_optimization.package_options"
    assert DEVELOPER_JSON_PATHS["optimizer_provenance"] == "canonical.package_optimization.search"
