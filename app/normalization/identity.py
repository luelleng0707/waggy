"""Breed identity knowledge provider — Ω12 surface, not a second resolver.

CSV/pandas remain inside MappingCatalog.load_catalog. This module exposes
plain typed values only. name_tokens are not knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.normalization.catalog import EntityRecord, MappingCatalog, load_catalog
from app.normalization.enums import EntityKind
from app.normalization.text import fold_lookup_key
from app.normalization.version import MAPPING_CONFIG_VERSION

# Existing Ω12 identity row. Do not duplicate the type.
BreedIdentity = EntityRecord

VARIANT_CANONICAL_SELF = "canonical_self"
VARIANT_ALIAS = "alias"
REVIEW_APPROVED = "approved"


@dataclass(frozen=True, slots=True)
class BreedNameVariant:
    value: str
    canonical_id: str
    variant_type: str
    review_status: str


class BreedIdentityKnowledgeProvider(Protocol):
    def knowledge_version(self) -> str: ...

    def identities(self) -> tuple[BreedIdentity, ...]: ...

    def variants_for(self, normalized_value: str) -> tuple[BreedNameVariant, ...]: ...


class Omega12BreedIdentityProvider:
    """Approved breed identities and display variants from the existing KindIndex."""

    def __init__(self, catalog: MappingCatalog | None = None) -> None:
        self._catalog = catalog if catalog is not None else load_catalog()
        self._index = self._catalog.kinds[EntityKind.BREED]

    def knowledge_version(self) -> str:
        return MAPPING_CONFIG_VERSION

    def identities(self) -> tuple[BreedIdentity, ...]:
        return tuple(self._index.by_id.values())

    def variants_for(self, normalized_value: str) -> tuple[BreedNameVariant, ...]:
        key = fold_lookup_key(normalized_value)
        if not key:
            return ()
        records = self._index.aliases.get(key) or []
        out: list[BreedNameVariant] = []
        for record in records:
            name_key = fold_lookup_key(record.canonical_name)
            id_key = fold_lookup_key(record.canonical_id)
            if key == id_key and key != name_key:
                continue
            variant_type = VARIANT_CANONICAL_SELF if key == name_key else VARIANT_ALIAS
            out.append(
                BreedNameVariant(
                    value=key,
                    canonical_id=record.canonical_id,
                    variant_type=variant_type,
                    review_status=REVIEW_APPROVED,
                )
            )
        return tuple(out)


def breed_identity_provider(
    catalog: MappingCatalog | None = None,
) -> Omega12BreedIdentityProvider:
    return Omega12BreedIdentityProvider(catalog)
