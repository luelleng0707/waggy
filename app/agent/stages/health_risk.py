"""
Health-risk pipeline — ports src/engine/{traitResolver,overlapEngine,benefitEngine,significanceEngine,riskEngine}.js

Goal: identical risk ranking, confidence, mixed-breed factors, and groomer boosts for parity.
"""

from __future__ import annotations

import math
import re
from typing import Any

import pandas as pd

from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, js_round, normalize_breed_name, parse_prevalence

CATEGORY_WEIGHTS = {
    "weakness_group": 3.0,
    "body_type": 2.5,
    "skull_type": 2.5,
    "function_group": 2.0,
    "size": 2.0,
    "energy": 1.5,
    "lifespan": 1.5,
    "coat_type": 1.0,
    "climate": 1.0,
}
TOTAL_TRAIT_CATEGORIES = len(CATEGORY_WEIGHTS)
INTERACTION_MIN = 0.80
INTERACTION_MAX = 1.20

GROOMER_MAP = {
    "tear_stains": "Tear Staining",
    "limping": "Hip Dysplasia",
    "limps": "Cruciate Ligament Rupture",
    "itching": "Atopic Dermatitis",
    "scratching": "Atopic Dermatitis",
    "dry_skin": "Dry Skin",
    "eye_discharge": "Cataracts",
    "eyes": "Tear Staining",
    "bad_breath": "Dental Disease",
    "teeth": "Dental Disease",
    "ears": "Ear Infection",
    "shedding": "Dry Skin",
    "anal_gland": "Anal Gland Impaction",
    "skin": "Dry Skin",
    "odor": "Ear Infection",
}


def condition_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").lower()).strip("_")


def clamp_risk(decimal: float) -> float:
    return min(1.0, max(0.0, float(decimal)))


def clamp_interaction_factor(factor: float) -> float:
    try:
        f = float(factor)
    except (TypeError, ValueError):
        f = 1.0
    return min(INTERACTION_MAX, max(INTERACTION_MIN, f))


def round_pct(decimal: float) -> float:
    return js_round(clamp_risk(decimal) * 1000) / 10


def _breed_records(repo: DataRepository, breed_names: list[str]) -> list[dict[str, Any]]:
    breeds_df = repo.breeds()
    if breeds_df.empty:
        return []
    out = []
    for name in breed_names:
        key = normalize_breed_name(name)
        hit = breeds_df[breeds_df["breed"].str.lower() == key.lower()]
        if hit.empty:
            hit = breeds_df[breeds_df["breed"].str.lower().str.contains(key.lower(), na=False)]
        if hit.empty:
            continue
        row = hit.iloc[0]
        out.append({
            "breed_name": row.get("breed"),
            "size_class": row.get("size"),
            "body_type": row.get("body_type"),
            "coat_type": row.get("coat_type"),
            "energy_level": row.get("energy"),
            "weakness_group": row.get("weakness_group"),
            "lifespan_class": row.get("lifespan"),
            "skull_type": row.get("skull_type"),
            "climate": row.get("climate"),
            "function_group": row.get("function_group"),
        })
    return out


