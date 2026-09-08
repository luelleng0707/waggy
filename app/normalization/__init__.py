"""Ω12 normalization + entity mapping. Fail closed. Not the scientific engine."""

from __future__ import annotations

from app.normalization.enums import EntityKind, MappingStatus
from app.normalization.models import NormalizationInput, NormalizationResult
from app.normalization.resolver import resolve, resolve_raw
from app.normalization.version import MAPPING_CONFIG_VERSION

__all__ = [
    "MAPPING_CONFIG_VERSION",
    "EntityKind",
    "MappingStatus",
    "NormalizationInput",
    "NormalizationResult",
    "resolve",
    "resolve_raw",
]
