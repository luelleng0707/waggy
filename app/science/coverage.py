"""Knowledge coverage — conditions × papers / prevention / ingredients / foods / products."""

from __future__ import annotations

from typing import Any

from app.science.graph import KnowledgeGraph
from app.science.repository import GraphRepository


class KnowledgeCoverageReport:
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    @classmethod
    def from_repository(cls, repo: GraphRepository) -> "KnowledgeCoverageReport":
        return cls(repo.graph)

    def build(self) -> dict[str, Any]:
        rows = []
        for cond in sorted(self.graph.by_type("condition"), key=lambda n: n.label.lower()):
            out = self.graph.neighbors(cond.id, direction="out")
            incoming = self.graph.neighbors(cond.id, direction="in")
            has_papers = any(e.relation == "supported_by" for e in out)
            has_ingredients = any(e.relation in ("supports", "reduces") for e in incoming)
            has_prevention = any(e.relation == "prevents" for e in incoming)
            # foods via ingredients
            has_foods = False
            has_products = False
            for e in incoming:
                if e.relation in ("supports", "reduces", "contains"):
                    src = self.graph.get(e.source)
                    if not src:
                        continue
                    if src.type == "food":
                        has_foods = True
                    for e2 in self.graph.neighbors(src.id, direction="in"):
                        n2 = self.graph.get(e2.source)
                        if n2 and n2.type == "food":
                            has_foods = True
                        if n2 and n2.type == "product":
                            has_products = True
                    if src.type == "product":
                        has_products = True
            missing = []
            if not has_papers:
                missing.append("papers")
            if not has_ingredients:
                missing.append("ingredients")
            if not has_foods:
                missing.append("foods")
            if not has_products:
                missing.append("products")
            if not has_prevention:
                missing.append("prevention")
            rows.append(
                {
                    "condition": cond.label,
                    "has_papers": has_papers,
                    "has_prevention": has_prevention,
                    "has_ingredients": has_ingredients,
                    "has_foods": has_foods,
                    "has_products": has_products,
                    "missing": missing,
                    "complete": not missing,
                }
            )
        complete = sum(1 for r in rows if r["complete"])
        return {
            "conditions": len(rows),
            "fully_covered": complete,
            "coverage_percent": round(100.0 * complete / max(len(rows), 1), 1),
            "rows": rows,
        }
