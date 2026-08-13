"""6L — Internal research portal (deterministic graph queries)."""

from __future__ import annotations

from typing import Any

from authoring.research import ResearchAssistant
from ontology import condition_path, ingredient_path, CONDITION_ONTOLOGY, INGREDIENT_ONTOLOGY
from curation.evidence_ranking import rank_evidence_rows
from curation.conflict_resolution import detect_conflicts
from curation.duplicate_detection import suggest_condition_duplicates, suggest_ingredient_duplicates


class ResearchPortal:
    def __init__(self) -> None:
        self.ra = ResearchAssistant()

    def evidence_for_condition(self, condition: str) -> dict[str, Any]:
        papers = self.ra.papers_by_condition(condition)
        products = self.ra.products_supporting_condition(condition)
        return {
            "condition": condition,
            "ontology_path": condition_path(condition),
            "papers": papers,
            "products": products,
            "ranked_hint": "Use evidence_level/study_type via ranking on clinical_evidence_base rows",
        }

    def omega3_studies(self) -> dict[str, Any]:
        return {
            "query": "Omega-3 / EPA / DHA",
            "ingredients": self.ra.ingredients_by_mechanism("omega")
            + self.ra.ingredients_by_mechanism("EPA")
            + self.ra.ingredients_by_mechanism("inflammatory"),
            "ontology": {k: INGREDIENT_ONTOLOGY[k] for k in ("Omega-3", "EPA", "DHA") if k in INGREDIENT_ONTOLOGY},
        }

    def joint_papers(self) -> dict[str, Any]:
        out = []
        for cond, meta in CONDITION_ONTOLOGY.items():
            if meta.get("system") == "Musculoskeletal" or "Joint" in (meta.get("class") or ""):
                out.extend(self.ra.papers_by_condition(cond))
        return {"query": "joint / musculoskeletal", "papers": out}

    def compare_papers(self, a: str, b: str) -> dict[str, Any]:
        left = self.ra.recommendations_affected_by_paper(a)
        right = self.ra.recommendations_affected_by_paper(b)
        left_e = {x.get("entity") for x in left}
        right_e = {x.get("entity") for x in right}
        return {
            "paper_a": a,
            "paper_b": b,
            "only_a": sorted(left_e - right_e),
            "only_b": sorted(right_e - left_e),
            "shared": sorted(left_e & right_e),
            "a_links": left,
            "b_links": right,
        }

    def products_for_ingredient(self, ingredient: str) -> list[dict[str, Any]]:
        # reuse graph walk via condition products + ingredient nodes
        q = ingredient.lower()
        out = []
        for n in self.ra.graph.by_type("ingredient"):
            if q not in (n.label or "").lower() and q not in n.id.lower():
                continue
            for e in self.ra.graph.edges:
                if e.source != n.id and e.target != n.id:
                    continue
                other = e.target if e.source == n.id else e.source
                p = self.ra.graph.nodes.get(other)
                if p and p.type == "product":
                    out.append({"ingredient": n.label, "product": p.label or p.id, "relation": e.relation})
        return out

    def conditions_missing_interventions(self) -> list[dict[str, Any]]:
        from app.science.coverage import KnowledgeCoverageReport

        cov = KnowledgeCoverageReport(self.ra.graph).build()
        return [r for r in (cov.get("rows") or []) if "ingredients" in (r.get("missing") or []) or "products" in (r.get("missing") or [])]

    def curation_dashboard(self) -> dict[str, Any]:
        return {
            "conflicts": detect_conflicts(),
            "duplicate_conditions": suggest_condition_duplicates(),
            "duplicate_ingredients": suggest_ingredient_duplicates(),
        }
