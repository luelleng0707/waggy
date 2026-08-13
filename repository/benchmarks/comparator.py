"""Compare benchmark outputs across formula versions."""

from __future__ import annotations

from dataclasses import dataclass

from .metrics import mean_absolute_error, mean_agreement, ranking_stability, root_mean_squared_error


@dataclass(frozen=True)
class BenchmarkComparison:
    formula_version: str
    mae: float
    rmse: float
    agreement: float
    ranking_stability: float


def compare_versions(
    reference_actual: tuple[float, ...],
    baseline_predicted: tuple[float, ...],
    candidate_predicted: tuple[float, ...],
    baseline_ranking: tuple[str, ...],
    candidate_ranking: tuple[str, ...],
    candidate_version: str,
) -> BenchmarkComparison:
    del baseline_predicted  # baseline already captured by reference metric strategy
    return BenchmarkComparison(
        formula_version=candidate_version,
        mae=round(mean_absolute_error(reference_actual, candidate_predicted), 6),
        rmse=round(root_mean_squared_error(reference_actual, candidate_predicted), 6),
        agreement=round(mean_agreement(reference_actual, candidate_predicted), 6),
        ranking_stability=round(ranking_stability(baseline_ranking, candidate_ranking), 6),
    )
