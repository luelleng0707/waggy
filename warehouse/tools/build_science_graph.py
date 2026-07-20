#!/usr/bin/env python3
"""Build warehouse graph artifacts + SCIENTIFIC_AUDIT.md (Phase 4)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.repository import DataPlatform
from app.science.audit import write_scientific_audit
from app.science.builder import KnowledgeGraphBuilder
from app.science.validator import DataValidator


def main() -> None:
    data = ROOT / "data"
    wh = ROOT / "warehouse"
    platform = DataPlatform(data, strict=True)
    md = write_scientific_audit(platform, wh)
    builder = KnowledgeGraphBuilder(platform)
    graph = builder.build()
    graph_dir = wh / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    (graph_dir / "nodes.json").write_text(
        json.dumps([n.to_dict() for n in graph.nodes.values()], indent=2),
        encoding="utf-8",
    )
    (graph_dir / "edges.json").write_text(
        json.dumps([e.to_dict() for e in graph.edges], indent=2),
        encoding="utf-8",
    )
    reasoning = wh / "reasoning"
    reasoning.mkdir(parents=True, exist_ok=True)
    (reasoning / "README.md").write_text(
        "# reasoning/\n\nDeterministic recommendation explanation chains "
        "are produced at assessment time (`debug.science`). "
        "This folder holds exported samples and templates — no AI.\n",
        encoding="utf-8",
    )
    report = DataValidator(platform).validate()
    (wh / "generated" / "data_validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(f"Wrote {md}")
    print(f"Graph nodes={len(graph.nodes)} edges={len(graph.edges)} ok={report['ok']}")


if __name__ == "__main__":
    main()
