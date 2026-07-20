"""
EngineTrace — Phase 21 debug-only calculation audit.

Projects a frozen analyze envelope into an engineering trace.
Does NOT recompute clinical formulas or expose proprietary equations.
Uses formula identifiers (e.g. RISK_V2_1) plus inputs/outputs only.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

from app.agent.version import ALGORITHM_VERSION, ENGINE_NAME
from app.data.repository import DataRepository
from app.inference.formula_registry import (
    FORMULA_ACTIVITY,
    FORMULA_ASSESSMENT,
    FORMULA_BREED,
    FORMULA_EVIDENCE,
    FORMULA_NUTRIENT,
    FORMULA_PACKAGE,
    FORMULA_PRODUCT,
    FORMULA_RISK,
    FORMULA_TRAIT,
    FORMULA_VALIDATION,
)

# Re-export for historical imports
__all_formula_ids__ = (
    FORMULA_BREED,
    FORMULA_TRAIT,
    FORMULA_RISK,
    FORMULA_NUTRIENT,
    FORMULA_ACTIVITY,
    FORMULA_PRODUCT,
    FORMULA_PACKAGE,
    FORMULA_EVIDENCE,
    FORMULA_VALIDATION,
    FORMULA_ASSESSMENT,
)


def is_engine_debug(*, request_debug: bool | None = None) -> bool:
    """True when PPIE_DEBUG / DEBUG_ENGINE env is set, or request explicitly asks."""
    if request_debug is True:
        return True
    for key in ("PPIE_DEBUG", "DEBUG_ENGINE"):
        raw = str(os.getenv(key, "")).strip().lower()
        if raw in ("1", "true", "yes", "on"):
            return True
    return False


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stage(
    *,
    name: str,
    formula_id: str,
    inputs: Any,
    outputs: Any,
    csv_sources: list[dict[str, Any]] | None = None,
    dependencies: list[str] | None = None,
    elapsed_ms: float | None = None,
    confidence: Any = None,
    notes: list[str] | None = None,
    missing: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "stage": name,
        "formula_id": formula_id,
        "algorithm_version": ALGORITHM_VERSION,
        "inputs": inputs,
        "outputs": outputs,
        "csv_sources": csv_sources or [],
        "dependencies": dependencies or [],
        "elapsed_ms": elapsed_ms,
        "confidence": confidence,
        "notes": notes or [],
        "missing": missing or [],
        # Explicit: never include equation text
        "equation_exposed": False,
    }


def _csv_ref(table: str, rows: Any = None, note: str | None = None) -> dict[str, Any]:
    ref: dict[str, Any] = {"table": table}
    if rows is not None:
        ref["rows"] = rows
    if note:
        ref["note"] = note
    return ref


def _profile_section(analyze: dict[str, Any]) -> dict[str, Any]:
    p = analyze.get("profile") or analyze.get("pet") or {}
    return _stage(
        name="profile",
        formula_id="PROFILE_NORMALIZE_V2_1",
        inputs={"raw_profile_keys": sorted(p.keys())},
        outputs={
            "display_name": p.get("pet_name") or p.get("name"),
            "breeds": p.get("breeds"),
            "weight_kg": p.get("weight_kg"),
            "age_years": p.get("age_years"),
            "activity_level": p.get("activity_level"),
            "environment": p.get("current_environment"),
            "observed_conditions": p.get("observed_conditions") or [],
        },
        dependencies=[],
        notes=["DogProfile normalized into analyze.profile"],
    )


def _breed_section(analyze: dict[str, Any]) -> dict[str, Any]:
    bio = analyze.get("biology") or {}
    resolved = bio.get("resolved_breeds") or bio.get("breeds") or []
    descriptors = bio.get("descriptors") or []
    profile = analyze.get("profile") or {}
    breeds_in = profile.get("breeds") or []
    items = []
    for i, row in enumerate(resolved if isinstance(resolved, list) else []):
        if not isinstance(row, dict):
            items.append({"name": str(row)})
            continue
        weight = row.get("weight_pct") or row.get("split_pct") or row.get("weight")
        items.append(
            {
                "name": row.get("breed") or row.get("name") or row.get("breed_name"),
                "weight_pct": weight,
                "traits_loaded": row.get("traits") or {},
            }
        )
    # If weights missing, assume equal split for audit display only (not a formula change)
    if items and all(x.get("weight_pct") is None for x in items) and len(breeds_in) >= 1:
        for x in items:
            x["weight_pct_note"] = "Not emitted on resolved row; see DogProfile breed_split"
    return _stage(
        name="breed",
        formula_id=FORMULA_BREED,
        inputs={"breeds": breeds_in},
        outputs={"resolved": items, "descriptors": descriptors, "record_count": len(items)},
        csv_sources=[
            _csv_ref("BREEDS"),
            _csv_ref("BREED_ALIASES"),
            _csv_ref("MIXED_BREED_MATRIX"),
            _csv_ref("MIXED_BREED_INTERACTIONS"),
        ],
        dependencies=["profile"],
        notes=["Breed resolution + descriptor load; formula_id only (no equation text)"],
    )


def _traits_section(analyze: dict[str, Any]) -> dict[str, Any]:
    bio = analyze.get("biology") or {}
    traits = bio.get("trait_summary") or []
    items = []
    for t in traits if isinstance(traits, list) else []:
        if isinstance(t, dict):
            items.append(
                {
                    "trait": t.get("title") or t.get("trait") or t.get("name"),
                    "category": t.get("category") or t.get("group"),
                    "formula_id": FORMULA_TRAIT,
                    "contribution_note": "Weighted inheritance from resolved breeds (see formula_id)",
                    "summary": t.get("summary") or t.get("explanation") or "",
                }
            )
        else:
            items.append({"trait": str(t), "formula_id": FORMULA_TRAIT})
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "biology"), {})
    return _stage(
        name="traits",
        formula_id=FORMULA_TRAIT,
        inputs={"descriptor_count": len(bio.get("descriptors") or [])},
        outputs={"traits": items, "count": len(items)},
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or ["TRAIT_PURPOSES", "TRAIT_CONTRIBUTION_WEIGHTS"])],
        dependencies=["breed"],
    )


def _risks_section(analyze: dict[str, Any]) -> dict[str, Any]:
    """Risk audit from emitted fields only — no invented modifier deltas."""
    insights = analyze.get("healthInsights") or []
    calc = {str(c.get("condition")): c for c in (analyze.get("calculationTrace") or []) if isinstance(c, dict)}
    risks = []
    missing = []
    for h in insights:
        if not isinstance(h, dict):
            continue
        title = h.get("title") or h.get("condition") or "Condition"
        ct = calc.get(str(title)) or {}
        # Available intermediate values from engine emission (not proprietary constants)
        intermediates = {
            "biological_risk_percent": h.get("biological_risk_percent") or h.get("estimated_biological_risk_percent"),
            "observed_breed_prevalence_percent": h.get("observed_breed_prevalence_percent")
            or h.get("observed_prevalence_percent"),
            "estimate_vs_observed_difference": h.get("estimate_vs_observed_difference"),
            "priority_score": h.get("priority_score"),
            "confidence_percent": h.get("confidence_percent"),
        }
        if intermediates["observed_breed_prevalence_percent"] is None:
            missing.append(
                {
                    "subject": title,
                    "missing": "published_prevalence_or_observed_breed_prevalence",
                    "reason": "No observed breed prevalence emitted on this insight",
                    "fallback": "Trait / biology estimate path",
                    "severity": "warning",
                }
            )
        risks.append(
            {
                "condition": title,
                "goal_id_internal": h.get("goal_id"),  # debug only
                "formula_id": FORMULA_RISK,
                "inputs": {
                    "supporting_traits": h.get("supporting_traits") or [],
                    "supporting_conditions": h.get("supporting_conditions") or [],
                    "observed_inputs": ct.get("observed_inputs") or {},
                    "published_evidence_rows": len(ct.get("published_evidence") or []),
                },
                "outputs": {
                    "final_risk_percent": intermediates["biological_risk_percent"],
                    "priority_score": intermediates["priority_score"],
                    "confidence_percent": intermediates["confidence_percent"],
                },
                "intermediates": intermediates,
                "trait_contributions": ct.get("trait_contributions") or [],
                "published_evidence": ct.get("published_evidence") or [],
                "decision_log": ct.get("decision_log") or [],
                "notes": [
                    "Modifier_line_items (e.g. activity +4%) are not separately emitted by RISK_V2_1; "
                    "audit uses intermediates the engine already publishes.",
                ],
            }
        )
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "health_risk"), {})
    return _stage(
        name="risks",
        formula_id=FORMULA_RISK,
        inputs={"insight_count": len(insights)},
        outputs={"risks": risks, "count": len(risks)},
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or ["BREED_CONDITIONS", "TRAIT_INTERACTIONS"])],
        dependencies=["traits", "breed"],
        missing=missing,
        confidence={"priority_count": len(risks)},
    )


def _nutrition_section(analyze: dict[str, Any]) -> dict[str, Any]:
    targets = analyze.get("nutritionalTargets") or analyze.get("ingredientRequirements") or []
    calc = analyze.get("calculationTrace") or []
    items = []
    for t in targets if isinstance(targets, list) else []:
        if not isinstance(t, dict):
            continue
        # Product contributions from calculation trace nutrient lines
        food_mg = None
        supp_mg = None
        for c in calc:
            for pc in c.get("product_contributions") or []:
                for nl in pc.get("nutrient_lines") or []:
                    if str(nl.get("nutrient") or "").lower() != str(t.get("ingredient") or t.get("name") or "").lower():
                        continue
                    # Classify by product type if available
                    food_mg = (food_mg or 0) + float(nl.get("provided_value") or 0)
        items.append(
            {
                "nutrient": t.get("ingredient") or t.get("name"),
                "formula_id": FORMULA_NUTRIENT,
                "inputs": {
                    "supports_goals": t.get("supports_goals") or t.get("for_conditions") or [],
                },
                "outputs": {
                    "daily_target": t.get("daily_target") or t.get("daily"),
                    "monthly_target": t.get("monthly_target") or t.get("monthly"),
                    "coverage_pct": t.get("coverage_pct") or t.get("coverage"),
                    "provided_from_products_sum": food_mg,
                },
                "csv_sources": [
                    _csv_ref("CONDITION_INGREDIENTS"),
                    _csv_ref("INGREDIENT_EVIDENCE"),
                    _csv_ref("INGREDIENT_MECHANISMS"),
                ],
            }
        )
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "nutrition"), {})
    return _stage(
        name="nutrition",
        formula_id=FORMULA_NUTRIENT,
        inputs={"target_count": len(items)},
        outputs={"targets": items},
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or [])],
        dependencies=["risks"],
        missing=[
            {
                "missing": "per_source_food_vs_supplement_split",
                "reason": "Engine emits combined product contributions; split not always available",
                "severity": "info",
            }
        ]
        if items
        else [],
    )


def _activity_section(analyze: dict[str, Any]) -> dict[str, Any]:
    act = analyze.get("activityRecommendations") or {}
    return _stage(
        name="activity",
        formula_id=FORMULA_ACTIVITY,
        inputs={"activity_level": (analyze.get("profile") or {}).get("activity_level")},
        outputs=act if isinstance(act, dict) else {"items": act},
        csv_sources=[_csv_ref("ACTIVITY_PRESCRIPTION_RULES"), _csv_ref("CONDITION_ACTIVITIES")],
        dependencies=["breed", "risks"],
    )


def _grooming_section(analyze: dict[str, Any]) -> dict[str, Any]:
    g = analyze.get("groomer") or []
    return _stage(
        name="grooming",
        formula_id="GROOMING_OBS_V2_1",
        inputs={"observed_conditions": (analyze.get("profile") or {}).get("observed_conditions") or []},
        outputs={"checklist": g if isinstance(g, list) else g},
        csv_sources=[_csv_ref("GROOMING_OBSERVATION_DEFS")],
        dependencies=["profile"],
    )


def _products_section(analyze: dict[str, Any]) -> dict[str, Any]:
    recs = analyze.get("productRecommendations") or analyze.get("products") or []
    analyses = analyze.get("productAnalyses") or {}
    selected = []
    for p in recs if isinstance(recs, list) else []:
        if not isinstance(p, dict):
            continue
        pid = str(p.get("product_id") or "")
        selected.append(
            {
                "product_id": pid,
                "name": p.get("product_name") or p.get("name"),
                "formula_id": FORMULA_PRODUCT,
                "inputs": {"category": p.get("category") or p.get("type")},
                "outputs": {
                    "serving": p.get("serving") or p.get("serving_size") or p.get("daily_amount"),
                    "monthly_cost": p.get("monthly_cost"),
                    "why": p.get("why") or p.get("why_selected") or p.get("short_description"),
                },
                "analysis_present": bool(analyses.get(pid)),
            }
        )
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "products"), {})
    return _stage(
        name="products",
        formula_id=FORMULA_PRODUCT,
        inputs={"recommendation_count": len(selected)},
        outputs={
            "selected": selected,
            "candidates_note": "Full rejected-candidate list is not emitted on analyze; package optimizer holds selection set",
            "analyses_keys": list(analyses.keys())[:40] if isinstance(analyses, dict) else [],
        },
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or ["PRODUCT_CATALOG", "PRODUCT_COMPONENTS"])],
        dependencies=["nutrition"],
        missing=[
            {
                "missing": "rejected_product_candidate_list",
                "reason": "Not currently serialized on analyze envelope",
                "severity": "info",
            }
        ],
    )


def _packages_section(analyze: dict[str, Any]) -> dict[str, Any]:
    pkgs = analyze.get("wellnessPackages") or []
    tiers = []
    for p in pkgs if isinstance(pkgs, list) else []:
        if not isinstance(p, dict):
            continue
        products = p.get("products_included") or p.get("product_cards") or []
        tiers.append(
            {
                "tier": p.get("tier") or p.get("package_id"),
                "title": p.get("title"),
                "recommended": bool(p.get("recommended")),
                "formula_id": FORMULA_PACKAGE,
                "inputs": {
                    "product_count": len(products) if isinstance(products, list) else 0,
                },
                "outputs": {
                    "coverage_score": p.get("coverage_score"),
                    "overall_score": p.get("overall_score"),
                    "monthly_cost": p.get("monthly_cost"),
                    "yearly_cost": p.get("yearly_cost"),
                    "summary": p.get("package_summary") or p.get("tagline"),
                },
            }
        )
    return _stage(
        name="packages",
        formula_id=FORMULA_PACKAGE,
        inputs={"tier_count": len(tiers)},
        outputs={
            "tiers": tiers,
            "recommended": next((t for t in tiers if t.get("recommended")), tiers[1] if len(tiers) > 1 else (tiers[0] if tiers else None)),
        },
        csv_sources=[_csv_ref("PACKAGE_TIERS"), _csv_ref("PRODUCT_PRICING"), _csv_ref("PRODUCT_DEFAULTS")],
        dependencies=["products", "nutrition", "risks"],
        missing=[
            {
                "missing": "candidates_evaluated_count",
                "reason": "Optimizer does not emit candidate tally on package row",
                "severity": "info",
            }
        ],
    )


def _evidence_section(analyze: dict[str, Any]) -> dict[str, Any]:
    raw = analyze.get("scientificEvidence") or analyze.get("evidence") or []
    items = []
    for e in raw if isinstance(raw, list) else []:
        if not isinstance(e, dict):
            continue
        items.append(
            {
                "title": e.get("title") or e.get("source_name"),
                "formula_id": FORMULA_EVIDENCE,
                "inputs": {"supports": e.get("supports") or e.get("conditions") or []},
                "outputs": {
                    "journal": e.get("journal") or e.get("source_name"),
                    "year": e.get("year"),
                    "url": e.get("source_url") or e.get("url"),
                    "quoted_finding": e.get("finding") or e.get("quote") or e.get("summary"),
                    "evidence_level": e.get("evidence_level") or e.get("level"),
                    "status": e.get("status"),
                },
            }
        )
    return _stage(
        name="evidence",
        formula_id=FORMULA_EVIDENCE,
        inputs={"count": len(items)},
        outputs={"items": items},
        csv_sources=[_csv_ref("CLINICAL_EVIDENCE_BASE"), _csv_ref("INGREDIENT_EVIDENCE")],
        dependencies=["risks", "nutrition"],
    )


def _validation_section(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    val = (assessment or {}).get("validation") or {}
    items = val.get("items") if isinstance(val, dict) else []
    if not items:
        # Derive lightweight validation slots from health insights
        items = []
        for h in analyze.get("healthInsights") or []:
            if not isinstance(h, dict):
                continue
            title = h.get("title")
            obs = h.get("observed_breed_prevalence_percent") or h.get("observed_prevalence_percent")
            est = h.get("biological_risk_percent") or h.get("estimated_biological_risk_percent")
            if obs is not None:
                items.append(
                    {
                        "subject": title,
                        "formula_id": FORMULA_VALIDATION,
                        "status": "compared",
                        "inputs": {"published_or_observed_pct": obs, "ppie_estimate_pct": est},
                        "outputs": {
                            "deviation_pct": h.get("estimate_vs_observed_difference"),
                            "confidence_percent": h.get("confidence_percent"),
                        },
                    }
                )
            else:
                items.append(
                    {
                        "subject": title,
                        "formula_id": FORMULA_VALIDATION,
                        "status": "unavailable",
                        "inputs": {"ppie_estimate_pct": est},
                        "outputs": {
                            "reason": "No high-quality prevalence study linked for this exact population",
                            "derived_from": ["breed", "traits", "environment", "nutrition"],
                        },
                    }
                )
    return _stage(
        name="validation",
        formula_id=FORMULA_VALIDATION,
        inputs={"item_count": len(items)},
        outputs={"items": items},
        dependencies=["risks", "evidence"],
    )


def run_consistency_checks(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Non-mutating sanity checks — warnings only."""
    warnings: list[dict[str, Any]] = []
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        pct = h.get("biological_risk_percent")
        if pct is not None:
            try:
                v = float(pct)
                if v < 0 or v > 100:
                    warnings.append(
                        {
                            "check": "risk_bounds",
                            "severity": "error",
                            "subject": h.get("title"),
                            "detail": f"biological_risk_percent out of bounds: {v}",
                        }
                    )
            except (TypeError, ValueError):
                warnings.append(
                    {
                        "check": "risk_bounds",
                        "severity": "error",
                        "subject": h.get("title"),
                        "detail": "non-numeric risk percent",
                    }
                )
        conf = h.get("confidence_percent")
        if conf is not None:
            try:
                c = float(conf)
                if c < 0 or c > 100:
                    warnings.append(
                        {
                            "check": "confidence_bounds",
                            "severity": "warning",
                            "subject": h.get("title"),
                            "detail": f"confidence_percent out of bounds: {c}",
                        }
                    )
            except (TypeError, ValueError):
                pass

    breeds = (analyze.get("profile") or {}).get("breeds") or []
    resolved = (analyze.get("biology") or {}).get("resolved_breeds") or []
    weights = []
    for r in resolved if isinstance(resolved, list) else []:
        if isinstance(r, dict) and r.get("weight_pct") is not None:
            try:
                weights.append(float(r["weight_pct"]))
            except (TypeError, ValueError):
                pass
    if weights:
        total = sum(weights)
        # Allow 0–1 or 0–100 scales
        if total > 1.5:
            if abs(total - 100) > 1.0:
                warnings.append(
                    {
                        "check": "breed_weights_sum",
                        "severity": "warning",
                        "detail": f"breed weight_pct sum={total} (expected ~100)",
                    }
                )
        elif abs(total - 1.0) > 0.02:
            warnings.append(
                {
                    "check": "breed_weights_sum",
                    "severity": "warning",
                    "detail": f"breed weight_pct sum={total} (expected ~1.0)",
                }
            )

    for t in analyze.get("nutritionalTargets") or []:
        if not isinstance(t, dict):
            continue
        cov = t.get("coverage_pct")
        if cov is not None:
            try:
                if float(cov) < 0:
                    warnings.append(
                        {
                            "check": "nutrition_coverage_nonnegative",
                            "severity": "error",
                            "subject": t.get("ingredient") or t.get("name"),
                            "detail": f"negative coverage {cov}",
                        }
                    )
            except (TypeError, ValueError):
                pass

    if assessment:
        pkg = assessment.get("packages") or {}
        tiers = pkg.get("tiers") or []
        rec = pkg.get("recommended_tier")
        if rec and tiers:
            match = next((t for t in tiers if t.get("tier") == rec), None)
            if match and not match.get("recommended"):
                warnings.append(
                    {
                        "check": "package_recommended_flag",
                        "severity": "warning",
                        "detail": "recommended_tier does not have recommended=true on tier row",
                    }
                )

    if not breeds:
        warnings.append({"check": "profile_breeds", "severity": "error", "detail": "No breeds on profile"})

    return warnings


