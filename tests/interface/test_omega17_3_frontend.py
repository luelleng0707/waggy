"""Ω17.3 workbench displays system explanation facts. Chat still does not recompute."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = (WORKBENCH_JS).read_text(encoding="utf-8")
HTML = (WORKBENCH_HTML).read_text(encoding="utf-8")


def test_recompute_renders_summary_facts_and_chat_consumes_contract():
    assert 'id="recalculation-facts"' in HTML
    assert "/analyses/compare" in HTML
    assert "payload.explanation" in JS
    assert "summary_facts" in JS
    assert "lastRecalculation" in JS
    ask_start = JS.index("async function askWaggy")
    ask_end = JS.index("function bindToggles")
    ask = JS[ask_start:ask_end]
    assert "recalculation" in ask
    assert "/recompute" not in ask
    assert "generate_reproducible_report" not in ask
