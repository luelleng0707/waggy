"""Clinical Execution Explorer — single backend owner for debug payload.

Assembles and presents frozen assessment execution for /debug/calculation.
Does NOT recompute FormulaGraph / clinical formulas.

Public API:
  build_validation_console / build_clinical_execution_explorer
  console_to_markdown
  build_engine_trace
  is_engine_debug
  compare_analyses
  list_presets / get_preset_body / DEFAULT_PRESET_ID
  list_repository_tables / preview_table
  developer_banner / maybe_open_validation_console / debug_status_payload
"""

from __future__ import annotations


# === from debug_presets.py ===

from typing import Any

# Request bodies compatible with profile_from_analyze_body / analyze API.
PRESETS: dict[str, dict[str, Any]] = {
    "golden_retriever": {
        "id": "golden_retriever",
        "label": "Golden Retriever",
        "description": "Adult Golden, 28 kg, moderate activity",
        "body": {
            "name": "Sunny",
            "pet_name": "Sunny",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-06-01",
            "weight": 28,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "german_shepherd": {
        "id": "german_shepherd",
        "label": "German Shepherd",
        "description": "Working-line adult, high activity",
        "body": {
            "name": "Rex",
            "pet_name": "Rex",
            "breeds": ["German Shepherd Dog"],
            "birthday": "2019-04-12",
            "weight": 34,
            "sex": "Male",
            "activity_level": "High",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "border_collie": {
        "id": "border_collie",
        "label": "Border Collie",
        "description": "High-drive herding breed",
        "body": {
            "name": "Pip",
            "pet_name": "Pip",
            "breeds": ["Border Collie"],
            "birthday": "2021-01-20",
            "weight": 18,
            "sex": "Female",
            "activity_level": "High",
            "current_environment": "Rural Cool",
            "observed_conditions": [],
        },
    },
    "french_bulldog": {
        "id": "french_bulldog",
        "label": "French Bulldog",
        "description": "Brachycephalic companion breed",
        "body": {
            "name": "Biscuit",
            "pet_name": "Biscuit",
            "breeds": ["French Bulldog"],
            "birthday": "2022-08-08",
            "weight": 12,
            "sex": "Male",
            "activity_level": "Low",
            "current_environment": "Urban Indoor",
            "observed_conditions": [],
        },
    },
    "mixed_breed": {
        "id": "mixed_breed",
        "label": "Mixed Breed",
        "description": "Dolly — Golden × Labrador (default demo)",
        "body": {
            "name": "Dolly",
            "pet_name": "Dolly",
            "breeds": ["Golden Retriever", "Labrador Retriever"],
            "birthday": "2021-03-15",
            "weight": 30,
            "sex": "Female",
            "activity_level": "High",
            "current_environment": "Shanghai Summer",
            "observed_conditions": [],
        },
    },
    "senior_labrador": {
        "id": "senior_labrador",
        "label": "Senior Labrador",
        "description": "Aging Labrador, lower activity",
        "body": {
            "name": "Maple",
            "pet_name": "Maple",
            "breeds": ["Labrador Retriever"],
            "birthday": "2013-05-01",
            "weight": 32,
            "sex": "Female",
            "activity_level": "Low",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "large_breed_puppy": {
        "id": "large_breed_puppy",
        "label": "Large Breed Puppy",
        "description": "Growing Golden puppy",
        "body": {
            "name": "Scout",
            "pet_name": "Scout",
            "breeds": ["Golden Retriever"],
            "birthday": "2025-09-01",
            "weight": 14,
            "sex": "Male",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "golden_20kg": {
        "id": "golden_20kg",
        "label": "Golden @ 20 kg",
        "description": "Compare preset A — lighter Golden",
        "body": {
            "name": "CompareA",
            "pet_name": "CompareA",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-06-01",
            "weight": 20,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "golden_25kg": {
        "id": "golden_25kg",
        "label": "Golden @ 25 kg",
        "description": "Compare preset B — heavier Golden",
        "body": {
            "name": "CompareB",
            "pet_name": "CompareB",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-06-01",
            "weight": 25,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
}

DEFAULT_PRESET_ID = "mixed_breed"


def list_presets() -> list[dict[str, Any]]:
    return [
        {
            "id": p["id"],
            "label": p["label"],
            "description": p["description"],
        }
        for p in PRESETS.values()
    ]


def get_preset_body(preset_id: str) -> dict[str, Any]:
    key = (preset_id or DEFAULT_PRESET_ID).strip().lower()
    if key not in PRESETS:
        raise KeyError(f"Unknown preset: {preset_id}")
    return dict(PRESETS[key]["body"])


# === from debug_repository_browser.py ===

from pathlib import Path
from typing import Any

from app.data.loader import resolve_csv_path
from app.data.repository import DataRepository

NOT_TRACEABLE = "NOT CURRENTLY TRACEABLE"


def list_repository_tables(repo: DataRepository) -> dict[str, Any]:
    """Catalog every manifest CSV with metadata (no edits)."""
    platform = repo.platform
    manifest = platform.manifest
    tables = []
    for spec in manifest.files:
        path = resolve_csv_path(platform.data_root, spec.path)
        try:
            df = platform.table(spec.table)
            row_count = int(len(df))
            columns = [str(c) for c in df.columns.tolist()]
            loaded = True
        except Exception as exc:  # noqa: BLE001
            row_count = 0
            columns = list(spec.required_columns)
            loaded = False
            err = str(exc)
        else:
            err = None

        mtime = None
        if path.exists():
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = None

        tables.append(
            {
                "table": spec.table,
                "path": spec.path,
                "absolute_path": str(path) if path.exists() else None,
                "row_count": row_count,
                "columns": columns,
                "primary_key": list(spec.primary_key),
                "required_columns": list(spec.required_columns),
                "allow_empty": bool(spec.allow_empty),
                "last_modified": mtime,
                "loaded": loaded,
                "load_error": err,
                "manifest_version": manifest.version,
                "platform_csv_hash": platform.csv_hash,
                "cache_status": "IN_MEMORY" if loaded else "MISSING",
                "per_row_cache": NOT_TRACEABLE,
            }
        )

    return {
        "schema": "repository_browser.v1",
        "read_only": True,
        "manifest_version": manifest.version,
        "csv_hash": platform.csv_hash,
        "loaded_at": platform.loaded_at,
        "file_count": platform.file_count,
        "data_root": str(platform.data_root),
        "tables": tables,
    }


def preview_table(
    repo: DataRepository,
    table: str,
    *,
    limit: int = 25,
    offset: int = 0,
    q: str | None = None,
) -> dict[str, Any]:
    """Preview rows from a loaded table (read-only)."""
    platform = repo.platform
    by = platform.manifest.by_table()
    if table not in by:
        raise KeyError(f"Unknown table: {table}")
    spec = by[table]
    df = platform.table(table)
    total = int(len(df))

    if q:
        needle = q.strip().lower()
        if needle:
            mask = df.astype(str).apply(
                lambda col: col.str.lower().str.contains(needle, na=False)
            ).any(axis=1)
            df = df.loc[mask]
    filtered = int(len(df))
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))
    slice_df = df.iloc[offset : offset + limit]
    rows = slice_df.fillna("").to_dict(orient="records")

    path = resolve_csv_path(platform.data_root, spec.path)
    return {
        "schema": "repository_table_preview.v1",
        "read_only": True,
        "table": table,
        "path": spec.path,
        "absolute_path": str(path) if path.exists() else None,
        "columns": [str(c) for c in slice_df.columns.tolist()] or list(spec.required_columns),
        "primary_key": list(spec.primary_key),
        "total_rows": total,
        "filtered_rows": filtered,
        "offset": offset,
        "limit": limit,
        "rows": rows,
        "cache_status": "IN_MEMORY",
        "platform_csv_hash": platform.csv_hash,
        "note": "Preview only — never edit repository data from this browser.",
    }


# === from assessment_diff.py ===

from typing import Any

NOT_TRACEABLE = "NOT CURRENTLY TRACEABLE"


def _num(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _flatten_health(analyze: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        key = str(h.get("title") or h.get("condition") or "").strip()
        if not key:
            continue
        out[key] = {
            "biological_risk_percent": h.get("biological_risk_percent"),
            "estimated_biological_risk_percent": h.get("estimated_biological_risk_percent"),
            "observed_breed_prevalence_percent": h.get("observed_breed_prevalence_percent")
            or h.get("observed_prevalence_percent"),
            "priority_score": h.get("priority_score"),
            "confidence_percent": h.get("confidence_percent"),
        }
    return out


def _flatten_packages(analyze: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in analyze.get("wellnessPackages") or []:
        if not isinstance(p, dict):
            continue
        key = str(p.get("tier") or p.get("title") or "").strip()
        if not key:
            continue
        out[key] = {
            "monthly_cost": p.get("monthly_cost"),
            "yearly_cost": p.get("yearly_cost"),
            "coverage_score": p.get("coverage_score"),
            "overall_score": p.get("overall_score"),
            "recommended": bool(p.get("recommended")),
            "product_count": len(p.get("products_included") or p.get("product_cards") or []),
        }
    return out


def _profile_inputs(analyze: dict[str, Any], raw: dict[str, Any] | None) -> dict[str, Any]:
    profile = analyze.get("profile") or analyze.get("pet") or {}
    return {
        "raw_request": raw,
        "name": profile.get("pet_name") or profile.get("name"),
        "breeds": profile.get("breeds") or profile.get("breed_list"),
        "weight_kg": profile.get("weight_kg") or profile.get("weight"),
        "age_years": profile.get("age_years") or profile.get("age"),
        "activity_level": profile.get("activity_level"),
        "current_environment": profile.get("current_environment") or profile.get("environment"),
    }


def _why_changed(path: str, left_inputs: dict, right_inputs: dict) -> dict[str, Any]:
    """Best-effort explanation: which profile inputs differed (not formula internals)."""
    input_diffs = []
    for k in ("weight_kg", "age_years", "activity_level", "current_environment", "breeds", "name"):
        lv, rv = left_inputs.get(k), right_inputs.get(k)
        if lv != rv:
            input_diffs.append({"field": k, "left": lv, "right": rv})

    if path.startswith("health.") or path.startswith("packages."):
        if not input_diffs:
            return {
                "status": NOT_TRACEABLE,
                "reason": "Outputs differ but no profile input delta detected in summarized fields.",
            }
        return {
            "status": "input_delta",
            "reason": "Profile inputs differ; engine may have re-run risk/optimizer with new inputs.",
            "input_deltas": input_diffs,
            "modifier_chain": NOT_TRACEABLE,
            "note": "Per-modifier contribution to this delta is not emitted by the engine.",
        }
    return {
        "status": "field_delta",
        "input_deltas": input_diffs,
        "modifier_chain": NOT_TRACEABLE,
    }


def compare_analyses(
    left_analyze: dict[str, Any],
    right_analyze: dict[str, Any],
    *,
    left_raw: dict[str, Any] | None = None,
    right_raw: dict[str, Any] | None = None,
    left_label: str = "Left",
    right_label: str = "Right",
    left_timings: dict[str, float] | None = None,
    right_timings: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Diff two frozen analyze envelopes. Does not recompute formulas."""
    left_in = _profile_inputs(left_analyze, left_raw)
    right_in = _profile_inputs(right_analyze, right_raw)

    changes: list[dict[str, Any]] = []

    lh, rh = _flatten_health(left_analyze), _flatten_health(right_analyze)
    for key in sorted(set(lh) | set(rh)):
        a, b = lh.get(key), rh.get(key)
        if a is None:
            changes.append(
                {
                    "path": f"health.{key}",
                    "kind": "added_right",
                    "left": None,
                    "right": b,
                    "why": _why_changed(f"health.{key}", left_in, right_in),
                }
            )
            continue
        if b is None:
            changes.append(
                {
                    "path": f"health.{key}",
                    "kind": "removed_right",
                    "left": a,
                    "right": None,
                    "why": _why_changed(f"health.{key}", left_in, right_in),
                }
            )
            continue
        for field in (
            "biological_risk_percent",
            "estimated_biological_risk_percent",
            "observed_breed_prevalence_percent",
            "priority_score",
            "confidence_percent",
        ):
            lv, rv = a.get(field), b.get(field)
            if lv != rv:
                ln, rn = _num(lv), _num(rv)
                delta = None if ln is None or rn is None else round(rn - ln, 4)
                changes.append(
                    {
                        "path": f"health.{key}.{field}",
                        "kind": "changed",
                        "left": lv,
                        "right": rv,
                        "delta": delta,
                        "why": _why_changed(f"health.{key}.{field}", left_in, right_in),
                    }
                )

    lp, rp = _flatten_packages(left_analyze), _flatten_packages(right_analyze)
    for key in sorted(set(lp) | set(rp)):
        a, b = lp.get(key), rp.get(key)
        if a is None or b is None:
            changes.append(
                {
                    "path": f"packages.{key}",
                    "kind": "added_right" if a is None else "removed_right",
                    "left": a,
                    "right": b,
                    "why": _why_changed(f"packages.{key}", left_in, right_in),
                }
            )
            continue
        for field in ("monthly_cost", "yearly_cost", "coverage_score", "overall_score", "recommended", "product_count"):
            lv, rv = a.get(field), b.get(field)
            if lv != rv:
                ln, rn = _num(lv), _num(rv)
                delta = None if ln is None or rn is None else round(rn - ln, 4)
                changes.append(
                    {
                        "path": f"packages.{key}.{field}",
                        "kind": "changed",
                        "left": lv,
                        "right": rv,
                        "delta": delta,
                        "why": _why_changed(f"packages.{key}.{field}", left_in, right_in),
                    }
                )

    # Nutrition target count
    ln = left_analyze.get("nutritionalTargets") or []
    rn = right_analyze.get("nutritionalTargets") or []
    if len(ln) != len(rn):
        changes.append(
            {
                "path": "nutrition.target_count",
                "kind": "changed",
                "left": len(ln),
                "right": len(rn),
                "delta": len(rn) - len(ln),
                "why": _why_changed("nutrition.target_count", left_in, right_in),
            }
        )

    unchanged_health = sum(
        1
        for k in set(lh) & set(rh)
        if lh[k].get("biological_risk_percent") == rh[k].get("biological_risk_percent")
    )

    input_deltas = []
    for k in ("weight_kg", "age_years", "activity_level", "current_environment", "breeds", "name"):
        lv, rv = left_in.get(k), right_in.get(k)
        if lv != rv:
            input_deltas.append({"field": k, "left": lv, "right": rv})

    return {
        "schema": "assessment_compare.v1",
        "left_label": left_label,
        "right_label": right_label,
        "left_inputs": left_in,
        "right_inputs": right_in,
        "input_deltas": input_deltas,
        "change_count": len(changes),
        "unchanged_health_priorities": unchanged_health,
        "changes": changes,
        "outputs_identical": len(changes) == 0,
        "timings": {"left": left_timings or {}, "right": right_timings or {}},
        "note": (
            "Diff compares frozen analyze outputs only. "
            "Why-changed cites profile input deltas; per-modifier attribution is "
            f"{NOT_TRACEABLE}."
            + (
                " Inputs differ but compared health/package fields are identical."
                if len(changes) == 0 and input_deltas
                else ""
            )
        ),
    }


# === from console_inspectors.py ===

import ast
import csv
from pathlib import Path
from typing import Any

from app.agent.formula_registry import FORMULA_REGISTRY as AGENT_FORMULA_REGISTRY
from app.inference.formula_registry import (
    FORMULA_COVERAGE,
    FORMULA_EVIDENCE,
    FORMULA_NUTRIENT,
    FORMULA_PACKAGE,
    FORMULA_PRODUCT,
    FORMULA_RISK,
    FORMULA_RISK_TRACE,
    formula_dependency_edges,
    formula_list,
)
from app.inference.models import NOT_TRACEABLE
from app.inference.resolver import component_to_ingredient_key, ingredient_key, normalize_label
from app.inference.risk import build_risk_modifier_ledger
from repository.math_debugger.independent_replay import IndependentFormulaReplay
from repository.math_debugger.models import CodeReference, FormulaTrace, VariableTrace
from repository.math_debugger.sensitivity import SensitivityAnalyzer


def _nt(reason: str, *, needs: str | None = None) -> dict[str, Any]:
    return {
        "status": NOT_TRACEABLE,
        "traceable": False,
        "reason": reason,
        "needs_engine_instrumentation": needs
        or "Emit named debug fields from the production stage (no equation text).",
    }


def expand_risk_ledgers(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Full risk chain for every healthInsight / debug risk_trace (emitted + honest gaps)."""
    calc_by = {
        str(c.get("condition")): c for c in (analyze.get("calculationTrace") or []) if isinstance(c, dict)
    }
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    by_condition = debug.get("risk_by_condition") if isinstance(debug.get("risk_by_condition"), dict) else {}
    fx_by = (
        debug.get("formula_execution_by_condition")
        if isinstance(debug.get("formula_execution_by_condition"), dict)
        else {}
    )
    traces = list(debug.get("risk_traces") or [])
    executions = list(debug.get("formula_executions") or [])
    # Also index traces by condition name
    for t in traces:
        if isinstance(t, dict) and t.get("condition"):
            by_condition.setdefault(str(t["condition"]), t)
    for fx in executions:
        if isinstance(fx, dict) and fx.get("condition"):
            fx_by.setdefault(str(fx["condition"]), fx)

    out = []
    # Prefer per-condition production traces (condition grain), then insights (goal grain)
    seen = set()
    for t in traces:
        if not isinstance(t, dict):
            continue
        cond = str(t.get("condition") or "")
        if not cond or cond in seen:
            continue
        seen.add(cond)
        base = build_risk_modifier_ledger(calc_row=calc_by.get(cond), observatory_trace=t)
        base["expanded_chain"] = base.get("steps") or []
        base["csv_lookups"] = t.get("csv_refs") or (calc_by.get(cond) or {}).get("published_evidence") or []
        base["decision_tree"] = (calc_by.get(cond) or {}).get("decision_log") or [
            {"logic": t.get("logic"), "groomer_boosted": t.get("groomer_boosted")}
        ]
        base["code"] = t.get("code")
        fx = fx_by.get(cond)
        if fx:
            base["formula_execution"] = fx
            # Prefer execution lookups (with csv_row) when present
            if fx.get("lookups"):
                base["csv_lookups"] = fx["lookups"]
        out.append(base)

    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        title = str(h.get("title") or "")
        # Skip if we already have condition-level traces covering supporting conditions
        supports = [str(x) for x in (h.get("supporting_conditions") or []) if x]
        if any(s in seen for s in supports):
            continue
        ot = by_condition.get(title)
        base = build_risk_modifier_ledger(h, calc_row=calc_by.get(title), observatory_trace=ot)
        if not base.get("expanded_chain"):
            # legacy expanded slot mapping
            chain = []
            emitted = {s.get("name"): s for s in base.get("steps") or []}
            for key, label in [
                ("baseline", "baseline / breed prevalence"),
                ("interaction", "trait interaction"),
                ("benefit", "benefit reductions"),
                ("mixed_breed", "mixed-breed adjustment"),
                ("age", "age modifier"),
                ("activity", "activity modifier"),
                ("weight", "weight modifier"),
                ("climate", "climate modifier"),
                ("final", "final risk"),
            ]:
                hit = emitted.get(key) or emitted.get(f"{key}_modifier") or emitted.get(
                    "baseline_observed_prevalence" if key == "baseline" else ""
                ) or emitted.get("final_probability" if key == "final" else "")
                if hit and hit.get("traceable"):
                    chain.append({**hit, "label": label})
                else:
                    chain.append(
                        {
                            "name": key,
                            "label": label,
                            "traceable": False,
                            "status": NOT_TRACEABLE,
                            "reason": f"Intermediate `{label}` not in observatory trace",
                        }
                    )
            base["expanded_chain"] = chain
        base["csv_lookups"] = (ot or {}).get("csv_refs") or (calc_by.get(title) or {}).get("published_evidence") or []
        fx = fx_by.get(title)
        if fx:
            base["formula_execution"] = fx
            if fx.get("lookups"):
                base["csv_lookups"] = fx["lookups"]
        out.append(base)
    return out


def formula_execution_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Project analyze.debug.formula_executions — engine-emitted ledgers only."""
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    rows = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        fid = str(fx.get("formula_id") or FORMULA_RISK)
        meta = _registry_meta(fid)
        code_ref = fx.get("code") or _code_ref_from_registry(fid)
        lookups = []
        for lu in fx.get("lookups") or []:
            if not isinstance(lu, dict):
                continue
            row_status = "AVAILABLE" if lu.get("csv_row") not in (None, "") else "NOT_AVAILABLE"
            lookups.append({**lu, "warehouse_row_status": row_status})
        with_row = sum(1 for lu in lookups if isinstance(lu, dict) and lu.get("csv_row") not in (None, ""))
        conf = list(fx.get("confidence") or fx.get("confidence_steps") or [])
        rows.append(
            {
                "schema": fx.get("schema") or "formula_execution.v2",
                "formula_id": fid,
                "formula_name": fx.get("formula_name") or meta.get("display_name") or meta.get("purpose"),
                "purpose": meta.get("purpose"),
                "stage": fx.get("stage"),
                "condition": fx.get("condition"),
                "subject": fx.get("subject") or fx.get("condition"),
                "inputs": fx.get("inputs") or {},
                "parameters": list((meta.get("node_meta") or {}).get("parameters") or []),
                "steps": fx.get("steps") or [],
                "modifiers": fx.get("modifiers") or [],
                "decisions": fx.get("decisions") or [],
                "competitions": fx.get("competitions") or [],
                "confidence": conf,
                "confidence_steps": conf,
                "lookups": lookups,
                "outputs": fx.get("outputs") or {},
                "timing": fx.get("timing") or {},
                "consumers": fx.get("consumers") or [],
                "dependencies": list(meta.get("depends_on") or []),
                "provenance": fx.get("provenance") or [],
                "code": code_ref,
                "lookup_row_coverage": {
                    "total": len(lookups),
                    "with_csv_row": with_row,
                    "pct": round(100.0 * with_row / len(lookups), 1) if lookups else None,
                },
                "emitted_by_engine": True,
                "execution_origin": "engine_formula_execution",
            }
        )
    return rows


_NUMERICAL_PROVENANCE_CACHE: list[dict[str, Any]] | None = None


def _registry_meta(formula_id: str) -> dict[str, Any]:
    meta = next((f for f in formula_list() if f.get("formula_id") == formula_id), {}) or {}
    node_meta = AGENT_FORMULA_REGISTRY.get(formula_id) or {}
    merged = {**meta}
    merged["node_meta"] = node_meta
    return merged


def _code_ref_from_registry(formula_id: str) -> dict[str, Any]:
    meta = _registry_meta(formula_id)
    node_meta = meta.get("node_meta") or {}
    module = node_meta.get("module") or meta.get("owner_module")
    function = node_meta.get("function")
    if not function:
        wrapped = node_meta.get("wrapped") or meta.get("callable_path")
        if isinstance(wrapped, str) and "." in wrapped:
            function = wrapped.rsplit(".", 1)[-1]
    file_path = ""
    if isinstance(module, str) and module:
        file_path = module.replace(".", "/") + ".py"
    return {"file": file_path or None, "function": function or None}


def _resolve_source_location(code: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(code, dict):
        return {
            "status": "SOURCE_NOT_AVAILABLE",
            "file": None,
            "function": None,
            "line_start": None,
            "line_end": None,
            "exists": False,
            "reason": "No code reference on execution record.",
            "excerpt": [],
        }
    file_rel = str(code.get("file") or "").replace("\\", "/")
    function_name = str(code.get("function") or "")
    if not file_rel:
        return {
            "status": "SOURCE_NOT_AVAILABLE",
            "file": None,
            "function": function_name or None,
            "line_start": None,
            "line_end": None,
            "exists": False,
            "reason": "Code file not mapped for this formula.",
            "excerpt": [],
        }
    root = Path(__file__).resolve().parents[2]
    target = root / file_rel
    if not target.exists():
        return {
            "status": "SOURCE_NOT_AVAILABLE",
            "file": file_rel,
            "function": function_name or None,
            "line_start": None,
            "line_end": None,
            "exists": False,
            "reason": "Mapped source file does not exist.",
            "excerpt": [],
        }
    try:
        text = target.read_text(encoding="utf-8")
    except Exception:
        return {
            "status": "SOURCE_NOT_AVAILABLE",
            "file": file_rel,
            "function": function_name or None,
            "line_start": None,
            "line_end": None,
            "exists": True,
            "reason": "Source file exists but could not be read.",
            "excerpt": [],
        }
    line_start = None
    line_end = None
    if function_name:
        try:
            tree = ast.parse(text)
            fn = function_name.split(".")[-1].strip()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == fn:
                    line_start = int(getattr(node, "lineno", 0)) or None
                    line_end = int(getattr(node, "end_lineno", 0)) or line_start
                    break
        except SyntaxError:
            pass
    lines = text.splitlines()
    excerpt: list[dict[str, Any]] = []
    if line_start is not None:
        start = max(1, line_start - 4)
        end = min(len(lines), (line_end or line_start) + 4)
        for ln in range(start, end + 1):
            excerpt.append({"line": ln, "code": lines[ln - 1]})
    status = "SOURCE_LOCATED" if line_start is not None else "SOURCE_FILE_ONLY"
    return {
        "status": status,
        "file": file_rel,
        "function": function_name or None,
        "line_start": line_start,
        "line_end": line_end,
        "exists": True,
        "reason": None if status == "SOURCE_LOCATED" else "Function line range not resolved.",
        "excerpt": excerpt,
    }


def _source_validation(loc: dict[str, Any]) -> dict[str, Any]:
    ok = bool(loc.get("exists")) and (
        loc.get("status") in {"SOURCE_LOCATED", "SOURCE_FILE_ONLY", "SOURCE_NOT_AVAILABLE"}
    )
    range_ok = True
    if loc.get("status") == "SOURCE_LOCATED":
        try:
            line_start = int(loc.get("line_start"))
            line_end = int(loc.get("line_end"))
            range_ok = line_start > 0 and line_end >= line_start
        except Exception:
            range_ok = False
    return {"ok": ok and range_ok, "file_exists": bool(loc.get("exists")), "line_range_valid": range_ok}


def _formula_expression_from_execution(fx: dict[str, Any]) -> str:
    exprs = [
        str(step.get("expression")).strip()
        for step in (fx.get("steps") or [])
        if isinstance(step, dict) and step.get("expression")
    ]
    if exprs:
        return "\n".join(exprs)
    explicit = fx.get("formula_expression")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    return "FORMULA DOCUMENTATION MISSING"


def _extract_section_items(section: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = section.get("outputs") if isinstance(section, dict) else {}
    if not isinstance(outputs, dict):
        return []
    for key in ("risks", "targets", "selected", "tiers", "items"):
        value = outputs.get(key)
        if isinstance(value, list) and value:
            return [item for item in value if isinstance(item, dict)]
    return []


def _section_lookups(section: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for src in section.get("csv_sources") or []:
        if not isinstance(src, dict):
            continue
        table = src.get("table")
        if not table:
            continue
        out.append(
            {
                "table": table,
                "csv_file": f"{table}.csv",
                "csv_row": None,
                "row_id": None,
                "primary_key": {},
                "matched": True,
                "matched_on": [],
                "selected_columns": {},
                "columns": {},
                "column": None,
                "evidence_id": None,
                "decision": "dataset_used_runtime_rows_not_emitted",
                "source_note": src.get("note"),
                "warehouse_row_status": "NOT_AVAILABLE",
            }
        )
    return out


def _derive_formula_executions_from_trace(trace: dict[str, Any], analyze: dict[str, Any]) -> list[dict[str, Any]]:
    sections = (trace or {}).get("sections") or {}
    if not isinstance(sections, dict):
        return []
    derived: list[dict[str, Any]] = []
    for stage_name, section in sections.items():
        if not isinstance(section, dict):
            continue
        formula_id = section.get("formula_id")
        if not formula_id:
            continue
        meta = _registry_meta(str(formula_id))
        code_ref = _code_ref_from_registry(str(formula_id))
        lookups = _section_lookups(section)
        items = _extract_section_items(section)
        if items:
            for idx, item in enumerate(items):
                subject = (
                    item.get("condition")
                    or item.get("nutrient")
                    or item.get("ingredient")
                    or item.get("name")
                    or item.get("title")
                    or item.get("tier")
                    or f"{stage_name}_{idx + 1}"
                )
                fx = {
                    "schema": "formula_execution.v2",
                    "formula_id": formula_id,
                    "formula_name": meta.get("display_name") or meta.get("purpose") or formula_id,
                    "stage": section.get("stage") or stage_name,
                    "condition": item.get("condition"),
                    "subject": subject,
                    "purpose": meta.get("purpose"),
                    "inputs": item.get("inputs") if isinstance(item.get("inputs"), dict) else section.get("inputs") or {},
                    "parameters": list((meta.get("node_meta") or {}).get("parameters") or []),
                    "steps": [],
                    "modifiers": [],
                    "decisions": [],
                    "competitions": [],
                    "confidence": [],
                    "confidence_steps": [],
                    "lookups": lookups,
                    "outputs": item.get("outputs") if isinstance(item.get("outputs"), dict) else item,
                    "timing": {"elapsed_ms": section.get("elapsed_ms")},
                    "consumers": list(meta.get("consumes") or meta.get("consumers") or []),
                    "dependencies": list(meta.get("depends_on") or []),
                    "provenance": [],
                    "code": code_ref,
                    "lookup_row_coverage": {"total": len(lookups), "with_csv_row": 0, "pct": 0.0},
                    "emitted_by_engine": False,
                    "derived_from_stage_trace": True,
                    "execution_origin": "engine_trace_section",
                    "formula_expression": "FORMULA DOCUMENTATION MISSING",
                    "units": item.get("unit"),
                }
                fx["formula_expression"] = _formula_expression_from_execution(fx)
                derived.append(fx)
            continue

        fx = {
            "schema": "formula_execution.v2",
            "formula_id": formula_id,
            "formula_name": meta.get("display_name") or meta.get("purpose") or formula_id,
            "stage": section.get("stage") or stage_name,
            "condition": None,
            "subject": section.get("stage") or stage_name,
            "purpose": meta.get("purpose"),
            "inputs": section.get("inputs") or {},
            "parameters": list((meta.get("node_meta") or {}).get("parameters") or []),
            "steps": [],
            "modifiers": [],
            "decisions": [],
            "competitions": [],
            "confidence": [],
            "confidence_steps": [],
            "lookups": lookups,
            "outputs": section.get("outputs") or {},
            "timing": {"elapsed_ms": section.get("elapsed_ms")},
            "consumers": list(meta.get("consumes") or meta.get("consumers") or []),
            "dependencies": list(meta.get("depends_on") or []),
            "provenance": [],
            "code": code_ref,
            "lookup_row_coverage": {"total": len(lookups), "with_csv_row": 0, "pct": 0.0},
            "emitted_by_engine": False,
            "derived_from_stage_trace": True,
            "execution_origin": "engine_trace_section",
            "formula_expression": "FORMULA DOCUMENTATION MISSING",
            "units": None,
        }
        fx["formula_expression"] = _formula_expression_from_execution(fx)
        derived.append(fx)
    return derived


def _merge_formula_executions(primary: list[dict[str, Any]], secondary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for idx, fx in enumerate(list(primary) + list(secondary), start=1):
        if not isinstance(fx, dict):
            continue
        key = (
            str(fx.get("formula_id") or ""),
            str(fx.get("stage") or ""),
            str(fx.get("subject") or fx.get("condition") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        if "formula_expression" not in fx:
            fx["formula_expression"] = _formula_expression_from_execution(fx)
        fx["execution_id"] = (
            fx.get("execution_id")
            or f"{fx.get('formula_id') or 'UNKNOWN'}:{fx.get('stage') or 'unknown'}:{fx.get('subject') or fx.get('condition') or idx}"
        )
        merged.append(fx)
    return merged


def _load_numerical_provenance_rows() -> list[dict[str, Any]]:
    global _NUMERICAL_PROVENANCE_CACHE
    if _NUMERICAL_PROVENANCE_CACHE is not None:
        return _NUMERICAL_PROVENANCE_CACHE
    rows: list[dict[str, Any]] = []
    csv_path = Path(__file__).resolve().parents[2] / "docs" / "mathematics" / "NUMERICAL_PROVENANCE.csv"
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(dict(row))
    _NUMERICAL_PROVENANCE_CACHE = rows
    return rows


def _numerical_rows_for_formula(formula_id: str, code: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows = _load_numerical_provenance_rows()
    if not rows:
        return []
    matched = [r for r in rows if str(r.get("formula_id") or "").strip() == str(formula_id)]
    if matched:
        return matched[:40]
    file_ref = ""
    if isinstance(code, dict):
        file_ref = str(code.get("file") or "")
    if file_ref:
        fallback = [r for r in rows if file_ref.replace("\\", "/") in str(r.get("file") or "")]
        if fallback:
            return fallback[:40]
    return []


def _publication_risk_for_formula(numerical_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not numerical_rows:
        return [
            {
                "classification": "Unknown",
                "reason": "No numerical provenance rows mapped to this formula execution.",
            }
        ]
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in numerical_rows:
        classification = str(row.get("classification") or "").upper()
        if classification.startswith("SCIENTIFIC"):
            label = "Scientific parameter"
        elif classification.startswith("ENGINEERING"):
            label = "Engineering assumption"
        elif classification in {"OBSERVED_DATA", "SCIENTIFIC_FACT"}:
            label = "Observed data"
        elif classification in {"CALCULATED_VALUE", "EMPIRICALLY_DERIVED"}:
            label = "Derived value"
        else:
            label = "Unknown"
        if label in seen:
            continue
        seen.add(label)
        out.append(
            {
                "classification": label,
                "reason": row.get("description")
                or row.get("derivation")
                or "Classification inferred from numerical provenance inventory.",
            }
        )
    return out


def _build_formula_trace_for_replay(fx: dict[str, Any], numerical_rows: list[dict[str, Any]]) -> FormulaTrace | None:
    formula_id = str(fx.get("formula_id") or "")
    if not formula_id.startswith("MAT-"):
        return None
    outputs = fx.get("outputs") or {}
    output_value = None
    for key in ("final_risk_percent", "final_value", "target", "value", "output"):
        if outputs.get(key) is not None:
            output_value = outputs.get(key)
            break
    if output_value is None:
        return None
    inputs = []
    for key, value in (fx.get("inputs") or {}).items():
        if isinstance(value, (int, float)):
            inputs.append(
                VariableTrace(
                    variable_name=str(key),
                    variable_type="float",
                    unit="",
                    value=float(value),
                    source="runtime_inputs",
                )
            )
    params = []
    for row in numerical_rows:
        raw = row.get("value")
        try:
            parsed = float(raw)
        except (TypeError, ValueError):
            continue
        params.append(
            VariableTrace(
                variable_name=str(row.get("variable") or row.get("provenance_id") or "param"),
                variable_type="float",
                unit=str(row.get("unit") or ""),
                value=parsed,
                source=str(row.get("source_type") or "numerical_provenance"),
            )
        )
    code = fx.get("code") or {}
    code_ref = None
    if code.get("file"):
        code_ref = CodeReference(
            python_file=str(code.get("file")),
            python_function=str(code.get("function") or ""),
            source_line_start=0,
            source_line_end=0,
        )
    return FormulaTrace(
        trace_id=f"{formula_id}:{fx.get('subject') or fx.get('stage')}",
        formula_id=formula_id,
        formula_version=str((_registry_meta(formula_id).get("version") or "unknown")),
        formula_name=str(fx.get("formula_name") or formula_id),
        status="ACTIVE",
        equation=str(fx.get("formula_expression") or "FORMULA DOCUMENTATION MISSING"),
        substituted_equation=str(fx.get("formula_expression") or "FORMULA DOCUMENTATION MISSING"),
        intermediate_calculations=tuple(
            str(s.get("expression") or s.get("name") or "") for s in (fx.get("steps") or []) if isinstance(s, dict)
        ),
        output_variable="output",
        output_value=output_value,
        unit=str(fx.get("units") or ""),
        input_variables=tuple(inputs),
        parameter_variables=tuple(params),
        code_reference=code_ref,
    )


def _attach_math_audit(formula_executions: list[dict[str, Any]]) -> dict[str, Any]:
    replay_engine = IndependentFormulaReplay()
    sensitivity = SensitivityAnalyzer()
    replay_rows: list[dict[str, Any]] = []
    sensitivity_rows: list[dict[str, Any]] = []
    for fx in formula_executions:
        if not isinstance(fx, dict):
            continue
        numerical_rows = _numerical_rows_for_formula(str(fx.get("formula_id") or ""), fx.get("code"))
        publication_risk = _publication_risk_for_formula(numerical_rows)
        source_loc = _resolve_source_location(fx.get("code"))
        source_check = _source_validation(source_loc)
        documentation_status = (
            "DOCUMENTED"
            if str(fx.get("formula_expression") or "").strip()
            and str(fx.get("formula_expression") or "").strip() != "FORMULA DOCUMENTATION MISSING"
            else "NOT_DOCUMENTED"
        )
        warehouse_status = (
            "WAREHOUSE_ROW_TRACED"
            if any((lu or {}).get("csv_row") not in (None, "") for lu in (fx.get("lookups") or []))
            else ("WAREHOUSE_LOOKUP_ONLY" if (fx.get("lookups") or []) else "WAREHOUSE_NOT_AVAILABLE")
        )
        evidence_refs = [
            {"evidence_id": (lu or {}).get("evidence_id")}
            for lu in (fx.get("lookups") or [])
            if isinstance(lu, dict) and lu.get("evidence_id")
        ]
        evidence_status = "EVIDENCE_TRACED" if evidence_refs else "EVIDENCE_NOT_AVAILABLE"
        fx["source_location"] = source_loc
        fx["source_validation"] = source_check
        fx["documentation_status"] = documentation_status
        fx["warehouse_status"] = warehouse_status
        fx["evidence_references"] = evidence_refs
        fx["evidence_status"] = evidence_status
        fx["execution_status"] = {
            "executed": "YES",
            "source_located": "YES" if source_loc.get("status") == "SOURCE_LOCATED" else "PARTIAL",
            "formula_documented": "YES" if documentation_status == "DOCUMENTED" else "NO",
            "parameterized": "YES" if bool(fx.get("parameters")) else "NO",
            "warehouse_traced": "YES" if warehouse_status == "WAREHOUSE_ROW_TRACED" else "PARTIAL",
            "evidence_traced": "YES" if evidence_status == "EVIDENCE_TRACED" else "NO",
            "replayable": "NO",
            "sensitivity_analyzable": "NO",
            "scientifically_validated": "NOT_AVAILABLE",
        }
        fx["scientific_support_status"] = (
            "SUPPORTED" if evidence_status == "EVIDENCE_TRACED" else "NOT_AVAILABLE_FOR_THIS_EXECUTION"
        )
        fx["publication_status"] = "NOT_ASSESSED"
        fx["numerical_provenance"] = numerical_rows
        fx["publication_risk"] = publication_risk
        fx["formula_expression"] = _formula_expression_from_execution(fx)
        trace = _build_formula_trace_for_replay(fx, numerical_rows)
        if trace is None:
            fx["replay"] = {
                "status": "NOT_IMPLEMENTED",
                "capability_status": "NOT_IMPLEMENTED",
                "detail": "REPLAY: NOT IMPLEMENTED FOR THIS FORMULA",
            }
            fx["sensitivity"] = {
                "status": "NOT_IMPLEMENTED",
                "capability_status": "NOT_IMPLEMENTED",
                "rows": [],
                "detail": "SENSITIVITY: NOT IMPLEMENTED FOR THIS FORMULA",
            }
            fx["execution_status"]["replayable"] = "NO"
            fx["execution_status"]["sensitivity_analyzable"] = "NO"
            replay_rows.append(
                {
                    "execution_id": fx.get("execution_id"),
                    "formula_id": fx.get("formula_id"),
                    "subject": fx.get("subject"),
                    "status": "NOT_IMPLEMENTED",
                    "detail": "REPLAY: NOT IMPLEMENTED FOR THIS FORMULA",
                }
            )
            continue
        comparison = replay_engine.replay_formula(trace)
        denom = abs(comparison.production_output) if comparison.production_output else None
        rel_err = comparison.absolute_delta / denom if denom else None
        replay_doc = {
            "status": comparison.status,
            "production_output": comparison.production_output,
            "independent_replay_output": comparison.replay_output,
            "absolute_error": comparison.absolute_delta,
            "relative_error": rel_err,
            "tolerance": replay_engine.tolerance,
            "detail": comparison.detail,
        }
        fx["replay"] = replay_doc
        fx["execution_status"]["replayable"] = "YES"
        replay_rows.append(
            {
                "execution_id": fx.get("execution_id"),
                "formula_id": fx.get("formula_id"),
                "subject": fx.get("subject"),
                **replay_doc,
            }
        )
        sens = []
        for row in sensitivity.analyze(trace):
            sens.append(
                {
                    "formula_id": row.formula_id,
                    "parameter": row.parameter_name,
                    "baseline": row.baseline_parameter,
                    "minus_10_percent": row.baseline_parameter * 0.9,
                    "plus_10_percent": row.baseline_parameter * 1.1,
                    "output_minus_10_percent": row.minus_10_result,
                    "output_plus_10_percent": row.plus_10_result,
                    "absolute_change_minus": row.absolute_change_minus,
                    "absolute_change_plus": row.absolute_change_plus,
                    "relative_change_minus": row.relative_change_minus,
                    "relative_change_plus": row.relative_change_plus,
                }
            )
        fx["sensitivity"] = {
            "status": "AVAILABLE" if sens else "INSUFFICIENT_TRACE",
            "capability_status": "SUPPORTED" if sens else "INSUFFICIENT_TRACE",
            "rows": sens,
        }
        fx["execution_status"]["sensitivity_analyzable"] = "YES" if sens else "NO"
        sensitivity_rows.extend(sens)
    return {"replay": replay_rows, "sensitivity": sensitivity_rows}


def decision_ledger_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    if debug.get("decision_ledger"):
        return list(debug["decision_ledger"])
    out = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for d in fx.get("decisions") or []:
            if isinstance(d, dict):
                out.append({**d, "formula_id": fx.get("formula_id"), "subject_ctx": fx.get("subject")})
    return out


def provenance_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    if debug.get("provenance_index"):
        return list(debug["provenance_index"])
    out = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for p in fx.get("provenance") or []:
            if isinstance(p, dict):
                out.append({**p, "formula_id": fx.get("formula_id"), "stage": fx.get("stage")})
    return out


def competition_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    out = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for c in fx.get("competitions") or []:
            if isinstance(c, dict):
                out.append(
                    {
                        **c,
                        "formula_id": fx.get("formula_id"),
                        "subject": fx.get("subject") or fx.get("condition"),
                    }
                )
    return out


def nutrition_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for t in analyze.get("nutritionalTargets") or []:
        if not isinstance(t, dict):
            continue
        name = t.get("ingredient") or t.get("nutrient") or t.get("name")
        rows.append(
            {
                "formula_id": FORMULA_NUTRIENT,
                "condition": t.get("condition") or t.get("supports_condition") or NOT_TRACEABLE,
                "ingredient": name,
                "daily_target": t.get("daily_target") or t.get("target") or t.get("dose"),
                "unit": t.get("unit"),
                "chain": [
                    {"step": "condition", "value": t.get("condition"), "traceable": t.get("condition") is not None},
                    {
                        "step": "ingredient_rule",
                        "value": name,
                        "traceable": name is not None,
                        "csv": "condition_ingredients_*",
                    },
                    {
                        "step": "weight_calculation",
                        **_nt("Dose×weight intermediate not always emitted separately"),
                    },
                    {
                        "step": "daily_target",
                        "value": t.get("daily_target") or t.get("target"),
                        "traceable": True,
                    },
                    {
                        "step": "product_contribution",
                        **_nt("Per-product contribution split not on nutritionalTargets"),
                    },
                    {
                        "step": "food_contribution",
                        **_nt("Food vs supplement split often missing"),
                    },
                    {
                        "step": "coverage",
                        "value": t.get("coverage_percent") or t.get("coverage"),
                        "traceable": t.get("coverage_percent") is not None or t.get("coverage") is not None,
                        "formula_id": FORMULA_COVERAGE,
                    },
                    {
                        "step": "remaining_requirement",
                        **_nt("Remaining requirement field not standard on targets"),
                    },
                ],
                "raw": t,
            }
        )
    return rows


def ingredient_resolution_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Show resolution path for ingredients appearing in analyze (resolver view, not rescore)."""
    names: list[str] = []
    for t in analyze.get("nutritionalTargets") or []:
        if isinstance(t, dict):
            n = t.get("ingredient") or t.get("nutrient") or t.get("name")
            if n:
                names.append(str(n))
    for p in analyze.get("productRecommendations") or []:
        if isinstance(p, dict):
            for a in p.get("actives") or p.get("active_ingredients") or []:
                if isinstance(a, dict) and a.get("name"):
                    names.append(str(a["name"]))
                elif isinstance(a, str):
                    names.append(a)

    seen = set()
    out = []
    for raw in names:
        key = ingredient_key(raw)
        if key in seen:
            continue
        seen.add(key)
        canon = component_to_ingredient_key(raw)
        out.append(
            {
                "original": raw,
                "normalized": normalize_label(raw).lower(),
                "ingredient_key": key,
                "canonical_key": canon,
                "alias_match": key != canon or key == canon,
                "chain": [
                    {"step": "original", "value": raw, "traceable": True},
                    {"step": "normalized", "value": normalize_label(raw).lower(), "traceable": True},
                    {
                        "step": "alias_match",
                        "value": canon,
                        "traceable": True,
                        "note": "Formatting normalize + known remaps in resolver (CSV aliases applied in pipeline)",
                    },
                    {"step": "canonical_key", "value": canon, "traceable": True},
                    {"step": "taxonomy", **_nt("Taxonomy walk not logged per request")},
                    {"step": "mechanisms", **_nt("Attach from ingredient_mechanisms at request time not traced")},
                    {"step": "evidence", **_nt("See Evidence tab for attached papers")},
                    {"step": "products_matched", **_nt("Inverse product→ingredient match log not emitted")},
                    {"step": "coverage", **_nt("See Coverage / Packages")},
                    {"step": "confidence", **_nt("Per-ingredient confidence ladder not on analyze")},
                ],
            }
        )
    return out


def product_match_inspector(analyze: dict[str, Any]) -> dict[str, Any]:
    selected = []
    for p in analyze.get("productRecommendations") or []:
        if not isinstance(p, dict):
            continue
        selected.append(
            {
                "formula_id": FORMULA_PRODUCT,
                "product_id": p.get("product_id") or p.get("id"),
                "name": p.get("product_name") or p.get("name"),
                "chain": [
                    {"step": "candidate", "value": p.get("product_name") or p.get("name"), "traceable": True},
                    {
                        "step": "ingredient_overlap",
                        **_nt("Overlap score not on productRecommendations row"),
                    },
                    {
                        "step": "coverage",
                        "value": p.get("coverage_pct") or p.get("coverage"),
                        "traceable": p.get("coverage_pct") is not None or p.get("coverage") is not None,
                    },
                    {"step": "evidence_score", **_nt("Per-product evidence score not emitted on recommendation card")},
                    {"step": "clinical_function", **_nt("Function score not on recommendation card")},
                    {"step": "cost_efficiency", **_nt("Cost efficiency term not on recommendation card")},
                    {"step": "diversity", **_nt("Diversity term not on recommendation card")},
                    {
                        "step": "overall_score",
                        "value": p.get("score") or p.get("overall_score"),
                        "traceable": p.get("score") is not None or p.get("overall_score") is not None,
                    },
                ],
                "raw": {k: p.get(k) for k in ("product_id", "product_name", "category", "monthly_cost") if k in p},
            }
        )

    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    rejected = list(debug.get("package_rejects") or [])
    if not rejected:
        for pkg in analyze.get("wellnessPackages") or []:
            if isinstance(pkg, dict):
                for rej in pkg.get("products_rejected") or []:
                    if isinstance(rej, dict):
                        rejected.append({**rej, "tier": pkg.get("tier")})

    return {
        "formula_id": FORMULA_PRODUCT,
        "selected": selected,
        "rejected": rejected,
        "rejected_note": (
            None
            if rejected
            else "No products_rejected on wellnessPackages / debug.package_rejects"
        ),
    }


def package_optimizer_inspector(analyze: dict[str, Any]) -> dict[str, Any]:
    tiers = []
    for p in analyze.get("wellnessPackages") or []:
        if not isinstance(p, dict):
            continue
        products = p.get("products_included") or p.get("product_cards") or []
        rejected = p.get("products_rejected") or []
        breakdown = p.get("score_breakdown") or {}
        obs = p.get("observatory") if isinstance(p.get("observatory"), dict) else {}
        tiers.append(
            {
                "tier": p.get("tier"),
                "title": p.get("title"),
                "recommended": bool(p.get("recommended")),
                "coverage_score": p.get("coverage_score"),
                "overall_score": p.get("overall_score"),
                "monthly_cost": p.get("monthly_cost"),
                "yearly_cost": p.get("yearly_cost"),
                "score_breakdown": breakdown,
                "candidates_evaluated_count": p.get("candidates_evaluated_count"),
                "chain": [
                    {
                        "step": "candidate_products",
                        "value": p.get("candidates_evaluated_count") or len(products),
                        "traceable": True,
                    },
                    {
                        "step": "coverage_matrix",
                        "value": p.get("coverage_score"),
                        "traceable": p.get("coverage_score") is not None,
                        "formula_id": FORMULA_COVERAGE,
                        "matrix": p.get("coverage_matrix"),
                    },
                    {
                        "step": "score_breakdown",
                        "value": breakdown,
                        "traceable": bool(breakdown),
                    },
                    {
                        "step": "optimization_passes",
                        **_nt(
                            "Per-pass candidate trial scores not stored",
                            needs="Emit optimization_passes[] from greedy/best-add loops",
                        ),
                    },
                    {"step": "tier_assignment", "value": p.get("tier"), "traceable": True},
                    {"step": "final_package", "value": p.get("title"), "traceable": True},
                ],
                "products_selected": [
                    {
                        "product_id": x.get("product_id"),
                        "name": x.get("name") or x.get("product_name"),
                        "why_selected": x.get("why_selected") or x.get("reason") or NOT_TRACEABLE,
                    }
                    for x in (products if isinstance(products, list) else [])
                    if isinstance(x, dict)
                ],
                "removed_products": rejected,
                "observatory": obs,
            }
        )
    return {"formula_id": FORMULA_PACKAGE, "tiers": tiers}


def evidence_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for e in analyze.get("scientificEvidence") or []:
        if not isinstance(e, dict):
            continue
        out.append(
            {
                "formula_id": FORMULA_EVIDENCE,
                "title": e.get("title") or e.get("source_name"),
                "condition": e.get("condition") or e.get("linked_condition"),
                "ingredient": e.get("ingredient") or e.get("ingredient_name"),
                "year": e.get("year"),
                "url": e.get("url") or e.get("source_url"),
                "quote": e.get("quote") or e.get("finding") or e.get("summary"),
                "pmid": e.get("pmid") or NOT_TRACEABLE,
                "doi": e.get("doi") or NOT_TRACEABLE,
                "evidence_status": (
                    "EVIDENCE INCOMPLETE"
                    if not (e.get("url") or e.get("source_url")) or not (e.get("quote") or e.get("finding"))
                    else "OK"
                ),
                "chain": [
                    {"step": "condition", "value": e.get("condition"), "traceable": bool(e.get("condition"))},
                    {
                        "step": "evidence_row",
                        "value": e.get("title") or e.get("source_name"),
                        "traceable": True,
                        "csv": "ingredient_evidence_* / clinical_evidence_base",
                    },
                    {"step": "mechanisms", **_nt("Mechanism join not always on evidence card")},
                    {
                        "step": "evidence_strength",
                        "value": e.get("evidence_level") or e.get("strength"),
                        "traceable": e.get("evidence_level") is not None or e.get("strength") is not None,
                    },
                    {"step": "final_ranking", **_nt("Rank position not always emitted")},
                ],
                "raw": e,
            }
        )
    return out


def confidence_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        conf = h.get("confidence_percent")
        rows.append(
            {
                "condition": h.get("title"),
                "final_confidence_percent": conf,
                "formula_id": FORMULA_RISK,
                "chain": [
                    {"step": "base_confidence", **_nt("Base confidence intermediate not emitted")},
                    {"step": "evidence_quality", **_nt("Evidence quality factor not emitted")},
                    {"step": "data_completeness", **_nt("Completeness factor not emitted")},
                    {"step": "inference_penalty", **_nt("Inference penalty not emitted")},
                    {"step": "estimated_value_penalty", **_nt("Estimate penalty not emitted")},
                    {
                        "step": "final_confidence",
                        "value": conf,
                        "unit": "%",
                        "traceable": conf is not None,
                        "source": "healthInsights.confidence_percent",
                    },
                ],
            }
        )
    return rows


def coverage_inspector(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Coverage from package / nutrition fields already on analyze."""
    rows = []
    for p in analyze.get("wellnessPackages") or []:
        if isinstance(p, dict) and p.get("coverage_score") is not None:
            rows.append(
                {
                    "scope": "package",
                    "tier": p.get("tier"),
                    "coverage_score": p.get("coverage_score"),
                    "formula_id": FORMULA_COVERAGE,
                    "traceable": True,
                }
            )
    for t in analyze.get("nutritionalTargets") or []:
        if isinstance(t, dict) and (t.get("coverage_percent") is not None or t.get("coverage") is not None):
            rows.append(
                {
                    "scope": "nutrient",
                    "name": t.get("ingredient") or t.get("nutrient"),
                    "coverage": t.get("coverage_percent") or t.get("coverage"),
                    "formula_id": FORMULA_COVERAGE,
                    "traceable": True,
                }
            )
    return rows


def pipeline_timeline(analyze: dict[str, Any], timings: dict[str, float] | None) -> list[dict[str, Any]]:
    stages = [
        ("payload", "Payload / profile"),
        ("biology", "Breed / Traits"),
        ("health_risk", "Risk"),
        ("epidemiology", "Epidemiology"),
        ("management", "Management"),
        ("nutrition", "Nutrition"),
        ("optimization", "Products / Optimization"),
        ("assembly", "Assembly"),
    ]
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    stage_ms = dict(debug.get("stage_timings_ms") or {})
    if timings:
        stage_ms.update({k: v for k, v in timings.items() if isinstance(v, (int, float))})

    pipe = analyze.get("pipeline_trace") or []
    by_stage = {}
    for s in pipe:
        if isinstance(s, dict):
            by_stage[str(s.get("stage") or "").lower()] = s

    out = []
    cumulative = 0.0
    for sid, label in stages:
        hit = by_stage.get(sid)
        if not hit:
            for k, v in by_stage.items():
                if sid in k or label.lower().split()[0].lower() in k:
                    hit = v
                    break
        ms = stage_ms.get(sid)
        if isinstance(ms, (int, float)):
            cumulative += float(ms)
        out.append(
            {
                "id": sid,
                "label": label,
                "record_count": (hit or {}).get("record_count") or (hit or {}).get("record_counts"),
                "source_files": (hit or {}).get("source_files") or [],
                "elapsed_ms": ms if ms is not None else NOT_TRACEABLE,
                "cumulative_ms": round(cumulative, 3) if ms is not None else NOT_TRACEABLE,
                "message": (hit or {}).get("message") or (hit or {}).get("label"),
                "present": hit is not None or ms is not None,
            }
        )
    if stage_ms.get("total_pipeline") is not None:
        out.append(
            {
                "id": "total",
                "label": "Total pipeline",
                "elapsed_ms": stage_ms["total_pipeline"],
                "present": True,
            }
        )
    return out


def performance_inspector(analyze: dict[str, Any], timings: dict[str, float] | None) -> dict[str, Any]:
    pipe = analyze.get("pipeline_trace") or []
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    stage_ms = debug.get("stage_timings_ms") or {}
    return {
        "wrapper_timings": timings or {},
        "stage_timings_ms": stage_ms if stage_ms else NOT_TRACEABLE,
        "lookup_counts": NOT_TRACEABLE,
        "rows_scanned": NOT_TRACEABLE,
        "rows_matched": [
            {"stage": s.get("stage"), "record_count": s.get("record_count") or s.get("record_counts")}
            for s in pipe
            if isinstance(s, dict)
        ],
        "cache_hits": NOT_TRACEABLE,
        "note": "Stage wall-clock from engine.perf_counter. Cache/lookup counts still require data-layer instrumentation.",
    }


def csv_dependency_viewer(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for s in analyze.get("pipeline_trace") or []:
        if not isinstance(s, dict):
            continue
        for f in s.get("source_files") or []:
            rows.append(
                {
                    "stage": s.get("stage"),
                    "csv": f,
                    "record_counts": s.get("record_counts"),
                    "matched_row_id": NOT_TRACEABLE,
                    "ignored_rows": NOT_TRACEABLE,
                    "joins": NOT_TRACEABLE,
                }
            )
    return rows


def formula_graph() -> dict[str, Any]:
    return {
        "nodes": formula_list(),
        "edges": formula_dependency_edges(),
    }


def decision_trees(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    trees = []
    for c in analyze.get("calculationTrace") or []:
        if not isinstance(c, dict):
            continue
        log = c.get("decision_log") or []
        trees.append(
            {
                "condition": c.get("condition"),
                "formula_id": FORMULA_RISK,
                "nodes": log
                if log
                else [
                    {"input": c.get("condition"), "decision": NOT_TRACEABLE, "why": "No decision_log on calculationTrace"}
                ],
            }
        )
    return trees


def build_search_index(console_sections: dict[str, Any]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for f in formula_list():
        hits.append(
            {
                "kind": "formula_id",
                "label": f["formula_id"],
                "nav": "formulas",
                "purpose": f.get("purpose"),
            }
        )
        for dep in f.get("depends_on") or []:
            hits.append({"kind": "formula_id", "label": dep, "nav": "graph"})
    for ex in console_sections.get("risk_ledgers") or []:
        hits.append({"kind": "condition", "label": ex.get("condition"), "nav": "risks"})
    for e in console_sections.get("evidence") or []:
        hits.append({"kind": "evidence", "label": e.get("title"), "nav": "evidence"})
        if e.get("pmid") and e["pmid"] != NOT_TRACEABLE:
            hits.append({"kind": "pmid", "label": str(e["pmid"]), "nav": "evidence"})
        if e.get("mechanism"):
            hits.append({"kind": "mechanism", "label": e.get("mechanism"), "nav": "evidence"})
        if e.get("ingredient"):
            hits.append({"kind": "ingredient", "label": e.get("ingredient"), "nav": "evidence"})
    for ing in console_sections.get("ingredients") or []:
        hits.append({"kind": "ingredient", "label": ing.get("original"), "nav": "ingredients"})
        if ing.get("canonical_key"):
            hits.append({"kind": "ingredient", "label": ing.get("canonical_key"), "nav": "ingredients"})
    for row in console_sections.get("csv_lookups") or []:
        hits.append({"kind": "csv", "label": row.get("csv"), "nav": "csv"})
    products = console_sections.get("products") or {}
    for p in products.get("selected") or []:
        hits.append({"kind": "product", "label": p.get("name"), "nav": "products"})
    for n in console_sections.get("nutrition") or []:
        hits.append({"kind": "ingredient", "label": n.get("ingredient"), "nav": "nutrition"})
    for rej in (console_sections.get("products") or {}).get("rejected") or []:
        if isinstance(rej, dict):
            hits.append(
                {
                    "kind": "product",
                    "label": rej.get("product_name") or rej.get("product_id"),
                    "nav": "products",
                }
            )
    seen: set[tuple[str, str]] = set()
    deduped = []
    for h in hits:
        if not h.get("label"):
            continue
        key = (str(h.get("kind")), str(h.get("label")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(h)
    return deduped


# --- Phase 5 observatory projections (read-only) ---

CODE_TRACE = {
    "PROFILE_NORMALIZE_V2_1": {
        "file": "app/api/payload_adapter.py",
        "function": "profile_from_analyze_body",
    },
    "BREED_RESOLVE_V2_1": {"file": "app/agent/stages/biological.py", "function": "run_biological_stage"},
    "TRAIT_BLEND_V2_1": {"file": "app/agent/stages/biological.py", "function": "run_biological_stage"},
    "RISK_V2_1": {"file": "app/agent/stages/health_risk.py", "function": "compute_risks"},
    "NUTRIENT_TARGET_V2_1": {"file": "app/agent/stages/nutrition.py", "function": "run_nutrition_stage"},
    "PRODUCT_MATCH_V2_1": {"file": "app/agent/stages/optimization.py", "function": "run_optimization_stage"},
    "PACKAGE_OPTIMIZER_V2_1": {
        "file": "app/agent/package_optimizer.py",
        "function": "build_optimized_packages",
    },
    "COVERAGE_V2_1": {"file": "app/agent/package_optimizer.py", "function": "coverage_matrix"},
    "EVIDENCE_RANK_V2_1": {"file": "app/agent/response_assembler.py", "function": "collect_evidence"},
    "ASSESSMENT_PROJECT_V1": {
        "file": "app/data/clinical_assessment.py",
        "function": "build_clinical_assessment",
    },
}

CSV_USAGE_MAP = {
    "BREEDS.csv": {"functions": ["run_biological_stage", "_breed_records"], "formulas": ["BREED_RESOLVE_V2_1", "TRAIT_BLEND_V2_1"]},
    "BREED_CONDITIONS.csv": {"functions": ["_breed_observed", "compute_risks"], "formulas": ["RISK_V2_1"]},
    "TRAIT_INTERACTIONS.csv": {"functions": ["compute_evidence_scores"], "formulas": ["RISK_V2_1"]},
    "TRAIT_BENEFITS.csv": {"functions": ["apply_benefit_reductions"], "formulas": ["RISK_V2_1"]},
    "MIXED_BREED_MATRIX.csv": {"functions": ["apply_mixed_breed_nudge"], "formulas": ["RISK_V2_1"]},
    "CONDITION_INGREDIENTS.csv": {"functions": ["run_nutrition_stage", "map_ingredients"], "formulas": ["NUTRIENT_TARGET_V2_1"]},
    "NUTRIENT_PRIORITIES.csv": {"functions": ["response_assembler"], "formulas": ["NUTRIENT_TARGET_V2_1"]},
    "INGREDIENT_EVIDENCE.csv": {"functions": ["collect_evidence", "ingredient_engine"], "formulas": ["EVIDENCE_RANK_V2_1"]},
    "PRODUCT_CATALOG.csv": {"functions": ["load_candidate_products"], "formulas": ["PRODUCT_MATCH_V2_1", "PACKAGE_OPTIMIZER_V2_1"]},
    "PRODUCT_COMPONENTS.csv": {"functions": ["coverage_matrix", "package_optimizer"], "formulas": ["COVERAGE_V2_1"]},
    "PACKAGE_TIERS.csv": {"functions": ["_pick_staple"], "formulas": ["PACKAGE_OPTIMIZER_V2_1"]},
}


def formula_explorer() -> list[dict[str, Any]]:
    rows = []
    for f in formula_list():
        fid = f["formula_id"]
        code = CODE_TRACE.get(fid) or {
            "file": f.get("owner_module"),
            "function": NOT_TRACEABLE,
        }
        rows.append(
            {
                **f,
                "description": f.get("purpose"),
                "code_file": code.get("file"),
                "python_function": code.get("function"),
                "equation": {
                    "policy": "formula_id_only",
                    "exposed": False,
                    "note": "Proprietary equation text is not exposed. Use observatory step ops (baseline/multiply/set).",
                },
                "example_output": NOT_TRACEABLE,
            }
        )
    return rows


def pipeline_dag() -> dict[str, Any]:
    nodes = [
        "payload",
        "biology",
        "health_risk",
        "epidemiology",
        "management",
        "nutrition",
        "optimization",
        "assembly",
        "assessment",
    ]
    edges = [
        {"from": "payload", "to": "biology"},
        {"from": "biology", "to": "health_risk"},
        {"from": "health_risk", "to": "epidemiology"},
        {"from": "epidemiology", "to": "management"},
        {"from": "epidemiology", "to": "nutrition"},
        {"from": "nutrition", "to": "optimization"},
        {"from": "optimization", "to": "assembly"},
        {"from": "assembly", "to": "assessment"},
    ]
    return {"nodes": nodes, "edges": edges, "kind": "pipeline_dag"}


def observability_coverage(analyze: dict[str, Any], risk_ledgers: list, packages: dict) -> dict[str, Any]:
    """Percent of inspector slots that are traceable (not NT)."""

    def _pct(items: list[bool]) -> float:
        if not items:
            return 0.0
        return round(100.0 * sum(1 for x in items if x) / len(items), 1)

    risk_flags = []
    for r in risk_ledgers:
        for s in r.get("expanded_chain") or r.get("steps") or []:
            if s.get("status") == "NOT_APPLIED_IN_RISK_V2_1":
                continue  # not a gap — intentionally unused
            risk_flags.append(bool(s.get("traceable")))

    pkg_flags = []
    for t in packages.get("tiers") or []:
        for s in t.get("chain") or []:
            pkg_flags.append(bool(s.get("traceable")))
        pkg_flags.append(isinstance(t.get("removed_products"), list))

    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    has_timings = bool(debug.get("stage_timings_ms"))
    has_risk_traces = bool(debug.get("risk_traces"))
    has_fx = bool(debug.get("formula_executions"))

    csv_flags = []
    for fx in debug.get("formula_executions") or []:
        if not isinstance(fx, dict):
            continue
        for lu in fx.get("lookups") or []:
            if isinstance(lu, dict):
                csv_flags.append(lu.get("csv_row") not in (None, ""))

    areas = {
        "risk": _pct(risk_flags) if risk_flags else (100.0 if has_risk_traces else 0.0),
        "formula_execution": 100.0 if has_fx else 0.0,
        "packages": _pct(pkg_flags),
        "timings": 100.0 if has_timings else 0.0,
        "nutrition": 80.0 if any(
            isinstance(fx, dict) and fx.get("formula_id") == "NUTRIENT_TARGET_V2_1"
            for fx in (debug.get("formula_executions") or [])
        )
        else 50.0,
        "products": 40.0 if (analyze.get("productRecommendations")) else 0.0,
        "confidence": 80.0 if has_fx else 30.0,
        "csv_row_ids": _pct(csv_flags) if csv_flags else 0.0,
        "decisions": 100.0 if debug.get("decision_ledger") else 40.0,
    }
    vals = list(areas.values())
    areas["backend"] = round(sum(vals) / len(vals), 1) if vals else 0.0
    return areas


def missing_data_report(analyze: dict[str, Any], risk_ledgers: list) -> list[dict[str, Any]]:
    gaps = []
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    if not debug.get("risk_traces"):
        gaps.append({"kind": "missing_formula_trace", "area": "risk", "detail": "analyze.debug.risk_traces empty"})
    if not debug.get("formula_executions"):
        gaps.append(
            {
                "kind": "missing_formula_execution",
                "area": "risk",
                "detail": "analyze.debug.formula_executions empty — engine did not emit step ledger",
            }
        )
    if not debug.get("stage_timings_ms"):
        gaps.append({"kind": "missing_timing", "area": "performance", "detail": "stage_timings_ms missing"})
    for r in risk_ledgers:
        for ref in r.get("csv_refs") or r.get("csv_lookups") or []:
            if isinstance(ref, dict) and ref.get("row_id") in (None, NOT_TRACEABLE, "NOT CURRENTLY TRACEABLE") and ref.get("csv_row") in (
                None,
                "",
            ):
                gaps.append(
                    {
                        "kind": "missing_csv_row_id",
                        "area": "csv",
                        "condition": r.get("condition"),
                        "csv": ref.get("csv") or ref.get("table"),
                        "detail": "Row number not emitted",
                    }
                )
    for pkg in analyze.get("wellnessPackages") or []:
        if isinstance(pkg, dict) and not pkg.get("products_rejected"):
            gaps.append(
                {
                    "kind": "missing_rejects",
                    "area": "packages",
                    "tier": pkg.get("tier"),
                    "detail": "No products_rejected on package",
                }
            )
    for e in analyze.get("scientificEvidence") or []:
        if isinstance(e, dict) and not (e.get("source_url") or e.get("url")):
            gaps.append(
                {
                    "kind": "missing_evidence_url",
                    "area": "evidence",
                    "title": e.get("title") or e.get("source_name"),
                }
            )
    return gaps


def reverse_lookup(analyze: dict[str, Any], risk_ledgers: list) -> list[dict[str, Any]]:
    """Condition → CSV → formula → products → ingredients → evidence → packages."""
    rows = []
    for r in risk_ledgers:
        cond = r.get("condition")
        if not cond:
            continue
        products = []
        for pkg in analyze.get("wellnessPackages") or []:
            if not isinstance(pkg, dict):
                continue
            for p in pkg.get("products_included") or []:
                if isinstance(p, dict):
                    products.append(p.get("product_name") or p.get("name"))
        ingredients = []
        for t in analyze.get("nutritionalTargets") or []:
            if isinstance(t, dict):
                ingredients.append(t.get("ingredient") or t.get("nutrient"))
        evidence = []
        for e in analyze.get("scientificEvidence") or []:
            if isinstance(e, dict) and (
                e.get("condition") == cond or cond in str(e.get("linked_condition") or "")
            ):
                evidence.append(e.get("title") or e.get("source_name"))
        rows.append(
            {
                "condition": cond,
                "csv_rows": r.get("csv_refs") or r.get("csv_lookups") or [],
                "formula_id": r.get("locked_formula_id") or FORMULA_RISK,
                "products": sorted({p for p in products if p})[:20],
                "ingredients": sorted({i for i in ingredients if i})[:20],
                "evidence": evidence[:10],
                "packages": [
                    pkg.get("tier")
                    for pkg in (analyze.get("wellnessPackages") or [])
                    if isinstance(pkg, dict)
                ],
                "code": r.get("code"),
            }
        )
    return rows


def raw_production_objects(analyze: dict[str, Any]) -> dict[str, Any]:
    return {
        "healthInsights": analyze.get("healthInsights"),
        "nutritionalTargets": analyze.get("nutritionalTargets"),
        "productRecommendations": analyze.get("productRecommendations"),
        "wellnessPackages": analyze.get("wellnessPackages"),
        "scientificEvidence": analyze.get("scientificEvidence"),
        "calculationTrace": analyze.get("calculationTrace"),
        "debug": analyze.get("debug"),
        "preventativeNutritionSystem": analyze.get("preventativeNutritionSystem"),
    }


def api_contract_inspector(assessment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not assessment:
        return [{"note": "No ClinicalAssessment attached"}]
    rows = []
    for key, val in assessment.items():
        if key == "meta":
            continue
        rows.append(
            {
                "backend_object": f"assessment.{key}",
                "frontend_field": key,
                "component": NOT_TRACEABLE,
                "displayed_at": NOT_TRACEABLE,
                "has_data": val is not None,
            }
        )
    return rows


def nutrition_math_from_packages(analyze: dict[str, Any]) -> list[dict[str, Any]]:
    """Project coverage_matrix / daily_nutrition_intake when present — no recompute."""
    rows = []
    for pkg in analyze.get("wellnessPackages") or []:
        if not isinstance(pkg, dict) or not pkg.get("recommended"):
            continue
        matrix = pkg.get("coverage_matrix") or []
        for m in matrix:
            if not isinstance(m, dict):
                continue
            rows.append(
                {
                    "nutrient": m.get("nutrient") or m.get("ingredient_key"),
                    "target": m.get("recommended") or m.get("target"),
                    "provided": m.get("provided"),
                    "coverage_percent": m.get("coverage_percent"),
                    "unit": m.get("unit"),
                    "chain": [
                        {"step": "target", "value": m.get("recommended") or m.get("target"), "traceable": True},
                        {
                            "step": "food_contribution",
                            **_nt("Food vs treat vs supplement split not always on coverage_matrix"),
                        },
                        {"step": "provided_total", "value": m.get("provided"), "traceable": m.get("provided") is not None},
                        {
                            "step": "coverage",
                            "value": m.get("coverage_percent"),
                            "traceable": m.get("coverage_percent") is not None,
                            "unit": "%",
                        },
                    ],
                    "tier": pkg.get("tier"),
                    "raw": m,
                }
            )
        intake = pkg.get("daily_nutrition_intake") or []
        for item in intake:
            if not isinstance(item, dict):
                continue
            rows.append(
                {
                    "nutrient": item.get("nutrient") or item.get("ingredient"),
                    "source": "daily_nutrition_intake",
                    "chain": [
                        {"step": "target", "value": item.get("target") or item.get("daily_target"), "traceable": True},
                        {"step": "food", "value": item.get("food") or item.get("from_food"), "traceable": item.get("food") is not None or item.get("from_food") is not None},
                        {"step": "treat", "value": item.get("treat"), "traceable": item.get("treat") is not None},
                        {"step": "supplement", "value": item.get("supplement") or item.get("from_supplement"), "traceable": item.get("supplement") is not None or item.get("from_supplement") is not None},
                        {"step": "total", "value": item.get("total") or item.get("provided"), "traceable": True},
                        {"step": "coverage", "value": item.get("coverage_percent") or item.get("coverage"), "traceable": True},
                    ],
                    "raw": item,
                }
            )
        break
    return rows


# === from engine_trace.py ===

import os
import time
from datetime import datetime, timezone
from typing import Any

from app.agent.version import ALGORITHM_VERSION, ENGINE_NAME
from app.data.repository import DataRepository
from app.inference.formula_registry import (
    FORMULA_ACTIVITY,
    FORMULA_ASSESSMENT,
    FORMULA_BREED,
    FORMULA_EVIDENCE,
    FORMULA_NUTRIENT,
    FORMULA_PACKAGE,
    FORMULA_PRODUCT,
    FORMULA_RISK,
    FORMULA_TRAIT,
    FORMULA_VALIDATION,
)

# Re-export for historical imports
__all_formula_ids__ = (
    FORMULA_BREED,
    FORMULA_TRAIT,
    FORMULA_RISK,
    FORMULA_NUTRIENT,
    FORMULA_ACTIVITY,
    FORMULA_PRODUCT,
    FORMULA_PACKAGE,
    FORMULA_EVIDENCE,
    FORMULA_VALIDATION,
    FORMULA_ASSESSMENT,
)


def is_engine_debug(*, request_debug: bool | None = None) -> bool:
    """True when PPIE_DEBUG / DEBUG_ENGINE env is set, or request explicitly asks."""
    if request_debug is True:
        return True
    for key in ("PPIE_DEBUG", "DEBUG_ENGINE"):
        raw = str(os.getenv(key, "")).strip().lower()
        if raw in ("1", "true", "yes", "on"):
            return True
    return False


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stage(
    *,
    name: str,
    formula_id: str,
    inputs: Any,
    outputs: Any,
    csv_sources: list[dict[str, Any]] | None = None,
    dependencies: list[str] | None = None,
    elapsed_ms: float | None = None,
    confidence: Any = None,
    notes: list[str] | None = None,
    missing: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "stage": name,
        "formula_id": formula_id,
        "algorithm_version": ALGORITHM_VERSION,
        "inputs": inputs,
        "outputs": outputs,
        "csv_sources": csv_sources or [],
        "dependencies": dependencies or [],
        "elapsed_ms": elapsed_ms,
        "confidence": confidence,
        "notes": notes or [],
        "missing": missing or [],
        # Explicit: never include equation text
        "equation_exposed": False,
    }


def _csv_ref(table: str, rows: Any = None, note: str | None = None) -> dict[str, Any]:
    ref: dict[str, Any] = {"table": table}
    if rows is not None:
        ref["rows"] = rows
    if note:
        ref["note"] = note
    return ref


def _profile_section(analyze: dict[str, Any]) -> dict[str, Any]:
    p = analyze.get("profile") or analyze.get("pet") or {}
    return _stage(
        name="profile",
        formula_id="PROFILE_NORMALIZE_V2_1",
        inputs={"raw_profile_keys": sorted(p.keys())},
        outputs={
            "display_name": p.get("pet_name") or p.get("name"),
            "breeds": p.get("breeds"),
            "weight_kg": p.get("weight_kg"),
            "age_years": p.get("age_years"),
            "activity_level": p.get("activity_level"),
            "environment": p.get("current_environment"),
            "observed_conditions": p.get("observed_conditions") or [],
        },
        dependencies=[],
        notes=["DogProfile normalized into analyze.profile"],
    )


def _breed_section(analyze: dict[str, Any]) -> dict[str, Any]:
    bio = analyze.get("biology") or {}
    resolved = bio.get("resolved_breeds") or bio.get("breeds") or []
    descriptors = bio.get("descriptors") or []
    profile = analyze.get("profile") or {}
    breeds_in = profile.get("breeds") or []
    items = []
    for i, row in enumerate(resolved if isinstance(resolved, list) else []):
        if not isinstance(row, dict):
            items.append({"name": str(row)})
            continue
        weight = row.get("weight_pct") or row.get("split_pct") or row.get("weight")
        items.append(
            {
                "name": row.get("breed") or row.get("name") or row.get("breed_name"),
                "weight_pct": weight,
                "traits_loaded": row.get("traits") or {},
            }
        )
    # If weights missing, assume equal split for audit display only (not a formula change)
    if items and all(x.get("weight_pct") is None for x in items) and len(breeds_in) >= 1:
        for x in items:
            x["weight_pct_note"] = "Not emitted on resolved row; see DogProfile breed_split"
    return _stage(
        name="breed",
        formula_id=FORMULA_BREED,
        inputs={"breeds": breeds_in},
        outputs={"resolved": items, "descriptors": descriptors, "record_count": len(items)},
        csv_sources=[
            _csv_ref("BREEDS"),
            _csv_ref("BREED_ALIASES"),
            _csv_ref("MIXED_BREED_MATRIX"),
            _csv_ref("MIXED_BREED_INTERACTIONS"),
        ],
        dependencies=["profile"],
        notes=["Breed resolution + descriptor load; formula_id only (no equation text)"],
    )


def _traits_section(analyze: dict[str, Any]) -> dict[str, Any]:
    bio = analyze.get("biology") or {}
    traits = bio.get("trait_summary") or []
    items = []
    for t in traits if isinstance(traits, list) else []:
        if isinstance(t, dict):
            items.append(
                {
                    "trait": t.get("title") or t.get("trait") or t.get("name"),
                    "category": t.get("category") or t.get("group"),
                    "formula_id": FORMULA_TRAIT,
                    "contribution_note": "Weighted inheritance from resolved breeds (see formula_id)",
                    "summary": t.get("summary") or t.get("explanation") or "",
                }
            )
        else:
            items.append({"trait": str(t), "formula_id": FORMULA_TRAIT})
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "biology"), {})
    return _stage(
        name="traits",
        formula_id=FORMULA_TRAIT,
        inputs={"descriptor_count": len(bio.get("descriptors") or [])},
        outputs={"traits": items, "count": len(items)},
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or ["TRAIT_PURPOSES", "TRAIT_CONTRIBUTION_WEIGHTS"])],
        dependencies=["breed"],
    )


def _risks_section(analyze: dict[str, Any]) -> dict[str, Any]:
    """Risk audit from emitted fields only — no invented modifier deltas."""
    insights = analyze.get("healthInsights") or []
    calc = {str(c.get("condition")): c for c in (analyze.get("calculationTrace") or []) if isinstance(c, dict)}
    risks = []
    missing = []
    for h in insights:
        if not isinstance(h, dict):
            continue
        title = h.get("title") or h.get("condition") or "Condition"
        ct = calc.get(str(title)) or {}
        # Available intermediate values from engine emission (not proprietary constants)
        intermediates = {
            "biological_risk_percent": h.get("biological_risk_percent") or h.get("estimated_biological_risk_percent"),
            "observed_breed_prevalence_percent": h.get("observed_breed_prevalence_percent")
            or h.get("observed_prevalence_percent"),
            "estimate_vs_observed_difference": h.get("estimate_vs_observed_difference"),
            "priority_score": h.get("priority_score"),
            "confidence_percent": h.get("confidence_percent"),
        }
        if intermediates["observed_breed_prevalence_percent"] is None:
            missing.append(
                {
                    "subject": title,
                    "missing": "published_prevalence_or_observed_breed_prevalence",
                    "reason": "No observed breed prevalence emitted on this insight",
                    "fallback": "Trait / biology estimate path",
                    "severity": "warning",
                }
            )
        risks.append(
            {
                "condition": title,
                "goal_id_internal": h.get("goal_id"),  # debug only
                "formula_id": FORMULA_RISK,
                "inputs": {
                    "supporting_traits": h.get("supporting_traits") or [],
                    "supporting_conditions": h.get("supporting_conditions") or [],
                    "observed_inputs": ct.get("observed_inputs") or {},
                    "published_evidence_rows": len(ct.get("published_evidence") or []),
                },
                "outputs": {
                    "final_risk_percent": intermediates["biological_risk_percent"],
                    "priority_score": intermediates["priority_score"],
                    "confidence_percent": intermediates["confidence_percent"],
                },
                "intermediates": intermediates,
                "trait_contributions": ct.get("trait_contributions") or [],
                "published_evidence": ct.get("published_evidence") or [],
                "decision_log": ct.get("decision_log") or [],
                "notes": [
                    "Modifier_line_items (e.g. activity +4%) are not separately emitted by RISK_V2_1; "
                    "audit uses intermediates the engine already publishes.",
                ],
            }
        )
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "health_risk"), {})
    return _stage(
        name="risks",
        formula_id=FORMULA_RISK,
        inputs={"insight_count": len(insights)},
        outputs={"risks": risks, "count": len(risks)},
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or ["BREED_CONDITIONS", "TRAIT_INTERACTIONS"])],
        dependencies=["traits", "breed"],
        missing=missing,
        confidence={"priority_count": len(risks)},
    )


def _nutrition_section(analyze: dict[str, Any]) -> dict[str, Any]:
    targets = analyze.get("nutritionalTargets") or analyze.get("ingredientRequirements") or []
    calc = analyze.get("calculationTrace") or []
    items = []
    for t in targets if isinstance(targets, list) else []:
        if not isinstance(t, dict):
            continue
        # Product contributions from calculation trace nutrient lines
        food_mg = None
        supp_mg = None
        for c in calc:
            for pc in c.get("product_contributions") or []:
                for nl in pc.get("nutrient_lines") or []:
                    if str(nl.get("nutrient") or "").lower() != str(t.get("ingredient") or t.get("name") or "").lower():
                        continue
                    # Classify by product type if available
                    food_mg = (food_mg or 0) + float(nl.get("provided_value") or 0)
        items.append(
            {
                "nutrient": t.get("ingredient") or t.get("name"),
                "formula_id": FORMULA_NUTRIENT,
                "inputs": {
                    "supports_goals": t.get("supports_goals") or t.get("for_conditions") or [],
                },
                "outputs": {
                    "daily_target": t.get("daily_target") or t.get("daily"),
                    "monthly_target": t.get("monthly_target") or t.get("monthly"),
                    "coverage_pct": t.get("coverage_pct") or t.get("coverage"),
                    "provided_from_products_sum": food_mg,
                },
                "csv_sources": [
                    _csv_ref("CONDITION_INGREDIENTS"),
                    _csv_ref("INGREDIENT_EVIDENCE"),
                    _csv_ref("INGREDIENT_MECHANISMS"),
                ],
            }
        )
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "nutrition"), {})
    return _stage(
        name="nutrition",
        formula_id=FORMULA_NUTRIENT,
        inputs={"target_count": len(items)},
        outputs={"targets": items},
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or [])],
        dependencies=["risks"],
        missing=[
            {
                "missing": "per_source_food_vs_supplement_split",
                "reason": "Engine emits combined product contributions; split not always available",
                "severity": "info",
            }
        ]
        if items
        else [],
    )


def _activity_section(analyze: dict[str, Any]) -> dict[str, Any]:
    act = analyze.get("activityRecommendations") or {}
    return _stage(
        name="activity",
        formula_id=FORMULA_ACTIVITY,
        inputs={"activity_level": (analyze.get("profile") or {}).get("activity_level")},
        outputs=act if isinstance(act, dict) else {"items": act},
        csv_sources=[_csv_ref("ACTIVITY_PRESCRIPTION_RULES"), _csv_ref("CONDITION_ACTIVITIES")],
        dependencies=["breed", "risks"],
    )


def _grooming_section(analyze: dict[str, Any]) -> dict[str, Any]:
    g = analyze.get("groomer") or []
    return _stage(
        name="grooming",
        formula_id="GROOMING_OBS_V2_1",
        inputs={"observed_conditions": (analyze.get("profile") or {}).get("observed_conditions") or []},
        outputs={"checklist": g if isinstance(g, list) else g},
        csv_sources=[_csv_ref("GROOMING_OBSERVATION_DEFS")],
        dependencies=["profile"],
    )


def _products_section(analyze: dict[str, Any]) -> dict[str, Any]:
    recs = analyze.get("productRecommendations") or analyze.get("products") or []
    analyses = analyze.get("productAnalyses") or {}
    selected = []
    for p in recs if isinstance(recs, list) else []:
        if not isinstance(p, dict):
            continue
        pid = str(p.get("product_id") or "")
        selected.append(
            {
                "product_id": pid,
                "name": p.get("product_name") or p.get("name"),
                "formula_id": FORMULA_PRODUCT,
                "inputs": {"category": p.get("category") or p.get("type")},
                "outputs": {
                    "serving": p.get("serving") or p.get("serving_size") or p.get("daily_amount"),
                    "monthly_cost": p.get("monthly_cost"),
                    "why": p.get("why") or p.get("why_selected") or p.get("short_description"),
                },
                "analysis_present": bool(analyses.get(pid)),
            }
        )
    pipe = next((s for s in (analyze.get("pipeline_trace") or []) if s.get("stage") == "products"), {})
    return _stage(
        name="products",
        formula_id=FORMULA_PRODUCT,
        inputs={"recommendation_count": len(selected)},
        outputs={
            "selected": selected,
            "candidates_note": "Full rejected-candidate list is not emitted on analyze; package optimizer holds selection set",
            "analyses_keys": list(analyses.keys())[:40] if isinstance(analyses, dict) else [],
        },
        csv_sources=[_csv_ref(f) for f in (pipe.get("source_files") or ["PRODUCT_CATALOG", "PRODUCT_COMPONENTS"])],
        dependencies=["nutrition"],
        missing=[
            {
                "missing": "rejected_product_candidate_list",
                "reason": "Not currently serialized on analyze envelope",
                "severity": "info",
            }
        ],
    )


def _packages_section(analyze: dict[str, Any]) -> dict[str, Any]:
    pkgs = analyze.get("wellnessPackages") or []
    tiers = []
    for p in pkgs if isinstance(pkgs, list) else []:
        if not isinstance(p, dict):
            continue
        products = p.get("products_included") or p.get("product_cards") or []
        tiers.append(
            {
                "tier": p.get("tier") or p.get("package_id"),
                "title": p.get("title"),
                "recommended": bool(p.get("recommended")),
                "formula_id": FORMULA_PACKAGE,
                "inputs": {
                    "product_count": len(products) if isinstance(products, list) else 0,
                },
                "outputs": {
                    "coverage_score": p.get("coverage_score"),
                    "overall_score": p.get("overall_score"),
                    "monthly_cost": p.get("monthly_cost"),
                    "yearly_cost": p.get("yearly_cost"),
                    "summary": p.get("package_summary") or p.get("tagline"),
                },
            }
        )
    return _stage(
        name="packages",
        formula_id=FORMULA_PACKAGE,
        inputs={"tier_count": len(tiers)},
        outputs={
            "tiers": tiers,
            "recommended": next((t for t in tiers if t.get("recommended")), tiers[1] if len(tiers) > 1 else (tiers[0] if tiers else None)),
        },
        csv_sources=[_csv_ref("PACKAGE_TIERS"), _csv_ref("PRODUCT_PRICING"), _csv_ref("PRODUCT_DEFAULTS")],
        dependencies=["products", "nutrition", "risks"],
        missing=[
            {
                "missing": "candidates_evaluated_count",
                "reason": "Optimizer does not emit candidate tally on package row",
                "severity": "info",
            }
        ],
    )


def _evidence_section(analyze: dict[str, Any]) -> dict[str, Any]:
    raw = analyze.get("scientificEvidence") or analyze.get("evidence") or []
    items = []
    for e in raw if isinstance(raw, list) else []:
        if not isinstance(e, dict):
            continue
        items.append(
            {
                "title": e.get("title") or e.get("source_name"),
                "formula_id": FORMULA_EVIDENCE,
                "inputs": {"supports": e.get("supports") or e.get("conditions") or []},
                "outputs": {
                    "journal": e.get("journal") or e.get("source_name"),
                    "year": e.get("year"),
                    "url": e.get("source_url") or e.get("url"),
                    "quoted_finding": e.get("finding") or e.get("quote") or e.get("summary"),
                    "evidence_level": e.get("evidence_level") or e.get("level"),
                    "status": e.get("status"),
                },
            }
        )
    return _stage(
        name="evidence",
        formula_id=FORMULA_EVIDENCE,
        inputs={"count": len(items)},
        outputs={"items": items},
        csv_sources=[_csv_ref("CLINICAL_EVIDENCE_BASE"), _csv_ref("INGREDIENT_EVIDENCE")],
        dependencies=["risks", "nutrition"],
    )


def _validation_section(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    val = (assessment or {}).get("validation") or {}
    items = val.get("items") if isinstance(val, dict) else []
    if not items:
        # Derive lightweight validation slots from health insights
        items = []
        for h in analyze.get("healthInsights") or []:
            if not isinstance(h, dict):
                continue
            title = h.get("title")
            obs = h.get("observed_breed_prevalence_percent") or h.get("observed_prevalence_percent")
            est = h.get("biological_risk_percent") or h.get("estimated_biological_risk_percent")
            if obs is not None:
                items.append(
                    {
                        "subject": title,
                        "formula_id": FORMULA_VALIDATION,
                        "status": "compared",
                        "inputs": {"published_or_observed_pct": obs, "ppie_estimate_pct": est},
                        "outputs": {
                            "deviation_pct": h.get("estimate_vs_observed_difference"),
                            "confidence_percent": h.get("confidence_percent"),
                        },
                    }
                )
            else:
                items.append(
                    {
                        "subject": title,
                        "formula_id": FORMULA_VALIDATION,
                        "status": "unavailable",
                        "inputs": {"ppie_estimate_pct": est},
                        "outputs": {
                            "reason": "No high-quality prevalence study linked for this exact population",
                            "derived_from": ["breed", "traits", "environment", "nutrition"],
                        },
                    }
                )
    return _stage(
        name="validation",
        formula_id=FORMULA_VALIDATION,
        inputs={"item_count": len(items)},
        outputs={"items": items},
        dependencies=["risks", "evidence"],
    )


def run_consistency_checks(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Non-mutating sanity checks — warnings only."""
    warnings: list[dict[str, Any]] = []
    for h in analyze.get("healthInsights") or []:
        if not isinstance(h, dict):
            continue
        pct = h.get("biological_risk_percent")
        if pct is not None:
            try:
                v = float(pct)
                if v < 0 or v > 100:
                    warnings.append(
                        {
                            "check": "risk_bounds",
                            "severity": "error",
                            "subject": h.get("title"),
                            "detail": f"biological_risk_percent out of bounds: {v}",
                        }
                    )
            except (TypeError, ValueError):
                warnings.append(
                    {
                        "check": "risk_bounds",
                        "severity": "error",
                        "subject": h.get("title"),
                        "detail": "non-numeric risk percent",
                    }
                )
        conf = h.get("confidence_percent")
        if conf is not None:
            try:
                c = float(conf)
                if c < 0 or c > 100:
                    warnings.append(
                        {
                            "check": "confidence_bounds",
                            "severity": "warning",
                            "subject": h.get("title"),
                            "detail": f"confidence_percent out of bounds: {c}",
                        }
                    )
            except (TypeError, ValueError):
                pass

    breeds = (analyze.get("profile") or {}).get("breeds") or []
    resolved = (analyze.get("biology") or {}).get("resolved_breeds") or []
    weights = []
    for r in resolved if isinstance(resolved, list) else []:
        if isinstance(r, dict) and r.get("weight_pct") is not None:
            try:
                weights.append(float(r["weight_pct"]))
            except (TypeError, ValueError):
                pass
    if weights:
        total = sum(weights)
        # Allow 0–1 or 0–100 scales
        if total > 1.5:
            if abs(total - 100) > 1.0:
                warnings.append(
                    {
                        "check": "breed_weights_sum",
                        "severity": "warning",
                        "detail": f"breed weight_pct sum={total} (expected ~100)",
                    }
                )
        elif abs(total - 1.0) > 0.02:
            warnings.append(
                {
                    "check": "breed_weights_sum",
                    "severity": "warning",
                    "detail": f"breed weight_pct sum={total} (expected ~1.0)",
                }
            )

    for t in analyze.get("nutritionalTargets") or []:
        if not isinstance(t, dict):
            continue
        cov = t.get("coverage_pct")
        if cov is not None:
            try:
                if float(cov) < 0:
                    warnings.append(
                        {
                            "check": "nutrition_coverage_nonnegative",
                            "severity": "error",
                            "subject": t.get("ingredient") or t.get("name"),
                            "detail": f"negative coverage {cov}",
                        }
                    )
            except (TypeError, ValueError):
                pass

    if assessment:
        pkg = assessment.get("packages") or {}
        tiers = pkg.get("tiers") or []
        rec = pkg.get("recommended_tier")
        if rec and tiers:
            match = next((t for t in tiers if t.get("tier") == rec), None)
            if match and not match.get("recommended"):
                warnings.append(
                    {
                        "check": "package_recommended_flag",
                        "severity": "warning",
                        "detail": "recommended_tier does not have recommended=true on tier row",
                    }
                )

    if not breeds:
        warnings.append({"check": "profile_breeds", "severity": "error", "detail": "No breeds on profile"})

    return warnings


def build_engine_trace(
    repo: DataRepository,
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    *,
    timings: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Build full EngineTrace from frozen analyze (+ optional assessment)."""
    t0 = time.perf_counter()
    sections = {
        "profile": _profile_section(analyze),
        "breed": _breed_section(analyze),
        "traits": _traits_section(analyze),
        "risks": _risks_section(analyze),
        "nutrition": _nutrition_section(analyze),
        "activity": _activity_section(analyze),
        "grooming": _grooming_section(analyze),
        "products": _products_section(analyze),
        "packages": _packages_section(analyze),
        "evidence": _evidence_section(analyze),
        "validation": _validation_section(analyze, assessment),
    }
    consistency = run_consistency_checks(analyze, assessment)
    build_ms = round((time.perf_counter() - t0) * 1000, 2)
    timeline = []
    for name, sec in sections.items():
        timeline.append(
            {
                "stage": name,
                "elapsed_ms": (timings or {}).get(name) or sec.get("elapsed_ms"),
                "formula_id": sec.get("formula_id"),
            }
        )
    if timings:
        for k, v in timings.items():
            if k not in {t["stage"] for t in timeline}:
                timeline.append({"stage": k, "elapsed_ms": v, "formula_id": None})

    return {
        "schema": "engine_trace.v1",
        "engine": ENGINE_NAME,
        "algorithm_version": ALGORITHM_VERSION,
        "data_version": getattr(repo, "version", None) or "",
        "content_hash": getattr(repo, "csv_hash", None) or "",
        "generated_at": _now_iso(),
        "debug": True,
        "equation_policy": "formula_id_only",
        "formula_ids": {
            "breed": FORMULA_BREED,
            "traits": FORMULA_TRAIT,
            "risks": FORMULA_RISK,
            "nutrition": FORMULA_NUTRIENT,
            "activity": FORMULA_ACTIVITY,
            "products": FORMULA_PRODUCT,
            "packages": FORMULA_PACKAGE,
            "evidence": FORMULA_EVIDENCE,
            "validation": FORMULA_VALIDATION,
            "assessment": FORMULA_ASSESSMENT,
        },
        "sections": sections,
        "pipeline_trace_raw": analyze.get("pipeline_trace") or [],
        "calculation_trace_raw": analyze.get("calculationTrace") or [],
        "timeline": timeline,
        "consistency_warnings": consistency,
        "meta": {
            "trace_build_ms": build_ms,
            "analyze_keys": sorted(analyze.keys()),
            "assessment_attached": bool(assessment),
        },
    }


# === from validation_console.py ===

from typing import Any

from app.data.repository import DataRepository
from app.inference.formula_registry import FORMULA_REGISTRY, FORMULA_RISK, formula_list
from app.inference.models import NOT_TRACEABLE

NAV = [
    {"id": "top_summary", "label": "Top Summary"},
    {"id": "clinical_output", "label": "Clinical Output"},
    {"id": "input", "label": "Input"},
    {"id": "validation", "label": "Validation"},
    {"id": "runtime_flow", "label": "Data Flow"},
    {"id": "repository", "label": "Repository Retrieval"},
    {"id": "timeline", "label": "FormulaGraph Timeline"},
    {"id": "formulas", "label": "Formula Details"},
    {"id": "evidence", "label": "Scientific Evidence"},
    {"id": "numerical_provenance", "label": "Numerical Provenance"},
    {"id": "replay", "label": "Replay"},
    {"id": "sensitivity", "label": "Sensitivity"},
    {"id": "publication_risk", "label": "Publication Risk"},
    {"id": "risks", "label": "Risk Aggregation"},
    {"id": "nutrition", "label": "Nutrition"},
    {"id": "ingredients", "label": "Ingredient Selection"},
    {"id": "products", "label": "Product Optimization"},
    {"id": "packages", "label": "Package Optimization"},
    {"id": "assessment", "label": "Final Assessment"},
    {"id": "json", "label": "JSON Output"},
    {"id": "performance", "label": "Performance"},
]


def _assessment_provenance(assessment: dict[str, Any] | None) -> dict[str, Any]:
    if not assessment:
        return {"modules": [], "note": "No assessment attached"}
    mapping = [
        ("profile", "analyze.profile / pet", "projection", ["profile", "pet"]),
        ("breed", "analyze.biology", "projection", ["biology"]),
        ("traits", "analyze.biology.trait_summary", "projection", ["biology"]),
        ("health", "analyze.healthInsights", "projection", ["healthInsights", "calculationTrace"]),
        ("nutrition", "analyze.nutritionalTargets", "projection", ["nutritionalTargets"]),
        ("packages", "analyze.wellnessPackages", "projection", ["wellnessPackages"]),
        ("products", "analyze.productRecommendations", "projection", ["productRecommendations"]),
        ("evidence", "analyze.scientificEvidence", "projection", ["scientificEvidence"]),
    ]
    modules = []
    for mid, source, kind, keys in mapping:
        modules.append(
            {
                "module_id": mid,
                "source_engine_node": source,
                "kind": kind,
                "computed_in_assessment": False,
                "analyze_keys": keys,
                "has_data": assessment.get(mid) is not None,
            }
        )
    return {"modules": modules, "note": "ClinicalAssessment is projection-only."}


def _validation_checklist(
    analyze: dict[str, Any], assessment: dict[str, Any] | None, consistency: list
) -> list[dict[str, Any]]:
    insights = analyze.get("healthInsights") or []
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
    checks = [
        {
            "id": "risks_present",
            "ok": bool(insights),
            "label": "Health priorities present",
            "detail": f"{len(insights)} insights",
        },
        {
            "id": "evidence_present",
            "ok": bool(analyze.get("scientificEvidence")),
            "label": "Evidence attached",
            "detail": f"{len(analyze.get('scientificEvidence') or [])} items",
        },
        {
            "id": "formula_registry",
            "ok": bool(FORMULA_REGISTRY),
            "label": "Formula registry loaded",
            "detail": f"{len(FORMULA_REGISTRY)} formulas",
        },
        {
            "id": "risk_traces",
            "ok": bool(debug.get("risk_traces")),
            "label": "Observatory risk traces",
            "detail": f"{len(debug.get('risk_traces') or [])} conditions",
        },
        {
            "id": "stage_timings",
            "ok": bool(debug.get("stage_timings_ms")),
            "label": "Stage timings",
            "detail": str(list((debug.get("stage_timings_ms") or {}).keys())),
        },
        {
            "id": "package_rejects",
            "ok": bool(debug.get("package_rejects"))
            or any(
                isinstance(p, dict) and p.get("products_rejected")
                for p in (analyze.get("wellnessPackages") or [])
            ),
            "label": "Package rejected products",
            "detail": f"{len(debug.get('package_rejects') or [])} rejects in debug",
        },
        {
            "id": "assessment",
            "ok": bool(assessment),
            "label": "ClinicalAssessment attached",
            "detail": "present" if assessment else "missing",
        },
        {
            "id": "consistency",
            "ok": not consistency,
            "label": "No consistency warnings",
            "detail": f"{len(consistency)} warnings",
        },
    ]
    return checks


def _gaps() -> list[dict[str, Any]]:
    return [
        {
            "id": "csv_row_ids",
            "area": "csv",
            "status": "PARTIAL",
            "detail": "RISK + nutrition lookups emit csv_row/row_id. Package optimizer product joins still sparse on row IDs.",
            "blocks_complete_audit": False,
            "instrumentation": "Extend LookupResult through catalog joins",
        },
        {
            "id": "optimizer_pass_scores",
            "area": "packages",
            "status": NOT_TRACEABLE,
            "detail": "Per-candidate trial scores inside greedy/best-add loops not stored.",
            "blocks_complete_audit": True,
            "instrumentation": "Append optimization_passes[] without changing selection",
        },
        {
            "id": "stable_business_row_keys",
            "area": "csv",
            "status": "PARTIAL",
            "detail": "row_id is currently `{TABLE}_{csv_line}` from loader, not a stable BC_##### business key.",
            "blocks_complete_audit": False,
            "instrumentation": "Add explicit id columns to CSVs when migrating data platform",
        },
        {
            "id": "conf_factor_chain",
            "area": "confidence",
            "status": "PARTIAL",
            "detail": "RISK confidence is category-coverage only (emitted). CONF_V1 study-quality ladder is not production.",
            "blocks_complete_audit": False,
            "instrumentation": "Emit confidence breakdown when approved",
        },
        {
            "id": "activity_weight_climate_risk",
            "area": "risk",
            "status": "NOT_APPLIED_IN_RISK_V2_1",
            "detail": "Locked risk path does not apply activity/weight/climate multipliers.",
            "blocks_complete_audit": False,
            "instrumentation": "N/A — not part of RISK_V2_1",
        },
        {
            "id": "cache_lookup_ms",
            "area": "performance",
            "status": NOT_TRACEABLE,
            "detail": "Per-lookup ms and cache hits not instrumented (formula_execution.timing.cache = NT).",
            "blocks_complete_audit": False,
            "instrumentation": "DataPlatform query counters",
        },
    ]


def build_validation_console(
    repo: DataRepository,
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    *,
    timings: dict[str, float] | None = None,
    raw_request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full Validation Console / Observatory document for /debug/calculation."""
    trace = build_engine_trace(repo, analyze, assessment, timings=timings)

    risk_ledgers = expand_risk_ledgers(analyze)
    emitted_formula_executions = formula_execution_inspector(analyze)
    derived_formula_executions = _derive_formula_executions_from_trace(trace, analyze)
    formula_executions = _merge_formula_executions(emitted_formula_executions, derived_formula_executions)
    math_audit = _attach_math_audit(formula_executions)
    decisions_ledger = decision_ledger_inspector(analyze)
    provenance = provenance_inspector(analyze)
    competitions = competition_inspector(analyze)
    nutrition = nutrition_inspector(analyze)
    nutrition_math = nutrition_math_from_packages(analyze)
    ingredients = ingredient_resolution_inspector(analyze)
    products = product_match_inspector(analyze)
    packages = package_optimizer_inspector(analyze)
    evidence = evidence_inspector(analyze)
    confidence = confidence_inspector(analyze)
    coverage = coverage_inspector(analyze)
    csv_lookups = csv_dependency_viewer(analyze)
    timeline = pipeline_timeline(analyze, timings)
    performance = performance_inspector(analyze, timings)
    graph = formula_graph()
    dag = pipeline_dag()
    decisions = decision_trees(analyze)
    formulas = formula_explorer()
    obs_cov = observability_coverage(analyze, risk_ledgers, packages)
    missing = missing_data_report(analyze, risk_ledgers)
    reverse = reverse_lookup(analyze, risk_ledgers)
    raw_objs = raw_production_objects(analyze)

    profile = analyze.get("profile") or analyze.get("pet") or {}
    debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}

    console: dict[str, Any] = {
        "schema": "validation_console.v8",
        "debug": True,
        "equation_policy": "emitted_step_expressions",
        "not_traceable_token": NOT_TRACEABLE,
        "philosophy": "Clinical Execution Explorer — every stage explains inputs, repository retrieval, formulas, intermediates, evidence, outputs, timing, and confidence. Engine-emitted ledgers only; no invented intermediates.",
        "primary_view": "clinical_execution_explorer",
        "title": "Clinical Execution Explorer",
        "single_page": True,
        "nav": NAV,
        "formula_registry": formula_list(),
        "formula_catalog": formulas,
        "formula_explorer": formulas,
        "formula_executions": formula_executions,
        "execution_records": formula_executions,
        "execution_index": {
            str(fx.get("execution_id")): fx
            for fx in formula_executions
            if isinstance(fx, dict) and fx.get("execution_id")
        },
        "execution_status_summary": {
            "executed": len(formula_executions),
            "source_located": sum(
                1
                for fx in formula_executions
                if isinstance(fx, dict)
                and ((fx.get("source_location") or {}).get("status") == "SOURCE_LOCATED")
            ),
            "documented": sum(
                1 for fx in formula_executions if isinstance(fx, dict) and fx.get("documentation_status") == "DOCUMENTED"
            ),
            "warehouse_row_traced": sum(
                1 for fx in formula_executions if isinstance(fx, dict) and fx.get("warehouse_status") == "WAREHOUSE_ROW_TRACED"
            ),
            "evidence_traced": sum(
                1 for fx in formula_executions if isinstance(fx, dict) and fx.get("evidence_status") == "EVIDENCE_TRACED"
            ),
            "replay_supported": sum(
                1 for fx in formula_executions if isinstance(fx, dict) and (fx.get("replay") or {}).get("status") not in ("NOT_IMPLEMENTED", None)
            ),
            "sensitivity_supported": sum(
                1 for fx in formula_executions if isinstance(fx, dict) and (fx.get("sensitivity") or {}).get("status") == "AVAILABLE"
            ),
        },
        "formula_executions_emitted": emitted_formula_executions,
        "formula_executions_derived": derived_formula_executions,
        "decision_ledger": decisions_ledger,
        "provenance_index": provenance,
        "lookup_competitions": competitions,
        "modifier_ledger": [
            {**m, "formula_id": fx.get("formula_id"), "subject": fx.get("subject") or fx.get("condition")}
            for fx in formula_executions
            for m in (fx.get("modifiers") or [])
            if isinstance(m, dict)
        ],
        "confidence_ledger": [
            {**c, "formula_id": fx.get("formula_id"), "subject": fx.get("subject") or fx.get("condition")}
            for fx in formula_executions
            for c in (fx.get("confidence") or fx.get("confidence_steps") or [])
            if isinstance(c, dict)
        ],
        "running_calculations": [
            {
                "formula_id": fx.get("formula_id"),
                "subject": fx.get("subject") or fx.get("condition"),
                "steps": fx.get("steps"),
                "outputs": fx.get("outputs"),
            }
            for fx in formula_executions
        ],
        "runtime_stage_flow": [
            {
                "stage": sec.get("stage") or name,
                "formula_id": sec.get("formula_id"),
                "input": sec.get("inputs") or {},
                "process": {
                    "dependencies": sec.get("dependencies") or [],
                    "notes": sec.get("notes") or [],
                    "repository_lookups": sec.get("csv_sources") or [],
                },
                "output": sec.get("outputs") or {},
                "elapsed_ms": sec.get("elapsed_ms"),
            }
            for name, sec in (trace.get("sections") or {}).items()
            if isinstance(sec, dict)
        ],
        "formula_graph": graph,
        "pipeline_dag": dag,
        "code_trace": CODE_TRACE,
        "csv_usage_map": CSV_USAGE_MAP,
        "engine_trace": trace,
        "overview": {
            "risk_count": len(risk_ledgers),
            "nutrition_targets": len(nutrition),
            "products": len(products.get("selected") or []),
            "rejected_products": len(products.get("rejected") or [])
            if isinstance(products.get("rejected"), list)
            else 0,
            "packages": len(packages.get("tiers") or []),
            "evidence": len(evidence),
            "formulas_registered": len(FORMULA_REGISTRY),
            "timings": timings or {},
            "stage_timings_ms": debug.get("stage_timings_ms") or {},
            "observability_coverage": obs_cov,
        },
        "observability_coverage": obs_cov,
        "profile_inspector": {
            "raw_request": raw_request,
            "normalized": profile,
            "defaults_applied": _nt("Default-application ledger not emitted by payload adapter."),
            "aliases_resolved": _nt("Alias resolution steps not logged per field."),
            "missing_values": [
                k for k, v in (profile.items() if isinstance(profile, dict) else []) if v in (None, "", [])
            ],
        },
        "risk_ledgers": risk_ledgers,
        "risk_modifier_ledgers": risk_ledgers,
        "explain_why": [
            {
                "condition": r.get("condition"),
                "final_probability_pct": r.get("final_probability_pct"),
                "confidence_percent": r.get("confidence_percent"),
                "steps": r.get("expanded_chain") or r.get("steps"),
                "formula": {"formula_id": r.get("locked_formula_id") or FORMULA_RISK},
                "audit_note": r.get("note"),
                "complete_modifier_chain": bool(r.get("complete")),
                "code": r.get("code"),
                "csv_refs": r.get("csv_refs") or r.get("csv_lookups"),
                "formula_execution": r.get("formula_execution"),
            }
            for r in risk_ledgers
        ],
        "ingredients": ingredients,
        "nutrition": nutrition,
        "nutrition_math": nutrition_math,
        "coverage": coverage,
        "confidence": confidence,
        "evidence": evidence,
        "products": products,
        "packages": packages,
        "package_optimizer": packages,
        "decisions": decisions,
        "reverse_lookup": reverse,
        "csv_lookups": csv_lookups,
        "repository_lookups": csv_lookups,
        "pipeline_timeline": timeline,
        "performance": performance,
        "missing_data": missing,
        "numerical_provenance": [
            {
                "formula_id": fx.get("formula_id"),
                "subject": fx.get("subject"),
                "rows": fx.get("numerical_provenance") or [],
            }
            for fx in formula_executions
        ],
        "replay": math_audit.get("replay") or [],
        "sensitivity": math_audit.get("sensitivity") or [],
        "publication_risk": [
            {
                "execution_id": fx.get("execution_id"),
                "formula_id": fx.get("formula_id"),
                "subject": fx.get("subject"),
                "classifications": fx.get("publication_risk") or [],
            }
            for fx in formula_executions
        ],
        "api_contract": api_contract_inspector(assessment),
        "raw_production_objects": raw_objs,
        "assessment_provenance": _assessment_provenance(assessment),
        "validation_checklist": _validation_checklist(
            analyze, assessment, trace.get("consistency_warnings") or []
        ),
        "gaps": _gaps(),
        "raw_analyze_keys": sorted(analyze.keys()) if isinstance(analyze, dict) else [],
        "analyze_debug": debug,
        "export": {"formats": ["json", "markdown"]},
        # Phase 4 — knowledge / evidence graphs (additive; from analyze.debug.science)
        "knowledge_graph": (debug.get("science") or {}).get("knowledge_graph")
        or (analyze.get("scientificExplainability") or {}).get("knowledge_graph")
        or {},
        "science": debug.get("science") or analyze.get("scientificExplainability") or {},
        "science_versions": debug.get("science_versions")
        or (debug.get("science") or {}).get("versions")
        or {},
        "recommendation_explanations": (debug.get("science") or {}).get("recommendation_explanations")
        or (analyze.get("scientificExplainability") or {}).get("recommendations")
        or [],
        "formula_explanations": (debug.get("science") or {}).get("formula_explanations")
        or (analyze.get("scientificExplainability") or {}).get("formulas")
        or [],
        "evidence_objects": (debug.get("science") or {}).get("evidence_objects") or [],
    }
    console["search_index"] = build_search_index(
        {
            "risk_ledgers": risk_ledgers,
            "evidence": evidence,
            "ingredients": ingredients,
            "csv_lookups": csv_lookups,
            "products": products,
            "nutrition": nutrition,
        }
    )
    # Deep search tokens from debug payload
    for t in debug.get("risk_traces") or []:
        if isinstance(t, dict) and t.get("condition"):
            console["search_index"].append(
                {"kind": "condition", "label": t["condition"], "nav": "risks"}
            )
    return console


def console_to_markdown(console: dict[str, Any]) -> str:
    lines = [
        "# Clinical Execution Explorer Export",
        "",
        f"Schema: `{console.get('schema')}`",
        f"Equation policy: `{console.get('equation_policy')}`",
        f"Observability coverage: `{console.get('observability_coverage')}`",
        "",
        "## Formula explorer",
        "",
    ]
    for f in console.get("formula_explorer") or console.get("formula_registry") or []:
        lines.append(
            f"- `{f.get('formula_id')}` — {f.get('purpose') or f.get('description')} "
            f"({f.get('code_file') or f.get('owner_module')})"
        )
    lines.append("")
    lines.append("## Risk ledgers")
    lines.append("")
    for ex in console.get("risk_ledgers") or []:
        lines.append(f"### {ex.get('condition')} — final {ex.get('final_probability_pct')}%")
        for step in ex.get("expanded_chain") or ex.get("steps") or []:
            if step.get("traceable"):
                lines.append(
                    f"- **{step.get('label') or step.get('name')}**: "
                    f"{step.get('value')}{step.get('unit') or ''} (`{step.get('op')}`)"
                )
            elif step.get("status") == "NOT_APPLIED_IN_RISK_V2_1":
                lines.append(f"- **{step.get('label') or step.get('name')}**: not applied in RISK_V2_1")
            else:
                lines.append(f"- **{step.get('label') or step.get('name')}**: {NOT_TRACEABLE}")
    lines.append("")
    lines.append("## Formula executions")
    lines.append("")
    for fx in console.get("formula_executions") or []:
        lines.append(f"### {fx.get('condition')} — `{fx.get('formula_id')}`")
        for s in fx.get("steps") or []:
            lines.append(
                f"- Step {s.get('step')} **{s.get('name')}**: "
                f"{s.get('before')} → {s.get('after') if s.get('after') is not None else s.get('result')}"
                f"{s.get('unit') or ''}"
            )
        for lu in (fx.get("lookups") or [])[:12]:
            lines.append(
                f"  - lookup `{lu.get('table')}` row `{lu.get('csv_row')}` pk={lu.get('primary_key')}"
            )
    lines.append("")
    lines.append("## Package rejects")
    lines.append("")
    for tier in (console.get("packages") or {}).get("tiers") or []:
        lines.append(f"### {tier.get('title')}")
        for r in tier.get("removed_products") or []:
            if isinstance(r, dict):
                lines.append(f"- REJECTED `{r.get('product_name')}` — {r.get('reason')}")
    return "\n".join(lines) + "\n"


# === from debug_boot.py ===

import os
import sys
import threading
import uuid
import webbrowser
from typing import Any


# Stable for process lifetime; changes on uvicorn --reload worker restart.
BOOT_ID = uuid.uuid4().hex[:10]


def is_reload_process() -> bool:
    """True when uvicorn was started with --reload (best-effort)."""
    joined = " ".join(sys.argv).lower()
    return "--reload" in joined


def is_local_dev_boot() -> bool:
    """True when developer tooling should print banner / soft-enable console page."""
    if is_engine_debug():
        return True
    if is_reload_process():
        return True
    raw = str(os.getenv("PPIE_DEV_BOOT", "")).strip().lower()
    return raw in ("1", "true", "yes", "on")


def should_open_browser() -> bool:
    raw = str(os.getenv("PPIE_OPEN_BROWSER", "true")).strip().lower()
    return raw in ("1", "true", "yes", "on")


def developer_banner(*, host: str = "127.0.0.1", port: int = 8000) -> str:
    base = f"http://{host}:{port}"
    return (
        "\n"
        "=========================================\n"
        "PPIE Developer Mode Enabled\n"
        "\n"
        f"Validation Console / Clinical Execution Explorer:\n"
        f"{base}/debug/calculation?debug=1\n"
        "\n"
        f"Engine Trace:\n"
        f"{base}/api/v1/ppie/trace?debug=1\n"
        "\n"
        f"Repository Browser:\n"
        f"{base}/api/v1/ppie/debug/repository?debug=1\n"
        "\n"
        f"Boot id: {BOOT_ID}\n"
        "=========================================\n"
    )


def print_developer_banner(*, host: str = "127.0.0.1", port: int = 8000) -> None:
    if not is_local_dev_boot():
        return
    print(developer_banner(host=host, port=port), flush=True)


def maybe_open_validation_console(*, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Open Validation Console once in a background thread (local/dev only)."""
    if not is_local_dev_boot() or not should_open_browser():
        return
    if str(os.getenv("PPIE_BROWSER_OPENED", "")).strip() == "1":
        return
    os.environ["PPIE_BROWSER_OPENED"] = "1"
    url = f"http://{host}:{port}/debug/calculation?debug=1"

    def _open() -> None:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass

    threading.Timer(1.2, _open).start()


def debug_status_payload(repo: Any) -> dict[str, Any]:
    return {
        "schema": "ppie_debug_status.v1",
        "boot_id": BOOT_ID,
        "debug_env": is_engine_debug(),
        "local_dev_boot": is_local_dev_boot(),
        "reload": is_reload_process(),
        "csv_hash": getattr(repo, "csv_hash", None),
        "data_version": getattr(repo, "version", None),
        "loaded_at": getattr(repo, "loaded_at", None),
        "console_url": "/debug/calculation?debug=1",
        "trace_url": "/api/v1/ppie/trace?debug=1",
    }


# Stable public aliases
build_clinical_execution_explorer = build_validation_console
