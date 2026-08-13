from __future__ import annotations

import pandas as pd

from repository.warehouse import WarehouseInterface
from repository.warehouse_qa import WarehouseQARuntime


def _table(rows: list[dict[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, dtype=str)


def _base_tables() -> dict[str, pd.DataFrame]:
    return {
        "biology.conditions": _table(
            [
                {
                    "condition_id": "COND_A",
                    "condition_name": "Hip Dysplasia",
                    "scientific_quote": "Condition quote provides clear context for the claim.",
                    "paper_name": "Condition Paper",
                    "paper_link": "https://example.org/cond",
                    "publication_year": "2021",
                    "study_type": "cohort",
                }
            ]
        ),
        "reference.condition_systems": _table([{"condition_id": "COND_A", "body_system_id": "SYS_A"}]),
        "objectives.objectives": _table(
            [
                {
                    "objective_id": "OBJ_A",
                    "objective_name": "Reduce Joint Inflammation",
                    "scientific_quote": "Objective quote supports inflammation reduction mechanism.",
                    "paper_name": "Objective Paper",
                    "paper_link": "https://example.org/obj",
                    "publication_year": "2020",
                    "study_type": "review",
                }
            ]
        ),
        "objectives.condition_objectives": _table(
            [
                {
                    "condition_id": "COND_A",
                    "objective_id": "OBJ_A",
                    "importance": "0.9",
                    "scientific_quote": "Condition to objective mapping is directly supported.",
                    "paper_name": "CO Paper",
                    "paper_link": "https://example.org/co",
                    "publication_year": "2022",
                    "study_type": "cohort",
                }
            ]
        ),
        "mechanisms.mechanisms": _table(
            [
                {
                    "mechanism_id": "MEC_A",
                    "mechanism_name": "Anti-inflammatory",
                    "scientific_quote": "Mechanism quote with enough detail to support entry.",
                    "paper_name": "Mechanism Paper",
                    "paper_link": "https://example.org/mech",
                    "publication_year": "2019",
                    "study_type": "review",
                }
            ]
        ),
        "objectives.objective_mechanisms": _table(
            [
                {
                    "objective_id": "OBJ_A",
                    "mechanism_id": "MEC_A",
                    "importance": "0.8",
                    "scientific_quote": "Objective to mechanism relation is evidence-supported.",
                    "paper_name": "OM Paper",
                    "paper_link": "https://example.org/om",
                    "publication_year": "2020",
                    "study_type": "trial",
                }
            ]
        ),
        "nutrition.ingredients": _table(
            [
                {
                    "ingredient_id": "ING_A",
                    "ingredient_name": "Omega-3",
                    "scientific_quote": "Ingredient quote for omega-3 entry support.",
                    "paper_name": "Ing Paper",
                    "paper_link": "https://example.org/ing",
                    "publication_year": "2020",
                    "study_type": "trial",
                }
            ]
        ),
        "mechanisms.ingredient_mechanisms": _table(
            [
                {
                    "ingredient_id": "ING_A",
                    "mechanism_id": "MEC_A",
                    "observed_effect": "reduces inflammation markers",
                    "unit": "mg_per_day",
                    "scientific_quote": "Ingredient mechanism quote with adequate detail.",
                    "paper_name": "IM Paper",
                    "paper_link": "https://example.org/im",
                    "publication_year": "2021",
                    "study_type": "trial",
                }
            ]
        ),
        "sources.ingredient_sources": _table(
            [
                {
                    "source_id": "SRC_A",
                    "ingredient_id": "ING_A",
                    "unit": "mg_per_100g",
                    "scientific_quote": "Source quote provides origin and composition context.",
                    "paper_name": "Src Paper",
                    "paper_link": "https://example.org/src",
                    "publication_year": "2022",
                    "study_type": "analysis",
                }
            ]
        ),
        "science_graph.source_recipes": _table(
            [
                {
                    "source_id": "SRC_A",
                    "recipe_id": "RCP_A",
                    "scientific_quote": "Source to recipe mapping is justified in study text.",
                    "paper_name": "SR Paper",
                    "paper_link": "https://example.org/sr",
                    "publication_year": "2022",
                    "study_type": "analysis",
                }
            ]
        ),
        "recipes.recipes": _table(
            [
                {
                    "recipe_id": "RCP_A",
                    "scientific_quote": "Recipe quote supports compositional design basis.",
                    "paper_name": "Recipe Paper",
                    "paper_link": "https://example.org/rcp",
                    "publication_year": "2022",
                    "study_type": "analysis",
                }
            ]
        ),
        "science_graph.recipe_products": _table(
            [
                {
                    "recipe_id": "RCP_A",
                    "product_id": "PROD_A",
                    "scientific_quote": "Recipe to product mapping follows declared composition.",
                    "paper_name": "RP Paper",
                    "paper_link": "https://example.org/rp",
                    "publication_year": "2022",
                    "study_type": "analysis",
                }
            ]
        ),
        "optimization.product_servings": _table(
            [
                {
                    "product_id": "PROD_A",
                    "product_name": "Product A",
                    "scientific_quote": "Serving evidence with dosage boundary details.",
                    "paper_name": "Serving Paper",
                    "paper_link": "https://example.org/prod",
                    "publication_year": "2021",
                    "study_type": "label",
                }
            ]
        ),
        "biology.trait_condition_associations": _table(
            [
                {
                    "fact_id": "FACT_1",
                    "trait_name": "size",
                    "trait_value": "large",
                    "condition_id": "COND_A",
                    "effect_direction": "positive",
                    "unit": "ratio",
                    "scientific_quote": "Trait quote is specific and meaningful for association.",
                    "paper_name": "Trait Paper",
                    "paper_link": "https://example.org/trait",
                    "publication_year": "2021",
                    "study_type": "cohort",
                }
            ]
        ),
    }


def test_qa_runtime_deterministic():
    runtime = WarehouseQARuntime(WarehouseInterface())
    first = runtime.run(_base_tables())
    second = runtime.run(_base_tables())
    assert first == second


def test_broken_fk_detected():
    tables = _base_tables()
    tables["objectives.condition_objectives"].loc[0, "objective_id"] = "OBJ_MISSING"
    result = WarehouseQARuntime(WarehouseInterface()).run(tables)
    assert any(issue.code == "BROKEN_FOREIGN_KEY" for issue in result.foreign_keys.issues)


def test_duplicate_id_and_claim_detected():
    tables = _base_tables()
    duplicate_row = tables["mechanisms.ingredient_mechanisms"].iloc[0].copy()
    tables["mechanisms.ingredient_mechanisms"] = pd.concat(
        [tables["mechanisms.ingredient_mechanisms"], pd.DataFrame([duplicate_row])], ignore_index=True
    )
    result = WarehouseQARuntime(WarehouseInterface()).run(tables)
    assert any(issue.code == "DUPLICATE_CLAIM" for issue in result.duplicates.issues)


def test_invalid_url_and_missing_evidence_detected():
    tables = _base_tables()
    tables["objectives.objectives"].loc[0, "paper_link"] = "notaurl"
    tables["objectives.objectives"].loc[0, "scientific_quote"] = ""
    result = WarehouseQARuntime(WarehouseInterface()).run(tables)
    assert any(issue.code == "INVALID_URL" for issue in result.schema.issues)
    assert any(issue.code == "MISSING_EVIDENCE_FIELD" for issue in result.evidence.issues)


def test_missing_unit_and_ontology_violation_detected():
    tables = _base_tables()
    tables["mechanisms.ingredient_mechanisms"].loc[0, "unit"] = ""
    tables["nutrition.ingredients"] = _table(
        [
            {
                "ingredient_id": "ING_A",
                "ingredient_name": "Omega-3",
                "scientific_quote": "ok",
                "paper_name": "ok",
                "paper_link": "https://example.org/ing",
                "publication_year": "2020",
                "study_type": "trial",
            },
            {
                "ingredient_id": "ING_ORPHAN",
                "ingredient_name": "Orphan",
                "scientific_quote": "orphan entry quote",
                "paper_name": "orphan paper",
                "paper_link": "https://example.org/orphan",
                "publication_year": "2020",
                "study_type": "trial",
            },
        ]
    )
    result = WarehouseQARuntime(WarehouseInterface()).run(tables)
    assert any(issue.code == "MISSING_UNIT" for issue in result.units.issues)
    assert any(issue.code == "ORPHAN_INGREDIENT" for issue in result.ontology.issues)


def test_contradiction_coverage_and_publication_score():
    tables = _base_tables()
    contradiction_row = tables["mechanisms.ingredient_mechanisms"].iloc[0].copy()
    contradiction_row["observed_effect"] = "increases inflammation response"
    tables["mechanisms.ingredient_mechanisms"] = pd.concat(
        [tables["mechanisms.ingredient_mechanisms"], pd.DataFrame([contradiction_row])], ignore_index=True
    )
    result = WarehouseQARuntime(WarehouseInterface()).run(tables)
    assert any(issue.code == "CONTRADICTORY_EFFECT" for issue in result.consistency.issues)
    assert result.coverage.rows
    assert 0.0 <= result.publication.publication_score <= 100.0
