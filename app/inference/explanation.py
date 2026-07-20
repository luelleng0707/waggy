"""Explanation engine — builds reasoning chains from inferred values / ledgers."""

from __future__ import annotations

from typing import Any

from app.inference.models import InferredValue, NOT_TRACEABLE


def explain_inferred(value: InferredValue | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, InferredValue):
        d = value.to_dict()
    else:
        d = dict(value)
    bullets: list[str] = []
    if d.get("reason"):
        bullets.append(str(d["reason"]))
    for step in d.get("trace") or []:
        if isinstance(step, dict):
            if step.get("note") and not step.get("traceable", True):
                bullets.append(f"{step.get('name') or 'step'}: {NOT_TRACEABLE}")
            else:
                bullets.append(
                    " · ".join(
                        f"{k}={v}" for k, v in step.items() if k not in ("note",) and v is not None
                    )
                )
    return {
        "value": d.get("value"),
        "confidence": d.get("confidence"),
        "formula_id": d.get("formula_id"),
        "source": d.get("source"),
        "reason": d.get("reason"),
        "trace": d.get("trace") or [],
        "bullets": bullets,
        "enabled": d.get("enabled", True),
    }


def explain_risk_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    bullets = []
    for step in ledger.get("steps") or []:
        if step.get("traceable") and step.get("value") is not None:
            unit = step.get("unit") or ""
            bullets.append(f"{step.get('name')}: {step.get('value')}{unit}")
        else:
            bullets.append(f"{step.get('name')}: {NOT_TRACEABLE}")
    return {
        "condition": ledger.get("condition"),
        "final_probability_pct": ledger.get("final_probability_pct"),
        "formula_id": ledger.get("formula_id"),
        "locked_formula_id": ledger.get("locked_formula_id"),
        "confidence_percent": ledger.get("confidence_percent"),
        "bullets": bullets,
        "steps": ledger.get("steps") or [],
        "complete": ledger.get("complete"),
        "note": ledger.get("note"),
    }
