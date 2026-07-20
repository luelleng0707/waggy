"""Paper registry + adapter — normalize citations without changing formula inputs."""

from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

CITATION_COLS = (
    "source_name",
    "source_title",
    "source_quote",
    "source_url",
    "year",
    "journal",
    "authors",
    "doi",
    "pmid",
    "sample_population",
    "sample_size",
    "confidence_level",
    "study_type",
)


def _paper_id_from_row(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("source_name") or row.get("source_title") or "").strip(),
        str(row.get("source_url") or row.get("url") or "").strip(),
        str(row.get("year") or "").strip(),
        str(row.get("source_quote") or row.get("quote") or "").strip()[:120],
    ]
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"PAPER_{digest}"


class PaperAdapter:
    """Extract papers.csv rows and join paper_id metadata back onto science rows."""

    def __init__(self, papers_df: pd.DataFrame | None = None):
        self.papers = papers_df.copy() if papers_df is not None else pd.DataFrame()
        self._by_id: dict[str, dict[str, Any]] = {}
        if not self.papers.empty and "paper_id" in self.papers.columns:
            for _, r in self.papers.iterrows():
                self._by_id[str(r["paper_id"])] = r.to_dict()

    @classmethod
    def extract_from_frames(cls, frames: list[pd.DataFrame]) -> "PaperAdapter":
        papers: dict[str, dict[str, Any]] = {}
        for df in frames:
            if df is None or df.empty:
                continue
            for _, row in df.iterrows():
                rec = row.to_dict()
                # Skip rows with no citation signal
                if not any(str(rec.get(c) or "").strip() for c in ("source_name", "source_url", "source_quote", "year")):
                    continue
                pid = _paper_id_from_row(rec)
                if pid in papers:
                    continue
                papers[pid] = {
                    "paper_id": pid,
                    "title": str(rec.get("source_name") or rec.get("source_title") or ""),
                    "authors": str(rec.get("authors") or ""),
                    "journal": str(rec.get("journal") or rec.get("source_name") or ""),
                    "year": str(rec.get("year") or ""),
                    "doi": str(rec.get("doi") or ""),
                    "pmid": str(rec.get("pmid") or ""),
                    "url": str(rec.get("source_url") or rec.get("url") or ""),
                    "sample_size": str(rec.get("sample_size") or ""),
                    "study_type": str(rec.get("study_type") or ""),
                    "country": str(rec.get("country") or ""),
                    "species": str(rec.get("species") or "canine"),
                    "quote": str(rec.get("source_quote") or rec.get("quote") or ""),
                }
        df = pd.DataFrame(list(papers.values())) if papers else pd.DataFrame(
            columns=[
                "paper_id", "title", "authors", "journal", "year", "doi", "pmid",
                "url", "sample_size", "study_type", "country", "species", "quote",
            ]
        )
        return cls(df)

    def stamp_paper_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()
        out = df.copy()
        ids = []
        for _, row in out.iterrows():
            rec = row.to_dict()
            if any(str(rec.get(c) or "").strip() for c in ("source_name", "source_url", "source_quote", "year")):
                ids.append(_paper_id_from_row(rec))
            else:
                ids.append("")
        out["paper_id"] = ids
        return out

    def inject_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """Join paper_id → citation fields. Does not overwrite non-empty existing cols."""
        if df.empty or "paper_id" not in df.columns or not self._by_id:
            return df.copy()
        out = df.copy()
        for col in ("source_name", "source_quote", "source_url", "year"):
            if col not in out.columns:
                out[col] = ""
        for idx, row in out.iterrows():
            pid = str(row.get("paper_id") or "")
            paper = self._by_id.get(pid)
            if not paper:
                continue
            if not str(row.get("source_name") or "").strip():
                out.at[idx, "source_name"] = paper.get("title") or paper.get("journal") or ""
            if not str(row.get("source_quote") or "").strip():
                out.at[idx, "source_quote"] = paper.get("quote") or ""
            if not str(row.get("source_url") or "").strip():
                out.at[idx, "source_url"] = paper.get("url") or ""
            if not str(row.get("year") or "").strip():
                out.at[idx, "year"] = paper.get("year") or ""
        return out
