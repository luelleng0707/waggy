"""Side-by-side ClinicalAssessment / analyze diff for Validation Console."""

from __future__ import annotations

from typing import Any

NOT_TRACEABLE = "NOT CURRENTLY TRACEABLE"


def _num(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _flatten_health(analyze: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        key = str(h.get("title") or h.get("condition") or "").strip()
        if not key:
            continue
        out[key] = {
            "biological_risk_percent": h.get("biological_risk_percent"),
            "estimated_biological_risk_percent": h.get("estimated_biological_risk_percent"),
            "observed_breed_prevalence_percent": h.get("observed_breed_prevalence_percent")
            or h.get("observed_prevalence_percent"),
            "priority_score": h.get("priority_score"),
            "confidence_percent": h.get("confidence_percent"),
        }
    return out


def _flatten_packages(analyze: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in analyze.get("wellnessPackages") or []:
        if not isinstance(p, dict):
            continue
        key = str(p.get("tier") or p.get("title") or "").strip()
        if not key:
            continue
        out[key] = {
            "monthly_cost": p.get("monthly_cost"),
            "yearly_cost": p.get("yearly_cost"),
            "coverage_score": p.get("coverage_score"),
            "overall_score": p.get("overall_score"),
            "recommended": bool(p.get("recommended")),
            "product_count": len(p.get("products_included") or p.get("product_cards") or []),
        }
    return out


def _profile_inputs(analyze: dict[str, Any], raw: dict[str, Any] | None) -> dict[str, Any]:
    profile = analyze.get("profile") or analyze.get("pet") or {}
    return {
        "raw_request": raw,
        "name": profile.get("pet_name") or profile.get("name"),
        "breeds": profile.get("breeds") or profile.get("breed_list"),
        "weight_kg": profile.get("weight_kg") or profile.get("weight"),
        "age_years": profile.get("age_years") or profile.get("age"),
        "activity_level": profile.get("activity_level"),
        "current_environment": profile.get("current_environment") or profile.get("environment"),
    }


def _why_changed(path: str, left_inputs: dict, right_inputs: dict) -> dict[str, Any]:
    """Best-effort explanation: which profile inputs differed (not formula internals)."""
    input_diffs = []
    for k in ("weight_kg", "age_years", "activity_level", "current_environment", "breeds", "name"):
        lv, rv = left_inputs.get(k), right_inputs.get(k)
        if lv != rv:
            input_diffs.append({"field": k, "left": lv, "right": rv})

    if path.startswith("health.") or path.startswith("packages."):
        if not input_diffs:
            return {
                "status": NOT_TRACEABLE,
                "reason": "Outputs differ but no profile input delta detected in summarized fields.",
            }
        return {
            "status": "input_delta",
            "reason": "Profile inputs differ; engine may have re-run risk/optimizer with new inputs.",
            "input_deltas": input_diffs,
            "modifier_chain": NOT_TRACEABLE,
            "note": "Per-modifier contribution to this delta is not emitted by the engine.",
        }
    return {
        "status": "field_delta",
        "input_deltas": input_diffs,
        "modifier_chain": NOT_TRACEABLE,
    }


def compare_analyses(
    left_analyze: dict[str, Any],
    right_analyze: dict[str, Any],
    *,
    left_raw: dict[str, Any] | None = None,
    right_raw: dict[str, Any] | None = None,
    left_label: str = "Left",
    right_label: str = "Right",
    left_timings: dict[str, float] | None = None,
    right_timings: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Diff two frozen analyze envelopes. Does not recompute formulas."""
    left_in = _profile_inputs(left_analyze, left_raw)
    right_in = _profile_inputs(right_analyze, right_raw)

    changes: list[dict[str, Any]] = []

    lh, rh = _flatten_health(left_analyze), _flatten_health(right_analyze)
    for key in sorted(set(lh) | set(rh)):
        a, b = lh.get(key), rh.get(key)
        if a is None:
            changes.append(
                {
                    "path": f"health.{key}",
                    "kind": "added_right",
                    "left": None,
                    "right": b,
                    "why": _why_changed(f"health.{key}", left_in, right_in),
                }
            )
            continue
        if b is None:
            changes.append(
                {
                    "path": f"health.{key}",
                    "kind": "removed_right",
                    "left": a,
                    "right": None,
                    "why": _why_changed(f"health.{key}", left_in, right_in),
                }
            )
            continue
        for field in (
            "biological_risk_percent",
            "estimated_biological_risk_percent",
            "observed_breed_prevalence_percent",
            "priority_score",
            "confidence_percent",
        ):
            lv, rv = a.get(field), b.get(field)
            if lv != rv:
                ln, rn = _num(lv), _num(rv)
                delta = None if ln is None or rn is None else round(rn - ln, 4)
                changes.append(
                    {
                        "path": f"health.{key}.{field}",
                        "kind": "changed",
                        "left": lv,
                        "right": rv,
                        "delta": delta,
                        "why": _why_changed(f"health.{key}.{field}", left_in, right_in),
                    }
                )

    lp, rp = _flatten_packages(left_analyze), _flatten_packages(right_analyze)
    for key in sorted(set(lp) | set(rp)):
        a, b = lp.get(key), rp.get(key)
        if a is None or b is None:
            changes.append(
                {
                    "path": f"packages.{key}",
                    "kind": "added_right" if a is None else "removed_right",
                    "left": a,
                    "right": b,
                    "why": _why_changed(f"packages.{key}", left_in, right_in),
                }
            )
            continue
        for field in ("monthly_cost", "yearly_cost", "coverage_score", "overall_score", "recommended", "product_count"):
            lv, rv = a.get(field), b.get(field)
            if lv != rv:
                ln, rn = _num(lv), _num(rv)
                delta = None if ln is None or rn is None else round(rn - ln, 4)
                changes.append(
                    {
                        "path": f"packages.{key}.{field}",
                        "kind": "changed",
                        "left": lv,
                        "right": rv,
                        "delta": delta,
                        "why": _why_changed(f"packages.{key}.{field}", left_in, right_in),
                    }
                )

    # Nutrition target count
    ln = left_analyze.get("nutritionalTargets") or []
    rn = right_analyze.get("nutritionalTargets") or []
    if len(ln) != len(rn):
        changes.append(
            {
                "path": "nutrition.target_count",
                "kind": "changed",
                "left": len(ln),
                "right": len(rn),
                "delta": len(rn) - len(ln),
                "why": _why_changed("nutrition.target_count", left_in, right_in),
            }
        )

    unchanged_health = sum(
        1
        for k in set(lh) & set(rh)
        if lh[k].get("biological_risk_percent") == rh[k].get("biological_risk_percent")
    )

    input_deltas = []
    for k in ("weight_kg", "age_years", "activity_level", "current_environment", "breeds", "name"):
        lv, rv = left_in.get(k), right_in.get(k)
        if lv != rv:
            input_deltas.append({"field": k, "left": lv, "right": rv})

    return {
        "schema": "assessment_compare.v1",
        "left_label": left_label,
        "right_label": right_label,
        "left_inputs": left_in,
        "right_inputs": right_in,
        "input_deltas": input_deltas,
        "change_count": len(changes),
        "unchanged_health_priorities": unchanged_health,
        "changes": changes,
        "outputs_identical": len(changes) == 0,
        "timings": {"left": left_timings or {}, "right": right_timings or {}},
        "note": (
            "Diff compares frozen analyze outputs only. "
            "Why-changed cites profile input deltas; per-modifier attribution is "
            f"{NOT_TRACEABLE}."
            + (
                " Inputs differ but compared health/package fields are identical."
                if len(changes) == 0 and input_deltas
                else ""
            )
        ),
    }
