"""Transparent evidence quality scoring (6F) — deterministic, no ML."""

from __future__ import annotations

from typing import Any

# Higher = stronger. Transparent and documented.
STUDY_TYPE_SCORES: dict[str, tuple[int, str]] = {
    "meta-analysis": (100, "Meta-analysis / systematic review"),
    "systematic review": (95, "Systematic review"),
    "rct": (90, "Randomized controlled trial"),
    "randomized": (90, "Randomized controlled trial"),
    "cohort": (70, "Cohort study"),
    "case-control": (65, "Case-control"),
    "observational": (55, "Observational"),
    "clinical": (50, "Clinical report"),
    "case-report": (35, "Case report"),
    "case report": (35, "Case report"),
    "in vitro": (25, "In vitro"),
    "animal": (40, "Animal / preclinical"),
    "expert": (20, "Expert opinion"),
    "expert opinion": (20, "Expert opinion"),
    "guideline": (75, "Guideline"),
    "unknown": (10, "Unknown"),
}


def score_study_type(study_type: str) -> dict[str, Any]:
    raw = (study_type or "unknown").strip().lower()
    for key, (score, label) in STUDY_TYPE_SCORES.items():
        if key in raw or raw in key:
            return {"score": score, "label": label, "study_type": study_type}
    return {"score": 10, "label": "Unclassified", "study_type": study_type}


def rank_evidence_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for r in rows:
        st = str(r.get("study_type") or r.get("evidence_level") or "unknown")
        # map evidence_level soft boost
        q = score_study_type(st)
        level = str(r.get("evidence_level") or "").lower()
        boost = {"high": 10, "medium": 5, "low": 0}.get(level, 0)
        ranked.append({**r, "quality_score": q["score"] + boost, "quality_label": q["label"]})
    ranked.sort(key=lambda x: -int(x.get("quality_score") or 0))
    return ranked
