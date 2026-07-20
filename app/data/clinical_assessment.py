"""
ClinicalAssessment builder — Phase 17.5 contract.

Transforms a frozen PPIE analyze dict into modular, independently
cacheable report objects. Does NOT recompute clinical formulas.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.agent.version import ALGORITHM_VERSION
from app.data.repository import DataRepository

ASSESSMENT_SCHEMA = "1.0.0"
MODULE_IDS = (
    "profile",
    "breed",
    "traits",
    "behavior",
    "environment",
    "health",
    "nutrition",
    "activity",
    "grooming",
    "packages",
    "products",
    "evidence",
    "validation",
    "confidence",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _module(module_id: str, title: str, summary: str, data: dict[str, Any], *, priority: int = 50) -> dict[str, Any]:
    """Envelope for one independently renderable / cacheable module."""
    return {
        "id": module_id,
        "title": title,
        "summary": summary or "",
        "priority": priority,
        "schema": ASSESSMENT_SCHEMA,
        "data": data or {},
    }


def _plain_label(value: Any) -> str:
    s = str(value or "").replace("_", " ").strip()
    return s[:1].upper() + s[1:] if s else ""


def _scrub_tech_list(items: list[Any] | None) -> list[str]:
    out: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            label = item.get("label") or item.get("title") or item.get("name") or item.get("condition")
            if label:
                out.append(_plain_label(label))
        elif item:
            out.append(_plain_label(item))
    return out


def _profile_module(analyze: dict[str, Any]) -> dict[str, Any]:
    p = analyze.get("profile") or analyze.get("pet") or {}
    breeds = p.get("breeds") or []
    if len(breeds) >= 2:
        breed_label = f"{breeds[0]} × {breeds[1]}"
    elif breeds:
        breed_label = str(breeds[0])
    else:
        breed_label = "—"
    name = p.get("pet_name") or p.get("name") or "Your dog"
    data = {
        "display_name": name,
        "breed_label": breed_label,
        "breeds": breeds,
        "age_years": p.get("age_years"),
        "age_stage": p.get("age_stage"),
        "weight_kg": p.get("weight_kg"),
        "sex": p.get("sex") or p.get("gender"),
        "activity_level": p.get("activity_level"),
        "environment": p.get("current_environment"),
        "birthday": p.get("birthday"),
        "body_condition_score": p.get("bcs"),
    }
    summary = f"{name} · {breed_label}"
    if p.get("weight_kg") is not None:
        summary += f" · {p['weight_kg']} kg"
    return _module("profile", "Profile", summary, data, priority=10)


def _breed_module(analyze: dict[str, Any]) -> dict[str, Any]:
    bio = analyze.get("biology") or {}
    resolved = bio.get("resolved_breeds") or bio.get("breeds") or []
    breeds = []
    for row in resolved:
        if isinstance(row, dict):
            breeds.append(
                {
                    "name": row.get("breed") or row.get("name") or row.get("breed_name"),
                    "weight_pct": row.get("weight_pct") or row.get("split_pct"),
                    "traits": row.get("traits") or {},
                }
            )
        else:
            breeds.append({"name": str(row)})
    summary = bio.get("summary") or "Breed composition and biological context."
    if isinstance(summary, dict):
        summary = summary.get("text") or "Breed composition and biological context."
    data = {
        "breeds": breeds,
        "descriptors": bio.get("descriptors") or [],
        "mixed_breed": bool(len(breeds) >= 2),
    }
    return _module("breed", "Breed & biology", str(summary)[:220], data, priority=40)


def _traits_module(analyze: dict[str, Any]) -> dict[str, Any]:
    bio = analyze.get("biology") or {}
    traits = bio.get("trait_summary") or []
    items = []
    for t in traits:
        if isinstance(t, dict):
            items.append(
                {
                    "title": _plain_label(t.get("title") or t.get("trait") or t.get("name")),
                    "category": _plain_label(t.get("category") or t.get("group")),
                    "summary": t.get("summary") or t.get("explanation") or "",
                }
            )
        else:
            items.append({"title": _plain_label(t), "category": "", "summary": ""})
    pns = analyze.get("preventativeNutritionSystem") or {}
    trait_analysis = pns.get("trait_analysis") or []
    return _module(
        "traits",
        "Traits",
        f"{len(items)} biological traits assessed." if items else "Trait profile.",
        {"items": items, "extended": trait_analysis[:12] if isinstance(trait_analysis, list) else []},
        priority=45,
    )


def _environment_module(analyze: dict[str, Any]) -> dict[str, Any]:
    p = analyze.get("profile") or analyze.get("pet") or {}
    mgmt = analyze.get("management") or {}
    env = p.get("current_environment") or mgmt.get("current_environment") or mgmt.get("environment")
    compat = (analyze.get("biology") or {}).get("environmental_compatibility") or []
    return _module(
        "environment",
        "Environment",
        str(env or "Environment context"),
        {
            "label": env,
            "activity_level": p.get("activity_level"),
            "compatibility": compat if isinstance(compat, list) else [],
            "notes": mgmt.get("summary") or mgmt.get("notes") or "",
        },
        priority=42,
    )


def _behavior_module(analyze: dict[str, Any]) -> dict[str, Any]:
    p = analyze.get("profile") or {}
    bio = analyze.get("biology") or {}
    return _module(
        "behavior",
        "Behavior & lifestyle",
        f"Activity level · {p.get('activity_level') or '—'}",
        {
            "activity_level": p.get("activity_level"),
            "energy_notes": bio.get("energy_profile") or "",
            "lifestyle_flags": [],
        },
        priority=48,
    )


def _health_module(analyze: dict[str, Any]) -> dict[str, Any]:
    insights = analyze.get("healthInsights") or analyze.get("risks") or []
    priorities = []
    for i, h in enumerate(insights):
        if not isinstance(h, dict):
            continue
        title = h.get("title") or h.get("condition") or h.get("condition_name") or "Health priority"
        # Plain-language fields for default UI
        explanation = (
            h.get("why_this_matters")
            or h.get("explanation")
            or h.get("summary")
            or h.get("finding")
            or ""
        )
        technical = []
        for key, label in (
            ("condition_key", "Internal condition key"),
            ("logic", "Logic path"),
            ("source", "Source tag"),
            ("goal", "Goal id"),
            ("supports_goals", "Goal tags"),
        ):
            val = h.get(key)
            if val:
                technical.append({"label": label, "value": val})
        # Trace-like fields that look like engine variables
        for k, v in (h.items() if isinstance(h, dict) else []):
            if k in ("title", "condition", "condition_name", "why_this_matters", "explanation", "summary", "finding"):
                continue
            if k.endswith("_id") or k in ("condition_key", "logic", "source", "goal"):
                continue
        traits = _scrub_tech_list(h.get("contributing_traits") or h.get("supporting_traits") or h.get("traits"))
        prevention = _scrub_tech_list(h.get("prevention") or h.get("recommendations"))
        early = _scrub_tech_list(h.get("early_warnings") or h.get("early_signs"))
        nutrients = _scrub_tech_list(h.get("relevant_nutrients") or h.get("nutrients"))
        products = []
        for pid in h.get("relevant_products") or h.get("product_ids") or []:
            if isinstance(pid, dict):
                products.append(
                    {
                        "product_id": pid.get("product_id"),
                        "name": pid.get("name") or pid.get("product_name"),
                    }
                )
            else:
                products.append({"product_id": str(pid), "name": str(pid)})
        prob = h.get("biological_risk_percent")
        if prob is None:
            prob = h.get("risk_percent") or h.get("probability") or h.get("prevalence")
        if isinstance(prob, float) and prob <= 1:
            prob = round(prob * 100, 1)
        priorities.append(
            {
                "id": h.get("condition_key") or h.get("id") or f"risk_{i}",
                "title": _plain_label(title),
                "probability_pct": prob,
                "priority_rank": i + 1,
                "explanation": explanation,
                "contributing_traits": traits,
                "prevention": prevention,
                "early_signs": early,
                "relevant_nutrients": nutrients,
                "relevant_products": products,
                "technical_reasoning": technical,
                "confidence": h.get("confidence") or h.get("confidence_label"),
            }
        )
    summary_score = None
    ws = analyze.get("wellness_summary") or {}
    if isinstance(ws, dict) and ws.get("score") is not None:
        summary_score = {"value": ws.get("score"), "unit": "%", "label": ws.get("label") or "Wellness"}
    elif analyze.get("wellness_score") is not None:
        summary_score = {"value": analyze.get("wellness_score"), "unit": "%", "label": "Wellness"}
    cov = analyze.get("wellness_coverage") or {}
    data = {
        "priorities": priorities,
        "summary_score": summary_score,
        "coverage": cov if isinstance(cov, dict) else {},
        "headline": (ws.get("headline") if isinstance(ws, dict) else None)
        or (priorities[0]["title"] + " is the leading focus" if priorities else "No elevated priorities"),
    }
    top = priorities[0]["title"] if priorities else "Health"
    return _module(
        "health",
        "Health",
        f"Top focus · {top}" + (f" · {priorities[0]['probability_pct']}%" if priorities and priorities[0].get("probability_pct") is not None else ""),
        data,
        priority=20,
    )


def _nutrition_module(analyze: dict[str, Any]) -> dict[str, Any]:
    targets = analyze.get("nutritionalTargets") or analyze.get("ingredientRequirements") or analyze.get("ingredients") or []
    items = []
    for t in targets:
        if not isinstance(t, dict):
            continue
        items.append(
            {
                "name": t.get("ingredient") or t.get("nutrient") or t.get("name") or "Nutrient",
                "daily_target": t.get("daily_target") or t.get("daily") or t.get("dosage"),
                "monthly_target": t.get("monthly_target") or t.get("monthly"),
                "supports": _scrub_tech_list(t.get("supports_goals") or t.get("for_conditions") or t.get("supports")),
                "coverage_pct": t.get("coverage_pct") or t.get("coverage"),
            }
        )
    return _module(
        "nutrition",
        "Nutrition",
        f"{len(items)} nutrient targets" if items else "Nutrition plan",
        {"targets": items, "meal_guidance": []},
        priority=25,
    )


def _activity_module(analyze: dict[str, Any]) -> dict[str, Any]:
    acts = analyze.get("activityRecommendations") or analyze.get("activities") or {}
    if isinstance(acts, list):
        primary = acts[0] if acts and isinstance(acts[0], dict) else {}
        items = acts
    elif isinstance(acts, dict):
        primary = acts
        items = [acts] if acts else []
    else:
        primary = {}
        items = []
    # Prefer nested schedule object when present; otherwise use the recommendation dict
    nested = primary.get("recommended_daily_exercise")
    schedule = nested if isinstance(nested, dict) else {}
    data = {
        "daily_exercise": nested if isinstance(nested, str) else None,
        "morning_min": schedule.get("morning_min") or schedule.get("morning") or primary.get("morning_min"),
        "evening_min": schedule.get("evening_min") or schedule.get("evening") or primary.get("evening_min"),
        "daily_km": schedule.get("daily_km") or schedule.get("daily_distance_km") or primary.get("daily_km"),
        "weekly_km": schedule.get("weekly_km") or schedule.get("weekly_distance_km") or primary.get("weekly_km"),
        "swimming": primary.get("swimming") or schedule.get("swimming"),
        "fetch": primary.get("fetch") or schedule.get("fetch"),
        "training": primary.get("training") or schedule.get("training"),
        "recovery": (
            primary.get("recovery")
            or primary.get("mental")
            or primary.get("lifestyle_tip")
            or primary.get("notes")
            or ""
        ),
        "suggested_physical": primary.get("suggested_physical") or [],
        "suggested_mental": primary.get("suggested_mental") or [],
        "items": items,
    }
    summary = "Activity plan"
    if data.get("morning_min") is not None or data.get("evening_min") is not None:
        summary = f"Walk · {data.get('morning_min') or '—'} + {data.get('evening_min') or '—'} min"
    elif data.get("daily_exercise"):
        summary = f"Daily · {data['daily_exercise']}"
    elif data.get("daily_km") is not None:
        summary = f"Daily · {data['daily_km']} km"
    elif data.get("recovery"):
        summary = str(data["recovery"])[:120]
    return _module("activity", "Activity", summary, data, priority=35)


def _grooming_module(analyze: dict[str, Any]) -> dict[str, Any]:
    g = analyze.get("groomer") or analyze.get("grooming") or {}
    if isinstance(g, list):
        checklist = g
        g = {"checklist": g, "summary": "Grooming guidance"}
    elif not isinstance(g, dict):
        g = {}
        checklist = []
    else:
        checklist = g.get("checklist") or g.get("observations") or g.get("recommendations") or []
    scrubbed = (
        _scrub_tech_list(checklist)
        if checklist and not isinstance(checklist[0], dict)
        else checklist
    )
    return _module(
        "grooming",
        "Grooming",
        g.get("summary") or g.get("interval_label") or "Grooming guidance",
        {
            "interval": g.get("interval") or g.get("recommended_interval"),
            "checklist": scrubbed,
            "notes": g.get("notes") or "",
        },
        priority=55,
    )


def _packages_module(analyze: dict[str, Any]) -> dict[str, Any]:
    pkgs = analyze.get("wellnessPackages") or []
    details = analyze.get("packageDetails") or {}
    tiers = []
    for p in pkgs:
        if not isinstance(p, dict):
            continue
        tier = p.get("tier") or p.get("package_id") or p.get("id")
        products = []
        for prod in p.get("products_included") or []:
            if not isinstance(prod, dict):
                continue
            products.append(
                {
                    "product_id": prod.get("product_id"),
                    "name": prod.get("name") or prod.get("product_name"),
                    "serving": prod.get("serving_size") or prod.get("daily_amount") or prod.get("serving"),
                    "monthly_cost": prod.get("monthly_cost"),
                    "why_selected": prod.get("why_selected") or prod.get("reason") or "",
                    "category": prod.get("type") or prod.get("category"),
                }
            )
        detail = details.get(str(tier)) or details.get(tier) or {}
        tiers.append(
            {
                "tier": tier,
                "title": p.get("title") or tier,
                "recommended": bool(p.get("recommended")),
                "monthly_cost": p.get("monthly_cost"),
                "yearly_cost": p.get("yearly_cost"),
                "coverage_score": p.get("coverage_score"),
                "overall_score": p.get("overall_score"),
                "summary": p.get("package_summary") or p.get("tagline") or p.get("overview") or "",
                "products": products,
                "product_ids": [x["product_id"] for x in products if x.get("product_id")],
                "detail": {
                    "coverage": detail.get("coverage") or detail.get("coverage_matrix"),
                    "rationale": detail.get("rationale") or detail.get("why") or p.get("package_summary"),
                    "plan_365": detail.get("yearly_plan") or detail.get("plan_365") or p.get("yearly_plan"),
                    "feeding": detail.get("feeding") or detail.get("daily_schedule"),
                },
            }
        )
    rec = next((t for t in tiers if t.get("recommended")), tiers[1] if len(tiers) > 1 else (tiers[0] if tiers else None))
    summary = f"Recommended · {rec['title']}" if rec else "Care pathways"
    return _module(
        "packages",
        "Care packages",
        summary,
        {"tiers": tiers, "recommended_tier": rec.get("tier") if rec else None},
        priority=30,
    )


def _products_module(analyze: dict[str, Any]) -> dict[str, Any]:
    recs = analyze.get("productRecommendations") or analyze.get("products") or []
    analyses = analyze.get("productAnalyses") or {}
    items = []
    by_id: dict[str, Any] = {}
    for p in recs:
        if not isinstance(p, dict):
            continue
        pid = str(p.get("product_id") or "")
        entry = {
            "product_id": pid,
            "name": p.get("product_name") or p.get("name") or pid,
            "category": p.get("category") or p.get("type"),
            "summary": p.get("short_description") or p.get("description") or p.get("why") or "",
            "monthly_cost": p.get("monthly_cost") or p.get("unit_cost"),
            "serving": p.get("serving") or p.get("daily_amount"),
        }
        items.append(entry)
        if pid:
            by_id[pid] = {**entry, "analysis": analyses.get(pid) or {}}
    for pid, analysis in (analyses.items() if isinstance(analyses, dict) else []):
        if pid not in by_id:
            by_id[str(pid)] = {"product_id": str(pid), "analysis": analysis}
    return _module(
        "products",
        "Products",
        f"{len(items)} matched products" if items else "Product matches",
        {"items": items, "by_id": by_id},
        priority=32,
    )


def _evidence_module(analyze: dict[str, Any]) -> dict[str, Any]:
    raw = analyze.get("scientificEvidence") or analyze.get("evidence") or []
    research = analyze.get("researchSection") or {}
    items = []
    for i, e in enumerate(raw if isinstance(raw, list) else []):
        if not isinstance(e, dict):
            continue
        items.append(
            {
                "evidence_id": e.get("id") or e.get("evidence_id") or f"ev_{i}",
                "title": e.get("title") or e.get("source_name") or "Veterinary literature",
                "journal": e.get("journal") or e.get("source_name"),
                "year": e.get("year"),
                "doi": e.get("doi"),
                "url": e.get("source_url") or e.get("url"),
                "quoted_finding": e.get("finding") or e.get("quote") or e.get("summary") or "",
                "evidence_level": e.get("evidence_level") or e.get("level"),
                "supports": _scrub_tech_list(e.get("supports") or e.get("conditions")),
                "status": e.get("status") or ("linked" if (e.get("source_url") or e.get("url")) else "pending"),
            }
        )
    return _module(
        "evidence",
        "Evidence",
        f"{len(items)} scientific references" if items else "Scientific references",
        {"items": items, "research": research if isinstance(research, dict) else {}},
        priority=60,
    )


def _validation_module(analyze: dict[str, Any]) -> dict[str, Any]:
    """Structured validation slots — populated when published benchmarks exist."""
    items = []
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        title = _plain_label(h.get("title") or h.get("condition") or "Condition")
        est = h.get("biological_risk_percent") or h.get("risk_percent")
        if isinstance(est, float) and est <= 1:
            est = round(est * 100, 1)
        bench = h.get("published_benchmark_pct") or h.get("benchmark_pct")
        if bench is not None:
            items.append(
                {
                    "validation_id": f"val_{h.get('condition_key') or title}",
                    "subject": {"type": "condition", "title": title},
                    "ppie_estimate_pct": est,
                    "published_benchmark_pct": bench,
                    "published_range_pct": h.get("published_range_pct"),
                    "confidence": h.get("confidence") or "moderate",
                    "status": "compared",
                }
            )
        else:
            items.append(
                {
                    "validation_id": f"val_{h.get('condition_key') or title}",
                    "subject": {"type": "condition", "title": title},
                    "ppie_estimate_pct": est,
                    "published_benchmark_pct": None,
                    "status": "unavailable",
                    "reason": "No high-quality prevalence study is linked for this exact population.",
                    "confidence": h.get("confidence") or "high",
                    "derived_from": [
                        "breed biology",
                        "trait interactions",
                        "environment",
                        "nutrition context",
                    ],
                }
            )
    return _module(
        "validation",
        "Validation",
        f"{len(items)} clinical estimates reviewed" if items else "Validation",
        {"items": items},
        priority=65,
    )


def _confidence_module(analyze: dict[str, Any]) -> dict[str, Any]:
    insights = analyze.get("healthInsights") or []
    pkgs = analyze.get("wellnessPackages") or []
    evidence = analyze.get("scientificEvidence") or []
    data = {
        "breed_resolution": "high" if (analyze.get("biology") or {}).get("resolved_breeds") or (analyze.get("profile") or {}).get("breeds") else "low",
        "evidence_coverage": "moderate" if evidence else "pending",
        "package_ready": bool(pkgs),
        "priority_count": len(insights) if isinstance(insights, list) else 0,
        "notes": "Confidence reflects data completeness for this assessment run.",
    }
    return _module("confidence", "Confidence", "Assessment confidence", data, priority=90)


def build_clinical_assessment(repo: DataRepository, analyze: dict[str, Any]) -> dict[str, Any]:
    """Build modular ClinicalAssessment from frozen analyze output (no recalculation)."""
    modules = {
        "profile": _profile_module(analyze),
        "breed": _breed_module(analyze),
        "traits": _traits_module(analyze),
        "behavior": _behavior_module(analyze),
        "environment": _environment_module(analyze),
        "health": _health_module(analyze),
        "nutrition": _nutrition_module(analyze),
        "activity": _activity_module(analyze),
        "grooming": _grooming_module(analyze),
        "packages": _packages_module(analyze),
        "products": _products_module(analyze),
        "evidence": _evidence_module(analyze),
        "validation": _validation_module(analyze),
        "confidence": _confidence_module(analyze),
    }
    meta = {
        "algorithm_version": ALGORITHM_VERSION,
        "data_version": getattr(repo, "version", None) or "",
        "content_hash": getattr(repo, "csv_hash", None) or "",
        "generated_at": _now_iso(),
        "assessment_schema": ASSESSMENT_SCHEMA,
        "engine": "PPIE",
    }
    # Flat contract aliases (data payload) + modules envelope for independent cache keys
    assessment: dict[str, Any] = {
        "meta": meta,
        "modules": modules,
        "module_ids": list(MODULE_IDS),
    }
    for mid in MODULE_IDS:
        assessment[mid] = modules[mid]["data"]
        assessment[f"{mid}_module"] = modules[mid]
    return assessment


def get_assessment_module(assessment: dict[str, Any], module_id: str) -> dict[str, Any] | None:
    modules = assessment.get("modules") or {}
    return modules.get(module_id)
