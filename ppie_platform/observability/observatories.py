"""ΩA–ΩE observatories — read-only over live system; no clinical math changes."""

from __future__ import annotations

import time
import tracemalloc
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.agent.formula_graph import FormulaGraph
from app.agent.formula_registry import FORMULA_REGISTRY
from app.agent.nodes import default_nodes
from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.science.builder import KnowledgeGraphBuilder
from app.science.coverage import KnowledgeCoverageReport

from ppie_platform.observability.common import ROOT, META, PLATFORM_OUT, default_platform, now_iso, write_md_json


def _sample_profile(i: int = 0) -> DogProfileInput:
    breeds = [
        "Labrador Retriever",
        "German Shepherd Dog",
        "French Bulldog",
        "Golden Retriever",
        "Chihuahua",
        "Border Collie",
        "Poodle",
        "Beagle",
    ]
    return DogProfileInput(
        name=f"OmegaDog{i:04d}",
        primary_breed=breeds[i % len(breeds)],
        age_years=float(1 + (i % 14)),
        weight_kg=float(4 + (i % 45)),
        current_environment=["Shanghai Summer", "temperate", "cold"][i % 3],
        activity_level=["Low", "Moderate", "High"][i % 3],
        sex="female" if i % 2 else "male",
    )


def collect_runtime_sample(n: int = 5) -> dict[str, Any]:
    agent = PPIEWellnessAgent(data_dir="data")
    node_stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"runs": 0, "ms": [], "lookups": []})
    warnings = 0
    errors = 0
    tracemalloc.start()
    t0 = time.perf_counter()
    for i in range(n):
        result = agent.assess(_sample_profile(i))
        trace = []
        if hasattr(result, "trace") and isinstance(result.trace, dict):
            trace = result.trace.get("execution") or []
        for step in trace:
            if not isinstance(step, dict):
                continue
            nid = str(step.get("node") or step.get("formula_id") or "unknown")
            ms = step.get("timing_ms")
            if ms is not None:
                node_stats[nid]["ms"].append(float(ms))
            node_stats[nid]["runs"] += 1
            lookups = step.get("lookups") or []
            node_stats[nid]["lookups"].append(len(lookups) if isinstance(lookups, list) else 0)
            warnings += len(step.get("warnings") or [])
            errors += len(step.get("errors") or [])
    total_s = time.perf_counter() - t0
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    nodes_out = {}
    for nid, st in node_stats.items():
        ms = st["ms"]
        lk = st["lookups"]
        nodes_out[nid] = {
            "runs": st["runs"],
            "avg_runtime_ms": round(sum(ms) / len(ms), 3) if ms else None,
            "avg_lookups": round(sum(lk) / len(lk), 3) if lk else 0,
        }

    platform = default_platform()
    return {
        "generated_at": now_iso(),
        "sample_dogs": n,
        "total_runtime_seconds": round(total_s, 4),
        "memory_peak_mb": round(peak / (1024 * 1024), 3),
        "warnings": warnings,
        "errors": errors,
        "nodes": nodes_out,
        "repository_tables": len(platform._tables),
        "cache_note": "DataPlatform loads CSVs once per process into _tables",
    }


def generate_system_runtime(n: int = 5) -> Path:
    payload = collect_runtime_sample(n)
    lines = [
        "# System Runtime",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        f"- Sample dogs: {payload['sample_dogs']}",
        f"- Total runtime: {payload['total_runtime_seconds']}s",
        f"- Peak memory: {payload['memory_peak_mb']} MB",
        f"- Warnings: {payload['warnings']}",
        f"- Errors: {payload['errors']}",
        f"- Repository tables: {payload['repository_tables']}",
        "",
        "## Per-node",
        "",
        "| Node | Runs | Avg ms | Avg lookups |",
        "|---|---:|---:|---:|",
    ]
    for nid, st in sorted(payload["nodes"].items(), key=lambda x: -(x[1].get("avg_runtime_ms") or 0)):
        lines.append(
            f"| `{nid}` | {st['runs']} | {st['avg_runtime_ms']} | {st['avg_lookups']} |"
        )
    write_md_json("SYSTEM_RUNTIME", "\n".join(lines), payload, PLATFORM_OUT, META / "metrics")
    return PLATFORM_OUT / "SYSTEM_RUNTIME.md"


