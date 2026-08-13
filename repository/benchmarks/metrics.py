"""Deterministic benchmark metrics."""

from __future__ import annotations

import math


def mean_absolute_error(actual: tuple[float, ...], predicted: tuple[float, ...]) -> float:
    if not actual:
        return 0.0
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / float(len(actual))


def root_mean_squared_error(actual: tuple[float, ...], predicted: tuple[float, ...]) -> float:
    if not actual:
        return 0.0
    mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / float(len(actual))
    return math.sqrt(mse)


def mean_agreement(actual: tuple[float, ...], predicted: tuple[float, ...]) -> float:
    if not actual:
        return 0.0
    values = []
    for a, p in zip(actual, predicted):
        rel_error = abs(a - p) / max(abs(a), 1e-6)
        values.append(max(0.0, 100.0 - (rel_error * 100.0)))
    return sum(values) / float(len(values))


def ranking_stability(reference: tuple[str, ...], compared: tuple[str, ...]) -> float:
    if not reference:
        return 100.0
    matched_positions = 0
    index = {condition: pos for pos, condition in enumerate(compared)}
    for pos, condition in enumerate(reference):
        if index.get(condition, -1) == pos:
            matched_positions += 1
    return (matched_positions / float(len(reference))) * 100.0
