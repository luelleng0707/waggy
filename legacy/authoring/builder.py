"""6A/6B — validate drafts and materialize warehouse-bound CSV rows (never touches live data/ until publish)."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from authoring.models import DRAFTS, EvidenceDraft, load_draft, save_draft
from curation.evidence_ranking import score_study_type
from science_pipeline.provenance import PROVENANCE_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "authoring" / "published"
STAGING_CSV = ROOT / "warehouse" / "draft" / "authoring_staging"


def validate_draft(draft: EvidenceDraft) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not (draft.paper_title or "").strip():
        errors.append("paper_title required")
    if not draft.conditions:
        errors.append("at least one condition required")
    if not draft.ingredients and not draft.mechanism:
        warnings.append("no ingredients and no mechanism — coverage will be weak")
    if draft.year is not None and (draft.year < 1900 or draft.year > datetime.now().year + 1):
        errors.append(f"invalid year: {draft.year}")
    if not draft.doi and not draft.paper_url:
        warnings.append("missing DOI and URL")
    if draft.effect_direction == "conflicts":
        warnings.append("effect_direction=conflicts — will flag in conflict detector after publish")
    quality = score_study_type(draft.study_type)
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "evidence_quality_score": quality["score"],
        "evidence_quality_label": quality["label"],
        "draft_id": draft.draft_id,
    }


def draft_to_csv_rows(draft: EvidenceDraft) -> dict[str, list[dict[str, Any]]]:
    """Project a draft into table-shaped rows (authoring staging, not live data/)."""
    paper_id = f"PAPER-{draft.draft_id[-8:].upper()}"
    provenance = {
        "created_by": draft.author,
        "created_date": draft.created_at[:10],
        "modified_by": draft.author,
        "modified_date": datetime.now(timezone.utc).date().isoformat(),
        "review_status": draft.review_status,
        "approval_date": "",
        "change_reason": draft.change_reason or "authoring studio",
        "evidence_level": draft.evidence_level,
    }
    papers = [
        {
            "paper_id": paper_id,
            "title": draft.paper_title,
            "doi": draft.doi,
            "url": draft.paper_url,
            "year": draft.year or "",
            "study_type": draft.study_type,
            **{k: provenance[k] for k in PROVENANCE_COLUMNS if k in provenance},
        }
    ]
    evidence_rows = []
    for cond in draft.conditions:
        for ing in draft.ingredients or [""]:
            evidence_rows.append(
                {
                    "evidence_id": f"EVD-{draft.draft_id[-6:].upper()}-{_safe(cond)[:8]}",
                    "paper_id": paper_id,
                    "condition": cond,
                    "ingredient_name": ing,
                    "dose": draft.dose,
                    "dose_unit": draft.dose_unit,
                    "mechanism": draft.mechanism,
                    "population": draft.population,
                    "effect": draft.effect,
                    "effect_direction": draft.effect_direction,
                    "effect_size": draft.effect_size,
                    "evidence_level": draft.evidence_level,
                    "source_name": draft.paper_title,
                    "source_quote": draft.quote,
                    "source_url": draft.paper_url,
                    "year": draft.year or "",
                    "study_type": draft.study_type,
                    **{k: provenance[k] for k in PROVENANCE_COLUMNS if k in provenance},
                }
            )
    return {"papers": papers, "ingredient_evidence": evidence_rows}


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in s.upper())


def materialize_draft(draft_id: str) -> dict[str, Any]:
    draft = load_draft(draft_id)
    result = validate_draft(draft)
    if not result["ok"]:
        return {"published": False, **result}

    rows = draft_to_csv_rows(draft)
    STAGING_CSV.mkdir(parents=True, exist_ok=True)
    PUBLISHED.mkdir(parents=True, exist_ok=True)

    written = []
    for table, records in rows.items():
        if not records:
            continue
        path = STAGING_CSV / f"{table}.csv"
        # append-aware: rewrite full staging merge of all approved drafts
        written.append(str(path.relative_to(ROOT)).replace("\\", "/"))
        _write_csv(path, records)

    draft.review_status = "validation"
    save_draft(draft)
    pub = PUBLISHED / f"{draft.draft_id}.json"
    pub.write_text(
        json.dumps({"draft": draft.to_dict(), "rows": rows, "validation": result}, indent=2),
        encoding="utf-8",
    )

    # Rebuild staging from all published packs so multiple drafts accumulate
    _rebuild_staging_from_published()

    return {
        "published": True,
        "staging_dir": str(STAGING_CSV.relative_to(ROOT)).replace("\\", "/"),
        "artifact": str(pub.relative_to(ROOT)).replace("\\", "/"),
        "note": "Staging only — live data/ unchanged until governance release promotes authoring staging",
        **result,
        "row_counts": {k: len(v) for k, v in rows.items()},
    }


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    # If file exists, merge by evidence_id / paper_id
    existing: list[dict[str, Any]] = []
    key = "evidence_id" if "evidence_id" in records[0] else "paper_id"
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            existing = list(csv.DictReader(f))
    by_key = {str(r.get(key)): r for r in existing if r.get(key)}
    for r in records:
        by_key[str(r.get(key))] = r
    merged = list(by_key.values())
    fields = list(merged[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(merged)


def _rebuild_staging_from_published() -> None:
    papers: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for p in PUBLISHED.glob("*.json"):
        try:
            pack = json.loads(p.read_text(encoding="utf-8"))
            rows = pack.get("rows") or {}
            papers.extend(rows.get("papers") or [])
            evidence.extend(rows.get("ingredient_evidence") or [])
        except Exception:
            continue
    STAGING_CSV.mkdir(parents=True, exist_ok=True)
    if papers:
        _write_csv(STAGING_CSV / "papers.csv", papers)
    if evidence:
        _write_csv(STAGING_CSV / "ingredient_evidence.csv", evidence)


def create_evidence_interactive(payload: dict[str, Any]) -> dict[str, Any]:
    """API/CLI entry: New Paper → conditions → ingredients → … → submit."""
    draft = EvidenceDraft(
        paper_title=str(payload.get("paper_title") or payload.get("title") or ""),
        paper_url=str(payload.get("paper_url") or payload.get("url") or ""),
        doi=str(payload.get("doi") or ""),
        year=int(payload["year"]) if payload.get("year") not in (None, "") else None,
        study_type=str(payload.get("study_type") or "observational"),
        conditions=list(payload.get("conditions") or []),
        ingredients=list(payload.get("ingredients") or []),
        dose=str(payload.get("dose") or ""),
        dose_unit=str(payload.get("dose_unit") or ""),
        mechanism=str(payload.get("mechanism") or ""),
        population=str(payload.get("population") or ""),
        effect=str(payload.get("effect") or ""),
        effect_direction=str(payload.get("effect_direction") or "supports"),
        effect_size=str(payload.get("effect_size") or ""),
        evidence_level=str(payload.get("evidence_level") or "medium"),
        quote=str(payload.get("quote") or ""),
        author=str(payload.get("author") or "researcher"),
        change_reason=str(payload.get("change_reason") or "evidence builder submit"),
    )
    path = save_draft(draft)
    validation = validate_draft(draft)
    out: dict[str, Any] = {
        "draft_id": draft.draft_id,
        "draft_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "validation": validation,
    }
    if payload.get("submit") and validation["ok"]:
        out["materialize"] = materialize_draft(draft.draft_id)
    return out
