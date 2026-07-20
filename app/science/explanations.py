"""Human / developer / scientific explanations — deterministic templates."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DeveloperExplanation:
    title: str
    expression: str
    inputs: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScientificExplanation:
    title: str
    narrative: str
    paper_id: str | None = None
    paper_url: str | None = None
    observed_effect: str | None = None
    population: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Catalog of known formula narratives (no invented modifiers beyond locked math)
_FORMULA_SCIENCE = {
    "RISK_V2_1": {
        "human": "Breed and trait prevalences are combined with interaction and benefit modifiers to rank conditions.",
        "developer": DeveloperExplanation(
            title="Condition Risk Ranking",
            expression="clamp(base_prevalence × interactions × benefits [× 1.05 if senior])",
            inputs={"tables": ["breed_conditions", "trait_*_conditions", "trait_interactions", "trait_benefits"]},
            notes="Wrapped compute_risks; INTERACTION_MIN/MAX clamp 0.80–1.20",
        ),
        "scientific": ScientificExplanation(
            title="Epidemiologic prevalence ranking",
            narrative="Observed condition prevalences in breed and trait cohorts are adjusted by documented trait interactions and protective benefits.",
        ),
    },
    "NUTRIENT_TARGET_V2_1": {
        "human": "Ranked conditions map to nutrient/ingredient daily targets from the evidence tables.",
        "developer": DeveloperExplanation(
            title="Condition → Nutrient Targets",
            expression="map_ingredients(risks, weight_kg, repo)",
            inputs={"tables": ["condition_ingredients", "ingredient_evidence"]},
        ),
        "scientific": ScientificExplanation(
            title="Nutritional intervention mapping",
            narrative="Ingredients linked to conditions in the clinical nutrition CSVs become dose targets for the dog's weight.",
        ),
    },
    "PACKAGE_OPTIMIZER_V2_1": {
        "human": "Products are scored for coverage of nutrient targets across package tiers.",
        "developer": DeveloperExplanation(
            title="Tier Package Optimizer",
            expression="coverage − surplus + clinical_function + evidence + cost weights",
            inputs={"parameters": ["score_weights.*"]},
        ),
        "scientific": ScientificExplanation(
            title="Commercial fulfillment",
            narrative="Inventory components are matched to ingredient targets; packages balance coverage and cost by tier.",
        ),
    },
}


def build_formula_explanations(formula_id: str, *, extras: dict[str, Any] | None = None) -> dict[str, Any]:
    base = _FORMULA_SCIENCE.get(formula_id, {})
    human = base.get("human") or f"Formula {formula_id}"
    dev = base.get("developer")
    sci = base.get("scientific")
    out = {
        "formula_id": formula_id,
        "human": human,
        "developer": dev.to_dict() if isinstance(dev, DeveloperExplanation) else {"title": formula_id, "expression": formula_id},
        "scientific": sci.to_dict() if isinstance(sci, ScientificExplanation) else {"title": formula_id, "narrative": human},
    }
    if extras:
        out["runtime"] = extras
    return out


def build_recommendation_chain(
    *,
    condition: str,
    breed: str | None = None,
    ingredient: str | None = None,
    nutrient: str | None = None,
    food: str | None = None,
    product: str | None = None,
    paper: dict[str, Any] | None = None,
    graph_paths: list[list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """
    UI-ready explanation object:

    Joint Health → Evidence → Hip Dysplasia → Breed → Omega-3 → Food → Product
    """
    steps: list[dict[str, Any]] = [{"kind": "condition", "label": condition}]
    if breed:
        steps.append({"kind": "breed", "label": breed})
    if ingredient:
        steps.append({"kind": "ingredient", "label": ingredient})
    if nutrient:
        steps.append({"kind": "nutrient", "label": nutrient})
    if food:
        steps.append({"kind": "food", "label": food})
    if product:
        steps.append({"kind": "product", "label": product})
    if paper:
        steps.append(
            {
                "kind": "paper",
                "label": paper.get("title") or paper.get("source_name") or paper.get("paper_id"),
                "url": paper.get("url") or paper.get("source_url"),
                "paper_id": paper.get("paper_id"),
            }
        )
    return {
        "condition": condition,
        "chain": steps,
        "graph_paths": graph_paths or [],
        "render": " → ".join(str(s.get("label") or "") for s in steps if s.get("label")),
    }
