"""Commercial catalog eligibility. Not nutrient min/max and not ranking math.

Preference exclusions shrink the candidate list before PACKAGE_OPTIMIZER_V2_1
enumerates combinations. Scientific constraints still run on whatever remains.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Any, Iterator

_INGREDIENT_KEYS = (
    "ingredient_name",
    "component_name",
    "name",
    "ingredient",
    "ingredient_key",
    "component",
)

_active: ContextVar["PackageConstraints | None"] = ContextVar(
    "waggy_package_constraints",
    default=None,
)


@dataclass(frozen=True)
class PackageConstraints:
    ingredient_exclusions: tuple[str, ...] = ()
    product_exclusions: tuple[str, ...] = ()
    monthly_budget: float | None = None

    def eligibility_empty(self) -> bool:
        return not self.ingredient_exclusions and not self.product_exclusions

    def as_dict(self) -> dict[str, Any]:
        return {
            "applied": not self.eligibility_empty() or self.monthly_budget is not None,
            "ingredient_exclusions": list(self.ingredient_exclusions),
            "product_exclusions": list(self.product_exclusions),
            "monthly_budget": self.monthly_budget,
            "scientific": False,
        }


def empty_eligibility_report(candidate_count: int) -> dict[str, Any]:
    return {
        "applied": False,
        "scientific": False,
        "ingredient_exclusions": [],
        "product_exclusions": [],
        "removed_product_ids": [],
        "removed": [],
        "candidate_count_before": candidate_count,
        "candidate_count_after": candidate_count,
    }


@contextmanager
def using_package_constraints(constraints: PackageConstraints | None) -> Iterator[PackageConstraints | None]:
    token: Token = _active.set(constraints)
    try:
        yield constraints
    finally:
        _active.reset(token)


def active_constraints() -> PackageConstraints | None:
    return _active.get()


def _blob(product: dict[str, Any]) -> str:
    parts: list[str] = [
        str(product.get("product_id") or ""),
        str(product.get("product_name") or ""),
        str(product.get("tags") or ""),
        str(product.get("short_description") or ""),
        str(product.get("description") or ""),
        str(product.get("subcategory") or ""),
    ]
    for comp in product.get("components") or []:
        if not isinstance(comp, dict):
            continue
        for key in _INGREDIENT_KEYS:
            val = comp.get(key)
            if val not in (None, ""):
                parts.append(str(val))
    for item in product.get("active_ingredients") or []:
        if isinstance(item, dict):
            parts.append(str(item.get("name") or item.get("ingredient") or ""))
        else:
            parts.append(str(item))
    aliases = product.get("alias_groups") or {}
    if isinstance(aliases, dict):
        for key, vals in aliases.items():
            parts.append(str(key))
            if isinstance(vals, (list, tuple)):
                parts.extend(str(v) for v in vals)
            else:
                parts.append(str(vals))
    return " ".join(parts).casefold()


def _ingredient_hit(blob: str, token: str) -> bool:
    needle = token.strip().casefold()
    if len(needle) < 3:
        return False
    return needle in blob


def _product_hit(product: dict[str, Any], token: str) -> bool:
    needle = token.strip().casefold()
    if not needle:
        return False
    pid = str(product.get("product_id") or "").casefold()
    name = str(product.get("product_name") or "").casefold()
    return pid == needle or name == needle or needle in pid


def candidate_excluded(product: dict[str, Any], constraints: PackageConstraints) -> str | None:
    pid = str(product.get("product_id") or "")
    for token in constraints.product_exclusions:
        if _product_hit(product, token):
            return f"product_exclusion:{token}"
    blob = _blob(product)
    for token in constraints.ingredient_exclusions:
        if _ingredient_hit(blob, token):
            return f"ingredient_exclusion:{token}"
    return None if pid else "missing_product_id"


def filter_candidates(
    candidates: list[dict[str, Any]],
    constraints: PackageConstraints,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for item in candidates:
        reason = candidate_excluded(item, constraints)
        if reason:
            removed.append({"product_id": item.get("product_id"), "reason": reason})
            continue
        kept.append(item)
    report = {
        "applied": True,
        "scientific": False,
        "ingredient_exclusions": list(constraints.ingredient_exclusions),
        "product_exclusions": list(constraints.product_exclusions),
        "removed_product_ids": [row["product_id"] for row in removed],
        "removed": removed,
        "candidate_count_before": len(candidates),
        "candidate_count_after": len(kept),
    }
    return kept, report


def apply_active_constraints(
    candidates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Filter catalog candidates. Does not change nutrient min/max or ranking math."""
    constraints = _active.get()
    empty = empty_eligibility_report(len(candidates))
    if constraints is None or constraints.eligibility_empty():
        return candidates, empty
    return filter_candidates(candidates, constraints)
