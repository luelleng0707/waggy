"""Narrow catalog facts. No SQL, paths, or warehouse file reads in the tool."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.state.recalculation import snapshot_from_digest
from app.tools.adapters.analysis import resolve_analysis
from app.tools.auth import authorize_dog
from app.tools.errors import INVALID_TOOL_INPUT, NOT_AVAILABLE, ToolFailure
from app.tools.models import GetProductsInput, ToolCaller

NOT_AVAILABLE_TOKEN = "NOT_AVAILABLE"
_MAX_LIMIT = 50
_MAX_IDS = 50

CatalogLoader = Callable[[], list[dict[str, Any]]]


def _public_product(row: dict[str, Any]) -> dict[str, Any]:
    ingredients = row.get("ingredients") or row.get("ingredient_list")
    if ingredients in (None, "", []):
        ingredients_out: Any = NOT_AVAILABLE_TOKEN
    else:
        ingredients_out = ingredients
    return {
        "product_id": row.get("product_id"),
        "product_name": row.get("product_name") or row.get("name") or NOT_AVAILABLE_TOKEN,
        "category": row.get("category") or row.get("subcategory"),
        "brand": row.get("brand"),
        "price": row.get("price") if row.get("price") is not None else row.get("monthly_cost"),
        "currency": row.get("currency"),
        "ingredients": ingredients_out,
    }


def _from_analysis(dog_id: str, caller: ToolCaller) -> list[dict[str, Any]]:
    authorize_dog(caller, dog_id)
    record = resolve_analysis(dog_id)
    snap = snapshot_from_digest(record.result_digest) or {}
    recs = snap.get("recommendations") if isinstance(snap.get("recommendations"), dict) else {}
    seen: dict[str, dict[str, Any]] = {}
    for row in recs.values():
        if not isinstance(row, dict):
            continue
        ids = list(row.get("product_ids") or [])
        names = list(row.get("product_names") or [])
        for index, pid in enumerate(ids):
            key = str(pid)
            if key in seen:
                continue
            seen[key] = {
                "product_id": key,
                "product_name": names[index] if index < len(names) else NOT_AVAILABLE_TOKEN,
                "category": None,
                "brand": None,
                "price": NOT_AVAILABLE_TOKEN,
                "currency": None,
                "ingredients": NOT_AVAILABLE_TOKEN,
            }
    return list(seen.values())


def get_products(
    payload: GetProductsInput,
    caller: ToolCaller,
    *,
    catalog_loader: CatalogLoader | None = None,
) -> dict:
    if payload.limit < 1 or payload.limit > _MAX_LIMIT:
        raise ToolFailure(INVALID_TOOL_INPUT, "limit must be between 1 and 50", field="limit")
    if payload.product_ids is not None and len(payload.product_ids) > _MAX_IDS:
        raise ToolFailure(INVALID_TOOL_INPUT, "too many product_ids", field="product_ids")
    has_filter = bool(payload.dog_id or payload.product_ids or payload.product_type or payload.category)
    if not has_filter:
        raise ToolFailure(
            INVALID_TOOL_INPUT,
            "narrow filtering is required (dog_id, product_ids, product_type, or category)",
            field="product_ids",
        )

    if payload.dog_id:
        authorize_dog(caller, payload.dog_id)

    catalog_filters = bool(payload.product_ids or payload.product_type or payload.category)
    rows: list[dict[str, Any]] = []
    source = "none"
    if catalog_filters:
        if catalog_loader is None:
            raise ToolFailure(
                NOT_AVAILABLE,
                "approved catalog is not available in this tool runtime",
                field="catalog",
            )
        try:
            loaded = catalog_loader() or []
        except Exception as exc:  # noqa: BLE001
            raise ToolFailure(NOT_AVAILABLE, "approved catalog is not available", field="catalog") from exc
        if not isinstance(loaded, list):
            loaded = []
        rows = [_public_product(item) for item in loaded if isinstance(item, dict)]
        source = "presentation_catalog"
    elif payload.dog_id:
        rows = _from_analysis(payload.dog_id, caller)
        source = "stored_analysis_digest"
    else:
        raise ToolFailure(
            INVALID_TOOL_INPUT,
            "narrow filtering is required (dog_id, product_ids, product_type, or category)",
            field="product_ids",
        )

    wanted_ids = {str(item) for item in (payload.product_ids or []) if item not in (None, "")}
    if wanted_ids:
        rows = [row for row in rows if str(row.get("product_id")) in wanted_ids]
    token = (payload.product_type or payload.category or "").strip().lower()
    if token:
        rows = [
            row
            for row in rows
            if token in str(row.get("category") or "").lower()
            or token in str(row.get("product_name") or "").lower()
        ]
    rows = rows[: payload.limit]
    return {
        "products": rows,
        "count": len(rows),
        "catalog_source": source,
        "engine_ran": False,
        "ingredients_policy": "NOT_AVAILABLE unless present on the approved catalog row",
    }
