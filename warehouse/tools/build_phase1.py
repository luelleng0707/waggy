#!/usr/bin/env python3
"""Phase 1 warehouse scaffolding - read-only over data/, writes warehouse/ only."""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
WH = ROOT / "warehouse"
APP = ROOT / "app"

# ---------------------------------------------------------------------------
# Consumer / purpose metadata (from Phase 0 + DATA_CONSUMERS)
# ---------------------------------------------------------------------------

REQUIRED = {
    "BREEDS.csv",
    "BREED_ALIASES.csv",
    "BREED_CONDITIONS.csv",
    "SIZE_CONDITIONS.csv",
    "BODYTYPE_CONDITIONS.csv",
    "COATTYPE_CONDITIONS.csv",
    "ENERGY_CONDITIONS.csv",
    "SKULLTYPE_CONDITIONS.csv",
    "FUNCTIONGROUP_CONDITIONS.csv",
    "WEAKNESSGROUP_CONDITIONS.csv",
    "CLIMATE_CONDITIONS.csv",
    "LIFESPAN_CONDITIONS.csv",
    "TRAIT_INTERACTIONS.csv",
    "TRAIT_BENEFITS.csv",
    "MIXED_BREED_MATRIX.csv",
    "TRAIT_PURPOSES.csv",
    "ENVIRONMENTAL_MATRICES.csv",
    "CONDITION_INGREDIENTS.csv",
    "PRODUCT_CATALOG.csv",
    "PRODUCT_PRICING.csv",
    "PRODUCT_COMPONENTS.csv",
    "PRODUCT_FEEDING_RULES.csv",
    "PRODUCT_FUNCTIONS.csv",
    "EXT_SUPPLEMENTS.csv",
    "EXT_TREATS_BAKERY.csv",
    "PACKAGE_TIERS.csv",
    "INGREDIENT_ALIASES.csv",
    "CONDITION_ACTIVITIES.csv",
    "NUTRIENT_PRIORITIES.csv",
    "INGREDIENT_EVIDENCE.csv",
    "INGREDIENT_MECHANISMS.csv",
    "NATURAL_FOOD_SOURCES.csv",
}

PARTIAL = {
    "TRAIT_ATTRIBUTE_EXPLANATIONS.csv",
    "TRAIT_CONTRIBUTION_WEIGHTS.csv",
    "CLINICAL_RISK_TIMELINE.csv",
    "CLINICAL_EVIDENCE_BASE.csv",
    "ACTIVITY_PRESCRIPTION_RULES.csv",
    "GROOMING_OBSERVATION_DEFS.csv",
    "INGREDIENT_NUTRIENT_ESTIMATES.csv",
}

UNUSED = {
    "MIXED_BREED_INTERACTIONS.csv",
    "ACTIVITY_EVIDENCE.csv",
    "CONDITION_PROTOCOLS.csv",
    "PRODUCT_DEFAULTS.csv",
    "STAPLE_FOOD.csv",
    "TREATS.csv",
}

PURPOSE = {
    "BREEDS.csv": "Canonical breed identity + biological trait defaults",
    "BREED_ALIASES.csv": "Breed name normalization aliases",
    "BREED_CONDITIONS.csv": "Breed -> condition prevalence + citations",
    "SIZE_CONDITIONS.csv": "Body-size trait -> condition prevalence",
    "BODYTYPE_CONDITIONS.csv": "Body-type trait -> condition prevalence",
    "COATTYPE_CONDITIONS.csv": "Coat-type trait -> condition prevalence",
    "ENERGY_CONDITIONS.csv": "Energy trait -> condition prevalence",
    "SKULLTYPE_CONDITIONS.csv": "Skull-type trait -> condition prevalence",
    "FUNCTIONGROUP_CONDITIONS.csv": "Function-group trait -> condition prevalence",
    "WEAKNESSGROUP_CONDITIONS.csv": "Weakness-group trait -> condition prevalence",
    "CLIMATE_CONDITIONS.csv": "Climate trait -> condition prevalence",
    "LIFESPAN_CONDITIONS.csv": "Lifespan band -> condition prevalence",
    "TRAIT_INTERACTIONS.csv": "Multiplicative trait pair risk modifiers",
    "TRAIT_BENEFITS.csv": "Subtractive trait benefit modifiers (risk)",
    "MIXED_BREED_MATRIX.csv": "Cross-breed condition interaction multipliers",
    "MIXED_BREED_INTERACTIONS.csv": "Mixed-breed interaction notes (unused by engine)",
    "TRAIT_PURPOSES.csv": "Trait purpose narratives for biological stage",
    "ENVIRONMENTAL_MATRICES.csv": "Environment x trait guidance matrices",
    "TRAIT_ATTRIBUTE_EXPLANATIONS.csv": "Trait attribute copy for reports",
    "TRAIT_CONTRIBUTION_WEIGHTS.csv": "Report contribution weight metadata",
    "CLINICAL_RISK_TIMELINE.csv": "Age/timeline risk narrative for reports",
    "CONDITION_ACTIVITIES.csv": "Condition -> activity recommendations",
    "ACTIVITY_PRESCRIPTION_RULES.csv": "Activity prescription rules (reports)",
    "ACTIVITY_EVIDENCE.csv": "Activity evidence citations (unused by engine)",
    "GROOMING_OBSERVATION_DEFS.csv": "Grooming observation definitions (reports)",
    "CONDITION_INGREDIENTS.csv": "Condition -> nutrient targets / ingredients (dual home)",
    "CONDITION_PROTOCOLS.csv": "Condition protocols (unused by engine)",
    "NUTRIENT_PRIORITIES.csv": "Nutrient priority ordering for assembly",
    "CLINICAL_EVIDENCE_BASE.csv": "Clinical evidence base for reports",
    "INGREDIENT_EVIDENCE.csv": "Ingredient evidence citations (dual home)",
    "INGREDIENT_MECHANISMS.csv": "Ingredient mechanism narratives",
    "NATURAL_FOOD_SOURCES.csv": "Natural food sources for nutrients",
    "INGREDIENT_ALIASES.csv": "Ingredient name aliases for coverage matching",
    "INGREDIENT_NUTRIENT_ESTIMATES.csv": "Ingredient nutrient estimates (opt-in)",
    "PRODUCT_CATALOG.csv": "Product identity catalog",
    "PRODUCT_PRICING.csv": "Product pricing",
    "PRODUCT_COMPONENTS.csv": "Product composition / active ingredients",
    "PRODUCT_FEEDING_RULES.csv": "Feeding amount rules by size/weight",
    "PRODUCT_FUNCTIONS.csv": "Product functional tags",
    "EXT_SUPPLEMENTS.csv": "External supplement SKUs",
    "EXT_TREATS_BAKERY.csv": "External treat/bakery SKUs",
    "PACKAGE_TIERS.csv": "Package tier definitions & staple rules",
    "PRODUCT_DEFAULTS.csv": "Product defaults (unused by engine)",
    "STAPLE_FOOD.csv": "Unmanifested staple food table",
    "TREATS.csv": "Unmanifested treats table",
}

