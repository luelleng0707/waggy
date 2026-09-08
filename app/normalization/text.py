"""Fold text for lookup. Representation only — not scientific reasoning."""

from __future__ import annotations

import re

_WS = re.compile(r"\s+")


def fold_lookup_key(raw: str | None) -> str:
    """Trim, collapse whitespace, case-fold. Does not strip hyphens or punctuation."""
    if raw is None:
        return ""
    return _WS.sub(" ", str(raw).strip()).casefold()


def is_blank(raw: str | None) -> bool:
    return fold_lookup_key(raw) == ""
