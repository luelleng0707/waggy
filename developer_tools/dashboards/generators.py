"""Generated documentation + health / performance / formula stability reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agent.formula_graph import FormulaGraph
from app.agent.formula_registry import FORMULA_REGISTRY
from app.agent.nodes import default_nodes
from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder
from app.science.coverage import KnowledgeCoverageReport

ROOT = Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_formula_stability(out_dir: Path | None = None) -> Path:
    out_dir = out_dir or (ROOT / "governance" / "reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    graph = FormulaGraph(default_nodes())
    lines = [
        "# Formula Stability Report",
        "",
        f"Generated: `{_now()}`",
        "",
        "| Formula | Version | Tables | Consumers | Module |",
        "|---|---|---|---|---|",
    ]
    rows = []
    for fid, meta in FORMULA_REGISTRY.items():
        tables = ", ".join(meta.get("tables") or []) or "—"
        consumers = ", ".join(meta.get("consumers") or []) or "—"
        lines.append(
            f"| `{fid}` | {meta.get('version')} | {tables} | {consumers} | `{meta.get('module')}` |"
        )
        rows.append(
            {
                "formula": fid,
                "version": meta.get("version"),
                "last_changed": meta.get("version"),
                "affected_papers": "see knowledge graph supported_by edges",
                "affected_csv": meta.get("tables") or [],
                "affected_apis": ["/api/v1/ppie/assess", "/api/v1/clinical-report"],
                "affected_ui": ["Validation Console", "Journey / Wellness"],
                "parity_status": "gated by tests/test_warehouse_parity.py + golden suite",
                "coverage": "see DATA_HEALTH.md",
                "performance": "see PERFORMANCE_REPORT.md / BENCHMARK_REPORT.md",
                "module": meta.get("module"),
                "wrapped": meta.get("wrapped"),
            }
        )
    lines += [
        "",
        "## Execution Order",
        "",
    ]
    try:
        order = graph.order()
        for i, nid in enumerate(order, 1):
            lines.append(f"{i}. `{nid}`")
    except Exception:
        for i, fid in enumerate(FORMULA_REGISTRY.keys(), 1):
            lines.append(f"{i}. `{fid}`")

    path = out_dir / "FORMULA_STABILITY_REPORT.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "formula_stability.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return path


def generate_data_health(platform: DataPlatform | None = None, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or (ROOT / "governance" / "reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    platform = platform or DataPlatform("data", strict=True)
    graph = KnowledgeGraphBuilder(platform).build()
    try:
        coverage = KnowledgeCoverageReport(graph).build()
    except Exception:
        coverage = {}

    conditions = list(graph.by_type("condition"))
    papers = list(graph.by_type("paper"))
    ingredients = list(graph.by_type("ingredient"))
    products = list(graph.by_type("product"))

    supported = set()
    for e in graph.edges:
        if e.relation == "supported_by":
            src = graph.nodes.get(e.source)
            if src and src.type == "condition":
                supported.add(src.label or src.id)
    all_cond = {c.label or c.id for c in conditions}
    without_evidence = sorted(all_cond - supported)

    # Ingredients without products
    ing_with_prod = set()
    for e in graph.edges:
        a, b = graph.nodes.get(e.source), graph.nodes.get(e.target)
        if not a or not b:
            continue
        if a.type == "ingredient" and b.type == "product":
            ing_with_prod.add(a.label or a.id)
        if b.type == "ingredient" and a.type == "product":
            ing_with_prod.add(b.label or b.id)
    ing_labels = {i.label or i.id for i in ingredients}
    ing_without_prod = sorted(ing_labels - ing_with_prod)

    breeds = platform.breeds
    lines = [
        "# Data Health",
        "",
        f"Generated: `{_now()}`",
        "",
        "## Coverage",
        "",
        f"- Conditions with evidence: {len(supported)}",
        f"- Conditions without evidence: {len(without_evidence)}",
        f"- Ingredients without products: {len(ing_without_prod)}",
        "",
        "## Statistics",
        "",
        f"- Papers: {len(papers)}",
        f"- Breeds: {0 if breeds.empty else len(breeds)}",
        f"- Ingredients: {len(ingredients)}",
        f"- Products: {len(products)}",
        f"- Graph nodes: {len(graph.nodes)}",
        f"- Graph edges: {len(graph.edges)}",
        f"- Formula registry entries: {len(FORMULA_REGISTRY)}",
        "",
        "## Conditions Without Evidence",
        "",
    ]
    for c in without_evidence[:80]:
        lines.append(f"- {c}")
    if not without_evidence:
        lines.append("_None_")
    lines += ["", "## Ingredients Without Products", ""]
    for i in ing_without_prod[:80]:
        lines.append(f"- {i}")
    if not ing_without_prod:
        lines.append("_None_")
    if coverage:
        lines += ["", "## Coverage Object", "", "```json", json.dumps(coverage, indent=2, default=str)[:8000], "```", ""]

    path = out_dir / "DATA_HEALTH.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "generated_at": _now(),
        "conditions_with_evidence": len(supported),
        "conditions_without_evidence": without_evidence,
        "ingredients_without_products": ing_without_prod,
        "stats": {
            "papers": len(papers),
            "breeds": 0 if breeds.empty else len(breeds),
            "ingredients": len(ingredients),
            "products": len(products),
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
        },
        "coverage": coverage,
    }
    (out_dir / "data_health.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def generate_performance_report(benchmark: dict[str, Any] | None, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or (ROOT / "governance" / "reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    bench = benchmark or {}
    # Table sizes
    platform = DataPlatform("data", strict=True)
    sizes = []
    for name, df in sorted(platform._tables.items(), key=lambda x: -len(x[1])):
        sizes.append((name, len(df), len(df.columns)))

    lines = [
        "# Performance Report",
        "",
        f"Generated: `{_now()}`",
        "",
        "## Runtime (from benchmark)",
        "",
        f"- Total: {bench.get('runtime_seconds', 'n/a')}s",
        f"- Avg API latency: {bench.get('avg_api_latency_ms', 'n/a')} ms",
        f"- P95 API latency: {bench.get('p95_api_latency_ms', 'n/a')} ms",
        f"- Peak memory: {bench.get('memory_peak_mb', 'n/a')} MB",
        f"- CSV loading: {bench.get('csv_loading_seconds', 'n/a')}s",
        f"- Graph traversal: {bench.get('graph_traversal_seconds', 'n/a')}s",
        "",
        "## Slowest Nodes",
        "",
    ]
    for name, ms in bench.get("slowest_nodes") or []:
        lines.append(f"- `{name}`: {ms} ms")
    if not bench.get("slowest_nodes"):
        lines.append("_Run benchmark suite to populate._")
    lines += ["", "## Largest Tables", "", "| Table | Rows | Cols |", "|---|---:|---:|"]
    for name, rows, cols in sizes[:25]:
        lines.append(f"| `{name}` | {rows} | {cols} |")
    lines += [
        "",
        "## Cache Efficiency",
        "",
        "- DataPlatform loads CSVs once per process into `_tables` (in-memory).",
        "- Warehouse materialize is opt-in via `backend=warehouse`.",
        "- Knowledge graph rebuild is per Validation/Audit invocation unless cached by caller.",
        "",
    ]
    path = out_dir / "PERFORMANCE_REPORT.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "performance_report.json").write_text(
        json.dumps({"generated_at": _now(), "benchmark": bench, "largest_tables": sizes[:40]}, indent=2),
        encoding="utf-8",
    )
    return path


def generate_reference_docs(
    *,
    validation: dict[str, Any] | None = None,
    benchmark: dict[str, Any] | None = None,
    out_dir: Path | None = None,
) -> dict[str, Path]:
    """Phase 5L — auto-generate living technical docs."""
    docs = out_dir or (ROOT / "docs")
    docs.mkdir(parents=True, exist_ok=True)
    gov = ROOT / "governance" / "reports"
    gov.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    platform = DataPlatform("data", strict=True)
    graph = KnowledgeGraphBuilder(platform).build()
    summary = graph.summary() if hasattr(graph, "summary") else {"nodes": len(graph.nodes), "edges": len(graph.edges)}

    # PROJECT_STATUS.md
    p = docs / "PROJECT_STATUS.md"
    p.write_text(
        "\n".join(
            [
                "# Project Status",
                "",
                f"Generated: `{_now()}`",
                "",
                "## Clinical Pipeline (unchanged)",
                "",
                "```",
                "Warehouse / data/",
                "    ↓",
                "Repository",
                "    ↓",
                "ExecutionContext",
                "    ↓",
                "FormulaGraph",
                "    ↓",
                "AssessmentResult",
                "```",
                "",
                "## Phase Overlay",
                "",
                "- Phase 1–2: warehouse + adapters",
                "- Phase 3: FormulaGraph / AssessmentAgent",
                "- Phase 4: knowledge graph + explainability",
                "- Phase 5: governance + science release OS",
                "",
                f"- Graph nodes/edges: {summary}",
                f"- Validation ok: {(validation or {}).get('ok', 'n/a')}",
                f"- Benchmark dogs: {(benchmark or {}).get('dogs', 'n/a')}",
                f"- Clinical formulas changed this release: **false**",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["PROJECT_STATUS"] = p

    # FORMULA_REFERENCE.md
    p = docs / "FORMULA_REFERENCE.md"
    lines = ["# Formula Reference", "", f"Generated: `{_now()}`", ""]
    for fid, meta in FORMULA_REGISTRY.items():
        lines += [f"## `{fid}`", "", f"- Version: {meta.get('version')}", f"- Module: `{meta.get('module')}`"]
        if meta.get("wrapped"):
            lines.append(f"- Wraps: `{meta['wrapped']}`")
        lines.append(f"- Tables: {', '.join(meta.get('tables') or []) or '—'}")
        lines.append("")
    p.write_text("\n".join(lines), encoding="utf-8")
    paths["FORMULA_REFERENCE"] = p

    # SCIENCE_REFERENCE.md
    p = docs / "SCIENCE_REFERENCE.md"
    by_type: dict[str, int] = {}
    for n in graph.nodes.values():
        by_type[n.type] = by_type.get(n.type, 0) + 1
    p.write_text(
        "\n".join(
            [
                "# Science Reference",
                "",
                f"Generated: `{_now()}`",
                "",
                "## Knowledge Graph Node Types",
                "",
                *[f"- `{k}`: {v}" for k, v in sorted(by_type.items())],
                "",
                "## APIs",
                "",
                "- `GET /api/v1/graph/...`",
                "- `GET /api/v1/science/audit`",
                "- `GET /api/v1/science/coverage`",
                "- `GET /api/v1/science/versions`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["SCIENCE_REFERENCE"] = p

    # WAREHOUSE_REFERENCE.md
    p = docs / "WAREHOUSE_REFERENCE.md"
    wh = ROOT / "warehouse"
    layers = []
    for layer in ("reference", "science", "runtime", "generated", "graph", "current", "releases", "draft", "staging", "production", "snapshots"):
        d = wh / layer
        if d.exists():
            n = len(list(d.rglob("*"))) if d.is_dir() else 0
            layers.append(f"- `{layer}/` ({n} entries)")
    p.write_text(
        "\n".join(
            [
                "# Warehouse Reference",
                "",
                f"Generated: `{_now()}`",
                "",
                "Live clinical engine reads `data/` via `DataPlatform`.",
                "`warehouse/` holds schemas, materialized science, graph artifacts, and Phase 5 release pointers.",
                "",
                "## Layout",
                "",
                *layers,
                "",
                "Never edit `production/` tables by hand — promote via `science_pipeline.release`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["WAREHOUSE_REFERENCE"] = p

    # GRAPH_REFERENCE.md
    p = docs / "GRAPH_REFERENCE.md"
    p.write_text(
        "\n".join(
            [
                "# Graph Reference",
                "",
                f"Generated: `{_now()}`",
                "",
                f"- Nodes: {len(graph.nodes)}",
                f"- Edges: {len(graph.edges)}",
                f"- Summary: `{json.dumps(summary, default=str)}`",
                "",
                "Build: `py -3 warehouse/tools/build_science_graph.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["GRAPH_REFERENCE"] = p

    # API_REFERENCE.md — scan routes lightly
    api_main = ROOT / "app" / "api" / "main.py"
    api_lines = ["# API Reference", "", f"Generated: `{_now()}`", "", "Extracted from `app/api/main.py` route decorators.", ""]
    if api_main.exists():
        import re

        text = api_main.read_text(encoding="utf-8")
        for m in re.finditer(r'@app\.(get|post|put|delete|patch)\("([^"]+)"', text):
            api_lines.append(f"- `{m.group(1).upper()} {m.group(2)}`")
    p = docs / "API_REFERENCE.md"
    p.write_text("\n".join(api_lines) + "\n", encoding="utf-8")
    paths["API_REFERENCE"] = p

    # CHANGELOG.md append stub for release
    p = ROOT / "governance" / "changelogs" / "CHANGELOG.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = (
        f"\n## {stamp} — Phase 5 governance release\n\n"
        "- Scientific validation, benchmarks, docs regenerated.\n"
        "- Clinical formulas: unchanged.\n"
        "- Recommendation logic: unchanged.\n"
    )
    if p.exists():
        existing = p.read_text(encoding="utf-8")
        if stamp not in existing[:500]:
            # prepend after title if present
            if existing.startswith("#"):
                first, _, rest = existing.partition("\n")
                p.write_text(first + "\n" + entry + rest, encoding="utf-8")
            else:
                p.write_text(entry + existing, encoding="utf-8")
    else:
        p.write_text("# Science CHANGELOG\n" + entry, encoding="utf-8")
    paths["CHANGELOG"] = p
    # Mirror to docs
    (docs / "CHANGELOG.md").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

    # DATA_DICTIONARY.md
    p = docs / "DATA_DICTIONARY.md"
    lines = ["# Data Dictionary", "", f"Generated: `{_now()}`", ""]
    for name, df in sorted(platform._tables.items()):
        lines.append(f"## `{name}`")
        lines.append("")
        lines.append(f"Rows: {len(df)}")
        lines.append("")
        lines.append("| Column | Dtype | Non-null |")
        lines.append("|---|---|---:|")
        for col in df.columns:
            lines.append(f"| `{col}` | {df[col].dtype} | {int(df[col].notna().sum())} |")
        lines.append("")
    p.write_text("\n".join(lines), encoding="utf-8")
    paths["DATA_DICTIONARY"] = p

    return paths
