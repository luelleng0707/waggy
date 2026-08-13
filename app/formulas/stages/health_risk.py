"""
Health-risk pipeline — ports src/engine/{traitResolver,overlapEngine,benefitEngine,significanceEngine,riskEngine}.js

Goal: identical risk ranking, confidence, mixed-breed factors, and groomer boosts for parity.
"""

from __future__ import annotations

import copy
import math
import re
from typing import Any

import pandas as pd

from app.agent.formula_trace import (
    TRAIT_TABLE_FILES,
    confidence_factor,
    decision,
    empty_execution,
    lookup_competition,
    lookup_row,
    modifier,
    seal_execution,
    start_timer,
    step,
)
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, js_round, normalize_breed_name, parse_prevalence
from app.inference.config import (
    DEFAULT_CATEGORY_WEIGHTS,
    DEFAULT_GROOMER_MAP,
    category_weights,
    groomer_map,
)

# Parity defaults (also seeded in data/inference/*.csv). Prefer runtime loaders below.
CATEGORY_WEIGHTS = DEFAULT_CATEGORY_WEIGHTS
TOTAL_TRAIT_CATEGORIES = len(CATEGORY_WEIGHTS)
INTERACTION_MIN = 0.80
INTERACTION_MAX = 1.20

GROOMER_MAP = DEFAULT_GROOMER_MAP


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
    Attaches lookup provenance (_csv_file, _csv_row, primary_key) for formula execution.
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
        for _, r in tables.iterrows():
            category = r.get("trait_category")
            value = trait_values.get(str(category))
            if not value or r.get("trait_value") != value:
                continue
            cond = r.get("condition")
            csv_file = r.get("_csv_file") or TRAIT_TABLE_FILES.get(str(category), "TRAIT_CONDITIONS.csv")
            csv_row = r.get("_csv_row")
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
                "_csv_file": csv_file,
                "_csv_row": csv_row,
                "_primary_key": {
                    "trait_category": category,
                    "trait_value": value,
                    "condition": cond,
                },
            })
    return all_rows


