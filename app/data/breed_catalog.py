"""CSV-era adapter: wrap the existing DataPlatform breed projection.

Does not parse warehouse CSVs. Does not replace load_biology_warehouse.
Does not implement contains/isin matching used by FormulaGraph consumers.
"""

from __future__ import annotations

from typing import Any, Mapping

from app.data.breed_knowledge import TRAIT_NAMES, BreedKnowledge, BreedTraitFact


def _cell(row: Mapping[str, Any], key: str) -> str:
    raw = row.get(key)
    if raw is None:
        return ""
    if isinstance(raw, float) and raw != raw:
        return ""
    text = str(raw)
    if text.lower() == "nan":
        return ""
    return text


def _knowledge_from_row(row: Mapping[str, Any]) -> BreedKnowledge:
    traits: list[BreedTraitFact] = []
    for name in TRAIT_NAMES:
        value = _cell(row, name)
        if value:
            traits.append(BreedTraitFact(trait_name=name, trait_value=value))
    return BreedKnowledge(
        breed_id=_cell(row, "breed_id"),
        canonical_name=_cell(row, "breed"),
        status=_cell(row, "status"),
        species=_cell(row, "species"),
        breed_group=_cell(row, "breed_group"),
        traits=tuple(traits),
    )


class BiologyCsvBreedCatalog:
    """Snapshot of DataPlatform.breeds_df() + existing alias map."""

    def __init__(
        self,
        *,
        warehouse_version: str,
        alias_map: Mapping[str, str],
        rows: list[Mapping[str, Any]],
    ) -> None:
        self._warehouse_version = str(warehouse_version)
        self._alias_map = {str(k): str(v) for k, v in dict(alias_map).items()}
        breeds: list[BreedKnowledge] = []
        by_lower: dict[str, BreedKnowledge] = {}
        for row in rows:
            fact = _knowledge_from_row(row)
            breeds.append(fact)
            if fact.canonical_name:
                key = fact.canonical_name.lower()
                if key not in by_lower:
                    by_lower[key] = fact
        self._breeds = tuple(breeds)
        self._by_lower = by_lower

    @classmethod
    def from_platform(cls, platform: Any) -> BiologyCsvBreedCatalog:
        frame = platform.breeds_df()
        rows = frame.to_dict(orient="records") if frame is not None else []
        return cls(
            warehouse_version=str(getattr(platform, "version", "")),
            alias_map=dict(platform.breed_alias_map()),
            rows=list(rows),
        )

    @property
    def warehouse_version(self) -> str:
        return self._warehouse_version

    def normalize_name(self, raw: str) -> str:
        key = str(raw or "").strip().lower()
        return self._alias_map.get(key, str(raw or "").strip())

    def all_breeds(self) -> tuple[BreedKnowledge, ...]:
        return self._breeds

    def get_by_canonical_name(self, name: str) -> BreedKnowledge | None:
        text = str(name or "").strip()
        if not text:
            return None
        return self._by_lower.get(text.lower())
