"""Ω17.1 workbench: one frontend, dog history, no client secrets."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = (WORKBENCH_JS).read_text(encoding="utf-8")
HTML = (WORKBENCH_HTML).read_text(encoding="utf-8")
CSS = (WORKBENCH_CSS).read_text(encoding="utf-8")


def test_care_history_is_on_the_single_workbench():
    assert 'id="care-history-panel"' in HTML
    assert 'id="save-dog"' in HTML
    assert "/api/v1/dogs" in JS
    assert "not diagnoses" in HTML
    assert "not scientific facts" in HTML
    assert JS.count('"/api/v1/presentation/workbench"') >= 1


def test_load_demo_does_not_persist_and_ask_waggy_uses_saved_dog_id():
    assert "setDogId(\"\")" in JS or "setDogId('')" in JS
    assert "Load Demo does not save" in HTML
    assert "dogIdFromForm()" in JS
    assert "dog_profile.name" not in JS


def test_run_analysis_still_does_not_call_explain():
    run_start = JS.index("async function runAnalysis")
    run_end = JS.index('$("module-load-demo")')
    run_body = JS[run_start:run_end]
    assert "/api/v1/ai/explain" not in run_body
    assert "WORKBENCH_PATH" in run_body
    assert run_body.count('AI_EXPLAIN_PATH') == 0


def test_no_provider_secrets_or_second_frontend():
    for token in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "AIza"):
        assert token not in JS
        assert token not in HTML
        assert token not in CSS
    assert "ChatGPT" not in HTML
    assert "/api/v1/analyze/customer" not in JS
