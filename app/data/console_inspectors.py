"""
Validation Console inspectors — project frozen analyze into debug views.

Never recomputes clinical formulas. Marks gaps as NOT CURRENTLY TRACEABLE.
"""

from __future__ import annotations

from typing import Any

from app.inference.formula_registry import (
    FORMULA_COVERAGE,
    FORMULA_EVIDENCE,
    FORMULA_NUTRIENT,
    FORMULA_PACKAGE,
    FORMULA_PRODUCT,
    FORMULA_RISK,
    FORMULA_RISK_TRACE,
    formula_dependency_edges,
    formula_list,
)
from app.inference.models import NOT_TRACEABLE
from app.inference.resolver import component_to_ingredient_key, ingredient_key, normalize_label
from app.inference.risk import build_risk_modifier_ledger


def _nt(reason: str, *, needs: str | None = None) -> dict[str, Any]:
    return {
        "status": NOT_TRACEABLE,
        "traceable": False,
        "reason": reason,
        "needs_engine_instrumentation": needs
        or "Emit named debug fields from the production stage (no equation text).",
    }


def expand_risk_ledgers(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Full risk chain for every healthInsight / debug risk_trace (emitted + honest gaps)."""
    calc_by = {
        str(c.get("condition")): c for c in (analyze.get("calculationTrace") or []) if isinstance(c, dict)
    }
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    by_condition = debug.get("risk_by_condition") if isinstance(debug.get("risk_by_condition"), dict) else {}
    fx_by = (
        debug.get("formula_execution_by_condition")
        if isinstance(debug.get("formula_execution_by_condition"), dict)
        else {}
    )
    traces = list(debug.get("risk_traces") or [])
    executions = list(debug.get("formula_executions") or [])
    # Also index traces by condition name
    for t in traces:
        if isinstance(t, dict) and t.get("condition"):
            by_condition.setdefault(str(t["condition"]), t)
    for fx in executions:
        if isinstance(fx, dict) and fx.get("condition"):
            fx_by.setdefault(str(fx["condition"]), fx)

    out = []
    # Prefer per-condition production traces (condition grain), then insights (goal grain)
    seen = set()
    for t in traces:
        if not isinstance(t, dict):
            continue
        cond = str(t.get("condition") or "")
        if not cond or cond in seen:
            continue
        seen.add(cond)
        base = build_risk_modifier_ledger(calc_row=calc_by.get(cond), observatory_trace=t)
        base["expanded_chain"] = base.get("steps") or []
        base["csv_lookups"] = t.get("csv_refs") or (calc_by.get(cond) or {}).get("published_evidence") or []
        base["decision_tree"] = (calc_by.get(cond) or {}).get("decision_log") or [
            {"logic": t.get("logic"), "groomer_boosted": t.get("groomer_boosted")}
        ]
        base["code"] = t.get("code")
        fx = fx_by.get(cond)
        if fx:
            base["formula_execution"] = fx
            # Prefer execution lookups (with csv_row) when present
            if fx.get("lookups"):
                base["csv_lookups"] = fx["lookups"]
        out.append(base)

    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        title = str(h.get("title") or "")
        # Skip if we already have condition-level traces covering supporting conditions
        supports = [str(x) for x in (h.get("supporting_conditions") or []) if x]
        if any(s in seen for s in supports):
            continue
        ot = by_condition.get(title)
        base = build_risk_modifier_ledger(h, calc_row=calc_by.get(title), observatory_trace=ot)
        if not base.get("expanded_chain"):
            # legacy expanded slot mapping
            chain = []
            emitted = {s.get("name"): s for s in base.get("steps") or []}
            for key, label in [
                ("baseline", "baseline / breed prevalence"),
                ("interaction", "trait interaction"),
                ("benefit", "benefit reductions"),
                ("mixed_breed", "mixed-breed adjustment"),
                ("age", "age modifier"),
                ("activity", "activity modifier"),
                ("weight", "weight modifier"),
                ("climate", "climate modifier"),
                ("final", "final risk"),
            ]:
                hit = emitted.get(key) or emitted.get(f"{key}_modifier") or emitted.get(
                    "baseline_observed_prevalence" if key == "baseline" else ""
                ) or emitted.get("final_probability" if key == "final" else "")
                if hit and hit.get("traceable"):
                    chain.append({**hit, "label": label})
                else:
                    chain.append(
                        {
                            "name": key,
                            "label": label,
                            "traceable": False,
                            "status": NOT_TRACEABLE,
                            "reason": f"Intermediate `{label}` not in observatory trace",
                        }
                    )
            base["expanded_chain"] = chain
        base["csv_lookups"] = (ot or {}).get("csv_refs") or (calc_by.get(title) or {}).get("published_evidence") or []
        fx = fx_by.get(title)
        if fx:
            base["formula_execution"] = fx
            if fx.get("lookups"):
                base["csv_lookups"] = fx["lookups"]
        out.append(base)
    return out


def formula_execution_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Project analyze.debug.formula_executions — engine-emitted ledgers only."""
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    rows = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        lookups = list(fx.get("lookups") or [])
        with_row = sum(1 for lu in lookups if isinstance(lu, dict) and lu.get("csv_row") not in (None, ""))
        conf = list(fx.get("confidence") or fx.get("confidence_steps") or [])
        rows.append(
            {
                "schema": fx.get("schema") or "formula_execution.v2",
                "formula_id": fx.get("formula_id") or FORMULA_RISK,
                "formula_name": fx.get("formula_name"),
                "stage": fx.get("stage"),
                "condition": fx.get("condition"),
                "subject": fx.get("subject") or fx.get("condition"),
                "inputs": fx.get("inputs") or {},
                "steps": fx.get("steps") or [],
                "modifiers": fx.get("modifiers") or [],
                "decisions": fx.get("decisions") or [],
                "competitions": fx.get("competitions") or [],
                "confidence": conf,
                "confidence_steps": conf,
                "lookups": lookups,
                "outputs": fx.get("outputs") or {},
                "timing": fx.get("timing") or {},
                "consumers": fx.get("consumers") or [],
                "provenance": fx.get("provenance") or [],
                "code": fx.get("code"),
                "lookup_row_coverage": {
                    "total": len(lookups),
                    "with_csv_row": with_row,
                    "pct": round(100.0 * with_row / len(lookups), 1) if lookups else None,
                },
                "emitted_by_engine": True,
            }
        )
    return rows


def decision_ledger_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    if debug.get("decision_ledger"):
        return list(debug["decision_ledger"])
    out = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for d in fx.get("decisions") or []:
            if isinstance(d, dict):
                out.append({**d, "formula_id": fx.get("formula_id"), "subject_ctx": fx.get("subject")})
    return out


def provenance_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    if debug.get("provenance_index"):
        return list(debug["provenance_index"])
    out = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for p in fx.get("provenance") or []:
            if isinstance(p, dict):
                out.append({**p, "formula_id": fx.get("formula_id"), "stage": fx.get("stage")})
    return out


def competition_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    out = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for c in fx.get("competitions") or []:
            if isinstance(c, dict):
                out.append(
                    {
                        **c,
                        "formula_id": fx.get("formula_id"),
                        "subject": fx.get("subject") or fx.get("condition"),
                    }
                )
    return out


def nutrition_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for t in analyze.get("nutritionalTargets") or []:
        if not isinstance(t, dict):
            continue
        name = t.get("ingredient") or t.get("nutrient") or t.get("name")
        rows.append(
            {
                "formula_id": FORMULA_NUTRIENT,
                "condition": t.get("condition") or t.get("supports_condition") or NOT_TRACEABLE,
                "ingredient": name,
                "daily_target": t.get("daily_target") or t.get("target") or t.get("dose"),
                "unit": t.get("unit"),
                "chain": [
                    {"step": "condition", "value": t.get("condition"), "traceable": t.get("condition") is not None},
                    {
                        "step": "ingredient_rule",
                        "value": name,
                        "traceable": name is not None,
                        "csv": "condition_ingredients_*",
                    },
                    {
                        "step": "weight_calculation",
                        **_nt("Dose×weight intermediate not always emitted separately"),
                    },
                    {
                        "step": "daily_target",
                        "value": t.get("daily_target") or t.get("target"),
                        "traceable": True,
                    },
                    {
                        "step": "product_contribution",
                        **_nt("Per-product contribution split not on nutritionalTargets"),
                    },
                    {
                        "step": "food_contribution",
                        **_nt("Food vs supplement split often missing"),
                    },
                    {
                        "step": "coverage",
                        "value": t.get("coverage_percent") or t.get("coverage"),
                        "traceable": t.get("coverage_percent") is not None or t.get("coverage") is not None,
                        "formula_id": FORMULA_COVERAGE,
                    },
                    {
                        "step": "remaining_requirement",
                        **_nt("Remaining requirement field not standard on targets"),
                    },
                ],
                "raw": t,
            }
        )
    return rows


def ingredient_resolution_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Show resolution path for ingredients appearing in analyze (resolver view, not rescore)."""
    names: list[str] = []
    for t in analyze.get("nutritionalTargets") or []:
        if isinstance(t, dict):
            n = t.get("ingredient") or t.get("nutrient") or t.get("name")
            if n:
                names.append(str(n))
    for p in analyze.get("productRecommendations") or []:
        if isinstance(p, dict):
            for a in p.get("actives") or p.get("active_ingredients") or []:
                if isinstance(a, dict) and a.get("name"):
                    names.append(str(a["name"]))
                elif isinstance(a, str):
                    names.append(a)

    seen = set()
    out = []
    for raw in names:
        key = ingredient_key(raw)
        if key in seen:
            continue
        seen.add(key)
        canon = component_to_ingredient_key(raw)
        out.append(
            {
                "original": raw,
                "normalized": normalize_label(raw).lower(),
                "ingredient_key": key,
                "canonical_key": canon,
                "alias_match": key != canon or key == canon,
                "chain": [
                    {"step": "original", "value": raw, "traceable": True},
                    {"step": "normalized", "value": normalize_label(raw).lower(), "traceable": True},
                    {
                        "step": "alias_match",
                        "value": canon,
                        "traceable": True,
                        "note": "Formatting normalize + known remaps in resolver (CSV aliases applied in pipeline)",
                    },
                    {"step": "canonical_key", "value": canon, "traceable": True},
                    {"step": "taxonomy", **_nt("Taxonomy walk not logged per request")},
                    {"step": "mechanisms", **_nt("Attach from ingredient_mechanisms at request time not traced")},
                    {"step": "evidence", **_nt("See Evidence tab for attached papers")},
                    {"step": "products_matched", **_nt("Inverse product→ingredient match log not emitted")},
                    {"step": "coverage", **_nt("See Coverage / Packages")},
                    {"step": "confidence", **_nt("Per-ingredient confidence ladder not on analyze")},
                ],
            }
        )
    return out


def product_match_inspector(analyze: dict[str, Any]) -> dict[str, Any]:
    selected = []
    for p in analyze.get("productRecommendations") or []:
        if not isinstance(p, dict):
            continue
        selected.append(
            {
                "formula_id": FORMULA_PRODUCT,
                "product_id": p.get("product_id") or p.get("id"),
                "name": p.get("product_name") or p.get("name"),
                "chain": [
                    {"step": "candidate", "value": p.get("product_name") or p.get("name"), "traceable": True},
                    {
                        "step": "ingredient_overlap",
                        **_nt("Overlap score not on productRecommendations row"),
                    },
                    {
                        "step": "coverage",
                        "value": p.get("coverage_pct") or p.get("coverage"),
                        "traceable": p.get("coverage_pct") is not None or p.get("coverage") is not None,
                    },
                    {"step": "evidence_score", **_nt("Per-product evidence score not emitted on recommendation card")},
                    {"step": "clinical_function", **_nt("Function score not on recommendation card")},
                    {"step": "cost_efficiency", **_nt("Cost efficiency term not on recommendation card")},
                    {"step": "diversity", **_nt("Diversity term not on recommendation card")},
                    {
                        "step": "overall_score",
                        "value": p.get("score") or p.get("overall_score"),
                        "traceable": p.get("score") is not None or p.get("overall_score") is not None,
                    },
                ],
                "raw": {k: p.get(k) for k in ("product_id", "product_name", "category", "monthly_cost") if k in p},
            }
        )

    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    rejected = list(debug.get("package_rejects") or [])
    if not rejected:
        for pkg in analyze.get("wellnessPackages") or []:
            if isinstance(pkg, dict):
                for rej in pkg.get("products_rejected") or []:
                    if isinstance(rej, dict):
                        rejected.append({**rej, "tier": pkg.get("tier")})

    return {
        "formula_id": FORMULA_PRODUCT,
        "selected": selected,
        "rejected": rejected,
        "rejected_note": (
            None
            if rejected
            else "No products_rejected on wellnessPackages / debug.package_rejects"
        ),
    }


def package_optimizer_inspector(analyze: dict[str, Any]) -> dict[str, Any]:
    tiers = []
    for p in analyze.get("wellnessPackages") or []:
        if not isinstance(p, dict):
            continue
        products = p.get("products_included") or p.get("product_cards") or []
        rejected = p.get("products_rejected") or []
        breakdown = p.get("score_breakdown") or {}
        obs = p.get("observatory") if isinstance(p.get("observatory"), dict) else {}
        tiers.append(
            {
                "tier": p.get("tier"),
                "title": p.get("title"),
                "recommended": bool(p.get("recommended")),
                "coverage_score": p.get("coverage_score"),
                "overall_score": p.get("overall_score"),
                "monthly_cost": p.get("monthly_cost"),
                "yearly_cost": p.get("yearly_cost"),
                "score_breakdown": breakdown,
                "candidates_evaluated_count": p.get("candidates_evaluated_count"),
                "chain": [
                    {
                        "step": "candidate_products",
                        "value": p.get("candidates_evaluated_count") or len(products),
                        "traceable": True,
                    },
                    {
                        "step": "coverage_matrix",
                        "value": p.get("coverage_score"),
                        "traceable": p.get("coverage_score") is not None,
                        "formula_id": FORMULA_COVERAGE,
                        "matrix": p.get("coverage_matrix"),
                    },
                    {
                        "step": "score_breakdown",
                        "value": breakdown,
                        "traceable": bool(breakdown),
                    },
                    {
                        "step": "optimization_passes",
                        **_nt(
                            "Per-pass candidate trial scores not stored",
                            needs="Emit optimization_passes[] from greedy/best-add loops",
                        ),
                    },
                    {"step": "tier_assignment", "value": p.get("tier"), "traceable": True},
                    {"step": "final_package", "value": p.get("title"), "traceable": True},
                ],
                "products_selected": [
                    {
                        "product_id": x.get("product_id"),
                        "name": x.get("name") or x.get("product_name"),
                        "why_selected": x.get("why_selected") or x.get("reason") or NOT_TRACEABLE,
                    }
                    for x in (products if isinstance(products, list) else [])
                    if isinstance(x, dict)
                ],
                "removed_products": rejected,
                "observatory": obs,
            }
        )
    return {"formula_id": FORMULA_PACKAGE, "tiers": tiers}


def evidence_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for e in analyze.get("scientificEvidence") or []:
        if not isinstance(e, dict):
            continue
        out.append(
            {
                "formula_id": FORMULA_EVIDENCE,
                "title": e.get("title") or e.get("source_name"),
                "condition": e.get("condition") or e.get("linked_condition"),
                "ingredient": e.get("ingredient") or e.get("ingredient_name"),
                "year": e.get("year"),
                "url": e.get("url") or e.get("source_url"),
                "pmid": e.get("pmid") or NOT_TRACEABLE,
                "doi": e.get("doi") or NOT_TRACEABLE,
                "chain": [
                    {"step": "condition", "value": e.get("condition"), "traceable": bool(e.get("condition"))},
                    {
                        "step": "evidence_row",
                        "value": e.get("title") or e.get("source_name"),
                        "traceable": True,
                        "csv": "ingredient_evidence_* / clinical_evidence_base",
                    },
                    {"step": "mechanisms", **_nt("Mechanism join not always on evidence card")},
                    {
                        "step": "evidence_strength",
                        "value": e.get("evidence_level") or e.get("strength"),
                        "traceable": e.get("evidence_level") is not None or e.get("strength") is not None,
                    },
                    {"step": "final_ranking", **_nt("Rank position not always emitted")},
                ],
                "raw": e,
            }
        )
    return out


def confidence_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        conf = h.get("confidence_percent")
        rows.append(
            {
                "condition": h.get("title"),
                "final_confidence_percent": conf,
                "formula_id": FORMULA_RISK,
                "chain": [
                    {"step": "base_confidence", **_nt("Base confidence intermediate not emitted")},
                    {"step": "evidence_quality", **_nt("Evidence quality factor not emitted")},
                    {"step": "data_completeness", **_nt("Completeness factor not emitted")},
                    {"step": "inference_penalty", **_nt("Inference penalty not emitted")},
                    {"step": "estimated_value_penalty", **_nt("Estimate penalty not emitted")},
                    {
                        "step": "final_confidence",
                        "value": conf,
                        "unit": "%",
                        "traceable": conf is not None,
                        "source": "healthInsights.confidence_percent",
                    },
                ],
            }
        )
    return rows


def coverage_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Coverage from package / nutrition fields already on analyze."""
    rows = []
    for p in analyze.get("wellnessPackages") or []:
        if isinstance(p, dict) and p.get("coverage_score") is not None:
            rows.append(
                {
                    "scope": "package",
                    "tier": p.get("tier"),
                    "coverage_score": p.get("coverage_score"),
                    "formula_id": FORMULA_COVERAGE,
                    "traceable": True,
                }
            )
    for t in analyze.get("nutritionalTargets") or []:
        if isinstance(t, dict) and (t.get("coverage_percent") is not None or t.get("coverage") is not None):
            rows.append(
                {
                    "scope": "nutrient",
                    "name": t.get("ingredient") or t.get("nutrient"),
                    "coverage": t.get("coverage_percent") or t.get("coverage"),
                    "formula_id": FORMULA_COVERAGE,
                    "traceable": True,
                }
            )
    return rows


def pipeline_timeline(analyze: dict[str, Any], timings: dict[str, float] | None) -> list[dict[str, Any]]:
    stages = [
        ("payload", "Payload / profile"),
        ("biology", "Breed / Traits"),
        ("health_risk", "Risk"),
        ("epidemiology", "Epidemiology"),
        ("management", "Management"),
        ("nutrition", "Nutrition"),
        ("optimization", "Products / Optimization"),
        ("assembly", "Assembly"),
    ]
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    stage_ms = dict(debug.get("stage_timings_ms") or {})
    if timings:
        stage_ms.update({k: v for k, v in timings.items() if isinstance(v, (int, float))})

    pipe = analyze.get("pipeline_trace") or []
    by_stage = {}
    for s in pipe:
        if isinstance(s, dict):
            by_stage[str(s.get("stage") or "").lower()] = s

    out = []
    cumulative = 0.0
    for sid, label in stages:
        hit = by_stage.get(sid)
        if not hit:
            for k, v in by_stage.items():
                if sid in k or label.lower().split()[0].lower() in k:
                    hit = v
                    break
        ms = stage_ms.get(sid)
        if isinstance(ms, (int, float)):
            cumulative += float(ms)
        out.append(
            {
                "id": sid,
                "label": label,
                "record_count": (hit or {}).get("record_count") or (hit or {}).get("record_counts"),
                "source_files": (hit or {}).get("source_files") or [],
                "elapsed_ms": ms if ms is not None else NOT_TRACEABLE,
                "cumulative_ms": round(cumulative, 3) if ms is not None else NOT_TRACEABLE,
                "message": (hit or {}).get("message") or (hit or {}).get("label"),
                "present": hit is not None or ms is not None,
            }
        )
    if stage_ms.get("total_pipeline") is not None:
        out.append(
            {
                "id": "total",
                "label": "Total pipeline",
                "elapsed_ms": stage_ms["total_pipeline"],
                "present": True,
            }
        )
    return out


def performance_inspector(analyze: dict[str, Any], timings: dict[str, float] | None) -> dict[str, Any]:
    pipe = analyze.get("pipeline_trace") or []
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    stage_ms = debug.get("stage_timings_ms") or {}
    return {
        "wrapper_timings": timings or {},
        "stage_timings_ms": stage_ms if stage_ms else NOT_TRACEABLE,
        "lookup_counts": NOT_TRACEABLE,
        "rows_scanned": NOT_TRACEABLE,
        "rows_matched": [
            {"stage": s.get("stage"), "record_count": s.get("record_count") or s.get("record_counts")}
            for s in pipe
            if isinstance(s, dict)
        ],
        "cache_hits": NOT_TRACEABLE,
        "note": "Stage wall-clock from engine.perf_counter. Cache/lookup counts still require data-layer instrumentation.",
    }


def csv_dependency_viewer(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for s in analyze.get("pipeline_trace") or []:
        if not isinstance(s, dict):
            continue
        for f in s.get("source_files") or []:
            rows.append(
                {
                    "stage": s.get("stage"),
                    "csv": f,
                    "record_counts": s.get("record_counts"),
                    "matched_row_id": NOT_TRACEABLE,
                    "ignored_rows": NOT_TRACEABLE,
                    "joins": NOT_TRACEABLE,
                }
            )
    return rows


def formula_graph() -> dict[str, Any]:
    return {
        "nodes": formula_list(),
        "edges": formula_dependency_edges(),
    }


def decision_trees(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    trees = []
    for c in analyze.get("calculationTrace") or []:
        if not isinstance(c, dict):
            continue
        log = c.get("decision_log") or []
        trees.append(
            {
                "condition": c.get("condition"),
                "formula_id": FORMULA_RISK,
                "nodes": log
                if log
                else [
                    {"input": c.get("condition"), "decision": NOT_TRACEABLE, "why": "No decision_log on calculationTrace"}
                ],
            }
        )
    return trees


def build_search_index(console_sections: dict[str, Any]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for f in formula_list():
        hits.append(
            {
                "kind": "formula_id",
                "label": f["formula_id"],
                "nav": "formulas",
                "purpose": f.get("purpose"),
            }
        )
        for dep in f.get("depends_on") or []:
            hits.append({"kind": "formula_id", "label": dep, "nav": "graph"})
    for ex in console_sections.get("risk_ledgers") or []:
        hits.append({"kind": "condition", "label": ex.get("condition"), "nav": "risks"})
    for e in console_sections.get("evidence") or []:
        hits.append({"kind": "evidence", "label": e.get("title"), "nav": "evidence"})
        if e.get("pmid") and e["pmid"] != NOT_TRACEABLE:
            hits.append({"kind": "pmid", "label": str(e["pmid"]), "nav": "evidence"})
        if e.get("mechanism"):
            hits.append({"kind": "mechanism", "label": e.get("mechanism"), "nav": "evidence"})
        if e.get("ingredient"):
            hits.append({"kind": "ingredient", "label": e.get("ingredient"), "nav": "evidence"})
    for ing in console_sections.get("ingredients") or []:
        hits.append({"kind": "ingredient", "label": ing.get("original"), "nav": "ingredients"})
        if ing.get("canonical_key"):
            hits.append({"kind": "ingredient", "label": ing.get("canonical_key"), "nav": "ingredients"})
    for row in console_sections.get("csv_lookups") or []:
        hits.append({"kind": "csv", "label": row.get("csv"), "nav": "csv"})
    products = console_sections.get("products") or {}
    for p in products.get("selected") or []:
        hits.append({"kind": "product", "label": p.get("name"), "nav": "products"})
    for n in console_sections.get("nutrition") or []:
        hits.append({"kind": "ingredient", "label": n.get("ingredient"), "nav": "nutrition"})
    for rej in (console_sections.get("products") or {}).get("rejected") or []:
        if isinstance(rej, dict):
            hits.append(
                {
                    "kind": "product",
                    "label": rej.get("product_name") or rej.get("product_id"),
                    "nav": "products",
                }
            )
    seen: set[tuple[str, str]] = set()
    deduped = []
    for h in hits:
        if not h.get("label"):
            continue
        key = (str(h.get("kind")), str(h.get("label")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(h)
    return deduped


# --- Phase 5 observatory projections (read-only) ---

CODE_TRACE = {
    "PROFILE_NORMALIZE_V2_1": {
        "file": "app/api/payload_adapter.py",
        "function": "profile_from_analyze_body",
    },
    "BREED_RESOLVE_V2_1": {"file": "app/agent/stages/biological.py", "function": "run_biological_stage"},
    "TRAIT_BLEND_V2_1": {"file": "app/agent/stages/biological.py", "function": "run_biological_stage"},
    "RISK_V2_1": {"file": "app/agent/stages/health_risk.py", "function": "compute_risks"},
    "NUTRIENT_TARGET_V2_1": {"file": "app/agent/stages/nutrition.py", "function": "run_nutrition_stage"},
    "PRODUCT_MATCH_V2_1": {"file": "app/agent/stages/optimization.py", "function": "run_optimization_stage"},
    "PACKAGE_OPTIMIZER_V2_1": {
        "file": "app/agent/package_optimizer.py",
        "function": "build_optimized_packages",
    },
    "COVERAGE_V2_1": {"file": "app/agent/package_optimizer.py", "function": "coverage_matrix"},
    "EVIDENCE_RANK_V2_1": {"file": "app/agent/response_assembler.py", "function": "collect_evidence"},
    "ASSESSMENT_PROJECT_V1": {
        "file": "app/data/clinical_assessment.py",
        "function": "build_clinical_assessment",
    },
}

CSV_USAGE_MAP = {
    "BREEDS.csv": {"functions": ["run_biological_stage", "_breed_records"], "formulas": ["BREED_RESOLVE_V2_1", "TRAIT_BLEND_V2_1"]},
    "BREED_CONDITIONS.csv": {"functions": ["_breed_observed", "compute_risks"], "formulas": ["RISK_V2_1"]},
    "TRAIT_INTERACTIONS.csv": {"functions": ["compute_evidence_scores"], "formulas": ["RISK_V2_1"]},
    "TRAIT_BENEFITS.csv": {"functions": ["apply_benefit_reductions"], "formulas": ["RISK_V2_1"]},
    "MIXED_BREED_MATRIX.csv": {"functions": ["apply_mixed_breed_nudge"], "formulas": ["RISK_V2_1"]},
    "CONDITION_INGREDIENTS.csv": {"functions": ["run_nutrition_stage", "map_ingredients"], "formulas": ["NUTRIENT_TARGET_V2_1"]},
    "NUTRIENT_PRIORITIES.csv": {"functions": ["response_assembler"], "formulas": ["NUTRIENT_TARGET_V2_1"]},
    "INGREDIENT_EVIDENCE.csv": {"functions": ["collect_evidence", "ingredient_engine"], "formulas": ["EVIDENCE_RANK_V2_1"]},
    "PRODUCT_CATALOG.csv": {"functions": ["load_candidate_products"], "formulas": ["PRODUCT_MATCH_V2_1", "PACKAGE_OPTIMIZER_V2_1"]},
    "PRODUCT_COMPONENTS.csv": {"functions": ["coverage_matrix", "package_optimizer"], "formulas": ["COVERAGE_V2_1"]},
    "PACKAGE_TIERS.csv": {"functions": ["_pick_staple"], "formulas": ["PACKAGE_OPTIMIZER_V2_1"]},
}


def formula_explorer() -> list[dict[str, Any]]:
    rows = []
    for f in formula_list():
        fid = f["formula_id"]
        code = CODE_TRACE.get(fid) or {
            "file": f.get("owner_module"),
            "function": NOT_TRACEABLE,
        }
        rows.append(
            {
                **f,
                "description": f.get("purpose"),
                "code_file": code.get("file"),
                "python_function": code.get("function"),
                "equation": {
                    "policy": "formula_id_only",
                    "exposed": False,
                    "note": "Proprietary equation text is not exposed. Use observatory step ops (baseline/multiply/set).",
                },
                "example_output": NOT_TRACEABLE,
            }
        )
    return rows


def pipeline_dag() -> dict[str, Any]:
    nodes = [
        "payload",
        "biology",
        "health_risk",
        "epidemiology",
        "management",
        "nutrition",
        "optimization",
        "assembly",
        "assessment",
    ]
    edges = [
        {"from": "payload", "to": "biology"},
        {"from": "biology", "to": "health_risk"},
        {"from": "health_risk", "to": "epidemiology"},
        {"from": "epidemiology", "to": "management"},
        {"from": "epidemiology", "to": "nutrition"},
        {"from": "nutrition", "to": "optimization"},
        {"from": "optimization", "to": "assembly"},
        {"from": "assembly", "to": "assessment"},
    ]
    return {"nodes": nodes, "edges": edges, "kind": "pipeline_dag"}


def observability_coverage(analyze: dict[str, Any], risk_ledgers: list, packages: dict) -> dict[str, Any]:
    """Percent of inspector slots that are traceable (not NT)."""

    def _pct(items: list[bool]) -> float:
        if not items:
            return 0.0
        return round(100.0 * sum(1 for x in items if x) / len(items), 1)

    risk_flags = []
    for r in risk_ledgers:
        for s in r.get("expanded_chain") or r.get("steps") or []:
            if s.get("status") == "NOT_APPLIED_IN_RISK_V2_1":
                continue  # not a gap — intentionally unused
            risk_flags.append(bool(s.get("traceable")))

    pkg_flags = []
    for t in packages.get("tiers") or []:
        for s in t.get("chain") or []:
            pkg_flags.append(bool(s.get("traceable")))
        pkg_flags.append(isinstance(t.get("removed_products"), list))

    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    has_timings = bool(debug.get("stage_timings_ms"))
    has_risk_traces = bool(debug.get("risk_traces"))
    has_fx = bool(debug.get("formula_executions"))

    csv_flags = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for lu in fx.get("lookups") or []:
            if isinstance(lu, dict):
                csv_flags.append(lu.get("csv_row") not in (None, ""))

    areas = {
        "risk": _pct(risk_flags) if risk_flags else (100.0 if has_risk_traces else 0.0),
        "formula_execution": 100.0 if has_fx else 0.0,
        "packages": _pct(pkg_flags),
        "timings": 100.0 if has_timings else 0.0,
        "nutrition": 80.0 if any(
            isinstance(fx, dict) and fx.get("formula_id") == "NUTRIENT_TARGET_V2_1"
            for fx in (debug.get("formula_executions") or [])
        )
        else 50.0,
        "products": 40.0 if (analyze.get("productRecommendations")) else 0.0,
        "confidence": 80.0 if has_fx else 30.0,
        "csv_row_ids": _pct(csv_flags) if csv_flags else 0.0,
        "decisions": 100.0 if debug.get("decision_ledger") else 40.0,
    }
    vals = list(areas.values())
    areas["backend"] = round(sum(vals) / len(vals), 1) if vals else 0.0
    return areas


def missing_data_report(analyze: dict[str, Any], risk_ledgers: list) -> list[dict[str, Any]]:
    gaps = []
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    if not debug.get("risk_traces"):
        gaps.append({"kind": "missing_formula_trace", "area": "risk", "detail": "analyze.debug.risk_traces empty"})
    if not debug.get("formula_executions"):
        gaps.append(
            {
                "kind": "missing_formula_execution",
                "area": "risk",
                "detail": "analyze.debug.formula_executions empty — engine did not emit step ledger",
            }
        )
    if not debug.get("stage_timings_ms"):
        gaps.append({"kind": "missing_timing", "area": "performance", "detail": "stage_timings_ms missing"})
    for r in risk_ledgers:
        for ref in r.get("csv_refs") or r.get("csv_lookups") or []:
            if isinstance(ref, dict) and ref.get("row_id") in (None, NOT_TRACEABLE, "NOT CURRENTLY TRACEABLE") and ref.get("csv_row") in (
                None,
                "",
            ):
                gaps.append(
                    {
                        "kind": "missing_csv_row_id",
                        "area": "csv",
                        "condition": r.get("condition"),
                        "csv": ref.get("csv") or ref.get("table"),
                        "detail": "Row number not emitted",
                    }
                )
    for pkg in analyze.get("wellnessPackages") or []:
        if isinstance(pkg, dict) and not pkg.get("products_rejected"):
            gaps.append(
                {
                    "kind": "missing_rejects",
                    "area": "packages",
                    "tier": pkg.get("tier"),
                    "detail": "No products_rejected on package",
                }
            )
    for e in analyze.get("scientificEvidence") or []:
        if isinstance(e, dict) and not (e.get("source_url") or e.get("url")):
            gaps.append(
                {
                    "kind": "missing_evidence_url",
                    "area": "evidence",
                    "title": e.get("title") or e.get("source_name"),
                }
            )
    return gaps


def reverse_lookup(analyze: dict[str, Any], risk_ledgers: list) -> list[dict[str, Any]]:
    """Condition → CSV → formula → products → ingredients → evidence → packages."""
    rows = []
    for r in risk_ledgers:
        cond = r.get("condition")
        if not cond:
            continue
        products = []
        for pkg in analyze.get("wellnessPackages") or []:
            if not isinstance(pkg, dict):
                continue
            for p in pkg.get("products_included") or []:
                if isinstance(p, dict):
                    products.append(p.get("product_name") or p.get("name"))
        ingredients = []
        for t in analyze.get("nutritionalTargets") or []:
            if isinstance(t, dict):
                ingredients.append(t.get("ingredient") or t.get("nutrient"))
        evidence = []
        for e in analyze.get("scientificEvidence") or []:
            if isinstance(e, dict) and (
                e.get("condition") == cond or cond in str(e.get("linked_condition") or "")
            ):
                evidence.append(e.get("title") or e.get("source_name"))
        rows.append(
            {
                "condition": cond,
                "csv_rows": r.get("csv_refs") or r.get("csv_lookups") or [],
                "formula_id": r.get("locked_formula_id") or FORMULA_RISK,
                "products": sorted({p for p in products if p})[:20],
                "ingredients": sorted({i for i in ingredients if i})[:20],
                "evidence": evidence[:10],
                "packages": [
                    pkg.get("tier")
                    for pkg in (analyze.get("wellnessPackages") or [])
                    if isinstance(pkg, dict)
                ],
                "code": r.get("code"),
            }
        )
    return rows


def raw_production_objects(analyze: dict[str, Any]) -> dict[str, Any]:
    return {
        "healthInsights": analyze.get("healthInsights"),
        "nutritionalTargets": analyze.get("nutritionalTargets"),
        "productRecommendations": analyze.get("productRecommendations"),
        "wellnessPackages": analyze.get("wellnessPackages"),
        "scientificEvidence": analyze.get("scientificEvidence"),
        "calculationTrace": analyze.get("calculationTrace"),
        "debug": analyze.get("debug"),
        "preventativeNutritionSystem": analyze.get("preventativeNutritionSystem"),
    }


def api_contract_inspector(assessment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not assessment:
        return [{"note": "No ClinicalAssessment attached"}]
    rows = []
    for key, val in assessment.items():
        if key == "meta":
            continue
        rows.append(
            {
                "backend_object": f"assessment.{key}",
                "frontend_field": key,
                "component": NOT_TRACEABLE,
                "displayed_at": NOT_TRACEABLE,
                "has_data": val is not None,
            }
        )
    return rows


def nutrition_math_from_packages(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Project coverage_matrix / daily_nutrition_intake when present — no recompute."""
    rows = []
    for pkg in analyze.get("wellnessPackages") or []:
        if not isinstance(pkg, dict) or not pkg.get("recommended"):
            continue
        matrix = pkg.get("coverage_matrix") or []
        for m in matrix:
            if not isinstance(m, dict):
                continue
            rows.append(
                {
                    "nutrient": m.get("nutrient") or m.get("ingredient_key"),
                    "target": m.get("recommended") or m.get("target"),
                    "provided": m.get("provided"),
                    "coverage_percent": m.get("coverage_percent"),
                    "unit": m.get("unit"),
                    "chain": [
                        {"step": "target", "value": m.get("recommended") or m.get("target"), "traceable": True},
                        {
                            "step": "food_contribution",
                            **_nt("Food vs treat vs supplement split not always on coverage_matrix"),
                        },
                        {"step": "provided_total", "value": m.get("provided"), "traceable": m.get("provided") is not None},
                        {
                            "step": "coverage",
                            "value": m.get("coverage_percent"),
                            "traceable": m.get("coverage_percent") is not None,
                            "unit": "%",
                        },
                    ],
                    "tier": pkg.get("tier"),
                    "raw": m,
                }
            )
        intake = pkg.get("daily_nutrition_intake") or []
        for item in intake:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "nutrient": item.get("nutrient") or item.get("ingredient"),
                    "source": "daily_nutrition_intake",
                    "chain": [
                        {"step": "target", "value": item.get("target") or item.get("daily_target"), "traceable": True},
                        {"step": "food", "value": item.get("food") or item.get("from_food"), "traceable": item.get("food") is not None or item.get("from_food") is not None},
                        {"step": "treat", "value": item.get("treat"), "traceable": item.get("treat") is not None},
                        {"step": "supplement", "value": item.get("supplement") or item.get("from_supplement"), "traceable": item.get("supplement") is not None or item.get("from_supplement") is not None},
                        {"step": "total", "value": item.get("total") or item.get("provided"), "traceable": True},
                        {"step": "coverage", "value": item.get("coverage_percent") or item.get("coverage"), "traceable": True},
                    ],
                    "raw": item,
                }
            )
        break
    return rows
