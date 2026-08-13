"""Observed epidemiology retrieval stage."""

from __future__ import annotations

from repository.models.explainability import ScientificCitation
from repository.models.runtime import EvidenceGraph
from repository.reasoning.models import FormulaTrace, ObservedCondition
from repository.reasoning.mathematics import FORMULA_REGISTRY, canonical_percentage


class DeterministicObservedEngine:
    def evaluate(self, evidence_graph: EvidenceGraph) -> tuple[ObservedCondition, ...]:
        condition_nodes = [n for n in evidence_graph.nodes if n.get("node_type") == "condition"]
        citations_by_id = {c.get("citation_id", ""): c for c in evidence_graph.citations}
        out: list[ObservedCondition] = []

        for node in condition_nodes:
            node_id = node.get("node_id", "")
            observed_edges = [
                e for e in evidence_graph.edges
                if e.get("to_node_id") == node_id and e.get("evidence_type") == "observed"
            ]
            if not observed_edges:
                continue

            edge = observed_edges[0]
            observed_pct = canonical_percentage(edge.get("observed_value", ""))
            citation_row = citations_by_id.get(edge.get("citation_id", ""), {})
            citation = ScientificCitation(
                citation_id=citation_row.get("citation_id", ""),
                paper_name=citation_row.get("paper_name", ""),
                paper_link=citation_row.get("paper_link", ""),
                scientific_quote=citation_row.get("scientific_quote", ""),
                fact_id=citation_row.get("fact_id", ""),
            )
            f = FORMULA_REGISTRY["EST-001"]
            trace = FormulaTrace(
                formula_id=f.formula_id,
                formula_version=f.version,
                equation=f.equation,
                inputs={"raw_observed": edge.get("observed_value", "")},
                output=observed_pct,
            )
            out.append(
                ObservedCondition(
                    condition_id=node.get("condition_id", ""),
                    condition_name=node.get("condition_name", ""),
                    observed_prevalence=observed_pct,
                    population=edge.get("population", ""),
                    sample_size=edge.get("sample_size", ""),
                    publication_year=edge.get("publication_year", ""),
                    paper=citation.paper_name,
                    quote=citation.scientific_quote,
                    paper_link=citation.paper_link,
                    source_fact_id=edge.get("source_fact_id", ""),
                    citations=(citation,),
                    formula_traces=(trace,),
                )
            )
        return tuple(out)
