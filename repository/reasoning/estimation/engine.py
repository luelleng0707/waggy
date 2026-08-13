"""Estimated epidemiology stage."""

from __future__ import annotations

from collections import defaultdict

from repository.models.explainability import ScientificCitation
from repository.models.runtime import EvidenceGraph, ResolvedDog
from repository.reasoning.mathematics import (
    FORMULA_REGISTRY,
    canonical_percentage,
    contribution_from_factor,
    estimated_prevalence,
)
from repository.reasoning.models import (
    EstimatedCondition,
    EvidenceContribution,
    FormulaTrace,
)


WEIGHT_BY_EVIDENCE_TYPE = {
    "trait": 1.0,
    "environment": 1.0,
    "interaction": 1.0,
    "life_stage": 1.0,
    "activity": 1.0,
    "ingredient": 1.0,
}


class DeterministicEstimatedEngine:
    def evaluate(
        self,
        resolved_dog: ResolvedDog,
        evidence_graph: EvidenceGraph,
    ) -> tuple[EstimatedCondition, ...]:
        _ = resolved_dog
        condition_nodes = [n for n in evidence_graph.nodes if n.get("node_type") == "condition"]
        citations_by_id = {c.get("citation_id", ""): c for c in evidence_graph.citations}

        by_condition_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
        for edge in evidence_graph.edges:
            to_node_id = edge.get("to_node_id", "")
            by_condition_edges[to_node_id].append(edge)

        out: list[EstimatedCondition] = []
        for node in condition_nodes:
            node_id = node.get("node_id", "")
            condition_id = node.get("condition_id", "")
            condition_name = node.get("condition_name", "")
            edges = by_condition_edges.get(node_id, [])

            # baseline from observed when available
            observed_edges = [e for e in edges if e.get("evidence_type") == "observed"]
            baseline = canonical_percentage(observed_edges[0].get("observed_value", 0.0)) if observed_edges else 0.0

            contributions: list[EvidenceContribution] = []
            formulas: list[FormulaTrace] = []
            citations: list[ScientificCitation] = []
            numeric_contribs: list[float] = []

            for edge in edges:
                etype = edge.get("evidence_type", "")
                if etype not in WEIGHT_BY_EVIDENCE_TYPE:
                    continue
                weight = WEIGHT_BY_EVIDENCE_TYPE[etype]
                source_fact_id = edge.get("source_fact_id", "")
                citation_row = citations_by_id.get(edge.get("citation_id", ""), {})
                citation = ScientificCitation(
                    citation_id=citation_row.get("citation_id", ""),
                    paper_name=citation_row.get("paper_name", ""),
                    paper_link=citation_row.get("paper_link", ""),
                    scientific_quote=citation_row.get("scientific_quote", ""),
                    fact_id=citation_row.get("fact_id", ""),
                )
                citations.append(citation)

                if etype == "interaction":
                    factor = edge.get("factor", "")
                    value = contribution_from_factor(factor, baseline if baseline > 0 else 1.0)
                    f = FORMULA_REGISTRY["EST-003"]
                    formulas.append(
                        FormulaTrace(
                            formula_id=f.formula_id,
                            formula_version=f.version,
                            equation=f.equation,
                            inputs={"factor": factor, "baseline_percent": baseline},
                            output=value,
                        )
                    )
                else:
                    raw_value = edge.get("value_number", edge.get("observed_value", ""))
                    value = canonical_percentage(raw_value) * weight
                    f = FORMULA_REGISTRY["EST-002"]
                    formulas.append(
                        FormulaTrace(
                            formula_id=f.formula_id,
                            formula_version=f.version,
                            equation=f.equation,
                            inputs={"raw_value": str(raw_value), "weight": weight},
                            output=value,
                        )
                    )
                numeric_contribs.append(value)
                contributions.append(
                    EvidenceContribution(
                        condition_id=condition_id,
                        condition_name=condition_name,
                        source_type=etype,
                        source_fact_id=source_fact_id,
                        source_trait=edge.get("source_label", ""),
                        paper_name=citation.paper_name,
                        paper_link=citation.paper_link,
                        scientific_quote=citation.scientific_quote,
                        weight=weight,
                        contribution_value=value,
                        formula_used=formulas[-1].formula_id,
                    )
                )

            estimate = estimated_prevalence(tuple(numeric_contribs))
            f_est = FORMULA_REGISTRY["EST-004"]
            formulas.append(
                FormulaTrace(
                    formula_id=f_est.formula_id,
                    formula_version=f_est.version,
                    equation=f_est.equation,
                    inputs={"contribution_count": float(len(numeric_contribs))},
                    output=estimate,
                )
            )
            out.append(
                EstimatedCondition(
                    condition_id=condition_id,
                    condition_name=condition_name,
                    estimated_prevalence=estimate,
                    contributions=tuple(contributions),
                    citations=tuple(citations),
                    formula_traces=tuple(formulas),
                )
            )

        return tuple(out)