def collect_trait_risks(repo: DataRepository, breeds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Port of traitResolver.collectTraitRisks + queries.getTraitRisksForBreed.

    Preserves CSV concat encounter order so by_category Object.values order matches JS.
    """
    tables = repo.trait_condition_tables()
    if tables.empty:
        return []
    all_rows: list[dict[str, Any]] = []
    for breed in breeds:
        trait_values = {
            "size": breed.get("size_class"),
            "body_type": breed.get("body_type"),
            "coat_type": breed.get("coat_type"),
            "energy": breed.get("energy_level"),
            "skull_type": breed.get("skull_type"),
            "climate": breed.get("climate"),
            "lifespan": breed.get("lifespan_class"),
            "weakness_group": breed.get("weakness_group"),
            "function_group": breed.get("function_group"),
        }
        # Iterate full store in file order (same as JS filter on traitConditions).
        for _, r in tables.iterrows():
            category = r.get("trait_category")
            value = trait_values.get(str(category))
            if not value or r.get("trait_value") != value:
                continue
            cond = r.get("condition")
            all_rows.append({
                "trait_category": category,
                "trait_value": value,
                "condition_name": cond,
                "condition_key": condition_key(str(cond)),
                "prevalence": float(r.get("prevalence") or 0),
                "source_name": r.get("source_name"),
                "source_quote": r.get("source_quote"),
                "source_url": r.get("source_url"),
                "source_breed": breed.get("breed_name"),
            })
    return all_rows


def compute_evidence_scores(trait_risks: list[dict[str, Any]], breeds: list[dict[str, Any]], repo: DataRepository) -> list[dict[str, Any]]:
    by_condition: dict[str, dict[str, Any]] = {}
    for row in trait_risks:
        key = row["condition_key"] or row["condition_name"]
        if key not in by_condition:
            by_condition[key] = {"condition_name": row["condition_name"], "by_category": {}}
        cat = row["trait_category"]
        prev = float(row["prevalence"])
        existing = by_condition[key]["by_category"].get(cat)
        if not existing or prev > existing["prevalence"]:
            by_condition[key]["by_category"][cat] = {
                "trait_category": cat,
                "trait_value": row["trait_value"],
                "prevalence": prev,
                "weight": CATEGORY_WEIGHTS.get(cat, 1.0),
                "source_name": row.get("source_name"),
                "source_quote": row.get("source_quote"),
                "source_url": row.get("source_url"),
            }

    interactions_df = repo.trait_interactions()
    trait_values = set()
    for b in breeds:
        for v in b.values():
            if isinstance(v, str) and v:
                trait_values.add(v)

    results = []
    for key, payload in by_condition.items():
        evidence = list(payload["by_category"].values())
        base_risk = clamp_risk(sum(float(e["prevalence"]) for e in evidence))
        confidence_percent = js_round((len(evidence) / TOTAL_TRAIT_CATEGORIES) * 1000) / 10

        factor = 1.0
        applied = []
        if not interactions_df.empty:
            matches = interactions_df[
                (
                    (interactions_df["condition"].map(lambda c: condition_key(str(c))) == key)
                    | (interactions_df["condition"] == payload["condition_name"])
                )
                & (interactions_df["trait_a"].isin(trait_values))
                & (interactions_df["trait_b"].isin(trait_values))
            ]
            for _, m in matches.iterrows():
                if str(m.get("interaction", "")).lower() == "neutral":
                    continue
                # TRAIT_INTERACTIONS may use column "factor" or lack "interaction"
                f = m.get("factor", 1.0)
                if "interaction" in m and pd.notna(m.get("interaction")) and str(m.get("interaction")).lower() not in ("", "nan"):
                    # Some CSVs store multiplicative factor only
                    pass
                factor *= clamp_interaction_factor(f)
                applied.append(m.to_dict())
            factor = clamp_interaction_factor(factor)

        after = clamp_risk(base_risk * factor)
        results.append({
            "condition_name": payload["condition_name"],
            "condition_key": key,
            "trait_evidence": evidence,
            "base_risk": round(base_risk * 10000) / 10000,
            "base_risk_percent": round_pct(base_risk),
            "confidence_percent": confidence_percent,
            "evidence_count": len(evidence),
            "supporting_traits": [
                {"category": e["trait_category"], "value": e["trait_value"], "prevalence_percent": round_pct(e["prevalence"])}
                for e in evidence
            ],
            "interaction_factor": factor,
            "interactions_applied": applied,
            "risk_after_interaction": after,
            "risk_after_interaction_percent": round_pct(after),
        })

    results.sort(key=lambda r: r["risk_after_interaction"], reverse=True)
    return results


def apply_benefit_reductions(evidence_scores: list[dict[str, Any]], breeds: list[dict[str, Any]], repo: DataRepository) -> list[dict[str, Any]]:
    benefits_df = repo.trait_benefits()
    trait_values = set()
    for b in breeds:
        for v in b.values():
            if isinstance(v, str) and v:
                trait_values.add(v)

    out = []
    for risk in evidence_scores:
        key = risk["condition_key"]
        benefit = None
        if not benefits_df.empty:
            hits = benefits_df[
                (benefits_df["trait_a"].isin(trait_values))
                & (benefits_df["trait_b"].isin(trait_values))
                & (
                    (benefits_df["condition"].map(lambda c: condition_key(str(c))) == key)
                    | (benefits_df["condition"] == risk["condition_name"])
                )
            ]
            if not hits.empty:
                benefit = hits.iloc[0].to_dict()

        if not benefit:
            out.append({
                **risk,
                "benefit_factor": 1,
                "benefit_applied": None,
                "final_trait_risk": risk["risk_after_interaction"],
                "final_trait_risk_percent": risk["risk_after_interaction_percent"],
            })
            continue

        factor = float(benefit.get("reduction_factor") or 1)
        final = clamp_risk(risk["risk_after_interaction"] * factor)
        out.append({
            **risk,
            "benefit_factor": factor,
            "benefit_applied": benefit,
            "final_trait_risk": final,
            "final_trait_risk_percent": round_pct(final),
        })
    return out


def resolve_groomer_boosts(observed_conditions: list[str]) -> dict[str, bool]:
    boosts: dict[str, bool] = {}
    for obs in observed_conditions:
        raw = re.sub(r"\s+", "_", str(obs or "").lower())
        condition = GROOMER_MAP.get(raw)
        if condition:
            boosts[condition_key(condition)] = True
    return boosts


def apply_mixed_breed_nudge(
    trait_risk_decimal: float,
    condition_key_val: str,
    breed_names: list[str],
    repo: DataRepository,
) -> dict[str, Any]:
    matrix = repo.mixed_breed_matrix()
    if matrix.empty or len(breed_names) < 2:
        return {"risk": trait_risk_decimal, "mixed_breed_factor": 1, "mixed_breed_sources": []}

    pairs = []
    for i in range(len(breed_names)):
        for j in range(i + 1, len(breed_names)):
            pairs.append((breed_names[i], breed_names[j]))

    rows = []
    for _, mb in matrix.iterrows():
        a = str(mb.get("breed_a", ""))
        b = str(mb.get("breed_b", ""))
        cond = condition_key(str(mb.get("condition", "")))
        if cond != condition_key_val:
            continue
        for x, y in pairs:
            if (a.lower() == x.lower() and b.lower() == y.lower()) or (a.lower() == y.lower() and b.lower() == x.lower()):
                rows.append(mb.to_dict())
                break

    if not rows:
        return {"risk": trait_risk_decimal, "mixed_breed_factor": 1, "mixed_breed_sources": []}

    factor = 1.0
    for row in rows:
        f = float(row.get("factor") or 1)
        factor *= min(1.20, max(0.80, f))
    factor = min(1.20, max(0.80, factor))
    return {
        "risk": clamp_risk(trait_risk_decimal * factor),
        "mixed_breed_factor": factor,
        "mixed_breed_sources": rows,
    }


def _breed_observed(repo: DataRepository, breed_names: list[str]) -> list[dict[str, Any]]:
    df = repo.breed_conditions()
    if df.empty:
        return []
    names_l = {n.lower() for n in breed_names}
    hits = df[df["breed"].str.lower().isin(names_l)]
    out = []
    for _, r in hits.iterrows():
        prev = float(r.get("prevalence") or 0)
        out.append({
            "condition_name": r.get("condition"),
            "condition_key": condition_key(str(r.get("condition"))),
            "prevalence": prev,
            "breed_name": r.get("breed"),
            "source_name": r.get("source_name"),
            "source_quote": r.get("source_quote"),
            "source_url": r.get("source_url"),
        })
    return out


def apply_significance_logic(
    breeds: list[dict[str, Any]],
    breed_names: list[str],
    trait_scores: list[dict[str, Any]],
    observed_conditions: list[str],
    repo: DataRepository,
) -> list[dict[str, Any]]:
    observed = _breed_observed(repo, breed_names)
    is_purebred = len(breed_names) == 1
    groomer_boosts = resolve_groomer_boosts(observed_conditions)
    trait_map = {t["condition_key"]: t for t in trait_scores}

    def build_trait_context(condition_key_val: str) -> dict[str, Any] | None:
        trait = next(
            (t for t in trait_scores if t["condition_key"] == condition_key_val or t["condition_name"] == condition_key_val),
            None,
        )
        if not trait:
            return None
        interaction_pct = js_round((trait["interaction_factor"] - 1) * 1000) / 10
        benefit_pct = js_round((1 - trait["benefit_factor"]) * 1000) / 10 if trait.get("benefit_applied") else 0
        return {
            "trait_risk_percent": trait["final_trait_risk_percent"],
            "trait_risk_decimal": trait["final_trait_risk"],
            "confidence_percent": trait["confidence_percent"],
            "evidence_count": trait["evidence_count"],
            "supporting_traits": trait["supporting_traits"],
            "trait_evidence": trait["trait_evidence"],
            "interaction_adjustment_percent": interaction_pct,
            "benefit_adjustment_percent": benefit_pct,
            "interaction_factor": trait["interaction_factor"],
            "benefit_factor": trait["benefit_factor"],
        }

    if is_purebred:
        results = []
        for obs in observed:
            ctx = build_trait_context(obs["condition_key"])
            groomer_boosted = bool(groomer_boosts.get(obs["condition_key"]))
            results.append({
                "condition_name": obs["condition_name"],
                "condition_key": obs["condition_key"],
                "risk_percent": round_pct(obs["prevalence"]),
                "risk_decimal": clamp_risk(obs["prevalence"]),
                "breed_prevalence_percent": round_pct(obs["prevalence"]),
                "trait_risk_percent": None if not ctx else ctx["trait_risk_percent"],
                "confidence_percent": 0 if not ctx else ctx["confidence_percent"],
                "evidence_count": 0 if not ctx else ctx["evidence_count"],
                "supporting_traits": [] if not ctx else ctx["supporting_traits"],
                "interaction_adjustment_percent": 0 if not ctx else ctx["interaction_adjustment_percent"],
                "benefit_adjustment_percent": 0 if not ctx else ctx["benefit_adjustment_percent"],
                "mixed_breed_adjustment_percent": 0,
                "mixed_breed_factor": 1,
                "logic": "purebred_observed",
                "groomer_boosted": groomer_boosted,
                "trait_explanation": trait_map.get(obs["condition_key"]),
                "source": {
                    "source_name": obs.get("source_name"),
                    "source_quote": obs.get("source_quote"),
                    "source_url": obs.get("source_url"),
                    "breed": obs.get("breed_name"),
                },
            })
        results.sort(key=lambda a: (-int(a["groomer_boosted"]), -a["risk_percent"]))
        return results

    merged: dict[str, dict[str, Any]] = {}
    for trait in trait_scores:
        nudged = apply_mixed_breed_nudge(trait["final_trait_risk"], trait["condition_key"], breed_names, repo)
        groomer_boosted = bool(groomer_boosts.get(trait["condition_key"]))
        mixed_pct = js_round((nudged["mixed_breed_factor"] - 1) * 1000) / 10
        breed_evidence = [o for o in observed if o["condition_key"] == trait["condition_key"]]
        merged[trait["condition_key"]] = {
            "condition_name": trait["condition_name"],
            "condition_key": trait["condition_key"],
            "risk_percent": round_pct(nudged["risk"]),
            "risk_decimal": nudged["risk"],
            "trait_risk_percent": trait["final_trait_risk_percent"],
            "breed_prevalence_percent": (
                round_pct(max(b["prevalence"] for b in breed_evidence)) if breed_evidence else None
            ),
            "confidence_percent": trait["confidence_percent"],
            "evidence_count": trait["evidence_count"],
            "supporting_traits": trait["supporting_traits"],
            "interaction_adjustment_percent": js_round((trait["interaction_factor"] - 1) * 1000) / 10,
            "benefit_adjustment_percent": (
                js_round((1 - trait["benefit_factor"]) * 1000) / 10 if trait.get("benefit_applied") else 0
            ),
            "mixed_breed_adjustment_percent": mixed_pct,
            "mixed_breed_factor": nudged["mixed_breed_factor"],
            "logic": "mixed_trait_estimate",
            "groomer_boosted": groomer_boosted,
            "trait_explanation": trait,
            "mixed_breed_sources": nudged["mixed_breed_sources"],
            "breed_evidence": breed_evidence,
            "source": (
                {
                    "source_name": breed_evidence[0].get("source_name"),
                    "source_quote": breed_evidence[0].get("source_quote"),
                    "source_url": breed_evidence[0].get("source_url"),
                    "breed": " × ".join(b["breed_name"] for b in breed_evidence),
                }
                if breed_evidence
                else None
            ),
        }

    for obs in observed:
        groomer_boosted = bool(groomer_boosts.get(obs["condition_key"]))
        existing = merged.get(obs["condition_key"])
        if existing:
            union_prev = max(existing["risk_decimal"], obs["prevalence"])
            existing["risk_decimal"] = clamp_risk(union_prev)
            existing["risk_percent"] = round_pct(existing["risk_decimal"])
            existing["breed_prevalence_percent"] = max(
                existing["breed_prevalence_percent"] or 0,
                round_pct(obs["prevalence"]),
            )
            existing["breed_evidence"] = [*(existing.get("breed_evidence") or []), obs]
            existing["logic"] = "mixed_breed_union"
            existing["groomer_boosted"] = existing["groomer_boosted"] or groomer_boosted
            continue

        ctx = build_trait_context(obs["condition_key"])
        merged[obs["condition_key"]] = {
            "condition_name": obs["condition_name"],
            "condition_key": obs["condition_key"],
            "risk_percent": round_pct(obs["prevalence"]),
            "risk_decimal": clamp_risk(obs["prevalence"]),
            "trait_risk_percent": None if not ctx else ctx["trait_risk_percent"],
            "breed_prevalence_percent": round_pct(obs["prevalence"]),
            "confidence_percent": 0 if not ctx else ctx["confidence_percent"],
            "evidence_count": 0 if not ctx else ctx["evidence_count"],
            "supporting_traits": [] if not ctx else ctx["supporting_traits"],
            "interaction_adjustment_percent": 0 if not ctx else ctx["interaction_adjustment_percent"],
            "benefit_adjustment_percent": 0 if not ctx else ctx["benefit_adjustment_percent"],
            "mixed_breed_adjustment_percent": 0,
            "mixed_breed_factor": 1,
            "logic": "mixed_breed_union",
            "groomer_boosted": groomer_boosted,
            "trait_explanation": trait_map.get(obs["condition_key"]),
            "mixed_breed_sources": [],
            "breed_evidence": [obs],
            "source": {
                "source_name": obs.get("source_name"),
                "source_quote": obs.get("source_quote"),
                "source_url": obs.get("source_url"),
                "breed": obs.get("breed_name"),
            },
        }

    positives = [t["final_trait_risk"] for t in trait_scores if t["final_trait_risk"] > 0]
    anchor = min(positives) if positives else 0.05

    results = [
        r for r in merged.values()
        if r["risk_decimal"] >= anchor or r["groomer_boosted"]
    ]
    results.sort(key=lambda a: (-int(a["groomer_boosted"]), -a["risk_percent"]))
    return results


def compute_risks(repo: DataRepository, profile: DogProfileInput) -> dict[str, Any]:
    breed_names = [profile.primary_breed]
    if profile.secondary_breed:
        breed_names.append(profile.secondary_breed)

    breeds = _breed_records(repo, breed_names)
    resolved_names = [b["breed_name"] for b in breeds] or breed_names

    trait_risks = collect_trait_risks(repo, breeds)
    evidence = compute_evidence_scores(trait_risks, breeds, repo)
    with_benefits = apply_benefit_reductions(evidence, breeds, repo)
    final_risks = apply_significance_logic(
        breeds,
        resolved_names,
        with_benefits,
        list(profile.observed_conditions or []),
        repo,
    )

    age_years = float(profile.age_years)
    stage = "puppy" if age_years < 1 else ("senior" if age_years >= 7 else "adult")
    if stage == "senior":
        for r in final_risks:
            r["risk_decimal"] = clamp_risk(r["risk_decimal"] * 1.05)
            r["risk_percent"] = round_pct(r["risk_decimal"])
            r["age_adjusted"] = True

    return {
        "risks": final_risks,
        "resolved_breeds": breeds,
        "meta": {
            "ageYears": round(age_years * 10) / 10,
            "ageStage": stage,
            "breedCount": len(breeds),
            "breeds": resolved_names,
        },
    }