def generate_formula_observatory(n: int = 5) -> Path:
    runtime = collect_runtime_sample(n)
    graph = FormulaGraph(default_nodes())
    order = graph.order()
    rows = []
    lines = [
        "# Formula Observatory",
        "",
        f"Generated: `{now_iso()}`",
        "",
        "| Node | Formula | Version | Consumers | Avg Runtime ms | Avg Lookups |",
        "|---|---|---|---|---:|---:|",
    ]
    nodes = {n.id: n for n in default_nodes()}
    for nid in order:
        node = nodes[nid]
        meta = FORMULA_REGISTRY.get(node.formula_id, {})
        st = runtime["nodes"].get(nid, {})
        consumers = ", ".join(meta.get("consumers") or []) or "—"
        lines.append(
            f"| `{nid}` | `{node.formula_id}` | {node.version} | {consumers} | "
            f"{st.get('avg_runtime_ms')} | {st.get('avg_lookups')} |"
        )
        rows.append(
            {
                "node": nid,
                "formula_id": node.formula_id,
                "version": node.version,
                "consumers": meta.get("consumers") or [],
                "tables": list(node.tables),
                "avg_runtime_ms": st.get("avg_runtime_ms"),
                "avg_lookups": st.get("avg_lookups"),
                "runs": st.get("runs"),
                "avg_confidence": "see debug.science when enabled",
                "avg_output_distribution": "inspect AssessmentResult per node produces",
            }
        )
    payload = {"generated_at": now_iso(), "nodes": rows, "execution_order": order}
    write_md_json("FORMULA_OBSERVATORY", "\n".join(lines), payload, PLATFORM_OUT, META / "metrics")
    (META / "architecture" / "FORMULA_GRAPH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return PLATFORM_OUT / "FORMULA_OBSERVATORY.md"


def generate_science_observatory() -> Path:
    platform = default_platform()
    graph = KnowledgeGraphBuilder(platform).build()
    by_type: dict[str, int] = defaultdict(int)
    for n in graph.nodes.values():
        by_type[n.type] += 1
    coverage = KnowledgeCoverageReport(graph).build()
    missing = 0
    weak = 0
    if isinstance(coverage, dict):
        rows = coverage.get("rows") or coverage.get("conditions") or []
        if isinstance(rows, list):
            for r in rows:
                if not isinstance(r, dict):
                    continue
                miss = r.get("missing") or []
                if miss:
                    missing += 1
                if "papers" in miss:
                    weak += 1

    # Unused: tables with zero rows
    unused = [name for name, df in platform._tables.items() if df is not None and len(df) == 0]

    payload = {
        "generated_at": now_iso(),
        "papers": by_type.get("paper", 0),
        "conditions": by_type.get("condition", 0),
        "traits": by_type.get("trait", 0),
        "ingredients": by_type.get("ingredient", 0),
        "foods": by_type.get("food", 0),
        "products": by_type.get("product", 0),
        "nodes": len(graph.nodes),
        "edges": len(graph.edges),
        "by_type": dict(by_type),
        "conditions_missing_evidence": missing,
        "weak_evidence_heuristic": weak,
        "conflicting_evidence": "structural conflicts not auto-detected; use ScientificDiffEngine",
        "unused_tables": unused,
        "coverage": coverage if isinstance(coverage, dict) else {},
    }
    lines = [
        "# Science Observatory",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        "## Counts",
        "",
        *[f"- {k}: {payload[k]}" for k in ("papers", "conditions", "traits", "ingredients", "foods", "products", "nodes", "edges")],
        "",
        f"- Conditions with missing evidence facets: {missing}",
        f"- Unused empty tables: {len(unused)}",
        "",
        "## Unused Tables",
        "",
        *([f"- `{t}`" for t in unused] or ["_None_"]),
        "",
    ]
    write_md_json("SCIENCE_OBSERVATORY", "\n".join(lines), payload, PLATFORM_OUT, META / "metrics")
    (META / "architecture" / "SCIENCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (META / "architecture" / "KNOWLEDGE_GRAPH.md").write_text(
        f"# Knowledge Graph\n\nGenerated: `{now_iso()}`\n\n"
        f"- Nodes: {payload['nodes']}\n- Edges: {payload['edges']}\n\n"
        + "\n".join(f"- `{k}`: {v}" for k, v in sorted(by_type.items()))
        + "\n",
        encoding="utf-8",
    )
    return PLATFORM_OUT / "SCIENCE_OBSERVATORY.md"


def generate_dependency_observatory() -> Path:
    """Formula → CSV → Repository → Node → Output → API → Frontend."""
    edges: list[dict[str, str]] = []
    for fid, meta in FORMULA_REGISTRY.items():
        for table in meta.get("tables") or []:
            edges.append({"from": f"csv:{table}", "to": f"formula:{fid}", "via": "registry.tables"})
            edges.append({"from": f"formula:{fid}", "to": f"repository:{table}", "via": "DataRepository"})
        for c in meta.get("consumers") or []:
            edges.append({"from": f"formula:{fid}", "to": f"consumer:{c}", "via": "registry.consumers"})
        edges.append({"from": f"formula:{fid}", "to": "api:/api/v1/ppie/assess", "via": "AssessmentAgent"})
        edges.append({"from": f"formula:{fid}", "to": "api:/api/v1/clinical-report", "via": "AssessmentAgent"})
        edges.append({"from": "api:/api/v1/clinical-report", "to": "frontend:app.js", "via": "boot"})

    graph = FormulaGraph(default_nodes())
    for nid, node in graph.nodes.items():
        edges.append({"from": f"node:{nid}", "to": f"formula:{node.formula_id}", "via": "FormulaNode"})
        for dep in node.dependencies:
            edges.append({"from": f"node:{dep}", "to": f"node:{nid}", "via": "dependency"})

    payload = {"generated_at": now_iso(), "edge_count": len(edges), "edges": edges[:2000]}
    lines = [
        "# Dependency Observatory",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        f"Edges: {payload['edge_count']}",
        "",
        "```mermaid",
        "flowchart LR",
        "  CSV --> Repository",
        "  Repository --> FormulaNode",
        "  FormulaNode --> FormulaGraph",
        "  FormulaGraph --> AssessmentResult",
        "  AssessmentResult --> API",
        "  API --> Frontend",
        "```",
        "",
        "## Sample edges",
        "",
    ]
    for e in edges[:80]:
        lines.append(f"- `{e['from']}` → `{e['to']}` ({e['via']})")
    write_md_json("DEPENDENCY_OBSERVATORY", "\n".join(lines), payload, PLATFORM_OUT, META / "dependency_graph")
    (META / "architecture" / "DEPENDENCY_GRAPH.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return PLATFORM_OUT / "DEPENDENCY_OBSERVATORY.md"


def generate_performance_observatory(scales: list[int] | None = None) -> Path:
    """Benchmark multiple population sizes (capped for CI; full 10k+ via CLI flag)."""
    scales = scales or [1, 10]
    results = []
    for n in scales:
        # reuse collect but limit wall time for large n by sampling subset stats
        sample_n = min(n, 20) if n > 20 else n
        # For requested N, run min(N, 50) assessments and extrapolate note
        run_n = min(n, 50)
        payload = collect_runtime_sample(run_n)
        results.append(
            {
                "requested_dogs": n,
                "executed_dogs": run_n,
                "runtime_seconds": payload["total_runtime_seconds"],
                "avg_ms_per_dog": round(1000 * payload["total_runtime_seconds"] / max(run_n, 1), 3),
                "memory_peak_mb": payload["memory_peak_mb"],
                "extrapolated": run_n < n,
            }
        )
    # Static probes
    platform = default_platform()
    t0 = time.perf_counter()
    _ = list(platform._tables.keys())
    repo_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    kg = KnowledgeGraphBuilder(platform).build()
    kg_s = time.perf_counter() - t0

    payload = {
        "generated_at": now_iso(),
        "scales": results,
        "repository_probe_s": round(repo_s, 6),
        "knowledge_graph_build_s": round(kg_s, 4),
        "knowledge_graph_nodes": len(kg.nodes),
        "formula_graph_nodes": len(default_nodes()),
        "note": "Scales >50 execute a capped sample and mark extrapolated=true",
    }
    lines = [
        "# Performance Observatory",
        "",
        f"Generated: `{payload['generated_at']}`",
        "",
        "| Requested | Executed | Runtime s | Avg ms/dog | Peak MB | Extrapolated |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['requested_dogs']} | {r['executed_dogs']} | {r['runtime_seconds']} | "
            f"{r['avg_ms_per_dog']} | {r['memory_peak_mb']} | {r['extrapolated']} |"
        )
    lines += [
        "",
        f"- Repository probe: {payload['repository_probe_s']}s",
        f"- KnowledgeGraph build: {payload['knowledge_graph_build_s']}s ({payload['knowledge_graph_nodes']} nodes)",
        "",
    ]
    write_md_json("PERFORMANCE_OBSERVATORY", "\n".join(lines), payload, PLATFORM_OUT, META / "metrics")
    (META / "architecture" / "PERFORMANCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return PLATFORM_OUT / "PERFORMANCE_OBSERVATORY.md"
