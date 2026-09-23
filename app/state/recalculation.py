"""Deterministic recalculation provenance. Not scientific facts and not model prose."""

from __future__ import annotations

from typing import Any

from app.state.version import (
    WAGGY_RECALCULATION_EXPLANATION_SCHEMA,
    WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA,
)

_TIERS = ("essential", "balanced", "optimal")


def _canonical(envelope: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(envelope, dict):
        return {}
    inner = envelope.get("canonical")
    if isinstance(inner, dict) and "scientific_analysis" in inner:
        return inner
    if "scientific_analysis" in envelope or "package_optimization" in envelope:
        return envelope
    return inner if isinstance(inner, dict) else envelope


def _product_ids_and_names(row: dict[str, Any]) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    names: list[str] = []
    for item in row.get("products") or []:
        if isinstance(item, dict):
            pid = item.get("product_id")
            if pid:
                ids.append(str(pid))
            name = item.get("product_name") or item.get("name")
            if name:
                names.append(str(name))
        elif item not in (None, ""):
            ids.append(str(item))
    if not ids:
        ids = [str(item) for item in (row.get("product_ids") or []) if item not in (None, "")]
    return ids, names


def _tier_choice(options: dict[str, Any], tier: str) -> dict[str, Any]:
    rows = options.get(tier) or []
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        return {"bundle_id": None, "product_ids": [], "product_names": [], "monthly_cost": None}
    ids, names = _product_ids_and_names(rows[0])
    return {
        "bundle_id": rows[0].get("bundle_id"),
        "product_ids": ids,
        "product_names": names,
        "monthly_cost": rows[0].get("monthly_cost"),
    }


def _science_slice(canonical: dict[str, Any]) -> dict[str, Any]:
    science = canonical.get("scientific_analysis") if isinstance(canonical.get("scientific_analysis"), dict) else {}
    titles = [
        str(item.get("title"))
        for item in (science.get("findings") or [])
        if isinstance(item, dict) and item.get("title")
    ]
    nutrients: list[dict[str, Any]] = []
    for item in science.get("nutrient_targets") or []:
        if not isinstance(item, dict):
            continue
        nutrients.append(
            {
                "nutrient": item.get("nutrient") or item.get("name") or item.get("ingredient"),
                "min": item.get("min") if item.get("min") is not None else item.get("minimum"),
                "max": item.get("max") if item.get("max") is not None else item.get("maximum"),
            }
        )
    return {"finding_titles": titles, "nutrients": nutrients}


def _eligibility(canonical: dict[str, Any], envelope: dict[str, Any]) -> dict[str, Any]:
    search = ((canonical.get("package_optimization") or {}) if isinstance(canonical.get("package_optimization"), dict) else {}).get("search") or {}
    if not isinstance(search, dict):
        search = {}
    raw = search.get("preference_eligibility") or {}
    if not isinstance(raw, dict):
        raw = {}
    prefs = envelope.get("effective_preferences") if isinstance(envelope.get("effective_preferences"), dict) else {}
    return {
        "scientific": False,
        "applied": bool(raw.get("applied")),
        "ingredient_exclusions": list(raw.get("ingredient_exclusions") or prefs.get("ingredient_exclusions") or []),
        "product_exclusions": list(raw.get("product_exclusions") or prefs.get("product_exclusions") or []),
        "removed_product_ids": [str(item) for item in (raw.get("removed_product_ids") or []) if item not in (None, "")],
        "removed": list(raw.get("removed") or []),
        "candidate_count_before": raw.get("candidate_count_before"),
        "candidate_count_after": raw.get("candidate_count_after"),
    }


def recommendation_snapshot(envelope: dict[str, Any] | None) -> dict[str, Any]:
    """Compact auditable recommendation state. Not a warehouse fact."""
    env = envelope if isinstance(envelope, dict) else {}
    canonical = _canonical(env)
    options = ((canonical.get("package_optimization") or {}) if isinstance(canonical.get("package_optimization"), dict) else {}).get("package_options") or {}
    if not isinstance(options, dict):
        options = {}
    prefs = env.get("effective_preferences") if isinstance(env.get("effective_preferences"), dict) else {}
    return {
        "schema": WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA,
        "scientific": False,
        "analysis_signature": env.get("analysis_signature") or canonical.get("analysis_id"),
        "engine_version": env.get("engine_version"),
        "optimizer_version": "PACKAGE_OPTIMIZER_V2_1",
        "science": _science_slice(canonical),
        "recommendations": {tier: _tier_choice(options, tier) for tier in _TIERS},
        "eligibility": _eligibility(canonical, env),
        "monthly_budget": prefs.get("monthly_budget"),
        "llm_used": False,
    }


def snapshot_from_digest(digest: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(digest, dict):
        return None
    snap = digest.get("recommendation_snapshot")
    return snap if isinstance(snap, dict) else None


def _usable_snapshot(snapshot: dict[str, Any] | None) -> bool:
    return isinstance(snapshot, dict) and snapshot.get("schema") == WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA


def _previous_status(snapshot: dict[str, Any] | None, signature: str | None) -> str:
    if _usable_snapshot(snapshot):
        return "COMPLETE"
    if signature:
        return "INCOMPLETE"
    return "NONE"


def _preference_changes_from_snapshots(
    previous: dict[str, Any] | None,
    current: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    prev_el = (previous or {}).get("eligibility") or {}
    new_el = (current or {}).get("eligibility") or {}
    prev_ing = {str(item) for item in (prev_el.get("ingredient_exclusions") or [])}
    new_ing = {str(item) for item in (new_el.get("ingredient_exclusions") or [])}
    changes: list[dict[str, Any]] = []
    for token in sorted(new_ing - prev_ing):
        changes.append({"category": "ingredient_exclusion", "value": token, "action": "added"})
    prev_budget = (previous or {}).get("monthly_budget")
    new_budget = (current or {}).get("monthly_budget")
    if new_budget is not None and new_budget != prev_budget:
        changes.append({"category": "budget", "value": str(new_budget), "action": "replaced"})
    return changes


def _science_changed(previous: dict[str, Any] | None, current: dict[str, Any] | None) -> bool:
    return ((previous or {}).get("science") or {}) != ((current or {}).get("science") or {})


def explain_recalculation(
    *,
    previous_snapshot: dict[str, Any] | None,
    new_snapshot: dict[str, Any] | None,
    previous_signature: str | None,
    new_signature: str | None,
    preference_changes: list[dict[str, Any]] | None = None,
    engine_version: str | None = None,
) -> dict[str, Any]:
    """Machine-readable 'why it changed'. Generated by the system, never by a model."""
    current = new_snapshot if _usable_snapshot(new_snapshot) else (new_snapshot or {})
    previous_status = _previous_status(previous_snapshot, previous_signature)
    comparable = previous_status == "COMPLETE" and _usable_snapshot(new_snapshot)
    previous = previous_snapshot if comparable else None
    changes = list(preference_changes or [])
    if not changes and comparable:
        changes = _preference_changes_from_snapshots(previous, current)
    rec_changes: dict[str, Any] = {}
    for tier in _TIERS:
        prev_t = ((previous or {}).get("recommendations") or {}).get(tier) or {}
        new_t = (current.get("recommendations") or {}).get(tier) or {}
        prev_ids = [str(item) for item in (prev_t.get("product_ids") or [])]
        new_ids = [str(item) for item in (new_t.get("product_ids") or [])]
        added = sorted(set(new_ids) - set(prev_ids)) if comparable else []
        removed = sorted(set(prev_ids) - set(new_ids)) if comparable else []
        rec_changes[tier] = {
            "previous_bundle_id": prev_t.get("bundle_id") if comparable else None,
            "new_bundle_id": new_t.get("bundle_id"),
            "added_product_ids": added,
            "removed_product_ids": removed,
            "previous_monthly_cost": prev_t.get("monthly_cost") if comparable else None,
            "new_monthly_cost": new_t.get("monthly_cost"),
            "changed": bool(added or removed or (comparable and prev_t.get("bundle_id") != new_t.get("bundle_id"))),
            "comparable": comparable,
        }
    prev_el = (previous or {}).get("eligibility") or {}
    new_el = current.get("eligibility") or {}
    newly_ineligible = sorted(
        set(str(item) for item in (new_el.get("removed_product_ids") or []) if item)
        - set(str(item) for item in (prev_el.get("removed_product_ids") or []) if item)
    )
    causes: list[dict[str, Any]] = []
    facts: list[str] = []
    if previous_status == "NONE":
        causes.append({"kind": "FIRST_ANALYSIS", "scientific": False, "reason": "no_previous_analysis"})
        facts.append("No previous analysis was stored. This is the first comparable run.")
    elif previous_status == "INCOMPLETE":
        causes.append({"kind": "INCOMPLETE_PREVIOUS_SNAPSHOT", "scientific": False, "reason": "previous_digest_lacked_snapshot"})
        facts.append(
            "Previous analysis digest did not include a recommendation snapshot. "
            "Preference changes and current eligibility are still recorded."
        )
    for change in changes:
        if change.get("action") == "unchanged":
            continue
        category = change.get("category")
        value = str(change.get("value") or "")
        if category == "ingredient_exclusion" and value:
            matching = [
                row
                for row in (new_el.get("removed") or [])
                if isinstance(row, dict) and value in str(row.get("reason") or "")
            ]
            ids = [str(row.get("product_id")) for row in matching if row.get("product_id")]
            causes.append(
                {
                    "kind": "CATALOG_ELIGIBILITY",
                    "preference_category": "ingredient_exclusion",
                    "preference_value": value,
                    "ineligible_product_ids": ids or newly_ineligible,
                    "reason": f"ingredient_exclusion:{value}",
                    "scientific": False,
                }
            )
            facts.append(
                f"User preference excluded ingredient '{value}'. "
                "Matching catalog products became ineligible before PACKAGE_OPTIMIZER_V2_1 ran. "
                "This is not a scientific finding."
            )
        elif category == "budget" and value:
            causes.append(
                {
                    "kind": "BUDGET_CONSTRAINT",
                    "preference_category": "budget",
                    "preference_value": value,
                    "ineligible_product_ids": [],
                    "reason": "monthly_budget",
                    "scientific": False,
                }
            )
            facts.append(
                f"User monthly budget is {value}. Essential and balanced packages use that ceiling; "
                "optimal does not. This is a commercial constraint, not a nutrient requirement."
            )
    science_changed = _science_changed(previous, current) if comparable else False
    material = any(bool(item.get("changed")) for item in rec_changes.values())
    has_pref_cause = any(
        item.get("kind") in {"CATALOG_ELIGIBILITY", "BUDGET_CONSTRAINT"} for item in causes
    )
    if comparable:
        if science_changed:
            causes.append(
                {
                    "kind": "SCIENCE_INPUT_CHANGE",
                    "scientific": False,
                    "reason": "findings_or_nutrient_targets",
                }
            )
            facts.append(
                "Scientific findings or nutrient targets changed with the dog/profile inputs. "
                "User preferences do not rewrite warehouse facts."
            )
        else:
            facts.append("Scientific findings and nutrient targets were unchanged.")
        if rec_changes["balanced"]["changed"]:
            facts.append(
                "Recommended (balanced) package products changed. "
                f"Removed {rec_changes['balanced']['removed_product_ids'] or []}. "
                f"Added {rec_changes['balanced']['added_product_ids'] or []}."
            )
        if material and not has_pref_cause:
            causes.append(
                {
                    "kind": "DETERMINISTIC_RECOMPUTE",
                    "scientific": False,
                    "reason": "profile_or_catalog",
                }
            )
            facts.append(
                "Packages changed under PACKAGE_OPTIMIZER_V2_1 without a new ingredient exclusion "
                "or budget constraint in this comparison."
            )
        if not material and not science_changed:
            causes.append(
                {
                    "kind": "NO_MATERIAL_CHANGE",
                    "scientific": False,
                    "reason": "packages_unchanged",
                }
            )
            facts.append("Rank-1 packages did not change.")
    facts.append("PACKAGE_OPTIMIZER_V2_1 recomputed packages. An LLM did not select products.")
    return {
        "schema": WAGGY_RECALCULATION_EXPLANATION_SCHEMA,
        "scientific": False,
        "llm_used": False,
        "optimizer_version": "PACKAGE_OPTIMIZER_V2_1",
        "engine_version": engine_version or current.get("engine_version"),
        "previous_analysis_signature": previous_signature,
        "new_analysis_signature": new_signature or current.get("analysis_signature"),
        "previous_snapshot_status": previous_status,
        "analysis_changed": bool(previous_signature and new_signature and previous_signature != new_signature),
        "science_changed": science_changed,
        "preference_changes": changes,
        "eligibility": {
            "scientific": False,
            "newly_ineligible_product_ids": newly_ineligible,
            "removed": list(new_el.get("removed") or []),
        },
        "recommendation_changes": rec_changes,
        "causes": causes,
        "summary_facts": facts,
    }


def explain_from_envelopes(
    previous_envelope: dict[str, Any] | None,
    new_envelope: dict[str, Any],
    *,
    preference_changes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    previous = recommendation_snapshot(previous_envelope) if previous_envelope else None
    current = recommendation_snapshot(new_envelope)
    return explain_recalculation(
        previous_snapshot=previous,
        new_snapshot=current,
        previous_signature=(previous or {}).get("analysis_signature") if previous else None,
        new_signature=current.get("analysis_signature"),
        preference_changes=preference_changes,
        engine_version=new_envelope.get("engine_version") if isinstance(new_envelope, dict) else None,
    )


def explain_from_digests(
    previous_digest: dict[str, Any] | None,
    new_digest: dict[str, Any] | None,
    *,
    previous_signature: str | None,
    new_signature: str | None,
    preference_changes: list[dict[str, Any]] | None = None,
    engine_version: str | None = None,
) -> dict[str, Any]:
    return explain_recalculation(
        previous_snapshot=snapshot_from_digest(previous_digest),
        new_snapshot=snapshot_from_digest(new_digest),
        previous_signature=previous_signature,
        new_signature=new_signature,
        preference_changes=preference_changes,
        engine_version=engine_version,
    )


def package_membership_difference(explanation: dict[str, Any] | None) -> dict[str, Any] | None:
    if not explanation:
        return None
    added: set[str] = set()
    removed: set[str] = set()
    changed = bool(explanation.get("analysis_changed"))
    for rec in (explanation.get("recommendation_changes") or {}).values():
        if not isinstance(rec, dict):
            continue
        added.update(str(item) for item in (rec.get("added_product_ids") or []))
        removed.update(str(item) for item in (rec.get("removed_product_ids") or []))
        changed = changed or bool(rec.get("changed"))
    return {
        "changed": changed,
        "added_product_ids": sorted(added),
        "removed_product_ids": sorted(removed),
        "source": "system_recalculation",
        "scientific": False,
    }
