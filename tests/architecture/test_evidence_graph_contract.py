from __future__ import annotations

from repository.models.runtime import ConditionEvidence, EvidenceCollection
from repository.pipeline.biological_runtime import InMemoryEvidenceGraphBuilder


def _sample_row(fact_id: str, quote: str) -> dict[str, str]:
    return {
        "fact_id": fact_id,
        "paper_name": "Clinical Study A",
        "paper_link": "https://example.org/paper-a",
        "scientific_quote": quote,
        "condition_name": "Atopic Dermatitis",
        "condition_id": "COND_ATOPIC",
        "trait_value": "pruritus",
    }


def test_evidence_graph_is_deterministic_for_same_input():
    evidence = ConditionEvidence(
        dog_id="DOG001",
        condition_id="COND_ATOPIC",
        condition_name="Atopic Dermatitis",
        trait_evidence=(_sample_row("FACT001", "Quote 1"),),
    )
    collection = EvidenceCollection(dog_id="DOG001", condition_evidence=(evidence,))
    builder = InMemoryEvidenceGraphBuilder()

    g1 = builder.build(collection)
    g2 = builder.build(collection)
    assert g1 == g2


def test_evidence_graph_preserves_provenance_fields():
    evidence = ConditionEvidence(
        dog_id="DOG001",
        condition_id="COND_ATOPIC",
        condition_name="Atopic Dermatitis",
        observed_evidence=(_sample_row("FACT001", "Quote 1"),),
    )
    graph = InMemoryEvidenceGraphBuilder().build(
        EvidenceCollection(dog_id="DOG001", condition_evidence=(evidence,))
    )
    assert graph.citations
    citation = graph.citations[0]
    assert citation["fact_id"] == "FACT001"
    assert citation["paper_name"] == "Clinical Study A"
    assert citation["paper_link"] == "https://example.org/paper-a"
    assert citation["scientific_quote"] == "Quote 1"
    assert any(edge.get("citation_id") for edge in graph.edges)


def test_evidence_graph_handles_missing_evidence_without_failure():
    graph = InMemoryEvidenceGraphBuilder().build(EvidenceCollection(dog_id="DOG001"))
    assert graph.nodes == tuple()
    assert graph.edges == tuple()
    assert graph.citations == tuple()


def test_evidence_graph_duplicate_rows_remain_traceable():
    row = _sample_row("FACT001", "Quote 1")
    evidence = ConditionEvidence(
        dog_id="DOG001",
        condition_id="COND_ATOPIC",
        condition_name="Atopic Dermatitis",
        trait_evidence=(row, row),
    )
    graph = InMemoryEvidenceGraphBuilder().build(
        EvidenceCollection(dog_id="DOG001", condition_evidence=(evidence,))
    )
    trait_edges = [edge for edge in graph.edges if edge.get("evidence_type") == "trait"]
    assert len(trait_edges) == 2
    assert all(edge["source_fact_id"] == "FACT001" for edge in trait_edges)
