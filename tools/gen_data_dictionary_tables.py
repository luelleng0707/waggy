"""Generate column dictionary sections from live CSVs (planning helper)."""
from __future__ import annotations

import csv
from pathlib import Path

OWN = {
    "breed": "S",
    "size": "S",
    "body_type": "S",
    "coat_type": "S",
    "energy": "S",
    "weakness_group": "S",
    "skull_type": "S",
    "climate": "S",
    "lifespan": "S",
    "function_group": "S",
    "alias": "X",
    "canonical_breed": "X",
    "canonical_key": "X",
    "alias_key": "X",
    "condition": "C",
    "prevalence": "S",
    "factor": "S",
    "reduction_factor": "S",
    "source_name": "R",
    "source_quote": "R",
    "source_url": "R",
    "year": "R",
    "sample_population": "R",
    "sample_size": "R",
    "confidence_level": "R",
    "evidence_level": "R",
    "evidence_id": "R",
    "source_csv": "M",
    "card_title": "U",
    "label": "U",
    "priority_rank": "A",
    "confidence": "A",
    "key": "A",
    "sort_order": "U",
    "display_order": "U",
    "featured": "U",
    "tags": "U",
    "inventory_status": "P",
    "rating": "P",
    "review_count": "P",
    "image_url": "P",
    "purchase_url": "P",
    "description": "U",
    "short_description": "U",
    "list_price_rmb": "P",
    "product_id": "P",
    "brand": "P",
    "category": "P",
    "subcategory": "P",
    "product_name": "P",
    "status": "P",
    "component_type": "P",
    "component_name": "P",
    "value": "P",
    "unit": "S",
    "notes": "P",
    "daily_amount": "P",
    "daily_unit": "P",
    "min_weight_kg": "P",
    "max_weight_kg": "P",
    "package_units": "P",
    "unit_label": "P",
    "ingredient_name": "S",
    "nutrient_name": "S",
    "ingredient": "S",
    "canonical_ingredient": "S",
    "recommended_daily_dose": "S",
    "target_dose": "S",
    "dose_unit": "S",
    "target_unit": "S",
    "amount_per_100g": "S",
    "is_estimated": "S",
    "parent": "S",
    "parent_key": "S",
    "property_tags": "S",
    "mechanism_summary": "S",
    "food_source": "S",
    "trait_category": "S",
    "trait_value": "S",
    "trait": "D",
    "trait_a": "S",
    "trait_b": "S",
    "interaction": "S",
    "reason": "C",
    "source": "R",
    "breed_a": "S",
    "breed_b": "S",
    "biological_purpose": "C",
    "advantage_summary": "C",
    "explanation": "C",
    "related_conditions": "D",
    "management_note": "C",
    "management_advice": "C",
    "compatibility_score": "A",
    "climate_context": "S",
    "dimension": "S",
    "risk_delta": "A",
    "mechanism_note": "C",
    "age_stage": "C",
    "trait_or_breed": "C",
    "risk_level": "C",
    "monitoring": "C",
    "prevention": "C",
    "activity_name": "C",
    "frequency": "C",
    "duration_minutes": "C",
    "daily_km": "C",
    "weekly_km": "C",
    "walk_morning_min": "C",
    "walk_evening_min": "C",
    "mental_enrichment": "C",
    "swimming": "C",
    "fetch": "C",
    "training": "C",
    "recovery_note": "C",
    "observation_key": "C",
    "normal_criteria": "C",
    "monitor_criteria": "C",
    "attention_criteria": "C",
    "severity_scale": "C",
    "recommendation_template": "U",
    "domain": "C",
    "nutrient_or_activity": "C",
    "mechanism": "S",
    "supports_joint": "S",
    "supports_skin": "S",
    "supports_gut": "S",
    "anti_inflammatory": "S",
    "evidence_type": "R",
    "source_product_id": "P",
    "amount_per_serving": "P",
    "tier_id": "P",
    "title": "U",
    "yearly_discount_factor": "A",
    "staple_product_id": "P",
    "function": "P",
    "bioavailability_notes": "S",
    "amount_per_100g": "S",
}

OWN_NAME = {
    "S": "Scientific",
    "C": "Clinical",
    "P": "Product",
    "R": "Reference",
    "X": "Parser",
    "A": "Algorithm",
    "D": "Derived",
    "U": "Display",
    "M": "Metadata",
    "?": "Review",
}

MOVE_COLS = {
    "alias",
    "canonical_key",
    "alias_key",
    "canonical_breed",
    "source_csv",
    "card_title",
    "label",
    "recommendation_template",
    "key",
    "trait",
}


def classify(col: str) -> str:
    if col in OWN:
        return OWN[col]
    if col.endswith("_url") or col.startswith("source_"):
        return "R"
    if "price" in col or col.endswith("_pct"):
        return "P"
    return "?"


def main() -> None:
    lines: list[str] = []
    for p in sorted(Path("data").rglob("*.csv")):
        with p.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames or []
            rows = list(reader)
        lines.append(f"\n### `{p.as_posix()}`\n\n")
        lines.append(f"Rows: **{len(rows)}** · Columns: **{len(cols)}**\n\n")
        lines.append(
            "| Column | Type | Example | Ownership | Nullable | Intern edit? | Disposition |\n"
            "|--------|------|---------|-----------|----------|--------------|-------------|\n"
        )
        for c in cols:
            ex = "—"
            for row in rows[:10]:
                v = (row.get(c) or "").strip()
                if v:
                    ex = v.replace("|", "/").replace("\n", " ")[:55]
                    break
            own = classify(c)
            if c in MOVE_COLS or own in ("X", "M"):
                disp = "MOVE→Python / DELETE"
                intern = "No"
            elif own in ("A", "U") and c in (
                "priority_rank",
                "confidence",
                "yearly_discount_factor",
                "compatibility_score",
                "risk_delta",
                "sort_order",
                "display_order",
                "featured",
            ):
                disp = "REVIEW (algo/display)"
                intern = "Careful"
            elif own == "D":
                disp = "DERIVE or DROP"
                intern = "No"
            else:
                disp = "KEEP (normalize name)"
                intern = "Yes" if own in ("S", "C", "P", "R") else "Review"
            typ = "str"
            if any(x in c for x in ("pct", "dose", "amount", "price", "factor", "km", "min", "rank", "order", "count", "days", "weight", "value", "delta", "score")):
                typ = "number|str"
            if c.startswith("supports_") or c in ("is_estimated", "featured"):
                typ = "bool|flag"
            nullable = "Yes" if any(not (row.get(c) or "").strip() for row in rows[:20]) or not rows else "Often"
            lines.append(
                f"| `{c}` | {typ} | {ex} | {OWN_NAME.get(own, own)} | {nullable} | {intern} | {disp} |\n"
            )

    Path("docs/_generated_column_tables.md").write_text("".join(lines), encoding="utf-8")
    print("wrote docs/_generated_column_tables.md")


if __name__ == "__main__":
    main()
