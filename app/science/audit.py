"""Scientific audit report generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder
from app.science.coverage import KnowledgeCoverageReport
from app.science.validator import DataValidator
from app.science.versioning import current_science_versions


class ScientificAudit:
    def __init__(self, platform: DataPlatform):
        self.platform = platform

    def build(self) -> dict[str, Any]:
        builder = KnowledgeGraphBuilder(self.platform)
        graph = builder.build()
        evidence = builder.evidence_objects()
        coverage = KnowledgeCoverageReport(graph).build()
        validation = DataValidator(self.platform).validate()
        versions = current_science_versions()

        weak = [
            e.to_dict()
            for e in evidence
            if str(e.confidence or "").lower() in ("low", "c", "")
        ][:40]
        products = graph.by_type("product")
        products_without_science = []
        for p in products:
            outs = graph.neighbors(p.id, direction="out")
            ings = [e for e in outs if e.relation == "contains"]
            linked = False
            for e in ings:
                ing = graph.get(e.target)
                if not ing:
                    continue
                if graph.neighbors(ing.id, direction="out", relation="supports") or graph.neighbors(
                    ing.id, direction="out", relation="cites"
                ):
                    linked = True
                    break
            if not linked:
                products_without_science.append(p.label)

        science_without_products = [
            r["condition"]
            for r in coverage["rows"]
            if r["has_ingredients"] and not r["has_products"]
        ]

        return {
            "versions": versions.to_dict(),
            "graph": graph.summary(),
            "evidence_count": len(evidence),
            "coverage": {
                "conditions": coverage["conditions"],
                "fully_covered": coverage["fully_covered"],
                "coverage_percent": coverage["coverage_percent"],
            },
            "validation": validation,
            "weak_evidence": weak,
            "missing_papers": coverage["rows"] and [r["condition"] for r in coverage["rows"] if not r["has_papers"]][:40],
            "products_without_science": products_without_science[:40],
            "science_without_products": science_without_products[:40],
            "duplicate_studies": validation.get("duplicate_paper_ids") or [],
        }

    def to_markdown(self, report: dict[str, Any] | None = None) -> str:
        r = report or self.build()
        lines = [
            "# SCIENTIFIC_AUDIT",
            "",
            "## Versions",
            "",
            f"- Algorithm: `{r['versions'].get('algorithm')}`",
            f"- Warehouse: `{r['versions'].get('warehouse')}`",
            f"- Evidence: `{r['versions'].get('evidence')}`",
            f"- Papers: `{r['versions'].get('papers')}`",
            f"- Knowledge graph: `{r['versions'].get('knowledge_graph')}`",
            "",
            "## Graph",
            "",
            f"- Nodes: {r['graph'].get('nodes')}",
            f"- Edges: {r['graph'].get('edges')}",
            f"- By type: `{r['graph'].get('by_type')}`",
            "",
            "## Coverage",
            "",
            f"- Conditions: {r['coverage'].get('conditions')}",
            f"- Fully covered: {r['coverage'].get('fully_covered')}",
            f"- Coverage %: {r['coverage'].get('coverage_percent')}",
            "",
            "## Validation",
            "",
            f"- OK: {r['validation'].get('ok')}",
            f"- Errors: {len(r['validation'].get('errors') or [])}",
            f"- Warnings: {len(r['validation'].get('warnings') or [])}",
            "",
            "## Weak evidence (sample)",
            "",
        ]
        for w in (r.get("weak_evidence") or [])[:15]:
            lines.append(f"- {w.get('id')}: {w.get('condition') or w.get('ingredient')} conf={w.get('confidence')}")
        lines += ["", "## Conditions missing papers", ""]
        for c in (r.get("missing_papers") or [])[:25]:
            lines.append(f"- {c}")
        lines += ["", "## Products without science link", ""]
        for p in (r.get("products_without_science") or [])[:25]:
            lines.append(f"- {p}")
        lines += ["", "## Science without products", ""]
        for c in (r.get("science_without_products") or [])[:25]:
            lines.append(f"- {c}")
        lines.append("")
        return "\n".join(lines)


def write_scientific_audit(platform: DataPlatform, warehouse_root: str | Path = "warehouse") -> Path:
    audit = ScientificAudit(platform)
    report = audit.build()
    root = Path(warehouse_root)
    gen = root / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    md = gen / "SCIENTIFIC_AUDIT.md"
    md.write_text(audit.to_markdown(report), encoding="utf-8")
    import json

    (gen / "scientific_audit.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    # also persist graph summary
    builder = KnowledgeGraphBuilder(platform)
    g = builder.build()
    graph_dir = root / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    (graph_dir / "summary.json").write_text(json.dumps(g.summary(), indent=2), encoding="utf-8")
    cov = KnowledgeCoverageReport(g).build()
    (gen / "knowledge_coverage.json").write_text(json.dumps(cov, indent=2), encoding="utf-8")
    return md
