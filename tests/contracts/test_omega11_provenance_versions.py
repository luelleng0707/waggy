"""Ω11 provenance and versioning contracts."""

from __future__ import annotations

from app.agent.version import ALGORITHM_VERSION, ENGINE_NAME
from app.contracts.agent.adapters import evidence_from_warehouse_row, fact_from_warehouse_row
from app.contracts.agent.enums import EvidenceStatus
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.registry import FUTURE_TOOL_REGISTRY
from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION, VersionStamp, runtime_engine_version


def test_provenance_retains_warehouse_evidence_fields():
    record = ProvenanceRecord(
        source_type="warehouse_row",
        fact_id="EXAMPLE_FACT",
        paper_id="EXAMPLE_PAPER",
        source_name="Example paper",
        source_link="https://example.invalid/paper",
        publication_year="2021",
        quote="Example quote",
        status=EvidenceStatus.NEEDS_VALIDATION,
        warehouse_version="example-warehouse",
        csv_hash="deadbeef",
        engine_version=ALGORITHM_VERSION,
        capability_id="analyze_health",
    )
    dumped = record.model_dump(mode="json")
    assert dumped["paper_id"] == "EXAMPLE_PAPER"
    assert dumped["source_name"] == "Example paper"
    assert dumped["source_link"] == "https://example.invalid/paper"
    assert dumped["publication_year"] == "2021"
    assert dumped["quote"] == "Example quote"
    assert dumped["status"] == "NEEDS_VALIDATION"
    assert dumped["warehouse_version"] == "example-warehouse"
    assert dumped["engine_version"] == ALGORITHM_VERSION


def test_unavailable_provenance_is_explicit_not_fabricated():
    record = ProvenanceRecord(
        source_type="warehouse_row",
        status=EvidenceStatus.MISSING_PROVENANCE,
        paper_id=None,
        source_link=None,
        publication_year=None,
        quote=None,
    )
    assert record.paper_id is None
    assert record.quote is None
    assert record.status == EvidenceStatus.MISSING_PROVENANCE


def test_fact_adapter_preserves_row_provenance_without_inventing():
    row = {
        "fact_id": "EXAMPLE_FACT",
        "breed_name": "Example Breed",
        "condition_name": "Example Condition",
        "measure_type": "prevalence",
        "value_number": 0.127,
        "unit": "ratio",
        "scientific_quote": "Example quote",
        "paper_name": "Example paper",
        "paper_link": "https://example.invalid/paper",
        "publication_year": "2021",
        "status": "NEEDS_VALIDATION",
        "source_table": "observed_breed_conditions",
    }
    fact = fact_from_warehouse_row(row, warehouse_version="example")
    evidence = evidence_from_warehouse_row(row, warehouse_version="example")
    assert fact.status == EvidenceStatus.NEEDS_VALIDATION
    assert evidence.paper_name == "Example paper"
    assert fact.provenance[0].quote == "Example quote"
    assert fact.provenance[0].engine_version == ALGORITHM_VERSION


def test_version_stamp_reuses_algorithm_version():
    stamp = VersionStamp(
        warehouse_version="5.0.0-science",
        csv_hash="abc",
        tool_version="1.0.0",
        analysis_version=ALGORITHM_VERSION,
    )
    assert stamp.engine_version == ALGORITHM_VERSION
    assert stamp.engine_name == ENGINE_NAME
    assert stamp.schema_version == AGENT_CONTRACT_SCHEMA_VERSION
    assert runtime_engine_version() == ALGORITHM_VERSION
    assert stamp.engine_version != stamp.schema_version or ALGORITHM_VERSION == AGENT_CONTRACT_SCHEMA_VERSION
    # The important invariant: contract schema is additive, engine version is unchanged.
    assert ALGORITHM_VERSION == "2.1.0"


def test_registry_has_tool_version_place():
    names = {entry.name for entry in FUTURE_TOOL_REGISTRY}
    assert names == {"analyze_health", "calculate_nutrition", "optimize_bundles", "generate_report"}
    for entry in FUTURE_TOOL_REGISTRY:
        assert entry.tool_version == "1.0.0"
        assert entry.schema_version == AGENT_CONTRACT_SCHEMA_VERSION
        assert not hasattr(entry, "execute")