FORMULAS = {
    "BREEDS.csv": ["run_biological_stage", "compute_risk / RISK_V2_1"],
    "BREED_ALIASES.csv": ["normalize_breed"],
    "BREED_CONDITIONS.csv": ["compute_risk", "epidemiology stage"],
    "SIZE_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "BODYTYPE_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "COATTYPE_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "ENERGY_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "SKULLTYPE_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "FUNCTIONGROUP_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "WEAKNESSGROUP_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "CLIMATE_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "LIFESPAN_CONDITIONS.csv": ["lookup_trait_prevalence -> compute_risk"],
    "TRAIT_INTERACTIONS.csv": ["apply_trait_interactions -> compute_risk"],
    "TRAIT_BENEFITS.csv": ["apply_trait_benefits -> compute_risk"],
    "MIXED_BREED_MATRIX.csv": ["apply_mixed_breed_matrix -> compute_risk"],
    "CONDITION_INGREDIENTS.csv": ["map_ingredients", "nutrition stage", "package_optimizer"],
    "PRODUCT_CATALOG.csv": ["build_packages / package_optimizer"],
    "PRODUCT_PRICING.csv": ["package_optimizer cost"],
    "PRODUCT_COMPONENTS.csv": ["coverage matching / package_optimizer"],
    "PRODUCT_FEEDING_RULES.csv": ["feeding amount / package_optimizer"],
    "PRODUCT_FUNCTIONS.csv": ["product tagging / package_optimizer"],
    "EXT_SUPPLEMENTS.csv": ["package_optimizer"],
    "EXT_TREATS_BAKERY.csv": ["package_optimizer"],
    "PACKAGE_TIERS.csv": ["staple selection / package_optimizer"],
    "INGREDIENT_ALIASES.csv": ["coverage matching"],
    "CONDITION_ACTIVITIES.csv": ["management / assembler"],
    "NUTRIENT_PRIORITIES.csv": ["response_assembler"],
    "INGREDIENT_EVIDENCE.csv": ["response_assembler evidence"],
    "INGREDIENT_MECHANISMS.csv": ["response_assembler"],
    "NATURAL_FOOD_SOURCES.csv": ["response_assembler"],
    "TRAIT_PURPOSES.csv": ["run_biological_stage"],
    "ENVIRONMENTAL_MATRICES.csv": ["run_biological_stage"],
}

APIS = {
    "required": [
        "POST /api/v1/analyze",
        "POST /api/v1/ppie/assess",
        "POST /api/v1/clinical-report",
    ],
    "partial": [
        "POST /api/v1/clinical-report",
        "GET /api/v1/store/* (products)",
        "GET /api/v1/evidence/*",
    ],
    "unused": [],
}

DEBUG = "Validation Console /debug/calculation?debug=1 (repository browser + formula_execution)"

TRAIT_CONDITION_FILES = {
    "SIZE_CONDITIONS.csv": "size",
    "BODYTYPE_CONDITIONS.csv": "body_type",
    "COATTYPE_CONDITIONS.csv": "coat_type",
    "ENERGY_CONDITIONS.csv": "energy",
    "SKULLTYPE_CONDITIONS.csv": "skull_type",
    "FUNCTIONGROUP_CONDITIONS.csv": "function_group",
    "WEAKNESSGROUP_CONDITIONS.csv": "weakness_group",
    "CLIMATE_CONDITIONS.csv": "climate",
    "LIFESPAN_CONDITIONS.csv": "lifespan",
}

