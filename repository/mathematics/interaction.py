"""Interaction adjustment mathematics."""

from __future__ import annotations

from .normalization import as_float


def interaction_adjustment(edges: tuple[dict[str, str], ...]) -> float:
    """Return additive percent adjustment from interaction factors."""
    deltas: list[float] = []
    for edge in edges:
        factor = as_float(edge.get("factor", ""))
        baseline = as_float(edge.get("value_number", ""))
        if baseline <= 1.0:
            baseline *= 100.0
        if factor > 0:
            deltas.append((factor - 1.0) * baseline)
    if not deltas:
        return 0.0
    return sum(deltas) / float(len(deltas))
