"""Shared helpers for local multi-interface launcher and tests."""

from __future__ import annotations

from dataclasses import dataclass
import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any

from .demo_profiles import SYNTHETIC_DEMO_PROFILES
from .models import AnalyzeDogRequest, AnalysisPresentation

DEBUG_TRACE_UNAVAILABLE = "Debug trace unavailable — API is not running in debug mode."


@dataclass(frozen=True)
class InterfaceSnapshot:
    dog_name: str | None
    primary_breed: str | None
    secondary_breed: str | None
    health_count: int
    product_count: int
    package_count: int
    monthly_total: float | None
    yearly_total: float | None
    evidence_count: int
    formula_ids: tuple[str, ...]


def default_demo_profile() -> tuple[str, AnalyzeDogRequest]:
    """Stable demo profile used across interfaces."""
    key = "mixed_lab_golden"
    return key, SYNTHETIC_DEMO_PROFILES[key]


def is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def find_open_port(host: str, preferred_port: int, *, max_port: int = 9000) -> int:
    for port in range(preferred_port, max_port + 1):
        if is_port_available(host, port):
            return port
    raise RuntimeError(f"No open port found in range {preferred_port}-{max_port}")


def get_json(url: str, timeout_seconds: float = 2.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload) if payload else {}


def health_check(api_base_url: str, timeout_seconds: float = 2.0) -> tuple[bool, str]:
    try:
        payload = get_json(f"{api_base_url.rstrip('/')}/health", timeout_seconds=timeout_seconds)
        status = str(payload.get("status") or "")
        if status in {"ok", "degraded"}:
            return True, status
        return False, f"Unexpected health payload: {payload}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def wait_for_health(
    api_base_url: str,
    *,
    timeout_seconds: float = 45.0,
    interval_seconds: float = 0.5,
) -> tuple[bool, str]:
    deadline = time.time() + timeout_seconds
    last_detail = "not_started"
    while time.time() < deadline:
        ok, detail = health_check(api_base_url)
        if ok:
            return True, detail
        last_detail = detail
        time.sleep(interval_seconds)
    return False, last_detail


def snapshot_from_analyze(analyze: dict[str, Any]) -> InterfaceSnapshot:
    profile = analyze.get("profile") or {}
    breeds = tuple(profile.get("breeds") or ())
    formula_ids = _formula_ids_from_analyze(analyze)
    monthly = _to_float(((analyze.get("monthly_plan") or {}).get("total_cost")))
    yearly = _to_float(((analyze.get("yearly_plan") or {}).get("total_cost")))
    return InterfaceSnapshot(
        dog_name=_safe_str(profile.get("pet_name")),
        primary_breed=_safe_str(breeds[0] if len(breeds) > 0 else None),
        secondary_breed=_safe_str(breeds[1] if len(breeds) > 1 else None),
        health_count=len(analyze.get("healthInsights") or analyze.get("risks") or []),
        product_count=len(analyze.get("productRecommendations") or []),
        package_count=len(analyze.get("wellnessPackages") or []),
        monthly_total=monthly,
        yearly_total=yearly,
        evidence_count=len(analyze.get("scientificEvidence") or analyze.get("evidence") or []),
        formula_ids=formula_ids,
    )


def snapshot_from_presentation(result: AnalysisPresentation) -> InterfaceSnapshot:
    formula_ids = tuple(
        sorted(
            {
                str(x.get("formula_id"))
                for x in (result.trace.debug_formula_executions or ())
                if isinstance(x, dict) and x.get("formula_id")
            }
        )
    )
    breeds = result.dog.breeds or ()
    return InterfaceSnapshot(
        dog_name=result.dog.name,
        primary_breed=_safe_str(breeds[0] if len(breeds) > 0 else None),
        secondary_breed=_safe_str(breeds[1] if len(breeds) > 1 else None),
        health_count=len(result.health.insights or result.health.priorities or ()),
        product_count=len(result.products.products or ()),
        package_count=len(result.packages.packages or ()),
        monthly_total=_to_float(result.financial.monthly_plan.get("total_cost")),
        yearly_total=_to_float(result.financial.yearly_plan.get("total_cost")),
        evidence_count=len(result.evidence.evidence or ()),
        formula_ids=formula_ids,
    )


def _formula_ids_from_analyze(analyze: dict[str, Any]) -> tuple[str, ...]:
    debug = analyze.get("debug") or {}
    ids = {
        str(x.get("formula_id"))
        for x in (debug.get("formula_executions") or ())
        if isinstance(x, dict) and x.get("formula_id")
    }
    return tuple(sorted(ids))


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