WAREHOUSE_MAP = {
    "BREEDS.csv": {"new": "reference/breeds.csv", "transform": "identity + FK to trait dims"},
    "BREED_ALIASES.csv": {"new": "runtime/aliases.csv", "transform": "alias_type=breed"},
    "BREED_CONDITIONS.csv": {"new": "science/breed_condition_risk.csv", "transform": "citation -> paper_id"},
    "SIZE_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=size; citation -> paper_id",
    },
    "BODYTYPE_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=body_type; citation -> paper_id",
    },
    "COATTYPE_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=coat_type; citation -> paper_id",
    },
    "ENERGY_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=energy; citation -> paper_id",
    },
    "SKULLTYPE_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=skull_type; citation -> paper_id",
    },
    "FUNCTIONGROUP_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=function_group; citation -> paper_id",
    },
    "WEAKNESSGROUP_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=weakness_group; citation -> paper_id",
    },
    "CLIMATE_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=climate; citation -> paper_id",
    },
    "LIFESPAN_CONDITIONS.csv": {
        "new": "science/trait_condition_risk.csv",
        "transform": "trait_category=lifespan; citation -> paper_id",
    },
    "TRAIT_INTERACTIONS.csv": {"new": "science/mixed_trait_interactions.csv", "transform": "rename; keep multipliers"},
    "TRAIT_BENEFITS.csv": {"new": "science/prevention_effectiveness.csv", "transform": "benefit rows; paper_id"},
    "MIXED_BREED_MATRIX.csv": {"new": "science/mixed_trait_interactions.csv", "transform": "scope=breed_pair"},
    "MIXED_BREED_INTERACTIONS.csv": {"new": "science/mixed_trait_interactions.csv", "transform": "optional; currently unused"},
    "CONDITION_INGREDIENTS.csv": {
        "new": "science/nutrient_targets.csv (+ ingredient_evidence)",
        "transform": "dose->canonical units; citation->paper_id",
    },
    "INGREDIENT_EVIDENCE.csv": {"new": "science/ingredient_evidence.csv", "transform": "citation->paper_id"},
    "INGREDIENT_MECHANISMS.csv": {"new": "science/ingredient_evidence.csv", "transform": "mechanism narrative cols"},
    "NATURAL_FOOD_SOURCES.csv": {"new": "science/ingredient_food_sources.csv", "transform": "identity"},
    "INGREDIENT_NUTRIENT_ESTIMATES.csv": {"new": "science/food_nutrients.csv", "transform": "units->canonical"},
    "INGREDIENT_ALIASES.csv": {"new": "runtime/aliases.csv", "transform": "alias_type=ingredient"},
    "NUTRIENT_PRIORITIES.csv": {"new": "runtime/parameter_defaults.csv", "transform": "param_group=nutrient_priority"},
    "PRODUCT_CATALOG.csv": {"new": "science/product_composition.csv (catalog half)", "transform": "split identity vs composition"},
    "PRODUCT_COMPONENTS.csv": {"new": "science/product_composition.csv", "transform": "composition rows"},
    "PRODUCT_PRICING.csv": {"new": "runtime/parameter_defaults.csv", "transform": "param_group=pricing"},
    "PRODUCT_FEEDING_RULES.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=feeding"},
    "PRODUCT_FUNCTIONS.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=product_function"},
    "EXT_SUPPLEMENTS.csv": {"new": "science/product_composition.csv", "transform": "source=ext_supplements"},
    "EXT_TREATS_BAKERY.csv": {"new": "science/product_composition.csv", "transform": "source=ext_treats"},
    "PACKAGE_TIERS.csv": {"new": "runtime/parameter_defaults.csv", "transform": "param_group=package_tier"},
    "CONDITION_ACTIVITIES.csv": {"new": "science/prevention_effectiveness.csv", "transform": "prevention_type=activity"},
    "ACTIVITY_PRESCRIPTION_RULES.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=activity_rx"},
    "ACTIVITY_EVIDENCE.csv": {"new": "reference/papers.csv (+ prevention)", "transform": "unused today"},
    "TRAIT_PURPOSES.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=trait_purpose"},
    "ENVIRONMENTAL_MATRICES.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=environment"},
    "TRAIT_ATTRIBUTE_EXPLANATIONS.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=trait_explain"},
    "TRAIT_CONTRIBUTION_WEIGHTS.csv": {"new": "runtime/parameter_defaults.csv", "transform": "param_group=report_weights"},
    "CLINICAL_RISK_TIMELINE.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=risk_timeline"},
    "CLINICAL_EVIDENCE_BASE.csv": {"new": "reference/papers.csv", "transform": "normalize into papers"},
    "GROOMING_OBSERVATION_DEFS.csv": {"new": "runtime/lookup_maps.csv", "transform": "map_type=grooming"},
    "CONDITION_PROTOCOLS.csv": {"new": "science/prevention_effectiveness.csv", "transform": "unused today"},
    "PRODUCT_DEFAULTS.csv": {"new": "runtime/parameter_defaults.csv", "transform": "unused today"},
    "STAPLE_FOOD.csv": {"new": "reference/foods.csv", "transform": "unmanifested; inventory only"},
    "TREATS.csv": {"new": "reference/foods.csv", "transform": "unmanifested; inventory only"},
}

SCHEMA = {
    "reference/breeds.csv": [
        "breed_id",
        "breed",
        "size",
        "body_type",
        "coat_type",
        "energy",
        "skull_type",
        "function",
        "climate",
        "origin",
        "lifespan_band",
        "notes",
    ],
    "reference/traits.csv": ["trait_id", "trait_category", "trait_value", "description"],
    "reference/conditions.csv": ["condition_id", "condition", "system", "notes"],
    "reference/ingredients.csv": ["ingredient_id", "ingredient", "canonical_name", "notes"],
    "reference/foods.csv": ["food_id", "food", "food_type", "notes"],
    "reference/nutrients.csv": ["nutrient_id", "nutrient", "canonical_unit", "notes"],
    "reference/activities.csv": ["activity_id", "activity", "category", "notes"],
    "reference/climates.csv": ["climate_id", "climate", "notes"],
    "reference/body_sizes.csv": ["body_size_id", "body_size", "notes"],
    "reference/body_types.csv": ["body_type_id", "body_type", "notes"],
    "reference/coat_types.csv": ["coat_type_id", "coat_type", "notes"],
    "reference/skull_types.csv": ["skull_type_id", "skull_type", "notes"],
    "reference/prevention_methods.csv": ["prevention_id", "method", "category", "notes"],
    "reference/papers.csv": [
        "paper_id",
        "title",
        "authors",
        "journal",
        "year",
        "doi",
        "pmid",
        "url",
        "sample_size",
        "study_type",
        "country",
        "species",
        "quote",
    ],
    "science/breed_condition_risk.csv": [
        "breed",
        "condition",
        "population",
        "observed_percent",
        "paper_id",
    ],
    "science/trait_condition_risk.csv": [
        "trait_category",
        "trait_value",
        "condition",
        "population",
        "observed_percent",
        "paper_id",
    ],
    "science/mixed_trait_interactions.csv": [
        "interaction_type",
        "left_key",
        "right_key",
        "condition",
        "multiplier",
        "paper_id",
        "notes",
    ],
    "science/prevention_effectiveness.csv": [
        "prevention_id",
        "condition",
        "trait_or_activity",
        "effect_type",
        "effect_value",
        "paper_id",
    ],
    "science/ingredient_evidence.csv": [
        "ingredient",
        "condition",
        "mechanism",
        "evidence_level",
        "paper_id",
    ],
    "science/food_nutrients.csv": [
        "food",
        "nutrient",
        "amount",
        "unit",
        "canonical_amount",
        "canonical_unit",
        "paper_id",
    ],
    "science/nutrient_targets.csv": [
        "condition",
        "nutrient_or_ingredient",
        "target_amount",
        "unit",
        "canonical_amount",
        "canonical_unit",
        "priority",
        "paper_id",
    ],
    "science/ingredient_food_sources.csv": [
        "ingredient",
        "food",
        "notes",
        "paper_id",
    ],
    "science/product_composition.csv": [
        "product_id",
        "product_name",
        "component",
        "amount",
        "unit",
        "canonical_amount",
        "canonical_unit",
        "source_table",
    ],
    "runtime/unit_conversion.csv": ["unit", "canonical_unit", "multiplier", "notes"],
    "runtime/aliases.csv": ["alias_type", "alias", "canonical", "notes"],
    "runtime/parameter_defaults.csv": ["param_group", "key", "value", "unit", "notes"],
    "runtime/lookup_maps.csv": ["map_type", "key", "value", "meta_json"],
}

