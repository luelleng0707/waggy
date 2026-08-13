"""Numeric normalization utilities."""

from __future__ import annotations

import math


def as_float(value: str | float | int | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def canonical_percent(value: str | float | int | None) -> float:
    raw = as_float(value)
    if raw <= 1.0:
        return raw * 100.0
    return raw


def clamp_probability(value: float) -> float:
    return min(0.999999, max(0.000001, value))


def percent_to_probability(percent: float) -> float:
    return clamp_probability(percent / 100.0)


def probability_to_percent(probability: float) -> float:
    return clamp_probability(probability) * 100.0


def logit(probability: float) -> float:
    p = clamp_probability(probability)
    return math.log(p / (1.0 - p))


def logistic(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))
