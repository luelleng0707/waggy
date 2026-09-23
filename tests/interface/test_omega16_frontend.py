"""Ω16 unified workbench: role-aware intake, one POST, developer contract view."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_HTML, WORKBENCH_JS, frontend_js_text
from pathlib import Path

from app.api.http_models import DEVELOPER_JSON_PATHS, WORKBENCH_EXAMPLE_REQUEST

ROOT = Path(__file__).resolve().parents[2]
JS = (WORKBENCH_JS).read_text(encoding="utf-8")
HTML = (WORKBENCH_HTML).read_text(encoding="utf-8")


def test_one_frontend_four_role_tabs():
    for role in ("customer", "groomer", "business", "developer"):
        assert f'data-role="{role}"' in HTML
        assert f'data-view="{role}"' in HTML


def test_customer_input_fields():
    assert 'id="dog-profile-fields"' in HTML
    assert 'name="primary_breed"' in HTML
    assert 'name="weight"' in HTML
    assert 'name="activity_level"' in HTML
    assert 'name="current_environment"' in HTML
    start = JS.index("function updateIntakeForRole")
    end = JS.index("function emptyState")
    assert 'dog.hidden = role === "developer"' in JS[start:end]


def test_groomer_observation_fields_are_labeled_observation():
    assert 'id="groomer-fields"' in HTML
    assert "Observations" in HTML
    assert "Not a diagnosis" in HTML
    assert 'id="groomer-observations"' in HTML
    assert "Diagnosis" not in HTML.split("groomer-fields")[1].split("business-fields")[0]


def test_business_commercial_context_separated():
    assert 'id="business-fields"' in HTML
    assert "Commercial context" in HTML
    assert "Does not change scientific findings" in HTML
    assert 'id="business-segment"' in HTML


def test_developer_tab_documents_endpoints_and_paths():
    assert "POST /api/v1/presentation/workbench" in HTML or "CANONICAL API" in HTML
    assert "/api/v1/analyze" in HTML
    assert "canonical.scientific_analysis.findings" in JS
    assert "canonical.package_optimization.search" in JS
    assert "packages.funnel" not in JS
    for path in (
        DEVELOPER_JSON_PATHS["health"],
        DEVELOPER_JSON_PATHS["nutrition"],
        DEVELOPER_JSON_PATHS["products"],
        DEVELOPER_JSON_PATHS["packages"],
        DEVELOPER_JSON_PATHS["scientific_evidence"],
        DEVELOPER_JSON_PATHS["optimizer_provenance"],
        DEVELOPER_JSON_PATHS["engine_version"],
        DEVELOPER_JSON_PATHS["analysis_signature"],
    ):
        assert path in JS


def test_role_switch_does_not_run_analysis():
    start = JS.index("function switchRole")
    end = JS.index("function emptyState")
    body = JS[start:end]
    assert "fetch(" not in body
    assert "runAnalysis" not in body


def test_one_run_analysis_posts_workbench_only():
    assert JS.count('"/api/v1/presentation/workbench"') >= 1
    run_start = JS.index("async function runAnalysis")
    run_end = JS.index('$("module-load-demo")')
    run_body = JS[run_start:run_end]
    assert "runWorkbenchAnalysis" in run_body
    assert "fetch(" not in run_body
    assert "/api/v1/analyze" not in run_body


def test_name_is_not_substituted_with_dolly():
    assert '|| "Dolly"' not in JS
    read = JS[JS.index("function readForm") : JS.index("function roleContext")]
    assert "Dolly" not in read


def test_errors_render_typed_payload():
    assert "function formatApiError" in JS
    assert "parsed.error.message" in JS


def test_developer_shows_live_response_and_copyable_example():
    src = frontend_js_text()
    assert "Live response" in JS
    assert "workbench-example-json" in JS
    assert WORKBENCH_EXAMPLE_REQUEST["birthday"] in src
    assert WORKBENCH_EXAMPLE_REQUEST["as_of_date"] in src
    assert "as_of_date" in src
    assert "copy-workbench-example" in JS


def test_no_four_role_analysis_endpoints_in_frontend():
    assert "/api/v1/analyze/customer" not in JS
    assert "/api/v1/analyze/groomer" not in JS
