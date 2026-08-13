from app.core.paths import clinical_root_str, resolve_clinical_root
"""Unit tests for app.inference — no production scoring wiring required."""

from app.inference.confidence import confidence_for_source
from app.inference.config import (
    DEFAULT_CATEGORY_WEIGHTS,
    DEFAULT_SCORE_WEIGHTS,
    category_weights,
    nutrient_catalog,
    score_weights,
)
from app.inference.ingredient import estimate_fractions_from_order, estimate_nutrient
from app.inference.nutrition import condition_support_score, coverage_ratio
from app.inference.risk import build_risk_modifier_ledger
from app.inference.score import package_score_weights
from app.data.runtime import bootstrap, get_platform


def test_confidence_ladder():
    assert confidence_for_source("lab_measured") == 100.0
    assert confidence_for_source("unknown") == 0.0
    assert confidence_for_source("ingredient_order") == 70.0


def test_csv_weights_match_defaults():
    bootstrap(clinical_root_str(), strict=True)
    assert category_weights() == DEFAULT_CATEGORY_WEIGHTS
    assert score_weights() == DEFAULT_SCORE_WEIGHTS
    assert package_score_weights() == DEFAULT_SCORE_WEIGHTS
    cat = nutrient_catalog()
    assert any(c["key"] == "omega_3" for c in cat)


def test_fraction_order_and_nutrient_est_disabled():
    fr = estimate_fractions_from_order(["a", "b", "c", "d", "e", "f", "g"])
    assert fr.enabled is False
    assert fr.formula_id == "ING_FRAC_ORDER_V1"
    vals = fr.value
    assert abs(sum(x["fraction"] for x in vals) - 1.0) < 1e-6
    assert vals[0]["percent"] == 35.0

    platform = get_platform()
    est = estimate_nutrient(
        [{"ingredient": "Chicken Heart", "fraction": 0.35}],
        "Taurine",
        platform.table("ingredient_nutrient_estimates"),
    )
    assert est.enabled is False
    assert est.formula_id == "NUTRIENT_EST_V1"
    assert est.value is not None
    assert abs(float(est.value) - 0.35 * 160) < 1e-6


def test_coverage_and_condition_support_gated():
    cov = coverage_ratio(800, 1000)
    assert cov.formula_id == "COVERAGE_V2_1"
    assert abs(cov.value - 0.8) < 1e-9
    support = condition_support_score([{"coverage": 0.8, "evidence_weight": 1.0, "priority": 1.0}])
    assert support.enabled is False
    assert support.formula_id == "CONDITION_SUPPORT_V1"


def test_risk_trace_ledger_does_not_invent_modifiers():
    ledger = build_risk_modifier_ledger(
        {"title": "Joint Health", "biological_risk_percent": 55, "observed_breed_prevalence_percent": 18}
    )
    assert ledger["formula_id"] == "RISK_TRACE_V1"
    assert ledger["complete"] is False
    nt = [s for s in ledger["steps"] if not s.get("traceable")]
    assert nt
