"""6D — conflicting evidence detection (deterministic)."""

from __future__ import annotations

from app.core.paths import clinical_root_str, resolve_clinical_root

from collections import defaultdict
from typing import Any

from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder
from curation.evidence_ranking import score_study_type


POSITIVE = {"supports", "improves", "increases", "positive", "+", "benefit"}
NEGATIVE = {"reduces", "worsens", "decreases", "negative", "-", "harm", "conflicts", "adverse"}


def _direction(text: str) -> str:
    t = (text or "").lower()
    if any(p in t for p in POSITIVE):
        return "positive"
    if any(n in t for n in NEGATIVE):
        return "negative"
    return "neutral"


def detect_conflicts(platform: DataPlatform | None = None) -> list[dict[str, Any]]:
    """
    Group evidence by (ingredient, condition) and flag opposing effect directions.
    """
    platform = platform or DataPlatform(clinical_root_str(), strict=True)
    conflicts: list[dict[str, Any]] = []

    # From clinical evidence base
    ceb = platform.clinical_evidence_base()
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    if not ceb.empty:
        for _, row in ceb.iterrows():
            cond = str(row.get("condition") or "").strip()
            nutrient = str(row.get("nutrient_or_activity") or row.get("ingredient") or "").strip()
            if not cond:
                continue
            mech = str(row.get("mechanism") or "")
            quote = str(row.get("source_quote") or "")
            direction = _direction(mech + " " + quote)
            groups[(nutrient.lower() or "*", cond.lower())].append(
                {
                    "condition": cond,
                    "ingredient_or_activity": nutrient,
                    "source_name": row.get("source_name"),
                    "source_url": row.get("source_url"),
                    "year": row.get("year"),
                    "evidence_level": row.get("evidence_level"),
                    "direction": direction,
                    "quality": score_study_type(str(row.get("evidence_level") or "unknown")),
                    "quote": quote[:200],
                }
            )

    # Graph supports vs reduces edges for same ingredient→condition
    graph = KnowledgeGraphBuilder(platform).build()
    pair_rels: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_papers: dict[tuple[str, str], list[str]] = defaultdict(list)
    for e in graph.edges:
        src, tgt = graph.nodes.get(e.source), graph.nodes.get(e.target)
        if not src or not tgt:
            continue
        if src.type == "ingredient" and tgt.type == "condition":
            key = (src.label.lower(), tgt.label.lower())
            pair_rels[key].add(e.relation)
        if src.type == "condition" and tgt.type == "paper":
            pass

    for (ing, cond), rels in pair_rels.items():
        if "supports" in rels and ("reduces" in rels or "conflicts" in rels):
            conflicts.append(
                {
                    "type": "graph_relation_conflict",
                    "ingredient": ing,
                    "condition": cond,
                    "relations": sorted(rels),
                    "recommendation": "Scientific review required — opposing graph relations",
                }
            )

    for key, rows in groups.items():
        dirs = {r["direction"] for r in rows if r["direction"] != "neutral"}
        if "positive" in dirs and "negative" in dirs:
            conflicts.append(
                {
                    "type": "effect_direction_conflict",
                    "ingredient": key[0],
                    "condition": key[1],
                    "papers": rows,
                    "recommendation": "Show populations & quality; curator decide inclusion",
                }
            )

    return conflicts
