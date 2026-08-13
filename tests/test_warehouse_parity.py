"""Phase Σ — canonical warehouse parity (entity layers + formula projection)."""

from __future__ import annotations

import asyncio
import itertools
import os
from typing import Any

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.core.paths import clinical_root_str, WAREHOUSE
from app.data.repository import DataPlatform, DataRepository
from app.data.warehouse.parity import deep_diff, stable_hash
from app.data.warehouse.units import UnitNormalizer
from app.data.warehouse.parameters import ParameterRepository
from app.data.warehouse.ingredients import IngredientRepository
from warehouse.repository.scientific import ScientificRepository


@pytest.fixture(scope="module")
def platform() -> DataPlatform:
    return DataPlatform(clinical_root_str(), strict=True)


def test_canonical_root_is_warehouse():
    root = clinical_root_str().replace("\\", "/")
    assert root.rstrip("/").endswith("/warehouse") or root.endswith("warehouse")


def test_formula_tables_load(platform: DataPlatform):
    assert "breeds" in platform._tables
    assert "breed_conditions" in platform._tables
    assert len(platform._tables) >= 40


def test_scientific_entities():
    sci = ScientificRepository(WAREHOUSE)
    assert len(sci.breeds()) >= 40
    assert len(sci.conditions()) >= 10
    assert len(sci.traits()) >= 20
    assert sci.get_breed("Golden Retriever") is not None
    rels = sci.get_condition_relationship(
        breed_id=sci.get_breed("Golden Retriever").breed_id  # type: ignore[union-attr]
    )
    assert isinstance(rels, list)


def test_unit_normalizer_identity_safe():
    n = UnitNormalizer()
    c = n.normalize(1, "g")
    assert c.unit == "mg"
    assert c.amount == 1000.0
    u = n.normalize(5, "mystery")
    assert u.unit == "mystery"
    assert u.amount == 5.0


def test_parameter_repository_mirrors_constants():
    p = ParameterRepository()
    assert p.get("risk_interaction", "INTERACTION_MIN") == 0.8
    assert p.get("risk_interaction", "INTERACTION_MAX") == 1.2
    assert "coverage" in p.group("score_weights")


def test_ingredient_repository_joins(platform: DataPlatform):
    repo = IngredientRepository(platform)
    rows = platform.condition_ingredients()
    if rows.empty:
        pytest.skip("no condition ingredients")
    name = str(rows.iloc[0].get("ingredient_name") or rows.iloc[0].get("ingredient") or "")
    if not name:
        pytest.skip("no ingredient name")
    rec = repo.get(name)
    assert rec is not None


def test_repository_entity_api(platform: DataPlatform):
    repo = DataRepository(clinical_root_str(), platform=platform)
    breed = repo.get_breed("Labrador Retriever")
    assert breed is not None
    assert breed.breed_id.startswith("brd_")


def _profiles_from_breeds(n: int) -> list[DogProfileInput]:
    breeds = DataPlatform(clinical_root_str(), strict=True).breeds
    names = [str(r["breed"]) for _, r in breeds.iterrows() if str(r.get("breed") or "").strip()]
    out: list[DogProfileInput] = []
    for i, name in enumerate(itertools.islice(names, n)):
        out.append(
            DogProfileInput(
                name=f"Dog{i}",
                primary_breed=name,
                age_years=3.0 + (i % 7),
                weight_kg=8.0 + (i % 30),
                current_environment="Shanghai Summer",
                activity_level="Moderate",
            )
        )
    return out


def _golden_profiles() -> list[DogProfileInput]:
    n = int(os.environ.get("WAREHOUSE_PARITY_N", "5"))
    return _profiles_from_breeds(n)


def _clinical_fingerprint(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "healthInsights": report.get("healthInsights"),
        "wellnessPackages": report.get("wellnessPackages"),
        "nutritionalTargets": report.get("nutritionalTargets"),
        "wellness_score": report.get("wellness_score") or report.get("wellnessScore"),
        "algorithm_version": report.get("algorithm_version") or report.get("version"),
    }


@pytest.mark.asyncio
async def test_engine_hash_stable_one_dog():
    profile = DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=4.3,
        weight_kg=30.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )
    a = await PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(profile)
    b = await PPIEWellnessAgent(data_dir=clinical_root_str()).generate_reproducible_report(profile)
    assert stable_hash(_clinical_fingerprint(a)) == stable_hash(_clinical_fingerprint(b))


@pytest.mark.asyncio
async def test_engine_parity_golden_dogs():
    agent = PPIEWellnessAgent(data_dir=clinical_root_str())
    failures: list[dict[str, Any]] = []
    for profile in _golden_profiles():
        left = await agent.generate_reproducible_report(profile)
        right = await agent.generate_reproducible_report(profile)
        fp_l = _clinical_fingerprint(left)
        fp_r = _clinical_fingerprint(right)
        if stable_hash(fp_l) != stable_hash(fp_r):
            failures.append(
                {
                    "breed": profile.primary_breed,
                    "diffs": deep_diff(fp_l, fp_r)[:10],
                }
            )
    assert not failures, failures[:3]
