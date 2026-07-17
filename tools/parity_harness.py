"""
Historical Node↔Python parity harness (DEPRECATED).

Production regression uses golden fixtures:
  py -3 tools/parity_suite.py

This script remains only for forensic comparison if a Node checkout
from tag `legacy-node-final` is restored. It requires Node:3000.
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
TOLERANCE = 0.05

BIRTHDAY = "2021-03-15"
WEIGHT_KG = 30.0
SEX = "Female"
ACTIVITY = "High"
ENVIRONMENT = "Shanghai Summer"
BREEDS = ["Golden Retriever", "Labrador Retriever"]
NAME = "Dolly"


def age_years_from_birthday(birthday: str) -> float:
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
        for i in range(min(len(a), len(b))):
            diff(f"{path}[{i}]", a[i], b[i], diffs)
        return

    if a != b:
        diffs.append({"path": path, "kind": "value", "js": a, "py": b})


def main() -> None:
    print("DEPRECATED: use tools/parity_suite.py (golden fixtures).")
    print("This harness requires a restored Node checkout from tag legacy-node-final.")
    OUT_DIR.mkdir(exist_ok=True)

    js_health_code, js_health = http_json("GET", "http://127.0.0.1:3000/health")
    py_health_code, py_health = http_json("GET", "http://127.0.0.1:8000/health")
    print("Node /health:", js_health_code, js_health)
    print("Python /health:", py_health_code, py_health)
    if js_health_code != 200 or py_health_code != 200:
        raise SystemExit("One or both APIs are not healthy.")

    js_code, js_body = http_json(
        "POST",
        "http://127.0.0.1:3000/api/v1/analyze",
        js_payload(),
        headers={"x-api-key": "wagtopia-demo-key"},
    )
    py_code, py_body = http_json(
        "POST",
        "http://127.0.0.1:8000/api/v1/analyze",
        js_payload(),
        headers={"x-api-key": "wagtopia-demo-key"},
    )
    if js_code != 200:
        raise SystemExit(f"Node analyze failed: {js_body}")
    if py_code != 200:
        raise SystemExit(f"Python analyze failed: {py_body}")

    diffs: list[dict[str, Any]] = []
    diff("", js_body, py_body, diffs)
    (OUT_DIR / "js_response.json").write_text(json.dumps(js_body, indent=2, default=str), encoding="utf-8")
    (OUT_DIR / "py_response.json").write_text(json.dumps(py_body, indent=2, default=str), encoding="utf-8")
    (OUT_DIR / "parity_diff.json").write_text(
        json.dumps({"diff_count": len(diffs), "diffs": diffs[:200]}, indent=2, default=str),
        encoding="utf-8",
    )
    print("JS wellness_score:", js_body.get("wellness_score"), "PY:", py_body.get("wellness_score"))
    print("Total diffs:", len(diffs))


if __name__ == "__main__":
    main()
