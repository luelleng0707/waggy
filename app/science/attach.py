"""Attach knowledge-graph explainability onto AssessmentResult / analyze debug (additive)."""

from __future__ import annotations

from typing import Any

from app.agent.assessment_result import AssessmentResult
from app.agent.state import DogProfileInput
from app.data.repository import DataPlatform, DataRepository
from app.science.builder import KnowledgeGraphBuilder
from app.science.confidence import build_confidence_bundle
from app.science.coverage import KnowledgeCoverageReport
from app.science.explanations import build_formula_explanations, build_recommendation_chain
from app.science.repository import GraphRepository
from app.science.versioning import current_science_versions


def build_reasoning_payload(
    *,
    profile: DogProfileInput,
    result: AssessmentResult,
    repository: DataRepository,
) -> dict[str, Any]:
    platform: DataPlatform = repository.platform
    builder = KnowledgeGraphBuilder(platform)
    graph = builder.build()
    evidence = builder.evidence_objects()
    grepo = GraphRepository(graph, evidence)

    risks = (result.health or {}).get("risks") or []
    ingredients = (result.nutrition or {}).get("nutrient_targets") or []
    # Prefer ingredient node output if present in health path via legacy json
    legacy = result.legacy_json or {}
    raw_ings = legacy.get("ingredients") or legacy.get("ingredientRequirements") or []

    breed = profile.primary_breed
    recommendation_explanations = []
    for r in risks[:12]:
        cond = str(r.get("condition_name") or r.get("title") or "")
        if not cond:
            continue
        ev_for = [e for e in evidence if (e.condition or "").lower() == cond.lower()]
        paper = None
        if ev_for:
            paper = {
                "paper_id": ev_for[0].paper_id,
                "title": ev_for[0].paper_title,
                "url": ev_for[0].url,
            }
        why = grepo.why(cond, kind="condition")
        # find a supporting ingredient from graph
        ing_label = None
        cond_node = grepo.condition(cond)
        if cond_node:
            for edge in cond_node.get("incoming") or []:
                if edge.get("relation") in ("supports", "reduces"):
                    src = edge.get("source") or ""
                    if src.startswith("ingredient:"):
                        node = graph.get(src)
                        ing_label = node.label if node else src
                        break
        recommendation_explanations.append(
            {
                "recommendation_id": f"condition:{cond}",
                "condition": cond,
                "risk_percent": r.get("risk_percent"),
                "chain": build_recommendation_chain(
                    condition=cond,
                    breed=breed,
                    ingredient=ing_label,
                    paper=paper,
                    graph_paths=why.get("paths") or [],
                ),
                "confidence": build_confidence_bundle(
                    execution_ok=True,
                    evidence_rows=[e.to_dict() for e in ev_for],
                    coverage={
                        "has_papers": bool(ev_for),
                        "has_ingredients": bool(ing_label),
                        "has_foods": False,
                        "has_products": False,
                        "has_prevention": False,
                    },
                ),
                "evidence_objects": [e.to_dict() for e in ev_for[:5]],
            }
        )

    formula_explanations = [
        build_formula_explanations("RISK_V2_1"),
        build_formula_explanations("NUTRIENT_TARGET_V2_1"),
        build_formula_explanations("PACKAGE_OPTIMIZER_V2_1"),
    ]

    coverage = KnowledgeCoverageReport(graph).build()
    versions = current_science_versions()

    return {
        "versions": versions.to_dict(),
        "knowledge_graph": graph.summary(),
        "evidence_objects": [e.to_dict() for e in evidence[:100]],
        "recommendation_explanations": recommendation_explanations,
        "formula_explanations": formula_explanations,
        "coverage_snapshot": {
            "conditions": coverage["conditions"],
            "fully_covered": coverage["fully_covered"],
            "coverage_percent": coverage["coverage_percent"],
        },
        "why_examples": {
            "sample_ingredient": grepo.why(
                str((raw_ings[0] or {}).get("ingredient_name") or (raw_ings[0] or {}).get("name") or "Omega")
                if raw_ings
                else "Omega-3",
                kind="ingredient",
            )
        },
    }


def attach_science_to_analyze(analyze: dict[str, Any], reasoning: dict[str, Any]) -> dict[str, Any]:
    """Additive only — clinical keys untouched."""
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    debug = dict(debug)
    debug["science"] = reasoning
    debug["science_versions"] = reasoning.get("versions")
    analyze["debug"] = debug
    # Optional top-level for future UI (non-breaking additive)
    analyze.setdefault("scientificExplainability", {
        "versions": reasoning.get("versions"),
        "recommendations": reasoning.get("recommendation_explanations"),
        "formulas": reasoning.get("formula_explanations"),
        "knowledge_graph": reasoning.get("knowledge_graph"),
    })
    return analyze
