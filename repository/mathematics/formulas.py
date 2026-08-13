"""Versioned formula registry for Ω9 mathematics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormulaDefinition:
    formula_id: str
    version: str
    equation: str
    description: str
    units: str


FORMULA_REGISTRY: dict[str, FormulaDefinition] = {
    "MAT-1001": FormulaDefinition(
        "MAT-1001",
        "1.0.0",
        "observed_prevalence = mean(observed_edge_values)",
        "Observed epidemiology aggregation from direct observed edges.",
        "percent",
    ),
    "MAT-1002": FormulaDefinition(
        "MAT-1002",
        "1.0.0",
        "trait_environment_aggregate = logistic(weighted_mean(logit(edge_prevalence)))",
        "Trait/environment evidence aggregation using weighted log-odds.",
        "percent",
    ),
    "MAT-1003": FormulaDefinition(
        "MAT-1003",
        "1.0.0",
        "posterior = logistic((1-strength)*logit(prior)+strength*logit(evidence))",
        "Bayesian-style prevalence update from prior and evidence aggregate.",
        "percent",
    ),
    "MAT-1004": FormulaDefinition(
        "MAT-1004",
        "1.0.0",
        "agreement = max(0, 100-(abs_error/max(observed,1e-6))*100)",
        "Agreement and prediction error mathematics.",
        "percent",
    ),
    "MAT-1005": FormulaDefinition(
        "MAT-1005",
        "1.0.0",
        "confidence = weighted_evidence_score * agreement_factor",
        "Confidence from evidence depth, study breadth, and agreement quality.",
        "percent",
    ),
    "MAT-1006": FormulaDefinition(
        "MAT-1006",
        "1.0.0",
        "novelty = max(0, estimated-observed) * confidence_scale",
        "Novelty scoring and emerging concern detection.",
        "score",
    ),
    "MAT-1007": FormulaDefinition(
        "MAT-1007",
        "1.0.0",
        "priority = estimated * confidence * (1+novelty/100) * agreement_scale",
        "Priority ranking from prevalence burden, certainty, and novelty.",
        "score",
    ),
    "MAT-1008": FormulaDefinition(
        "MAT-1008",
        "1.0.0",
        "uncertainty = stddev(contributions) * uncertainty_factor",
        "Uncertainty and confidence interval calculation.",
        "percent",
    ),
}

