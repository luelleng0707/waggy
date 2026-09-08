"""Warehouse-backed preventative care model.

Scientific input only. Demo synthetic breed-care is not used as evidence
and is not a production fallback.
"""

from __future__ import annotations

from typing import Any

from app.agent.wellness_map import goal_for_condition, get_wellness_goals
from app.data.demo_catalog import demo_mode_enabled


def _condition_key(name: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")


def _pct(ratio: Any) -> float | None:
    if ratio is None or ratio == "":
        return None
    try:
        val = float(ratio)
    except (TypeError, ValueError):
        return None
    if val <= 1.0:
        return round(val * 1000) / 10
    return round(val * 10) / 10


WAREHOUSE_UNAVAILABLE = "Not available from current scientific warehouse."
NOT_AVAILABLE = "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE"

GOAL_TO_PATHWAY = {
    "joint_health": "joint",
    "skin_health": "skin",
    "dental_health": "dental",
    "digestive_health": "digestive",
    "weight_management": "digestive",
    "respiratory_comfort": "respiratory",
    "cardiac_support": "cardiac",
    "eye_health": "eye",
    "immune_support": "immune",
}

INGREDIENT_TO_STAR_NUTRIENT = {
    "zinc": "zinc_mg_per_kg_dm",
}

PATHWAY_LABELS = {
    "joint": "Joint health",
    "skin": "Skin / coat",
    "dental": "Dental / oral",
    "digestive": "Digestive",
    "respiratory": "Respiratory",
    "cardiac": "Cardiac",
    "eye": "Eye health",
    "immune": "Immune",
}

TRAIT_COLUMNS = (
    ("size", "size"),
    ("body_type", "body_type"),
    ("coat_type", "coat_type"),
    ("energy", "energy"),
    ("weakness_group", "weakness_group"),
    ("skull_type", "skull_type"),
    ("climate", "climate"),
    ("lifespan", "lifespan"),
    ("function_group", "function_group"),
)


def _star_nutrient_for(ingredient_name: str) -> str | None:
    key = str(ingredient_name or "").strip().lower()
    return INGREDIENT_TO_STAR_NUTRIENT.get(key)


def _empty_model(*, demo: bool = False) -> dict[str, Any]:
    return {
        "demo_synthetic": False,
        "clinical_evidence": False,
        "warehouse_evidence": False,
        "evidence_status": NOT_AVAILABLE,
        "label": WAREHOUSE_UNAVAILABLE,
        "matched_rows": [],
        "pathways": [],
        "pathway_briefs": [],
        "condition_records": [],
        "care_pathway_records": [],
        "star_nutrients": [],
        "observation_pathways": [],
        "prevalence_available": False,
        "diagnosis_claim": False,
        "preventative_targets": [],
        "disclaimer": (
            "These are preventative considerations — they do not mean the dog currently has these conditions. "
            "Scientific evidence for this breed/pathway is not currently available in the warehouse."
        ),
        "note": NOT_AVAILABLE,
        "demo_mode": demo,
    }


def _targets_for_condition(ingredients: Any, condition: str, star_nutrients: list[str]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    if ingredients is None or getattr(ingredients, "empty", True):
        return targets
    hits = ingredients[ingredients["condition"].astype(str).str.lower() == condition.lower()]
    seen: set[str] = set()
    for _, ing in hits.iterrows():
        iname = str(ing.get("ingredient_name") or "").strip()
        if not iname or iname.lower() in seen:
            continue
        seen.add(iname.lower())
        target = {
            "ingredient_name": iname,
            "ingredient_id": ing.get("ingredient_id"),
            "display": iname,
            "kind": "preventative_ingredient",
            "star": False,
            "fact_id": ing.get("fact_id"),
            "paper_name": ing.get("source_name") or ing.get("paper_name"),
            "scientific_quote": ing.get("source_quote") or ing.get("scientific_quote"),
            "paper_link": ing.get("source_url") or ing.get("paper_link"),
            "condition": condition,
            "status": ing.get("status"),
        }
        nid = _star_nutrient_for(iname)
        if nid:
            target["nutrient_id"] = nid
            target["star"] = True
            target["kind"] = "preventative_nutrient"
            if nid not in star_nutrients:
                star_nutrients.append(nid)
        targets.append(target)
    return targets


def _breed_trait_rows(repo: Any, resolved_l: set[str]) -> list[dict[str, str]]:
    breeds_df = repo.breeds() if hasattr(repo, "breeds") else None
    if breeds_df is None or getattr(breeds_df, "empty", True):
        return []
    name_col = "breed" if "breed" in breeds_df.columns else "breed_name"
    rows = []
    for _, row in breeds_df.iterrows():
        name = str(row.get(name_col) or "").strip()
        if name.lower() not in resolved_l and not any(n in name.lower() or name.lower() in n for n in resolved_l):
            continue
        traits = {}
        for col, _ in TRAIT_COLUMNS:
            val = str(row.get(col) or "").strip()
            if val:
                traits[col] = val
        if traits:
            rows.append({"breed": name, "traits": traits, "phenotype_status": "MISSING_PROVENANCE"})
    return rows


def _estimated_associations(
    repo: Any,
    breed_rows: list[dict[str, str]],
    condition: str,
) -> list[dict[str, Any]]:
    """Trait→condition warehouse rows. Does not sum or invent a combined prevalence."""
    tables = repo.trait_condition_tables() if hasattr(repo, "trait_condition_tables") else None
    if tables is None or getattr(tables, "empty", True) or not breed_rows:
        return []
    out: list[dict[str, Any]] = []
    seen: set[tuple] = set()
    cond_l = condition.lower()
    for breed_row in breed_rows:
        traits = breed_row.get("traits") or {}
        for category, value in traits.items():
            hits = tables[
                (tables["trait_category"].astype(str) == category)
                & (tables["trait_value"].astype(str) == value)
                & (tables["condition"].astype(str).str.lower() == cond_l)
            ]
            for _, hit in hits.iterrows():
                key = (category, value, str(hit.get("paper_link") or ""), str(hit.get("prevalence") or ""))
                if key in seen:
                    continue
                seen.add(key)
                prev = hit.get("prevalence")
                try:
                    prev_f = float(prev) if prev not in (None, "") else None
                except (TypeError, ValueError):
                    prev_f = None
                out.append(
                    {
                        "breed": breed_row.get("breed"),
                        "trait_name": category,
                        "trait_value": value,
                        "condition": condition,
                        "effect_value": prev_f,
                        "effect_value_percent": _pct(prev_f) if prev_f is not None else None,
                        "paper_name": hit.get("source_name") or hit.get("paper_name"),
                        "scientific_quote": hit.get("source_quote") or hit.get("scientific_quote"),
                        "paper_link": hit.get("source_url") or hit.get("paper_link"),
                        "publication_year": hit.get("year") or hit.get("publication_year"),
                        "status": hit.get("status"),
                        "phenotype_status": breed_row.get("phenotype_status"),
                        "note": (
                            "Estimated association uses intern phenotype "
                            f"({breed_row.get('phenotype_status')}) × a cited trait-condition row. "
                            "This is not an observed breed prevalence and is not a merged estimate."
                        ),
                    }
                )
    return out


def _mixed_flagged_rows(repo: Any, breed_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    mixed = repo.mixed_breed_interactions() if hasattr(repo, "mixed_breed_interactions") else None
    if mixed is None or getattr(mixed, "empty", True) or len(breed_rows) < 2:
        return []
    values = set()
    for row in breed_rows:
        values.update((row.get("traits") or {}).values())
    flagged = []
    for _, row in mixed.iterrows():
        a = str(row.get("trait_a") or "").strip()
        b = str(row.get("trait_b") or "").strip()
        if a and b and a in values and b in values:
            flagged.append(
                {
                    "trait_a": a,
                    "trait_b": b,
                    "condition": row.get("condition"),
                    "interaction": row.get("interaction"),
                    "factor": row.get("factor"),
                    "reason": row.get("reason") or row.get("source"),
                    "status": row.get("status") or "NEEDS_VALIDATION",
                    "scientific_quote": row.get("scientific_quote") or "",
                    "paper_name": row.get("paper_name") or row.get("source") or "",
                    "paper_link": row.get("paper_link") or "",
                    "note": "Surfaced as flagged mixed-breed warehouse row. Not treated as validated science.",
                }
            )
    return flagged


def care_model_from_warehouse(repo: Any, breeds: list[str]) -> dict[str, Any]:
    """Observed breed-conditions + cited trait associations. No synthetic fallback."""
    wanted = [str(b or "").strip() for b in breeds if b]
    wanted_l = {w.lower() for w in wanted}
    if not wanted:
        return _empty_model(demo=demo_mode_enabled())

    normalize = getattr(repo, "normalize_breed_name", None)
    resolved = []
    for name in wanted:
        canon = normalize(name) if callable(normalize) else name
        resolved.append(str(canon or name).strip())
    resolved_l = {n.lower() for n in resolved} | wanted_l

    bc = repo.breed_conditions() if hasattr(repo, "breed_conditions") else None
    if bc is None or getattr(bc, "empty", True):
        return _empty_model(demo=demo_mode_enabled())

    breed_series = bc["breed"].astype(str).str.lower()
    mask = breed_series.isin(resolved_l)
    if not bool(mask.any()):
        extra = None
        for needle in resolved_l:
            part = breed_series.str.contains(needle, na=False, regex=False)
            extra = part if extra is None else extra | part
        if extra is not None:
            mask = extra
    hits = bc[mask]
    if hits.empty:
        return _empty_model(demo=demo_mode_enabled())

    ingredients = repo.condition_ingredients() if hasattr(repo, "condition_ingredients") else None
    breed_trait_rows = _breed_trait_rows(repo, resolved_l)
    mixed_flagged = _mixed_flagged_rows(repo, breed_trait_rows)

    by_pathway: dict[str, dict[str, Any]] = {}
    by_condition: dict[str, dict[str, Any]] = {}
    star_nutrients: list[str] = []
    preventative_targets: list[dict[str, Any]] = []

    for _, row in hits.iterrows():
        condition = str(row.get("condition") or "").strip()
        if not condition:
            continue
        goal_id = goal_for_condition(_condition_key(condition) or condition)
        pathway = GOAL_TO_PATHWAY.get(goal_id) or "other"
        goal = get_wellness_goals().get(goal_id) or {}
        bucket = by_pathway.setdefault(
            pathway,
            {
                "pathway": pathway,
                "label": PATHWAY_LABELS.get(pathway, goal.get("title") or pathway),
                "goal_id": goal_id,
                "conditions": [],
                "breeds": [],
                "evidence": [],
                "targets": [],
            },
        )
        cond_bucket = by_condition.setdefault(
            condition,
            {
                "condition": condition,
                "pathway": pathway,
                "label": condition,
                "goal_id": goal_id,
                "breeds": [],
                "evidence": [],
                "targets": [],
                "estimated_associations": [],
            },
        )
        breed_name = str(row.get("breed") or "")
        if breed_name and breed_name not in bucket["breeds"]:
            bucket["breeds"].append(breed_name)
        if breed_name and breed_name not in cond_bucket["breeds"]:
            cond_bucket["breeds"].append(breed_name)
        prev = row.get("prevalence")
        try:
            prev_f = float(prev) if prev not in (None, "") else None
        except (TypeError, ValueError):
            prev_f = None
        prev_pct = _pct(prev_f) if prev_f is not None else None
        evidence = {
            "fact_id": row.get("fact_id"),
            "breed": breed_name,
            "condition": condition,
            "condition_id": row.get("condition_id"),
            "observed_prevalence": prev_f,
            "observed_prevalence_percent": prev_pct,
            "paper_name": row.get("source_name"),
            "scientific_quote": row.get("source_quote"),
            "paper_link": row.get("source_url"),
            "publication_year": row.get("year") or row.get("publication_year"),
            "study_type": row.get("study_type"),
            "species": row.get("species"),
            "status": row.get("status"),
            "csv_file": row.get("_csv_file") or "biology/observed_breed_conditions.csv",
            "csv_row": row.get("_csv_row"),
        }
        bucket["evidence"].append(evidence)
        cond_bucket["evidence"].append(evidence)
        if condition not in bucket["conditions"]:
            bucket["conditions"].append(condition)
        targets = _targets_for_condition(ingredients, condition, star_nutrients)
        for target in targets:
            existing = {(t["display"].lower(), str(t.get("condition") or "").lower()) for t in bucket["targets"]}
            key = (target["display"].lower(), condition.lower())
            if key not in existing:
                bucket["targets"].append(target)
                cond_bucket["targets"].append(target)
                preventative_targets.append(target)

    for condition, cond_bucket in by_condition.items():
        cond_bucket["estimated_associations"] = _estimated_associations(repo, breed_trait_rows, condition)

    pathway_briefs: list[dict[str, Any]] = []
    condition_records: list[dict[str, Any]] = []
    for condition, cond_bucket in by_condition.items():
        papers = [e.get("paper_name") for e in cond_bucket["evidence"] if e.get("paper_name")]
        paper_line = ", ".join(dict.fromkeys(str(p) for p in papers)) or WAREHOUSE_UNAVAILABLE
        observed_lines = []
        for e in cond_bucket["evidence"]:
            if e.get("observed_prevalence_percent") is None:
                observed_lines.append(f"{e.get('breed')}: {WAREHOUSE_UNAVAILABLE}")
            else:
                observed_lines.append(f"{e.get('breed')}: {e['observed_prevalence_percent']}%")
        observed_copy = "; ".join(observed_lines) if observed_lines else WAREHOUSE_UNAVAILABLE
        estimates = cond_bucket["estimated_associations"]
        if estimates:
            est_lines = []
            for item in estimates:
                pct = item.get("effect_value_percent")
                bit = (
                    f"{item.get('trait_name')}={item.get('trait_value')} → {pct}%"
                    if pct is not None
                    else f"{item.get('trait_name')}={item.get('trait_value')} → {NOT_AVAILABLE}"
                )
                est_lines.append(bit)
            estimated_copy = (
                "Cited trait-condition associations (not a combined estimate; phenotype is "
                f"{estimates[0].get('phenotype_status')}): " + "; ".join(est_lines)
            )
        else:
            estimated_copy = NOT_AVAILABLE
        target_names = [t["display"] for t in cond_bucket["targets"]]
        breed_line = " / ".join(cond_bucket["breeds"] or wanted)
        implication = (
            "This package prioritizes nutritional support associated with the "
            f"{cond_bucket['pathway']} pathway."
            + (f" Preventative ingredients in the warehouse: {', '.join(dict.fromkeys(target_names))}." if target_names else "")
            + " This does not claim that a supplement reduces the chance of developing this condition."
        )
        record = {
            "condition": condition,
            "pathway": cond_bucket["pathway"],
            "label": condition,
            "goal_id": cond_bucket["goal_id"],
            "breeds": cond_bucket["breeds"],
            "evidence": cond_bucket["evidence"],
            "prevalence": {
                "observed": observed_copy,
                "observed_by_breed": [
                    {
                        "breed": e.get("breed"),
                        "percent": e.get("observed_prevalence_percent"),
                        "ratio": e.get("observed_prevalence"),
                    }
                    for e in cond_bucket["evidence"]
                ],
                "estimated": estimated_copy,
                "estimated_associations": estimates,
            },
            "preventative_targets": cond_bucket["targets"],
            "paper_name": paper_line if papers else None,
            "scientific_quote": next((e.get("scientific_quote") for e in cond_bucket["evidence"] if e.get("scientific_quote")), None),
            "paper_link": next((e.get("paper_link") for e in cond_bucket["evidence"] if e.get("paper_link")), None),
            "publication_year": next((e.get("publication_year") for e in cond_bucket["evidence"] if e.get("publication_year")), None),
            "why_this_matters": (
                f"Your dog's breed profile is associated with {condition} based on warehouse evidence."
            ),
            "preventative_implication": implication,
            "warehouse_evidence": True,
            "demo_synthetic": False,
            "diagnosis_claim": False,
            "status": "WAREHOUSE_EVIDENCE",
        }
        condition_records.append(record)

    for pathway, bucket in by_pathway.items():
        papers = [e.get("paper_name") for e in bucket["evidence"] if e.get("paper_name")]
        paper_line = ", ".join(dict.fromkeys(str(p) for p in papers)) or WAREHOUSE_UNAVAILABLE
        prev_bits = [
            f"{e['observed_prevalence_percent']}% ({e.get('breed')})"
            for e in bucket["evidence"]
            if e.get("observed_prevalence_percent") is not None
        ]
        prevalence_copy = ", ".join(prev_bits) if prev_bits else WAREHOUSE_UNAVAILABLE
        target_names = [t["display"] for t in bucket["targets"]]
        conditions = bucket["conditions"]
        breed_line = " / ".join(bucket["breeds"] or wanted)
        cond_records = [r for r in condition_records if r["pathway"] == pathway]
        est_any = any(
            r["prevalence"]["estimated"] not in (NOT_AVAILABLE, WAREHOUSE_UNAVAILABLE)
            for r in cond_records
        )
        copy = (
            "Because this condition has an evidence-backed association with the dog's breed profile, "
            "Balanced / Optimal packages may prioritize nutrients or ingredients associated with "
            "preventative nutritional support for this pathway. This is preventative guidance only. "
            "It does NOT mean the dog currently has this condition."
        )
        pathway_briefs.append(
            {
                "pathway": pathway,
                "label": bucket["label"],
                "goal_id": bucket["goal_id"],
                "breeds": bucket["breeds"],
                "conditions": conditions,
                "condition_records": cond_records,
                "chain": [
                    {"step": "breed", "value": bucket["breeds"] or wanted},
                    {"step": "condition", "value": conditions},
                    {"step": "observed_prevalence", "value": prevalence_copy},
                    {"step": "preventative_target", "value": target_names or ["pathway product function"]},
                ],
                "evidence_status": "WAREHOUSE_EVIDENCE",
                "prevalence_status": "AVAILABLE" if prev_bits else "NOT_AVAILABLE",
                "prevalence_copy": prevalence_copy,
                "estimated_prevalence_copy": (
                    "; ".join(r["prevalence"]["estimated"] for r in cond_records)
                    if est_any
                    else NOT_AVAILABLE
                ),
                "scientific_quote": next((e.get("scientific_quote") for e in bucket["evidence"] if e.get("scientific_quote")), None),
                "paper_name": paper_line if papers else None,
                "paper_link": next((e.get("paper_link") for e in bucket["evidence"] if e.get("paper_link")), None),
                "publication_year": next((e.get("publication_year") for e in bucket["evidence"] if e.get("publication_year")), None),
                "warehouse_evidence": True,
                "demo_synthetic": False,
                "diagnosis_claim": False,
                "language": "associated pathway / preventative consideration",
                "copy": copy,
                "why_this_matters": (
                    f"This dog's {breed_line} breed profile is associated with "
                    f"{', '.join(conditions)} based on {paper_line}."
                ),
                "preventative_targets": bucket["targets"],
                "evidence": bucket["evidence"],
                "product_role": "care_support",
            }
        )

    scoring_pathways = [p for p in by_pathway.keys() if p != "other"]
    return {
        "demo_synthetic": False,
        "clinical_evidence": True,
        "warehouse_evidence": True,
        "evidence_status": "WAREHOUSE_EVIDENCE",
        "label": "Scientific warehouse evidence",
        "matched_rows": [],
        "pathways": scoring_pathways,
        "pathway_briefs": pathway_briefs,
        "condition_records": condition_records,
        "care_pathway_records": condition_records,
        "mixed_breed_flagged": mixed_flagged,
        "star_nutrients": star_nutrients,
        "observation_pathways": [],
        "prevalence_available": any(
            brief.get("prevalence_status") == "AVAILABLE" for brief in pathway_briefs
        ),
        "diagnosis_claim": False,
        "preventative_targets": preventative_targets,
        "disclaimer": (
            "These are preventative considerations — they do not mean the dog currently has these conditions."
        ),
        "note": (
            "Observed rows: warehouse/biology/observed_breed_conditions.csv. "
            "Trait associations are listed separately and are not summed into a single estimate. "
            "Intern phenotype used for estimation is MISSING_PROVENANCE."
        ),
        "source_csv": "warehouse/biology/observed_breed_conditions.csv",
        "demo_mode": demo_mode_enabled(),
    }


def resolve_care_model(
    repo: Any,
    breeds: list[str],
    observations: list[str] | None = None,
    *,
    demo: bool | None = None,
) -> dict[str, Any]:
    """Warehouse evidence only. Observations do not invent conditions."""
    del observations
    if demo is None:
        demo = demo_mode_enabled()
    if repo is None:
        return _empty_model(demo=demo)
    scientific = care_model_from_warehouse(repo, breeds)
    if scientific.get("warehouse_evidence"):
        return scientific
    empty = _empty_model(demo=demo)
    empty["note"] = (
        "Scientific evidence for this breed/pathway is not currently available in the warehouse."
    )
    return empty
