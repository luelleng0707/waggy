"""
Scientific authoring pipeline (does not modify clinical FormulaGraph).

Usage:
  py -3 -m authoring.pipeline
  py -3 -m authoring.pipeline --submit-example
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_phase6(*, submit_example: bool = False) -> dict:
    from authoring.models import write_templates
    from authoring.builder import create_evidence_interactive
    from authoring.explorer import write_explorer
    from authoring.ml_sandbox import generate_suggestions
    from ontology import export_ontology_artifacts
    from curation.conflict_resolution import detect_conflicts
    from curation.duplicate_detection import suggest_condition_duplicates, suggest_ingredient_duplicates
    from curation.evidence_ranking import STUDY_TYPE_SCORES

    steps = []
    steps.append({"step": "templates", "path": str(write_templates())})
    steps.append({"step": "ontology", "paths": export_ontology_artifacts()})

    if submit_example:
        example = create_evidence_interactive(
            {
                "paper_title": "Example: EPA and canine joint inflammation",
                "paper_url": "https://example.org/epa-joint",
                "year": 2024,
                "study_type": "rct",
                "conditions": ["Hip Dysplasia"],
                "ingredients": ["Omega-3", "EPA"],
                "dose": "100",
                "dose_unit": "mg/kg",
                "mechanism": "Eicosanoid modulation reduces inflammation",
                "population": "Adult large-breed dogs",
                "effect": "Lower inflammatory cytokines",
                "effect_direction": "supports",
                "evidence_level": "high",
                "quote": "EPA reduced inflammatory markers in OA dogs.",
                "author": "authoring-pipeline",
                "submit": True,
            }
        )
        steps.append({"step": "evidence_builder_example", **example})

    conflicts = detect_conflicts()
    dups_c = suggest_condition_duplicates()
    dups_i = suggest_ingredient_duplicates()
    cur_dir = ROOT / "curation" / "reports"
    cur_dir.mkdir(parents=True, exist_ok=True)
    (cur_dir / "CONFLICTS.json").write_text(json.dumps(conflicts, indent=2, default=str), encoding="utf-8")
    (cur_dir / "DUPLICATES.json").write_text(
        json.dumps({"conditions": dups_c, "ingredients": dups_i}, indent=2, default=str),
        encoding="utf-8",
    )
    (cur_dir / "EVIDENCE_RANKING.md").write_text(
        "# Evidence Ranking Scale\n\n"
        + "\n".join(f"- **{k}**: score {v[0]} — {v[1]}" for k, v in STUDY_TYPE_SCORES.items())
        + "\n",
        encoding="utf-8",
    )
    steps.append({"step": "curation", "conflicts": len(conflicts), "dup_condition_groups": len(dups_c)})
    steps.append({"step": "explorer", "path": str(write_explorer())})
    steps.append({"step": "ml_sandbox", "suggestions": bool(generate_suggestions())})

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clinical_formulas_changed": False,
        "live_data_modified": False,
        "steps": steps,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit-example", action="store_true")
    args = parser.parse_args()
    summary = run_phase6(submit_example=args.submit_example)
    print(json.dumps({"ok": True, "steps": [s.get("step") for s in summary["steps"]]}, indent=2))


if __name__ == "__main__":
    main()
