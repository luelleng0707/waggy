"""Phase 2 warehouse adapter parity — bit-identical vs legacy DataPlatform."""

from __future__ import annotations

import asyncio
import itertools
from typing import Any

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.data.repository import DataPlatform, DataRepository
from app.data.warehouse.materialize import materialize_warehouse
from app.data.warehouse.parity import deep_diff, stable_hash
from app.data.warehouse.platform import WarehouseDataPlatform
from app.data.warehouse.repository import WarehouseRepository
from app.data.warehouse.units import UnitNormalizer
from app.data.warehouse.parameters import ParameterRepository
from app.data.warehouse.ingredients import IngredientRepository
from app.data.warehouse.traits import TraitConditionAdapter


@pytest.fixture(scope="module")
def legacy_platform() -> DataPlatform:
    return DataPlatform("data", strict=True)


@pytest.fixture(scope="module")
def warehouse_platform(legacy_platform: DataPlatform) -> WarehouseDataPlatform:
    return WarehouseDataPlatform("data", warehouse_root="warehouse", strict=True, persist=True)


def test_table_roundtrip_parity(legacy_platform: DataPlatform, warehouse_platform: WarehouseDataPlatform):
    report = warehouse_platform.parity_report
    assert report["ok"], report
    for name, expected in legacy_platform._tables.items():
        got = warehouse_platform._tables[name]
        assert list(got.columns) == list(expected.columns), name
        assert len(got) == len(expected), name
        assert got.fillna("").astype(str).reset_index(drop=True).equals(
            expected.fillna("").astype(str).reset_index(drop=True)
        ), name


def test_trait_adapter_collapses_nine_tables(legacy_platform: DataPlatform):
    wh = materialize_warehouse(legacy_platform)
    trait = wh["trait_condition_risk"]
    assert "trait_category" in trait.columns
    cats = set(trait["trait_category"].unique())
    assert "body_type" in cats
    assert "size" in cats
    assert len(cats) == 9
    expanded = TraitConditionAdapter().expand(trait)
    assert len(expanded) == 9


def test_unit_normalizer_identity_safe():
    n = UnitNormalizer()
    c = n.normalize(1, "g")
    assert c.unit == "mg"
    assert c.amount == 1000.0
    # Unknown units pass through — formulas still see originals via legacy layer
    u = n.normalize(5, "mystery")
    assert u.unit == "mystery"
    assert u.amount == 5.0


def test_parameter_repository_mirrors_constants():
    p = ParameterRepository()
    assert p.get("risk_interaction", "INTERACTION_MIN") == 0.8
    assert p.get("risk_interaction", "INTERACTION_MAX") == 1.2
    assert "coverage" in p.group("score_weights")


def test_ingredient_repository_joins(legacy_platform: DataPlatform):
    repo = IngredientRepository(legacy_platform)
    # Pick any ingredient from condition ingredients if present
    ci = legacy_platform.condition_ingredients()
    if ci.empty:
        pytest.skip("no condition ingredients")
    name = str(ci.iloc[0]["ingredient_name"])
    rec = repo.get(name)
    assert rec is not None
    assert rec.ingredient_name


def _profiles_from_breeds(limit: int = 100) -> list[DogProfileInput]:
    breeds = DataPlatform("data", strict=True).breeds
    names = [str(r["breed"]) for _, r in breeds.iterrows() if str(r.get("breed") or "").strip()]
    ages = [0.5, 1.0, 2.0, 4.0, 7.0, 10.0, 12.0]
    weights = [4.0, 8.0, 15.0, 25.0, 35.0, 45.0]
    envs = ["Shanghai Summer", "Indoor Apartment", "Rural"]
    activities = ["Low", "Moderate", "High"]
    out: list[DogProfileInput] = []
    for i, (breed, age, w, env, act) in enumerate(
        itertools.product(names, ages, weights, envs[:1], activities[:1])
    ):
        out.append(
            DogProfileInput(
                name=f"Dog{i}",
                primary_breed=breed,
                age_years=float(age),
                weight_kg=float(w),
                current_environment=env,
                activity_level=act,
            )
        )
        if len(out) >= limit:
            break
    # Ensure we hit mixed-breed path a few times
    if names:
        out.append(
            DogProfileInput(
                name="MixedParity",
                primary_breed=names[0],
                secondary_breed=names[min(1, len(names) - 1)],
                breed_split_pct=50.0,
                age_years=5.0,
                weight_kg=28.0,
                current_environment="Shanghai Summer",
                activity_level="High",
            )
        )
    return out[:limit]


