"""100-dog scientific benchmark suite — runtime metrics only; does not alter clinical math."""

from __future__ import annotations

import json
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.data.repository import DataPlatform

ROOT = Path(__file__).resolve().parents[2]


def _sample_dogs(n: int = 100) -> list[DogProfileInput]:
    breeds = [
        "Labrador Retriever",
        "German Shepherd Dog",
        "French Bulldog",
        "Golden Retriever",
        "Chihuahua",
        "Border Collie",
        "Poodle",
        "Beagle",
        "Boxer",
        "Dachshund",
    ]
    climates = ["Shanghai Summer", "temperate", "cold"]
    dogs: list[DogProfileInput] = []
    for i in range(n):
        dogs.append(
            DogProfileInput(
                name=f"BenchDog{i:03d}",
                primary_breed=breeds[i % len(breeds)],
                age_years=float(1 + (i % 12)),
                weight_kg=float(5 + (i % 40)),
                current_environment=climates[i % len(climates)],
                activity_level=["Low", "Moderate", "High"][i % 3],
                sex="male" if i % 2 == 0 else "female",
            )
        )
    return dogs


def run_benchmark(n: int = 100, agent: PPIEWellnessAgent | None = None) -> dict[str, Any]:
    agent = agent or PPIEWellnessAgent()
    dogs = _sample_dogs(n)

    tracemalloc.start()
    t0 = time.perf_counter()
    node_timings: dict[str, list[float]] = {}
    api_latencies: list[float] = []
    failures = 0

    for dog in dogs:
        s = time.perf_counter()
        try:
            result = agent.assess(dog)
            elapsed = time.perf_counter() - s
            api_latencies.append(elapsed)
            debug = {}
            if hasattr(result, "trace") and isinstance(result.trace, dict):
                debug = result.trace
            elif hasattr(result, "to_dict"):
                d = result.to_dict()
                debug = d.get("debug") or d.get("trace") or {}
            elif isinstance(result, dict):
                debug = result.get("debug") or {}
            trace = debug.get("execution") or debug.get("formula_execution_trace") or []
            if isinstance(trace, list):
                for step in trace:
                    if not isinstance(step, dict):
                        continue
                    nid = step.get("node") or step.get("formula_id") or step.get("id") or "unknown"
                    ms = step.get("timing_ms") or step.get("duration_ms") or step.get("elapsed_ms")
                    if ms is None and step.get("duration") is not None:
                        ms = float(step["duration"]) * 1000
                    if ms is not None:
                        node_timings.setdefault(str(nid), []).append(float(ms))
        except Exception:
            failures += 1
            api_latencies.append(time.perf_counter() - s)

    total_s = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    platform = DataPlatform("data", strict=True)
    load_t0 = time.perf_counter()
    _ = platform.breeds
    _ = platform.breed_conditions()
    _ = platform.products
    csv_load_s = time.perf_counter() - load_t0

    from app.science.builder import KnowledgeGraphBuilder

    g_t0 = time.perf_counter()
    graph = KnowledgeGraphBuilder(platform).build()
    _ = len(graph.edges)
    graph_s = time.perf_counter() - g_t0

    node_avg = {
        k: round(sum(v) / len(v), 3) for k, v in sorted(node_timings.items(), key=lambda x: -sum(x[1]))
    }
    slowest = sorted(node_avg.items(), key=lambda x: -x[1])[:15]

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dogs": n,
        "failures": failures,
        "runtime_seconds": round(total_s, 4),
        "avg_api_latency_ms": round(1000 * sum(api_latencies) / max(len(api_latencies), 1), 3),
        "p95_api_latency_ms": 0.0,
        "memory_peak_mb": round(peak / (1024 * 1024), 3),
        "memory_current_mb": round(current / (1024 * 1024), 3),
        "csv_loading_seconds": round(csv_load_s, 4),
        "graph_traversal_seconds": round(graph_s, 4),
        "graph_nodes": len(graph.nodes),
        "graph_edges": len(graph.edges),
        "node_avg_ms": node_avg,
        "slowest_nodes": slowest,
        "pipeline": ["risk", "nutrition", "products", "packages", "assessment", "reports"],
    }
    if api_latencies:
        sorted_lat = sorted(api_latencies)
        idx = min(len(sorted_lat) - 1, max(0, int(0.95 * (len(sorted_lat) - 1))))
        report["p95_api_latency_ms"] = round(1000 * sorted_lat[idx], 3)
    return report


def write_benchmark_report(report: dict[str, Any], out_path: Path | None = None) -> Path:
    out_path = out_path or (ROOT / "governance" / "reports" / "BENCHMARK_REPORT.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Benchmark Report",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"- Dogs: {report['dogs']}",
        f"- Failures: {report['failures']}",
        f"- Total runtime: {report['runtime_seconds']}s",
        f"- Avg API latency: {report['avg_api_latency_ms']} ms",
        f"- P95 API latency: {report['p95_api_latency_ms']} ms",
        f"- Peak memory (tracemalloc): {report['memory_peak_mb']} MB",
        f"- CSV loading: {report['csv_loading_seconds']}s",
        f"- Graph build/traverse: {report['graph_traversal_seconds']}s "
        f"({report['graph_nodes']} nodes / {report['graph_edges']} edges)",
        "",
        "## Slowest Nodes (avg ms)",
        "",
    ]
    for name, ms in report.get("slowest_nodes") or []:
        lines.append(f"- `{name}`: {ms}")
    if not report.get("slowest_nodes"):
        lines.append("_No per-node timings in response debug (run with debug formula trace enabled)._")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    out_path.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path
