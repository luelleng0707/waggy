"""
PPIE golden regression suite.

Compares live Python output against frozen golden fixtures under:
  tests/parity/<profile_id>/golden_response.json

Usage:
  py -3 tools/parity_suite.py              # run against goldens
  py -3 tools/parity_suite.py --repeat 3
  py -3 tools/parity_suite.py --freeze     # refresh goldens from live Python (intentional)
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from parity_harness import (  # noqa: E402
    TOLERANCE,
    age_years_from_birthday,
    diff,
    http_json,
)

SUITE_DIR = ROOT / "tests" / "parity"

PROFILES: list[dict[str, Any]] = [
    {
        "id": "dolly_golden_x_labrador",
        "label": "Golden Retriever × Labrador (Dolly golden)",
        "name": "Dolly",
        "breeds": ["Golden Retriever", "Labrador Retriever"],
        "birthday": "2021-03-15",
        "weight_kg": 30.0,
        "sex": "Female",
        "activity_level": "High",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
    },
    {
        "id": "chihuahua",
        "label": "Chihuahua (toy)",
        "name": "Peanut",
        "breeds": ["Chihuahua"],
        "birthday": "2019-06-01",
        "weight_kg": 2.5,
        "sex": "Male",
        "activity_level": "Moderate",
        "current_environment": "Indoor Temperate",
        "observed_conditions": [],
    },
    {
        "id": "german_shepherd_dog",
        "label": "German Shepherd Dog",
        "name": "Rex",
        "breeds": ["German Shepherd Dog"],
        "birthday": "2018-04-12",
        "weight_kg": 35.0,
        "sex": "Male",
        "activity_level": "High",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": [],
    },
    {
        "id": "french_bulldog",
        "label": "French Bulldog",
        "name": "Baguette",
        "breeds": ["French Bulldog"],
        "birthday": "2020-09-20",
        "weight_kg": 12.0,
        "sex": "Female",
        "activity_level": "Low",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
    },
    {
        "id": "border_collie",
        "label": "Border Collie",
        "name": "Scout",
        "breeds": ["Border Collie"],
        "birthday": "2017-02-08",
        "weight_kg": 18.0,
        "sex": "Female",
        "activity_level": "Extreme",
        "current_environment": "Rural Cool",
        "observed_conditions": [],
    },
    {
        "id": "great_pyrenees_giant",
        "label": "Great Pyrenees (giant stand-in; Great Dane not in BREEDS.csv)",
        "name": "Atlas",
        "breeds": ["Great Pyrenees"],
        "birthday": "2016-11-30",
        "weight_kg": 50.0,
        "sex": "Male",
        "activity_level": "Moderate",
        "current_environment": "Cold Mountain",
        "observed_conditions": [],
    },
    {
        "id": "mixed_chow_x_rural",
        "label": "Mixed Breed (Chow Chow × Chinese Rural Dog)",
        "name": "Mochi",
        "breeds": ["Chow Chow", "Chinese Rural Dog"],
        "birthday": "2019-01-15",
        "weight_kg": 22.0,
        "sex": "Male",
        "activity_level": "Moderate",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
    },
    {
        "id": "senior_labrador",
        "label": "Senior Labrador Retriever",
        "name": "OldBoy",
        "breeds": ["Labrador Retriever"],
        "birthday": "2014-03-01",
        "weight_kg": 32.0,
        "sex": "Male",
        "activity_level": "Low",
        "current_environment": "Temperate Indoor",
        "observed_conditions": [],
    },
    {
        "id": "puppy_golden",
        "label": "Puppy Golden Retriever",
        "name": "Pip",
        "breeds": ["Golden Retriever"],
        "birthday": "2025-12-01",
        "weight_kg": 8.0,
        "sex": "Female",
        "activity_level": "High",
        "current_environment": "Temperate Indoor",
        "observed_conditions": [],
    },
    {
        "id": "overweight_labrador",
        "label": "Overweight Labrador Retriever (obese/high BCS)",
        "name": "Butter",
        "breeds": ["Labrador Retriever"],
        "birthday": "2018-07-04",
        "weight_kg": 42.0,
        "sex": "Female",
        "activity_level": "Low",
        "current_environment": "Shanghai Summer",
        "bcs": 8,
        "observed_conditions": [],
    },
]


def py_payload(p: dict[str, Any]) -> dict[str, Any]:
    breeds = p["breeds"]
    body: dict[str, Any] = {
        "name": p["name"],
        "primary_breed": breeds[0],
        "secondary_breed": breeds[1] if len(breeds) > 1 else None,
        "breed_split_pct": 50.0 if len(breeds) > 1 else 100.0,
        "age_years": age_years_from_birthday(p["birthday"]),
        "weight_kg": p["weight_kg"],
        "current_environment": p["current_environment"],
        "activity_level": p["activity_level"],
        "sex": p["sex"],
        "gender": p["sex"],
        "birthday": p["birthday"],
        "height_cm": None,
        "observed_conditions": p.get("observed_conditions") or [],
    }
    if p.get("bcs") is not None:
        body["bcs"] = p["bcs"]
    return body


def analyze_payload(p: dict[str, Any]) -> dict[str, Any]:
    """Node-compatible /api/v1/analyze body (also accepted by Python)."""
    body: dict[str, Any] = {
        "name": p["name"],
        "pet_name": p["name"],
        "breeds": p["breeds"],
        "birthday": p["birthday"],
        "weight": p["weight_kg"],
        "sex": p["sex"],
        "activity_level": p["activity_level"],
        "current_environment": p["current_environment"],
        "observed_conditions": p.get("observed_conditions") or [],
    }
    if p.get("bcs") is not None:
        body["bcs"] = p["bcs"]
    return body


def ensure_python_health() -> None:
    code, body = http_json("GET", "http://127.0.0.1:8000/health")
    print(f"Python /health: {code} {body}")
    if code != 200:
        raise SystemExit("Python API is not healthy. Start: py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000")


def run_profile(p: dict[str, Any], *, freeze: bool = False) -> dict[str, Any]:
    out_dir = SUITE_DIR / p["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    golden_path = out_dir / "golden_response.json"

    # Prefer v1 analyze contract (production path); fall back to v2 evaluate.
    py_code, py_body = http_json(
        "POST",
        "http://127.0.0.1:8000/api/v1/analyze",
        analyze_payload(p),
        headers={"x-api-key": "wagtopia-demo-key"},
    )
    if py_code != 200:
        py_code, py_body = http_json(
            "POST",
            "http://127.0.0.1:8000/api/v2/wellness/evaluate",
            py_payload(p),
        )

    result: dict[str, Any] = {
        "id": p["id"],
        "label": p["label"],
        "py_status": py_code,
        "diff_count": None,
        "age_years": age_years_from_birthday(p["birthday"]),
        "ok": False,
    }

    if py_code != 200:
        (out_dir / "py_error.json").write_text(json.dumps(py_body, indent=2, default=str), encoding="utf-8")
        result["error"] = f"Python evaluate failed: {py_code}"
        return result

    (out_dir / "py_response.json").write_text(json.dumps(py_body, indent=2, default=str), encoding="utf-8")

    if freeze or not golden_path.exists():
        # Seed golden from locked py_response if migrating from Node parity era
        legacy_py = out_dir / "py_response.json"
        if not freeze and legacy_py.exists() and not golden_path.exists():
            shutil.copyfile(legacy_py, golden_path)
        else:
            golden_path.write_text(json.dumps(py_body, indent=2, default=str), encoding="utf-8")
        if freeze:
            result["diff_count"] = 0
            result["ok"] = True
            result["frozen"] = True
            return result

    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    diffs: list[dict[str, Any]] = []
    diff("", golden, py_body, diffs)

    (out_dir / "parity_diff.json").write_text(
        json.dumps(
            {
                "profile_id": p["id"],
                "label": p["label"],
                "mode": "golden_vs_python",
                "diff_count": len(diffs),
                "tolerance": TOLERANCE,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "diffs": diffs[:200],
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    result["diff_count"] = len(diffs)
    result["ok"] = len(diffs) == 0
    result["py_wellness_score"] = py_body.get("wellness_score")
    if diffs:
        result["sample_diffs"] = diffs[:10]
    return result


def freeze_all() -> None:
    """Copy existing py_response.json → golden_response.json, or refresh from live API."""
    ensure_python_health()
    for p in PROFILES:
        print(f"Freezing {p['id']}...")
        r = run_profile(p, freeze=True)
        print(f"  {'OK' if r.get('ok') else 'FAIL'} {r.get('error', '')}")


def run_suite() -> list[dict[str, Any]]:
    ensure_python_health()
    SUITE_DIR.mkdir(parents=True, exist_ok=True)
    # Ensure goldens exist (seed once from current py_response if present)
    for p in PROFILES:
        out_dir = SUITE_DIR / p["id"]
        golden = out_dir / "golden_response.json"
        legacy = out_dir / "py_response.json"
        if not golden.exists() and legacy.exists():
            shutil.copyfile(legacy, golden)
            print(f"Seeded golden from py_response: {p['id']}")

    results = []
    for p in PROFILES:
        print(f"\n=== {p['id']} ({p['label']}) ===")
        r = run_profile(p)
        results.append(r)
        status = "PASS" if r.get("ok") else "FAIL"
        print(f"  {status} diff_count={r.get('diff_count')} py={r.get('py_status')}")
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
        if r.get("sample_diffs"):
            for d in r["sample_diffs"][:5]:
                print(f"  - {d.get('path')} [{d.get('kind')}]")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="PPIE golden regression suite")
    parser.add_argument("--repeat", type=int, default=1, help="Consecutive full-suite runs")
    parser.add_argument("--freeze", action="store_true", help="Refresh golden fixtures from live Python")
    args = parser.parse_args()

    if args.freeze:
        freeze_all()
        print("\nGolden fixtures frozen from live Python.")
        return

    all_runs = []
    for run_idx in range(1, args.repeat + 1):
        print(f"\n######## SUITE RUN {run_idx}/{args.repeat} ########")
        results = run_suite()
        failed = [r for r in results if not r.get("ok")]
        summary = {
            "run": run_idx,
            "mode": "golden_vs_python",
            "total_profiles": len(results),
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "failed_ids": [r["id"] for r in failed],
            "results": results,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        all_runs.append(summary)
        (SUITE_DIR / f"summary_run_{run_idx}.json").write_text(
            json.dumps(summary, indent=2, default=str), encoding="utf-8"
        )
        print(f"\nRun {run_idx}: {summary['passed']}/{summary['total_profiles']} passed")
        if failed:
            print("FAILED:", ", ".join(summary["failed_ids"]))

    (SUITE_DIR / "summary.json").write_text(json.dumps(all_runs, indent=2, default=str), encoding="utf-8")
    if any(r["failed"] > 0 for r in all_runs):
        raise SystemExit(1)
    print("\nALL GOLDEN REGRESSION RUNS PASSED (0 diffs each).")


if __name__ == "__main__":
    main()
