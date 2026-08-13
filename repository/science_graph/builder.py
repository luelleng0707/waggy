"""Deterministic warehouse-to-graph builder for Ω7."""

from __future__ import annotations

from pathlib import Path

from repository.warehouse import WarehouseInterface
from repository.warehouse.warehouse_interface import CANONICAL_DATASETS

from .models import EvidenceEdge, EvidenceNode, KnowledgeGraph, ScientificEdge, ScientificNode

SCIENCE_GRAPH_DATASETS: dict[str, str] = {
    "science_graph.source_recipes": "science_graph/source_recipes.csv",
    "science_graph.recipe_products": "science_graph/recipe_products.csv",
    "science_graph.ingredient_aliases": "science_graph/ingredient_aliases.csv",
    "optimization.product_servings": "optimization/product_servings.csv",
}


def register_science_graph_datasets() -> None:
    for dataset_name, relative_path in SCIENCE_GRAPH_DATASETS.items():
        if dataset_name not in CANONICAL_DATASETS:
            CANONICAL_DATASETS[dataset_name] = Path(relative_path)


class WarehouseScientificGraphBuilder:
    def __init__(self, warehouse: WarehouseInterface):
        register_science_graph_datasets()
        self.warehouse = warehouse

    def build(self) -> KnowledgeGraph:
        nodes: dict[str, ScientificNode] = {}
        edges: list[ScientificEdge] = []

        def add_node(node_id: str, node_type: str, node_name: str, warehouse_row_id: str) -> None:
            if not node_id:
                return
            if node_id not in nodes:
                nodes[node_id] = ScientificNode(
                    node_id=node_id,
                    node_type=node_type,
                    node_name=node_name or node_id,
                    warehouse_row_id=warehouse_row_id,
                )

        def add_edge(
            edge_id: str,
            source: str,
            target: str,
            relationship_type: str,
            warehouse_row_id: str,
            scientific_quote: str,
            paper_name: str,
            paper_link: str,
        ) -> None:
            if not source or not target:
                return
            edges.append(
                ScientificEdge(
                    edge_id=edge_id,
                    source_node_id=source,
                    target_node_id=target,
                    relationship_type=relationship_type,
                    warehouse_row_id=warehouse_row_id,
                    scientific_quote=scientific_quote.strip(),
                    paper_name=paper_name.strip(),
                    paper_link=paper_link.strip(),
                    formula_ids=("GRF-803",),
                )
            )

        breeds = self.warehouse.load_dataset("biology.breeds")
        conditions = self.warehouse.load_dataset("biology.conditions")
        trait_condition = self.warehouse.load_dataset("biology.trait_condition_associations")
        objectives = self.warehouse.load_dataset("objectives.objectives")
        condition_objectives = self.warehouse.load_dataset("objectives.condition_objectives")
        objective_mechanisms = self.warehouse.load_dataset("objectives.objective_mechanisms")
        mechanisms = self.warehouse.load_dataset("mechanisms.mechanisms")
        ingredient_mechanisms = self.warehouse.load_dataset("mechanisms.ingredient_mechanisms")
        ingredients = self.warehouse.load_dataset("nutrition.ingredients")
        ingredient_sources = self.warehouse.load_dataset("sources.ingredient_sources")
        recipes = self.warehouse.load_dataset("recipes.recipes")
        source_recipes = self.warehouse.load_dataset("science_graph.source_recipes")
        recipe_products = self.warehouse.load_dataset("science_graph.recipe_products")
        product_servings = self.warehouse.load_dataset("optimization.product_servings")
        aliases = self.warehouse.load_dataset("science_graph.ingredient_aliases")

        for _, row in breeds.iterrows():
            breed_id = str(row.get("breed_id", "")).strip()
            add_node(breed_id, "breed", str(row.get("breed_name", "")).strip(), f"biology.breeds:{breed_id}")

        for _, row in conditions.iterrows():
            condition_id = str(row.get("condition_id", "")).strip()
            add_node(
                condition_id,
                "condition",
                str(row.get("condition_name", "")).strip(),
                f"biology.conditions:{condition_id}",
            )

        for _, row in objectives.iterrows():
            objective_id = str(row.get("objective_id", "")).strip()
            add_node(
                objective_id,
                "objective",
                str(row.get("objective_name", "")).strip(),
                f"objectives.objectives:{objective_id}",
            )

        for _, row in mechanisms.iterrows():
            mechanism_id = str(row.get("mechanism_id", "")).strip()
            add_node(
                mechanism_id,
                "mechanism",
                str(row.get("mechanism_name", "")).strip(),
                f"mechanisms.mechanisms:{mechanism_id}",
            )

        for _, row in ingredients.iterrows():
            ingredient_id = str(row.get("ingredient_id", "")).strip()
            add_node(
                ingredient_id,
                "ingredient",
                str(row.get("ingredient_name", "")).strip(),
                f"nutrition.ingredients:{ingredient_id}",
            )

        for _, row in aliases.iterrows():
            alias_id = str(row.get("alias_ingredient_id", "")).strip()
            canonical_id = str(row.get("canonical_ingredient_id", "")).strip()
            add_node(alias_id, "ingredient", str(row.get("alias_name", "")).strip() or alias_id, f"science_graph.ingredient_aliases:{alias_id}")
            if canonical_id:
                add_edge(
                    edge_id=f"EDGE_ALIAS_{alias_id}_{canonical_id}",
                    source=alias_id,
                    target=canonical_id,
                    relationship_type="alias_of",
                    warehouse_row_id=f"science_graph.ingredient_aliases:{alias_id}",
                    scientific_quote=str(row.get("scientific_quote", "")),
                    paper_name=str(row.get("paper_name", "")),
                    paper_link=str(row.get("paper_link", "")),
                )

        for _, row in ingredient_sources.iterrows():
            source_id = str(row.get("source_id", "")).strip()
            ingredient_id = str(row.get("ingredient_id", "")).strip()
            add_node(source_id, "source", source_id, f"sources.ingredient_sources:{source_id}")
            add_edge(
                edge_id=f"EDGE_ING_SRC_{ingredient_id}_{source_id}",
                source=ingredient_id,
                target=source_id,
                relationship_type="ingredient_to_source",
                warehouse_row_id=f"sources.ingredient_sources:{source_id}:{ingredient_id}",
                scientific_quote=str(row.get("scientific_quote", "")),
                paper_name=str(row.get("paper_name", "")),
                paper_link=str(row.get("paper_link", "")),
            )

        for _, row in recipes.iterrows():
            recipe_id = str(row.get("recipe_id", "")).strip()
            add_node(recipe_id, "recipe", str(row.get("recipe_name", "")).strip(), f"recipes.recipes:{recipe_id}")

        for _, row in product_servings.iterrows():
            product_id = str(row.get("product_id", "")).strip()
            add_node(
                product_id,
                "product",
                str(row.get("product_name", "")).strip() or product_id,
                f"optimization.product_servings:{product_id}",
            )

        for _, row in trait_condition.iterrows():
            trait_name = str(row.get("trait_name", "")).strip()
            trait_value = str(row.get("trait_value", "")).strip()
            condition_id = str(row.get("condition_id", "")).strip()
            trait_id = f"TRAIT_{trait_name}_{trait_value}".upper().replace(" ", "_")
            add_node(trait_id, "trait", f"{trait_name}:{trait_value}", f"biology.trait_condition_associations:{row.get('fact_id', '')}")
            add_edge(
                edge_id=f"EDGE_TRAIT_COND_{row.get('fact_id', '')}",
                source=trait_id,
                target=condition_id,
                relationship_type="trait_to_condition",
                warehouse_row_id=f"biology.trait_condition_associations:{row.get('fact_id', '')}",
                scientific_quote=str(row.get("scientific_quote", "")),
                paper_name=str(row.get("paper_name", "")),
                paper_link=str(row.get("paper_link", "")),
            )

        for _, row in condition_objectives.iterrows():
            condition_id = str(row.get("condition_id", "")).strip()
            objective_id = str(row.get("objective_id", "")).strip()
            add_edge(
                edge_id=f"EDGE_COND_OBJ_{condition_id}_{objective_id}",
                source=condition_id,
                target=objective_id,
                relationship_type="condition_to_objective",
                warehouse_row_id=f"objectives.condition_objectives:{condition_id}:{objective_id}",
                scientific_quote=str(row.get("scientific_quote", "")),
                paper_name=str(row.get("paper_name", "")),
                paper_link=str(row.get("paper_link", "")),
            )

        for _, row in objective_mechanisms.iterrows():
            objective_id = str(row.get("objective_id", "")).strip()
            mechanism_id = str(row.get("mechanism_id", "")).strip()
            add_edge(
                edge_id=f"EDGE_OBJ_MEC_{objective_id}_{mechanism_id}",
                source=objective_id,
                target=mechanism_id,
                relationship_type="objective_to_mechanism",
                warehouse_row_id=f"objectives.objective_mechanisms:{objective_id}:{mechanism_id}",
                scientific_quote=str(row.get("quote", "")),
                paper_name=str(row.get("paper", "")),
                paper_link=str(row.get("link", "")),
            )

        for _, row in ingredient_mechanisms.iterrows():
            mechanism_id = str(row.get("mechanism_id", "")).strip()
            ingredient_id = str(row.get("ingredient_id", "")).strip()
            add_node(
                ingredient_id,
                "ingredient",
                ingredient_id,
                f"mechanisms.ingredient_mechanisms:{mechanism_id}:{ingredient_id}",
            )
            add_edge(
                edge_id=f"EDGE_MEC_ING_{mechanism_id}_{ingredient_id}",
                source=mechanism_id,
                target=ingredient_id,
                relationship_type="mechanism_to_ingredient",
                warehouse_row_id=f"mechanisms.ingredient_mechanisms:{mechanism_id}:{ingredient_id}",
                scientific_quote=str(row.get("scientific_quote", "")),
                paper_name=str(row.get("paper_name", "")),
                paper_link=str(row.get("paper_link", "")),
            )

        for _, row in source_recipes.iterrows():
            source_id = str(row.get("source_id", "")).strip()
            recipe_id = str(row.get("recipe_id", "")).strip()
            add_edge(
                edge_id=f"EDGE_SRC_RCP_{source_id}_{recipe_id}",
                source=source_id,
                target=recipe_id,
                relationship_type="source_to_recipe",
                warehouse_row_id=f"science_graph.source_recipes:{source_id}:{recipe_id}",
                scientific_quote=str(row.get("scientific_quote", "")),
                paper_name=str(row.get("paper_name", "")),
                paper_link=str(row.get("paper_link", "")),
            )

        for _, row in recipe_products.iterrows():
            recipe_id = str(row.get("recipe_id", "")).strip()
            product_id = str(row.get("product_id", "")).strip()
            add_edge(
                edge_id=f"EDGE_RCP_PROD_{recipe_id}_{product_id}",
                source=recipe_id,
                target=product_id,
                relationship_type="recipe_to_product",
                warehouse_row_id=f"science_graph.recipe_products:{recipe_id}:{product_id}",
                scientific_quote=str(row.get("scientific_quote", "")),
                paper_name=str(row.get("paper_name", "")),
                paper_link=str(row.get("paper_link", "")),
            )

        sorted_nodes = tuple(sorted(nodes.values(), key=lambda row: (row.node_type, row.node_id)))
        sorted_edges = tuple(sorted(edges, key=lambda row: row.edge_id))
        evidence_nodes, evidence_edges = _build_evidence(sorted_edges)
        return KnowledgeGraph(
            nodes=sorted_nodes,
            edges=sorted_edges,
            evidence_nodes=evidence_nodes,
            evidence_edges=evidence_edges,
        )


def _build_evidence(edges: tuple[ScientificEdge, ...]) -> tuple[tuple[EvidenceNode, ...], tuple[EvidenceEdge, ...]]:
    evidence_nodes: list[EvidenceNode] = []
    evidence_edges: list[EvidenceEdge] = []
    for edge in edges:
        evidence_id = f"EVD_{edge.edge_id}"
        evidence_nodes.append(
            EvidenceNode(
                evidence_id=evidence_id,
                warehouse_row_id=edge.warehouse_row_id,
                scientific_quote=edge.scientific_quote,
                paper_name=edge.paper_name,
                paper_link=edge.paper_link,
            )
        )
        evidence_edges.append(
            EvidenceEdge(
                evidence_edge_id=f"EEDGE_{edge.edge_id}",
                edge_id=edge.edge_id,
                evidence_id=evidence_id,
            )
        )
    return tuple(evidence_nodes), tuple(evidence_edges)
