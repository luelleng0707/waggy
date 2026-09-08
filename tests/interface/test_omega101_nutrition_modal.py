"""Ω10.1: Nutrition Facts modal close contract. UI only."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.main import app


ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "legacy" / "workbench.html").read_text(encoding="utf-8")
JS = (ROOT / "legacy" / "workbench.js").read_text(encoding="utf-8")
CSS = (ROOT / "legacy" / "workbench.css").read_text(encoding="utf-8")


def test_one_modal_markup_and_close_button():
    assert HTML.count('id="nutrition-modal"') == 1
    assert 'class="wb-modal-backdrop" data-close-nutrition' in HTML
    assert 'class="wb-modal-panel"' in HTML
    assert 'type="button"' in HTML
    assert 'class="wb-modal-close"' in HTML
    assert 'aria-label="Close nutrition facts"' in HTML
    assert HTML.index('id="nutrition-modal"') < HTML.index("workbench.js")


def test_selected_bundle_is_authoritative_open_state():
    assert "var selectedBundleForNutrition = null;" in JS
    assert "selectedBundleForNutrition = key;" in JS
    open_fn = JS[JS.index("function openNutritionModal") : JS.index("function renderBundleReasoning")]
    close_fn = JS[JS.index("function closeNutritionModal") : JS.index("function openNutritionModal")]
    assert "selectedBundleForNutrition = null;" in close_fn
    assert "body.innerHTML = \"\"" in close_fn or "body.innerHTML = '';" in close_fn
    assert "modal.hidden = true" in close_fn
    assert "wb-modal-open" in close_fn
    assert "renderNutritionFacts(stored.opt, key" in open_fn
    assert "selectedBundleForNutrition = key" in open_fn
    assert "wb-modal-open" in open_fn
    assert ".wb-modal-close" in open_fn


def test_close_handlers_cover_x_esc_backdrop_not_content():
    assert "event.key === \"Escape\" && selectedBundleForNutrition" in JS
    assert 'event.target.closest("[data-close-nutrition]")' in JS
    assert "closeNutritionModal()" in JS
    panel_guard = JS[JS.index("nutritionPanel") : JS.index("window.WagtopiaWorkbench")]
    assert "stopPropagation" in panel_guard
    assert 'event.target.closest("[data-close-nutrition]")' in panel_guard


def test_modal_scrolls_internally_page_does_not():
    assert "body.wb-modal-open" in CSS
    assert "overflow: hidden" in CSS
    assert "#nutrition-modal-body" in CSS
    assert "flex: 1 1 auto" in CSS


def test_customer_nutrition_uses_names_not_skus():
    facts = JS[JS.index("function renderNutritionFacts") : JS.index("function closeNutritionModal")]
    assert "currentRole === \"developer\"" in facts
    assert "productNamesLine(opt, nameOpts)" in facts
    customer = JS[JS.index("function renderOptions") : JS.index("function renderCompare")]
    assert "wb-facts-table" not in customer
    assert "View nutrition" in customer
    assert "SF002" not in HTML
    assert "TR007" not in HTML


@pytest.fixture
def demo_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("API_KEYS", raising=False)


def test_roles_still_share_bundle_ids(demo_env):
    body = TestClient(app).post(
        "/api/v1/presentation/workbench",
        json={
            "name": "Dolly",
            "breeds": ["Labrador Retriever", "Golden Retriever"],
            "birthday": "2021-04-15",
            "weight": 30,
            "observed_conditions": ["joint_stiffness", "itching"],
        },
    ).json()
    ids = []
    for role in ("customer", "groomer", "business", "developer"):
        options = (
            ((body["roles"][role].get("wellness") or {}).get("package_options"))
            or body["roles"][role].get("package_options")
            or ((body["roles"][role].get("portfolio") or {}).get("package_options"))
            or ((body["roles"][role].get("package_optimization") or {}).get("package_options"))
        )
        ids.append(
            [row["bundle_id"] for tier in ("essential", "balanced", "optimal") for row in (options or {}).get(tier) or []]
        )
    assert ids[0] and ids[0] == ids[1] == ids[2] == ids[3]
