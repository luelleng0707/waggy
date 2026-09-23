"""Ω17 workbench: one frontend, contextual Ask Waggy, no client secrets."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = (WORKBENCH_JS).read_text(encoding="utf-8")
HTML = (WORKBENCH_HTML).read_text(encoding="utf-8")


def test_ask_waggy_is_on_the_single_workbench():
    assert "Ask Waggy why" in JS
    assert 'id="ai-explain-panel"' in HTML
    assert "/api/v1/ai/explain" in JS
    assert JS.count('"/api/v1/presentation/workbench"') >= 1


def test_ai_fetch_is_not_inside_run_analysis():
    run_start = JS.index("async function runAnalysis")
    run_end = JS.index('$("module-load-demo")')
    run_body = JS[run_start:run_end]
    assert "/api/v1/ai/explain" not in run_body
    assert "WORKBENCH_PATH" in run_body
    assert "async function askWaggy" in JS


def test_no_provider_secrets_in_frontend():
    for token in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "AIza"):
        assert token not in JS
        assert token not in HTML


def test_no_second_frontend_or_role_engines():
    assert "/api/v1/analyze/customer" not in JS
    assert "ChatGPT" not in HTML
    assert "Ask Waggy" in HTML
