"""Clinical Report V3 — CSV-backed explanation layer (no PPIE math changes)."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.agent.utils import DataRepository


def _native(value: Any) -> Any:
    """Convert pandas/NumPy scalars to JSON-serializable Python builtins."""
    if value is None:
        return None
    # NumPy scalars (e.g. int64 from DataFrame._csv_row) → Python int/float/bool
    if hasattr(value, "item") and type(value).__module__ == "numpy":
        value = value.item()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _row_dict(row: pd.Series) -> dict[str, Any]:
    return {k: _native(v) for k, v in row.items()}


def _split_pipe(value: Any) -> list[str]:
    if not value or (isinstance(value, float) and pd.isna(value)):
        return []
    return [p.strip() for p in str(value).split("|") if p.strip()]


def _split_advantages(value: Any) -> list[str]:
    if not value:
        return []
    return [p.strip() for p in str(value).replace("|", ",").split(",") if p.strip()]


def _citation_from_evidence(row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {
            "status": "placeholder",
            "label": "Awaiting evidence entry",
            "source_name": None,
            "source_url": None,
            "year": None,
            "evidence_level": None,
        }
    url = row.get("source_url")
    if not url or str(url).strip() in ("", "nan"):
        return {
            "status": "placeholder",
            "label": "Awaiting evidence entry",
            "evidence_id": row.get("evidence_id"),
            "source_name": row.get("source_name"),
            "evidence_level": row.get("evidence_level"),
        }
    return {
        "status": "published",
        "evidence_id": row.get("evidence_id"),
        "title": row.get("source_name") or row.get("mechanism"),
        "source_name": row.get("source_name"),
        "source_url": url,
        "year": row.get("year"),
        "evidence_level": row.get("evidence_level"),
        "quote": row.get("source_quote"),
    }


class ClinicalReportBuilder:
    """Joins frozen PPIE analyze output with CSV explanation tables."""

    BREED_FIELDS = (
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

    def __init__(self, repo: DataRepository):
        self.repo = repo

    def build(self, analyze: dict[str, Any]) -> dict[str, Any]:
        profile = analyze.get("profile") or analyze.get("pet") or {}
        biology = analyze.get("biology") or {}
        sections = [
            self._section_biological_profile(biology),
            self._section_advantages(biology),
            self._section_challenges(analyze, biology, profile),
            self._section_environment(analyze, biology, profile),
            self._section_contribution_tree(biology),
            self._section_risk_timeline(biology, profile),
            self._section_scientific_evidence(analyze),
            self._section_nutrition_analysis(analyze),
            self._section_nutrient_ledger(analyze),
            self._section_activity(analyze, biology, profile),
            self._section_bundle_optimization(analyze),
            self._section_grooming(analyze),
            self._section_product_justification(analyze),
            self._section_traceability(analyze),
        ]
        return {
            "version": "3.0.0",
            "engine": analyze.get("engine"),
            "ppie_version": analyze.get("version"),
            "sections": sections,
        }

    def _lookup_trait_explanation(self, category: str, value: str) -> dict[str, Any] | None:
        df = self.repo.trait_attribute_explanations()
        if df.empty:
            return None
        hit = df[
            (df["trait_category"].astype(str).str.lower() == category.lower())
            & (df["trait_value"].astype(str).str.lower() == value.lower())
        ]
        return _row_dict(hit.iloc[0]) if not hit.empty else None

    def _evidence_by_id(self, evidence_id: str) -> dict[str, Any] | None:
        if not evidence_id:
            return None
        df = self.repo.clinical_evidence_base()
        if df.empty:
            return None
        hit = df[df["evidence_id"].astype(str) == str(evidence_id)]
        return _row_dict(hit.iloc[0]) if not hit.empty else None

    def _section_biological_profile(self, biology: dict[str, Any]) -> dict[str, Any]:
        cards = []
        seen: set[tuple[str, str]] = set()
        for desc in biology.get("descriptors") or []:
            breed = desc.get("breed")
            for field, col in self.BREED_FIELDS:
                val = desc.get(field) or desc.get(col)
                if not val:
                    continue
                key = (field, str(val))
                if key in seen:
                    continue
                seen.add(key)
                expl = self._lookup_trait_explanation(field, str(val))
                ev_id = (expl or {}).get("evidence_id")
                cards.append({
                    "title": (expl or {}).get("card_title") or str(val),
                    "breed": breed,
                    "derived_from": {
                        "source_csv": (expl or {}).get("source_csv") or "BREEDS.csv",
                        "field": field,
                        "value": str(val),
                    },
                    "explanation": (expl or {}).get("explanation") or f"Attribute {field}={val} from BREEDS.csv.",
                    "evidence_level": (expl or {}).get("evidence_level") or "derived",
                    "related_conditions": _split_pipe((expl or {}).get("related_conditions")),
                    "citation": _citation_from_evidence(self._evidence_by_id(str(ev_id)) if ev_id else None),
                })
        return {"id": "s1", "title": "Breed Biological Profile", "cards": cards}

    def _section_advantages(self, biology: dict[str, Any]) -> dict[str, Any]:
        df = self.repo.trait_purposes()
        items = []
        for trait in biology.get("trait_summary") or []:
            if df.empty:
                continue
            hits = df[df["trait_value"].astype(str).str.lower() == str(trait).lower()]
            for _, row in hits.iterrows():
                r = _row_dict(row)
                items.append({
                    "trait": str(trait),
                    "source_trait": r.get("trait_value"),
                    "category": r.get("trait_category"),
                    "purpose": r.get("biological_purpose"),
                    "advantages": _split_advantages(r.get("advantage_summary")),
                    "citation": _citation_from_evidence({
                        "source_name": r.get("source_name"),
                        "source_url": r.get("source_url"),
                        "source_quote": r.get("source_quote"),
                        "evidence_level": "medium",
                    }),
                    "source_csv": "TRAIT_PURPOSES.csv",
                })
        return {"id": "s2", "title": "Breed Advantage Analysis", "items": items}

    def _section_challenges(
        self, analyze: dict[str, Any], biology: dict[str, Any], profile: dict[str, Any]
    ) -> dict[str, Any]:
        chains = []
        breeds = profile.get("breeds") or biology.get("breeds") or []
        bc = self.repo.breed_conditions()
        if not bc.empty and breeds:
            for breed in breeds:
                hits = bc[bc["breed"].astype(str).str.lower() == str(breed).lower()]
                for _, row in hits.iterrows():
                    r = _row_dict(row)
                    prev = float(r.get("prevalence") or 0)
                    if prev > 1:
                        prev /= 100
                    chains.append({
                        "trait": str(breed),
                        "disadvantage": f"Elevated {r.get('condition')} prevalence",
                        "condition": r.get("condition"),
                        "prevalence_pct": round(prev * 100, 1),
                        "source_csv": "BREED_CONDITIONS.csv",
                        "citation": _citation_from_evidence({
                            "source_name": r.get("source_name"),
                            "source_url": r.get("source_url"),
                            "source_quote": r.get("source_quote"),
                            "year": r.get("year"),
                            "evidence_level": r.get("confidence_level"),
                        }),
                    })
        ti = self.repo.trait_interactions()
        if not ti.empty:
            traits = set(biology.get("trait_summary") or [])
            for _, row in ti.iterrows():
                ta = str(row.get("trait_a", ""))
                if ta in traits or ta.replace(" ", "") in {t.replace(" ", "") for t in traits}:
                    chains.append({
                        "trait": ta,
                        "disadvantage": str(row.get("reason") or row.get("interaction")),
                        "condition": row.get("condition"),
                        "factor": row.get("factor"),
                        "source_csv": "TRAIT_INTERACTIONS.csv",
                        "citation": _citation_from_evidence({
                            "source_name": row.get("source"),
                            "evidence_level": "medium",
                        }),
                    })
        for insight in (analyze.get("healthInsights") or analyze.get("risks") or [])[:6]:
            chains.append({
                "trait": ", ".join(insight.get("supporting_traits") or []),
                "disadvantage": insight.get("title"),
                "condition": insight.get("goal_id"),
                "prevalence_pct": insight.get("biological_risk_percent"),
                "source_csv": "PPIE healthInsights (deterministic)",
                "citation": _citation_from_evidence({
                    "source_name": (insight.get("evidence_sources") or [{}])[0].get("source_name")
                    if insight.get("evidence_sources")
                    else None,
                    "source_url": (insight.get("evidence_sources") or [{}])[0].get("source_url")
                    if insight.get("evidence_sources")
                    else None,
                    "evidence_level": "computed",
                }),
            })
        return {"id": "s3", "title": "Breed Challenges", "chains": chains}

    def _section_environment(
        self, analyze: dict[str, Any], biology: dict[str, Any], profile: dict[str, Any]
    ) -> dict[str, Any]:
        env = profile.get("current_environment") or "Shanghai Summer"
        df = self.repo.environmental_matrices()
        findings = []
        if not df.empty:
            ctx = df[df["climate_context"].astype(str).str.lower() == str(env).lower()]
            traits = biology.get("trait_summary") or []
            for _, row in ctx.iterrows():
                tv = str(row.get("trait_value", ""))
                if tv not in traits and tv.lower() not in {t.lower() for t in traits}:
                    continue
                r = _row_dict(row)
                findings.append({
                    "dimension": r.get("dimension") or r.get("management_note"),
                    "trait": tv,
                    "compatibility_score": r.get("compatibility_score"),
                    "derived_from": {
                        "source_csv": "ENVIRONMENTAL_MATRICES.csv",
                        "climate_context": env,
                        "trait_category": r.get("trait_category"),
                        "trait_value": tv,
                    },
                    "citation": _citation_from_evidence({
                        "source_name": r.get("source_name"),
                        "source_url": r.get("source_url"),
                        "source_quote": r.get("source_quote"),
                        "evidence_level": "medium",
                    }),
                })
        return {
            "id": "s4",
            "title": "Environmental Analysis",
            "environment": env,
            "findings": findings,
        }

    def _section_contribution_tree(self, biology: dict[str, Any]) -> dict[str, Any]:
        df = self.repo.trait_contribution_weights()
        nodes = []
        traits = set(biology.get("trait_summary") or [])
        if not df.empty:
            for _, row in df.iterrows():
                tv = str(row.get("trait_value", ""))
                if tv not in traits and tv.lower() not in {t.lower() for t in traits}:
                    continue
                r = _row_dict(row)
                delta = float(r.get("risk_delta") or 0)
                sign = "+" if delta >= 0 else ""
                nodes.append({
                    "trait": tv,
                    "condition": r.get("condition"),
                    "delta_display": f"{sign}{delta} {r.get('unit', 'percent')}",
                    "risk_delta": delta,
                    "mechanism": r.get("mechanism_note"),
                    "derived_from": {
                        "source_csv": str(r.get("source_csv") or "TRAIT_CONTRIBUTION_WEIGHTS.csv"),
                        "trait_category": r.get("trait_category"),
                        "trait_value": tv,
                    },
                    "citation": _citation_from_evidence(self._evidence_by_id(str(r.get("evidence_id") or ""))),
                })
        return {"id": "s5", "title": "Trait Contribution Tree", "nodes": nodes}

    def _section_risk_timeline(self, biology: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
        df = self.repo.clinical_risk_timeline()
        age_stage = profile.get("age_stage") or biology.get("age_stage") or "Adult"
        stages = ["Puppy", "Adult", "Senior"]
        timeline = []
        traits = set(biology.get("trait_summary") or [])
        breeds = set(profile.get("breeds") or biology.get("breeds") or [])
        if not df.empty:
            for stage in stages:
                stage_rows = df[df["age_stage"].astype(str).str.lower() == stage.lower()]
                entries = []
                for _, row in stage_rows.iterrows():
                    ref = str(row.get("trait_or_breed", ""))
                    if ref not in traits and ref not in breeds:
                        continue
                    r = _row_dict(row)
                    entries.append({
                        "reference": ref,
                        "condition": r.get("condition"),
                        "risk_level": r.get("risk_level"),
                        "monitoring": r.get("monitoring"),
                        "prevention": _split_pipe(r.get("prevention")),
                        "source_csv": "CLINICAL_RISK_TIMELINE.csv",
                        "citation": _citation_from_evidence(self._evidence_by_id(str(r.get("evidence_id") or ""))),
                    })
                timeline.append({"age_stage": stage, "current": stage.lower() == str(age_stage).lower(), "entries": entries})
        return {"id": "s6", "title": "Clinical Risk Timeline", "timeline": timeline}

    def _section_scientific_evidence(self, analyze: dict[str, Any]) -> dict[str, Any]:
        items = []
        df = self.repo.clinical_evidence_base()
        if not df.empty:
            for _, row in df.iterrows():
                r = _row_dict(row)
                items.append({
                    "domain": r.get("domain"),
                    "condition": r.get("condition"),
                    "mechanism": r.get("mechanism"),
                    "nutrient_or_activity": r.get("nutrient_or_activity"),
                    "citation": _citation_from_evidence(r),
                    "source_csv": "CLINICAL_EVIDENCE_BASE.csv",
                })
        for ev in analyze.get("scientificEvidence") or analyze.get("evidence") or []:
            items.append({
                "domain": "ppie_computed",
                "condition": ev.get("condition"),
                "mechanism": ev.get("quote") or ev.get("mechanism"),
                "citation": _citation_from_evidence(ev),
                "source_csv": "PPIE deterministic evidence collector",
            })
        return {"id": "s7", "title": "Scientific Evidence", "items": items}

    def _section_nutrition_analysis(self, analyze: dict[str, Any]) -> dict[str, Any]:
        targets = []
        optimal = next(
            (p for p in (analyze.get("wellnessPackages") or []) if p.get("tier") == "optimal"),
            (analyze.get("wellnessPackages") or [{}])[0] if analyze.get("wellnessPackages") else None,
        )
        intake_map = {}
        if optimal:
            for row in optimal.get("full_nutrition_report") or optimal.get("daily_nutrition_intake") or []:
                key = row.get("nutrient_key") or row.get("nutrient")
                intake_map[str(key).lower()] = row
        for t in analyze.get("nutritionalTargets") or []:
            key = str(t.get("ingredient_key") or t.get("ingredient") or "").lower()
            intake = intake_map.get(key, {})
            target_val = float(intake.get("target") or intake.get("target_daily") or _parse_dose(t.get("daily_target")) or 0)
            provided = float(intake.get("provided") or 0)
            coverage = float(intake.get("coverage_percent") or (100 if target_val and provided >= target_val else 0))
            surplus = max(0, provided - target_val) if target_val else 0
            deficit = max(0, target_val - provided) if target_val else 0
            sources = intake.get("sources") or []
            food_amt = sum(s.get("amount", 0) for s in sources if "treat" not in str(s.get("product_name", "")).lower())
            supp_amt = provided - food_amt if provided else 0
            targets.append({
                "nutrient": t.get("ingredient") or t.get("ingredient_key"),
                "target_display": t.get("daily_target"),
                "target_value": target_val,
                "unit": intake.get("unit") or "mg",
                "reason": (t.get("supports_goals") or t.get("for_conditions") or ["Core wellness"])[0]
                if isinstance(t.get("supports_goals") or t.get("for_conditions"), list)
                else t.get("supports_goals"),
                "food_provides": food_amt,
                "supplement_provides": max(0, supp_amt),
                "final_intake": provided,
                "coverage_pct": coverage,
                "surplus": surplus,
                "deficit": deficit,
                "source_csv": "NUTRIENT_PRIORITIES.csv|CONDITION_PROTOCOLS.csv|PPIE nutrition stage",
                "citation": _citation_from_evidence({
                    "source_name": t.get("source_name"),
                    "source_url": t.get("source_url"),
                    "source_quote": t.get("evidence_quote"),
                }),
            })
        return {"id": "s8", "title": "Nutrition Analysis", "targets": targets}

    def _section_nutrient_ledger(self, analyze: dict[str, Any]) -> dict[str, Any]:
        pkg = next(
            (p for p in (analyze.get("wellnessPackages") or []) if p.get("recommended")),
            (analyze.get("wellnessPackages") or [{}])[-1] if analyze.get("wellnessPackages") else None,
        )
        rows = []
        if pkg:
            for row in pkg.get("full_nutrition_report") or pkg.get("daily_nutrition_intake") or []:
                target = float(row.get("target") or row.get("target_daily") or 0)
                provided = float(row.get("provided") or 0)
                coverage = float(row.get("coverage_percent") or 0)
                rows.append({
                    "nutrient": row.get("nutrient"),
                    "required": target,
                    "food": sum(
                        s.get("amount", 0)
                        for s in (row.get("sources") or [])
                        if "supplement" not in str(s.get("product_name", "")).lower()
                    ),
                    "treats": 0,
                    "supplements": sum(
                        s.get("amount", 0)
                        for s in (row.get("sources") or [])
                        if "supplement" in str(s.get("product_name", "")).lower()
                    ),
                    "total": provided,
                    "coverage_pct": coverage,
                    "surplus_pct": max(0, coverage - 100),
                    "deficit_pct": max(0, 100 - coverage),
                    "unit": row.get("unit"),
                    "source_csv": "PRODUCT_COMPONENTS.csv|PPIE package_detail",
                })
        return {"id": "s9", "title": "Nutrient Accounting", "ledger": rows}

    def _section_activity(
        self, analyze: dict[str, Any], biology: dict[str, Any], profile: dict[str, Any]
    ) -> dict[str, Any]:
        desc = (biology.get("descriptors") or [{}])[0]
        energy = desc.get("energy") or "High"
        size = desc.get("size") or "Large"
        body = desc.get("body_type") or "Athletic"
        age = profile.get("age_stage") or biology.get("age_stage") or "Adult"
        df = self.repo.activity_prescription_rules()
        prescription = None
        if not df.empty:
            hit = df[
                (df["energy"].astype(str).str.lower() == str(energy).lower())
                & (df["size"].astype(str).str.lower() == str(size).lower())
                & (df["body_type"].astype(str).str.lower() == str(body).lower())
                & (df["age_stage"].astype(str).str.lower() == str(age).lower())
            ]
            if not hit.empty:
                prescription = _row_dict(hit.iloc[0])
        act = analyze.get("activityRecommendations") or {}
        return {
            "id": "s10",
            "title": "Activity Prescription",
            "derived_from": {
                "energy": energy,
                "size": size,
                "body_type": body,
                "age_stage": age,
                "source_csv": "ACTIVITY_PRESCRIPTION_RULES.csv",
            },
            "prescription": prescription,
            "ppie_summary": act,
            "citation": _citation_from_evidence(
                {"source_name": (prescription or {}).get("source_name"), "source_url": (prescription or {}).get("source_url")}
                if prescription
                else None
            ),
        }

    def _section_bundle_optimization(self, analyze: dict[str, Any]) -> dict[str, Any]:
        reports = []
        tier_notes = {
            "essential": "Minimum cost — 100% required nutrition only.",
            "balanced": "Fill every nutrient — minimize unnecessary surplus.",
            "optimal": "Optimize nutrition, activity, skin, joint, coat, behavior, recovery without cost constraint.",
        }
        for pkg in analyze.get("wellnessPackages") or []:
            tier = pkg.get("tier")
            coverage_rows = pkg.get("nutrition_coverage") or pkg.get("daily_nutrition_intake") or []
            deficiencies = [
                f"{r.get('nutrient')}: {r.get('status')}"
                for r in coverage_rows
                if str(r.get("status", "")).lower().startswith("below")
            ]
            reports.append({
                "tier": tier,
                "title": pkg.get("title"),
                "objective": tier_notes.get(str(tier), pkg.get("tagline")),
                "coverage_pct": pkg.get("coverage_score"),
                "monthly_cost": pkg.get("monthly_cost"),
                "yearly_cost": pkg.get("yearly_cost"),
                "remaining_deficiencies": deficiencies,
                "products": [
                    {"product_id": p.get("product_id"), "name": p.get("name"), "category": p.get("category")}
                    for p in (pkg.get("products_included") or [])
                ],
                "source_csv": "PACKAGE_TIERS.csv|PPIE optimization stage",
            })
        return {"id": "s11", "title": "Bundle Optimization", "packages": reports}

    def _section_grooming(self, analyze: dict[str, Any]) -> dict[str, Any]:
        defs_df = self.repo.grooming_observation_defs()
        observations = []
        groomer = analyze.get("groomer") or {}
        for _, row in defs_df.iterrows() if not defs_df.empty else []:
            r = _row_dict(row)
            key = str(r.get("observation_key", ""))
            status = groomer.get(key) if isinstance(groomer, dict) else None
            observations.append({
                "key": key,
                "label": r.get("label"),
                "status": status or "normal",
                "normal": r.get("normal_criteria"),
                "monitor": r.get("monitor_criteria"),
                "attention": r.get("attention_criteria"),
                "recommendation": r.get("recommendation_template"),
                "source_csv": r.get("source_csv") or "GROOMING_OBSERVATION_DEFS.csv",
            })
        return {"id": "s12", "title": "Grooming Intelligence", "observations": observations}

    def _section_product_justification(self, analyze: dict[str, Any]) -> dict[str, Any]:
        items = []
        for rec in analyze.get("productRecommendations") or analyze.get("products") or []:
            pid = rec.get("product_id")
            analysis = (analyze.get("productAnalyses") or {}).get(pid) or {}
            items.append({
                "product_id": pid,
                "name": rec.get("product_name") or rec.get("name"),
                "why_selected": rec.get("why_selected") or analysis.get("summary"),
                "supports": rec.get("supports_goals") or rec.get("for_conditions") or [],
                "contribution": analysis.get("coverage_summary"),
                "evidence": _citation_from_evidence({
                    "source_name": rec.get("source_name"),
                    "source_url": rec.get("source_url"),
                    "evidence_level": rec.get("evidence_level"),
                }),
                "source_csv": "PRODUCT_CATALOG.csv|PPIE product selection",
            })
        return {"id": "s13", "title": "Product Justification", "items": items}

    def _section_traceability(self, analyze: dict[str, Any]) -> dict[str, Any]:
        traces = []
        for block in analyze.get("calculationTrace") or []:
            traces.append({
                "condition": block.get("condition"),
                "goal": block.get("goal"),
                "prevalence": block.get("prevalence"),
                "trait_contributions": block.get("trait_contributions") or [],
                "nutrient_targets": block.get("nutrient_targets") or [],
                "source": "calculationTrace (PPIE deterministic)",
            })
        for t in analyze.get("nutritionalTargets") or []:
            traces.append({
                "type": "nutrient",
                "nutrient": t.get("ingredient"),
                "target": t.get("daily_target"),
                "derived_from": "nutritionalTargets ← CONDITION_PROTOCOLS.csv",
                "expandable": True,
            })
        return {"id": "s14", "title": "Traceability", "traces": traces}


def _parse_dose(raw: Any) -> float:
    import re

    m = re.search(r"[-+]?[0-9]*\.?[0-9]+", str(raw or ""))
    return float(m.group(0)) if m else 0.0


def build_clinical_report(repo: DataRepository, analyze: dict[str, Any]) -> dict[str, Any]:
    return ClinicalReportBuilder(repo).build(analyze)
