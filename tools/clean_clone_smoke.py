"""Smoke-test a running PPIE API against tests/golden/dolly.json."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
BASE = f"http://127.0.0.1:{PORT}"

body = {
    "name": "Dolly",
    "pet_name": "Dolly",
    "breeds": ["Golden Retriever", "Labrador Retriever"],
    "birthday": "2021-03-15",
    "weight": 30,
    "sex": "Female",
    "activity_level": "High",
    "current_environment": "Shanghai Summer",
    "observed_conditions": [],
}


def get(path: str):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode())


def post(path: str, payload: dict, headers: dict | None = None):
    data = json.dumps(payload).encode()
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status, json.loads(resp.read().decode())


def main() -> None:
    code, health = get("/health")
    print("health", code, health)
    assert code == 200 and health.get("runtime") == "python"
    code, live = post("/api/v1/analyze", body, {"x-api-key": "wagtopia-demo-key"})
    print("analyze", code, "score", live.get("wellness_score"), "version", live.get("version"))
    assert code == 200
    golden = json.loads((ROOT / "tests/golden/dolly.json").read_text(encoding="utf-8"))
    assert live.get("wellness_score") == golden.get("wellness_score")
    assert set(live.keys()) == set(golden.keys())
    print("CLEAN_CLONE_SMOKE_OK")


if __name__ == "__main__":
    main()
