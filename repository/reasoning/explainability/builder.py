"""Explainability chain helpers for Ω4 condition assessments."""

from __future__ import annotations

from repository.models.explainability import ScientificCitation
from repository.reasoning.models import (
    AgreementResult,
    EstimatedCondition,
    ObservedCondition,
    ReasoningChainStep,
)


def build_reasoning_chain(
    observed: ObservedCondition | None,
    estimated: EstimatedCondition,
    agreement: AgreementResult | None,
) -> tuple[ReasoningChainStep, ...]:
    steps: list[ReasoningChainStep] = []
    if observed is not None:
        steps.append(
            ReasoningChainStep(
                stage="Observed Epidemiology",
                condition_id=observed.condition_id,
                condition_name=observed.condition_name,
                summary=f"Observed prevalence {observed.observed_prevalence:.4f}%",
                source_fact_ids=(observed.source_fact_id,),
                citations=observed.citations,
                formula_traces=observed.formula_traces,
            )
        )
    steps.append(
        ReasoningChainStep(
            stage="Estimated Epidemiology",
            condition_id=estimated.condition_id,
            condition_name=estimated.condition_name,
            summary=f"Estimated prevalence {estimated.estimated_prevalence:.4f}%",
            source_fact_ids=tuple([c.source_fact_id for c in estimated.contributions if c.source_fact_id]),
            citations=estimated.citations,
            formula_traces=estimated.formula_traces,
        )
    )
    if agreement is not None:
        steps.append(
            ReasoningChainStep(
                stage="Agreement Analysis",
                condition_id=agreement.condition_id,
                condition_name=agreement.condition_name,
                summary=f"Agreement {agreement.agreement_percentage:.4f}%",
                source_fact_ids=tuple(),
                citations=tuple(),
                formula_traces=agreement.formula_traces,
            )
        )
    return tuple(steps)


def unique_citations(citations: tuple[ScientificCitation, ...]) -> tuple[ScientificCitation, ...]:
    seen: set[str] = set()
    out: list[ScientificCitation] = []
    for c in citations:
        key = f"{c.fact_id}|{c.paper_link}"
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return tuple(out)
