"""ΩO Security audit — input schemas, keys, path safety, CSV integrity."""

from __future__ import annotations

import ast
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ppie_platform" / "security"


def run_security_audit() -> Path:
    findings: list[dict[str, Any]] = []

    # API keys default present
    keys = [k.strip() for k in os.getenv("API_KEYS", "wagtopia-demo-key,ppie-dev-key").split(",") if k.strip()]
    if "wagtopia-demo-key" in keys:
        findings.append(
            {
                "severity": "medium",
                "id": "default_demo_api_key",
                "detail": "Default demo API key is active; rotate API_KEYS in production",
            }
        )

    # Path traversal guards in loader
    loader = (ROOT / "app" / "data" / "loader.py").read_text(encoding="utf-8")
    if "resolve_csv_path" in loader:
        findings.append({"severity": "info", "id": "csv_resolver_present", "detail": "resolve_csv_path used for CSV lookup"})

    # Static scan for open(...,) with user path patterns in app/
    risky = []
    for py in (ROOT / "app").rglob("*.py"):
        text = py.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"open\([^)]*request", text, re.I):
            risky.append(str(py.relative_to(ROOT)))
    if risky:
        findings.append({"severity": "high", "id": "request_path_open", "detail": risky})
    else:
        findings.append({"severity": "info", "id": "no_request_path_open", "detail": "No open(request...) patterns in app/"})

    # Manifest / CSV integrity: files exist
    from app.data.schemas import load_manifest
    from app.data.loader import resolve_csv_path

    missing = []
    try:
        man = load_manifest(ROOT / "data")
        for f in man.files:
            p = resolve_csv_path(ROOT / "data", f.path)
            if not p.exists():
                missing.append(f.path)
    except Exception as exc:
        findings.append({"severity": "high", "id": "manifest_load_failed", "detail": str(exc)})
    if missing:
        findings.append({"severity": "high", "id": "missing_csv", "detail": missing[:20]})
    else:
        findings.append({"severity": "info", "id": "csv_integrity", "detail": "All manifest CSVs resolve"})

    # DogProfileInput schema enforcement exists
    from app.agent.state import DogProfileInput

    try:
        DogProfileInput(
            name="x",
            primary_breed="Labrador Retriever",
            age_years=-1,
            weight_kg=10,
            current_environment="t",
        )
        findings.append({"severity": "high", "id": "profile_schema_weak", "detail": "negative age accepted"})
    except Exception:
        findings.append({"severity": "info", "id": "profile_schema_enforced", "detail": "DogProfileInput rejects invalid age"})

    # Dependency note
    req = ROOT / "requirements.txt"
    findings.append(
        {
            "severity": "info",
            "id": "dependency_pinning",
            "detail": "Run pip-audit / safety in CI; requirements at " + str(req.name),
        }
    )

    highs = sum(1 for f in findings if f["severity"] == "high")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
        "high_count": highs,
        "ok": highs == 0,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    md = OUT / "SECURITY_AUDIT.md"
    lines = [
        "# Security Audit",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Status: **{'PASS' if payload['ok'] else 'FAIL'}** (high={highs})",
        "",
    ]
    for f in findings:
        lines.append(f"- [{f['severity']}] `{f['id']}` — {f['detail']}")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "SECURITY_AUDIT.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    # also copy to meta
    (ROOT / "meta" / "architecture").mkdir(parents=True, exist_ok=True)
    (ROOT / "meta" / "architecture" / "SECURITY_AUDIT.md").write_text(md.read_text(encoding="utf-8"), encoding="utf-8")
    return md
