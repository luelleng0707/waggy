"""Stage 5: condition-to-nutrient clinical conversion."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from app.agent.state import DogProfileInput, PipelineTraceEntry
from app.agent.utils import DataRepository, canonical_key

logger = logging.getLogger(__name__)


def run_nutrition_stage(
    repo: DataRepository,
    profile: DogProfileInput,
    epidemiology: dict[str, Any],
) -> tuple[dict[str, Any], PipelineTraceEntry]:
    ingredients_df = repo.condition_ingredients()
    priorities = epidemiology.get("priority_conditions", [])
    if not priorities or ingredients_df.empty:
        payload = {"nutrient_targets": [], "orphan_conditions": [p.get("condition") for p in priorities]}
        trace = PipelineTraceEntry(stage="nutrition", message="No nutrient mappings resolved", record_count=0)
        logger.info("[Stage 5] nutrition produced 0 targets")
        return payload, trace

    priority_df = pd.DataFrame(priorities)
    merged = priority_df.merge(
        ingredients_df,
        left_on="condition",
        right_on="condition",
        how="inner",
    )
    if merged.empty:
        payload = {
            "nutrient_targets": [],
            "orphan_conditions": priority_df["condition"].tolist(),
        }
        trace = PipelineTraceEntry(
            stage="nutrition",
            message="No CONDITION_INGREDIENTS joins for ranked priorities",
            record_count=0,
            metadata={"orphans": payload["orphan_conditions"][:5]},
        )
        logger.info("[Stage 5] nutrition orphans=%s", len(payload["orphan_conditions"]))
        return payload, trace

    dose_col = "recommended_daily_dose" if "recommended_daily_dose" in merged.columns else "target_daily_dose"
    unit_col = "dose_unit" if "dose_unit" in merged.columns else "unit"

    targets = []
    for _, row in merged.iterrows():
        dose = row.get(dose_col, 0)
        unit = row.get(unit_col, "")
        try:
            dose_val = float(dose)
        except (TypeError, ValueError):
            dose_val = 0.0
        targets.append({
            "condition": row["condition"],
            "ingredient_name": row["ingredient_name"],
            "ingredient_key": canonical_key(row["ingredient_name"]),
            "target_daily_dose": dose_val,
            "dose_unit": unit,
            "weighted_priority_score": float(row.get("weighted_priority_score", row.get("prevalence", 0))),
            "source_name": row.get("source_name"),
            "source_url": row.get("source_url"),
        })

    targets_df = pd.DataFrame(targets)
    if not targets_df.empty:
        targets_df = targets_df.sort_values(
            ["weighted_priority_score", "target_daily_dose"],
            ascending=[False, False],
        )
        targets_df = targets_df.drop_duplicates(subset=["ingredient_key"], keep="first")

    mapped_conditions = set(targets_df["condition"].tolist()) if not targets_df.empty else set()
    orphan_conditions = [
        c for c in priority_df["condition"].tolist() if c not in mapped_conditions
    ]

    payload = {
        "nutrient_targets": targets_df.to_dict(orient="records"),
        "orphan_conditions": orphan_conditions,
    }
    trace = PipelineTraceEntry(
        stage="nutrition",
        message="Mapped ranked conditions to active nutrient targets",
        record_count=len(targets_df),
        metadata={"orphan_count": len(orphan_conditions)},
    )
    logger.info("[Stage 5] nutrition targets=%s orphans=%s", len(targets_df), len(orphan_conditions))
    return payload, trace
