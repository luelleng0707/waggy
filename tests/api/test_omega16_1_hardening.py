"""Ω16.1: HTTP birthday determinism, groomer isolation, extraction paths."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.http_models import DEVELOPER_JSON_PATHS, WORKBENCH_EXAMPLE_REQUEST
from app.api.main import app
from app.api.payload_adapter import age_years_from_birthday


def _as_of(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _dolly(**overrides) -> dict:
    body = dict(WORKBENCH_EXAMPLE_REQUEST)
    body.update(overrides)
    return body


def _age(body: dict) -> float:
    profile = ((body.get("canonical") or {}).get("analyze") or {}).get("profile") or {}
    return float(profile["age_years"])


def _science(body: dict) -> dict:
    canonical = body["canonical"]
    return {
        "findings": canonical["scientific_analysis"]["findings"],
        "nutrient_targets": canonical["scientific_analysis"]["nutrient_targets"],
        "evidence": canonical["scientific_analysis"]["evidence"],
        "recommendations": canonical["product_matching"]["recommendations"],
        "package_options": canonical["package_optimization"]["package_options"],
        "search": canonical["package_optimization"]["search"],
        "analysis_signature": body["analysis_signature"],
        "age_years": _age(body),
    }


def _dig(payload: dict, path: str):
    cur: object = payload
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    return TestClient(app)


def test_http_birthday_as_of_date_same_request_twice(demo_client: TestClient):
    birthday = "2021-04-15"
    as_of_date = "2026-09-09"
    expected = age_years_from_birthday(birthday, as_of=_as_of(as_of_date))
    payload = _dolly(birthday=birthday, as_of_date=as_of_date)
    payload.pop("age_years", None)
    a = demo_client.post("/api/v1/presentation/workbench", json=payload)
    b = demo_client.post("/api/v1/presentation/workbench", json=payload)
    assert a.status_code == 200
    assert b.status_code == 200
    left, right = a.json(), b.json()
    assert _age(left) == expected
    assert _age(right) == expected
    assert _science(left) == _science(right)


def test_http_changing_as_of_date_changes_derived_age(demo_client: TestClient):
    first_date = "2026-09-09"
    second_date = "2027-09-09"
    birthday = "2021-04-15"
    first_expected = age_years_from_birthday(birthday, as_of=_as_of(first_date))
    second_expected = age_years_from_birthday(birthday, as_of=_as_of(second_date))
    assert first_expected != second_expected
    first = demo_client.post(
        "/api/v1/presentation/workbench",
        json=_dolly(birthday=birthday, as_of_date=first_date),
    )
    second = demo_client.post(
        "/api/v1/presentation/workbench",
        json=_dolly(birthday=birthday, as_of_date=second_date),
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert _age(first.json()) == first_expected
    assert _age(second.json()) == second_expected


def test_http_explicit_age_overrides_birthday_as_of(demo_client: TestClient):
    payload = _dolly(age_years=9.0, birthday="2021-04-15", as_of_date="2026-09-09")
    response = demo_client.post("/api/v1/presentation/workbench", json=payload)
    assert response.status_code == 200
    derived = age_years_from_birthday("2021-04-15", as_of=_as_of("2026-09-09"))
    actual = _age(response.json())
    assert actual == 9.0
    assert actual != derived


def test_http_invalid_as_of_date(demo_client: TestClient):
    payload = _dolly(as_of_date="not-a-date")
    response = demo_client.post("/api/v1/presentation/workbench", json=payload)
    assert response.status_code == 400
    err = response.json()["error"]
    assert err["code"] == "INVALID_INPUT"
    assert err["field"] == "as_of_date"


def test_workbench_ignores_groomer_session_state(demo_client: TestClient):
    payload = _dolly()
    first = demo_client.post("/api/v1/presentation/workbench", json=payload)
    assert first.status_code == 200
    mutate = demo_client.post(
        "/api/v1/groomer/update",
        json={
            "pet_name": payload["pet_name"],
            "pet_id": payload["pet_name"],
            "observed_conditions": ["session_only_flag_must_not_leak"],
            "notes": "hidden session must not enter workbench",
        },
    )
    assert mutate.status_code == 200
    session = demo_client.get(f"/api/v1/groomer/session/{payload['pet_name']}")
    assert "session_only_flag_must_not_leak" in (session.json().get("observed_conditions") or [])
    second = demo_client.post("/api/v1/presentation/workbench", json=payload)
    assert second.status_code == 200
    assert _science(first.json()) == _science(second.json())
    observed = first.json()["canonical"]["analyze"]["profile"].get("observed_conditions") or []
    assert "session_only_flag_must_not_leak" not in observed


def test_developer_paths_exist_on_live_workbench_response(demo_client: TestClient):
    body = demo_client.post("/api/v1/presentation/workbench", json=_dolly()).json()
    for key in (
        "health",
        "nutrition",
        "products",
        "packages",
        "scientific_evidence",
        "optimizer_provenance",
        "engine_version",
        "warehouse_version",
        "analysis_signature",
    ):
        assert _dig(body, DEVELOPER_JSON_PATHS[key]) is not None, key
    assert "packages.funnel" not in DEVELOPER_JSON_PATHS.values()
    assert DEVELOPER_JSON_PATHS["packages"] == "canonical.package_optimization.package_options"
    assert DEVELOPER_JSON_PATHS["optimizer_provenance"] == "canonical.package_optimization.search"
