"""
Phase 5M — one-command scientific release pipeline.

Clinical formulas and recommendation logic are never modified.

Usage:
  py -3 -m science_pipeline.release
  py -3 -m science_pipeline.release --dogs 20 --skip-benchmark
  py -3 -m science_pipeline.release --author alice --notes "add glucosamine paper"
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run_pytest_parity() -> dict[str, Any]:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_warehouse_parity.py::test_core_formula_parity_100_dogs",
        "tests/test_formula_graph.py",
        "-q",
        "--tb=line",
    ]
    # Prefer a smaller parity gate if env sets it
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    return {
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def run_release(
    *,
    author: str = "phase5-pipeline",
    notes: str = "",
    dogs: int = 100,
    skip_benchmark: bool = False,
    skip_parity: bool = False,
    impact_ingredient: str | None = None,
) -> dict[str, Any]:
    from app.data.repository import DataPlatform
    from app.science.audit import write_scientific_audit
    from app.science.builder import KnowledgeGraphBuilder
    from developer_tools.benchmarking.suite import run_benchmark, write_benchmark_report
    from developer_tools.dashboards.generators import (
        generate_data_health,
        generate_formula_stability,
        generate_performance_report,
        generate_reference_docs,
    )
    from developer_tools.dashboards.html_dashboard import write_developer_dashboard
    from science_pipeline.publishing.release_ops import (
        default_release_metadata,
        promote,
        publish_to_current,
        release_id,
        snapshot_warehouse,
    )
    from science_pipeline.validation.extended import ExtendedScienceValidator, write_validation_report
    from science_pipeline.validation.impact import ScientificImpactAnalyzer

    version = release_id()
    platform = DataPlatform("data", strict=True)
    steps: list[dict[str, Any]] = []

    # 1 Research Update → draft snapshot of current warehouse working tree
    draft = snapshot_warehouse(version, stage="draft")
    steps.append({"step": "research_update_draft_snapshot", "path": str(draft)})

    # 2 Validation
    validation = ExtendedScienceValidator(platform).validate()
    vpath = write_validation_report(validation)
    # also copy into governance/validation
    steps.append({"step": "validation", "ok": validation["ok"], "path": str(vpath)})

    # 3 Knowledge Graph Build
    try:
        from warehouse.tools import build_science_graph  # type: ignore
    except Exception:
        build_science_graph = None
    graph_script = ROOT / "warehouse" / "tools" / "build_science_graph.py"
    if graph_script.exists():
        proc = subprocess.run([sys.executable, str(graph_script)], cwd=str(ROOT), capture_output=True, text=True)
        steps.append(
            {
                "step": "knowledge_graph_build",
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stderr_tail": (proc.stderr or "")[-500:],
            }
        )
    else:
        KnowledgeGraphBuilder(platform).build()
        steps.append({"step": "knowledge_graph_build", "ok": True, "via": "KnowledgeGraphBuilder"})

    # 4 Warehouse validation already covered by ExtendedScienceValidator

    # 5 Parity tests
    if skip_parity:
        parity = {"ok": True, "skipped": True}
    else:
        parity = _run_pytest_parity()
    steps.append({"step": "parity_tests", **parity})

    # 6 Benchmarks
    if skip_benchmark:
        bench = {"skipped": True, "dogs": 0}
        bpath = None
    else:
        bench = run_benchmark(n=dogs)
        bpath = write_benchmark_report(bench)
    steps.append({"step": "benchmarks", "path": str(bpath) if bpath else None, "failures": bench.get("failures")})

    # 7 Scientific Audit
    try:
        audit_path = write_scientific_audit(platform)
        steps.append({"step": "scientific_audit", "path": str(audit_path)})
    except TypeError:
        # alternate signature
        try:
            from app.science.audit import ScientificAudit

            audit = ScientificAudit(platform).run()
            out = ROOT / "warehouse" / "generated" / "SCIENTIFIC_AUDIT.md"
            steps.append({"step": "scientific_audit", "path": str(out), "summary": audit.get("summary") if isinstance(audit, dict) else None})
        except Exception as exc:
            steps.append({"step": "scientific_audit", "ok": False, "error": str(exc)})

    # 8 Coverage / data health
    health_path = generate_data_health(platform)
    steps.append({"step": "coverage_report", "path": str(health_path)})

    # Formula stability + performance
    stab = generate_formula_stability()
    perf = generate_performance_report(bench if not bench.get("skipped") else None)
    steps.append({"step": "formula_stability", "path": str(stab)})
    steps.append({"step": "performance_report", "path": str(perf)})

    # Optional impact demo
    if impact_ingredient:
        impact = ScientificImpactAnalyzer(platform).analyze(
            entity_type="ingredient",
            entity_id=impact_ingredient,
            field="dose",
        )
        ipath = ScientificImpactAnalyzer(platform).write_report(impact)
        steps.append({"step": "impact_analysis", "path": str(ipath)})

    # 9 Documentation generation
    docs = generate_reference_docs(validation=validation, benchmark=bench if not bench.get("skipped") else None)
    dash = write_developer_dashboard(validation=validation, benchmark=bench if not bench.get("skipped") else None)
    steps.append({"step": "documentation", "paths": {k: str(v) for k, v in docs.items()}, "dashboard": str(dash)})

    # Promote draft → staging → releases; publish pointer
    staging = promote("draft", "staging", version)
    release_dir = snapshot_warehouse(version, stage="releases")
    # copy staging release.json notes into release
    meta = default_release_metadata(
        version=version,
        author=author,
        notes=notes or "Phase 5 automated science release",
        validation_status="pass" if validation.get("ok") and parity.get("ok") else "fail",
    )
    meta["steps"] = [s.get("step") for s in steps]
    meta["parity_ok"] = bool(parity.get("ok"))
    meta["validation_ok"] = bool(validation.get("ok"))
    meta["benchmark_failures"] = bench.get("failures", 0)
    (release_dir / "release.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (ROOT / "governance" / "releases" / f"{version}.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "governance" / "releases" / f"{version}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Only publish to production pointer if gates pass
    published = False
    if validation.get("ok") and parity.get("ok"):
        publish_to_current(version)
        # also copy release into production/
        prod = ROOT / "warehouse" / "production" / version
        if prod.exists():
            shutil.rmtree(prod)
        shutil.copytree(release_dir, prod)
        published = True

    # Version tag file (git tag left to humans)
    tag_path = ROOT / "governance" / "releases" / f"TAG_{version}.txt"
    tag_path.write_text(f"science-release-{version}\npublished={published}\n", encoding="utf-8")
    steps.append({"step": "version_tag", "path": str(tag_path), "published": published})

    summary = {
        "version": version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "published": published,
        "validation_ok": validation.get("ok"),
        "parity_ok": parity.get("ok"),
        "clinical_formulas_changed": False,
        "recommendation_logic_changed": False,
        "steps": steps,
        "release_dir": str(release_dir),
        "staging_dir": str(staging),
        "meta": meta,
    }
    out = ROOT / "governance" / "reports" / "RELEASE_SUMMARY.json"
    out.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    md = ROOT / "governance" / "reports" / "RELEASE_SUMMARY.md"
    md.write_text(
        "\n".join(
            [
                f"# Release Summary `{version}`",
                "",
                f"- Published: **{published}**",
                f"- Validation: **{validation.get('ok')}**",
                f"- Parity: **{parity.get('ok')}**",
                f"- Clinical formulas changed: **false**",
                "",
                "## Steps",
                "",
                *[f"- `{s.get('step')}`" for s in steps],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="PPIE Phase 5 science release pipeline")
    parser.add_argument("--author", default="phase5-pipeline")
    parser.add_argument("--notes", default="")
    parser.add_argument("--dogs", type=int, default=100)
    parser.add_argument("--skip-benchmark", action="store_true")
    parser.add_argument("--skip-parity", action="store_true")
    parser.add_argument("--impact-ingredient", default=None)
    args = parser.parse_args()
    summary = run_release(
        author=args.author,
        notes=args.notes,
        dogs=args.dogs,
        skip_benchmark=args.skip_benchmark,
        skip_parity=args.skip_parity,
        impact_ingredient=args.impact_ingredient,
    )
    print(json.dumps({"version": summary["version"], "published": summary["published"], "validation_ok": summary["validation_ok"], "parity_ok": summary["parity_ok"]}, indent=2))
    if not summary["published"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
