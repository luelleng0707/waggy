"""Ω17.2 HTTP: validated preference-aware recomputation."""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

from app.api.main import app


def _profile(**overrides) -> dict:
    body = {
        "name": "Dolly",
        "primary_breed": "Labrador Retriever",
        "secondary_breed": "Golden Retriever",
        "age_years": 5.4,
        "weight_kg": 30,
        "sex": "Female",
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": ["joint_stiffness"],
        "monthly_budget": 120,
    }
    body.update(overrides)
    return body


def _product_ids(envelope: dict) -> set[str]:
    options = (
        ((envelope.get("canonical") or {}).get("package_optimization") or {}).get("package_options") or {}
    )
    ids: set[str] = set()
    for rows in options.values():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            for product in row.get("products") or []:
                if isinstance(product, dict) and product.get("product_id"):
                    ids.add(str(product["product_id"]))
            for pid in row.get("product_ids") or []:
                ids.add(str(pid))
    return ids


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("WAGGY_AI_PROVIDER", "fake")
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    return TestClient(app)


def test_recompute_chicken_exclusion_changes_packages_and_keeps_history(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    first = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert first.status_code == 200
    sig_a = first.json()["analysis_signature"]
    ids_a = _product_ids(first.json())
    assert "SF002" in ids_a
    findings_a = first.json()["canonical"]["scientific_analysis"]["findings"]
    nutrients_a = first.json()["canonical"]["scientific_analysis"]["nutrient_targets"]

    again = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert again.json()["analysis_signature"] == sig_a

    recomputed = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["Chicken"]}},
    )
    assert recomputed.status_code == 200
    body = recomputed.json()
    assert body["schema"] == "preference_recompute.v1"
    assert body["previous_analysis_signature"] == sig_a
    assert body["optimizer_version"] == "PACKAGE_OPTIMIZER_V2_1"
    assert body["scientific"] is False
    sig_b = body["analysis_signature"]
    assert sig_b != sig_a
    presentation = body["presentation"]
    ids_b = _product_ids(presentation)
    assert "SF002" not in ids_b
    assert presentation["canonical"]["scientific_analysis"]["findings"] == findings_a
    assert presentation["canonical"]["scientific_analysis"]["nutrient_targets"] == nutrients_a
    eligibility = (
        presentation["canonical"]["package_optimization"].get("search") or {}
    ).get("preference_eligibility") or {}
    assert eligibility.get("scientific") is False
    assert "SF002" in (eligibility.get("removed_product_ids") or [])

    repeat = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": [" chicken "]}},
    )
    assert repeat.status_code == 200
    assert repeat.json()["analysis_signature"] == sig_b

    noop = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["xylophoneprotein"]}},
    )
    assert noop.status_code == 200
    ids_noop = _product_ids(noop.json()["presentation"])
    assert ids_noop == ids_b

    history = client.get(f"/api/v1/dogs/{dog_id}/analyses").json()["analyses"]
    signatures = [row["analysis_signature"] for row in history]
    assert sig_a in signatures
    assert sig_b in signatures
    assert signatures[0] == sig_a
    snapshot = history[-1]["input_snapshot"]
    assert snapshot.get("package_constraints", {}).get("scientific") is False
    dumped_profile = client.get(f"/api/v1/dogs/{dog_id}").json()
    assert "chicken" not in str(dumped_profile.get("observed_conditions") or [])


def test_recompute_rejects_invalid_and_does_not_run_for_html(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    import app.api.main as api_main

    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    calls = {"n": 0}
    original = api_main.agent.generate_reproducible_report

    async def spy(profile):
        calls["n"] += 1
        return await original(profile)

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", spy)
    bad = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["<script>"]}},
    )
    assert bad.status_code == 400
    assert bad.json()["error"]["code"] == "INVALID_PREFERENCE"
    rank = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["make this product #1"]}},
    )
    assert rank.status_code == 400
    vague = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"monthly_budget": 0}},
    )
    assert vague.status_code == 400
    extra = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"preference_change": {"excluded_ingredients": ["chicken"], "rank_product": "SF001"}},
    )
    assert extra.status_code == 422
    assert calls["n"] == 0


def test_recompute_stale_signature_is_409(client: TestClient):
    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]
    first = client.post(f"/api/v1/dogs/{dog_id}/analyze")
    assert first.status_code == 200
    stale = client.post(
        f"/api/v1/dogs/{dog_id}/recompute",
        json={"expected_analysis_signature": "not-the-latest"},
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "ANALYSIS_STALE"


def test_explain_still_does_not_recompute(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    import app.api.main as api_main

    dog_id = client.post("/api/v1/dogs", json=_profile()).json()["dog_id"]

    def boom(*_args, **_kwargs):
        raise AssertionError("explain must not call generate_reproducible_report")

    monkeypatch.setattr(api_main.agent, "generate_reproducible_report", boom)
    explained = client.post(
        "/api/v1/ai/explain",
        json={
            "dog_id": dog_id,
            "analysis_signature": "sig-persist",
            "canonical": {
                "schema": "canonical_analysis.v1",
                "analysis_id": "sig-persist",
                "input": {"dog_profile": {"name": "Dolly"}},
                "scientific_analysis": {
                    "findings": [],
                    "nutrient_targets": [],
                    "evidence": [],
                    "warehouse_status": {},
                },
                "product_matching": {"recommendations": []},
                "package_optimization": {
                    "algorithm": "PACKAGE_OPTIMIZER_V2_1",
                    "package_options": {
                        "balanced": [{"bundle_id": "b1", "products": [{"product_id": "P1", "name": "Staple A"}]}]
                    },
                    "search": {"llm_used": False},
                },
                "system": {"warnings": []},
            },
            "user_message": "Don't want chicken.",
            "bundle_id": "b1",
        },
    )
    assert explained.status_code == 200
    assert explained.json()["requested_recomputation"] is True