def compute_evidence_scores(trait_risks: list[dict[str, Any]], breeds: list[dict[str, Any]], repo: DataRepository) -> list[dict[str, Any]]:
    by_condition: dict[str, dict[str, Any]] = {}
    for row in trait_risks:
        key = row["condition_key"] or row["condition_name"]
        if key not in by_condition:
            by_condition[key] = {"condition_name": row["condition_name"], "by_category": {}, "raw_lookups": []}
        by_condition[key]["raw_lookups"].append(row)
        cat = row["trait_category"]
        prev = float(row["prevalence"])
        existing = by_condition[key]["by_category"].get(cat)
        if not existing or prev > existing["prevalence"]:
            by_condition[key]["by_category"][cat] = {
                "trait_category": cat,
                "trait_value": row["trait_value"],
                "prevalence": prev,
                "weight": category_weights().get(cat, 1.0),
                "source_name": row.get("source_name"),
                "source_quote": row.get("source_quote"),
                "source_url": row.get("source_url"),
                "_csv_file": row.get("_csv_file"),
                "_csv_row": row.get("_csv_row"),
                "_primary_key": row.get("_primary_key"),
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
        # JS overlapEngine: reduce from 0 (classic float fold), not Python sum()
        base_sum = 0.0
        for e in evidence:
            base_sum += float(e["prevalence"] or 0)
        base_risk = clamp_risk(base_sum)
        confidence_percent = js_round((len(evidence) / TOTAL_TRAIT_CATEGORIES) * 1000) / 10

        factor = 1.0
        applied = []
        interaction_lookups = []
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
                f = m.get("factor", 1.0)
                if "interaction" in m and pd.notna(m.get("interaction")) and str(m.get("interaction")).lower() not in ("", "nan"):
                    pass
                factor *= clamp_interaction_factor(f)
                row_dict = m.to_dict()
                applied.append(row_dict)
                interaction_lookups.append(
                    lookup_row(
                        table=str(m.get("_csv_file") or "TRAIT_INTERACTIONS.csv"),
                        primary_key={
                            "trait_a": m.get("trait_a"),
                            "trait_b": m.get("trait_b"),
                            "condition": m.get("condition"),
                        },
                        columns={
                            "factor": m.get("factor"),
                            "interaction": m.get("interaction"),
                        },
                        csv_row=m.get("_csv_row"),
                        csv_file=str(m.get("_csv_file") or "TRAIT_INTERACTIONS.csv"),
                        decision="applied",
                    )
                )
            factor = clamp_interaction_factor(factor)

        after = clamp_risk(base_risk * factor)
        base_pct = round_pct(base_risk)
        after_pct = round_pct(after)

        t0 = start_timer()
        # --- Formula execution ledger (built inside the engine) ---
        competitions = []
        trait_lookups = []
        for e in evidence:
            cat = e.get("trait_category")
            cat_candidates = [
                raw
                for raw in (payload.get("raw_lookups") or [])
                if raw.get("trait_category") == cat
            ]
            cand_lookups = [
                lookup_row(
                    table=str(c.get("_csv_file") or TRAIT_TABLE_FILES.get(str(cat), "TRAIT_CONDITIONS.csv")),
                    primary_key=c.get("_primary_key") or {
                        "trait_category": c.get("trait_category"),
                        "trait_value": c.get("trait_value"),
                        "condition": payload["condition_name"],
                    },
                    columns={
                        "prevalence": c.get("prevalence"),
                        "prevalence_percent": round_pct(float(c.get("prevalence") or 0)),
                        "source_breed": c.get("source_breed"),
                        "source_name": c.get("source_name"),
                    },
                    csv_row=c.get("_csv_row"),
                    csv_file=str(c.get("_csv_file") or TRAIT_TABLE_FILES.get(str(cat), "TRAIT_CONDITIONS.csv")),
                    evidence_id=c.get("source_name"),
                    decision=(
                        "selected_max_per_category"
                        if (
                            c.get("trait_value") == e.get("trait_value")
                            and float(c.get("prevalence") or 0) == float(e.get("prevalence") or 0)
                        )
                        else "skipped_lower_than_category_max"
                    ),
                )
                for c in cat_candidates
            ] or [
                lookup_row(
                    table=str(e.get("_csv_file") or TRAIT_TABLE_FILES.get(str(cat), "TRAIT_CONDITIONS.csv")),
                    primary_key=e.get("_primary_key")
                    or {
                        "trait_category": e.get("trait_category"),
                        "trait_value": e.get("trait_value"),
                        "condition": payload["condition_name"],
                    },
                    columns={
                        "prevalence": e.get("prevalence"),
                        "prevalence_percent": round_pct(float(e.get("prevalence") or 0)),
                        "source_name": e.get("source_name"),
                    },
                    csv_row=e.get("_csv_row"),
                    csv_file=str(e.get("_csv_file") or TRAIT_TABLE_FILES.get(str(cat), "TRAIT_CONDITIONS.csv")),
                    evidence_id=e.get("source_name"),
                    decision="selected_max_per_category",
                )
            ]
            selected_lu = next(
                (lu for lu in cand_lookups if lu.get("decision") == "selected_max_per_category"),
                cand_lookups[0] if cand_lookups else None,
            )
            trait_lookups.extend(cand_lookups)
            if len(cand_lookups) > 1:
                competitions.append(
                    lookup_competition(
                        purpose=f"max prevalence within trait category `{cat}`",
                        candidates=cand_lookups,
                        selected=selected_lu,
                        reason="Highest prevalence wins per trait category (JS parity)",
                    )
                )

        exec_ledger = empty_execution("RISK_V2_1", condition=str(payload["condition_name"]))
        exec_ledger["inputs"] = {
            "breeds": [b.get("breed_name") for b in breeds],
            "trait_values": sorted(trait_values),
            "condition_key": key,
        }
        exec_ledger["lookups"] = trait_lookups + interaction_lookups
        exec_ledger["competitions"] = competitions
        step_n = 1
        exec_ledger["steps"].append(
            step(
                step_n,
                "load_trait_prevalence",
                expression="lookup trait_condition tables for each breed trait value",
                inputs={"matched_rows": len(trait_lookups), "selected_categories": len(evidence)},
                result=len(evidence),
                lookups=trait_lookups,
                note="Per trait category, keep the max prevalence across breeds",
            )
        )
        step_n += 1
        values_pct = [round_pct(float(e["prevalence"] or 0)) for e in evidence]
        exec_ledger["steps"].append(
            step(
                step_n,
                "aggregate_base_risk",
                expression="clamp(sum(prevalence_i))  # NOT mean — JS parity fold",
                inputs=values_pct,
                before=0,
                after=base_pct,
                result=base_pct,
                unit="%",
            )
        )
        step_n += 1
        if applied:
            exec_ledger["steps"].append(
                step(
                    step_n,
                    "apply_interaction_factor",
                    expression="clamp(base_risk * product(interaction_factors), 0.8..1.2 per factor)",
                    inputs={"factors": [a.get("factor") for a in applied], "product": factor},
                    before=base_pct,
                    after=after_pct,
                    result=after_pct,
                    unit="%",
                    lookups=interaction_lookups,
                )
            )
            exec_ledger["modifiers"].append(
                modifier(
                    "trait_interaction",
                    source_table="TRAIT_INTERACTIONS.csv",
                    effect=f"×{factor}",
                    op="multiply",
                    value=factor,
                    running_total_before=base_pct,
                    running_total_after=after_pct,
                    details=applied,
                )
            )
            exec_ledger["decisions"].append(
                decision(
                    "Applied",
                    subject="TRAIT_INTERACTIONS",
                    reasons=[f"Matched {len(applied)} non-neutral interaction row(s)"],
                    details={"factor": factor},
                )
            )
            step_n += 1
        else:
            exec_ledger["steps"].append(
                step(
                    step_n,
                    "apply_interaction_factor",
                    expression="no matching TRAIT_INTERACTIONS rows (or all neutral)",
                    before=base_pct,
                    after=after_pct,
                    result=after_pct,
                    unit="%",
                )
            )
            exec_ledger["decisions"].append(
                decision(
                    "Skipped",
                    subject="TRAIT_INTERACTIONS",
                    reasons=["No matching non-neutral interaction rows for this condition"],
                )
            )
            step_n += 1

        # Confidence: coverage of trait categories only (production algorithm)
        conf = [
            confidence_factor(
                "trait_categories_with_evidence",
                delta=confidence_percent,
                running=confidence_percent,
                value=len(evidence),
                denominator=TOTAL_TRAIT_CATEGORIES,
                expression=f"round(len(evidence) / {TOTAL_TRAIT_CATEGORIES} * 100, 1)",
                note="Production confidence is category coverage only — not a study-quality ladder",
            )
        ]
        exec_ledger["confidence"] = conf
        exec_ledger["confidence_steps"] = conf
        exec_ledger["outputs"] = {
            "base_risk_percent": base_pct,
            "interaction_factor": factor,
            "risk_after_interaction_percent": after_pct,
            "confidence_percent": confidence_percent,
            "evidence_count": len(evidence),
        }
        seal_execution(exec_ledger, started=t0)

        results.append({
            "condition_name": payload["condition_name"],
            "condition_key": key,
            "trait_evidence": evidence,
            "base_risk": round(base_risk * 10000) / 10000,
            "base_risk_percent": base_pct,
            "confidence_percent": confidence_percent,
            "evidence_count": len(evidence),
            "supporting_traits": [
                {"category": e["trait_category"], "value": e["trait_value"], "prevalence_percent": round_pct(e["prevalence"])}
                for e in evidence
            ],
            "interaction_factor": factor,
            "interactions_applied": applied,
            "risk_after_interaction": after,
            "risk_after_interaction_percent": after_pct,
            "formula_execution": exec_ledger,
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
        benefit_lookup = None
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
                benefit_lookup = lookup_row(
                    table=str(hits.iloc[0].get("_csv_file") or "TRAIT_BENEFITS.csv"),
                    primary_key={
                        "trait_a": benefit.get("trait_a"),
                        "trait_b": benefit.get("trait_b"),
                        "condition": benefit.get("condition"),
                    },
                    columns={"reduction_factor": benefit.get("reduction_factor")},
                    csv_row=hits.iloc[0].get("_csv_row"),
                    decision="applied",
                )

        exec_ledger = dict(risk.get("formula_execution") or empty_execution("RISK_V2_1", condition=risk.get("condition_name")))
        before_pct = risk["risk_after_interaction_percent"]
        step_n = len(exec_ledger.get("steps") or []) + 1

        if not benefit:
            exec_ledger["steps"] = list(exec_ledger.get("steps") or [])
            exec_ledger["steps"].append(
                step(
                    step_n,
                    "apply_benefit_reduction",
                    expression="no matching TRAIT_BENEFITS row",
                    before=before_pct,
                    after=before_pct,
                    result=before_pct,
                    unit="%",
                )
            )
            out.append({
                **risk,
                "benefit_factor": 1,
                "benefit_applied": None,
                "final_trait_risk": risk["risk_after_interaction"],
                "final_trait_risk_percent": risk["risk_after_interaction_percent"],
                "formula_execution": exec_ledger,
            })
            continue

        factor = float(benefit.get("reduction_factor") or 1)
        final = clamp_risk(risk["risk_after_interaction"] * factor)
        after_pct = round_pct(final)
        exec_ledger["steps"] = list(exec_ledger.get("steps") or [])
        exec_ledger["lookups"] = list(exec_ledger.get("lookups") or [])
        if benefit_lookup:
            exec_ledger["lookups"].append(benefit_lookup)
        exec_ledger["steps"].append(
            step(
                step_n,
                "apply_benefit_reduction",
                expression="clamp(risk_after_interaction * reduction_factor)",
                inputs={"reduction_factor": factor},
                before=before_pct,
                after=after_pct,
                result=after_pct,
                unit="%",
                lookups=[benefit_lookup] if benefit_lookup else [],
            )
        )
        exec_ledger["modifiers"] = list(exec_ledger.get("modifiers") or [])
        exec_ledger["modifiers"].append(
            modifier(
                "benefit_reduction",
                source_table="TRAIT_BENEFITS.csv",
                source_row=benefit_lookup.get("csv_row") if benefit_lookup else None,
                primary_key=benefit_lookup.get("primary_key") if benefit_lookup else {},
                effect=f"×{factor}",
                op="multiply",
                value=factor,
                running_total_before=before_pct,
                running_total_after=after_pct,
                details=benefit,
            )
        )
        exec_ledger["outputs"] = {
            **(exec_ledger.get("outputs") or {}),
            "benefit_factor": factor,
            "final_trait_risk_percent": after_pct,
        }
        out.append({
            **risk,
            "benefit_factor": factor,
            "benefit_applied": benefit,
            "final_trait_risk": final,
            "final_trait_risk_percent": after_pct,
            "formula_execution": exec_ledger,
        })
    return out


def resolve_groomer_boosts(observed_conditions: list[str]) -> dict[str, bool]:
    boosts: dict[str, bool] = {}
    for obs in observed_conditions:
        raw = re.sub(r"\s+", "_", str(obs or "").lower())
        condition = groomer_map().get(raw)
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
    empty = {
        "risk": trait_risk_decimal,
        "mixed_breed_factor": 1,
        "mixed_breed_sources": [],
        "lookups": [],
    }
    if matrix.empty or len(breed_names) < 2:
        return empty

    pairs = []
    for i in range(len(breed_names)):
        for j in range(i + 1, len(breed_names)):
            pairs.append((breed_names[i], breed_names[j]))

    rows = []
    lookups = []
    for _, mb in matrix.iterrows():
        a = str(mb.get("breed_a", ""))
        b = str(mb.get("breed_b", ""))
        cond = condition_key(str(mb.get("condition", "")))
        if cond != condition_key_val:
            continue
        for x, y in pairs:
            if (a.lower() == x.lower() and b.lower() == y.lower()) or (a.lower() == y.lower() and b.lower() == x.lower()):
                row = mb.to_dict()
                rows.append(row)
                lookups.append(
                    lookup_row(
                        table=str(mb.get("_csv_file") or "MIXED_BREED_MATRIX.csv"),
                        primary_key={"breed_a": a, "breed_b": b, "condition": mb.get("condition")},
                        columns={"factor": mb.get("factor")},
                        csv_row=mb.get("_csv_row"),
                        decision="applied",
                    )
                )
                break

    if not rows:
        return empty

    factor = 1.0
    for row in rows:
        f = float(row.get("factor") or 1)
        factor *= min(1.20, max(0.80, f))
    factor = min(1.20, max(0.80, factor))
    return {
        "risk": clamp_risk(trait_risk_decimal * factor),
        "mixed_breed_factor": factor,
        "mixed_breed_sources": rows,
        "lookups": lookups,
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
            "_csv_file": r.get("_csv_file") or "BREED_CONDITIONS.csv",
            "_csv_row": r.get("_csv_row"),
            "_primary_key": {"breed": r.get("breed"), "condition": r.get("condition")},
        })
    return out


def _clone_execution(trait: dict[str, Any] | None, condition_name: str) -> dict[str, Any]:
    base = (trait or {}).get("formula_execution") if isinstance(trait, dict) else None
    if isinstance(base, dict):
        return copy.deepcopy(base)
    return empty_execution("RISK_V2_1", condition=condition_name)


def _append_exec_step(exec_ledger: dict[str, Any], **kwargs: Any) -> None:
    steps = list(exec_ledger.get("steps") or [])
    n = len(steps) + 1
    steps.append(step(n, **kwargs))
    exec_ledger["steps"] = steps


def _breed_obs_lookups(obs_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for obs in obs_list:
        out.append(
            lookup_row(
                table=str(obs.get("_csv_file") or "BREED_CONDITIONS.csv"),
                primary_key=obs.get("_primary_key")
                or {"breed": obs.get("breed_name"), "condition": obs.get("condition_name")},
                columns={
                    "prevalence": obs.get("prevalence"),
                    "source_name": obs.get("source_name"),
                },
                csv_row=obs.get("_csv_row"),
                decision="selected",
            )
        )
    return out


def _finalize_execution_outputs(exec_ledger: dict[str, Any], risk_row: dict[str, Any]) -> None:
    exec_ledger["outputs"] = {
        **(exec_ledger.get("outputs") or {}),
        "final_risk_percent": risk_row.get("risk_percent"),
        "confidence_percent": risk_row.get("confidence_percent"),
        "logic": risk_row.get("logic"),
        "groomer_boosted": bool(risk_row.get("groomer_boosted")),
    }
    # Ensure confidence alias + provenance refreshed for final outputs
    if exec_ledger.get("confidence") and not exec_ledger.get("confidence_steps"):
        exec_ledger["confidence_steps"] = exec_ledger["confidence"]
    elif exec_ledger.get("confidence_steps") and not exec_ledger.get("confidence"):
        exec_ledger["confidence"] = exec_ledger["confidence_steps"]
    seal_execution(exec_ledger)



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
            trait = trait_map.get(obs["condition_key"])
            before_pct = (trait or {}).get("final_trait_risk_percent")
            after_pct = round_pct(obs["prevalence"])
            exec_ledger = _clone_execution(trait, str(obs["condition_name"]))
            breed_lookups = _breed_obs_lookups([obs])
            exec_ledger["lookups"] = list(exec_ledger.get("lookups") or []) + breed_lookups
            _append_exec_step(
                exec_ledger,
                name="select_purebred_breed_prevalence",
                expression="risk = BREED_CONDITIONS.prevalence (overrides trait estimate for purebred)",
                inputs={"breed": obs.get("breed_name"), "prevalence": obs.get("prevalence")},
                before=before_pct,
                after=after_pct,
                result=after_pct,
                unit="%",
                lookups=breed_lookups,
                note="logic=purebred_observed",
            )
            if groomer_boosted:
                _append_exec_step(
                    exec_ledger,
                    name="groomer_observation_boost",
                    expression="flag groomer_boosted (sort priority; does not change risk %)",
                    result=True,
                    note="Observation matched groomer map",
                )
            row = {
                "condition_name": obs["condition_name"],
                "condition_key": obs["condition_key"],
                "risk_percent": after_pct,
                "risk_decimal": clamp_risk(obs["prevalence"]),
                "breed_prevalence_percent": after_pct,
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
                "trait_explanation": trait,
                "breed_evidence": [obs],
                "source": {
                    "source_name": obs.get("source_name"),
                    "source_quote": obs.get("source_quote"),
                    "source_url": obs.get("source_url"),
                    "breed": obs.get("breed_name"),
                },
            }
            _finalize_execution_outputs(exec_ledger, row)
            row["formula_execution"] = exec_ledger
            results.append(row)
        results.sort(key=lambda a: (-int(a["groomer_boosted"]), -a["risk_percent"]))
        return results

    merged: dict[str, dict[str, Any]] = {}
    for trait in trait_scores:
        nudged = apply_mixed_breed_nudge(trait["final_trait_risk"], trait["condition_key"], breed_names, repo)
        groomer_boosted = bool(groomer_boosts.get(trait["condition_key"]))
        mixed_pct = js_round((nudged["mixed_breed_factor"] - 1) * 1000) / 10
        breed_evidence = [o for o in observed if o["condition_key"] == trait["condition_key"]]
        before_pct = trait["final_trait_risk_percent"]
        after_pct = round_pct(nudged["risk"])
        exec_ledger = _clone_execution(trait, str(trait["condition_name"]))
        mb_lookups = list(nudged.get("lookups") or [])
        if mb_lookups:
            exec_ledger["lookups"] = list(exec_ledger.get("lookups") or []) + mb_lookups
        _append_exec_step(
            exec_ledger,
            name="apply_mixed_breed_nudge",
            expression="clamp(final_trait_risk * mixed_breed_factor)  # factors clamped 0.8..1.2",
            inputs={"mixed_breed_factor": nudged["mixed_breed_factor"], "breed_names": breed_names},
            before=before_pct,
            after=after_pct,
            result=after_pct,
            unit="%",
            lookups=mb_lookups,
        )
        if float(nudged["mixed_breed_factor"] or 1) != 1.0:
            exec_ledger["modifiers"] = list(exec_ledger.get("modifiers") or [])
            exec_ledger["modifiers"].append(
                modifier(
                    "mixed_breed",
                    source_table="MIXED_BREED_MATRIX.csv",
                    effect=f"×{nudged['mixed_breed_factor']}",
                    op="multiply",
                    value=nudged["mixed_breed_factor"],
                    running_total_before=before_pct,
                    running_total_after=after_pct,
                    details=nudged["mixed_breed_sources"],
                )
            )
        breed_lookups = _breed_obs_lookups(breed_evidence)
        if breed_lookups:
            exec_ledger["lookups"] = list(exec_ledger.get("lookups") or []) + breed_lookups
        if groomer_boosted:
            _append_exec_step(
                exec_ledger,
                name="groomer_observation_boost",
                expression="flag groomer_boosted (sort priority; does not change risk %)",
                result=True,
            )
        row = {
            "condition_name": trait["condition_name"],
            "condition_key": trait["condition_key"],
            "risk_percent": after_pct,
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
            "formula_execution": exec_ledger,
        }
        _finalize_execution_outputs(exec_ledger, row)
        merged[trait["condition_key"]] = row

    for obs in observed:
        groomer_boosted = bool(groomer_boosts.get(obs["condition_key"]))
        existing = merged.get(obs["condition_key"])
        if existing:
            before_pct = existing["risk_percent"]
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
            exec_ledger = existing.get("formula_execution") or _clone_execution(
                existing.get("trait_explanation"), str(existing["condition_name"])
            )
            breed_lookups = _breed_obs_lookups([obs])
            exec_ledger["lookups"] = list(exec_ledger.get("lookups") or []) + breed_lookups
            _append_exec_step(
                exec_ledger,
                name="mixed_breed_union",
                expression="max(trait_or_mixed_risk, breed_prevalence)",
                inputs={"breed_prevalence": obs.get("prevalence"), "prior_risk": before_pct},
                before=before_pct,
                after=existing["risk_percent"],
                result=existing["risk_percent"],
                unit="%",
                lookups=breed_lookups,
            )
            _finalize_execution_outputs(exec_ledger, existing)
            existing["formula_execution"] = exec_ledger
            continue

        ctx = build_trait_context(obs["condition_key"])
        trait = trait_map.get(obs["condition_key"])
        after_pct = round_pct(obs["prevalence"])
        exec_ledger = _clone_execution(trait, str(obs["condition_name"]))
        breed_lookups = _breed_obs_lookups([obs])
        exec_ledger["lookups"] = list(exec_ledger.get("lookups") or []) + breed_lookups
        _append_exec_step(
            exec_ledger,
            name="breed_observed_only",
            expression="risk = BREED_CONDITIONS.prevalence (no trait score for this condition)",
            inputs={"breed": obs.get("breed_name"), "prevalence": obs.get("prevalence")},
            before=None,
            after=after_pct,
            result=after_pct,
            unit="%",
            lookups=breed_lookups,
            note="logic=mixed_breed_union (observed-only branch)",
        )
        row = {
            "condition_name": obs["condition_name"],
            "condition_key": obs["condition_key"],
            "risk_percent": after_pct,
            "risk_decimal": clamp_risk(obs["prevalence"]),
            "trait_risk_percent": None if not ctx else ctx["trait_risk_percent"],
            "breed_prevalence_percent": after_pct,
            "confidence_percent": 0 if not ctx else ctx["confidence_percent"],
            "evidence_count": 0 if not ctx else ctx["evidence_count"],
            "supporting_traits": [] if not ctx else ctx["supporting_traits"],
            "interaction_adjustment_percent": 0 if not ctx else ctx["interaction_adjustment_percent"],
            "benefit_adjustment_percent": 0 if not ctx else ctx["benefit_adjustment_percent"],
            "mixed_breed_adjustment_percent": 0,
            "mixed_breed_factor": 1,
            "logic": "mixed_breed_union",
            "groomer_boosted": groomer_boosted,
            "trait_explanation": trait,
            "mixed_breed_sources": [],
            "breed_evidence": [obs],
            "source": {
                "source_name": obs.get("source_name"),
                "source_quote": obs.get("source_quote"),
                "source_url": obs.get("source_url"),
                "breed": obs.get("breed_name"),
            },
            "formula_execution": exec_ledger,
        }
        _finalize_execution_outputs(exec_ledger, row)
        merged[obs["condition_key"]] = row

    positives = [t["final_trait_risk"] for t in trait_scores if t["final_trait_risk"] > 0]
    anchor = min(positives) if positives else 0.05

    results = [
        r for r in merged.values()
        if r["risk_decimal"] >= anchor or r["groomer_boosted"]
    ]
    results.sort(key=lambda a: (-int(a["groomer_boosted"]), -a["risk_percent"]))
    return results


def build_observatory_risk_trace(risk: dict[str, Any]) -> dict[str, Any]:
    """
    Serialize RISK_V2_1 intermediates already on the risk row (observability only).

    Does not recompute. Omits modifiers the engine never applies (activity/weight/climate).
    """
    te = risk.get("trait_explanation") if isinstance(risk.get("trait_explanation"), dict) else {}
    steps: list[dict[str, Any]] = []

    if te.get("base_risk_percent") is not None:
        steps.append(
            {
                "name": "baseline_trait_evidence",
                "label": "Baseline (trait evidence)",
                "op": "baseline",
                "value": te.get("base_risk_percent"),
                "unit": "%",
                "traceable": True,
                "source": "trait_explanation.base_risk_percent",
                "formula_id": "RISK_V2_1",
            }
        )
    elif risk.get("breed_prevalence_percent") is not None:
        steps.append(
            {
                "name": "baseline_breed_prevalence",
                "label": "Baseline (breed prevalence)",
                "op": "baseline",
                "value": risk.get("breed_prevalence_percent"),
                "unit": "%",
                "traceable": True,
                "source": "breed_prevalence_percent / BREED_CONDITIONS",
                "formula_id": "RISK_V2_1",
                "csv": "BREED_CONDITIONS.csv",
            }
        )

    if te.get("interaction_factor") is not None:
        steps.append(
            {
                "name": "interaction",
                "label": "Trait interaction",
                "op": "multiply",
                "value": te.get("interaction_factor"),
                "unit": "×",
                "after_percent": te.get("risk_after_interaction_percent"),
                "adjustment_percent": risk.get("interaction_adjustment_percent"),
                "traceable": True,
                "source": "trait_explanation.interaction_factor / TRAIT_INTERACTIONS",
                "formula_id": "RISK_V2_1",
                "csv": "TRAIT_INTERACTIONS.csv",
                "details": te.get("interactions_applied") or [],
            }
        )

    if te.get("benefit_factor") is not None and (
        te.get("benefit_applied") or float(te.get("benefit_factor") or 1) != 1.0
    ):
        steps.append(
            {
                "name": "benefit",
                "label": "Benefit reduction",
                "op": "multiply",
                "value": te.get("benefit_factor"),
                "unit": "×",
                "after_percent": te.get("final_trait_risk_percent"),
                "adjustment_percent": risk.get("benefit_adjustment_percent"),
                "traceable": True,
                "source": "trait_explanation.benefit_factor / TRAIT_BENEFITS",
                "formula_id": "RISK_V2_1",
                "csv": "TRAIT_BENEFITS.csv",
                "details": te.get("benefit_applied") or [],
            }
        )

    mb = risk.get("mixed_breed_factor")
    if mb is not None and float(mb) != 1.0:
        steps.append(
            {
                "name": "mixed_breed",
                "label": "Mixed-breed nudge",
                "op": "multiply",
                "value": mb,
                "unit": "×",
                "adjustment_percent": risk.get("mixed_breed_adjustment_percent"),
                "traceable": True,
                "source": "mixed_breed_factor / MIXED_BREED_MATRIX",
                "formula_id": "RISK_V2_1",
                "csv": "MIXED_BREED_MATRIX.csv",
                "details": risk.get("mixed_breed_sources") or [],
            }
        )

    if risk.get("age_adjusted"):
        steps.append(
            {
                "name": "age_senior",
                "label": "Senior age adjustment",
                "op": "multiply",
                "value": 1.05,
                "unit": "×",
                "traceable": True,
                "source": "compute_risks senior branch (age_years >= 7)",
                "formula_id": "RISK_V2_1",
                "note": "Factor applied in production; not a separate CSV",
            }
        )

    # Explicitly document modifiers this engine does not apply (do not invent values)
    for name, label in (
        ("activity", "Activity modifier"),
        ("weight", "Weight modifier"),
        ("climate", "Climate modifier"),
    ):
        steps.append(
            {
                "name": name,
                "label": label,
                "op": "none",
                "value": None,
                "traceable": False,
                "status": "NOT_APPLIED_IN_RISK_V2_1",
                "reason": f"{label} is not part of the locked health_risk path",
                "formula_id": "RISK_V2_1",
            }
        )

    steps.append(
        {
            "name": "final",
            "label": "Final risk",
            "op": "set",
            "value": risk.get("risk_percent"),
            "unit": "%",
            "traceable": risk.get("risk_percent") is not None,
            "source": "risk_percent after significance + optional age",
            "formula_id": "RISK_V2_1",
        }
    )

    csv_refs: list[dict[str, Any]] = []
    for be in risk.get("breed_evidence") or []:
        if isinstance(be, dict):
            csv_refs.append(
                {
                    "csv": "BREED_CONDITIONS.csv",
                    "breed": be.get("breed_name") or be.get("breed"),
                    "condition": be.get("condition_name") or risk.get("condition_name"),
                    "column": "prevalence",
                    "value": be.get("prevalence"),
                    "source_name": be.get("source_name"),
                    "row_id": be.get("_csv_row"),
                    "csv_row": be.get("_csv_row"),
                    "primary_key": be.get("_primary_key")
                    or {"breed": be.get("breed_name"), "condition": be.get("condition_name") or risk.get("condition_name")},
                    "file": be.get("_csv_file") or "BREED_CONDITIONS.csv",
                }
            )
    src = risk.get("source") if isinstance(risk.get("source"), dict) else {}
    if src.get("source_name") and not csv_refs:
        csv_refs.append(
            {
                "csv": "BREED_CONDITIONS.csv",
                "condition": risk.get("condition_name"),
                "column": "prevalence",
                "value": risk.get("breed_prevalence_percent"),
                "source_name": src.get("source_name"),
                "source_url": src.get("source_url"),
                "row_id": "NOT CURRENTLY TRACEABLE",
            }
        )

    return {
        "formula_id": "RISK_V2_1",
        "condition": risk.get("condition_name"),
        "condition_key": risk.get("condition_key"),
        "logic": risk.get("logic"),
        "confidence_percent": risk.get("confidence_percent"),
        "groomer_boosted": bool(risk.get("groomer_boosted")),
        "final_probability_pct": risk.get("risk_percent"),
        "steps": steps,
        "csv_refs": csv_refs,
        "code": {
            "file": "app/agent/stages/health_risk.py",
            "functions": [
                "collect_trait_risks",
                "compute_evidence_scores",
                "apply_benefit_reductions",
                "apply_significance_logic",
                "compute_risks",
            ],
        },
        "complete_for_applied_modifiers": True,
        "note": "Trace of applied RISK_V2_1 steps only. Activity/weight/climate are not applied.",
    }


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
            before_pct = r["risk_percent"]
            r["risk_decimal"] = clamp_risk(r["risk_decimal"] * 1.05)
            r["risk_percent"] = round_pct(r["risk_decimal"])
            r["age_adjusted"] = True
            exec_ledger = r.get("formula_execution") or empty_execution(
                "RISK_V2_1", condition=str(r.get("condition_name"))
            )
            _append_exec_step(
                exec_ledger,
                name="apply_senior_age_factor",
                expression="clamp(risk * 1.05)  # age_years >= 7",
                inputs={"age_years": age_years, "factor": 1.05},
                before=before_pct,
                after=r["risk_percent"],
                result=r["risk_percent"],
                unit="%",
            )
            exec_ledger["modifiers"] = list(exec_ledger.get("modifiers") or [])
            exec_ledger["modifiers"].append(
                modifier(
                    "senior_age",
                    source_table=None,
                    effect="×1.05",
                    op="multiply",
                    value=1.05,
                    running_total_before=before_pct,
                    running_total_after=r["risk_percent"],
                )
            )
            _finalize_execution_outputs(exec_ledger, r)
            r["formula_execution"] = exec_ledger
    else:
        for r in final_risks:
            exec_ledger = r.get("formula_execution") or empty_execution(
                "RISK_V2_1", condition=str(r.get("condition_name"))
            )
            _append_exec_step(
                exec_ledger,
                name="age_stage",
                expression=f"no senior factor (age_stage={stage})",
                inputs={"age_years": age_years, "age_stage": stage},
                before=r.get("risk_percent"),
                after=r.get("risk_percent"),
                result=r.get("risk_percent"),
                unit="%",
            )
            _finalize_execution_outputs(exec_ledger, r)
            r["formula_execution"] = exec_ledger

    # Observatory: attach traces after finals are fixed (additive; does not alter numbers)
    for r in final_risks:
        r["observatory_trace"] = build_observatory_risk_trace(r)

    return {
        "risks": final_risks,
        "resolved_breeds": breeds,
        "meta": {
            "ageYears": round(age_years * 10) / 10,
            "ageStage": stage,
            "breedCount": len(breeds),
            "breeds": resolved_names,
        },
        "observatory": {
            "risk_traces": [r["observatory_trace"] for r in final_risks],
            "formula_executions": [r.get("formula_execution") for r in final_risks if r.get("formula_execution")],
            "formula_id": "RISK_V2_1",
            "code_file": "app/agent/stages/health_risk.py",
        },
    }
