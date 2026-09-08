"""Ω12 mapping matrix. Fail closed. Does not reason or optimize."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.agent.version import ALGORITHM_VERSION
from app.contracts.agent.enums import DomainKind, InputState
from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION
from app.normalization.catalog import EntityRecord, KindIndex, MappingCatalog, load_catalog
from app.normalization.enums import FORBIDDEN_RESULT_DOMAINS, EntityKind, MappingStatus
from app.normalization.models import NormalizationInput
from app.normalization.resolver import resolve, resolve_raw
from app.normalization.version import MAPPING_CONFIG_VERSION

LABRADOR = "BREED_B02F1BE9"
GOLDEN = "BREED_4C2466ED"
GSD = "BREED_2E91411B"
HIP_DYSPLASIA = "COND_653473C1"
FARMINA_FOOD = "SF001"
ZEAL_MUSSELS = "TR011"
REPO = Path(__file__).resolve().parents[2]
BREEDS_CSV = REPO / "warehouse" / "biology" / "breeds.csv"
CONDITIONS_CSV = REPO / "warehouse" / "biology" / "conditions.csv"
PRODUCTS_CSV = REPO / "warehouse" / "commercial" / "product_master.csv"


def _ids(path: Path, id_col: str) -> set[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row[id_col].strip() for row in csv.DictReader(handle) if row.get(id_col)}


BREED_IDS = _ids(BREEDS_CSV, "breed_id")
CONDITION_IDS = _ids(CONDITIONS_CSV, "condition_id")
PRODUCT_IDS = _ids(PRODUCTS_CSV, "product_id")


def test_a_exact_canonical_breed_name():
    result = resolve_raw("Labrador Retriever", EntityKind.BREED)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == LABRADOR
    assert result.canonical_name == "Labrador Retriever"
    assert result.mapping_rule == "exact_canonical_name"
    assert result.canonical_id in BREED_IDS


def test_a_exact_canonical_id():
    result = resolve_raw(LABRADOR, EntityKind.BREED)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == LABRADOR
    assert result.mapping_rule == "exact_canonical_id"


def test_b_exact_alias_lab_and_labrador():
    lab = resolve_raw("Lab", EntityKind.BREED)
    labrador = resolve_raw("Labrador", EntityKind.BREED)
    assert lab.status == labrador.status == MappingStatus.RESOLVED
    assert lab.canonical_id == labrador.canonical_id == LABRADOR
    assert lab.mapping_source == "approved_alias_mapping"


def test_b_condition_alias_hd():
    result = resolve_raw("HD", EntityKind.CONDITION)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == HIP_DYSPLASIA
    assert result.canonical_id in CONDITION_IDS
    assert result.domain_kind == DomainKind.USER_INPUT
    assert result.domain_kind != DomainKind.SCIENTIFIC_FACT


def test_c_case_normalization():
    upper = resolve_raw("LABRADOR RETRIEVER", EntityKind.BREED)
    lower = resolve_raw("labrador retriever", EntityKind.BREED)
    assert upper.status == lower.status == MappingStatus.RESOLVED
    assert upper.canonical_id == lower.canonical_id == LABRADOR
    assert upper.normalized_value == lower.normalized_value == "labrador retriever"


def test_d_whitespace_normalization():
    result = resolve_raw("  Hip   Dysplasia  ", EntityKind.CONDITION)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == HIP_DYSPLASIA
    assert result.normalized_value == "hip dysplasia"


def test_e_unresolved_unknown_breed():
    result = resolve_raw("fluffster", EntityKind.BREED)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_id is None
    assert result.mapping_rule == "no_approved_mapping"


def test_e_does_not_fabricate_canonical_id():
    result = resolve_raw("some weird terrier mix", EntityKind.BREED)
    assert result.status in {MappingStatus.UNRESOLVED, MappingStatus.MIXED, MappingStatus.AMBIGUOUS}
    assert result.canonical_id != "some_weird_terrier_mix"
    assert result.canonical_id != "weird_terrier_mix"
    assert result.canonical_id not in BREED_IDS or result.status != MappingStatus.RESOLVED


def test_f_ambiguous_retriever():
    result = resolve_raw("retriever", EntityKind.BREED)
    assert result.status == MappingStatus.AMBIGUOUS
    assert result.canonical_id is None
    ids = {item.canonical_id for item in result.candidates}
    assert ids == {LABRADOR, GOLDEN}
    assert result.mapping_rule == "shared_name_token"


def test_f_ambiguous_terrier():
    result = resolve_raw("terrier", EntityKind.BREED)
    assert result.status == MappingStatus.AMBIGUOUS
    assert result.canonical_id is None
    assert len(result.candidates) >= 2


def test_g_duplicate_aliases_same_canonical():
    first = resolve_raw("Lab", EntityKind.BREED)
    second = resolve_raw("Labrador", EntityKind.BREED)
    assert first.canonical_id == second.canonical_id == LABRADOR
    assert first.status == MappingStatus.RESOLVED


def test_h_alias_collision_fails_closed():
    index = KindIndex()
    left = EntityRecord(canonical_id=LABRADOR, canonical_name="Labrador Retriever")
    right = EntityRecord(canonical_id=GOLDEN, canonical_name="Golden Retriever")
    index.aliases["shared"] = [left, right]
    catalog = MappingCatalog(kinds={EntityKind.BREED: index})
    result = resolve(
        NormalizationInput(raw_value="shared", entity_kind=EntityKind.BREED),
        catalog,
    )
    assert result.status == MappingStatus.AMBIGUOUS
    assert result.canonical_id is None
    assert {item.canonical_id for item in result.candidates} == {LABRADOR, GOLDEN}


def test_h_hyphen_not_stripped():
    hyphen = resolve_raw("Lab-rador", EntityKind.BREED)
    compact = resolve_raw("Labrador", EntityKind.BREED)
    assert hyphen.status == MappingStatus.UNRESOLVED
    assert compact.status == MappingStatus.RESOLVED
    assert hyphen.canonical_id != compact.canonical_id


def test_i_deterministic_repeated_resolution():
    first = resolve_raw("  Golden Retriever ", EntityKind.BREED).to_json_dict()
    second = resolve_raw("  Golden Retriever ", EntityKind.BREED).to_json_dict()
    third = resolve_raw("  Golden Retriever ", EntityKind.BREED).to_json_dict()
    assert first == second == third


def test_j_domain_kind_preserved_by_caller_kind():
    breed = resolve_raw("HD", EntityKind.BREED)
    condition = resolve_raw("HD", EntityKind.CONDITION)
    assert breed.status == MappingStatus.UNRESOLVED
    assert condition.status == MappingStatus.RESOLVED
    assert breed.entity_kind == EntityKind.BREED
    assert condition.entity_kind == EntityKind.CONDITION
    assert condition.domain_kind == DomainKind.USER_INPUT


def test_k_observation_remains_observation():
    result = resolve_raw(
        "coat is extremely dense",
        EntityKind.OBSERVATION,
        source="groomer",
    )
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == "dense_coat"
    assert result.domain_kind == DomainKind.OBSERVATION
    assert result.domain_kind != DomainKind.SCIENTIFIC_FACT
    assert result.source == "groomer"


def test_l_mapping_does_not_create_scientific_fact():
    result = resolve_raw("hip dysplasia", EntityKind.CONDITION)
    dumped = result.to_json_dict()
    assert "prevalence" not in dumped
    assert result.domain_kind not in FORBIDDEN_RESULT_DOMAINS
    assert result.domain_kind != DomainKind.SCIENTIFIC_FACT


def test_m_mapping_does_not_create_inference():
    result = resolve_raw("Labrador Retriever", EntityKind.BREED)
    dumped = result.to_json_dict()
    assert result.domain_kind != DomainKind.SCIENTIFIC_INFERENCE
    assert "risk" not in dumped
    assert dumped.get("canonical_id") == LABRADOR


def test_n_mapping_does_not_create_recommendation():
    result = resolve_raw(FARMINA_FOOD, EntityKind.PRODUCT)
    assert result.status == MappingStatus.RESOLVED
    assert result.domain_kind != DomainKind.RECOMMENDATION
    assert result.canonical_id == FARMINA_FOOD
    assert result.canonical_id in PRODUCT_IDS


def test_o_product_mapping_remains_product():
    result = resolve_raw("Zeal Green Lipped Mussels 50g", EntityKind.PRODUCT)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == ZEAL_MUSSELS
    assert result.domain_kind == DomainKind.PRODUCT_FACT
    brand = resolve_raw("Farmina", EntityKind.BRAND)
    assert brand.status == MappingStatus.RESOLVED
    assert brand.domain_kind == DomainKind.COMMERCIAL_CONFIGURATION


def test_p_condition_identity_is_not_evidence():
    result = resolve_raw("canine hip dysplasia", EntityKind.CONDITION)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == HIP_DYSPLASIA
    assert result.domain_kind != DomainKind.SCIENTIFIC_EVIDENCE
    assert result.domain_kind != DomainKind.SCIENTIFIC_FACT


def test_q_missing_age_does_not_default_to_five():
    result = resolve_raw(None, EntityKind.AGE_YEARS)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.numeric_value is None
    assert result.numeric_value != 5
    assert result.input_state == InputState.NOT_PROVIDED


def test_q_missing_weight_does_not_default_to_twenty():
    result = resolve_raw("   ", EntityKind.WEIGHT_KG)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.numeric_value is None
    assert result.numeric_value != 20
    assert result.input_state == InputState.NOT_PROVIDED


def test_q_blank_breed_is_not_provided():
    result = resolve_raw("", EntityKind.BREED)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.input_state == InputState.NOT_PROVIDED
    assert result.canonical_id is None


def test_r_mixed_breed_is_not_a_new_canonical_breed():
    result = resolve_raw("Labrador x Golden", EntityKind.BREED)
    assert result.status == MappingStatus.MIXED
    assert result.canonical_id is None
    assert len(result.components) == 2
    assert result.components[0].canonical_id == LABRADOR
    assert result.components[1].canonical_id == GOLDEN
    assert result.canonical_id not in BREED_IDS


def test_r_slash_mixed_breed():
    result = resolve_raw("Labrador Retriever / Golden Retriever", EntityKind.BREED)
    assert result.status == MappingStatus.MIXED
    assert result.canonical_id is None
    assert [item.canonical_id for item in result.components] == [LABRADOR, GOLDEN]


def test_r_intra_word_x_is_not_mixed():
    result = resolve_raw("Boxer", EntityKind.BREED)
    assert result.status != MappingStatus.MIXED
    assert result.status == MappingStatus.UNRESOLVED


def test_s_traceability_fields():
    result = resolve_raw("Labrador Retriever", EntityKind.BREED)
    assert result.raw_value == "Labrador Retriever"
    assert result.normalized_value == "labrador retriever"
    assert result.canonical_id == LABRADOR
    assert result.mapping_source == "canonical_identity"
    assert result.mapping_rule == "exact_canonical_name"
    assert result.mapping_config_version == MAPPING_CONFIG_VERSION


def test_t_resolved_ids_exist_in_warehouse():
    catalog = load_catalog()
    for record in catalog.kinds[EntityKind.BREED].by_id.values():
        assert record.canonical_id in BREED_IDS
    for record in catalog.kinds[EntityKind.CONDITION].by_id.values():
        assert record.canonical_id in CONDITION_IDS
    for record in catalog.kinds[EntityKind.PRODUCT].by_id.values():
        assert record.canonical_id in PRODUCT_IDS


def test_sex_aliases():
    assert resolve_raw("boy", EntityKind.SEX).canonical_id == "male"
    assert resolve_raw("m", EntityKind.SEX).canonical_id == "male"
    assert resolve_raw("girl", EntityKind.SEX).canonical_id == "female"
    assert resolve_raw("F", EntityKind.SEX).canonical_id == "female"
    male = resolve_raw("male", EntityKind.SEX)
    assert male.domain_kind == DomainKind.USER_INPUT


def test_age_and_weight_metric_parse():
    age = resolve_raw("5", EntityKind.AGE_YEARS)
    weight = resolve_raw("20 kg", EntityKind.WEIGHT_KG)
    bare = resolve_raw("20", EntityKind.WEIGHT_KG)
    assert age.status == MappingStatus.RESOLVED
    assert age.numeric_value == 5.0
    assert age.unit == "years"
    assert age.canonical_id is None
    assert weight.status == MappingStatus.RESOLVED
    assert weight.numeric_value == 20.0
    assert weight.unit == "kg"
    assert weight.canonical_id is None
    assert bare.status == MappingStatus.RESOLVED
    assert bare.numeric_value == 20.0


def test_unsupported_lb_and_about_phrases():
    assert resolve_raw("20 lb", EntityKind.WEIGHT_KG).status == MappingStatus.UNRESOLVED
    assert resolve_raw("about 10 kilos", EntityKind.WEIGHT_KG).status == MappingStatus.UNRESOLVED
    assert resolve_raw("about 5", EntityKind.AGE_YEARS).status == MappingStatus.UNRESOLVED


def test_gsd_alias():
    result = resolve_raw("GSD", EntityKind.BREED)
    assert result.status == MappingStatus.RESOLVED
    assert result.canonical_id == GSD


def test_versions_are_not_algorithm_version():
    assert ALGORITHM_VERSION == "2.1.0"
    assert AGENT_CONTRACT_SCHEMA_VERSION == "1.0.0"
    assert MAPPING_CONFIG_VERSION == "1.0.0"
    result = resolve_raw("Lab", EntityKind.BREED)
    assert result.mapping_config_version == "1.0.0"


def test_end_to_end_identity_only_stops_before_science():
    breed = resolve_raw("Labrador Retriever", EntityKind.BREED)
    age = resolve_raw("5", EntityKind.AGE_YEARS)
    weight = resolve_raw("20 kg", EntityKind.WEIGHT_KG)
    observation = resolve_raw("very dense coat", EntityKind.OBSERVATION, source="groomer")
    product = resolve_raw("Example Omega Supplement", EntityKind.PRODUCT)
    assert breed.canonical_id == LABRADOR
    assert age.numeric_value == 5.0
    assert weight.numeric_value == 20.0
    assert observation.canonical_id == "dense_coat"
    assert observation.domain_kind == DomainKind.OBSERVATION
    assert product.status == MappingStatus.UNRESOLVED
    for result in (breed, age, weight, observation, product):
        dumped = result.to_json_dict()
        assert "prevalence" not in dumped
        assert result.domain_kind not in FORBIDDEN_RESULT_DOMAINS
        assert result.domain_kind != DomainKind.RECOMMENDATION
