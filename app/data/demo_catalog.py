"""Isolated interview/demo product catalog overlay.

Activated only when WAGTOPIA_DEMO_MODE is truthy. Overlays product-domain
tables consumed by the existing catalog interface, PRODUCT_MATCH_V2_1, and
PACKAGE_OPTIMIZER_V2_1. Does not modify warehouse CSVs or scientific formulas.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import pandas as pd

DEMO_ENV = "WAGTOPIA_DEMO_MODE"
DEMO_TABLES = frozenset(
    {
        "products",
        "product_pricing",
        "product_components",
        "product_feeding_rules",
        "product_functions",
    }
)

CANONICAL_PRODUCT_COLUMNS = (
    "product_id",
    "product_name",
    "brand",
    "category",
    "subcategory",
    "status",
    "short_description",
    "description",
    "image_url",
    "purchase_url",
    "tags",
)

_DEMO_PRODUCTS: tuple[dict[str, str], ...] = (
    {
        "product_id": "SF001",
        "product_name": "Demo Fresh Beef Bowl",
        "brand": "Wagtopia Demo",
        "category": "Fresh Food",
        "subcategory": "fresh_combo",
        "status": "active",
        "short_description": "Demo premium nutrition product",
        "description": "Demonstration staple nutrition product for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo staple nutrition",
    },
    {
        "product_id": "SF002",
        "product_name": "Demo Fresh Chicken Bowl",
        "brand": "Wagtopia Demo",
        "category": "Fresh Food",
        "subcategory": "fresh_single",
        "status": "active",
        "short_description": "Demo premium nutrition product",
        "description": "Demonstration single-protein staple for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo staple nutrition",
    },
    {
        "product_id": "TR011",
        "product_name": "Demo Joint Mobility Chew",
        "brand": "Wagtopia Demo",
        "category": "All-Natural Treats",
        "subcategory": "functional_chew",
        "status": "active",
        "short_description": "Demo joint/mobility treat",
        "description": "Demonstration chew used as a catalog input for package optimization.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo joint mobility",
    },
    {
        "product_id": "TR001",
        "product_name": "Demo Dental Care Chew",
        "brand": "Wagtopia Demo",
        "category": "All-Natural Treats",
        "subcategory": "dental",
        "status": "active",
        "short_description": "Demo dental/oral care treat",
        "description": "Demonstration oral-care chew for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo dental oral",
    },
    {
        "product_id": "TR003",
        "product_name": "Demo Skin and Coat Oil",
        "brand": "Wagtopia Demo",
        "category": "Nutritional Supplements",
        "subcategory": "skin_coat",
        "status": "active",
        "short_description": "Demo skin/coat supplement",
        "description": "Demonstration skin and coat supplement for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo skin coat",
    },
    {
        "product_id": "TR007",
        "product_name": "Demo Daily Nutrition Capsule",
        "brand": "Wagtopia Demo",
        "category": "Nutritional Supplements",
        "subcategory": "daily",
        "status": "active",
        "short_description": "Demo nutritional supplement",
        "description": "Demonstration daily supplement for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo supplement",
    },
    {
        "product_id": "TR008",
        "product_name": "Demo Gut Balance Capsule",
        "brand": "Wagtopia Demo",
        "category": "Nutritional Supplements",
        "subcategory": "digestive",
        "status": "active",
        "short_description": "Demo nutritional supplement",
        "description": "Demonstration digestive supplement for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo gut",
    },
    {
        "product_id": "JB001",
        "product_name": "Demo Joint Support Tablet",
        "brand": "Wagtopia Demo",
        "category": "Nutritional Supplements",
        "subcategory": "joint",
        "status": "active",
        "short_description": "Demo joint/mobility supplement",
        "description": "Demonstration joint-support supplement for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo joint",
    },
    {
        "product_id": "HY001",
        "product_name": "Demo Hydration Broth",
        "brand": "Wagtopia Demo",
        "category": "All-Natural Treats",
        "subcategory": "hydration",
        "status": "active",
        "short_description": "Demo hydration / pet drink",
        "description": "Demonstration hydration broth for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo hydration drink",
    },
    {
        "product_id": "HG001",
        "product_name": "Demo Ear and Paw Hygiene Wipes",
        "brand": "Wagtopia Demo",
        "category": "Homestyle Bakery",
        "subcategory": "hygiene",
        "status": "active",
        "short_description": "Demo hygiene product",
        "description": "Demonstration hygiene item for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo hygiene",
    },
    {
        "product_id": "SK001",
        "product_name": "Demo Coat Conditioning Spray",
        "brand": "Wagtopia Demo",
        "category": "Nutritional Supplements",
        "subcategory": "coat",
        "status": "active",
        "short_description": "Demo skin/coat care product",
        "description": "Demonstration coat-care product for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo coat",
    },
    {
        "product_id": "DN001",
        "product_name": "Demo Oral Care Gel",
        "brand": "Wagtopia Demo",
        "category": "All-Natural Treats",
        "subcategory": "dental",
        "status": "active",
        "short_description": "Demo dental/oral care product",
        "description": "Demonstration oral-care gel for interview/demo catalogs.",
        "image_url": "",
        "purchase_url": "",
        "tags": "demo dental",
    },
)

_DEMO_PRICING: tuple[dict[str, Any], ...] = (
    {"product_id": "SF001", "list_price_rmb": 168, "package_units": 7, "unit_label": "pack"},
    {"product_id": "SF002", "list_price_rmb": 148, "package_units": 7, "unit_label": "pack"},
    {"product_id": "TR011", "list_price_rmb": 89, "package_units": 30, "unit_label": "bag"},
    {"product_id": "TR001", "list_price_rmb": 72, "package_units": 28, "unit_label": "bag"},
    {"product_id": "TR003", "list_price_rmb": 128, "package_units": 30, "unit_label": "bottle"},
    {"product_id": "TR007", "list_price_rmb": 96, "package_units": 60, "unit_label": "bottle"},
    {"product_id": "TR008", "list_price_rmb": 108, "package_units": 30, "unit_label": "bottle"},
    {"product_id": "JB001", "list_price_rmb": 138, "package_units": 60, "unit_label": "bottle"},
    {"product_id": "HY001", "list_price_rmb": 58, "package_units": 12, "unit_label": "carton"},
    {"product_id": "HG001", "list_price_rmb": 42, "package_units": 80, "unit_label": "pack"},
    {"product_id": "SK001", "list_price_rmb": 76, "package_units": 1, "unit_label": "bottle"},
    {"product_id": "DN001", "list_price_rmb": 64, "package_units": 1, "unit_label": "tube"},
)

_DEMO_FEEDING: tuple[dict[str, Any], ...] = (
    {"product_id": "SF001", "weight_min_kg": 20, "weight_max_kg": 45, "daily_amount": 1, "daily_unit": "bowl"},
    {"product_id": "SF002", "weight_min_kg": 20, "weight_max_kg": 45, "daily_amount": 1, "daily_unit": "bowl"},
    {"product_id": "TR011", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "chew"},
    {"product_id": "TR001", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "chew"},
    {"product_id": "TR003", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "serving"},
    {"product_id": "TR007", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "capsule"},
    {"product_id": "TR008", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "capsule"},
    {"product_id": "JB001", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "tablet"},
    {"product_id": "HY001", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "serving"},
    {"product_id": "HG001", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "wipe"},
    {"product_id": "SK001", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "application"},
    {"product_id": "DN001", "weight_min_kg": 0, "weight_max_kg": 80, "daily_amount": 1, "daily_unit": "application"},
)

# Declared-label composition only. Not scientific evidence.
_DEMO_COMPONENTS: tuple[dict[str, str], ...] = (
    {"product_id": "SF001", "component_type": "macro", "component_name": "protein", "value": "12", "unit": "%", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "SF001", "component_type": "active_ingredient", "component_name": "Omega-3", "value": "200", "unit": "mg", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "SF002", "component_type": "macro", "component_name": "protein", "value": "11", "unit": "%", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "TR011", "component_type": "active_ingredient", "component_name": "Glucosamine", "value": "500", "unit": "mg", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "TR003", "component_type": "active_ingredient", "component_name": "Omega-3", "value": "300", "unit": "mg", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "JB001", "component_type": "active_ingredient", "component_name": "Glucosamine", "value": "400", "unit": "mg", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "TR008", "component_type": "active_ingredient", "component_name": "Probiotics", "value": "1", "unit": "billion CFU", "evidence_level": "declared_label", "notes": "demo declared label"},
    {"product_id": "TR007", "component_type": "active_ingredient", "component_name": "Omega-3", "value": "120", "unit": "mg", "evidence_level": "declared_label", "notes": "demo declared label"},
)

_DEMO_FUNCTIONS: tuple[dict[str, str], ...] = (
    {"product_id": "SF001", "function": "daily nutrition staple", "confidence": "medium"},
    {"product_id": "SF002", "function": "daily nutrition staple", "confidence": "medium"},
    {"product_id": "TR011", "function": "joint mobility support", "confidence": "medium"},
    {"product_id": "TR001", "function": "dental oral care", "confidence": "medium"},
    {"product_id": "TR003", "function": "skin coat care", "confidence": "medium"},
    {"product_id": "TR007", "function": "daily nutrition supplement", "confidence": "medium"},
    {"product_id": "TR008", "function": "digestive gut support", "confidence": "medium"},
    {"product_id": "JB001", "function": "joint cartilage support", "confidence": "medium"},
    {"product_id": "HY001", "function": "hydration drink", "confidence": "medium"},
    {"product_id": "HG001", "function": "hygiene care", "confidence": "low"},
    {"product_id": "SK001", "function": "coat care", "confidence": "medium"},
    {"product_id": "DN001", "function": "dental oral care", "confidence": "medium"},
)


def demo_mode_enabled() -> bool:
    return str(os.getenv(DEMO_ENV, "")).strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def demo_table_frames() -> dict[str, pd.DataFrame]:
    return {
        "products": pd.DataFrame(list(_DEMO_PRODUCTS)),
        "product_pricing": pd.DataFrame(list(_DEMO_PRICING)),
        "product_components": pd.DataFrame(list(_DEMO_COMPONENTS)),
        "product_feeding_rules": pd.DataFrame(list(_DEMO_FEEDING)),
        "product_functions": pd.DataFrame(list(_DEMO_FUNCTIONS)),
    }


def demo_product_ids() -> set[str]:
    return {row["product_id"] for row in _DEMO_PRODUCTS}


def overlay_frame(name: str, base: pd.DataFrame) -> pd.DataFrame:
    if not demo_mode_enabled() or name not in DEMO_TABLES:
        return base
    demo = demo_table_frames().get(name)
    if demo is None or demo.empty:
        return base
    return demo.copy()
