"""ΩS — single-pane platform dashboard (static HTML)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ppie_platform" / "dashboard" / "index.html"


def _j(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def write_platform_dashboard() -> Path:
    from ppie_platform.status import (
        platform_audit,
        platform_coverage,
        platform_formulas,
        platform_performance,
        platform_release,
        platform_science,
        platform_status,
    )

    status = platform_status()
    formulas = platform_formulas()
    science = platform_science().get("data") or {}
    perf = platform_performance()
    cov = platform_coverage()
    release = platform_release()
    audit = platform_audit()
    runtime = _j(ROOT / "ppie_platform" / "observability" / "reports" / "SYSTEM_RUNTIME.json")

    sec_ok = (audit.get("security") or {}).get("ok")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>PPIE Platform Dashboard — Omega</title>
<style>
:root {{ --bg:#0c1218; --card:#15202b; --text:#e8eef5; --muted:#8fa3b8; --accent:#4db6ac; --line:#243040; }}
body {{ margin:0; font-family:"Source Sans 3","Segoe UI",sans-serif; background:
  radial-gradient(1200px 600px at 10% -10%, #1a3340 0%, transparent 55%),
  linear-gradient(165deg, #0c1218, #121a22 50%, #0e151c); color:var(--text); }}
header {{ padding:2rem 2.25rem 1rem; }}
h1 {{ margin:0; font-size:1.85rem; letter-spacing:-0.03em; }}
.sub {{ color:var(--muted); margin-top:.4rem; }}
main {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1rem; padding:0 2.25rem 2.5rem; }}
section {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:1rem 1.15rem; }}
h2 {{ margin:0 0 .7rem; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; color:var(--accent); }}
ul {{ margin:0; padding-left:1.1rem; color:var(--muted); font-size:.9rem; }}
code {{ font-family:"IBM Plex Mono",Consolas,monospace; font-size:.8rem; color:#c5e0dc; }}
.ok {{ color:#7dcea0; }} .bad {{ color:#f1948a; }}
</style>
</head>
<body>
<header>
  <h1>PPIE Platform Dashboard</h1>
  <p class="sub">Phase Ω · generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · core architecture frozen · clinical path unchanged</p>
</header>
<main>
  <section>
    <h2>Platform Health</h2>
    <ul>
      <li>Omega: <code>{status.get('omega_version')}</code></li>
      <li>Algorithm: <code>{status.get('algorithm_version')}</code></li>
      <li>Release: <code>{status.get('active_release') or '—'}</code></li>
      <li>Frozen: <span class="ok">{status.get('core_architecture_frozen')}</span></li>
    </ul>
  </section>
  <section>
    <h2>FormulaGraph</h2>
    <ul>
      <li>Formulas: {len(formulas.get('formulas') or [])}</li>
      <li>Nodes: {len(formulas.get('nodes') or [])}</li>
    </ul>
  </section>
  <section>
    <h2>Knowledge Graph / Science</h2>
    <ul>
      <li>Papers: {science.get('papers', '—')}</li>
      <li>Conditions: {science.get('conditions', '—')}</li>
      <li>Nodes/Edges: {science.get('nodes', '—')} / {science.get('edges', '—')}</li>
    </ul>
  </section>
  <section>
    <h2>Performance</h2>
    <ul>
      <li>Runtime peak MB: {(runtime or {}).get('memory_peak_mb', '—')}</li>
      <li>Sample dogs: {(runtime or {}).get('sample_dogs', '—')}</li>
      <li>See <code>PERFORMANCE_OBSERVATORY.md</code></li>
    </ul>
  </section>
  <section>
    <h2>Coverage / Validation</h2>
    <ul>
      <li>Data health present: {bool(cov.get('data_health'))}</li>
      <li>Security audit: <span class="{'ok' if sec_ok else 'bad'}">{sec_ok}</span></li>
    </ul>
  </section>
  <section>
    <h2>Releases</h2>
    <ul>
      <li>Current: <code>{(release.get('current') or {}).get('active_version', '—')}</code></li>
      <li>Rollback: <code>py -3 -m ppie_platform.omega --rollback VERSION</code></li>
    </ul>
  </section>
  <section>
    <h2>Telemetry / Runtime</h2>
    <ul>
      <li>Warnings: {(runtime or {}).get('warnings', '—')}</li>
      <li>Errors: {(runtime or {}).get('errors', '—')}</li>
      <li>APIs: <code>/api/v1/platform/*</code></li>
    </ul>
  </section>
  <section>
    <h2>Dependencies</h2>
    <ul>
      <li><code>meta/dependency_graph/</code></li>
      <li><code>meta/architecture/DEPENDENCY_GRAPH.md</code></li>
    </ul>
  </section>
</main>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    return OUT
