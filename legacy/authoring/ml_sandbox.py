"""
6M — Future ML sandbox (EXPERIMENTAL ONLY).

Never changes recommendations. Never writes to live data/ or FormulaGraph.
Produces curation *suggestions* for human review only.
"""

from __future__ import annotations

from app.core.paths import clinical_root_str, resolve_clinical_root

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from curation.duplicate_detection import suggest_condition_duplicates, suggest_ingredient_duplicates
from app.science.coverage import KnowledgeCoverageReport
from app.science.builder import KnowledgeGraphBuilder
from app.data.repository import DataPlatform

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "authoring" / "studio" / "ml_sandbox"


def generate_suggestions() -> dict[str, Any]:
    """Heuristic 'ML-like' suggestions without model calls — gap clustering & synonym hints."""
    platform = DataPlatform(clinical_root_str(), strict=True)
    graph = KnowledgeGraphBuilder(platform).build()
    cov = KnowledgeCoverageReport(graph).build()

    gaps = [r for r in (cov.get("rows") or []) if r.get("missing")]
    # Cluster by missing facet
    by_gap = Counter()
    for r in gaps:
        for m in r.get("missing") or []:
            by_gap[m] += 1

    suggestions = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "EXPERIMENTAL. Human review required. "
            "These suggestions MUST NOT auto-update the warehouse or clinical engine."
        ),
        "literature_gaps": gaps[:50],
        "gap_clusters": by_gap.most_common(),
        "synonym_suggestions": {
            "conditions": suggest_condition_duplicates(platform),
            "ingredients": suggest_ingredient_duplicates(platform),
        },
        "curation_priorities": sorted(
            gaps,
            key=lambda r: len(r.get("missing") or []),
            reverse=True,
        )[:30],
        "clinical_path_untouched": True,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "SUGGESTIONS.json").write_text(json.dumps(suggestions, indent=2, default=str), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# ML Sandbox\n\n"
        "Suggestions only. Production path remains:\n\n"
        "`Warehouse → Repository → ExecutionContext → FormulaGraph → AssessmentResult`\n",
        encoding="utf-8",
    )
    return suggestions
