"""Stage 1 & 2: biological trait identification and evolutionary analysis."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from app.agent.state import DogProfileInput, PipelineTraceEntry
from app.agent.utils import DataRepository, normalize_breed_name, resolve_breed_rows

logger = logging.getLogger(__name__)


def run_biological_stage(repo: DataRepository, profile: DogProfileInput) -> tuple[dict[str, Any], PipelineTraceEntry]:
    breeds_df = repo.breeds()
    breed_names = [profile.primary_breed]
    if profile.secondary_breed:
        breed_names.append(profile.secondary_breed)

    resolved = resolve_breed_rows(breeds_df, [normalize_breed_name(b) for b in breed_names])
    trait_purposes = repo.trait_purposes()
    environmental = repo.environmental_matrices()

    biology_records = []
    if not resolved.empty:
        for _, row in resolved.iterrows():
            biology_records.append({
                "breed": row.get("breed"),
                "size": row.get("size"),
                "body_type": row.get("body_type"),
                "coat_type": row.get("coat_type"),
                "energy": row.get("energy"),
                "weakness_group": row.get("weakness_group"),
                "skull_type": row.get("skull_type"),
                "climate": row.get("climate"),
                "lifespan": row.get("lifespan"),
                "function_group": row.get("function_group"),
            })

    env_hits = pd.DataFrame()
    if not environmental.empty and biology_records:
        trait_values = set()
        for rec in biology_records:
            trait_values.update(v for v in rec.values() if isinstance(v, str))
        env_hits = environmental[environmental["trait"].isin(trait_values)].copy()

    payload = {
        "resolved_breeds": biology_records,
        "breed_split_pct": profile.breed_split_pct,
        "activity_level": profile.activity_level,
        "current_environment": profile.current_environment,
        "trait_purposes": trait_purposes.to_dict(orient="records"),
        "environmental_compatibility": env_hits.to_dict(orient="records"),
    }

    trace = PipelineTraceEntry(
        stage="biology",
        message="Resolved biological traits and evolutionary compatibility matrices",
        record_count=len(biology_records),
        metadata={"breeds": breed_names},
    )
    logger.info("[Stage 1-2] biology resolved %s breed profile(s)", len(biology_records))
    return payload, trace
