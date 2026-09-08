"""Ω11 must not grow a second engine or invent science/products."""

from __future__ import annotations

import ast
from pathlib import Path

from app.contracts.agent.adapters import (
    bundles_from_search_envelope,
    health_from_care_model,
    nutrition_from_requirement_profile,
    product_from_catalog_row,
)
from app.contracts.agent.bundles import OPTIMIZER_ALGORITHM
from app.contracts.agent.enums import AvailabilityStatus, EvidenceStatus, ToolErrorCode
from app.contracts.agent.registry import EXCLUDED_FROM_AGENT_SURFACE, FUTURE_TOOL_REGISTRY
from app.contracts.agent.versions import VersionStamp

CONTRACTS_ROOT = Path(__file__).resolve().parents[2] / "app" / "contracts"

FORBIDDEN_IMPORTS = {
    "app.agent.engine",
    "app.agent.package_optimizer",
    "app.agent.package_search",
    "app.data.scientific_care",
    "app.data.scientific_requirements",
    "app.formulas",
    "app.presentation.adapter",
}


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_contract_layer_does_not_import_reasoning_engines():
    for py in CONTRACTS_ROOT.rglob("*.py"):
        for mod in _imports(py):
            for forbidden in FORBIDDEN_IMPORTS:
                assert not (mod == forbidden or mod.startswith(forbidden + ".")), (
                    f"{py} imports reasoning module {mod}"
                )


def test_contract_layer_does_not_instantiate_ppie_engine():
    for py in CONTRACTS_ROOT.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "PPIEWellnessAgent" not in text
        assert "AgentHealthEngine" not in text
        assert "AgentNutritionEngine" not in text
        assert "AgentPackageEngine" not in text


def test_allowed_engine_imports_are_version_and_state_only():
    adapters = CONTRACTS_ROOT / "agent" / "adapters.py"
    mods = _imports(adapters)
    assert "app.agent.state" in mods
    versions = CONTRACTS_ROOT / "agent" / "versions.py"
    assert "app.agent.version" in _imports(versions)


def test_health_adapter_does_not_invent_prevalence():
    empty = health_from_care_model(
        {
            "evidence_status": "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE",
            "condition_records": [],
            "prevalence_available": False,
            "diagnosis_claim": False,
        },
        versions=VersionStamp(),
    )
    assert empty.evidence_status == EvidenceStatus.NOT_AVAILABLE
    assert empty.findings == []
    mapped = health_from_care_model(
        {
            "evidence_status": "WAREHOUSE_EVIDENCE",
            "prevalence_available": False,
            "condition_records": [
                {
                    "condition": "Example",
                    "status": "WAREHOUSE_EVIDENCE",
                    "prevalence": {"observed": "NOT_AVAILABLE", "estimated": "NOT_AVAILABLE"},
                    "diagnosis_claim": False,
                }
            ],
        },
        versions=VersionStamp(),
    )
    finding = mapped.findings[0]
    assert finding.observed_prevalence.status == AvailabilityStatus.NOT_AVAILABLE
    assert finding.observed_prevalence.percent is None
    assert finding.diagnosis_claim is False


def test_nutrition_adapter_does_not_invent_requirements():
    result = nutrition_from_requirement_profile(
        {
            "basis": "dry_matter_diet_density",
            "nutrients": {
                "protein_pct_dm": {
                    "id": "protein_pct_dm",
                    "display": "Protein",
                    "minimum": 18.0,
                    "maximum": None,
                    "unit": "% DM",
                    "basis": "percent_dry_matter",
                }
            },
            "not_modeled": [{"id": "water"}],
            "senior_specific_minima": "NOT_AVAILABLE — source does not provide senior-specific nutrient minima",
            "source": {"label": "secondary source example"},
        },
        versions=VersionStamp(),
    )
    assert result.nutrients[0].minimum == 18.0
    assert result.nutrients[0].daily_requirement is None
    assert result.nutrients[0].daily_requirement_status == EvidenceStatus.NOT_AVAILABLE
    assert result.senior_specific_minima == EvidenceStatus.NOT_AVAILABLE


def test_bundle_adapter_does_not_choose_or_invent_products():
    empty = bundles_from_search_envelope({"package_options": {}}, versions=VersionStamp())
    assert empty.status == ToolErrorCode.NO_VALID_BUNDLES
    assert empty.optimizer.algorithm == OPTIMIZER_ALGORITHM
    assert empty.optimizer.llm_used is False
    filled = bundles_from_search_envelope(
        {
            "package_options": {
                "essential": [
                    {
                        "bundle_id": "EXAMPLE",
                        "product_ids": ["SKU1"],
                        "products": [{"product_id": "SKU1", "product_name": "Example"}],
                        "monthly_cost": 10.0,
                    }
                ]
            },
            "optimizer_provenance": {
                "algorithm": OPTIMIZER_ALGORITHM,
                "llm_used": False,
                "filter_funnel": {"generated": 7, "evaluated": 7, "displayed": {"essential": 1}},
            },
        },
        versions=VersionStamp(),
    )
    assert filled.essential[0].product_ids == ["SKU1"]
    assert filled.optimizer.filter_funnel is not None
    assert filled.optimizer.filter_funnel.generated == 7
    assert filled.status is None


def test_product_adapter_does_not_invent_price_or_efficacy():
    product = product_from_catalog_row({"product_id": "SKU1", "product_name": "Example"})
    assert product.commercial.price is None
    assert product.eligibility is None
    assert product.evidence == []


def test_authoring_routes_are_excluded_from_registry():
    names = [entry.name for entry in FUTURE_TOOL_REGISTRY]
    assert "authoring" not in " ".join(names)
    assert any("authoring/evidence" in item for item in EXCLUDED_FROM_AGENT_SURFACE)
