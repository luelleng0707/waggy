"""6E — duplicate / synonym detection for conditions and ingredients."""

from __future__ import annotations

from app.core.paths import clinical_root_str, resolve_clinical_root

import re
from collections import defaultdict
from typing import Any

from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder

# Seed synonym groups (extensible; curation can grow this file)
CONDITION_ALIASES: dict[str, list[str]] = {
    "hip dysplasia": ["hip dysplasia", "canine hip dysplasia", "hd", "coxofemoral dysplasia"],
    "atopic dermatitis": ["atopic dermatitis", "atopy", "allergic dermatitis"],
    "obesity": ["obesity", "overweight", "adiposity"],
}

INGREDIENT_ALIASES: dict[str, list[str]] = {
    "omega-3": ["omega-3", "omega 3", "fish oil", "salmon oil", "marine oil", "epa", "dha"],
    "glucosamine": ["glucosamine", "glcnhcl", "glucosamine hcl", "glucosamine hydrochloride"],
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def suggest_condition_duplicates(platform: DataPlatform | None = None) -> list[dict[str, Any]]:
    platform = platform or DataPlatform(clinical_root_str(), strict=True)
    graph = KnowledgeGraphBuilder(platform).build()
    labels = [n.label for n in graph.by_type("condition")]
    suggestions = []

    # Alias group hits
    for canon, aliases in CONDITION_ALIASES.items():
        hits = [lab for lab in labels if _norm(lab) in {_norm(a) for a in aliases} or any(_norm(a) in _norm(lab) for a in aliases)]
        # also find near-equal
        for lab in labels:
            if _norm(lab) == _norm(canon) or _norm(lab) in {_norm(a) for a in aliases}:
                if lab not in hits:
                    hits.append(lab)
        uniq = sorted(set(hits))
        if len(uniq) >= 1:
            suggestions.append(
                {
                    "canonical": canon.title(),
                    "candidates": uniq,
                    "reason": "alias_group",
                    "same_condition": len(uniq) > 1,
                }
            )

    # Fuzzy: identical after normalization
    buckets: dict[str, list[str]] = defaultdict(list)
    for lab in labels:
        buckets[_norm(lab)].append(lab)
    for key, group in buckets.items():
        if len(set(group)) > 1:
            suggestions.append(
                {
                    "canonical": group[0],
                    "candidates": sorted(set(group)),
                    "reason": "normalized_match",
                    "same_condition": True,
                }
            )
    return suggestions


def suggest_ingredient_duplicates(platform: DataPlatform | None = None) -> list[dict[str, Any]]:
    platform = platform or DataPlatform(clinical_root_str(), strict=True)
    graph = KnowledgeGraphBuilder(platform).build()
    labels = [n.label for n in graph.by_type("ingredient")]
    suggestions = []
    for canon, aliases in INGREDIENT_ALIASES.items():
        hits = []
        for lab in labels:
            nl = _norm(lab)
            if nl == _norm(canon) or any(_norm(a) in nl or nl in _norm(a) for a in aliases):
                hits.append(lab)
        if hits:
            suggestions.append(
                {
                    "canonical": canon,
                    "candidates": sorted(set(hits)),
                    "reason": "alias_group",
                    "same_ingredient": len(set(hits)) > 1,
                }
            )
    return suggestions
