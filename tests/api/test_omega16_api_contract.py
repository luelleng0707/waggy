"""Ω16 canonical workbench API contract: fail-closed input + typed errors."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.http_models import DEVELOPER_JSON_PATHS, HTTP_API_VERSION, WORKBENCH_EXAMPLE_REQUEST
from app.api.main import app
from app.api.payload_adapter import (
    WorkbenchInputError,
    age_years_from_birthday,
    profile_from_analyze_body,
    profile_from_workbench_body,
)


def _dolly() -> dict:
    return dict(WORKBENCH_EXAMPLE_REQUEST)


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    return TestClient(app)


def test_valid_workbench_request(demo_client: TestClient):
    response = demo_client.post("/api/v1/presentation/workbench", json=_dolly())
    assert response.status_code == 200
    body = response.json()
    assert body["schema"] == "workbench_presentation.v1"
    assert body["api_version"] == HTTP_API_VERSION
    assert body["engine_version"]
    assert body["engine_version"] != body["api_version"]
    assert "warehouse_version" in body
    assert body["analysis_signature"]
    assert body["canonical"]["schema"] == "canonical_analysis.v1"
    assert set(body["roles"]) == {"customer", "groomer", "business", "developer"}
    science = body["canonical"]["scientific_analysis"]
    assert "findings" in science
    assert "nutrient_targets" in science
    assert "evidence" in science
    assert "package_options" in body["canonical"]["package_optimization"]
    assert "search" in body["canonical"]["package_optimization"]
    assert "recommendations" in body["canonical"]["product_matching"]
    assert body["canonical"]["analyze"]["version"] == body["engine_version"]
    assert "profile" in body["canonical"]["analyze"]
    assert "debug" not in body["canonical"]["analyze"]
    assert "packageDetails" not in body["canonical"]["analyze"]
    assert "wellnessPackages" not in body["canonical"]["analyze"]


def test_example_request_matches_runtime(demo_client: TestClient):
    response = demo_client.post("/api/v1/presentation/workbench", json=WORKBENCH_EXAMPLE_REQUEST)
    assert response.status_code == 200


def _error(response) -> dict:
    assert response.status_code == 400
    payload = response.json()
    assert "error" in payload
    assert payload["error"]["code"]
    assert payload["error"]["message"]
    return payload["error"]


def test_missing_age_and_birthday(demo_client: TestClient):
    body = _dolly()
    body.pop("birthday")
    body.pop("age_years", None)
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "MISSING_REQUIRED_INPUT"
    assert err["field"] == "age_years"


def test_missing_weight(demo_client: TestClient):
    body = _dolly()
    body.pop("weight")
    body.pop("weight_kg", None)
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "MISSING_REQUIRED_INPUT"
    assert err["field"] == "weight"


def test_missing_breed(demo_client: TestClient):
    body = _dolly()
    body.pop("primary_breed")
    body["breeds"] = []
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "MISSING_REQUIRED_INPUT"
    assert err["field"] == "primary_breed"


def test_invalid_weight(demo_client: TestClient):
    body = _dolly()
    body["weight"] = 0
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "INVALID_INPUT"
    assert err["field"] == "weight"


def test_invalid_age(demo_client: TestClient):
    body = _dolly()
    body.pop("birthday")
    body["age_years"] = -1
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "INVALID_INPUT"


def test_conflicting_weight_fields(demo_client: TestClient):
    body = _dolly()
    body["weight"] = 20
    body["weight_kg"] = 30
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "INVALID_INPUT"
    assert "weight" in err["fields"]
    assert "weight_kg" in err["fields"]


def test_matching_weight_aliases(demo_client: TestClient):
    body = _dolly()
    body["weight"] = 30
    body["weight_kg"] = 30
    assert demo_client.post("/api/v1/presentation/workbench", json=body).status_code == 200


def test_missing_activity(demo_client: TestClient):
    body = _dolly()
    body.pop("activity_level")
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "MISSING_REQUIRED_INPUT"
    assert err["field"] == "activity_level"


def test_empty_activity_is_missing(demo_client: TestClient):
    body = _dolly()
    body["activity_level"] = "   "
    err = _error(demo_client.post("/api/v1/presentation/workbench", json=body))
    assert err["code"] == "MISSING_REQUIRED_INPUT"


def test_empty_name_is_allowed(demo_client: TestClient):
    body = _dolly()
    body["name"] = ""
    body["pet_name"] = ""
    response = demo_client.post("/api/v1/presentation/workbench", json=body)
    assert response.status_code == 200


def test_not_available_is_http_200(demo_client: TestClient):
    response = demo_client.post("/api/v1/presentation/workbench", json=_dolly())
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["canonical"]["scientific_analysis"]["evidence"], list)
    assert isinstance(body["canonical"]["product_matching"]["recommendations"], list)
    # Empty matcher / missing warehouse slice is a 200 structured result, not HTTP 500.
    assert "error" not in body


def test_workbench_does_not_default_age_or_weight():
    with pytest.raises(WorkbenchInputError) as missing_age:
        profile_from_workbench_body(
            {
                "primary_breed": "Labrador Retriever",
                "weight": 20,
                "activity_level": "High",
                "current_environment": "Temperate Indoor",
            }
        )
    assert missing_age.value.error.code.value == "MISSING_REQUIRED_INPUT"
    with pytest.raises(WorkbenchInputError) as missing_weight:
        profile_from_workbench_body(
            {
                "primary_breed": "Labrador Retriever",
                "age_years": 4,
                "activity_level": "High",
                "current_environment": "Temperate Indoor",
            }
        )
    assert missing_weight.value.error.code.value == "MISSING_REQUIRED_INPUT"


def test_legacy_analyze_adapter_still_defaults():
    profile = profile_from_analyze_body({"breeds": ["Labrador Retriever"]})
    assert profile.age_years == 5.0
    assert profile.weight_kg == 20.0
    assert profile.activity_level == "Moderate"
    assert profile.current_environment == "Temperate Indoor"
    assert profile.name == "Pet"


def test_as_of_date_is_deterministic():
    age = age_years_from_birthday(
        "2020-01-01",
        as_of=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    assert age == 4.0


def test_developer_paths_exist_on_response(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly()).json()
    assert _dig(body, DEVELOPER_JSON_PATHS["health"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["nutrition"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["products"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["packages"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["optimizer_provenance"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["scientific_evidence"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["engine_version"])
    assert _dig(body, DEVELOPER_JSON_PATHS["warehouse_version"]) is not None
    assert _dig(body, DEVELOPER_JSON_PATHS["analysis_signature"])
    assert "packages.funnel" not in DEVELOPER_JSON_PATHS.values()


def test_canonical_response_shape_and_provenance(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly()).json()
    opt = body["canonical"]["package_optimization"]
    assert opt["algorithm"] == "PACKAGE_OPTIMIZER_V2_1"
    assert opt["search"]
    assert body["canonical"]["system"]["ai"]["llm_used"] is False
    assert body["analysis_signature"] == body["canonical"]["analysis_id"]


def test_identical_inputs_same_science(demo_client: TestClient):
    a = demo_client.post("/api/v1/presentation/workbench", json=_dolly()).json()
    b = demo_client.post("/api/v1/presentation/workbench", json=_dolly()).json()
    assert a["canonical"]["scientific_analysis"]["findings"] == b["canonical"]["scientific_analysis"]["findings"]
    assert (
        a["canonical"]["scientific_analysis"]["nutrient_targets"]
        == b["canonical"]["scientific_analysis"]["nutrient_targets"]
    )
    assert a["canonical"]["product_matching"]["recommendations"] == b["canonical"]["product_matching"]["recommendations"]
    assert (
        a["canonical"]["package_optimization"]["package_options"]
        == b["canonical"]["package_optimization"]["package_options"]
    )
    assert a["analysis_signature"] == b["analysis_signature"]


def test_raw_analyze_compatibility_preserved(demo_client: TestClient):
    response = demo_client.post("/api/v1/analyze", json=_dolly())
    assert response.status_code == 200
    body = response.json()
    assert "healthInsights" in body
    assert "nutritionalTargets" in body
    assert "productRecommendations" in body
    assert "wellnessPackages" in body
    assert "roles" not in body
    assert body.get("version")
    assert "schema" not in body or body.get("schema") != "workbench_presentation.v1"


def _dig(payload: dict, path: str):
    cur: object = payload
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur
