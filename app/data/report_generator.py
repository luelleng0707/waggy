"""
Standardized Clinical Report Generator.

CSV → Repository → PPIE analyze (frozen) → ReportGenerator → Standard JSON

No HTML. No frontend business logic. No fabricated citations.
Does not change PPIE calculation math — only assembles structured widgets.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.agent.utils import DataRepository
from app.data.report_schema import (
    make_reference,
    make_report_envelope,
    make_section,
    make_widget,
    empty_reference,
    AWAITING_PUBLICATION,
    AWAITING_DATABASE,
)


def _row_dict(row: pd.Series) -> dict[str, Any]:
    return {k: (None if pd.isna(v) else v) for k, v in row.items()}


def _split(value: Any, seps: str = "|,") -> list[str]:
    if not value or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value)
    for s in seps[1:]:
        text = text.replace(s, seps[0])
    return [p.strip() for p in text.split(seps[0]) if p.strip()]


def _pct(n: Any) -> float | None:
    try:
        v = float(n)
    except (TypeError, ValueError):
        return None
    if v <= 1 and v > 0:
        return round(v * 100, 1)
    return round(v, 1)


def _cite(row: dict[str, Any] | None, csv_source: str | None = None) -> dict[str, Any]:
    if not row:
        return make_reference(csv_source=csv_source)
    return make_reference(
        source_name=row.get("source_name") or row.get("title"),
        source_url=row.get("source_url"),
        year=row.get("year"),
        evidence_level=row.get("evidence_level") or row.get("confidence_level"),
        quote=row.get("source_quote") or row.get("quote"),
        csv_source=csv_source or row.get("source_csv"),
    )


class ReportGenerator:
    """Assembles a schema-v4 clinical report from frozen PPIE analyze output + CSV."""

    BREED_FIELDS = (
        ("size", "Size"),
        ("body_type", "Body Type"),
        ("coat_type", "Coat"),
        ("energy", "Energy"),
        ("weakness_group", "Weakness Group"),
        ("skull_type", "Skull"),
        ("climate", "Climate Origin"),
        ("lifespan", "Lifespan"),
        ("function_group", "Function Group"),
    )

    def __init__(self, repo: DataRepository):
        self.repo = repo

    def _data_version(self) -> str:
        return str(getattr(self.repo, "version", None) or "unknown")

    def _csv_hash(self) -> str:
        return str(getattr(self.repo, "csv_hash", None) or "")

    def build(self, analyze: dict[str, Any]) -> dict[str, Any]:
        profile = analyze.get("profile") or analyze.get("pet") or {}
        biology = analyze.get("biology") or {}

        sections = [
            self._summary(analyze, biology, profile),
            self._breed_analysis(biology, profile),
            self._trait_analysis(biology),
            self._environment(analyze, biology, profile),
            self._risk_analysis(analyze, biology, profile),
            self._nutrition(analyze),
            self._activity(analyze, biology, profile),
            self._packages(analyze),
            self._grooming(analyze),
            # Evidence is embedded in breed/risk/nutrition/package/product sections — no standalone page.
        ]

        package_reports = self._package_detail_reports(analyze)
        product_reports = self._product_detail_reports(analyze)

        return make_report_envelope(
            sections=sections,
            data_version=self._data_version(),
            csv_hash=self._csv_hash(),
            ppie_version=analyze.get("version") or analyze.get("engine"),
            package_reports=package_reports,
            product_reports=product_reports,
        )

    # ── helpers ──────────────────────────────────────────

    def _evidence_by_id(self, evidence_id: str) -> dict[str, Any] | None:
        if not evidence_id:
            return None
        df = self.repo.clinical_evidence_base()
        if df.empty:
            return None
        hit = df[df["evidence_id"].astype(str) == str(evidence_id)]
        return _row_dict(hit.iloc[0]) if not hit.empty else None

    def _trait_explanation(self, category: str, value: str) -> dict[str, Any] | None:
        df = self.repo.trait_attribute_explanations()
        if df.empty:
            return None
        hit = df[
            (df["trait_category"].astype(str).str.lower() == category.lower())
            & (df["trait_value"].astype(str).str.lower() == value.lower())
        ]
        return _row_dict(hit.iloc[0]) if not hit.empty else None

    def _purposes_for(self, trait_value: str) -> list[dict[str, Any]]:
        df = self.repo.trait_purposes()
        if df.empty:
            return []
        hits = df[df["trait_value"].astype(str).str.lower() == str(trait_value).lower()]
        return [_row_dict(r) for _, r in hits.iterrows()]

    # ── sections ─────────────────────────────────────────

    def _summary(self, analyze: dict, biology: dict, profile: dict) -> dict[str, Any]:
        name = profile.get("pet_name") or profile.get("name") or "Pet"
        breeds = profile.get("breeds") or biology.get("breeds") or []
        pkgs = analyze.get("wellnessPackages") or []
        scores = [_pct(p.get("coverage_score")) for p in pkgs]
        scores = [s for s in scores if s is not None]
        avg = round(sum(scores) / len(scores)) if scores else None
        traits = biology.get("trait_summary") or []
        insights = analyze.get("healthInsights") or []
        concerns = [i.get("title") for i in insights[:4] if i.get("title")]

        widgets = [
            make_widget(
                "metrics",
                items=[
                    {"label": "Weight", "value": f"{profile.get('weight_kg') or profile.get('weight') or '—'} kg"},
                    {"label": "Age", "value": f"{profile.get('age_years') or '—'} yrs"},
                    {"label": "Activity", "value": profile.get("activity_level") or "—"},
                    {"label": "Environment", "value": profile.get("current_environment") or "—"},
                ],
            ),
            make_widget(
                "text",
                title="Overview",
                body=(
                    f"{name} is a {' × '.join(breeds) if breeds else 'canine'} profile. "
                    f"Inherited traits include {', '.join(str(t) for t in traits[:5]) or 'pending'}. "
                    f"Overall pathway coverage across care packages averages "
                    f"{avg if avg is not None else '—'}% of priority nutrient targets."
                ),
            ),
            make_widget(
                "chips",
                title="Primary concerns",
                items=[{"label": c, "tone": "warn"} for c in concerns]
                or [{"label": "No priority risks flagged", "tone": "good"}],
            ),
            make_widget(
                "list",
                title="Report provenance",
                items=[
                    f"Algorithm · {analyze.get('engine') or 'PPIE'}",
                    f"Data version · {self._data_version()}",
                    f"CSV hash · {self._csv_hash()[:12] or '—'}",
                ],
            ),
        ]
        return make_section(
            section_id="summary",
            title="Summary",
            priority=10,
            summary=f"Clinical wellness summary for {name}.",
            score={"value": avg, "label": "Pathway coverage", "unit": "%"} if avg is not None else None,
            widgets=widgets,
        )

    def _breed_analysis(self, biology: dict, profile: dict) -> dict[str, Any]:
        widgets = []
        seen: set[tuple[str, str]] = set()
        env = str(profile.get("current_environment") or "")
        env_df = self.repo.environmental_matrices()
        for desc in biology.get("descriptors") or []:
            breed = desc.get("breed")
            for field, label in self.BREED_FIELDS:
                val = desc.get(field)
                if not val:
                    continue
                key = (field, str(val))
                if key in seen:
                    continue
                seen.add(key)
                expl = self._trait_explanation(field, str(val))
                purposes = self._purposes_for(str(val))
                advantages = []
                problems = []
                for p in purposes:
                    advantages.extend(_split(p.get("advantage_summary")))
                    problems.extend(_split(p.get("risk_summary") or p.get("disadvantage_summary")))
                problems.extend(_split((expl or {}).get("related_conditions")))
                ev = self._evidence_by_id(str((expl or {}).get("evidence_id") or ""))
                shanghai = []
                if not env_df.empty and env:
                    hits = env_df[
                        (env_df["climate_context"].astype(str).str.lower() == env.lower())
                        & (env_df["trait_value"].astype(str).str.lower() == str(val).lower())
                    ]
                    for _, row in hits.iterrows():
                        note = row.get("management_note")
                        if note and str(note) not in ("nan", ""):
                            shanghai.append(str(note))
                refs = [_cite(ev, (expl or {}).get("source_csv") or "BREEDS.csv")]
                if not env_df.empty and shanghai:
                    for _, row in env_df[
                        (env_df["climate_context"].astype(str).str.lower() == env.lower())
                        & (env_df["trait_value"].astype(str).str.lower() == str(val).lower())
                    ].head(1).iterrows():
                        refs.append(_cite(_row_dict(row), "ENVIRONMENTAL_MATRICES.csv"))
                widgets.append(
                    make_widget(
                        "trait",
                        id=f"trait-{field}-{val}",
                        title=(expl or {}).get("card_title") or f"{label}: {val}",
                        category=label,
                        value=str(val),
                        breed=breed,
                        summary=(expl or {}).get("explanation")
                        or f"Attribute {field}={val} derived from BREEDS.csv.",
                        benefits=[{"title": a} for a in advantages] or [{"title": AWAITING_DATABASE}],
                        risks=[{"title": p} for p in dict.fromkeys(problems)] or None,
                        shanghai_context=shanghai or ([f"{env}: {AWAITING_DATABASE}"] if env else None),
                        management=shanghai[:2] or _split((expl or {}).get("management_advice")),
                        related_conditions=_split((expl or {}).get("related_conditions")),
                        evidence_level=(expl or {}).get("evidence_level") or "derived",
                        references=refs,
                        csv_sources=["BREEDS.csv", "TRAIT_ATTRIBUTE_EXPLANATIONS.csv", "TRAIT_PURPOSES.csv"],
                        trace=[
                            {"label": "Source CSV", "value": "BREEDS.csv"},
                            {"label": "Field", "value": field},
                            {"label": "Value", "value": str(val)},
                            {"label": "Breed", "value": breed},
                            {"label": "Environment", "value": env or AWAITING_DATABASE},
                        ],
                    )
                )
        # Mixed breed composition card
        breeds = biology.get("breeds") or profile.get("breeds") or []
        if len(breeds) >= 2 or biology.get("descriptors"):
            descs = biology.get("descriptors") or []
            items = []
            for d in descs:
                pct = d.get("split_pct") or d.get("weight") or d.get("contribution")
                items.append(
                    {
                        "label": f"{d.get('breed')} · {pct if pct is not None else '—'}%",
                        "mark": "◇",
                    }
                )
            if items:
                widgets.append(
                    make_widget(
                        "accordion",
                        title="Mixed Breed Composition",
                        subtitle="Genetics",
                        body="Breed contribution weights from the biological stage (BREEDS.csv + aliases).",
                        items=items,
                        references=[empty_reference()],
                        csv_sources=["BREEDS.csv", "BREED_ALIASES.csv"],
                        trace=[{"label": "CSV", "value": "BREEDS.csv|BREED_ALIASES.csv"}],
                    )
                )
        if not widgets:
            widgets.append(make_widget("warning", title="Breed Analysis", body=AWAITING_DATABASE))
        return make_section(
            section_id="breed_analysis",
            title="Breed Analysis",
            priority=20,
            summary="Inherited biological attributes from BREEDS.csv with environment context.",
            widgets=widgets,
        )

    def _trait_analysis(self, biology: dict) -> dict[str, Any]:
        widgets = []
        df = self.repo.trait_purposes()
        for trait in biology.get("trait_summary") or []:
            if df.empty:
                continue
            hits = df[df["trait_value"].astype(str).str.lower() == str(trait).lower()]
            for _, row in hits.iterrows():
                r = _row_dict(row)
                widgets.append(
                    make_widget(
                        "accordion",
                        title=str(trait),
                        subtitle=r.get("trait_category"),
                        body=r.get("biological_purpose") or "",
                        items=[{"label": a, "mark": "✓"} for a in _split(r.get("advantage_summary"))],
                        references=[_cite(r, "TRAIT_PURPOSES.csv")],
                        trace=[
                            {"label": "CSV", "value": "TRAIT_PURPOSES.csv"},
                            {"label": "Trait", "value": str(trait)},
                        ],
                    )
                )
        weights = self.repo.trait_contribution_weights()
        if not weights.empty:
            traits = set(biology.get("trait_summary") or [])
            for _, row in weights.iterrows():
                tv = str(row.get("trait_value", ""))
                if tv not in traits and tv.lower() not in {t.lower() for t in traits}:
                    continue
                r = _row_dict(row)
                delta = float(r.get("risk_delta") or 0)
                widgets.append(
                    make_widget(
                        "progress",
                        title=f"{tv} → {r.get('condition')}",
                        value=abs(delta),
                        max=100,
                        display=f"{'+' if delta >= 0 else ''}{delta}%",
                        caption=r.get("mechanism_note"),
                        references=[_cite(self._evidence_by_id(str(r.get("evidence_id") or "")), "TRAIT_CONTRIBUTION_WEIGHTS.csv")],
                        trace=[
                            {"label": "CSV", "value": "TRAIT_CONTRIBUTION_WEIGHTS.csv"},
                            {"label": "Trait", "value": tv},
                            {"label": "Delta", "value": delta},
                        ],
                    )
                )
        return make_section(
            section_id="trait_analysis",
            title="Trait Analysis",
            priority=30,
            summary="Evolutionary purposes and contribution weights.",
            widgets=widgets,
        )

    def _environment(self, analyze: dict, biology: dict, profile: dict) -> dict[str, Any]:
        env = profile.get("current_environment") or "Current environment"
        df = self.repo.environmental_matrices()
        widgets = [
            make_widget("text", title=str(env), body="Climate compatibility with inherited biology from ENVIRONMENTAL_MATRICES.csv.")
        ]
        findings = []
        if not df.empty:
            ctx = df[df["climate_context"].astype(str).str.lower() == str(env).lower()]
            traits = biology.get("trait_summary") or []
            for _, row in ctx.iterrows():
                tv = str(row.get("trait_value", ""))
                if tv not in traits and tv.lower() not in {t.lower() for t in traits}:
                    continue
                r = _row_dict(row)
                score = _pct(r.get("compatibility_score")) or 0
                findings.append(score)
                widgets.append(
                    make_widget(
                        "progress",
                        title=f"{tv} · {r.get('dimension')}",
                        value=score,
                        max=100,
                        display=f"{int(score)}%",
                        caption=r.get("management_note") or r.get("source_quote"),
                        references=[_cite(r, "ENVIRONMENTAL_MATRICES.csv")],
                        trace=[
                            {"label": "CSV", "value": "ENVIRONMENTAL_MATRICES.csv"},
                            {"label": "Climate", "value": env},
                            {"label": "Trait", "value": tv},
                            {"label": "Dimension", "value": r.get("dimension")},
                        ],
                    )
                )
        avg = round(sum(findings) / len(findings)) if findings else None
        return make_section(
            section_id="environment_analysis",
            title="Environment Analysis",
            priority=40,
            summary=f"Environmental compatibility for {env}.",
            score={"value": avg, "label": "Compatibility", "unit": "%"} if avg is not None else None,
            widgets=widgets,
        )

    def _risk_analysis(self, analyze: dict, biology: dict, profile: dict) -> dict[str, Any]:
        widgets = []
        env = profile.get("current_environment") or biology.get("current_environment")
        targets = analyze.get("nutritionalTargets") or []
        rec_pkg = next(
            (p for p in (analyze.get("wellnessPackages") or []) if p.get("recommended")),
            (analyze.get("wellnessPackages") or [None])[0] if analyze.get("wellnessPackages") else None,
        )
        pkg_products = (rec_pkg or {}).get("products_included") or []
        activity = analyze.get("activityRecommendations") or analyze.get("activity_recommendations") or {}
        timeline = self.repo.clinical_risk_timeline()

        for insight in analyze.get("healthInsights") or []:
            title = insight.get("title") or insight.get("goal_id")
            conditions = [c for c in (insight.get("supporting_conditions") or []) if c]
            # Prevention / monitoring from CLINICAL_RISK_TIMELINE.csv
            prevention: list[str] = []
            warnings: list[str] = []
            if not timeline.empty and conditions:
                for cond in conditions:
                    hits = timeline[
                        timeline["condition"].astype(str).str.lower() == str(cond).lower()
                    ]
                    for _, row in hits.head(3).iterrows():
                        prevention.extend(_split(row.get("prevention")))
                        mon = row.get("monitoring")
                        if mon and str(mon) not in ("nan", ""):
                            warnings.append(str(mon))
            nutrients = [
                t.get("ingredient") or t.get("ingredient_key")
                for t in targets
                if title
                and any(str(title).lower() in str(g).lower() for g in (t.get("supports_goals") or []))
            ]
            products = [
                p.get("name") or p.get("product_name")
                for p in pkg_products
                if p.get("why_selected") or p.get("functions") or True
            ][:4]
            # Prefer products whose why/function mentions the goal
            scored_products = []
            for p in pkg_products:
                blob = " ".join(
                    [
                        str(p.get("why_selected") or ""),
                        " ".join(str(f.get("function") or "") for f in (p.get("functions") or [])),
                        str(p.get("name") or ""),
                    ]
                ).lower()
                if title and any(tok in blob for tok in str(title).lower().split()):
                    scored_products.append(p.get("name") or p.get("product_name"))
            if scored_products:
                products = scored_products[:4]

            acts = []
            if isinstance(activity, dict):
                for key in ("walk", "play", "mental", "weekly_summary", "recommendations"):
                    val = activity.get(key)
                    if isinstance(val, list):
                        acts.extend([str(x) for x in val[:2]])
                    elif val:
                        acts.append(str(val))
            elif isinstance(activity, list):
                acts = [str(a.get("activity") or a.get("title") or a) for a in activity[:3]]

            refs = [
                _cite(e, "BREED_CONDITIONS.csv")
                for e in (insight.get("evidence_sources") or [])[:3]
            ]
            if not refs:
                refs = [empty_reference()]

            widgets.append(
                make_widget(
                    "risk",
                    title=title,
                    probability=_pct(insight.get("biological_risk_percent")),
                    observed=_pct(
                        insight.get("observed_prevalence_percent")
                        or insight.get("observed_breed_prevalence_percent")
                    ),
                    confidence=_pct(insight.get("confidence_percent")),
                    severity=_pct(insight.get("priority_score")),
                    contributing_traits=insight.get("supporting_traits") or [],
                    contributing_conditions=conditions,
                    contributing_environment=[str(env)] if env else [],
                    summary=insight.get("explanation")
                    or insight.get("why_this_matters")
                    or insight.get("summary")
                    or AWAITING_DATABASE,
                    finding=insight.get("why_this_matters") or title,
                    reason=insight.get("explanation") or AWAITING_DATABASE,
                    prevention=list(dict.fromkeys(prevention))[:6] or [AWAITING_DATABASE],
                    early_warnings=list(dict.fromkeys(warnings))[:6] or [AWAITING_DATABASE],
                    relevant_nutrients=nutrients or [AWAITING_DATABASE],
                    relevant_activities=acts[:4] or [AWAITING_DATABASE],
                    relevant_products=products or [AWAITING_DATABASE],
                    references=refs,
                    trace=[
                        {"label": "Goal", "value": insight.get("goal_id")},
                        {"label": "Biological risk %", "value": insight.get("biological_risk_percent")},
                        {"label": "Traits", "value": ", ".join(insight.get("supporting_traits") or [])},
                        {"label": "Conditions", "value": ", ".join(conditions)},
                        {"label": "Environment", "value": env},
                        {"label": "CSV", "value": "BREED_CONDITIONS.csv|CLINICAL_RISK_TIMELINE.csv"},
                    ],
                )
            )

        # Timeline from CSV
        df = self.repo.clinical_risk_timeline()
        age_stage = profile.get("age_stage") or biology.get("age_stage") or "Adult"
        if not df.empty:
            stages = []
            traits = set(biology.get("trait_summary") or [])
            breeds = set(profile.get("breeds") or biology.get("breeds") or [])
            for stage in ("Puppy", "Adult", "Senior"):
                entries = []
                for _, row in df[df["age_stage"].astype(str).str.lower() == stage.lower()].iterrows():
                    ref = str(row.get("trait_or_breed", ""))
                    if ref not in traits and ref not in breeds:
                        continue
                    r = _row_dict(row)
                    entries.append(
                        {
                            "title": r.get("condition"),
                            "caption": f"{r.get('risk_level')} · Monitor: {r.get('monitoring')}",
                            "items": _split(r.get("prevention")),
                        }
                    )
                stages.append({"stage": stage, "current": stage.lower() == str(age_stage).lower(), "entries": entries})
            widgets.append(make_widget("timeline", title="Age progression", stages=stages))

        if not widgets:
            widgets.append(make_widget("warning", title="Risk Analysis", body=AWAITING_DATABASE))

        return make_section(
            section_id="risk_analysis",
            title="Risk Analysis",
            priority=50,
            summary="Deterministic priority risks with traits, prevention, nutrients, and products.",
            widgets=widgets,
        )

    def _nutrition(self, analyze: dict) -> dict[str, Any]:
        widgets = []
        pkg = next(
            (p for p in (analyze.get("wellnessPackages") or []) if p.get("recommended")),
            (analyze.get("wellnessPackages") or [None])[-1] if analyze.get("wellnessPackages") else None,
        )
        rows = (pkg or {}).get("full_nutrition_report") or (pkg or {}).get("daily_nutrition_intake") or []
        matrix = (pkg or {}).get("coverage_matrix") or []
        if not rows and matrix:
            rows = [
                {
                    "nutrient": r.get("nutrient"),
                    "target": r.get("target"),
                    "target_daily": r.get("target"),
                    "provided": r.get("provided"),
                    "unit": r.get("unit"),
                    "coverage_percent": r.get("coverage_percent"),
                    "sources": [{"product_name": s} for s in (r.get("primary_sources") or [])],
                }
                for r in matrix
            ]
        if not rows:
            # Engine targets still shown when active doses are absent from CSV
            for t in analyze.get("nutritionalTargets") or []:
                widgets.append(
                    make_widget(
                        "progress",
                        title=t.get("ingredient") or t.get("ingredient_key"),
                        value=0,
                        max=100,
                        display="0%",
                        caption=(
                            f"Target {t.get('daily_target') or AWAITING_DATABASE} · Provided 0 "
                            "(no active_ingredient doses in PRODUCT_COMPONENTS.csv)"
                        ),
                        references=[
                            make_reference(
                                source_name=t.get("source_name"),
                                source_url=t.get("source_url"),
                                quote=t.get("evidence_quote"),
                                csv_source="CONDITION_INGREDIENTS.csv",
                            )
                        ],
                        trace=[
                            {"label": "Target", "value": t.get("daily_target")},
                            {"label": "Goals", "value": ", ".join(t.get("supports_goals") or [])},
                            {"label": "CSV gap", "value": "PRODUCT_COMPONENTS.active_ingredient"},
                        ],
                    )
                )
            widgets.append(
                make_widget(
                    "warning",
                    title="Coverage note",
                    body=(
                        "Nutrient coverage requires active_ingredient rows in PRODUCT_COMPONENTS.csv. "
                        f"{AWAITING_DATABASE}"
                    ),
                )
            )
        else:
            for row in rows:
                target = float(row.get("target") or row.get("target_daily") or 0)
                provided = float(row.get("provided") or 0)
                cov = _pct(row.get("coverage_percent")) or 0
                sources = row.get("sources") or []
                widgets.append(
                    make_widget(
                        "progress",
                        title=row.get("nutrient"),
                        value=cov,
                        max=100,
                        display=f"{int(cov)}%",
                        caption=f"Target {target}{row.get('unit') or ''} · Provided {provided}{row.get('unit') or ''}",
                        meta={
                            "target": target,
                            "provided": provided,
                            "unit": row.get("unit"),
                            "deficit": max(0, target - provided),
                            "surplus": max(0, provided - target),
                            "contributors": [s.get("product_name") for s in sources if s.get("product_name")],
                        },
                        references=[
                            _cite(
                                row.get("evidence") if isinstance(row.get("evidence"), dict) else None,
                                "CONDITION_INGREDIENTS.csv",
                            )
                        ],
                        trace=[
                            {"label": "Nutrient", "value": row.get("nutrient")},
                            {"label": "Target", "value": target},
                            {"label": "Provided", "value": provided},
                            {"label": "Coverage %", "value": cov},
                            {"label": "CSV", "value": "PRODUCT_COMPONENTS.csv|CONDITION_INGREDIENTS.csv"},
                        ],
                    )
                )
            widgets.append(
                make_widget(
                    "ledger",
                    title="Nutrient ledger",
                    columns=["Nutrient", "Need", "Provided", "Coverage"],
                    rows=[
                        [
                            r.get("nutrient"),
                            f"{r.get('target') or r.get('target_daily')}{r.get('unit') or ''}",
                            f"{r.get('provided')}{r.get('unit') or ''}",
                            f"{int(_pct(r.get('coverage_percent') or 0) or 0)}%",
                        ]
                        for r in rows
                    ],
                )
            )

        # Yearly totals from recommended package 365-day plan
        if pkg and pkg.get("plan_365"):
            plan = pkg["plan_365"]
            widgets.append(
                make_widget(
                    "metrics",
                    title="365-day package totals",
                    items=[
                        {"label": "Yearly cost", "value": f"¥{pkg.get('yearly_cost') or plan.get('yearly_cost')}"},
                        {
                            "label": "Monthly (yearly÷12)",
                            "value": f"¥{pkg.get('monthly_cost') or plan.get('monthly_cost_derived')}",
                        },
                        {"label": "Products", "value": str(len(plan.get("products") or []))},
                    ],
                )
            )

        if not widgets:
            widgets.append(make_widget("warning", title="Nutrition", body=AWAITING_DATABASE))

        return make_section(
            section_id="nutrition_analysis",
            title="Nutrition Analysis",
            priority=60,
            summary="Target vs provided nutrient accounting from package optimization.",
            widgets=widgets,
        )

    def _activity(self, analyze: dict, biology: dict, profile: dict) -> dict[str, Any]:
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

        widgets = []
        if prescription:
            widgets.append(
                make_widget(
                    "activity",
                    title="Daily prescription",
                    morning_min=prescription.get("walk_morning_min"),
                    evening_min=prescription.get("walk_evening_min"),
                    daily_km=prescription.get("daily_km"),
                    weekly_km=prescription.get("weekly_km"),
                    swimming=prescription.get("swimming"),
                    fetch=prescription.get("fetch"),
                    training=prescription.get("training"),
                    mental=prescription.get("mental_enrichment"),
                    recovery=prescription.get("recovery_note"),
                    references=[_cite(prescription, "ACTIVITY_PRESCRIPTION_RULES.csv")],
                    trace=[
                        {"label": "Energy", "value": energy},
                        {"label": "Size", "value": size},
                        {"label": "Body", "value": body},
                        {"label": "Age stage", "value": age},
                        {"label": "CSV", "value": "ACTIVITY_PRESCRIPTION_RULES.csv"},
                    ],
                )
            )
            widgets.append(
                make_widget(
                    "progress",
                    title="Weekly walking",
                    value=min(100, float(prescription.get("weekly_km") or 0) * 2),
                    max=100,
                    display=f"{prescription.get('weekly_km')} km/week",
                )
            )
        else:
            widgets.append(make_widget("warning", title="Activity rules", body="No matching ACTIVITY_PRESCRIPTION_RULES row."))

        return make_section(
            section_id="activity_analysis",
            title="Activity Analysis",
            priority=70,
            summary="Deterministic activity plan from energy, size, body type, and age.",
            widgets=widgets,
        )

    def _packages(self, analyze: dict) -> dict[str, Any]:
        widgets = []
        for pkg in analyze.get("wellnessPackages") or []:
            tier = pkg.get("tier")
            products = [
                {
                    "product_id": p.get("product_id"),
                    "name": p.get("name") or p.get("product_name"),
                    "role": p.get("type") or p.get("category"),
                    "why": p.get("why_selected"),
                }
                for p in (pkg.get("products_included") or [])
            ]
            coverage = [
                {"label": c.get("title") or c.get("goal_id"), "value": _pct(c.get("coverage_percent")) or 0}
                for c in (pkg.get("nutrition_coverage") or [])
            ]
            widgets.append(
                make_widget(
                    "package",
                    id=str(tier),
                    title=pkg.get("title") or str(tier),
                    recommended=bool(pkg.get("recommended")),
                    summary=pkg.get("package_summary") or pkg.get("overview") or pkg.get("tagline"),
                    route=f"#/packages/{tier}",
                    monthly_cost=pkg.get("monthly_cost"),
                    yearly_cost=pkg.get("yearly_cost"),
                    coverage_score=_pct(pkg.get("coverage_score")),
                    overall_score=_pct(pkg.get("overall_score")),
                    products=products,
                    coverage_matrix=coverage,
                    why=pkg.get("why_fits"),
                    references=[_cite(n, "CLINICAL_EVIDENCE_BASE.csv") for n in (pkg.get("research_notes") or [])[:3]],
                    trace=[
                        {"label": "Tier", "value": tier},
                        {"label": "Coverage", "value": pkg.get("coverage_score")},
                        {"label": "CSV", "value": "PACKAGE_TIERS.csv|PPIE optimization"},
                    ],
                )
            )
        return make_section(
            section_id="package_analysis",
            title="Package Analysis",
            priority=80,
            summary="Optimization pathways — open a package for the full clinical recommendation.",
            widgets=widgets,
        )

    def _grooming(self, analyze: dict) -> dict[str, Any]:
        defs_df = self.repo.grooming_observation_defs()
        widgets = []
        groomer = analyze.get("groomer") or {}
        for _, row in defs_df.iterrows() if not defs_df.empty else []:
            r = _row_dict(row)
            key = str(r.get("observation_key", ""))
            status = groomer.get(key) if isinstance(groomer, dict) else None
            widgets.append(
                make_widget(
                    "accordion",
                    title=r.get("label") or key,
                    subtitle=status or "normal",
                    body=r.get("recommendation_template") or "",
                    items=[
                        {"label": f"Normal · {r.get('normal_criteria')}"},
                        {"label": f"Monitor · {r.get('monitor_criteria')}"},
                        {"label": f"Attention · {r.get('attention_criteria')}"},
                    ],
                    references=[make_reference(csv_source=r.get("source_csv") or "GROOMING_OBSERVATION_DEFS.csv")],
                )
            )
        return make_section(
            section_id="grooming_analysis",
            title="Grooming Analysis",
            priority=90,
            summary="Preventive observation definitions from GROOMING_OBSERVATION_DEFS.csv.",
            widgets=widgets,
        )

    def _references(self, analyze: dict) -> dict[str, Any]:
        widgets = []
        df = self.repo.clinical_evidence_base()
        if not df.empty:
            for _, row in df.iterrows():
                r = _row_dict(row)
                widgets.append(
                    make_widget(
                        "evidence",
                        title=r.get("condition") or r.get("domain") or "Evidence",
                        body=r.get("mechanism") or r.get("nutrient_or_activity") or "",
                        references=[_cite(r, "CLINICAL_EVIDENCE_BASE.csv")],
                    )
                )
        for note_pkg in analyze.get("wellnessPackages") or []:
            for n in note_pkg.get("research_notes") or []:
                widgets.append(
                    make_widget(
                        "evidence",
                        title=n.get("nutrient") or "Literature",
                        body=n.get("quote") or "",
                        references=[_cite(n, "INGREDIENT_EVIDENCE.csv")],
                    )
                )
        if not widgets:
            widgets.append(make_widget("warning", title="References", body="Awaiting linked publication."))
        return make_section(
            section_id="scientific_references",
            title="Scientific References",
            priority=100,
            summary="Citations from CLINICAL_EVIDENCE_BASE.csv and ingredient evidence. Missing links show placeholders.",
            widgets=widgets,
        )

    # ── nested package / product reports ─────────────────

    def _package_detail_reports(self, analyze: dict) -> dict[str, Any]:
        out = {}
        profile = analyze.get("profile") or {}
        for pkg in analyze.get("wellnessPackages") or []:
            tier = str(pkg.get("tier"))
            sections = [
                make_section(
                    section_id="why",
                    title="Why this package exists",
                    priority=10,
                    summary=pkg.get("package_summary") or "",
                    widgets=[
                        make_widget("text", body=pkg.get("overview") or pkg.get("description") or pkg.get("tagline") or ""),
                        make_widget("text", body=pkg.get("why_fits") or ""),
                        make_widget(
                            "chips",
                            title="Biological targets",
                            items=[
                                {"label": c.get("title"), "tone": "good" if (_pct(c.get("coverage_percent")) or 0) >= 90 else "warn"}
                                for c in (pkg.get("nutrition_coverage") or [])
                            ],
                        ),
                    ],
                ),
                make_section(
                    section_id="coverage",
                    title="Coverage Dashboard",
                    priority=20,
                    widgets=[
                        make_widget(
                            "progress",
                            title=c.get("title") or c.get("goal_id"),
                            value=_pct(c.get("coverage_percent")) or 0,
                            max=100,
                            display=f"{int(_pct(c.get('coverage_percent')) or 0)}%",
                        )
                        for c in (pkg.get("nutrition_coverage") or [])
                    ],
                ),
                make_section(
                    section_id="products",
                    title="Included Products",
                    priority=30,
                    widgets=[
                        make_widget(
                            "product",
                            product_id=p.get("product_id"),
                            title=p.get("name") or p.get("product_name"),
                            subtitle=p.get("type") or p.get("category"),
                            summary=p.get("why_selected"),
                            route=f"#/products/{p.get('product_id')}",
                            serving=p.get("serving_size") or p.get("daily_amount"),
                            monthly_cost=p.get("monthly_cost") or p.get("price"),
                            coverage=_pct(p.get("coverage_percent")),
                            actives=p.get("active_ingredients") or [],
                            trace=[
                                {"label": "Product", "value": p.get("product_id")},
                                {"label": "Why", "value": p.get("why_selected")},
                                {"label": "CSV", "value": "PRODUCT_CATALOG.csv|PRODUCT_COMPONENTS.csv"},
                            ],
                        )
                        for p in (pkg.get("products_included") or [])
                    ],
                ),

                make_section(
                    section_id="nutrition",
                    title="Coverage Matrix",
                    priority=40,
                    widgets=[
                        make_widget(
                            "ledger",
                            title="Target · Provided · Coverage · Surplus",
                            columns=["Nutrient", "Target", "Provided", "Coverage %", "Surplus", "Sources"],
                            rows=[
                                [
                                    r.get("nutrient"),
                                    f"{r.get('target') if r.get('target') is not None else r.get('target_daily')}{r.get('unit') or ''}",
                                    f"{r.get('provided')}{r.get('unit') or ''}",
                                    f"{int(_pct(r.get('coverage_percent')) or 0)}%",
                                    r.get("surplus", "—"),
                                    ", ".join(r.get("primary_sources") or []) or "—",
                                ]
                                for r in (
                                    pkg.get("coverage_matrix")
                                    or pkg.get("full_nutrition_report")
                                    or pkg.get("daily_nutrition_intake")
                                    or []
                                )
                            ],
                        )
                    ],
                ),
                make_section(
                    section_id="plan_365",
                    title="365-Day Plan",
                    priority=45,
                    summary="Yearly inventory first. Monthly cost = yearly ÷ 12.",
                    widgets=[
                        make_widget(
                            "ledger",
                            title="Annual inventory",
                            columns=["Product", "Daily", "Packages/year", "Yearly ¥", "Monthly ¥"],
                            rows=[
                                [
                                    row.get("product_name"),
                                    row.get("daily_serving"),
                                    row.get("packages_needed"),
                                    row.get("yearly_cost"),
                                    row.get("monthly_cost"),
                                ]
                                for row in ((pkg.get("plan_365") or {}).get("products") or [])
                            ],
                        ),
                        make_widget(
                            "metrics",
                            items=[
                                {"label": "Yearly total", "value": f"¥{int(pkg.get('yearly_cost') or 0)}"},
                                {
                                    "label": "Monthly (derived)",
                                    "value": f"¥{int(pkg.get('monthly_cost') or 0)}",
                                    "caption": "yearly ÷ 12",
                                },
                            ],
                        ),
                    ],
                ),
                make_section(
                    section_id="rejected",
                    title="Products considered & rejected",
                    priority=48,
                    widgets=[
                        make_widget(
                            "comparison",
                            title=r.get("product_name"),
                            status="rejected",
                            body=r.get("reason"),
                        )
                        for r in (pkg.get("products_rejected") or [])
                    ]
                    or [make_widget("text", body="All eligible functional candidates were included.")],
                ),
                make_section(
                    section_id="evidence",
                    title="Scientific Support",
                    priority=50,
                    widgets=[
                        make_widget(
                            "evidence",
                            title=n.get("nutrient"),
                            body=n.get("quote"),
                            references=[_cite(n, "INGREDIENT_EVIDENCE.csv")],
                        )
                        for n in (pkg.get("research_notes") or [])
                    ]
                    or [make_widget("warning", body="Awaiting linked publication.")],
                ),
            ]
            name = profile.get("pet_name") or profile.get("name") or "Pet"
            out[tier] = make_report_envelope(
                sections=sections,
                data_version=self._data_version(),
                csv_hash=self._csv_hash(),
                ppie_version=analyze.get("version"),
                navigation=[{"id": s["id"], "label": s["title"]} for s in sections],
            )
            out[tier]["hero"] = {
                "title": pkg.get("title") or tier,
                "subtitle": f"Designed specifically for {name}",
                "kicker": "Recommended pathway" if pkg.get("recommended") else "Care pathway",
                "metrics": [
                    {"label": "Monthly (÷12)", "value": f"¥{int(pkg.get('monthly_cost') or 0)}"},
                    {"label": "Yearly", "value": f"¥{int(pkg.get('yearly_cost') or 0)}"},
                    {"label": "Products", "value": str(len(pkg.get("products_included") or []))},
                    {
                        "label": "Overall score",
                        "value": f"{int(_pct(pkg.get('overall_score') or pkg.get('coverage_score')) or 0)}",
                        "caption": "coverage · clinical · evidence · cost · diversity",
                    },
                ],
                "calculated_from": [
                    "PRODUCT_CATALOG.csv",
                    "PRODUCT_COMPONENTS.csv",
                    "PRODUCT_FUNCTIONS.csv",
                    "PRODUCT_PRICING.csv",
                    "PRODUCT_FEEDING_RULES.csv",
                    "PACKAGE_TIERS.csv",
                ],
            }
        return out

    def _product_detail_reports(self, analyze: dict) -> dict[str, Any]:
        """Catalog-backed product reports for every package product + analyze.productAnalyses."""
        out: dict[str, Any] = {}
        analyses = analyze.get("productAnalyses") or {}
        for pid, a in analyses.items():
            out[str(pid)] = self._envelope_from_product_analysis(str(pid), a, analyze)

        from app.agent.package_optimizer import load_candidate_products

        profile = analyze.get("profile") or analyze.get("pet") or {}
        weight = float(profile.get("weight_kg") or profile.get("weight") or 10)
        candidates = {c["product_id"]: c for c in load_candidate_products(self.repo, weight)}
        for pkg in analyze.get("wellnessPackages") or []:
            for p in pkg.get("products_included") or []:
                pid = str(p.get("product_id") or "")
                if not pid or pid in out:
                    continue
                c = candidates.get(pid)
                if c:
                    out[pid] = self._product_report_from_candidate(c, p, analyze)
        return out

    def _envelope_from_product_analysis(self, pid: str, a: dict, analyze: dict) -> dict[str, Any]:
        sections = [
            make_section(
                section_id="overview",
                title="Overview",
                priority=10,
                widgets=[
                    make_widget("text", body=a.get("overview") or ""),
                    make_widget("list", title="Why included", items=a.get("why_included") or []),
                ],
            ),
            make_section(
                section_id="actives",
                title="Active ingredients",
                priority=20,
                widgets=[
                    make_widget(
                        "progress",
                        title=ai.get("name"),
                        value=ai.get("coverage_percent") or 0,
                        max=100,
                        display=f"{int(ai.get('coverage_percent') or 0)}%",
                        caption=f"{ai.get('amount')}{ai.get('unit') or ''} · target {ai.get('target')}{ai.get('target_unit') or ''}",
                        references=[_cite(ai.get("evidence") if isinstance(ai.get("evidence"), dict) else None)],
                    )
                    for ai in (a.get("active_ingredients") or [])
                ]
                or [make_widget("warning", body="Awaiting linked publication.")],
            ),
            make_section(
                section_id="alternatives",
                title="Alternatives considered",
                priority=30,
                widgets=[
                    make_widget(
                        "comparison",
                        title=alt.get("product_name"),
                        body=alt.get("reason") or "Not selected for this pathway.",
                        status="rejected",
                    )
                    for alt in (a.get("alternatives") or [])
                ]
                or [make_widget("text", body="No alternatives returned for this product.")],
            ),
            make_section(
                section_id="evidence",
                title="Evidence",
                priority=40,
                widgets=[
                    make_widget(
                        "evidence",
                        title=ev.get("ingredient"),
                        body=ev.get("summary") or ev.get("mechanism"),
                        references=[_cite(ev)],
                    )
                    for ev in (a.get("scientific_evidence") or [])
                ]
                or [make_widget("warning", body="Awaiting linked publication.")],
            ),
            make_section(
                section_id="specs",
                title="Specifications",
                priority=50,
                widgets=[
                    make_widget(
                        "metrics",
                        items=[
                            {"label": k.replace("_", " ").title(), "value": str(v)}
                            for k, v in (a.get("specifications") or {}).items()
                            if v is not None
                        ],
                    )
                ],
            ),
        ]
        env = make_report_envelope(
            sections=sections,
            data_version=self._data_version(),
            csv_hash=self._csv_hash(),
            ppie_version=analyze.get("version"),
        )
        env["hero"] = {
            "title": a.get("product_name") or pid,
            "subtitle": f"/products/{pid}",
            "kicker": "Product analysis",
            "metrics": [
                {"label": "Brand", "value": a.get("brand") or "—"},
                {"label": "Category", "value": a.get("category") or "—"},
            ],
        }
        return env

    def _product_report_from_candidate(self, c: dict, package_item: dict, analyze: dict) -> dict[str, Any]:
        yearly = c.get("yearly") or {}
        sections = [
            make_section(
                section_id="overview",
                title="Overview",
                priority=10,
                summary=c.get("short_description") or "",
                widgets=[
                    make_widget("text", body=c.get("short_description") or c.get("product_name")),
                    make_widget(
                        "list",
                        title="Why PPIE selected this",
                        items=package_item.get("selection_reasons")
                        or ([package_item.get("why_selected")] if package_item.get("why_selected") else []),
                    ),
                    make_widget(
                        "metrics",
                        items=[
                            {"label": "Price", "value": f"¥{c.get('list_price_rmb')}"},
                            {"label": "Cost / day", "value": f"¥{round((c.get('yearly_cost') or 0) / 365, 2)}"},
                            {"label": "Cost / year", "value": f"¥{c.get('yearly_cost')}"},
                            {"label": "Serving", "value": c.get("serving_size")},
                        ],
                    ),
                ],
            ),
            make_section(
                section_id="nutrition_facts",
                title="Nutrition Facts",
                priority=20,
                widgets=[
                    make_widget(
                        "ledger",
                        columns=["Component", "Type", "Value", "Unit", "Evidence"],
                        rows=[
                            [
                                row.get("component_name"),
                                row.get("component_type"),
                                row.get("value") if row.get("value") is not None else "—",
                                row.get("unit") or "",
                                row.get("evidence_level") or "—",
                            ]
                            for row in (c.get("components") or [])
                        ],
                    )
                    if c.get("components")
                    else make_widget("warning", body="Awaiting linked publication.")
                ],
            ),
            make_section(
                section_id="functions",
                title="Clinical Functions",
                priority=30,
                widgets=[
                    make_widget(
                        "chips",
                        items=[
                            {"label": f"{f.get('function')} · {f.get('confidence')}", "tone": "accent"}
                            for f in (c.get("functions") or [])
                        ],
                    )
                    if c.get("functions")
                    else make_widget("warning", body="No PRODUCT_FUNCTIONS row for this product.")
                ],
            ),
            make_section(
                section_id="serving",
                title="Serving Calculator",
                priority=40,
                widgets=[
                    make_widget(
                        "ledger",
                        title="365-day inventory",
                        columns=["Field", "Value"],
                        rows=[[k, v] for k, v in yearly.items()],
                    )
                ],
            ),
            make_section(
                section_id="storage",
                title="Storage",
                priority=50,
                widgets=[
                    make_widget(
                        "metrics",
                        items=[
                            {"label": "Storage", "value": (c.get("ext") or {}).get("storage_method") or "—"},
                            {"label": "Shelf life (days)", "value": (c.get("ext") or {}).get("shelf_life_days") or "—"},
                        ],
                    )
                ],
            ),
        ]
        env = make_report_envelope(
            sections=sections,
            data_version=self._data_version(),
            csv_hash=self._csv_hash(),
            ppie_version=analyze.get("version"),
        )
        env["hero"] = {
            "title": c.get("product_name") or c.get("product_id"),
            "subtitle": f"/products/{c.get('product_id')}",
            "kicker": "Product analysis",
            "metrics": [
                {"label": "Brand", "value": c.get("brand") or "—"},
                {"label": "Category", "value": c.get("category") or "—"},
                {"label": "Yearly", "value": f"¥{c.get('yearly_cost') or 0}"},
            ],
            "calculated_from": [
                "PRODUCT_CATALOG.csv",
                "PRODUCT_COMPONENTS.csv",
                "PRODUCT_FUNCTIONS.csv",
                "PRODUCT_PRICING.csv",
                "PRODUCT_FEEDING_RULES.csv",
            ],
        }
        return env




def build_standard_report(repo: DataRepository, analyze: dict[str, Any]) -> dict[str, Any]:
    return ReportGenerator(repo).build(analyze)
