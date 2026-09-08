"""Fail-closed entity resolver. Does not reason, optimize, or create IDs."""

from __future__ import annotations

import re
from typing import Iterable

from app.contracts.agent.enums import InputState
from app.normalization.catalog import EntityRecord, MappingCatalog, load_catalog
from app.normalization.enums import ENTITY_TO_DOMAIN, FORBIDDEN_RESULT_DOMAINS, EntityKind, MappingStatus
from app.normalization.models import MappingCandidate, NormalizationInput, NormalizationResult
from app.normalization.text import fold_lookup_key, is_blank
from app.normalization.version import MAPPING_CONFIG_VERSION

# Require a standalone separator. Do not split on the letter x inside words (e.g. Boxer).
_MIXED_SPLIT = re.compile(r"(?:\s+[x×]\s+|\s*×\s*|\s*/\s*)", re.IGNORECASE)
_WEIGHT = re.compile(
    r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(kg|kilogram|kilograms)?\s*$",
    re.IGNORECASE,
)
_AGE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(?:y(?:ears?)?|yo)?\s*$", re.IGNORECASE)
_LB = re.compile(r"\b(lb|lbs|pound|pounds)\b", re.IGNORECASE)


def _candidates(records: Iterable[EntityRecord]) -> list[MappingCandidate]:
    return [
        MappingCandidate(canonical_id=item.canonical_id, canonical_name=item.canonical_name)
        for item in records
    ]


def _base(
    inp: NormalizationInput,
    *,
    status: MappingStatus,
    normalized: str | None,
    record: EntityRecord | None = None,
    canonical_id: str | None = None,
    canonical_name: str | None = None,
    mapping_source: str | None = None,
    mapping_rule: str | None = None,
    candidates: list[MappingCandidate] | None = None,
    components: list[NormalizationResult] | None = None,
    numeric_value: float | None = None,
    unit: str | None = None,
    input_state: InputState | None = None,
) -> NormalizationResult:
    domain = ENTITY_TO_DOMAIN[inp.entity_kind]
    if domain in FORBIDDEN_RESULT_DOMAINS:
        raise RuntimeError(f"Ω12 must not emit {domain}")
    return NormalizationResult(
        raw_value=inp.raw_value,
        normalized_value=normalized,
        canonical_id=record.canonical_id if record is not None else canonical_id,
        canonical_name=record.canonical_name if record is not None else canonical_name,
        entity_kind=inp.entity_kind,
        domain_kind=domain,
        status=status,
        mapping_source=mapping_source,
        mapping_rule=mapping_rule,
        candidates=candidates or [],
        components=components or [],
        numeric_value=numeric_value,
        unit=unit,
        input_state=input_state,
        mapping_config_version=MAPPING_CONFIG_VERSION,
        source=inp.source,
    )


def _blank_result(inp: NormalizationInput) -> NormalizationResult:
    return _base(
        inp,
        status=MappingStatus.UNRESOLVED,
        normalized=None,
        mapping_rule="blank_or_missing",
        input_state=InputState.NOT_PROVIDED,
    )


def resolve(inp: NormalizationInput, catalog: MappingCatalog | None = None) -> NormalizationResult:
    catalog = catalog or load_catalog()
    if inp.entity_kind in {EntityKind.AGE_YEARS, EntityKind.WEIGHT_KG}:
        return _resolve_quantity(inp)
    if is_blank(inp.raw_value):
        return _blank_result(inp)
    if inp.entity_kind == EntityKind.BREED:
        mixed = _try_mixed_breed(inp, catalog)
        if mixed is not None:
            return mixed
    return _resolve_identity(inp, catalog)


def resolve_raw(
    raw_value: str | None,
    entity_kind: EntityKind,
    *,
    source: str | None = None,
    catalog: MappingCatalog | None = None,
) -> NormalizationResult:
    return resolve(
        NormalizationInput(raw_value=raw_value, entity_kind=entity_kind, source=source),
        catalog,
    )


