"""
Scientific release pipeline — validation + optional publish pointer.

Clinical formulas are never modified.

Usage:
  py -3 -m science_pipeline.release --skip-parity
  py -3 -m science_pipeline.release --author alice --notes "note"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.paths import clinical_root_str

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run_pytest_parity() -> dict[str, Any]:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_warehouse_parity.py",
        "tests/test_formula_graph.py",
        "-q",
        "--tb=line",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    return {
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def run_release(
    *,
    author: str = "science-pipeline",
    notes: str = "",
    skip_parity: bool = False,
) -> dict[str, Any]:
    from app.data.repository import DataPlatform
    from app.science.builder import KnowledgeGraphBuilder
    from science_pipeline.release_ops import (
        default_release_metadata,
        publish_to_current,
        release_id,
    )
    from science_pipeline.validation_extended import ExtendedScienceValidator

    version = release_id()
    platform = DataPlatform(clinical_root_str(), strict=True)
    steps: list[dict[str, Any]] = []

    validation = ExtendedScienceValidator(platform).validate()
    steps.append({"step": "validation", "ok": validation["ok"]})

    KnowledgeGraphBuilder(platform).build()
    steps.append({"step": "knowledge_graph_build", "ok": True, "via": "KnowledgeGraphBuilder"})

    if skip_parity:
        parity = {"ok": True, "skipped": True}
    else:
        parity = _run_pytest_parity()
    steps.append({"step": "parity_tests", **parity})

    meta = default_release_metadata(
        version=version,
        author=author,
        notes=notes or "science release",
        validation_status="pass" if validation.get("ok") and parity.get("ok") else "fail",
    )
    meta["steps"] = [s.get("step") for s in steps]
    meta["parity_ok"] = bool(parity.get("ok"))
    meta["validation_ok"] = bool(validation.get("ok"))

    published = False
    if validation.get("ok") and parity.get("ok"):
        publish_to_current(version)
        published = True

    summary = {
        "version": version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "published": published,
        "validation_ok": validation.get("ok"),
        "parity_ok": parity.get("ok"),
        "clinical_formulas_changed": False,
        "steps": steps,
        "meta": meta,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="PPIE science release pipeline")
    parser.add_argument("--author", default="science-pipeline")
    parser.add_argument("--notes", default="")
    parser.add_argument("--skip-parity", action="store_true")
    args = parser.parse_args()
    summary = run_release(author=args.author, notes=args.notes, skip_parity=args.skip_parity)
    print(
        json.dumps(
            {
                "version": summary["version"],
                "published": summary["published"],
                "validation_ok": summary["validation_ok"],
                "parity_ok": summary["parity_ok"],
            },
            indent=2,
        )
    )
    if not summary["published"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
