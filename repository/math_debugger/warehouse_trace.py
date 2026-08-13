"""Warehouse/evidence trace extraction."""

from __future__ import annotations

from .models import WarehouseTraceRow


def build_warehouse_trace_rows(
    warehouse_row_ids: tuple[str, ...],
    evidence_ids: tuple[str, ...],
    paper_names: tuple[str, ...],
    paper_links: tuple[str, ...],
    scientific_quotes: tuple[str, ...],
) -> tuple[WarehouseTraceRow, ...]:
    rows: list[WarehouseTraceRow] = []
    max_len = max(
        len(warehouse_row_ids),
        len(evidence_ids),
        len(paper_names),
        len(paper_links),
        len(scientific_quotes),
        1,
    )
    for idx in range(max_len):
        rows.append(
            WarehouseTraceRow(
                warehouse_row_id=warehouse_row_ids[idx] if idx < len(warehouse_row_ids) else "",
                evidence_id=evidence_ids[idx] if idx < len(evidence_ids) else "",
                paper_name=paper_names[idx] if idx < len(paper_names) else "",
                paper_link=paper_links[idx] if idx < len(paper_links) else "",
                scientific_quote=scientific_quotes[idx] if idx < len(scientific_quotes) else "",
            )
        )
    return tuple(rows)
