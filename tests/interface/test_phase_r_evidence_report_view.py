"""Phase R — read-only evidence report presentation over the Phase N payload."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.main import app

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "waggy-frontend"
HARNESS = Path(__file__).resolve().parent / "_phase_r_view_harness.mjs"
RENDER_JS = (FRONTEND / "src" / "evidence" / "render.js").read_text(encoding="utf-8")
LOAD_JS = (FRONTEND / "src" / "evidence" / "load.js").read_text(encoding="utf-8")
PAGE_JS = (FRONTEND / "src" / "evidence" / "page.js").read_text(encoding="utf-8")
PAGE_HTML = (FRONTEND / "evidence-report.html").read_text(encoding="utf-8")


def _view(op: str, payload: dict) -> dict:
    completed = subprocess.run(
        ["node", str(HARNESS), op],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        cwd=str(ROOT),
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def _record(**overrides) -> dict:
    body = {
        "observation_id": "obs-1",
        "dog_id": "dog-1",
        "observation_type": "weight_kg",
        "value": "20",
        "unit": "kg",
        "observer_role": "customer",
        "source": "USER",
        "observed_at": "2026-08-01T00:00:00Z",
        "recorded_at": "2026-08-01T01:00:00Z",
        "source_session_id": "sess-1",
        "event_id": "evt-1",
    }
    body.update(overrides)
    return body


def _report(**overrides) -> dict:
    body = {
        "dog_id": "dog-1",
        "generated_at": "2026-09-22T12:00:00Z",
        "as_of": None,
        "series": [],
    }
    body.update(overrides)
    return body


def test_normal_report_renders_multiple_series():
    weight = _record()
    coat = _record(
        observation_id="obs-coat",
        observation_type="coat_density",
        value="dense",
        unit=None,
        event_id="evt-coat",
    )
    html = _view(
        "render",
        _report(
            series=[
                {
                    "observation_type": "weight_kg",
                    "units": ["kg"],
                    "history": [weight],
                    "canonical_observation": weight,
                    "timeline": [{"observation": weight, "delta_from_previous": None}],
                },
                {
                    "observation_type": "coat_density",
                    "units": [],
                    "history": [coat],
                    "canonical_observation": coat,
                    "timeline": [{"observation": coat, "delta_from_previous": None}],
                },
            ]
        ),
    )["html"]
    assert 'data-observation-type="weight_kg"' in html
    assert 'data-observation-type="coat_density"' in html
    assert html.index("weight_kg") < html.index("coat_density")


def test_canonical_observation_is_labeled_as_policy_selection():
    chosen = _record(observation_id="obs-vet", observer_role="veterinarian", source="VETERINARIAN", value="22")
    html = _view(
        "render",
        _report(
            series=[
                {
                    "observation_type": "weight_kg",
                    "units": ["kg"],
                    "history": [_record(), chosen],
                    "canonical_observation": chosen,
                    "timeline": [],
                }
            ]
        ),
    )["html"]
    assert "Canonical observation selected by the evidence policy." in html
    assert "not a medical diagnosis" in html
    assert "not clinical validation" in html
    canonical = html.split('data-canonical="present"', 1)[1]
    assert "obs-vet" in canonical
    assert "veterinarian" in canonical


def test_provenance_fields_are_rendered():
    html = _view(
        "render",
        _report(
            series=[
                {
                    "observation_type": "weight_kg",
                    "units": ["kg"],
                    "history": [_record()],
                    "canonical_observation": _record(),
                    "timeline": [{"observation": _record(), "delta_from_previous": None}],
                }
            ]
        ),
    )["html"]
    for field in (
        "observation_id",
        "dog_id",
        "observation_type",
        "value",
        "unit",
        "observer_role",
        "source",
        "observed_at",
        "recorded_at",
        "source_session_id",
        "event_id",
    ):
        assert f'data-field="{field}"' in html
    assert "Observation time (observed_at)" in html
    assert "Recording time (recorded_at)" in html
    assert "Report generation time (generated_at)" in html
    assert "2026-08-01T00:00:00Z" in html
    assert "2026-08-01T01:00:00Z" in html
    assert "2026-09-22T12:00:00Z" in html


def test_numeric_delta_is_rendered_as_returned():
    current = _record(observation_id="obs-2", value="22.5", event_id="evt-2", observed_at="2026-09-01T00:00:00Z")
    html = _view(
        "render",
        _report(
            series=[
                {
                    "observation_type": "weight_kg",
                    "units": ["kg"],
                    "history": [_record(), current],
                    "canonical_observation": current,
                    "timeline": [
                        {"observation": _record(), "delta_from_previous": None},
                        {
                            "observation": current,
                            "delta_from_previous": {
                                "previous_observation_id": "obs-1",
                                "current_observation_id": "obs-2",
                                "previous_value": "20",
                                "current_value": "22.5",
                                "delta": 2.5,
                                "unit": "kg",
                                "observed_at_previous": "2026-08-01T00:00:00Z",
                                "observed_at_current": "2026-09-01T00:00:00Z",
                            },
                        },
                    ],
                }
            ]
        ),
    )["html"]
    assert 'data-delta-value="2.5"' in html
    assert 'data-delta-field="unit"' in html
    assert ">kg<" in html
    assert "22.5" in html


def test_categorical_series_with_null_delta_is_not_numeric():
    row = _record(
        observation_id="obs-skin",
        observation_type="skin_appearance",
        value="flaky",
        unit=None,
        event_id="evt-skin",
    )
    html = _view(
        "render",
        _report(
            series=[
                {
                    "observation_type": "skin_appearance",
                    "units": [],
                    "history": [row],
                    "canonical_observation": row,
                    "timeline": [{"observation": row, "delta_from_previous": None}],
                }
            ]
        ),
    )["html"]
    assert "No numeric delta is available." in html
    assert 'data-delta="absent"' in html
    assert "flaky" in html
    assert 'data-delta-value=' not in html


def test_null_numeric_delta_field_is_not_invented():
    row = _record(value="10", unit="lb")
    later = _record(observation_id="obs-lb", value="12", unit="kg", event_id="evt-lb")
    html = _view(
        "render",
        _report(
            series=[
                {
                    "observation_type": "weight_kg",
                    "units": ["lb", "kg"],
                    "history": [row, later],
                    "canonical_observation": later,
                    "timeline": [
                        {
                            "observation": later,
                            "delta_from_previous": {
                                "previous_observation_id": "obs-1",
                                "current_observation_id": "obs-lb",
                                "previous_value": "10",
                                "current_value": "12",
                                "delta": None,
                                "unit": None,
                                "observed_at_previous": "2026-08-01T00:00:00Z",
                                "observed_at_current": "2026-08-01T00:00:00Z",
                            },
                        }
                    ],
                }
            ]
        ),
    )["html"]
    assert "No numeric delta is available." in html
    assert 'data-delta-field="delta"' in html
    assert 'data-delta-value=' not in html


def test_empty_series_has_no_manufactured_rows():
    html = _view("render", _report(series=[]))["html"]
    assert 'data-empty="true"' in html
    assert "No evidence series were returned." in html
    assert "data-observation-type" not in html
    assert "weight_kg" not in html
    assert "No replay cutoff was supplied." in html


def test_as_of_is_a_query_parameter_and_a_displayed_stamp():
    path = _view(
        "path",
        {
            "dog_id": "dog 1",
            "observation_type": "weight_kg",
            "as_of": "2026-09-01T00:00:00Z",
            "generated_at": "2026-09-22T12:00:00Z",
            "limit": "5",
        },
    )["path"]
    assert path.startswith("/api/v1/dogs/dog%201/evidence-report?")
    assert "observation_type=weight_kg" in path
    assert "as_of=2026-09-01T00%3A00%3A00Z" in path
    assert "generated_at=2026-09-22T12%3A00%3A00Z" in path
    assert "limit=" not in path
    early = _record(observation_id="obs-early", observed_at="2026-08-01T00:00:00Z")
    late = _record(observation_id="obs-late", observed_at="2026-12-01T00:00:00Z", event_id="evt-late")
    html = _view(
        "render",
        _report(
            as_of="2026-09-01T00:00:00Z",
            series=[
                {
                    "observation_type": "weight_kg",
                    "units": ["kg"],
                    "history": [early, late],
                    "canonical_observation": early,
                    "timeline": [
                        {"observation": early, "delta_from_previous": None},
                        {"observation": late, "delta_from_previous": None},
                    ],
                }
            ],
        ),
    )["html"]
    assert 'data-as-of>2026-09-01T00:00:00Z<' in html
    assert "obs-early" in html
    assert "obs-late" in html
    assert "Replay cutoff (as_of)" in html


def test_dog_not_found_keeps_backend_error_code():
    viewed = _view(
        "http-error",
        {
            "status": 404,
            "body": {
                "error": {
                    "code": "DOG_NOT_FOUND",
                    "message": "dog missing-dog was not found",
                    "field": "dog_id",
                    "fields": ["dog_id"],
                }
            },
        },
    )
    assert viewed["code"] == "DOG_NOT_FOUND"
    assert viewed["status"] == 404
    assert viewed["field"] == "dog_id"
    html = _view("error", viewed)["html"]
    assert 'data-error-code="DOG_NOT_FOUND"' in html
    assert "dog missing-dog was not found" in html


def test_view_does_not_select_canonical_or_calculate_deltas():
    combined = "\n".join([RENDER_JS, LOAD_JS, PAGE_JS])
    for token in (
        "select_canonical",
        "selectCanonical",
        "filter_history",
        "SOURCE_PRECEDENCE",
        "parseFloat",
        "parseInt",
        "Number(",
        "toFixed",
        "2.204",
        "scientific_care",
        "package_optimizer",
        "package_search",
        "from app.",
        "app/state",
        "app/normalization",
    ):
        assert token not in combined
    assert "fetch(" not in RENDER_JS
    assert "delta -" not in combined
    assert ".filter(" not in PAGE_JS
    assert "observation_type" in PAGE_HTML
    assert 'name="as_of"' in PAGE_HTML
    assert 'name="generated_at"' in PAGE_HTML
    for forbidden in ("FormulaGraph", "resolve_breed", "scientific_care"):
        assert forbidden not in PAGE_HTML


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_evidence_report_page_is_served(client: TestClient):
    page = client.get("/evidence-report")
    assert page.status_code == 200
    assert 'id="evidence-query"' in page.text
    assert "/src/evidence/page.js" in page.text
    script = client.get("/src/evidence/render.js")
    assert script.status_code == 200
    assert "renderEvidenceReport" in script.text
    css = client.get("/src/styles/evidence-report.css")
    assert css.status_code == 200