UNIT_ROWS = [
    ["mg", "mg", "1", "mass base"],
    ["g", "mg", "1000", ""],
    ["kg", "mg", "1000000", ""],
    ["ug", "mg", "0.001", "microgram (ascii)"],
    ["mcg", "mg", "0.001", "microgram alias"],
    ["IU", "IU", "1", "pass-through until nutrient-specific"],
    ["IU Vitamin D", "IU", "1", ""],
    ["kcal", "kcal", "1", ""],
    ["kcal/kg", "kcal/kg", "1", ""],
    ["mg/kg", "mg/kg", "1", ""],
    ["mg/100g", "mg/100g", "1", ""],
    ["g/100g", "mg/100g", "1000", ""],
    ["%", "fraction", "0.01", "percent to fraction"],
    ["percent", "fraction", "0.01", ""],
    ["fraction", "fraction", "1", ""],
]


def read_csv_meta(path: Path) -> dict:
    with path.open(encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        rows = list(reader)
    return {"header": header, "row_count": len(rows), "rows": rows}


def grep_python_refs(stem: str, filename: str) -> list[str]:
    """Find Python files mentioning table stem or filename."""
    hits: set[str] = set()
    patterns = [
        re.escape(filename),
        re.escape(stem),
        re.escape(stem.lower()),
        re.escape(stem.replace("_", " ").title()),
    ]
    # also common manifest keys
    key = stem.lower()
    patterns.append(re.escape(key))
    for py in APP.rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                hits.add(py.relative_to(ROOT).as_posix())
                break
    return sorted(hits)


def status_for(name: str) -> str:
    if name in UNUSED:
        return "unused"
    if name in PARTIAL:
        return "partially_required"
    if name in REQUIRED:
        return "required"
    return "partially_required"


def dependency_graph(name: str) -> list[str]:
    """CSV -> pipeline stage chain for docs."""
    if name in TRAIT_CONDITION_FILES or name == "BREED_CONDITIONS.csv":
        return [
            name,
            "repository.trait_condition_tables / breed_conditions",
            "health_risk.compute_risk (RISK_V2_1)",
            "epidemiology stage",
            "ingredient_engine.map_ingredients",
            "package_optimizer.build_packages",
            "response_assembler",
            "Clinical Assessment / analyze JSON",
            "Validation Console",
        ]
    if name.startswith("PRODUCT") or name.startswith("EXT_") or name == "PACKAGE_TIERS.csv":
        return [
            name,
            "repository product accessors",
            "package_optimizer",
            "stages/optimization",
            "response_assembler",
            "store/catalog APIs",
            "Validation Console",
        ]
    if "INGREDIENT" in name or name == "CONDITION_INGREDIENTS.csv" or name == "NUTRIENT_PRIORITIES.csv":
        return [
            name,
            "repository condition_ingredients / evidence",
            "ingredient_engine / nutrition stage",
            "package_optimizer coverage",
            "response_assembler",
            "Clinical Assessment",
            "Validation Console",
        ]
    if name == "BREEDS.csv" or name == "BREED_ALIASES.csv":
        return [
            name,
            "run_biological_stage",
            "traits on dog profile",
            "compute_risk",
            "ingredient_engine",
            "package_optimizer",
            "response_assembler",
            "Clinical Assessment",
            "Validation Console",
        ]
    if name in ("TRAIT_INTERACTIONS.csv", "TRAIT_BENEFITS.csv", "MIXED_BREED_MATRIX.csv"):
        return [
            name,
            "health_risk modifiers",
            "compute_risk",
            "downstream nutrition + packages",
            "response_assembler",
            "Validation Console",
        ]
    if status_for(name) == "unused":
        return [name, "(loaded by repository if manifested)", "(no engine formula)", "Validation Console browser only"]
    return [
        name,
        "repository / report_generator",
        "clinical_report_builder (if report path)",
        "response_assembler (if wired)",
        "Validation Console",
    ]


def write_schema_csvs() -> None:
    for rel, cols in SCHEMA.items():
        path = WH / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            if rel == "runtime/unit_conversion.csv":
                for row in UNIT_ROWS:
                    w.writerow(row)


def extract_conditions(meta_by_file: dict[str, dict]) -> dict:
    """Find condition strings appearing across tables."""
    condition_cols = ("condition", "Condition", "CONDITION", "condition_name")
    locations: dict[str, list[str]] = defaultdict(list)
    for name, meta in meta_by_file.items():
        header = meta["header"]
        col = None
        for c in condition_cols:
            if c in header:
                col = header.index(c)
                break
        # fuzzy
        if col is None:
            for i, h in enumerate(header):
                if "condition" in h.lower():
                    col = i
                    break
        if col is None:
            continue
        for row in meta["rows"]:
            if col < len(row) and row[col].strip():
                locations[row[col].strip()].append(name)
    # duplicates = appear in 2+ files
    dups = {
        cond: sorted(set(files))
        for cond, files in locations.items()
        if len(set(files)) >= 2
    }
    return {
        "summary": {
            "unique_conditions_seen": len(locations),
            "conditions_in_multiple_tables": len(dups),
        },
        "duplicates": [
            {"condition": c, "tables": files, "table_count": len(files)}
            for c, files in sorted(dups.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
    }


def find_unused_columns(meta_by_file: dict[str, dict], py_refs: dict[str, list[str]]) -> dict:
    """Heuristic: columns never mentioned in Python + known dead names."""
    known_dead = {
        "confidence_score",
        "estimated_prevalence",
        "fake_prevalence",
        "internal_id",
        "legacy_alias",
        "csv_version",
        "row_hash",
        "imported_at",
        "source_file_legacy",
    }
    # Collect all Python text once
    py_blob = ""
    for py in APP.rglob("*.py"):
        try:
            py_blob += py.read_text(encoding="utf-8", errors="replace") + "\n"
        except OSError:
            pass

    findings = []
    for name, meta in sorted(meta_by_file.items()):
        for col in meta["header"]:
            cl = col.strip()
            if not cl:
                continue
            mentioned = cl in py_blob or cl.lower() in py_blob.lower()
            # also check snake variants
            snake = re.sub(r"[^a-z0-9]+", "_", cl.lower()).strip("_")
            if snake and snake in py_blob.lower():
                mentioned = True
            if cl.lower() in known_dead or (not mentioned and status_for(name) == "unused"):
                findings.append(
                    {
                        "file": name,
                        "column": cl,
                        "reason": (
                            "known_dead_name"
                            if cl.lower() in known_dead
                            else "file_unused_by_engine"
                            if status_for(name) == "unused"
                            else "no_python_string_match"
                        ),
                        "python_references": py_refs.get(name, []),
                        "safe_to_delete": status_for(name) == "unused" or cl.lower() in known_dead,
                        "replacement": None if cl.lower() not in ("estimated_prevalence", "fake_prevalence") else "observed_percent",
                    }
                )
            elif not mentioned:
                # soft unused - only flag if looks metadata-ish
                if any(x in cl.lower() for x in ("confidence", "legacy", "internal", "version", "hash", "fake", "estimated")):
                    findings.append(
                        {
                            "file": name,
                            "column": cl,
                            "reason": "metadata_like_unreferenced",
                            "python_references": py_refs.get(name, []),
                            "safe_to_delete": False,
                            "replacement": None,
                        }
                    )
    return {"summary": {"count": len(findings)}, "columns": findings}


def coverage_report(meta_by_file: dict) -> dict:
    """Formula -> CSV -> paper linkage gaps (design-time)."""
    chains = [
        {
            "formula": "RISK_V2_1 / compute_risk",
            "csv": "BREED_CONDITIONS + 9x *_CONDITIONS",
            "row_key": "breed|traits x condition",
            "paper_link": "inline citation columns today; warehouse -> paper_id",
            "calculation": "base prevalence x trait interactions x benefits x mixed matrix",
            "output": "risk_percent / ranked conditions",
            "gaps": ["citations not normalized to papers.csv", "9 isomorphic trait tables"],
        },
        {
            "formula": "map_ingredients",
            "csv": "CONDITION_INGREDIENTS (sci+prev merge)",
            "row_key": "condition x ingredient/nutrient",
            "paper_link": "partial via INGREDIENT_EVIDENCE",
            "calculation": "dose targets + priority",
            "output": "nutrition targets",
            "gaps": ["dual folder homes", "units not canonicalized"],
        },
        {
            "formula": "package_optimizer.build_packages",
            "csv": "PRODUCT_* + PACKAGE_TIERS + EXT_* + INGREDIENT_ALIASES",
            "row_key": "product x component coverage",
            "paper_link": "none (commercial)",
            "calculation": "coverage score + tier staple + cost",
            "output": "packages",
            "gaps": ["STAPLE_FOOD/TREATS unmanifested"],
        },
        {
            "formula": "response_assembler",
            "csv": "NUTRIENT_PRIORITIES, NATURAL_FOOD_SOURCES, mechanisms, activities",
            "row_key": "assembled sections",
            "paper_link": "evidence tables + CLINICAL_EVIDENCE_BASE (reports)",
            "calculation": "assembly only (no new risk math)",
            "output": "analyze / clinical JSON",
            "gaps": ["report-only tables not in risk path"],
        },
    ]
    missing = []
    for c in chains:
        for g in c["gaps"]:
            missing.append({"formula": c["formula"], "gap": g})
    # paper coverage sample: count citation-like columns
    citation_files = []
    for name, meta in meta_by_file.items():
        cite_cols = [h for h in meta["header"] if any(k in h.lower() for k in ("cite", "journal", "doi", "pmid", "url", "author", "quote", "reference", "paper", "study"))]
        if cite_cols:
            citation_files.append({"file": name, "citation_columns": cite_cols, "rows": meta["row_count"]})
    return {
        "formula_chains": chains,
        "gaps": missing,
        "citation_column_inventory": citation_files,
        "warehouse_target": "Every science row carries paper_id -> reference/papers.csv",
        "status": "Phase 1 inventory only - engine still uses data/",
    }


def analysis_stem_for(path: Path) -> str:
    """Unique markdown stem; dual-home CSVs share filenames."""
    rel = path.relative_to(DATA).as_posix()
    if path.name in ("CONDITION_INGREDIENTS.csv", "INGREDIENT_EVIDENCE.csv") and "/" in rel:
        parent = path.parent.name
        return f"{path.stem}__{parent}"
    return path.stem


def write_csv_analysis(
    name: str,
    meta: dict,
    py_refs: list[str],
    status: str,
    *,
    rel_path: str,
    analysis_stem: str,
) -> None:
    out = WH / "generated" / "csv_analysis" / (analysis_stem + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    mapping = WAREHOUSE_MAP.get(name, {"new": "(TBD)", "transform": "(TBD)"})
    formulas = FORMULAS.get(name, ["(none / report-only / unused)"])
    graph = dependency_graph(name)
    unused_cols = []
    # empty columns heuristic
    if meta["rows"] and meta["header"]:
        for i, col in enumerate(meta["header"]):
            vals = [r[i] for r in meta["rows"] if i < len(r) and str(r[i]).strip()]
            if not vals:
                unused_cols.append(col)

    lines = [
        f"# {name}",
        "",
        f"**Source path:** `{rel_path}`",
        "",
        "## Purpose",
        "",
        PURPOSE.get(name, "(see migration_report)"),
        "",
        "## Columns",
        "",
        "| # | Column |",
        "|---|--------|",
    ]
    for i, c in enumerate(meta["header"], 1):
        lines.append(f"| {i} | `{c}` |")
    lines += [
        "",
        "## Meaning",
        "",
        f"Rows: **{meta['row_count']}**. Column count: **{len(meta['header'])}**.",
        "",
        f"Status: **{status}**.",
        "",
        "## Who reads it",
        "",
        "### Python files",
        "",
    ]
    if py_refs:
        for p in py_refs:
            lines.append(f"- `{p}`")
    else:
        lines.append("- *(no direct filename/stem matches in app/)*")
    lines += [
        "",
        "## Formula",
        "",
    ]
    for f in formulas:
        lines.append(f"- `{f}`")
    lines += [
        "",
        "## Output",
        "",
        "- Consumed into analyze/assess/clinical JSON and/or Validation Console.",
        "",
        "## Dependency graph",
        "",
        "```",
        "\n->\n".join(graph),
        "```",
        "",
        "## Safe to migrate?",
        "",
        "Schema/mapping only in Phase 1. **Do not swap engine paths yet.**",
        "",
        f"- Warehouse target: `{mapping['new']}`",
        f"- Transform: {mapping['transform']}",
        "",
        "## Unused columns",
        "",
    ]
    if unused_cols:
        for c in unused_cols:
            lines.append(f"- `{c}` (all empty in source)")
    else:
        lines.append("- None detected as all-empty. See `unused_columns.json` for unreferenced names.")
    lines += [
        "",
        "## Possible normalization",
        "",
        f"1. Map to `{mapping['new']}`.",
        "2. Extract citation fields into `reference/papers.csv` + `paper_id`.",
        "3. Convert numeric units via `runtime/unit_conversion.csv`.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")


def write_formula_traces() -> None:
    out_dir = WH / "generated" / "formula_trace"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "risk_engine.md").write_text(
        """# Risk engine formula trace

**Source of truth (production):** `app/agent/stages/health_risk.py`  
**Status:** Phase 1 documentation only - formulas unchanged; still reads `data/`.

## Entry

`compute_risks(repo, profile)` / RISK_V2_1 - `app/agent/stages/health_risk.py`

## Call chain (actual functions)

```
compute_risks()
->
_breed_records() <- BREEDS.csv (+ normalize via BREED_ALIASES.csv)
->
collect_trait_risks()
  ->
  for each trait category on breed records:
    repository trait_*_conditions tables
    SIZE | BODYTYPE | COATTYPE | ENERGY | SKULLTYPE |
    FUNCTIONGROUP | WEAKNESSGROUP | CLIMATE | LIFESPAN
    ->
    reads prevalence / observed percent
->
compute_evidence_scores()
  <- BREED_CONDITIONS.csv
  <- TRAIT_INTERACTIONS.csv (multipliers; clamp 0.80-1.20)
->
apply_benefit_reductions() <- TRAIT_BENEFITS.csv
->
apply_mixed_breed_nudge() <- MIXED_BREED_MATRIX.csv (if mixed)
->
apply_significance_logic()
->
returns ranked risks with risk_percent (+ formula_execution debug)
```

## Columns that matter

- Prevalence / observed percent on condition tables
- Multiplier on TRAIT_INTERACTIONS
- Benefit magnitude on TRAIT_BENEFITS
- Mixed matrix factor on MIXED_BREED_MATRIX

## Warehouse target

- `science/breed_condition_risk.csv`
- `science/trait_condition_risk.csv` (all 9 trait tables collapsed)
- `science/mixed_trait_interactions.csv`
- `science/prevention_effectiveness.csv` (benefits)
- `reference/papers.csv` via `paper_id`

## Do not change

No edits to `health_risk.py` in Phase 1.
""",
        encoding="utf-8",
    )

    (out_dir / "ingredient_engine.md").write_text(
        """# Ingredient engine formula trace

**Source:** `app/agent/ingredient_engine.py` (+ `stages/nutrition.py`)

## Call chain

```
map_ingredients(risks, weight_kg, repo)
->
_condition_ingredient_rows() <- repository.condition_ingredients()
  merges CONDITION_INGREDIENTS.csv (scientific + preventative homes)
->
calculate_dose(link, weight_kg) - dose/unit math per link
->
_ingredient_evidence() <- INGREDIENT_EVIDENCE.csv
->
_ingredient_mechanisms() <- INGREDIENT_MECHANISMS.csv
->
returns nutrition targets / ingredient map
```

## Modifiers / side inputs

- `NUTRIENT_PRIORITIES.csv` (ordering; assembler-heavy)
- `INGREDIENT_MECHANISMS.csv`, `NATURAL_FOOD_SOURCES.csv` (narrative)
- `INGREDIENT_NUTRIENT_ESTIMATES.csv` (opt-in estimates)

## Warehouse target

- `science/nutrient_targets.csv`
- `science/ingredient_evidence.csv`
- `science/ingredient_food_sources.csv`
- `science/food_nutrients.csv`
- units via `runtime/unit_conversion.csv`

## Do not change

No edits to `ingredient_engine.py` in Phase 1.
""",
        encoding="utf-8",
    )

    (out_dir / "package_optimizer.md").write_text(
        """# Package optimizer formula trace

**Source:** `app/agent/package_optimizer.py` (+ `stages/optimization.py`)

## Call chain

```
build_optimized_packages(...)
->
load_candidate_products() <- PRODUCT_CATALOG + COMPONENTS + PRICING + FEEDING + FUNCTIONS + EXT_*
->
_targets_from_ingredients() <- nutrition targets from map_ingredients
->
coverage_matrix() + alias match via INGREDIENT_ALIASES
->
_pick_staple() <- PACKAGE_TIERS
->
_optimize_essential / _optimize_balanced / _optimize_optimal
->
_overall_score (coverage - surplus + clinical function)
->
returns package tiers / line items
```

## Warehouse target

- `science/product_composition.csv`
- `runtime/parameter_defaults.csv` (tiers, pricing)
- `runtime/lookup_maps.csv` (feeding, functions)
- `runtime/aliases.csv` (ingredient aliases)

## Do not change

No edits to `package_optimizer.py` in Phase 1.
""",
        encoding="utf-8",
    )

    (out_dir / "activity_engine.md").write_text(
        """# Activity / management formula trace

**Source:** management path + `CONDITION_ACTIVITIES.csv`; report rules in `ACTIVITY_PRESCRIPTION_RULES.csv`

## Call chain

```
management / assembler activity section
->
CONDITION_ACTIVITIES.csv (condition -> activity)
->
optional report enrichment <- ACTIVITY_PRESCRIPTION_RULES.csv
->
ACTIVITY_EVIDENCE.csv currently unused by engine formulas
->
returns activity recommendations in assembled response / reports
```

## Warehouse target

- `reference/activities.csv`
- `science/prevention_effectiveness.csv` (activity effectiveness)
- `runtime/lookup_maps.csv` (prescription rules)

## Do not change

No agent formula changes in Phase 1.
""",
        encoding="utf-8",
    )

    (out_dir / "nutrition_engine.md").write_text(
        """# Nutrition stage formula trace

**Source:** `app/agent/stages/nutrition.py` -> delegates to `ingredient_engine`

## Call chain

```
run_nutrition_stage(...)
->
ingredient_engine.map_ingredients
->
CONDITION_INGREDIENTS (+ evidence/mechanisms as attached)
->
passes targets to optimization stage
```

See `ingredient_engine.md` for CSV detail.

## Do not change

No edits in Phase 1.
""",
        encoding="utf-8",
    )

    (out_dir / "assembler.md").write_text(
        """# Response assembler formula trace

**Source:** `app/agent/response_assembler.py`

## Call chain

```
assemble_analyze_response / equivalent
->
biological profile (from bio stage)
->
risk ranking (from health_risk)
->
nutrition targets (from ingredient_engine)
->
packages (from package_optimizer)
->
enrich with:
  NUTRIENT_PRIORITIES
  NATURAL_FOOD_SOURCES
  INGREDIENT_MECHANISMS / EVIDENCE
  CONDITION_ACTIVITIES
  report tables (timeline, trait explanations, ...) when clinical report path
->
returns API JSON consumed by demo UI + Validation Console
```

## Note

Assembler **assembles**; it does not recompute RISK_V2_1 math.

## Do not change

No edits to `response_assembler.py` in Phase 1.
""",
        encoding="utf-8",
    )


def write_manifest() -> None:
    text = """# Waggy Scientific Data Warehouse - Phase 1
version: "0.1.0-phase1"
status: scaffolding_only
production_data_root: data/
warehouse_root: warehouse/
engine_reads: data/   # unchanged
notes: |
  Phase 1 creates schema, metadata, and generated audits only.
  No CSV rows have been migrated from data/ into science/reference tables
  except runtime/unit_conversion.csv seed rows.
  Do not point the engine at warehouse/ until a later phase.

layers:
  reference: dimension / identity tables (headers only)
  science: fact tables for risk, nutrition, products (headers only)
  runtime: units, aliases, defaults, lookup maps
  generated: audits produced from data/ scan

tables:
  reference:
    - breeds.csv
    - traits.csv
    - conditions.csv
    - ingredients.csv
    - foods.csv
    - nutrients.csv
    - activities.csv
    - climates.csv
    - body_sizes.csv
    - body_types.csv
    - coat_types.csv
    - skull_types.csv
    - prevention_methods.csv
    - papers.csv
  science:
    - breed_condition_risk.csv
    - trait_condition_risk.csv
    - mixed_trait_interactions.csv
    - prevention_effectiveness.csv
    - ingredient_evidence.csv
    - food_nutrients.csv
    - nutrient_targets.csv
    - ingredient_food_sources.csv
    - product_composition.csv
  runtime:
    - unit_conversion.csv
    - aliases.csv
    - parameter_defaults.csv
    - lookup_maps.csv
"""
    (WH / "manifest.yaml").write_text(text, encoding="utf-8")


def write_readme() -> None:
    (WH / "README.md").write_text(
        """# Scientific Data Warehouse (Phase 1)

This folder is the **future** scientific data warehouse for Waggy/Wagtopia.

## Hard rules (Phase 1)

- Production `data/` is **untouched**.
- `app/agent/*` is **untouched** - all formulas still run against `data/`.
- No live migration of rows into `reference/` or `science/` (headers + mapping only).
- `runtime/unit_conversion.csv` is seeded so unit policy is explicit.
- Generated audits live under `generated/`.

## Layout

```
warehouse/
  reference/     # identity dimensions + papers
  science/       # facts (risk, nutrition, products)
  runtime/       # units, aliases, defaults, maps
  generated/     # migration_report, coverage, duplicates, traces
  tools/         # build_phase1.py (regenerate audits)
  manifest.yaml
  README.md
  DATA_MIGRATION_PLAN.md
```

## Key normalization ideas

1. **Nine trait condition CSVs -> one** `science/trait_condition_risk.csv` with `trait_category`.
2. **Citations ->** `reference/papers.csv` + `paper_id` on every science row.
3. **Units ->** `runtime/unit_conversion.csv` so the engine later calculates only in canonical units.
4. **Aliases ->** single `runtime/aliases.csv` with `alias_type`.

## Regenerating audits

```bash
py -3 warehouse/tools/build_phase1.py
```

## What Phase 2+ will do

Point adapters at warehouse tables, dual-run parity, then cut over - **without changing formula math**.
""",
        encoding="utf-8",
    )


def write_migration_plan(inventory: list[dict]) -> None:
    lines = [
        "# DATA_MIGRATION_PLAN.md",
        "",
        "**Phase 1 - plan only. Do not execute.**",
        "",
        "Engine continues to read `data/`. Warehouse tables are schema stubs.",
        "",
        "## Status legend",
        "",
        "| Status | Meaning |",
        "|--------|---------|",
        "| Ready | Mapping known; safe to copy in a later phase |",
        "| Blocked | Needs design decision |",
        "| Skip | Unused / unmanifested; inventory only |",
        "",
        "## Table plan",
        "",
    ]
    for item in inventory:
        name = item["filename"]
        mapping = WAREHOUSE_MAP.get(name, {"new": "TBD", "transform": "TBD"})
        st = item["requirement"]
        status = "Skip" if st == "unused" else "Ready"
        if mapping["new"] == "TBD":
            status = "Blocked"
        lines += [
            f"### {name}",
            "",
            f"- **Rows:** {item['row_count']}",
            f"- **Old path:** `{item['path']}`",
            f"- **New:** `{mapping['new']}`",
            f"- **Transformation:** {mapping['transform']}",
            f"- **Requirement today:** {st}",
            f"- **Status:** {status}",
            f"- **Action:** Don't touch yet",
            "",
        ]
    lines += [
        "## Collapses (important)",
        "",
        "### Trait prevalence (9 -> 1)",
        "",
        "```",
        "SIZE_CONDITIONS.csv           -+",
        "BODYTYPE_CONDITIONS.csv       -+",
        "COATTYPE_CONDITIONS.csv       -+",
        "ENERGY_CONDITIONS.csv         -+",
        "SKULLTYPE_CONDITIONS.csv      -+-> science/trait_condition_risk.csv",
        "FUNCTIONGROUP_CONDITIONS.csv  -+     trait_category + trait_value",
        "WEAKNESSGROUP_CONDITIONS.csv  -+",
        "CLIMATE_CONDITIONS.csv        -+",
        "LIFESPAN_CONDITIONS.csv       -+",
        "```",
        "",
        "### Evidence normalization",
        "",
        "```",
        "inline journal/author/year/url/quote across many CSVs",
        "        ->",
        "reference/papers.csv  (paper_id)",
        "        ->",
        "science/*.csv rows keep paper_id only",
        "```",
        "",
        "## Cutover rule",
        "",
        "No cutover in Phase 1. Later phases add adapters and parity tests before switching paths.",
        "",
    ]
    (WH / "DATA_MIGRATION_PLAN.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    WH.mkdir(parents=True, exist_ok=True)
    write_schema_csvs()
    write_formula_traces()
    write_manifest()
    write_readme()

    analysis_dir = WH / "generated" / "csv_analysis"
    if analysis_dir.exists():
        for old in analysis_dir.glob("*.md"):
            old.unlink()

    meta_by_path: dict[str, dict] = {}
    meta_by_file: dict[str, dict] = {}
    inventory = []
    py_refs: dict[str, list[str]] = {}

    for path in sorted(DATA.rglob("*.csv")):
        name = path.name
        rel = path.relative_to(ROOT).as_posix()
        meta = read_csv_meta(path)
        meta_by_path[rel] = meta
        # Keep last-by-name for unused-column scan; path-keyed used for duplicates
        meta_by_file[name] = meta
        stem = path.stem
        refs = grep_python_refs(stem, name)
        py_refs[name] = refs
        st = status_for(name)
        apis = APIS["unused"] if st == "unused" else (APIS["partial"] if st == "partially_required" else APIS["required"])
        if name.startswith("PRODUCT") or name.startswith("EXT_"):
            apis = list(dict.fromkeys(apis + APIS["partial"]))
        a_stem = analysis_stem_for(path)
        item = {
            "filename": name,
            "path": rel,
            "analysis_doc": f"generated/csv_analysis/{a_stem}.md",
            "row_count": meta["row_count"],
            "column_count": len(meta["header"]),
            "columns": meta["header"],
            "primary_purpose": PURPOSE.get(name, "See csv_analysis"),
            "backend_files_importing": refs,
            "formulas_using": FORMULAS.get(name, []),
            "api_endpoints_exposing": apis,
            "debug_page_consuming": DEBUG if st != "unused" or name in (
                "MIXED_BREED_INTERACTIONS.csv",
                "ACTIVITY_EVIDENCE.csv",
                "CONDITION_PROTOCOLS.csv",
                "PRODUCT_DEFAULTS.csv",
            ) else "none (unmanifested or unused)",
            "requirement": st,
            "warehouse_target": WAREHOUSE_MAP.get(name, {}).get("new"),
            "dependency_graph": dependency_graph(name),
        }
        inventory.append(item)
        write_csv_analysis(
            name,
            meta,
            refs,
            st,
            rel_path=rel,
            analysis_stem=a_stem,
        )

    gen = WH / "generated"
    gen.mkdir(parents=True, exist_ok=True)

    migration_report = {
        "phase": 1,
        "source_root": "data/",
        "warehouse_root": "warehouse/",
        "engine_untouched": True,
        "csv_count": len(inventory),
        "tables": inventory,
    }
    (gen / "migration_report.json").write_text(
        json.dumps(migration_report, indent=2), encoding="utf-8"
    )

    # Duplicate detection keyed so dual-home files both count
    name_counts: dict[str, int] = {}
    for p in meta_by_path:
        name_counts[Path(p).name] = name_counts.get(Path(p).name, 0) + 1
    labeled: dict[str, dict] = {}
    for p, m in meta_by_path.items():
        label = Path(p).name
        if name_counts[label] > 1:
            label = f"{Path(p).name} [{Path(p).parent.name}]"
        labeled[label] = m
    dups = extract_conditions(labeled)
    (gen / "duplicate_detection.json").write_text(json.dumps(dups, indent=2), encoding="utf-8")

    unused = find_unused_columns(meta_by_file, py_refs)
    (gen / "unused_columns.json").write_text(json.dumps(unused, indent=2), encoding="utf-8")

    cov = coverage_report(meta_by_file)
    (gen / "coverage_report.json").write_text(json.dumps(cov, indent=2), encoding="utf-8")

    write_migration_plan(inventory)

    # mapping summary
    mapping_doc = {
        "phase": 1,
        "note": "Old data/ CSV -> warehouse target (no rows copied except unit_conversion seed)",
        "mappings": [
            {
                "old": item["path"],
                "filename": item["filename"],
                "new": WAREHOUSE_MAP.get(item["filename"], {}).get("new"),
                "transform": WAREHOUSE_MAP.get(item["filename"], {}).get("transform"),
                "rows": item["row_count"],
            }
            for item in inventory
        ],
    }
    (gen / "warehouse_mapping.json").write_text(json.dumps(mapping_doc, indent=2), encoding="utf-8")

    print(f"Phase 1 complete: {len(inventory)} CSVs inventoried under {WH}")


if __name__ == "__main__":
    main()
