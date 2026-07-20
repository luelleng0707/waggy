"""Multi-dimensional scientific confidence (honest, separate from one fake score)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ExecutionConfidence:
    percent: float
    note: str = "Pipeline nodes completed without error"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceConfidence:
    percent: float
    paper_count: int = 0
    citation_count: int = 0
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CoverageConfidence:
    percent: float
    has_papers: bool = False
    has_ingredients: bool = False
    has_foods: bool = False
    has_products: bool = False
    has_prevention: bool = False
    missing: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["missing"] = d.get("missing") or []
        return d


@dataclass
class StudyQuality:
    grade: str  # A | B | C | D | U
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationConfidence:
    percent: float
    components: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_CONF_MAP = {"high": 0.9, "medium": 0.7, "low": 0.45, "a": 0.92, "b": 0.8, "c": 0.6}


def _grade_from_levels(levels: list[str]) -> StudyQuality:
    if not levels:
        return StudyQuality("U", "No confidence_level on linked rows")
    norm = [str(x).strip().lower() for x in levels if str(x).strip()]
    if any(x in ("high", "a") for x in norm):
        return StudyQuality("A", "At least one high-confidence citation")
    if any(x in ("medium", "b") for x in norm):
        return StudyQuality("B", "Medium-confidence citations only")
    if any(x in ("low", "c") for x in norm):
        return StudyQuality("C", "Low-confidence citations only")
    return StudyQuality("D", f"Unrecognized levels: {sorted(set(norm))[:5]}")


def build_confidence_bundle(
    *,
    execution_ok: bool = True,
    evidence_rows: list[dict[str, Any]] | None = None,
    coverage: dict[str, bool] | None = None,
) -> dict[str, Any]:
    evidence_rows = evidence_rows or []
    coverage = coverage or {}
    exec_c = ExecutionConfidence(100.0 if execution_ok else 0.0)

    papers = {str(e.get("paper_id") or e.get("paper_title") or "") for e in evidence_rows if e}
    papers.discard("")
    levels = [str(e.get("confidence") or "") for e in evidence_rows]
    scores = [_CONF_MAP.get(str(l).lower(), 0.5) for l in levels if l]
    ev_pct = round(100.0 * (sum(scores) / len(scores)), 1) if scores else (40.0 if papers else 0.0)
    ev_c = EvidenceConfidence(
        percent=ev_pct,
        paper_count=len(papers),
        citation_count=len(evidence_rows),
        note="Mean of mapped confidence_level weights" if scores else "Sparse or missing confidence_level",
    )

    flags = {
        "papers": bool(coverage.get("has_papers") or papers),
        "ingredients": bool(coverage.get("has_ingredients")),
        "foods": bool(coverage.get("has_foods")),
        "products": bool(coverage.get("has_products")),
        "prevention": bool(coverage.get("has_prevention")),
    }
    missing = [k for k, v in flags.items() if not v]
    cov_pct = round(100.0 * (len(flags) - len(missing)) / max(len(flags), 1), 1)
    cov_c = CoverageConfidence(
        percent=cov_pct,
        has_papers=flags["papers"],
        has_ingredients=flags["ingredients"],
        has_foods=flags["foods"],
        has_products=flags["products"],
        has_prevention=flags["prevention"],
        missing=missing,
    )

    quality = _grade_from_levels(levels)
    # Recommendation blends execution, evidence, coverage (deterministic weights)
    rec_pct = round(
        0.25 * exec_c.percent + 0.40 * ev_c.percent + 0.35 * cov_c.percent,
        1,
    )
    rec = RecommendationConfidence(
        percent=rec_pct,
        components={
            "execution": exec_c.to_dict(),
            "evidence": ev_c.to_dict(),
            "coverage": cov_c.to_dict(),
            "study_quality": quality.to_dict(),
        },
    )
    return {
        "execution": exec_c.to_dict(),
        "evidence": ev_c.to_dict(),
        "coverage": cov_c.to_dict(),
        "study_quality": quality.to_dict(),
        "recommendation": rec.to_dict(),
    }
