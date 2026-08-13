"""6C — scientific ontology (condition + ingredient hierarchies)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Seed ontology — curated, extensible JSON
CONDITION_ONTOLOGY: dict[str, dict[str, Any]] = {
    "Hip Dysplasia": {
        "system": "Musculoskeletal",
        "class": "Joint Disease",
        "facets": ["Mobility", "Pain", "Inflammation"],
        "anatomy": ["Hip", "Coxofemoral joint"],
    },
    "Osteoarthritis": {
        "system": "Musculoskeletal",
        "class": "Joint Disease",
        "facets": ["Mobility", "Pain", "Inflammation", "Cartilage"],
        "anatomy": ["Joint"],
    },
    "Atopic Dermatitis": {
        "system": "Integumentary",
        "class": "Inflammatory Skin Disease",
        "facets": ["Pruritus", "Barrier", "Inflammation"],
        "anatomy": ["Skin"],
    },
    "Obesity": {
        "system": "Metabolic",
        "class": "Energy Balance Disorder",
        "facets": ["Adiposity", "Inflammation"],
        "anatomy": ["Systemic"],
    },
    "Anxiety": {
        "system": "Nervous",
        "class": "Behavioral Disorder",
        "facets": ["Stress", "Cognition"],
        "anatomy": ["CNS"],
    },
    "Heat Stress Syndrome": {
        "system": "Thermoregulatory",
        "class": "Environmental Stress",
        "facets": ["Heat", "Respiration"],
        "anatomy": ["Systemic"],
    },
}

INGREDIENT_ONTOLOGY: dict[str, dict[str, Any]] = {
    "EPA": {
        "parent": "Omega-3",
        "class": "Fatty Acid",
        "superclass": "Lipid",
        "domain": "Nutrient",
    },
    "DHA": {
        "parent": "Omega-3",
        "class": "Fatty Acid",
        "superclass": "Lipid",
        "domain": "Nutrient",
    },
    "Omega-3": {
        "parent": "Fatty Acid",
        "class": "Fatty Acid",
        "superclass": "Lipid",
        "domain": "Nutrient",
    },
    "Glucosamine": {
        "parent": "Aminosugar",
        "class": "Joint Nutraceutical",
        "superclass": "Nutraceutical",
        "domain": "Nutrient",
    },
    "Chondroitin Sulfate": {
        "parent": "Glycosaminoglycan",
        "class": "Joint Nutraceutical",
        "superclass": "Nutraceutical",
        "domain": "Nutrient",
    },
    "Probiotics": {
        "parent": "Microbiome Support",
        "class": "Live Microorganism",
        "superclass": "Biologic",
        "domain": "Nutrient",
    },
}


def condition_path(name: str) -> list[str]:
    meta = CONDITION_ONTOLOGY.get(name) or CONDITION_ONTOLOGY.get(name.title())
    if not meta:
        # fuzzy
        for k, v in CONDITION_ONTOLOGY.items():
            if k.lower() == name.lower():
                meta = v
                name = k
                break
    if not meta:
        return [name]
    path = [meta["system"], meta["class"], name]
    path.extend(meta.get("facets") or [])
    return path


def ingredient_path(name: str) -> list[str]:
    key = name
    meta = INGREDIENT_ONTOLOGY.get(name)
    if not meta:
        for k, v in INGREDIENT_ONTOLOGY.items():
            if k.lower() == name.lower():
                meta, key = v, k
                break
    if not meta:
        return [name]
    path = [meta.get("domain") or "Nutrient", meta.get("superclass") or "", meta.get("class") or "", meta.get("parent") or "", key]
    return [p for p in path if p]


def export_ontology_artifacts() -> dict[str, str]:
    cond_dir = ROOT / "ontology" / "condition_graph"
    ing_dir = ROOT / "ontology" / "ingredient_graph"
    anat = ROOT / "ontology" / "anatomy"
    phys = ROOT / "ontology" / "physiology"
    for d in (cond_dir, ing_dir, anat, phys):
        d.mkdir(parents=True, exist_ok=True)

    (cond_dir / "conditions.json").write_text(json.dumps(CONDITION_ONTOLOGY, indent=2), encoding="utf-8")
    (ing_dir / "ingredients.json").write_text(json.dumps(INGREDIENT_ONTOLOGY, indent=2), encoding="utf-8")

    # Flatten anatomy / physiology indices
    anatomy: dict[str, list[str]] = {}
    physiology: dict[str, list[str]] = {}
    for cond, meta in CONDITION_ONTOLOGY.items():
        for a in meta.get("anatomy") or []:
            anatomy.setdefault(a, []).append(cond)
        physiology.setdefault(meta["system"], []).append(cond)
        for f in meta.get("facets") or []:
            physiology.setdefault(f, []).append(cond)
    (anat / "anatomy_index.json").write_text(json.dumps(anatomy, indent=2), encoding="utf-8")
    (phys / "physiology_index.json").write_text(json.dumps(physiology, indent=2), encoding="utf-8")

    # Mermaid snapshot
    lines = ["# Condition Ontology", "", "```mermaid", "graph TD"]
    for cond, meta in CONDITION_ONTOLOGY.items():
        sys = meta["system"].replace(" ", "_")
        cls = meta["class"].replace(" ", "_")
        c = cond.replace(" ", "_")
        lines.append(f"  {sys} --> {cls}")
        lines.append(f"  {cls} --> {c}")
        for f in meta.get("facets") or []:
            lines.append(f"  {c} --> {f.replace(' ', '_')}")
    lines += ["```", ""]
    md = cond_dir / "CONDITION_ONTOLOGY.md"
    md.write_text("\n".join(lines), encoding="utf-8")

    return {
        "conditions": str(cond_dir / "conditions.json"),
        "ingredients": str(ing_dir / "ingredients.json"),
        "mermaid": str(md),
    }


def ontology_summary() -> dict[str, Any]:
    return {
        "conditions": len(CONDITION_ONTOLOGY),
        "ingredients": len(INGREDIENT_ONTOLOGY),
        "systems": sorted({v["system"] for v in CONDITION_ONTOLOGY.values()}),
    }
