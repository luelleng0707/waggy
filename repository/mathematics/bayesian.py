"""Bayesian-style posterior prevalence updates."""

from __future__ import annotations

from .normalization import logit, logistic, percent_to_probability, probability_to_percent


def posterior_percent(prior_percent: float, evidence_percent: float, strength: float) -> float:
    s = max(0.0, min(1.0, strength))
    prior_logit = logit(percent_to_probability(prior_percent))
    evidence_logit = logit(percent_to_probability(evidence_percent))
    posterior_logit = ((1.0 - s) * prior_logit) + (s * evidence_logit)
    return probability_to_percent(logistic(posterior_logit))
