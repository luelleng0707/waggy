"""
Phase Ω — one-command platform completion pipeline.

Does not change clinical formulas or recommendation logic.

Usage:
  py -3 -m ppie_platform.omega
  py -3 -m ppie_platform.omega --quick
  py -3 -m ppie_platform.omega --fuzz 20 --population 50
  py -3 -m ppie_platform.omega --rollback 2026.07.20
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_omega(
    *,
    quick: bool = False,
    fuzz_n: int = 30,
    population: int = 50,
    perf_scales: list[int] | None = None,
    skip_parity: bool = False,
    rollback: str | None = None,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []

    if rollback:
        from operations.lifecycle import rollback_to

        result = rollback_to(rollback)
        steps.append({"step": "rollback", **result})
        return {"steps": steps, "rollback": result}

    # Observatories
    from ppie_platform.observability.observatories import (
        generate_dependency_observatory,
        generate_formula_observatory,
        generate_performance_observatory,
        generate_science_observatory,
        generate_system_runtime,
    )

    n_runtime = 2 if quick else 5
    steps.append({"step": "system_runtime", "path": str(generate_system_runtime(n_runtime))})
    steps.append({"step": "formula_observatory", "path": str(generate_formula_observatory(n_runtime))})
    steps.append({"step": "science_observatory", "path": str(generate_science_observatory())})
    steps.append({"step": "dependency_observatory", "path": str(generate_dependency_observatory())})
    scales = perf_scales or ([1, 10] if quick else [1, 10, 100])
    steps.append({"step": "performance_observatory", "path": str(generate_performance_observatory(scales))})

    # Quality
    from quality.suites import run_failure_simulation, run_fuzz, run_mutation_tests, run_synthetic_population

    steps.append({"step": "failure_simulation", "path": str(run_failure_simulation())})
    steps.append({"step": "fuzz", "path": str(run_fuzz(n=fuzz_n if not quick else min(fuzz_n, 15)))})
    steps.append({"step": "synthetic_population", "path": str(run_synthetic_population(n=population if not quick else min(population, 20)))})
    steps.append({"step": "mutation", "path": str(run_mutation_tests())})

    # Security
    from ppie_platform.security.audit import run_security_audit

    steps.append({"step": "security_audit", "path": str(run_security_audit())})

    # Living docs + API stability + SDKs
    from ppie_platform.lifecycle.docs import generate_api_stability, generate_living_architecture
    from ppie_platform.sdk.generate import generate_sdks
    from developer_tools.dashboards.generators import generate_reference_docs

    steps.append({"step": "api_stability", "path": str(generate_api_stability())})
    paths = generate_living_architecture()
    steps.append({"step": "living_architecture", "paths": {k: str(v) for k, v in paths.items()}})
    try:
        generate_reference_docs()
        steps.append({"step": "docs_reference", "ok": True})
    except Exception as exc:
        steps.append({"step": "docs_reference", "ok": False, "error": str(exc)})
    steps.append({"step": "sdk", "paths": generate_sdks()})

    # Snapshot
    from operations.lifecycle import create_snapshot

    version = datetime.now(timezone.utc).strftime("%Y.%m.%d")
    snap = create_snapshot(version, label="omega")
    steps.append({"step": "snapshot", "path": str(snap)})

    # Dashboard
    from ppie_platform.dashboard.build import write_platform_dashboard

    steps.append({"step": "dashboard", "path": str(write_platform_dashboard())})

    # Optional science release + parity
    if not quick:
        cmd = [sys.executable, "-m", "science_pipeline.release", "--dogs", "5", "--skip-benchmark"]
        if skip_parity:
            cmd.append("--skip-parity")
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        steps.append(
            {
                "step": "science_release",
                "ok": proc.returncode == 0,
                "stdout_tail": (proc.stdout or "")[-500:],
            }
        )
    else:
        steps.append({"step": "science_release", "skipped": True})

    if not skip_parity and not quick:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_warehouse_parity.py::test_core_formula_parity_100_dogs", "-q", "--tb=line"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        steps.append({"step": "parity", "ok": proc.returncode == 0})

    # Deployment artifact note (Docker optional)
    deploy_dir = ROOT / "ppie_platform" / "deployment"
    deploy_dir.mkdir(parents=True, exist_ok=True)
    (deploy_dir / "ARTIFACT.md").write_text(
        f"# Production Artifact\n\nGenerated: `{datetime.now(timezone.utc).isoformat()}`\n\n"
        "Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`\n"
        "See `docs/RAILWAY_DEPLOYMENT.md`, `Procfile`, `railway.json`.\n"
        "Docker: use Nixpacks/Railway or wrap the same start command.\n",
        encoding="utf-8",
    )
    steps.append({"step": "deployment_artifact", "path": str(deploy_dir / "ARTIFACT.md")})

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": version,
        "clinical_formulas_changed": False,
        "core_architecture_frozen": True,
        "steps": steps,
    }
    out = ROOT / "meta" / "metrics" / "OMEGA_SUMMARY.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    (ROOT / "meta" / "architecture" / "OMEGA_SUMMARY.md").write_text(
        "# Omega Pipeline Summary\n\n"
        + "\n".join(f"- `{s.get('step')}`" for s in steps)
        + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="PPIE Phase Ω platform pipeline")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--fuzz", type=int, default=30)
    p.add_argument("--population", type=int, default=50)
    p.add_argument("--skip-parity", action="store_true")
    p.add_argument("--rollback", default=None, help="Rollback warehouse pointer to version")
    p.add_argument("--observatory", action="store_true", help="Only run observatories")
    args = p.parse_args()

    if args.observatory:
        from ppie_platform.observability.observatories import (
            generate_dependency_observatory,
            generate_formula_observatory,
            generate_science_observatory,
            generate_system_runtime,
        )

        generate_system_runtime(2)
        generate_formula_observatory(2)
        generate_science_observatory()
        generate_dependency_observatory()
        print(json.dumps({"ok": True, "mode": "observatory"}, indent=2))
        return

    summary = run_omega(
        quick=args.quick,
        fuzz_n=args.fuzz,
        population=args.population,
        skip_parity=args.skip_parity,
        rollback=args.rollback,
    )
    print(json.dumps({"version": summary.get("version"), "steps": len(summary.get("steps") or []), "frozen": True}, indent=2))


if __name__ == "__main__":
    main()
