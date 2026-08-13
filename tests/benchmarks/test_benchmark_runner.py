from __future__ import annotations

from repository.benchmarks.runner import BenchmarkRunner
from repository.warehouse import WarehouseInterface


def test_benchmark_runner_reproducible():
    runner = BenchmarkRunner(WarehouseInterface())
    first = runner.run("MAT-1005", "v1.0", ("v2.0",))
    second = runner.run("MAT-1005", "v1.0", ("v2.0",))
    assert first == second
    assert first


def test_benchmark_report_contains_metrics():
    runner = BenchmarkRunner(WarehouseInterface())
    report = runner.report("MAT-1005", "v1.0", ("v2.0",))
    assert "MAE=" in report
    assert "RMSE=" in report
    assert "Agreement=" in report
