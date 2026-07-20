"""
Risk inference helpers — RISK_TRACE_V1 ledger (does not replace RISK_V2_1).

Fills applied modifiers from analyze.debug.risk_traces / observatory when present.
Never invents activity/weight/climate factors.
"""

from __future__ import annotations

from typing import Any

from app.inference.models import NOT_TRACEABLE, ModifierStep

FORMULA_RISK = "RISK_V2_1"
FORMULA_RISK_TRACE = "RISK_TRACE_V1"


def build_risk_modifier_ledger(
    insight: dict[str, Any] | None = None,
    *,
    calc_row: dict[str, Any] | None = None,
    observatory_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Capture every modifier slot for debugging.

    Does NOT recompute risk. Prefers observatory_trace steps from production.
    """
    h = insight or {}
    c = calc_row or {}
    ot = observatory_trace or {}
    final = h.get("biological_risk_percent")
    if final is None:
        final = h.get("estimated_biological_risk_percent")
    if final is None:
        final = ot.get("final_probability_pct")
    observed = h.get("observed_breed_prevalence_percent")
    if observed is None:
        observed = h.get("observed_prevalence_percent")

    # Prefer production observatory chain when present
    if ot.get("steps"):
        steps_out = []
        for s in ot["steps"]:
            if not isinstance(s, dict):
                continue
            steps_out.append(
                {
                    "name": s.get("name"),
                    "label": s.get("label") or s.get("name"),
                    "op": s.get("op"),
                    "value": s.get("value"),
                    "unit": s.get("unit"),
                    "after_percent": s.get("after_percent"),
                    "adjustment_percent": s.get("adjustment_percent"),
                    "source": s.get("source"),
                    "csv": s.get("csv"),
                    "details": s.get("details"),
                    "formula_id": s.get("formula_id") or FORMULA_RISK,
                    "traceable": bool(s.get("traceable")),
                    "status": s.get("status"),
                    "reason": s.get("reason") or s.get("note"),
                    "note": s.get("note"),
                }
            )
        return {
            "formula_id": FORMULA_RISK_TRACE,
            "locked_formula_id": FORMULA_RISK,
            "condition": ot.get("condition") or h.get("title") or h.get("condition"),
            "final_probability_pct": final,
            "confidence_percent": ot.get("confidence_percent") or h.get("confidence_percent"),
            "supporting_traits": h.get("supporting_traits") or [],
            "trait_contributions": c.get("trait_contributions") or [],
            "decision_log": c.get("decision_log") or [],
            "steps": steps_out,
            "expanded_chain": steps_out,
            "csv_refs": ot.get("csv_refs") or [],
            "code": ot.get("code"),
            "logic": ot.get("logic"),
            "complete": bool(ot.get("complete_for_applied_modifiers")),
            "note": ot.get("note")
            or "Observatory trace from health_risk production intermediates.",
        }

    steps: list[ModifierStep] = []
    if observed is not None:
        steps.append(
            ModifierStep(
                name="baseline_observed_prevalence",
                op="baseline",
                value=observed,
                unit="%",
                source="healthInsights.observed_breed_prevalence_percent",
                formula_id=FORMULA_RISK,
                traceable=True,
            )
        )
    else:
        steps.append(
            ModifierStep(
                name="baseline",
                op="baseline",
                value=None,
                source=NOT_TRACEABLE,
                formula_id=FORMULA_RISK_TRACE,
                traceable=False,
                note="Baseline intermediate not separately emitted",
            )
        )

    for name in (
        "breed",
        "trait",
        "benefit",
        "interaction",
        "activity",
        "weight",
        "age",
        "climate",
        "mixed_breed",
    ):
        steps.append(
            ModifierStep(
                name=f"{name}_modifier",
                op="multiply",
                value=None,
                source=NOT_TRACEABLE,
                formula_id=FORMULA_RISK_TRACE,
                traceable=False,
                note=f"Per-modifier `{name}` not serialized — run pipeline to populate analyze.debug.risk_traces",
            )
        )

    if final is not None:
        steps.append(
            ModifierStep(
                name="final_probability",
                op="set",
                value=final,
                unit="%",
                source="healthInsights.biological_risk_percent",
                formula_id=FORMULA_RISK,
                traceable=True,
            )
        )

    return {
        "formula_id": FORMULA_RISK_TRACE,
        "locked_formula_id": FORMULA_RISK,
        "condition": h.get("title") or h.get("condition"),
        "final_probability_pct": final,
        "confidence_percent": h.get("confidence_percent"),
        "supporting_traits": h.get("supporting_traits") or [],
        "trait_contributions": c.get("trait_contributions") or [],
        "decision_log": c.get("decision_log") or [],
        "steps": [s.to_dict() for s in steps],
        "complete": False,
        "note": (
            "Ledger for observability only. RISK_V2_1 computation is unchanged. "
            "Missing modifiers remain NOT CURRENTLY TRACEABLE until engine instrumentation."
        ),
    }
