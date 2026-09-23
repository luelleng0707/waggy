"""Phase S — one persisted-dog history link to the evidence report page."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.interface.frontend_paths import CLIENT_JS, WORKBENCH_HTML, WORKBENCH_JS

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).resolve().parent / "_phase_s_link_harness.mjs"
JS = WORKBENCH_JS.read_text(encoding="utf-8")
HTML = WORKBENCH_HTML.read_text(encoding="utf-8")
CLIENT = CLIENT_JS.read_text(encoding="utf-8")
EVIDENCE_PAGE = (ROOT / "waggy-frontend" / "evidence-report.html").read_text(encoding="utf-8")


def _history_behavior() -> dict:
    completed = subprocess.run(
        ["node", str(HARNESS)],
        text=True,
        capture_output=True,
        check=False,
        cwd=str(ROOT),
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def test_history_panel_builds_one_encoded_evidence_report_link():
    viewed = _history_behavior()
    assert viewed["plain"] == "/evidence-report?dog_id=dog-123"
    assert viewed["encoded"] == "/evidence-report?dog_id=dog+123%26id"
    assert viewed["persisted"]["dataDogId"] == "dog-123"
    assert viewed["persisted"]["links"] == [
        {
            "id": "care-history-evidence-link",
            "href": "/evidence-report?dog_id=dog-123",
            "text": "Evidence report",
        }
    ]
    assert viewed["persisted"]["events"] == 1
    assert viewed["renderedAgain"]["links"] == viewed["persisted"]["links"]
    assert viewed["cleared"]["links"] == []
    assert viewed["cleared"]["dataDogId"] == ""


def test_link_is_navigation_only_and_absent_without_a_persisted_dog():
    history = JS[JS.index("function evidenceReportHref") : JS.index("async function loadPersistedDog")]
    assert history.count("/evidence-report?") == 1
    assert history.count('textContent = "Evidence report"') == 1
    assert "fetch(" not in history
    assert "/api/v1/dogs/" not in history
    assert "if (dogId)" in history
    demo = JS[JS.index("function loadDemo") : JS.index("async function runAnalysis")]
    assert 'renderCareHistory("", [])' in demo
    assert HTML.count("/evidence-report") == 0
    assert "evidence-report" not in CLIENT
    assert "./evidence/" not in JS
    assert "evidence-report?dog_id" not in EVIDENCE_PAGE