def _golden_profiles() -> list[DogProfileInput]:
    """Known parity fixtures (fast suite)."""
    return [
        DogProfileInput(name="Dolly", primary_breed="Golden Retriever", secondary_breed="Labrador Retriever", breed_split_pct=50.0, age_years=4.3, weight_kg=30.0, current_environment="Shanghai Summer", activity_level="High"),
        DogProfileInput(name="Chi", primary_breed="Chihuahua", age_years=7.0, weight_kg=2.5, current_environment="Indoor Apartment", activity_level="Low"),
        DogProfileInput(name="GSD", primary_breed="German Shepherd Dog", age_years=8.0, weight_kg=35.0, current_environment="Rural", activity_level="High"),
        DogProfileInput(name="Frenchie", primary_breed="French Bulldog", age_years=3.0, weight_kg=12.0, current_environment="Shanghai Summer", activity_level="Moderate"),
        DogProfileInput(name="BC", primary_breed="Border Collie", age_years=2.0, weight_kg=18.0, current_environment="Rural", activity_level="High"),
        DogProfileInput(name="Pyr", primary_breed="Great Pyrenees", age_years=5.0, weight_kg=45.0, current_environment="Rural", activity_level="Moderate"),
        DogProfileInput(name="SeniorLab", primary_breed="Labrador Retriever", age_years=11.0, weight_kg=32.0, current_environment="Indoor Apartment", activity_level="Low"),
        DogProfileInput(name="Puppy", primary_breed="Golden Retriever", age_years=0.4, weight_kg=8.0, current_environment="Shanghai Summer", activity_level="High"),
        DogProfileInput(name="OverLab", primary_breed="Labrador Retriever", age_years=6.0, weight_kg=42.0, current_environment="Indoor Apartment", activity_level="Low"),
        DogProfileInput(name="ChowMix", primary_breed="Chow Chow", secondary_breed="Mixed Breed", breed_split_pct=60.0, age_years=5.0, weight_kg=22.0, current_environment="Rural", activity_level="Moderate"),
    ]


@pytest.fixture(scope="module")
def parity_profiles() -> list[DogProfileInput]:
    import os

    n = int(os.environ.get("WAREHOUSE_PARITY_N", "100"))
    return _profiles_from_breeds(n)


def _clinical_fingerprint(report: dict[str, Any]) -> dict[str, Any]:
    """Focus on clinical outputs — ignore volatile UI chrome."""
    return {
        "healthInsights": report.get("healthInsights"),
        "wellnessPackages": report.get("wellnessPackages"),
        "nutritionalTargets": report.get("nutritionalTargets"),
        "wellness_score": report.get("wellness_score") or report.get("wellnessScore"),
        "algorithm_version": report.get("algorithm_version") or report.get("version"),
    }


@pytest.mark.asyncio
async def test_engine_hash_parity_one_dog():
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
    legacy = await PPIEWellnessAgent(data_dir="data", backend="legacy").generate_reproducible_report(profile)
    warehouse = await PPIEWellnessAgent(data_dir="data", backend="warehouse").generate_reproducible_report(profile)
    h1 = stable_hash(_clinical_fingerprint(legacy))
    h2 = stable_hash(_clinical_fingerprint(warehouse))
    assert h1 == h2, deep_diff(_clinical_fingerprint(legacy), _clinical_fingerprint(warehouse))[:20]


@pytest.mark.asyncio
async def test_engine_parity_golden_dogs():
    """Fast clinical parity across golden-like profiles + hash equality."""
    legacy_agent = PPIEWellnessAgent(data_dir="data", backend="legacy")
    wh_agent = PPIEWellnessAgent(data_dir="data", backend="warehouse")
    failures: list[dict[str, Any]] = []
    for profile in _golden_profiles():
        left = await legacy_agent.generate_reproducible_report(profile)
        right = await wh_agent.generate_reproducible_report(profile)
        fp_l = _clinical_fingerprint(left)
        fp_r = _clinical_fingerprint(right)
        if stable_hash(fp_l) != stable_hash(fp_r):
            failures.append(
                {
                    "breed": profile.primary_breed,
                    "diffs": deep_diff(fp_l, fp_r)[:10],
                }
            )
    assert not failures, failures


