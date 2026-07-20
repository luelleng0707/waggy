"""ScientificDiffEngine — impact of evidence / parameter / graph changes."""

from __future__ import annotations

from typing import Any

from app.science.graph import KnowledgeGraph


class ScientificDiffEngine:
    """
    Compare two knowledge graphs (or effect-size maps) and list blast radius.

    Deterministic: no model calls.
    """

    def diff_graphs(self, before: KnowledgeGraph, after: KnowledgeGraph) -> dict[str, Any]:
        before_edges = {e.id: e for e in before.edges}
        after_edges = {e.id: e for e in after.edges}
        added = [after_edges[i].to_dict() for i in after_edges.keys() - before_edges.keys()]
        removed = [before_edges[i].to_dict() for i in before_edges.keys() - after_edges.keys()]
        changed = []
        for eid in before_edges.keys() & after_edges.keys():
            b, a = before_edges[eid], after_edges[eid]
            if b.props != a.props or b.relation != a.relation:
                changed.append({"id": eid, "before": b.to_dict(), "after": a.to_dict()})

        affected_conditions = sorted(
            {
                *(self._condition_label(before, e.source, e.target) for e in before.edges if e.id in before_edges.keys() - after_edges.keys()),
                *(self._condition_label(after, e["source"], e["target"]) for e in added),
                *(self._condition_label(after, c["after"]["source"], c["after"]["target"]) for c in changed),
            }
            - {None}
        )

        # Heuristic downstream consumers for messaging
        formulas = []
        if any(e.get("relation") == "risk" or (e.get("after") or {}).get("relation") == "risk" for e in changed + added):
            formulas.append("RISK_V2_1")
        if any(
            e.get("relation") in ("supports", "reduces")
            or (e.get("after") or {}).get("relation") in ("supports", "reduces")
            for e in changed + added
        ):
            formulas.extend(["NUTRIENT_TARGET_V2_1", "PACKAGE_OPTIMIZER_V2_1"])

        return {
            "added_edges": len(added),
            "removed_edges": len(removed),
            "changed_edges": len(changed),
            "added": added[:50],
            "removed": removed[:50],
            "changed": changed[:50],
            "affected_conditions": affected_conditions[:50],
            "changed_formulas": sorted(set(formulas)),
            "affected_packages": ["essential", "balanced", "optimal"] if formulas else [],
            "affected_frontend": ["healthInsights", "nutritionalTargets", "wellnessPackages"] if formulas else [],
            "note": "Blast radius is structural (graph topology). Re-run parity suite after science edits.",
        }

    def diff_effect_size(
        self,
        *,
        subject: str,
        before: float,
        after: float,
        relation: str = "supports",
    ) -> dict[str, Any]:
        delta = after - before
        return {
            "subject": subject,
            "relation": relation,
            "before": before,
            "after": after,
            "delta": delta,
            "changed_formulas": ["NUTRIENT_TARGET_V2_1", "PACKAGE_OPTIMIZER_V2_1"],
            "affected_packages": ["essential", "balanced", "optimal"],
            "affected_frontend": ["nutritionalTargets", "wellnessPackages", "preventativeNutritionSystem"],
        }

    @staticmethod
    def _condition_label(graph: KnowledgeGraph, source: str, target: str) -> str | None:
        for nid in (source, target):
            n = graph.get(nid) if hasattr(graph, "get") else None
            if n is None and isinstance(source, str):
                # when passing dict edge endpoints only
                continue
            if n and n.type == "condition":
                return n.label
        # dict form from to_dict edges
        return None
