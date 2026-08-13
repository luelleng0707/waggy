from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.main import app


def test_customer_root_route_serves_customer_ui():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Wagtopia" in response.text
    assert "Clinical Execution Explorer" not in response.text


def test_customer_surface_hides_developer_internals():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    assert "execution_id" not in text
    assert "formula_execution.v2" not in text
    assert "warehouse_row_status" not in text
