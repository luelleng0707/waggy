"""Shop page view-model builder."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.ui.renderer.formatters import fmt_rmb

LEGACY_MOCK_PATTERN = re.compile(r"^(SF00[1-5]|SP00[1-8]|TR00[1-2])$", re.I)
ALLOWLIST_PRODUCTS = {"FF002_CHICKEN", "SP011", "TR003"}


@dataclass
class ShopItemVM:
    product_id: str
    name: str
    category: str
    price_display: str


@dataclass
class ShopPageVM:
    categories: list[str]
    items: list[ShopItemVM]


class ShopRenderer:
    def build(self, report: dict[str, Any], catalog_df, pricing_df) -> ShopPageVM:
        included_ids: set[str] = set()
        for tier in ("essential", "balanced", "optimal"):
            for card in report.get("packageDetails", {}).get(tier, {}).get("product_cards", []):
                pid = str(card.get("product_id", ""))
                if pid:
                    included_ids.add(pid)

        items: list[ShopItemVM] = []
        for _, row in catalog_df.iterrows():
            pid = str(row.get("product_id", ""))
            if LEGACY_MOCK_PATTERN.match(pid):
                continue
            if pid not in ALLOWLIST_PRODUCTS and pid not in included_ids:
                continue
            price_row = pricing_df[pricing_df["product_id"] == pid]
            price = float(price_row.iloc[0]["list_price_rmb"]) if not price_row.empty else 0.0
            items.append(
                ShopItemVM(
                    product_id=pid,
                    name=str(row.get("product_name", pid)),
                    category=str(row.get("category", "General")),
                    price_display=fmt_rmb(price),
                )
            )

        return ShopPageVM(
            categories=["Fresh Food", "Supplements", "Functional Treats"],
            items=items,
        )
