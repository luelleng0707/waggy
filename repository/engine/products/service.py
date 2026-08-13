"""Products service skeleton."""

from __future__ import annotations

from .models import ProductContext


class ProductEngineService:
    def build_product_context(self, nutrition_context: dict) -> dict:
        # Ω1 skeleton only.
        return ProductContext().__dict__
