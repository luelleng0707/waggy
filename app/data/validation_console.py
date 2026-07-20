"""
Validation Console payload (debug only) — full backend observatory over frozen analyze.

Does NOT recompute formulas. Marks non-reconstructible steps as NOT CURRENTLY TRACEABLE.
"""

from __future__ import annotations

from typing import Any

from app.data.console_inspectors import (
    CODE_TRACE,
    CSV_USAGE_MAP,
    api_contract_inspector,
    build_search_index,
    competition_inspector,
    confidence_inspector,
    coverage_inspector,
    csv_dependency_viewer,
    decision_ledger_inspector,
    decision_trees,
    evidence_inspector,
    expand_risk_ledgers,
    formula_execution_inspector,
    formula_explorer,
    formula_graph,
    ingredient_resolution_inspector,
    missing_data_report,
    nutrition_inspector,
    nutrition_math_from_packages,
    observability_coverage,
    package_optimizer_inspector,
    performance_inspector,
    pipeline_dag,
    pipeline_timeline,
    product_match_inspector,
    provenance_inspector,
    raw_production_objects,
    reverse_lookup,
)
from app.data.engine_trace import build_engine_trace
from app.data.repository import DataRepository
from app.inference.formula_registry import FORMULA_REGISTRY, FORMULA_RISK, formula_list
from app.inference.models import NOT_TRACEABLE

NAV = [
    {"id": "s0", "label": "0 · Summary"},
    {"id": "s1", "label": "1 · Raw Request"},
    {"id": "s2", "label": "2 · Normalization"},
    {"id": "s3", "label": "3 · Repository Lookups"},
    {"id": "s4", "label": "4 · Formula Execution"},
    {"id": "s5", "label": "5 · Modifier Ledger"},
    {"id": "s6", "label": "6 · Confidence Ledger"},
    {"id": "s7", "label": "7 · Nutrition"},
    {"id": "s8", "label": "8 · Products"},
    {"id": "s9", "label": "9 · Packages"},
    {"id": "s10", "label": "10 · Response Assembly"},
    {"id": "s11", "label": "11 · Final Response"},
    {"id": "s12", "label": "12 · Pipeline Timeline"},
    {"id": "s13", "label": "13 · Dependency Graph"},
    {"id": "s14", "label": "14 · Runtime Stats"},
    {"id": "s15", "label": "15 · Validation"},
    {"id": "s16", "label": "16 · Knowledge Graph"},
    {"id": "s17", "label": "17 · Evidence & Confidence"},
    {"id": "s18", "label": "18 · Science Versions"},
]


def _nt(reason: str, *, needs_instrumentation: str | None = None) -> dict[str, Any]:
    return {
        "status": NOT_TRACEABLE,
        "reason": reason,
        "needs_engine_instrumentation": needs_instrumentation
        or "Emit named intermediate fields from the deterministic stage (no equation text required).",
    }


def _assessment_provenance(assessment: dict[str, Any] | None) -> dict[str, Any]:
    if not assessment:
        return {"modules": [], "note": "No assessment attached"}
    mapping = [
        ("profile", "analyze.profile / pet", "projection", ["profile", "pet"]),
        ("breed", "analyze.biology", "projection", ["biology"]),
        ("traits", "analyze.biology.trait_summary", "projection", ["biology"]),
        ("health", "analyze.healthInsights", "projection", ["healthInsights", "calculationTrace"]),
        ("nutrition", "analyze.nutritionalTargets", "projection", ["nutritionalTargets"]),
        ("packages", "analyze.wellnessPackages", "projection", ["wellnessPackages"]),
        ("products", "analyze.productRecommendations", "projection", ["productRecommendations"]),
        ("evidence", "analyze.scientificEvidence", "projection", ["scientificEvidence"]),
    ]
    modules = []
    for mid, source, kind, keys in mapping:
        modules.append(
            {
                "module_id": mid,
                "source_engine_node": source,
                "kind": kind,
                "computed_in_assessment": False,
                "analyze_keys": keys,
                "has_data": assessment.get(mid) is not None,
            }
        )
    return {"modules": modules, "note": "ClinicalAssessment is projection-only."}