def _resolve_quantity(inp: NormalizationInput) -> NormalizationResult:
    if is_blank(inp.raw_value):
        return _blank_result(inp)
    text = str(inp.raw_value)
    folded = fold_lookup_key(text)
    if inp.entity_kind == EntityKind.WEIGHT_KG:
        if _LB.search(text):
            return _base(
                inp,
                status=MappingStatus.UNRESOLVED,
                normalized=folded,
                mapping_rule="unsupported_weight_unit",
                input_state=InputState.INVALID,
            )
        match = _WEIGHT.match(text)
        if not match:
            return _base(
                inp,
                status=MappingStatus.UNRESOLVED,
                normalized=folded,
                mapping_rule="unparseable_weight",
                input_state=InputState.INVALID,
            )
        value = float(match.group(1))
        return _base(
            inp,
            status=MappingStatus.RESOLVED,
            normalized=f"{value} kg",
            mapping_source="entity_kind_weight_kg",
            mapping_rule="parse_metric_weight",
            numeric_value=value,
            unit="kg",
            input_state=InputState.PROVIDED,
        )
    match = _AGE.match(text)
    if not match:
        return _base(
            inp,
            status=MappingStatus.UNRESOLVED,
            normalized=folded,
            mapping_rule="unparseable_age",
            input_state=InputState.INVALID,
        )
    value = float(match.group(1))
    return _base(
        inp,
        status=MappingStatus.RESOLVED,
        normalized=str(value),
        mapping_source="entity_kind_age_years",
        mapping_rule="parse_age_years",
        numeric_value=value,
        unit="years",
        input_state=InputState.PROVIDED,
    )


def _try_mixed_breed(inp: NormalizationInput, catalog: MappingCatalog) -> NormalizationResult | None:
    raw = str(inp.raw_value or "")
    if not _MIXED_SPLIT.search(raw):
        return None
    parts = [part.strip() for part in _MIXED_SPLIT.split(raw) if part.strip()]
    if len(parts) < 2:
        return None
    components = [
        _resolve_identity(
            NormalizationInput(raw_value=part, entity_kind=EntityKind.BREED, source=inp.source),
            catalog,
        )
        for part in parts
    ]
    return _base(
        inp,
        status=MappingStatus.MIXED,
        normalized=fold_lookup_key(raw),
        mapping_rule="mixed_breed_separator",
        mapping_source="structured_components_not_a_canonical_breed",
        components=components,
        input_state=InputState.PROVIDED,
    )


def _resolve_identity(inp: NormalizationInput, catalog: MappingCatalog) -> NormalizationResult:
    index = catalog.kinds[inp.entity_kind]
    key = fold_lookup_key(inp.raw_value)
    hits = index.aliases.get(key) or []
    if len(hits) == 1:
        record = hits[0]
        source = "canonical_identity"
        name_key = fold_lookup_key(record.canonical_name)
        id_key = fold_lookup_key(record.canonical_id)
        if key == name_key:
            rule = "exact_canonical_name"
        elif key == id_key:
            rule = "exact_canonical_id"
            source = "canonical_id"
        else:
            rule = "explicit_alias"
            source = "approved_alias_mapping"
        return _base(
            inp,
            status=MappingStatus.RESOLVED,
            normalized=key,
            record=record,
            mapping_source=source,
            mapping_rule=rule,
            input_state=InputState.PROVIDED,
        )
    if len(hits) > 1:
        return _base(
            inp,
            status=MappingStatus.AMBIGUOUS,
            normalized=key,
            mapping_rule="alias_collision",
            mapping_source="approved_alias_mapping",
            candidates=_candidates(hits),
            input_state=InputState.PROVIDED,
        )
    token_hits = index.name_tokens.get(key) or []
    if len(token_hits) >= 2:
        return _base(
            inp,
            status=MappingStatus.AMBIGUOUS,
            normalized=key,
            mapping_rule="shared_name_token",
            mapping_source="canonical_name_token_index",
            candidates=_candidates(token_hits),
            input_state=InputState.PROVIDED,
        )
    return _base(
        inp,
        status=MappingStatus.UNRESOLVED,
        normalized=key,
        mapping_rule="no_approved_mapping",
        input_state=InputState.PROVIDED,
    )


def assert_mapping_not_science(result: NormalizationResult) -> None:
    assert result.domain_kind not in FORBIDDEN_RESULT_DOMAINS
    assert "prevalence" not in result.model_fields
    dumped = result.model_dump()
    assert "prevalence" not in dumped
