"""Ω17.2 workbench: preference recompute is not an AI recommender."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_HTML, WORKBENCH_JS

JS = WORKBENCH_JS.read_text(encoding="utf-8")
HTML = WORKBENCH_HTML.read_text(encoding="utf-8")


def test_recompute_control_exists_and_chat_does_not_select_packages():
    assert 'id="recompute-preferences"' in HTML
    assert "/api/v1/dogs/" in JS
    assert "/recompute" in JS
    assert "recomputeWithPreferences" in JS
    ask_start = JS.index("async function askWaggy")
    ask_end = JS.index("function bindToggles")
    ask = JS[ask_start:ask_end]
    assert "/recompute" not in ask
    assert "generate_reproducible_report" not in ask
    run_start = JS.index("async function runAnalysis")
    run_end = JS.index('$("module-load-demo")')
    run_body = JS[run_start:run_end]
    assert "/api/v1/ai/explain" not in run_body
    assert "runWorkbenchAnalysis" in run_body
