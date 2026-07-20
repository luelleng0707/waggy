"""Standard clinical report schema — frontend renders widgets only."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "4.0.0"
ALGORITHM_VERSION = "PPIE"

# Widget types the frontend understands. No page-specific types.
WIDGET_TYPES = frozenset({
    "text",
    "metric",
    "metrics",
    "accordion",
    "progress",
    "timeline",
    "comparison",
    "chart",
    "warning",
    "package",
    "product",
    "risk",
    "activity",
    "trait",
    "list",
    "chips",
    "ledger",
    "evidence",
    "trace",
    "nav",
})


AWAITING_PUBLICATION = "Awaiting linked publication."
AWAITING_DATABASE = "Awaiting database content."


def empty_reference() -> dict[str, Any]:
    return {
        "status": "placeholder",
        "label": AWAITING_PUBLICATION,
        "evidence_level": None,
        "consensus": None,
        "quote": None,
        "source_name": None,
        "source_url": None,
        "year": None,
        "csv_source": None,
    }


def make_reference(
    *,
    status: str = "placeholder",
    label: str | None = None,
    evidence_level: Any = None,
    consensus: Any = None,
    quote: Any = None,
    source_name: Any = None,
    source_url: Any = None,
    year: Any = None,
    csv_source: Any = None,
) -> dict[str, Any]:
    url = str(source_url).strip() if source_url not in (None, "", "nan") else ""
    if not url:
        return {
            **empty_reference(),
            "evidence_level": evidence_level,
            "source_name": source_name,
            "csv_source": csv_source,
            "label": label or AWAITING_PUBLICATION,
        }
    return {
        "status": "published",
        "label": label or source_name or "Supporting literature",
        "evidence_level": evidence_level,
        "consensus": consensus or evidence_level,
        "quote": quote,
        "source_name": source_name,
        "source_url": url,
        "year": year,
        "csv_source": csv_source,
    }


def make_widget(widget_type: str, **payload: Any) -> dict[str, Any]:
    if widget_type not in WIDGET_TYPES:
        raise ValueError(f"Unknown widget type: {widget_type}")
    out = {"type": widget_type}
    out.update({k: v for k, v in payload.items() if v is not None})
    return out


def make_section(
    *,
    section_id: str,
    title: str,
    priority: int,
    summary: str = "",
    score: dict[str, Any] | None = None,
    widgets: list[dict[str, Any]] | None = None,
    references: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "id": section_id,
        "title": title,
        "priority": priority,
        "summary": summary or "",
        "score": score,
        "widgets": widgets or [],
        "references": references or [],
    }


def make_trace(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Mathematical / data provenance chain for a recommendation."""
    return make_widget("trace", steps=steps)


def make_report_envelope(
    *,
    sections: list[dict[str, Any]],
    data_version: str,
    csv_hash: str,
    algorithm_version: str = ALGORITHM_VERSION,
    schema_version: str = SCHEMA_VERSION,
    ppie_version: Any = None,
    package_reports: dict[str, Any] | None = None,
    product_reports: dict[str, Any] | None = None,
    navigation: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    from datetime import datetime, timezone

    return {
        "schema_version": schema_version,
        "algorithm_version": algorithm_version,
        "ppie_version": ppie_version,
        "data_version": data_version,
        "csv_hash": csv_hash,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "navigation": navigation
        or [
            {"id": s["id"], "label": s["title"]}
            for s in sorted(sections, key=lambda x: x.get("priority", 100))
        ],
        "sections": sorted(sections, key=lambda x: x.get("priority", 100)),
        "package_reports": package_reports or {},
        "product_reports": product_reports or {},
    }
