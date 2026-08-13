"""
Row-level scientific provenance columns (Phase 5B).

Apply to draft/staging science CSVs when editing evidence — never invent anonymous rows.
Production clinical `data/` CSVs remain the engine source of truth until a future migration
copies provenance-bearing warehouse tables into the live path.
"""

PROVENANCE_COLUMNS = [
    "created_by",
    "created_date",
    "modified_by",
    "modified_date",
    "review_status",  # draft | validation | scientific_review | approved | published | production
    "approval_date",
    "change_reason",
    "evidence_level",
]

REVIEW_STATUSES = [
    "draft",
    "validation",
    "scientific_review",
    "approved",
    "published",
    "production",
]

# Tables that should carry provenance when edited via the science pipeline
PROVENANCE_TARGET_TABLES = [
    "breed_condition_risk",
    "trait_condition_risk",
    "ingredient_evidence",
    "prevention_effectiveness",
    "papers",
    "product_composition",
]
