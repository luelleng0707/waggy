"""Stage 3 & 4: epidemiology pools, prevalence accrual, and interaction multipliers."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from app.agent.state import DogProfileInput, PipelineTraceEntry
from app.agent.utils import DataRepository, canonical_key, normalize_breed_name

logger = logging.getLogger(__name__)

TRAIT_COLUMNS = [
    ("size", "size"),
    ("body_type", "body_type"),
    ("coat_type", "coat_type"),
    ("energy", "energy"),
    ("weakness_group", "weakness_group"),
    ("skull_type", "skull_type"),
    ("climate", "climate"),
    ("lifespan", "lifespan"),
    ("function_group", "function_group"),
]


def compute_epidemiology_risk(
    profile: DogProfileInput,
    breeds_df: pd.DataFrame,
    conditions_df: pd.DataFrame,
) -> pd.DataFrame:
    """Multi-breed additive union (OR) over breed-specific epidemiology rows."""
    target_breeds = [normalize_breed_name(profile.primary_breed)]
    if profile.secondary_breed:
        target_breeds.append(normalize_breed_name(profile.secondary_breed))

    if conditions_df.empty:
        return pd.DataFrame(columns=["condition", "prevalence", "sample_size", "confidence"])

    matched = conditions_df[conditions_df["breed"].isin(target_breeds)].copy()
    if matched.empty:
        return pd.DataFrame(columns=["condition", "prevalence", "sample_size", "confidence"])

    matched["prevalence"] = pd.to_numeric(matched.get("prevalence"), errors="coerce").fillna(0.0)
    if "sample_size" in matched.columns:
        matched["sample_size"] = pd.to_numeric(matched["sample_size"], errors="coerce").fillna(0.0)
    else:
        matched["sample_size"] = 0.0

    if "confidence_level" in matched.columns:
        confidence_col = "confidence_level"
    elif "confidence" in matched.columns:
        confidence_col = "confidence"
    else:
        matched["confidence"] = ""
        confidence_col = "confidence"
    grouped = matched.groupby("condition", as_index=False).agg({
        "prevalence": "sum",
        "sample_size": "sum",
        confidence_col: "first",
    })
    grouped["prevalence"] = grouped["prevalence"].clip(upper=1.0)
    grouped = grouped.rename(columns={confidence_col: "confidence"})
    return grouped.sort_values("prevalence", ascending=False)


def _trait_prevalence_for_breeds(repo: DataRepository, biology: dict[str, Any]) -> pd.DataFrame:
    trait_tables = repo.trait_condition_tables()
    if trait_tables.empty or not biology.get("resolved_breeds"):
        return pd.DataFrame(columns=["condition", "prevalence"])

    trait_values: set[str] = set()
    for breed in biology["resolved_breeds"]:
        for col, _ in TRAIT_COLUMNS:
            val = breed.get(col)
            if val:
                trait_values.add(str(val))

    hits = trait_tables[trait_tables["trait_value"].isin(trait_values)].copy()
    if hits.empty:
        return pd.DataFrame(columns=["condition", "prevalence"])

    grouped = hits.groupby("condition", as_index=False).agg({"prevalence": "sum"})
    grouped["prevalence"] = grouped["prevalence"].clip(upper=1.0)
    return grouped


def _apply_interaction_multipliers(
    risks_df: pd.DataFrame,
    repo: DataRepository,
    biology: dict[str, Any],
) -> pd.DataFrame:
    if risks_df.empty:
        return risks_df

    interactions = repo.trait_interactions()
    if interactions.empty:
        risks_df["multiplier_effect"] = 1.0
        risks_df["weighted_priority_score"] = risks_df["prevalence"]
        return risks_df

    trait_values: set[str] = set()
    for breed in biology.get("resolved_breeds", []):
        trait_values.update(str(v) for v in breed.values() if isinstance(v, str))

    out = risks_df.copy()
    multipliers = []
    for _, row in out.iterrows():
        condition = row["condition"]
        matches = interactions[
            (interactions["condition"] == condition)
            & (interactions["trait_a"].isin(trait_values))
            & (interactions["trait_b"].isin(trait_values))
        ]
        factor = 1.0
        for _, m in matches.iterrows():
            if str(m.get("interaction", "")).lower() == "neutral":
                continue
            factor *= float(m.get("factor", 1.0))
        factor = max(0.8, min(1.2, factor))
        multipliers.append(factor)

    out["multiplier_effect"] = multipliers
    out["weighted_priority_score"] = (out["prevalence"] * out["multiplier_effect"]).clip(upper=1.0)
    return out.sort_values("weighted_priority_score", ascending=False)


def _union_breed_and_trait_risks(breed_risks: pd.DataFrame, trait_risks: pd.DataFrame) -> pd.DataFrame:
    if breed_risks.empty and trait_risks.empty:
        return pd.DataFrame(columns=["condition", "prevalence", "source"])

    breed_part = breed_risks.copy() if not breed_risks.empty else pd.DataFrame(columns=["condition", "prevalence"])
    trait_part = trait_risks.copy() if not trait_risks.empty else pd.DataFrame(columns=["condition", "prevalence"])

    breed_part["source"] = "breed_epidemiology"
    trait_part["source"] = "trait_epidemiology"

    merged = pd.concat([breed_part, trait_part], ignore_index=True)
    grouped = merged.groupby("condition", as_index=False).agg({"prevalence": "sum", "source": "first"})
    grouped["prevalence"] = grouped["prevalence"].clip(upper=1.0)
    return grouped


def run_epidemiology_stage(
    repo: DataRepository,
    profile: DogProfileInput,
    biology: dict[str, Any],
) -> tuple[dict[str, Any], PipelineTraceEntry]:
    breed_conditions = repo.breed_conditions()
    target_breeds = [normalize_breed_name(profile.primary_breed)]
    if profile.secondary_breed:
        target_breeds.append(normalize_breed_name(profile.secondary_breed))
    breed_evidence_detail = pd.DataFrame()
    if not breed_conditions.empty:
        breed_evidence_detail = breed_conditions[breed_conditions["breed"].isin(target_breeds)].copy()
        if "prevalence" in breed_evidence_detail.columns:
            breed_evidence_detail["prevalence_pct"] = (
                pd.to_numeric(breed_evidence_detail["prevalence"], errors="coerce").fillna(0) * 100
            ).round(1)

    breed_risks = compute_epidemiology_risk(profile, repo.breeds(), breed_conditions)
    trait_risks = _trait_prevalence_for_breeds(repo, biology)
    union_risks = _union_breed_and_trait_risks(breed_risks, trait_risks)
    weighted = _apply_interaction_multipliers(union_risks, repo, biology)

    mixed_matrix = repo.mixed_breed_matrix()
    mixed_hits = pd.DataFrame()
    if profile.secondary_breed and not mixed_matrix.empty:
        b1 = normalize_breed_name(profile.primary_breed)
        b2 = normalize_breed_name(profile.secondary_breed)
        mixed_hits = mixed_matrix[
            ((mixed_matrix["breed_a"] == b1) & (mixed_matrix["breed_b"] == b2))
            | ((mixed_matrix["breed_a"] == b2) & (mixed_matrix["breed_b"] == b1))
        ]

    payload = {
        "breed_risks": breed_risks.to_dict(orient="records"),
        "breed_evidence_detail": breed_evidence_detail.to_dict(orient="records"),
        "trait_risks": trait_risks.to_dict(orient="records"),
        "priority_conditions": weighted.to_dict(orient="records"),
        "mixed_breed_adjustments": mixed_hits.to_dict(orient="records"),
    }

    trace = PipelineTraceEntry(
        stage="epidemiology",
        message="Computed additive union epidemiology with interaction multipliers",
        record_count=len(weighted),
        metadata={"top_condition": weighted.iloc[0]["condition"] if not weighted.empty else None},
    )
    logger.info("[Stage 3-4] epidemiology ranked %s conditions", len(weighted))
    return payload, trace
