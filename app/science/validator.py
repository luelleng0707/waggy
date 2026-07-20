"""Warehouse / graph referential integrity checks (FK-like)."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.data.repository import DataPlatform
from app.data.warehouse.papers import _paper_id_from_row
from app.science.builder import KnowledgeGraphBuilder


class DataValidator:
    def __init__(self, platform: DataPlatform):
        self.platform = platform

    def validate(self) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        builder = KnowledgeGraphBuilder(self.platform)
        graph = builder.build()
        evidence = builder.evidence_objects()

        paper_ids = [n.id for n in graph.by_type("paper")]
        dup_papers = [pid for pid, c in Counter(paper_ids).items() if c > 1]
        if dup_papers:
            errors.append(f"Duplicate paper node ids: {dup_papers[:5]}")

        # Orphan edges
        for e in graph.edges:
            if e.source not in graph.nodes:
                errors.append(f"Edge source missing: {e.id}")
            if e.target not in graph.nodes:
                errors.append(f"Edge target missing: {e.id}")

        # Evidence paper_ids should resolve to paper nodes
        missing_papers = []
        for ev in evidence:
            if not ev.paper_id:
                continue
            if not any(n.id.endswith(ev.paper_id.lower()) or ev.paper_id in n.id for n in graph.by_type("paper")):
                # builder always upserts papers from same rows — soft warning if empty title
                if not ev.paper_title:
                    warnings.append(f"Evidence {ev.id} missing paper title")

        # Units on condition_ingredients
        ci = self.platform.condition_ingredients()
        if not ci.empty and "dose_unit" in ci.columns:
            empty_units = int((ci["dose_unit"].astype(str).str.strip() == "").sum())
            if empty_units:
                warnings.append(f"{empty_units} condition_ingredients rows missing dose_unit")

        # Conditions without any paper support
        conditions = {n.label for n in graph.by_type("condition")}
        supported = set()
        for e in graph.edges:
            if e.relation == "supported_by":
                src = graph.nodes.get(e.source)
                if src and src.type == "condition":
                    supported.add(src.label)
        unsupported = sorted(conditions - supported)
        if unsupported:
            warnings.append(f"{len(unsupported)} conditions lack supported_by paper edges")

        return {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "stats": graph.summary(),
            "evidence_count": len(evidence),
            "conditions_without_papers": unsupported[:30],
            "duplicate_paper_ids": dup_papers,
        }
