"""Observed epidemiology engine (MAT-1001)."""

from __future__ import annotations

from .formulas import FORMULA_REGISTRY
from .models import MathematicalFormulaTrace, ObservedEpidemiology
from .normalization import canonical_percent


class ObservedEpidemiologyEngine:
    def evaluate(self, condition_id: str, condition_name: str, edges: tuple[dict[str, str], ...], citations: dict[str, dict[str, str]]) -> ObservedEpidemiology:
        observed = [edge for edge in edges if edge.get("evidence_type", "").strip().lower() == "observed"]
        values = [canonical_percent(edge.get("observed_value", edge.get("value_number", ""))) for edge in observed]
        source_fact_ids = tuple(
            sorted(
                set(
                    [
                        str(edge.get("source_fact_id", "")).strip()
                        for edge in observed
                        if str(edge.get("source_fact_id", "")).strip()
                    ]
                )
            )
        )
        prevalence = (sum(values) / float(len(values))) if values else 0.0
        quotes: list[str] = []
        papers: list[str] = []
        links: list[str] = []
        for edge in observed:
            citation = citations.get(edge.get("citation_id", ""), {})
            quote = str(citation.get("scientific_quote", "")).strip()
            paper = str(citation.get("paper_name", "")).strip()
            link = str(citation.get("paper_link", "")).strip()
            if quote:
                quotes.append(quote)
            if paper:
                papers.append(paper)
            if link:
                links.append(link)
        formula = FORMULA_REGISTRY["MAT-1001"]
        substituted = f"observed_prevalence = mean({[round(value, 6) for value in values]})"
        trace = MathematicalFormulaTrace(
            formula_id=formula.formula_id,
            formula_version=formula.version,
            formula_name=formula.description,
            status="NO_EVIDENCE" if not observed else "active",
            equation=formula.equation,
            substituted_equation=substituted,
            python_file="repository/mathematics/epidemiology.py",
            python_function="ObservedEpidemiologyEngine.evaluate",
            source_line_start=11,
            source_line_end=66,
            input_variables=("observed_edge_values",),
            inputs={"observed_count": len(values), "observed_values_sum": round(sum(values), 6)},
            intermediate_values={"observed_values_mean": round(prevalence, 6)},
            output_variable="observed_prevalence",
            unit="percent",
            warehouse_row_ids=tuple([f"fact_id:{fact_id}" for fact_id in source_fact_ids]),
            evidence_ids=source_fact_ids,
            paper_names=tuple(dict.fromkeys(papers)),
            paper_links=tuple(dict.fromkeys(links)),
            scientific_quotes=tuple(dict.fromkeys(quotes)),
            output=round(prevalence, 6),
        )
        return ObservedEpidemiology(
            condition_id=condition_id,
            condition_name=condition_name,
            observed_prevalence=round(prevalence, 6),
            evidence_count=len(observed),
            supporting_quotes=tuple(dict.fromkeys(quotes)),
            supporting_papers=tuple(dict.fromkeys(papers)),
            supporting_links=tuple(dict.fromkeys(links)),
            formula_traces=(trace,),
        )