def build_engine_trace(
    repo: DataRepository,
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    *,
    timings: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Build full EngineTrace from frozen analyze (+ optional assessment)."""
    t0 = time.perf_counter()
    sections = {
        "profile": _profile_section(analyze),
        "breed": _breed_section(analyze),
        "traits": _traits_section(analyze),
        "risks": _risks_section(analyze),
        "nutrition": _nutrition_section(analyze),
        "activity": _activity_section(analyze),
        "grooming": _grooming_section(analyze),
        "products": _products_section(analyze),
        "packages": _packages_section(analyze),
        "evidence": _evidence_section(analyze),
        "validation": _validation_section(analyze, assessment),
    }
    consistency = run_consistency_checks(analyze, assessment)
    build_ms = round((time.perf_counter() - t0) * 1000, 2)
    timeline = []
    for name, sec in sections.items():
        timeline.append(
            {
                "stage": name,
                "elapsed_ms": (timings or {}).get(name) or sec.get("elapsed_ms"),
                "formula_id": sec.get("formula_id"),
            }
        )
    if timings:
        for k, v in timings.items():
            if k not in {t["stage"] for t in timeline}:
                timeline.append({"stage": k, "elapsed_ms": v, "formula_id": None})

    return {
        "schema": "engine_trace.v1",
        "engine": ENGINE_NAME,
        "algorithm_version": ALGORITHM_VERSION,
        "data_version": getattr(repo, "version", None) or "",
        "content_hash": getattr(repo, "csv_hash", None) or "",
        "generated_at": _now_iso(),
        "debug": True,
        "equation_policy": "formula_id_only",
        "formula_ids": {
            "breed": FORMULA_BREED,
            "traits": FORMULA_TRAIT,
            "risks": FORMULA_RISK,
            "nutrition": FORMULA_NUTRIENT,
            "activity": FORMULA_ACTIVITY,
            "products": FORMULA_PRODUCT,
            "packages": FORMULA_PACKAGE,
            "evidence": FORMULA_EVIDENCE,
            "validation": FORMULA_VALIDATION,
            "assessment": FORMULA_ASSESSMENT,
        },
        "sections": sections,
        "pipeline_trace_raw": analyze.get("pipeline_trace") or [],
        "calculation_trace_raw": analyze.get("calculationTrace") or [],
        "timeline": timeline,
        "consistency_warnings": consistency,
        "meta": {
            "trace_build_ms": build_ms,
            "analyze_keys": sorted(analyze.keys()),
            "assessment_attached": bool(assessment),
        },
    }
