"""
Runtime parity harness: identical Dolly profile → Node analyze + Python evaluate → recursive JSON diff.

Usage:
  py -3 tools/parity_harness.py
"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "parity_output"
TOLERANCE = 0.05  # absolute tolerance for floats / numbers

# Shared profile (canonical Dolly)
BIRTHDAY = "2021-03-15"
WEIGHT_KG = 30.0
SEX = "Female"
ACTIVITY = "High"
ENVIRONMENT = "Shanghai Summer"
BREEDS = ["Golden Retriever", "Labrador Retriever"]
NAME = "Dolly"


def age_years_from_birthday(birthday: str) -> float:
    """Mirror JS riskEngine.getAgeStage: round to 1 decimal using 365.25-day years."""
    birth = datetime.strptime(birthday, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    years = (now - birth).total_seconds() / (365.25 * 24 * 60 * 60)
    return round(years * 10) / 10


def js_payload() -> dict[str, Any]:
    return {
        "name": NAME,
        "pet_name": NAME,
        "breeds": BREEDS,
        "birthday": BIRTHDAY,
        "weight": WEIGHT_KG,
        "sex": SEX,
        "activity_level": ACTIVITY,
        "current_environment": ENVIRONMENT,
        "observed_conditions": [],
    }


def py_payload() -> dict[str, Any]:
    return {
        "name": NAME,
        "primary_breed": BREEDS[0],
        "secondary_breed": BREEDS[1],
        "breed_split_pct": 50.0,
        "age_years": age_years_from_birthday(BIRTHDAY),
        "weight_kg": WEIGHT_KG,
        "current_environment": ENVIRONMENT,
        "activity_level": ACTIVITY,
        "sex": SEX,
        "gender": SEX,
        "birthday": BIRTHDAY,
        "height_cm": None,
        "observed_conditions": [],
    }


def http_json(method: str, url: str, body: dict | None = None, headers: dict | None = None) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error": raw}
        return exc.code, payload


def is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def normalize_for_sort(v: Any) -> str:
    try:
        return json.dumps(v, sort_keys=True, default=str)
    except TypeError:
        return str(v)


def diff(path: str, a: Any, b: Any, diffs: list[dict[str, Any]]) -> None:
    if type(a) is not type(b) and not (is_number(a) and is_number(b)):
        # None vs missing handled by caller; treat None vs value as type mismatch unless both None
        if a is None or b is None:
            diffs.append({"path": path, "kind": "null_mismatch", "js": a, "py": b})
            return
        diffs.append({"path": path, "kind": "type", "js_type": type(a).__name__, "py_type": type(b).__name__, "js": a, "py": b})
        return

    if is_number(a) and is_number(b):
        if math.isnan(float(a)) and math.isnan(float(b)):
            return
        if abs(float(a) - float(b)) > TOLERANCE:
            diffs.append({"path": path, "kind": "number", "js": a, "py": b, "delta": float(b) - float(a)})
        return

    if isinstance(a, str):
        if a != b:
            diffs.append({"path": path, "kind": "string", "js": a, "py": b})
        return

    if isinstance(a, bool) or a is None:
        if a != b:
            diffs.append({"path": path, "kind": "value", "js": a, "py": b})
        return

    if isinstance(a, dict):
        keys_a = set(a.keys())
        keys_b = set(b.keys())
        for k in sorted(keys_a - keys_b):
            diffs.append({"path": f"{path}.{k}" if path else k, "kind": "missing_in_py", "js": a[k]})
        for k in sorted(keys_b - keys_a):
            diffs.append({"path": f"{path}.{k}" if path else k, "kind": "missing_in_js", "py": b[k]})
        for k in sorted(keys_a & keys_b):
            child = f"{path}.{k}" if path else k
            diff(child, a[k], b[k], diffs)
        return

    if isinstance(a, list):
        if len(a) != len(b):
            diffs.append({"path": path, "kind": "list_length", "js_len": len(a), "py_len": len(b)})
        # Compare by index first (order-sensitive)
        for i in range(min(len(a), len(b))):
            diff(f"{path}[{i}]", a[i], b[i], diffs)
        # Also note if multisets differ when sorted (order-insensitive hint)
        if sorted(map(normalize_for_sort, a)) != sorted(map(normalize_for_sort, b)):
            # Only flag if index walk didn't already capture enough
            if len(a) == len(b):
                # Check if order-only difference
                if sorted(map(normalize_for_sort, a)) == sorted(map(normalize_for_sort, b)):
                    diffs.append({"path": path, "kind": "list_order", "note": "same items, different order"})
        return

    if a != b:
        diffs.append({"path": path, "kind": "value", "js": a, "py": b})


def focus_summary(js: dict, py: dict) -> dict[str, Any]:
    def pkgs(obj: dict) -> list:
        return [
            {
                "tier": p.get("tier"),
                "title": p.get("title"),
                "monthly_cost": p.get("monthly_cost"),
                "yearly_cost": p.get("yearly_cost"),
            }
            for p in (obj.get("wellnessPackages") or [])
        ]

    def insights(obj: dict) -> list:
        return [
            {
                "title": h.get("title"),
                "priority_score": h.get("priority_score"),
                "confidence_percent": h.get("confidence_percent"),
                "estimated_biological_risk_percent": h.get(
                    "estimated_biological_risk_percent", h.get("biological_risk_percent")
                ),
                "groomer_priority": h.get("groomer_priority"),
            }
            for h in (obj.get("healthInsights") or [])[:8]
        ]

    return {
        "age_years_used_py": py_payload()["age_years"],
        "js_version": js.get("version"),
        "py_version": py.get("version"),
        "js_keys": sorted(js.keys()),
        "py_keys": sorted(py.keys()),
        "keys_only_js": sorted(set(js) - set(py)),
        "keys_only_py": sorted(set(py) - set(js)),
        "js_packages": pkgs(js),
        "py_packages": pkgs(py),
        "js_insights": insights(js),
        "py_insights": insights(py),
        "js_wellness_score": js.get("wellness_score"),
        "py_wellness_score": py.get("wellness_score"),
        "js_productAnalyses_keys": sorted((js.get("productAnalyses") or {}).keys()),
        "py_productAnalyses_keys": sorted((py.get("productAnalyses") or {}).keys()),
        "js_nutritionalTargets": (js.get("nutritionalTargets") or [])[:5],
        "py_nutritionalTargets": (py.get("nutritionalTargets") or [])[:5],
    }


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    print("=== Health checks ===")
    js_health_code, js_health = http_json("GET", "http://127.0.0.1:3000/health")
    py_health_code, py_health = http_json("GET", "http://127.0.0.1:8000/health")
    print("Node /health:", js_health_code, js_health)
    print("Python /health:", py_health_code, py_health)
    if js_health_code != 200 or py_health_code != 200:
        raise SystemExit("One or both APIs are not healthy. Start Node:3000 and Python:8000 first.")

    print("\n=== Shared age ===")
    print("age_years (JS formula mirror):", age_years_from_birthday(BIRTHDAY))

    print("\n=== Calling Node POST /api/v1/analyze ===")
    js_code, js_body = http_json(
        "POST",
        "http://127.0.0.1:3000/api/v1/analyze",
        js_payload(),
        headers={"x-api-key": "wagtopia-demo-key"},
    )
    print("Node status:", js_code)
    if js_code != 200:
        (OUT_DIR / "js_error.json").write_text(json.dumps(js_body, indent=2), encoding="utf-8")
        raise SystemExit(f"Node analyze failed: {js_body}")

    print("=== Calling Python POST /api/v2/wellness/evaluate ===")
    py_code, py_body = http_json(
        "POST",
        "http://127.0.0.1:8000/api/v2/wellness/evaluate",
        py_payload(),
    )
    print("Python status:", py_code)
    if py_code != 200:
        (OUT_DIR / "py_error.json").write_text(json.dumps(py_body, indent=2), encoding="utf-8")
        raise SystemExit(f"Python evaluate failed: {py_body}")

    (OUT_DIR / "js_response.json").write_text(json.dumps(js_body, indent=2, default=str), encoding="utf-8")
    (OUT_DIR / "py_response.json").write_text(json.dumps(py_body, indent=2, default=str), encoding="utf-8")

    diffs: list[dict[str, Any]] = []
    diff("", js_body, py_body, diffs)

    summary = focus_summary(js_body, py_body)
    report = {
        "tolerance": TOLERANCE,
        "payload_js": js_payload(),
        "payload_py": py_payload(),
        "summary": summary,
        "diff_count": len(diffs),
        "diffs": diffs[:500],  # cap for readability
        "diff_truncated": len(diffs) > 500,
    }
    (OUT_DIR / "parity_diff.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    print("\n=== Focus summary ===")
    print("keys only in JS:", summary["keys_only_js"])
    print("keys only in PY:", summary["keys_only_py"])
    print("JS packages:", json.dumps(summary["js_packages"], indent=2))
    print("PY packages:", json.dumps(summary["py_packages"], indent=2))
    print("JS insights top:", json.dumps(summary["js_insights"][:3], indent=2))
    print("PY insights top:", json.dumps(summary["py_insights"][:3], indent=2))
    print("JS wellness_score:", summary["js_wellness_score"], "PY:", summary["py_wellness_score"])
    print("JS productAnalyses count:", len(summary["js_productAnalyses_keys"]))
    print("PY productAnalyses count:", len(summary["py_productAnalyses_keys"]))
    print(f"\nTotal diffs: {len(diffs)}")
    print(f"Wrote {OUT_DIR / 'js_response.json'}")
    print(f"Wrote {OUT_DIR / 'py_response.json'}")
    print(f"Wrote {OUT_DIR / 'parity_diff.json'}")

    # Print first 30 diffs for console
    print("\n=== First 30 diffs ===")
    for d in diffs[:30]:
        print(json.dumps(d, default=str))


if __name__ == "__main__":
    main()
