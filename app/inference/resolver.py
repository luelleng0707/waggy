"""
Central string / alias resolver.

All agent modules should prefer these helpers over local copies of
ingredient_key / condition_key / canonical_join_key.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

import pandas as pd


def canonical_join_key(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def condition_key(name: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")


def ingredient_key(name: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")


def normalize_label(value: str | None) -> str:
    return str(value or "").strip()


def component_to_ingredient_key(name: str) -> str:
    """Parity remaps + formatting normalization before CSV alias lookup."""
    raw = str(name or "").strip()
    # Formatting variants → stable text before keying
    lowered = raw.lower().replace("＋", "+").replace("–", "-").replace("—", "-")
    lowered = lowered.replace("epa+dha", "omega_3").replace("epa-dha", "omega_3")
    lowered = lowered.replace("epa dha", "omega_3").replace("epa/dha", "omega_3")
    key = ingredient_key(lowered.replace("+", "_"))
    if key in ("epa_dha", "epadha", "epa_and_dha"):
        return "omega_3"
    if key == "joint_health_formula":
        return "glucosamine"
    if key == "brady_yeast_probiotics":
        return "probiotics"
    return key


def resolve_via_alias_groups(
    target_key: str,
    component_key: str,
    alias_groups: dict[str, set[str]],
) -> bool:
    if target_key == component_key:
        return True
    for aliases in alias_groups.values():
        if target_key in aliases and component_key in aliases:
            return True
    return False


def taxonomy_parents(
    ingredient: str,
    taxonomy_df: pd.DataFrame | None,
    *,
    max_depth: int = 8,
) -> list[str]:
    """Walk ingredient → parent chain. Empty if no taxonomy row."""
    if taxonomy_df is None or taxonomy_df.empty:
        return []
    by_ing = {}
    for _, row in taxonomy_df.iterrows():
        by_ing[normalize_label(row.get("ingredient"))] = normalize_label(row.get("parent"))
    chain: list[str] = []
    cur = normalize_label(ingredient)
    seen: set[str] = set()
    for _ in range(max_depth):
        parent = by_ing.get(cur)
        if not parent or parent in seen:
            break
        chain.append(parent)
        seen.add(parent)
        cur = parent
    return chain


def resolve_canonical_ingredient(
    name: str,
    *,
    taxonomy_df: pd.DataFrame | None = None,
    alias_groups: dict[str, set[str]] | None = None,
) -> dict[str, Any]:
    """Best-effort canonical resolution (no embeddings yet)."""
    raw = normalize_label(name)
    key = ingredient_key(raw)
    if alias_groups:
        for canon, aliases in alias_groups.items():
            if key == canon or key in aliases:
                return {
                    "input": raw,
                    "canonical_key": canon,
                    "method": "alias",
                    "parents": taxonomy_parents(raw, taxonomy_df),
                }
    parents = taxonomy_parents(raw, taxonomy_df)
    if parents:
        return {
            "input": raw,
            "canonical_key": ingredient_key(parents[0]) if parents else key,
            "method": "taxonomy",
            "parents": parents,
        }
    return {
        "input": raw,
        "canonical_key": key,
        "method": "passthrough",
        "parents": [],
    }
