"""Draft scientific objects — researchers edit these, not CSVs."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "authoring" / "drafts"
TEMPLATES = ROOT / "authoring" / "templates"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "untitled"


@dataclass
class EvidenceDraft:
    """Structured evidence entry (6A/6B) — becomes CSV rows after validation."""

    paper_title: str
    paper_url: str = ""
    doi: str = ""
    year: int | None = None
    study_type: str = "observational"  # rct | meta-analysis | observational | case-report | expert
    conditions: list[str] = field(default_factory=list)
    ingredients: list[str] = field(default_factory=list)
    dose: str = ""
    dose_unit: str = ""
    mechanism: str = ""
    population: str = ""
    effect: str = ""
    effect_direction: str = "supports"  # supports | reduces | neutral | conflicts
    effect_size: str = ""
    evidence_level: str = "medium"
    quote: str = ""
    author: str = "researcher"
    change_reason: str = ""
    draft_id: str = field(default_factory=lambda: f"draft-{uuid.uuid4().hex[:10]}")
    created_at: str = field(default_factory=_now)
    review_status: str = "draft"  # draft | validation | scientific_review | approved

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceDraft":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


def save_draft(draft: EvidenceDraft) -> Path:
    DRAFTS.mkdir(parents=True, exist_ok=True)
    path = DRAFTS / f"{draft.draft_id}.json"
    path.write_text(json.dumps(draft.to_dict(), indent=2), encoding="utf-8")
    return path


def load_draft(draft_id: str) -> EvidenceDraft:
    path = DRAFTS / f"{draft_id}.json"
    if not path.exists():
        # allow bare id without prefix
        matches = list(DRAFTS.glob(f"*{draft_id}*.json"))
        if not matches:
            raise FileNotFoundError(draft_id)
        path = matches[0]
    return EvidenceDraft.from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_drafts() -> list[dict[str, Any]]:
    DRAFTS.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted(DRAFTS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            out.append(
                {
                    "draft_id": d.get("draft_id"),
                    "paper_title": d.get("paper_title"),
                    "review_status": d.get("review_status"),
                    "conditions": d.get("conditions"),
                    "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                }
            )
        except Exception:
            continue
    return out


def write_templates() -> Path:
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    example = EvidenceDraft(
        paper_title="Example: EPA in canine osteoarthritis",
        paper_url="https://example.org/paper",
        year=2024,
        study_type="rct",
        conditions=["Hip Dysplasia", "Osteoarthritis"],
        ingredients=["Omega-3", "EPA"],
        dose="100",
        dose_unit="mg/kg",
        mechanism="Anti-inflammatory eicosanoid modulation",
        population="Adult large-breed dogs with OA",
        effect="Reduced inflammatory markers",
        effect_direction="supports",
        evidence_level="high",
        quote="EPA supplementation reduced cytokine expression…",
        author="curator",
        change_reason="Initial curated entry",
    )
    path = TEMPLATES / "evidence_entry.template.json"
    path.write_text(json.dumps(example.to_dict(), indent=2), encoding="utf-8")
    return path
