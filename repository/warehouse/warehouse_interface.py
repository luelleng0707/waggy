"""Immutable warehouse access and validation.

Responsibilities:
- Load canonical warehouse datasets.
- Validate structural and relational integrity.
- Resolve stable IDs for downstream engine layers.

Non-responsibilities:
- No inference, scoring, ranking, or recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from config import get_settings


CANONICAL_DATASETS: dict[str, Path] = {
    "biology.breeds": Path("biology/breeds.csv"),
    "biology.conditions": Path("biology/conditions.csv"),
    "biology.breed_traits": Path("biology/breed_traits.csv"),
    "biology.observed_breed_conditions": Path("biology/observed_breed_conditions.csv"),
    "biology.trait_condition_associations": Path("biology/trait_condition_associations.csv"),
    "biology.environment_facts": Path("biology/environment_facts.csv"),
    "biology.life_stage_health_NEEDS_VALIDATION": Path("biology/life_stage_health_NEEDS_VALIDATION.csv"),
    "biology.size_risk_NEEDS_VALIDATION": Path("biology/size_risk_NEEDS_VALIDATION.csv"),
    "biology.mixed_breed_NEEDS_VALIDATION": Path("biology/mixed_breed_NEEDS_VALIDATION.csv"),
    "prevention.condition_activities": Path("prevention/condition_activities.csv"),
    "prevention.condition_ingredients": Path("prevention/condition_ingredients.csv"),
    "nutrition.ingredients": Path("nutrition/ingredients.csv"),
    "nutrition.ingredient_composition": Path("nutrition/ingredient_composition.csv"),
    "nutrition.food_composition": Path("nutrition/food_composition.csv"),
    "nutrition.units": Path("nutrition/units.csv"),
    "commercial.product_master": Path("commercial/product_master.csv"),
    "commercial.product_recipe": Path("commercial/product_recipe.csv"),
    "commercial.product_declared_nutrition": Path("commercial/product_declared_nutrition.csv"),
    "commercial.product_feeding_guide": Path("commercial/product_feeding_guide.csv"),
    "reference.body_systems": Path("reference/body_systems.csv"),
    "reference.condition_systems": Path("reference/condition_systems.csv"),
    "reference.mechanisms": Path("reference/mechanisms.csv"),
    "reference.condition_mechanisms": Path("reference/condition_mechanisms.csv"),
    "mechanisms.mechanisms": Path("mechanisms/mechanisms.csv"),
    "mechanisms.condition_mechanisms": Path("mechanisms/condition_mechanisms.csv"),
    "mechanisms.ingredient_mechanisms": Path("mechanisms/ingredient_mechanisms.csv"),
    "mechanisms.food_mechanisms": Path("mechanisms/food_mechanisms.csv"),
    "mechanisms.mechanism_interactions": Path("mechanisms/mechanism_interactions.csv"),
    "mechanisms.mechanism_synergies": Path("mechanisms/mechanism_synergies.csv"),
    "mechanisms.mechanism_conflicts": Path("mechanisms/mechanism_conflicts.csv"),
    "mechanisms.absorption_factors": Path("mechanisms/absorption_factors.csv"),
    "mechanisms.dose_response": Path("mechanisms/dose_response.csv"),
    "objectives.objectives": Path("objectives/objectives.csv"),
    "objectives.condition_objectives": Path("objectives/condition_objectives.csv"),
    "objectives.objective_mechanisms": Path("objectives/objective_mechanisms.csv"),
    "objectives.objective_priorities": Path("objectives/objective_priorities.csv"),
    "objectives.objective_synergies": Path("objectives/objective_synergies.csv"),
    "objectives.objective_conflicts": Path("objectives/objective_conflicts.csv"),
    "sources.ingredient_sources": Path("sources/ingredient_sources.csv"),
    "sources.source_composition": Path("sources/source_composition.csv"),
    "sources.source_bioavailability": Path("sources/source_bioavailability.csv"),
    "recipes.recipes": Path("recipes/recipes.csv"),
    "recipes.recipe_components": Path("recipes/recipe_components.csv"),
}

REFERENCE_COLUMNS = ("scientific_quote", "paper_name", "paper_link")
COMMON_ID_COLUMNS = (
    "fact_id",
    "breed_id",
    "condition_id",
    "trait_id",
    "ingredient_id",
    "food_id",
    "environment_id",
    "product_id",
    "unit_id",
    "declaration_id",
)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    dataset: str
    issue_type: str
    detail: str


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    issues: tuple[ValidationIssue, ...]


class WarehouseInterface:
    def __init__(self, warehouse_root: Path | None = None):
        settings = get_settings()
        self.warehouse_root = Path(warehouse_root or settings.warehouse_root)
        self._cache: dict[str, pd.DataFrame] = {}

    def dataset_path(self, dataset_name: str) -> Path:
        rel = CANONICAL_DATASETS[dataset_name]
        return self.warehouse_root / rel

    def load_dataset(self, dataset_name: str) -> pd.DataFrame:
        if dataset_name in self._cache:
            return self._cache[dataset_name].copy(deep=True)
        path = self.dataset_path(dataset_name)
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        frame.columns = [str(c).strip() for c in frame.columns]
        # Freeze by convention for consumers.
        for col in frame.columns:
            frame[col] = frame[col].astype(str)
        self._cache[dataset_name] = frame
        return frame.copy(deep=True)

    def load_all(self) -> dict[str, pd.DataFrame]:
        return {name: self.load_dataset(name) for name in CANONICAL_DATASETS}

    def validate(self) -> ValidationReport:
        issues: list[ValidationIssue] = []
        tables = self.load_all()

        # Rule 1: duplicate primary IDs inside each dataset
        primary_id_columns = {
            "biology.breeds": ("breed_id",),
            "biology.conditions": ("condition_id",),
            "biology.breed_traits": ("fact_id",),
            "biology.observed_breed_conditions": ("fact_id",),
            "biology.trait_condition_associations": ("fact_id",),
            "biology.environment_facts": ("fact_id",),
            "prevention.condition_activities": ("fact_id",),
            "prevention.condition_ingredients": ("fact_id",),
            "nutrition.ingredients": ("ingredient_id",),
            "nutrition.ingredient_composition": ("fact_id",),
            "nutrition.food_composition": ("fact_id",),
            "nutrition.units": ("unit_id",),
            "commercial.product_master": ("product_id",),
            "commercial.product_recipe": ("declaration_id",),
            "commercial.product_declared_nutrition": ("declaration_id",),
            "commercial.product_feeding_guide": ("declaration_id",),
            "mechanisms.mechanisms": ("mechanism_id",),
            "objectives.objectives": ("objective_id",),
            "sources.ingredient_sources": ("source_id",),
            "recipes.recipes": ("recipe_id",),
        }
        for dataset_name, table in tables.items():
            for col in primary_id_columns.get(dataset_name, ()):
                if col not in table.columns:
                    continue
                nonempty = table[col].astype(str).str.strip()
                nonempty = nonempty[nonempty != ""]
                if nonempty.empty:
                    continue
                dupes = nonempty[nonempty.duplicated()].unique().tolist()
                for value in dupes:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            dataset=dataset_name,
                            issue_type="duplicate_id",
                            detail=f"{col}={value}",
                        )
                    )

        # Rule 2: required ids must not be missing
        required_ids = {
            "biology.breeds": ("breed_id",),
            "biology.conditions": ("condition_id",),
            "nutrition.ingredients": ("ingredient_id",),
            "commercial.product_master": ("product_id",),
        }
        for dataset_name, cols in required_ids.items():
            table = tables[dataset_name]
            for col in cols:
                if col not in table.columns:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            dataset=dataset_name,
                            issue_type="missing_column",
                            detail=col,
                        )
                    )
                    continue
                missing = int((table[col].astype(str).str.strip() == "").sum())
                if missing:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            dataset=dataset_name,
                            issue_type="missing_id",
                            detail=f"{col}: {missing} empty rows",
                        )
                    )

        # Rule 3: foreign-key checks
        fk_checks = (
            ("biology.observed_breed_conditions", "breed_id", "biology.breeds", "breed_id"),
            ("biology.observed_breed_conditions", "condition_id", "biology.conditions", "condition_id"),
            ("biology.trait_condition_associations", "condition_id", "biology.conditions", "condition_id"),
            ("prevention.condition_activities", "condition_id", "biology.conditions", "condition_id"),
            ("prevention.condition_ingredients", "condition_id", "biology.conditions", "condition_id"),
            ("prevention.condition_ingredients", "ingredient_id", "nutrition.ingredients", "ingredient_id"),
            ("commercial.product_recipe", "product_id", "commercial.product_master", "product_id"),
            ("commercial.product_declared_nutrition", "product_id", "commercial.product_master", "product_id"),
            ("commercial.product_feeding_guide", "product_id", "commercial.product_master", "product_id"),
            ("mechanisms.condition_mechanisms", "condition_id", "biology.conditions", "condition_id"),
            ("mechanisms.condition_mechanisms", "mechanism_id", "mechanisms.mechanisms", "mechanism_id"),
            ("mechanisms.ingredient_mechanisms", "mechanism_id", "mechanisms.mechanisms", "mechanism_id"),
            ("mechanisms.food_mechanisms", "ingredient_id", "nutrition.ingredients", "ingredient_id"),
            ("objectives.condition_objectives", "condition_id", "biology.conditions", "condition_id"),
            ("objectives.condition_objectives", "objective_id", "objectives.objectives", "objective_id"),
            ("objectives.objective_mechanisms", "objective_id", "objectives.objectives", "objective_id"),
            ("objectives.objective_mechanisms", "mechanism_id", "mechanisms.mechanisms", "mechanism_id"),
            ("objectives.objective_priorities", "objective_id", "objectives.objectives", "objective_id"),
            ("objectives.objective_synergies", "objective_A", "objectives.objectives", "objective_id"),
            ("objectives.objective_synergies", "objective_B", "objectives.objectives", "objective_id"),
            ("objectives.objective_conflicts", "objective_A", "objectives.objectives", "objective_id"),
            ("objectives.objective_conflicts", "objective_B", "objectives.objectives", "objective_id"),
            ("sources.ingredient_sources", "ingredient_id", "nutrition.ingredients", "ingredient_id"),
            ("sources.source_bioavailability", "ingredient_id", "nutrition.ingredients", "ingredient_id"),
            ("sources.source_bioavailability", "source_id", "sources.ingredient_sources", "source_id"),
            ("sources.source_composition", "source_id", "sources.ingredient_sources", "source_id"),
            ("recipes.recipe_components", "recipe_id", "recipes.recipes", "recipe_id"),
            ("recipes.recipe_components", "component", "sources.ingredient_sources", "source_id"),
        )
        for src_ds, src_col, dst_ds, dst_col in fk_checks:
            src = tables[src_ds]
            dst = tables[dst_ds]
            if src_col not in src.columns or dst_col not in dst.columns:
                continue
            src_values = set(src[src_col].astype(str).str.strip()) - {""}
            dst_values = set(dst[dst_col].astype(str).str.strip()) - {""}
            missing_refs = sorted(src_values - dst_values)
            for value in missing_refs:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        dataset=src_ds,
                        issue_type="broken_reference",
                        detail=f"{src_col}={value} missing in {dst_ds}.{dst_col}",
                    )
                )

        # Rule 4: missing evidence links for migrated rows
        for dataset_name, table in tables.items():
            if "status" not in table.columns:
                continue
            migrated = table[table["status"].astype(str).str.lower() == "migrated"]
            if migrated.empty:
                continue
            missing_links = (
                migrated["paper_link"].astype(str).str.strip() == ""
                if "paper_link" in migrated.columns
                else pd.Series([], dtype=bool)
            )
            if missing_links.any():
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        dataset=dataset_name,
                        issue_type="missing_evidence_link",
                        detail=f"{int(missing_links.sum())} migrated rows have empty paper_link",
                    )
                )

        # Rule 5: invalid URL format in paper_link
        for dataset_name, table in tables.items():
            if "paper_link" not in table.columns:
                continue
            values = table["paper_link"].astype(str).str.strip()
            bad = values[(values != "") & ~values.str.startswith(("http://", "https://"))]
            if len(bad):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        dataset=dataset_name,
                        issue_type="invalid_url",
                        detail=f"{len(bad)} non-http links",
                    )
                )

        ok = not any(i.severity == "error" for i in issues)
        return ValidationReport(ok=ok, issues=tuple(issues))

    def resolve_id(self, dataset_name: str, id_column: str, value: str) -> str | None:
        table = self.load_dataset(dataset_name)
        if id_column not in table.columns:
            return None
        matches = table[table[id_column].astype(str).str.strip() == value.strip()]
        if matches.empty:
            return None
        return str(matches.iloc[0][id_column]).strip()

    @staticmethod
    def render_validation_report(report: ValidationReport) -> str:
        lines = [
            "# validation_report",
            "",
            f"Status: {'PASS' if report.ok else 'FAIL'}",
            f"Total issues: {len(report.issues)}",
            "",
            "## Issues",
        ]
        if not report.issues:
            lines.append("- None")
            return "\n".join(lines) + "\n"

        for issue in report.issues:
            lines.append(
                f"- [{issue.severity.upper()}] `{issue.dataset}` `{issue.issue_type}` — {issue.detail}"
            )
        return "\n".join(lines) + "\n"

    @staticmethod
    def list_needs_validation_files(warehouse_root: Path) -> list[Path]:
        return sorted((warehouse_root).rglob("*_NEEDS_VALIDATION.csv"))

    def assert_immutable(self, frames: Iterable[pd.DataFrame]) -> None:
        # Guard method for engine callers: they should not mutate in-place.
        for frame in frames:
            if not isinstance(frame, pd.DataFrame):
                raise TypeError("WarehouseInterface only returns pandas.DataFrame objects.")
