"""Phase I — workbench can represent explicit UNKNOWN without collapsing Ω12."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.http_models import WORKBENCH_EXAMPLE_REQUEST
from app.api.main import app
from app.api.payload_adapter import (
    WorkbenchInputError,
    profile_from_analyze_body,
    profile_from_workbench_body,
    workbench_breed_field,
)
from app.contracts.agent.adapters import engine_profile_from_canonical
from app.contracts.agent.enums import InputState
from app.contracts.agent.input import CanonicalDogInput, provided, unknown
from app.normalization.enums import MappingStatus
from app.normalization.resolver import resolve_breed


def _workbench(**overrides) -> dict:
    body = dict(WORKBENCH_EXAMPLE_REQUEST)
    body.update(overrides)
    return body


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)
    monkeypatch.delenv("PPIE_DEBUG", raising=False)
    return TestClient(app)


def test_explicit_unknown_is_input_state_unknown_with_no_breed_string():
    field = workbench_breed_field({"breed_input_state": "UNKNOWN"})
    assert field.state == InputState.UNKNOWN
    assert field.value is None
    canonical = CanonicalDogInput(primary_breed=unknown())
    assert canonical.primary_breed.state == InputState.UNKNOWN
    assert canonical.primary_breed.value is None


def test_unknown_is_not_omega12_unresolved():
    field = workbench_breed_field({"breed_input_state": "UNKNOWN"})
    omega = resolve_breed("Corgi")
    assert field.state == InputState.UNKNOWN
    assert field.state != MappingStatus.UNRESOLVED
    assert omega.status == MappingStatus.UNRESOLVED
    assert omega.status != InputState.UNKNOWN


def test_unknown_is_not_omega12_ambiguous():
    field = workbench_breed_field({"breed_input_state": "UNKNOWN"})
    omega = resolve_breed("Retriever")
    assert field.state != MappingStatus.AMBIGUOUS
    assert omega.status == MappingStatus.AMBIGUOUS
    assert omega.status != InputState.UNKNOWN


def test_known_labrador_workbench_path_unchanged():
    profile = profile_from_workbench_body(_workbench(age_years=5.4))
    assert profile.primary_breed == "Labrador Retriever"
    assert profile.secondary_breed == "Golden Retriever"
    assert resolve_breed("Labrador Retriever").status == MappingStatus.RESOLVED


def test_ambiguous_retriever_omega12_unchanged():
    assert resolve_breed("Retriever").status == MappingStatus.AMBIGUOUS


def test_unresolved_corgi_omega12_unchanged():
    assert resolve_breed("Corgi").status == MappingStatus.UNRESOLVED


def test_blank_string_remains_omega12_unresolved_not_workbench_unknown():
    assert resolve_breed("").status == MappingStatus.UNRESOLVED
    with pytest.raises(WorkbenchInputError) as missing:
        workbench_breed_field({"primary_breed": ""})
    assert missing.value.error.code.value == "MISSING_REQUIRED_INPUT"
    assert missing.value.field == "primary_breed"
    with pytest.raises(WorkbenchInputError) as omitted:
        workbench_breed_field({})
    assert omitted.value.error.code.value == "MISSING_REQUIRED_INPUT"
    field = workbench_breed_field({"breed_input_state": "UNKNOWN"})
    assert field.state == InputState.UNKNOWN
    assert field.state != MappingStatus.UNRESOLVED


def test_unknown_cannot_carry_a_breed_string():
    with pytest.raises(WorkbenchInputError) as exc:
        workbench_breed_field(
            {"breed_input_state": "UNKNOWN", "primary_breed": "Labrador Retriever"}
        )
    assert exc.value.error.code.value == "INVALID_INPUT"
    assert "cannot carry a breed string" in exc.value.error.message


def test_unknown_does_not_fabricate_a_breed():
    field = workbench_breed_field({"breed_input_state": "UNKNOWN"})
    assert field.value is None
    with pytest.raises(WorkbenchInputError) as exc:
        profile_from_workbench_body(
            _workbench(
                breed_input_state="UNKNOWN",
                primary_breed=None,
                secondary_breed=None,
                breeds=[],
            )
        )
    assert exc.value.error.code.value == "INVALID_INPUT"
    assert exc.value.field == "breed_input_state"
    assert "UNKNOWN" in exc.value.error.message
    with pytest.raises(ValueError, match="UNKNOWN"):
        engine_profile_from_canonical(
            CanonicalDogInput(
                name=provided("Scout"),
                primary_breed=unknown(),
                age_years=provided(2.0),
                weight_kg=provided(12.0),
                environment=provided("Temperate Indoor"),
                activity_level=provided("Moderate"),
            )
        )


def test_mixed_lab_x_golden_omega12_unchanged():
    result = resolve_breed("Lab x Golden")
    assert result.status == MappingStatus.MIXED
    assert result.status != InputState.UNKNOWN


def test_workbench_http_unknown_fails_closed_without_analysis(demo_client: TestClient):
    body = _workbench(
        breed_input_state="UNKNOWN",
        primary_breed=None,
        secondary_breed=None,
        breeds=[],
        age_years=4.0,
    )
    response = demo_client.post("/api/v1/presentation/workbench", json=body)
    assert response.status_code == 400
    err = response.json()["error"]
    assert err["code"] == "INVALID_INPUT"
    assert err["field"] == "breed_input_state"
    assert "UNKNOWN" in err["message"]
    assert "UNRESOLVED" not in err["message"]
    assert "canonical" not in response.json()


def test_workbench_http_known_breed_still_runs(demo_client: TestClient):
    response = demo_client.post("/api/v1/presentation/workbench", json=_workbench())
    assert response.status_code == 200
    assert response.json()["canonical"]["schema"] == "canonical_analysis.v1"


def test_analyze_adapter_still_requires_a_breed_string():
    with pytest.raises(ValueError, match="primary_breed"):
        profile_from_analyze_body({"breed_input_state": "UNKNOWN"})


def test_omega12_status_is_rejected_as_workbench_breed_input_state():
    with pytest.raises(WorkbenchInputError) as exc:
        workbench_breed_field({"breed_input_state": "UNRESOLVED", "primary_breed": "Corgi"})
    assert exc.value.error.code.value == "INVALID_INPUT"
    assert exc.value.field == "breed_input_state"