def _validation_checklist(
    analyze: dict[str, Any], assessment: dict[str, Any] | None, consistency: list
) -> list[dict[str, Any]]:
    insights = analyze.get("healthInsights") or []
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    checks = [
        {
            "id": "risks_present",
            "ok": bool(insights),
            "label": "Health priorities present",
            "detail": f"{len(insights)} insights",
        },
        {
            "id": "evidence_present",
            "ok": bool(analyze.get("scientificEvidence")),
            "label": "Evidence attached",
            "detail": f"{len(analyze.get('scientificEvidence') or [])} items",
        },
        {
            "id": "formula_registry",
            "ok": bool(FORMULA_REGISTRY),
            "label": "Formula registry loaded",
            "detail": f"{len(FORMULA_REGISTRY)} formulas",
        },
        {
            "id": "risk_traces",
            "ok": bool(debug.get("risk_traces")),
            "label": "Observatory risk traces",
            "detail": f"{len(debug.get('risk_traces') or [])} conditions",
        },
        {
            "id": "stage_timings",
            "ok": bool(debug.get("stage_timings_ms")),
            "label": "Stage timings",
            "detail": str(list((debug.get("stage_timings_ms") or {}).keys())),
        },
        {
            "id": "package_rejects",
            "ok": bool(debug.get("package_rejects"))
            or any(
                isinstance(p, dict) and p.get("products_rejected")
                for p in (analyze.get("wellnessPackages") or [])
            ),
            "label": "Package rejected products",
            "detail": f"{len(debug.get('package_rejects') or [])} rejects in debug",
        },
        {
            "id": "assessment",
            "ok": bool(assessment),
            "label": "ClinicalAssessment attached",
            "detail": "present" if assessment else "missing",
        },
        {
            "id": "consistency",
            "ok": not consistency,
            "label": "No consistency warnings",
            "detail": f"{len(consistency)} warnings",
        },
    ]
    return checks


def _gaps() -> list[dict[str, Any]]:
    return [
        {
            "id": "csv_row_ids",
            "area": "csv",
            "status": "PARTIAL",
            "detail": "RISK + nutrition lookups emit csv_row/row_id. Package optimizer product joins still sparse on row IDs.",
            "blocks_complete_audit": False,
            "instrumentation": "Extend LookupResult through catalog joins",
        },
        {
            "id": "optimizer_pass_scores",
            "area": "packages",
            "status": NOT_TRACEABLE,
            "detail": "Per-candidate trial scores inside greedy/best-add loops not stored.",
            "blocks_complete_audit": True,
            "instrumentation": "Append optimization_passes[] without changing selection",
        },
        {
            "id": "stable_business_row_keys",
            "area": "csv",
            "status": "PARTIAL",
            "detail": "row_id is currently `{TABLE}_{csv_line}` from loader, not a stable BC_##### business key.",
            "blocks_complete_audit": False,
            "instrumentation": "Add explicit id columns to CSVs when migrating data platform",
        },
        {
            "id": "conf_factor_chain",
            "area": "confidence",
            "status": "PARTIAL",
            "detail": "RISK confidence is category-coverage only (emitted). CONF_V1 study-quality ladder is not production.",
            "blocks_complete_audit": False,
            "instrumentation": "Emit confidence breakdown when approved",
        },
        {
            "id": "activity_weight_climate_risk",
            "area": "risk",
            "status": "NOT_APPLIED_IN_RISK_V2_1",
            "detail": "Locked risk path does not apply activity/weight/climate multipliers.",
            "blocks_complete_audit": False,
            "instrumentation": "N/A — not part of RISK_V2_1",
        },
        {
            "id": "cache_lookup_ms",
            "area": "performance",
            "status": NOT_TRACEABLE,
            "detail": "Per-lookup ms and cache hits not instrumented (formula_execution.timing.cache = NT).",
            "blocks_complete_audit": False,
            "instrumentation": "DataPlatform query counters",
        },
    ]


