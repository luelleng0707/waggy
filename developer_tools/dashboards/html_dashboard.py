"""Internal developer dashboard (static HTML generated from live system)."""

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

ROOT = Path(__file__).resolve().parents[2]


def write_developer_dashboard(
    *,
    validation: dict[str, Any] | None = None,
    benchmark: dict[str, Any] | None = None,
    out_path: Path | None = None,
) -> Path:
    out_path = out_path or (ROOT / "developer_tools" / "dashboards" / "index.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    platform = DataPlatform("data", strict=True)
    kg = KnowledgeGraphBuilder(platform).build()
    fg = FormulaGraph(default_nodes())
    order = fg.order()
    current = ROOT / "warehouse" / "current" / "release.json"
    release_ptr = {}
    if current.exists():
        release_ptr = json.loads(current.read_text(encoding="utf-8"))

    by_type: dict[str, int] = {}
    for n in kg.nodes.values():
        by_type[n.type] = by_type.get(n.type, 0) + 1

    table_rows = "".join(
        f"<tr><td>{name}</td><td>{len(df)}</td><td>{len(df.columns)}</td></tr>"
        for name, df in sorted(platform._tables.items(), key=lambda x: -len(x[1]))[:40]
    )
    formula_rows = "".join(
        f"<tr><td><code>{nid}</code></td><td>{FORMULA_REGISTRY.get(fg.nodes[nid].formula_id, {}).get('version', fg.nodes[nid].version)}</td>"
        f"<td>{', '.join(fg.nodes[nid].dependencies)}</td></tr>"
        for nid in order
    )
    type_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(by_type.items()))

    v = validation or {}
    b = benchmark or {}
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>PPIE Developer Dashboard</title>
  <style>
    :root {{ --bg:#0f1419; --panel:#1a222c; --text:#e7eef7; --muted:#9aadc2; --accent:#3d9cf0; --ok:#3ecf8e; --bad:#f07178; }}
    body {{ margin:0; font-family: "IBM Plex Sans", "Segoe UI", sans-serif; background:linear-gradient(160deg,#0f1419,#182230 40%,#101820); color:var(--text); }}
    header {{ padding:2rem 2.5rem 1rem; }}
    h1 {{ margin:0; font-size:1.75rem; letter-spacing:-0.02em; }}
    .sub {{ color:var(--muted); margin-top:0.35rem; }}
    main {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1rem; padding:0 2.5rem 2.5rem; }}
    section {{ background:var(--panel); border:1px solid #2a3644; border-radius:12px; padding:1rem 1.1rem; }}
    h2 {{ margin:0 0 0.75rem; font-size:1rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.06em; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.85rem; }}
    td, th {{ text-align:left; padding:0.35rem 0.25rem; border-bottom:1px solid #2a3644; }}
    .pill {{ display:inline-block; padding:0.15rem 0.55rem; border-radius:999px; font-size:0.75rem; }}
    .ok {{ background:#1e3d32; color:var(--ok); }}
    .bad {{ background:#3d2226; color:var(--bad); }}
    code {{ font-family: "IBM Plex Mono", Consolas, monospace; font-size:0.8rem; }}
    ol {{ margin:0; padding-left:1.2rem; color:var(--muted); font-size:0.85rem; }}
  </style>
</head>
<body>
  <header>
    <h1>PPIE Developer Dashboard</h1>
    <p class="sub">Generated {_now()} · clinical execution path unchanged · Phase 5 governance view</p>
  </header>
  <main>
    <section>
      <h2>Validation</h2>
      <p>Status:
        <span class="pill {'ok' if v.get('ok') else 'bad'}">{'PASS' if v.get('ok') else 'FAIL / pending'}</span>
      </p>
      <p>Errors: {len(v.get('errors') or [])} · Warnings: {len(v.get('warnings') or [])}</p>
      <p>Release: <code>{release_ptr.get('active_version', '—')}</code></p>
    </section>
    <section>
      <h2>Runtime</h2>
      <p>Dogs: {b.get('dogs', '—')}</p>
      <p>Avg latency: {b.get('avg_api_latency_ms', '—')} ms</p>
      <p>Peak memory: {b.get('memory_peak_mb', '—')} MB</p>
      <p>Graph: {b.get('graph_nodes', len(kg.nodes))} nodes / {b.get('graph_edges', len(kg.edges))} edges</p>
    </section>
    <section>
      <h2>FormulaGraph order</h2>
      <ol>{''.join(f'<li><code>{n}</code></li>' for n in order)}</ol>
    </section>
    <section>
      <h2>Formula nodes</h2>
      <table><tr><th>Node</th><th>Ver</th><th>Deps</th></tr>{formula_rows}</table>
    </section>
    <section>
      <h2>Warehouse tables</h2>
      <table><tr><th>Table</th><th>Rows</th><th>Cols</th></tr>{table_rows}</table>
    </section>
    <section>
      <h2>Knowledge graph</h2>
      <table><tr><th>Type</th><th>Count</th></tr>{type_rows}</table>
    </section>
    <section>
      <h2>Science</h2>
      <p>Papers: {by_type.get('paper', 0)}</p>
      <p>Conditions: {by_type.get('condition', 0)}</p>
      <p>Ingredients: {by_type.get('ingredient', 0)}</p>
      <p>Products: {by_type.get('product', 0)}</p>
      <p>See <code>governance/reports/DATA_HEALTH.md</code></p>
    </section>
    <section>
      <h2>Release pipeline</h2>
      <p><code>py -3 -m science_pipeline.release</code></p>
      <p>Artifacts under <code>governance/reports/</code> and <code>warehouse/releases/</code></p>
    </section>
  </main>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
