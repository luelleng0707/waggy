"""Contracts for product services."""

from __future__ import annotations

from typing import Protocol


class ProductService(Protocol):
    def build_product_context(self, nutrition_context: dict) -> dict:
        """Return product intelligence placeholders."""
