"""Coverage analysis (QA-907)."""

from __future__ import annotations

import pandas as pd

from .models import CoverageReport, CoverageRow


class DeterministicCoverageAnalyzer:
    def analyze(self, tables: dict[str, pd.DataFrame]) -> CoverageReport:
        conditions = tables.get("biology.conditions", pd.DataFrame())
        condition_objectives = tables.get("objectives.condition_objectives", pd.DataFrame())
        objective_mechanisms = tables.get("objectives.objective_mechanisms", pd.DataFrame())
        ingredient_mechanisms = tables.get("mechanisms.ingredient_mechanisms", pd.DataFrame())
        ingredient_sources = tables.get("sources.ingredient_sources", pd.DataFrame())
        source_recipes = tables.get("science_graph.source_recipes", pd.DataFrame())
        recipe_products = tables.get("science_graph.recipe_products", pd.DataFrame())

        obj_by_cond = _group_set(condition_objectives, "condition_id", "objective_id")
        mech_by_obj = _group_set(objective_mechanisms, "objective_id", "mechanism_id")
        ing_by_mech = _group_set(ingredient_mechanisms, "mechanism_id", "ingredient_id")
        src_by_ing = _group_set(ingredient_sources, "ingredient_id", "source_id")
        rcp_by_src = _group_set(source_recipes, "source_id", "recipe_id")
        prod_by_rcp = _group_set(recipe_products, "recipe_id", "product_id")

        rows: list[CoverageRow] = []
        for _, row in conditions.iterrows():
            condition_id = str(row.get("condition_id", "")).strip()
            condition_name = str(row.get("condition_name", condition_id)).strip()
            if not condition_id:
                continue
            objectives = obj_by_cond.get(condition_id, set())
            mechanisms = set().union(*[mech_by_obj.get(obj, set()) for obj in objectives]) if objectives else set()
            ingredients = set().union(*[ing_by_mech.get(mech, set()) for mech in mechanisms]) if mechanisms else set()
            sources = set().union(*[src_by_ing.get(ing, set()) for ing in ingredients]) if ingredients else set()
            recipes = set().union(*[rcp_by_src.get(src, set()) for src in sources]) if sources else set()
            products = set().union(*[prod_by_rcp.get(rcp, set()) for rcp in recipes]) if recipes else set()

            evidence_rows = []
            for table_name in (
                condition_objectives,
                objective_mechanisms,
                ingredient_mechanisms,
                ingredient_sources,
                source_recipes,
                recipe_products,
            ):
                if "paper_name" in table_name.columns:
                    evidence_rows.extend(table_name["paper_name"].astype(str).str.strip().tolist())
                elif "paper" in table_name.columns:
                    evidence_rows.extend(table_name["paper"].astype(str).str.strip().tolist())
            evidence_papers = set([paper for paper in evidence_rows if paper])

            years = []
            for table_name in (conditions, condition_objectives, ingredient_mechanisms):
                if "publication_year" in table_name.columns:
                    for value in table_name["publication_year"].astype(str).str.strip():
                        if value.isdigit():
                            years.append(int(value))
            avg_year = float(sum(years) / len(years)) if years else 0.0

            rows.append(
                CoverageRow(
                    condition_id=condition_id,
                    condition_name=condition_name,
                    objectives_count=len(objectives),
                    mechanisms_count=len(mechanisms),
                    ingredients_count=len(ingredients),
                    sources_count=len(sources),
                    recipes_count=len(recipes),
                    products_count=len(products),
                    evidence_papers_count=len(evidence_papers),
                    average_publication_year=round(avg_year, 2),
                )
            )

        metrics = {
            "conditions_total": len(rows),
            "conditions_with_objectives": sum(1 for row in rows if row.objectives_count > 0),
            "conditions_with_products": sum(1 for row in rows if row.products_count > 0),
        }
        return CoverageReport(rows=tuple(sorted(rows, key=lambda row: row.condition_id)), metrics=metrics)


def _group_set(table: pd.DataFrame, key_col: str, value_col: str) -> dict[str, set[str]]:
    if table.empty or key_col not in table.columns or value_col not in table.columns:
        return {}
    output: dict[str, set[str]] = {}
    for _, row in table.iterrows():
        key = str(row.get(key_col, "")).strip()
        value = str(row.get(value_col, "")).strip()
        if not key or not value:
            continue
        output.setdefault(key, set()).add(value)
    return output
