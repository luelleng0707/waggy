"""Benchmark reporting primitives."""

from __future__ import annotations

from .comparator import BenchmarkComparison


def render_comparison_report(comparisons: tuple[BenchmarkComparison, ...]) -> str:
    lines = ["# Benchmark Comparison", ""]
    if not comparisons:
        lines.append("- No benchmark comparisons available.")
        return "\n".join(lines)
    for comparison in comparisons:
        lines.append(
            f"- {comparison.formula_version}: "
            f"MAE={comparison.mae:.6f}, RMSE={comparison.rmse:.6f}, "
            f"Agreement={comparison.agreement:.6f}, RankingStability={comparison.ranking_stability:.6f}"
        )
    return "\n".join(lines)