def build_validation_console(
    repo: DataRepository,
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    *,
    timings: dict[str, float] | None = None,
    raw_request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full Validation Console / Observatory document for /debug/calculation."""
    trace = build_engine_trace(repo, analyze, assessment, timings=timings)

    risk_ledgers = expand_risk_ledgers(analyze)
    formula_executions = formula_execution_inspector(analyze)
    decisions_ledger = decision_ledger_inspector(analyze)
    provenance = provenance_inspector(analyze)
    competitions = competition_inspector(analyze)
    nutrition = nutrition_inspector(analyze)
    nutrition_math = nutrition_math_from_packages(analyze)
    ingredients = ingredient_resolution_inspector(analyze)
    products = product_match_inspector(analyze)
    packages = package_optimizer_inspector(analyze)
    evidence = evidence_inspector(analyze)
    confidence = confidence_inspector(analyze)
    coverage = coverage_inspector(analyze)
    csv_lookups = csv_dependency_viewer(analyze)
    timeline = pipeline_timeline(analyze, timings)
    performance = performance_inspector(analyze, timings)
    graph = formula_graph()
    dag = pipeline_dag()
    decisions = decision_trees(analyze)
    formulas = formula_explorer()
    obs_cov = observability_coverage(analyze, risk_ledgers, packages)
    missing = missing_data_report(analyze, risk_ledgers)
    reverse = reverse_lookup(analyze, risk_ledgers)
    raw_objs = raw_production_objects(analyze)

    profile = analyze.get("profile") or analyze.get("pet") or {}
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}

    console: dict[str, Any] = {
        "schema": "validation_console.v7",
        "debug": True,
        "equation_policy": "emitted_step_expressions",
        "not_traceable_token": NOT_TRACEABLE,
        "philosophy": "Single Full Assessment Developer Report — one continuous page, engine-emitted ledgers only, no second engine, no invented intermediates.",
        "primary_view": "developer_report",
        "single_page": True,
        "nav": NAV,
        "formula_registry": formula_list(),
        "formula_catalog": formulas,
        "formula_explorer": formulas,
        "formula_executions": formula_executions,
        "decision_ledger": decisions_ledger,
        "provenance_index": provenance,
        "lookup_competitions": competitions,
        "modifier_ledger": [
            {**m, "formula_id": fx.get("formula_id"), "subject": fx.get("subject") or fx.get("condition")}
            for fx in formula_executions
            for m in (fx.get("modifiers") or [])
            if isinstance(m, dict)
        ],
        "confidence_ledger": [
            {**c, "formula_id": fx.get("formula_id"), "subject": fx.get("subject") or fx.get("condition")}
            for fx in formula_executions
            for c in (fx.get("confidence") or fx.get("confidence_steps") or [])
            if isinstance(c, dict)
        ],
        "running_calculations": [
            {
                "formula_id": fx.get("formula_id"),
                "subject": fx.get("subject") or fx.get("condition"),
                "steps": fx.get("steps"),
                "outputs": fx.get("outputs"),
            }
            for fx in formula_executions
        ],
        "formula_graph": graph,
        "pipeline_dag": dag,
        "code_trace": CODE_TRACE,
        "csv_usage_map": CSV_USAGE_MAP,
        "engine_trace": trace,
        "overview": {
            "risk_count": len(risk_ledgers),
            "nutrition_targets": len(nutrition),
            "products": len(products.get("selected") or []),
            "rejected_products": len(products.get("rejected") or [])
            if isinstance(products.get("rejected"), list)
            else 0,
            "packages": len(packages.get("tiers") or []),
            "evidence": len(evidence),
            "formulas_registered": len(FORMULA_REGISTRY),
            "timings": timings or {},
            "stage_timings_ms": debug.get("stage_timings_ms") or {},
            "observability_coverage": obs_cov,
        },
        "observability_coverage": obs_cov,
        "profile_inspector": {
            "raw_request": raw_request,
            "normalized": profile,
            "defaults_applied": _nt("Default-application ledger not emitted by payload adapter."),
            "aliases_resolved": _nt("Alias resolution steps not logged per field."),
            "missing_values": [
                k for k, v in (profile.items() if isinstance(profile, dict) else []) if v in (None, "", [])
            ],
        },
        "risk_ledgers": risk_ledgers,
        "risk_modifier_ledgers": risk_ledgers,
        "explain_why": [
            {
                "condition": r.get("condition"),
                "final_probability_pct": r.get("final_probability_pct"),
                "confidence_percent": r.get("confidence_percent"),
                "steps": r.get("expanded_chain") or r.get("steps"),
                "formula": {"formula_id": r.get("locked_formula_id") or FORMULA_RISK},
                "audit_note": r.get("note"),
                "complete_modifier_chain": bool(r.get("complete")),
                "code": r.get("code"),
                "csv_refs": r.get("csv_refs") or r.get("csv_lookups"),
                "formula_execution": r.get("formula_execution"),
            }
            for r in risk_ledgers
        ],
        "ingredients": ingredients,
        "nutrition": nutrition,
        "nutrition_math": nutrition_math,
        "coverage": coverage,
        "confidence": confidence,
        "evidence": evidence,
        "products": products,
        "packages": packages,
        "package_optimizer": packages,
        "decisions": decisions,
        "reverse_lookup": reverse,
        "csv_lookups": csv_lookups,
        "repository_lookups": csv_lookups,
        "pipeline_timeline": timeline,
        "performance": performance,
        "missing_data": missing,
        "api_contract": api_contract_inspector(assessment),
        "raw_production_objects": raw_objs,
        "assessment_provenance": _assessment_provenance(assessment),
        "validation_checklist": _validation_checklist(
            analyze, assessment, trace.get("consistency_warnings") or []
        ),
        "gaps": _gaps(),
        "raw_analyze_keys": sorted(analyze.keys()) if isinstance(analyze, dict) else [],
        "analyze_debug": debug,
        "export": {"formats": ["json", "markdown"]},
        # Phase 4 — knowledge / evidence graphs (additive; from analyze.debug.science)
        "knowledge_graph": (debug.get("science") or {}).get("knowledge_graph")
        or (analyze.get("scientificExplainability") or {}).get("knowledge_graph")
        or {},
        "science": debug.get("science") or analyze.get("scientificExplainability") or {},
        "science_versions": debug.get("science_versions")
        or (debug.get("science") or {}).get("versions")
        or {},
        "recommendation_explanations": (debug.get("science") or {}).get("recommendation_explanations")
        or (analyze.get("scientificExplainability") or {}).get("recommendations")
        or [],
        "formula_explanations": (debug.get("science") or {}).get("formula_explanations")
        or (analyze.get("scientificExplainability") or {}).get("formulas")
        or [],
        "evidence_objects": (debug.get("science") or {}).get("evidence_objects") or [],
    }
    console["search_index"] = build_search_index(
        {
            "risk_ledgers": risk_ledgers,
            "evidence": evidence,
            "ingredients": ingredients,
            "csv_lookups": csv_lookups,
            "products": products,
            "nutrition": nutrition,
        }
    )
    # Deep search tokens from debug payload
    for t in debug.get("risk_traces") or []:
        if isinstance(t, dict) and t.get("condition"):
            console["search_index"].append(
                {"kind": "condition", "label": t["condition"], "nav": "risks"}
            )
    return console


def console_to_markdown(console: dict[str, Any]) -> str:
    lines = [
        "# PPIE Validation Console Export",
        "",
        f"Schema: `{console.get('schema')}`",
        f"Equation policy: `{console.get('equation_policy')}`",
        f"Observability coverage: `{console.get('observability_coverage')}`",
        "",
        "## Formula explorer",
        "",
    ]
    for f in console.get("formula_explorer") or console.get("formula_registry") or []:
        lines.append(
            f"- `{f.get('formula_id')}` — {f.get('purpose') or f.get('description')} "
            f"({f.get('code_file') or f.get('owner_module')})"
        )
    lines.append("")
    lines.append("## Risk ledgers")
    lines.append("")
    for ex in console.get("risk_ledgers") or []:
        lines.append(f"### {ex.get('condition')} — final {ex.get('final_probability_pct')}%")
        for step in ex.get("expanded_chain") or ex.get("steps") or []:
            if step.get("traceable"):
                lines.append(
                    f"- **{step.get('label') or step.get('name')}**: "
                    f"{step.get('value')}{step.get('unit') or ''} (`{step.get('op')}`)"
                )
            elif step.get("status") == "NOT_APPLIED_IN_RISK_V2_1":
                lines.append(f"- **{step.get('label') or step.get('name')}**: not applied in RISK_V2_1")
            else:
                lines.append(f"- **{step.get('label') or step.get('name')}**: {NOT_TRACEABLE}")
    lines.append("")
    lines.append("## Formula executions")
    lines.append("")
    for fx in console.get("formula_executions") or []:
        lines.append(f"### {fx.get('condition')} — `{fx.get('formula_id')}`")
        for s in fx.get("steps") or []:
            lines.append(
                f"- Step {s.get('step')} **{s.get('name')}**: "
                f"{s.get('before')} → {s.get('after') if s.get('after') is not None else s.get('result')}"
                f"{s.get('unit') or ''}"
            )
        for lu in (fx.get("lookups") or [])[:12]:
            lines.append(
                f"  - lookup `{lu.get('table')}` row `{lu.get('csv_row')}` pk={lu.get('primary_key')}"
            )
    lines.append("")
    lines.append("## Package rejects")
    lines.append("")
    for tier in (console.get("packages") or {}).get("tiers") or []:
        lines.append(f"### {tier.get('title')}")
        for r in tier.get("removed_products") or []:
            if isinstance(r, dict):
                lines.append(f"- REJECTED `{r.get('product_name')}` — {r.get('reason')}")
    return "\n".join(lines) + "\n"