@pytest.mark.asyncio
async def test_core_formula_parity_100_dogs():
    """
    100 dogs through locked formula entrypoints (not full UI assemble).

    Proves adapters feed identical frames into compute_risks + map_ingredients
    + build_optimized_packages without changing those modules.
    """
    from app.agent.stages.health_risk import compute_risks
    from app.agent.ingredient_engine import map_ingredients
    from app.agent.package_optimizer import build_optimized_packages

    legacy_repo = DataRepository("data")
    from app.data.runtime import bootstrap

    bootstrap("data", strict=True)
    wh_repo = WarehouseRepository("data", warehouse_root="warehouse")

    failures: list[dict[str, Any]] = []
    for profile in _profiles_from_breeds(100):
        lr = compute_risks(legacy_repo, profile)
        wr = compute_risks(wh_repo, profile)
        # Strip execution ledgers timings if present
        def risk_fp(r: dict[str, Any]) -> Any:
            risks = []
            for row in r.get("risks") or []:
                risks.append(
                    {
                        "condition_name": row.get("condition_name") or row.get("condition_key"),
                        "risk_percent": row.get("risk_percent") or row.get("biological_risk_percent"),
                        "confidence_percent": row.get("confidence_percent"),
                    }
                )
            return risks

        if stable_hash(risk_fp(lr)) != stable_hash(risk_fp(wr)):
            failures.append({"stage": "risk", "breed": profile.primary_breed, "diffs": deep_diff(risk_fp(lr), risk_fp(wr))[:5]})
            continue

        li = map_ingredients(lr.get("risks") or [], float(profile.weight_kg or 10), legacy_repo)
        wi = map_ingredients(wr.get("risks") or [], float(profile.weight_kg or 10), wh_repo)

        def ing_fp(items: list) -> Any:
            out = []
            for it in items:
                out.append(
                    {
                        "ingredient_name": it.get("ingredient_name") or it.get("name"),
                        "daily": (it.get("dose") or {}).get("daily") if isinstance(it.get("dose"), dict) else it.get("daily"),
                        "unit": (it.get("dose") or {}).get("unit") if isinstance(it.get("dose"), dict) else it.get("unit"),
                    }
                )
            return out

        if stable_hash(ing_fp(li)) != stable_hash(ing_fp(wi)):
            failures.append({"stage": "ingredients", "breed": profile.primary_breed, "diffs": deep_diff(ing_fp(li), ing_fp(wi))[:5]})
            continue

        insights_l = [
            {"goal_id": r.get("goal_id"), "title": r.get("condition_name") or r.get("title")}
            for r in (lr.get("risks") or [])
        ]
        insights_w = [
            {"goal_id": r.get("goal_id"), "title": r.get("condition_name") or r.get("title")}
            for r in (wr.get("risks") or [])
        ]
        lp = build_optimized_packages(
            repo=legacy_repo,
            profile=profile,
            health_insights=insights_l,
            ingredients=li,
        )
        wp = build_optimized_packages(
            repo=wh_repo,
            profile=profile,
            health_insights=insights_w,
            ingredients=wi,
        )

        def pkg_fp(pkgs: list) -> Any:
            out = []
            for p in pkgs or []:
                if not isinstance(p, dict):
                    continue
                out.append(
                    {
                        "tier": p.get("tier") or p.get("tier_id"),
                        "coverage_score": p.get("coverage_score"),
                        "overall_score": p.get("overall_score"),
                        "monthly_cost": p.get("monthly_cost"),
                    }
                )
            return out

        if stable_hash(pkg_fp(lp)) != stable_hash(pkg_fp(wp)):
            failures.append(
                {
                    "stage": "packages",
                    "breed": profile.primary_breed,
                    "diffs": deep_diff(pkg_fp(lp), pkg_fp(wp))[:5],
                }
            )

    assert not failures, failures[:5]


@pytest.mark.asyncio
@pytest.mark.slow
async def test_engine_parity_suite_100_dogs_full_report(parity_profiles: list[DogProfileInput]):
    """Full 100-dog assemble suite (slow). Prefer test_core_formula_parity_100_dogs in CI."""
    legacy_agent = PPIEWellnessAgent(data_dir="data", backend="legacy")
    wh_agent = PPIEWellnessAgent(data_dir="data", backend="warehouse")
    failures: list[dict[str, Any]] = []
    for profile in parity_profiles:
        left = await legacy_agent.generate_reproducible_report(profile)
        right = await wh_agent.generate_reproducible_report(profile)
        fp_l = _clinical_fingerprint(left)
        fp_r = _clinical_fingerprint(right)
        if stable_hash(fp_l) != stable_hash(fp_r):
            failures.append(
                {
                    "breed": profile.primary_breed,
                    "age": profile.age_years,
                    "weight": profile.weight_kg,
                    "hash_left": stable_hash(fp_l),
                    "hash_right": stable_hash(fp_r),
                    "diffs": deep_diff(fp_l, fp_r)[:10],
                }
            )
    assert not failures, failures[:3]


def test_warehouse_repository_is_data_repository():
    repo = WarehouseRepository("data", warehouse_root="warehouse")
    assert isinstance(repo, DataRepository)
    assert not repo.breeds().empty
    assert not repo.trait_condition_tables().empty
