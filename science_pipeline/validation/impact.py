"""Scientific impact analysis — deterministic lineage from a change to clinical surfaces."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agent.formula_registry import FORMULA_REGISTRY
from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder

ROOT = Path(__file__).resolve().parents[2]


class ScientificImpactAnalyzer:
    """Given a changed entity (ingredient, paper, condition, dose), report blast radius."""

    def __init__(self, platform: DataPlatform | None = None):
        self.platform = platform or DataPlatform("data", strict=True)
        self.graph = KnowledgeGraphBuilder(self.platform).build()

    def analyze(
        self,
        *,
        entity_type: str,
        entity_id: str,
        field: str | None = None,
        old_value: Any = None,
        new_value: Any = None,
    ) -> dict[str, Any]:
        entity_type = entity_type.lower().strip()
        entity_id = str(entity_id).strip()
        label_l = entity_id.lower()

        # Resolve graph nodes
        matched_nodes = [
            n
            for n in self.graph.nodes.values()
            if n.type == entity_type or label_l in n.id.lower() or label_l in (n.label or "").lower()
        ]
        if not matched_nodes and entity_type:
            matched_nodes = [
                n
                for n in self.graph.nodes.values()
                if label_l in n.id.lower() or label_l in (n.label or "").lower()
            ]

        node_ids = {n.id for n in matched_nodes}
        affected_conditions: set[str] = set()
        affected_ingredients: set[str] = set()
        affected_products: set[str] = set()
        affected_papers: set[str] = set()
        affected_packages: set[str] = set()

        # BFS one hop out and in
        for e in self.graph.edges:
            if e.source in node_ids or e.target in node_ids:
                for nid in (e.source, e.target):
                    n = self.graph.nodes.get(nid)
                    if not n:
                        continue
                    if n.type == "condition":
                        affected_conditions.add(n.label or n.id)
                    elif n.type == "ingredient":
                        affected_ingredients.add(n.label or n.id)
                    elif n.type == "product":
                        affected_products.add(n.label or n.id)
                    elif n.type == "paper":
                        affected_papers.add(n.label or n.id)
                    elif n.type == "package":
                        affected_packages.add(n.label or n.id)

        # Formulas that consume related tables
        table_hints = {
            "ingredient": ["condition_ingredients", "ingredient_evidence", "product_components"],
            "condition": ["breed_conditions", "condition_ingredients", "condition_activities"],
            "paper": ["clinical_evidence_base", "ingredient_evidence"],
            "product": ["products", "product_components", "product_pricing"],
            "dose": ["condition_ingredients"],
        }
        hint = table_hints.get(entity_type, table_hints.get(field or "", []))
        if field and "dose" in field.lower():
            hint = list(set(hint + table_hints["dose"]))

        affected_formulas = []
        for fid, meta in FORMULA_REGISTRY.items():
            tables = [str(t).lower() for t in (meta.get("tables") or [])]
            if any(any(h.replace("_", "") in t.replace("_", "") or h in t for h in hint) for t in tables):
                affected_formulas.append(fid)
            elif entity_type == "ingredient" and "ingredient" in fid.lower():
                affected_formulas.append(fid)

        # Confidence delta placeholder — Phase 5 reports structure only; clinical math unchanged
        confidence_note = (
            "Confidence scores are not recalculated in impact analysis; "
            "run AssessmentAgent with debug.science after applying the change."
        )

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "change": {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "field": field,
                "old_value": old_value,
                "new_value": new_value,
            },
            "matched_nodes": [{"id": n.id, "type": n.type, "label": n.label} for n in matched_nodes[:20]],
            "affected_conditions": sorted(affected_conditions)[:50],
            "affected_ingredients": sorted(affected_ingredients)[:50],
            "affected_products": sorted(affected_products)[:50],
            "affected_packages": sorted(affected_packages)[:50],
            "affected_papers": sorted(affected_papers)[:50],
            "affected_formulas": sorted(set(affected_formulas)),
            "affected_reports": ["clinical-report", "ppie/assess", "scientificExplainability"],
            "affected_dogs": "Re-run 100-dog parity / benchmark suite to enumerate profile-level deltas.",
            "confidence_change": confidence_note,
            "counts": {
                "conditions": len(affected_conditions),
                "ingredients": len(affected_ingredients),
                "products": len(affected_products),
                "packages": len(affected_packages),
                "papers": len(affected_papers),
                "formulas": len(set(affected_formulas)),
            },
        }
        return report

    def write_report(self, report: dict[str, Any], out_path: Path | None = None) -> Path:
        out_path = out_path or (ROOT / "governance" / "reports" / "SCIENTIFIC_IMPACT.md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        c = report["change"]
        lines = [
            "# Scientific Impact Analysis",
            "",
            f"Generated: `{report['generated_at']}`",
            "",
            f"Change: **{c['entity_type']}** `{c['entity_id']}`",
        ]
        if c.get("field"):
            lines.append(f"Field: `{c['field']}` `{c.get('old_value')}` → `{c.get('new_value')}`")
        lines += ["", "## Counts", ""]
        for k, v in report["counts"].items():
            lines.append(f"- {k}: {v}")
        for section in (
            "affected_conditions",
            "affected_ingredients",
            "affected_products",
            "affected_packages",
            "affected_papers",
            "affected_formulas",
            "affected_reports",
        ):
            lines += ["", f"## {section.replace('_', ' ').title()}", ""]
            items = report.get(section) or []
            if not items:
                lines.append("_None detected_")
            else:
                for i in items:
                    lines.append(f"- {i}")
        lines += ["", "## Confidence", "", report.get("confidence_change") or "", ""]
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        out_path.with_suffix(".json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return out_path
