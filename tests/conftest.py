from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_legacy = _ROOT / "legacy"
if _legacy.is_dir() and str(_legacy) not in sys.path:
    sys.path.insert(0, str(_legacy))

# These tests assert the historical DataPlatform CSV projection (breeds table,
# warehouse-backed healthInsights). The current demo path uses WAGTOPIA_DEMO_MODE
# and PACKAGE_OPTIMIZER_V2_1; warehouse/current clinical CSVs are empty.
_REQUIRES_CLINICAL_CSV_PROJECTION = frozenset(
    {
        "tests/test_agent_pipeline.py::test_agent_pipeline_runs",
        "tests/test_agent_pipeline.py::test_frontend_contract_numeric_pricing",
        "tests/test_agent_pipeline.py::test_no_legacy_mock_product_ids",
        "tests/test_agent_pipeline.py::test_mixed_breed_additive_union",
        "tests/test_clinical_assessment.py::test_health_priorities_are_plain_language",
        "tests/test_clinical_report.py::test_biological_profile_from_csv",
        "tests/test_clinical_report.py::test_evidence_placeholder_when_no_url",
        "tests/test_engine_trace.py::test_engine_trace_sections",
        "tests/test_formula_graph.py::test_assessment_agent_returns_typed_result",
        "tests/test_formula_graph.py::test_engine_delegates_to_formula_graph",
        "tests/test_inference_layer.py::test_fraction_order_and_nutrient_est_disabled",
        "tests/test_inference_parity.py::test_analyze_shape_stable",
        "tests/test_inference_parity.py::test_snapshot_fingerprint_stable",
        "tests/test_phase6_authoring.py::test_evidence_builder_staging_only",
        "tests/test_science_graph.py::test_knowledge_graph_builds",
        "tests/test_science_graph.py::test_graph_repository_condition",
        "tests/test_science_graph.py::test_why_reverse_lookup",
        "tests/test_science_graph.py::test_evidence_objects",
        "tests/test_science_graph.py::test_coverage_and_audit",
        "tests/test_science_graph.py::test_analyze_includes_science_additive",
        "tests/test_ui_templates.py::test_home_intro_content",
        "tests/test_ui_templates.py::test_journey_template_renders",
        "tests/test_ui_templates.py::test_wellness_component_templates_render",
        "tests/test_validation_console.py::test_analyze_debug_observatory",
        "tests/test_validation_console.py::test_validation_console_v5_schema",
        "tests/test_validation_console.py::test_risk_ledger_uses_observatory",
        "tests/test_validation_console_live.py::test_repository_browser_read_only",
        "tests/test_warehouse_parity.py::test_formula_tables_load",
        "tests/test_warehouse_parity.py::test_scientific_entities",
        "tests/test_warehouse_parity.py::test_repository_entity_api",
    }
)


def _clinical_csv_projection_ready() -> bool:
    current = _ROOT / "warehouse" / "current" / "product_portfolio"
    # Historical DataPlatform tests require warehouse/current clinical CSVs.
    # Intern biology recovery populates warehouse/biology instead and must not
    # unskip those obsolete projection tests.
    return current.is_dir() and any(current.glob("*.csv"))


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "requires_clinical_csv_projection: needs populated DataPlatform breed tables",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if _clinical_csv_projection_ready():
        return
    skip = pytest.mark.skip(
        reason=(
            "DataPlatform clinical CSV projection is empty "
            "(warehouse/current not loaded; see docs/WAGGY_SYSTEM.md §25)"
        )
    )
    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        if nodeid in _REQUIRES_CLINICAL_CSV_PROJECTION:
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def _demo_catalog_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Production tests must not inherit an interview DEMO_MODE from the shell."""
    monkeypatch.delenv("WAGTOPIA_DEMO_MODE", raising=False)


@pytest.fixture(autouse=True)
def _isolated_waggy_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Dog-state SQLite must not leak across tests or into var/."""
    monkeypatch.setenv("WAGGY_STATE_PATH", str(tmp_path / "waggy_state.sqlite"))
    from app.state.groomer import reset_groomer_sessions
    from app.state.store import reset_connection, reset_store

    reset_connection()
    reset_store()
    reset_groomer_sessions()
    yield
    reset_groomer_sessions()
    reset_connection()
