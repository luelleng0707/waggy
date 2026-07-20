"""KnowledgeGraphBuilder — load platform tables into a pure relationship graph."""

from __future__ import annotations

import hashlib
from typing import Any

from app.data.repository import DataPlatform
from app.science.graph import KnowledgeGraph
from app.science.models import EvidenceObject


def _paper_id_from_row(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("source_name") or row.get("source_title") or "").strip(),
        str(row.get("source_url") or row.get("url") or "").strip(),
        str(row.get("year") or "").strip(),
        str(row.get("source_quote") or row.get("quote") or "").strip()[:120],
    ]
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"PAPER_{digest}"


class KnowledgeGraphBuilder:
    def __init__(self, platform: DataPlatform):
        self.platform = platform

    def build(self) -> KnowledgeGraph:
        g = KnowledgeGraph()
        self._add_breeds(g)
        self._add_breed_conditions(g)
        self._add_trait_conditions(g)
        self._add_ingredients(g)
        self._add_foods(g)
        self._add_activities(g)
        self._add_products(g)
        return g

    def evidence_objects(self) -> list[EvidenceObject]:
        """Flatten citation-bearing science rows into EvidenceObjects."""
        out: list[EvidenceObject] = []
        frames = [
            ("breed_conditions", self.platform.breed_conditions(), "breed", "condition"),
            ("condition_ingredients", self.platform.condition_ingredients(), "ingredient_name", "condition"),
            ("ingredient_evidence", self.platform.ingredient_evidence(), "ingredient_name", None),
        ]
        for table, df, subject_col, cond_col in frames:
            if df is None or df.empty:
                continue
            for _, row in df.iterrows():
                rec = row.to_dict()
                if not any(str(rec.get(c) or "").strip() for c in ("source_name", "source_url", "source_quote")):
                    continue
                pid = _paper_id_from_row(rec)
                subject = str(rec.get(subject_col) or "")
                condition = str(rec.get(cond_col) or "") if cond_col else None
                eid = f"EV_{hashlib.sha1(f'{table}|{subject}|{condition}|{pid}'.encode()).hexdigest()[:10]}"
                prev = rec.get("prevalence")
                try:
                    effect = float(prev) if prev is not None and str(prev) != "" else None
                except (TypeError, ValueError):
                    effect = None
                out.append(
                    EvidenceObject(
                        id=eid,
                        condition=condition,
                        ingredient=subject if table != "breed_conditions" else None,
                        paper_id=pid,
                        paper_title=str(rec.get("source_name") or ""),
                        confidence=str(rec.get("confidence_level") or rec.get("evidence_type") or ""),
                        effect_size=effect,
                        reason=str(rec.get("source_quote") or "")[:400],
                        citations=[
                            {
                                "source_name": rec.get("source_name"),
                                "source_url": rec.get("source_url"),
                                "year": rec.get("year"),
                                "quote": rec.get("source_quote"),
                            }
                        ],
                        source_table=table,
                        source_row=rec.get("_csv_row"),
                        url=str(rec.get("source_url") or ""),
                        year=str(rec.get("year") or ""),
                    )
                )
        return out

    def _add_breeds(self, g: KnowledgeGraph) -> None:
        df = self.platform.breeds_df()
        if df.empty:
            return
        for _, row in df.iterrows():
            breed = str(row.get("breed") or "")
            if not breed:
                continue
            bid = g.upsert_node("breed", breed, breed)
            for trait_col, kind in (
                ("size", "trait"),
                ("body_type", "trait"),
                ("coat_type", "trait"),
                ("energy", "trait"),
                ("skull_type", "trait"),
                ("climate", "trait"),
                ("lifespan", "trait"),
                ("function_group", "trait"),
                ("weakness_group", "trait"),
            ):
                val = str(row.get(trait_col) or "").strip()
                if not val:
                    continue
                tid = g.upsert_node(kind, f"{trait_col}:{val}", val, trait_category=trait_col)
                g.add_edge(bid, tid, "has_trait", trait_category=trait_col)

    def _add_breed_conditions(self, g: KnowledgeGraph) -> None:
        df = self.platform.breed_conditions()
        if df.empty:
            return
        for _, row in df.iterrows():
            breed = str(row.get("breed") or "")
            cond = str(row.get("condition") or "")
            if not breed or not cond:
                continue
            bid = g.upsert_node("breed", breed, breed)
            cid = g.upsert_node("condition", cond, cond)
            pid = _paper_id_from_row(row.to_dict())
            paper = g.upsert_node(
                "paper",
                pid,
                str(row.get("source_name") or pid),
                url=row.get("source_url"),
                year=row.get("year"),
                quote=str(row.get("source_quote") or "")[:240],
            )
            prev = row.get("prevalence")
            try:
                risk = float(prev) if prev is not None and str(prev) != "" else None
            except (TypeError, ValueError):
                risk = None
            g.add_edge(
                bid,
                cid,
                "risk",
                prevalence=risk,
                paper_id=pid,
                confidence=row.get("confidence_level"),
                csv_row=row.get("_csv_row"),
                csv_file=row.get("_csv_file"),
            )
            g.add_edge(cid, paper, "supported_by", paper_id=pid)
            g.add_edge(paper, bid, "studies", condition=cond)

    def _add_trait_conditions(self, g: KnowledgeGraph) -> None:
        df = self.platform.trait_condition_tables()
        if df.empty:
            return
        for _, row in df.iterrows():
            cat = str(row.get("trait_category") or "")
            val = str(row.get("trait_value") or "")
            cond = str(row.get("condition") or "")
            if not cat or not val or not cond:
                continue
            tid = g.upsert_node("trait", f"{cat}:{val}", val, trait_category=cat)
            cid = g.upsert_node("condition", cond, cond)
            pid = _paper_id_from_row(row.to_dict())
            paper = g.upsert_node(
                "paper",
                pid,
                str(row.get("source_name") or pid),
                url=row.get("source_url"),
                year=row.get("year"),
            )
            try:
                prev = float(row.get("prevalence")) if row.get("prevalence") not in (None, "") else None
            except (TypeError, ValueError):
                prev = None
            g.add_edge(tid, cid, "risk", prevalence=prev, paper_id=pid, trait_category=cat)
            g.add_edge(cid, paper, "supported_by", paper_id=pid)

    def _add_ingredients(self, g: KnowledgeGraph) -> None:
        ci = self.platform.condition_ingredients()
        if not ci.empty:
            for _, row in ci.iterrows():
                ing = str(row.get("ingredient_name") or "")
                cond = str(row.get("condition") or "")
                if not ing or not cond:
                    continue
                iid = g.upsert_node("ingredient", ing, ing)
                cid = g.upsert_node("condition", cond, cond)
                pid = _paper_id_from_row(row.to_dict())
                paper = g.upsert_node("paper", pid, str(row.get("source_name") or pid), url=row.get("source_url"))
                g.add_edge(
                    iid,
                    cid,
                    "supports",
                    dose=row.get("recommended_daily_dose"),
                    unit=row.get("dose_unit"),
                    paper_id=pid,
                    priority=row.get("priority_rank"),
                )
                g.add_edge(iid, paper, "cites", paper_id=pid)
                # Heuristic: omega / fish oil → joint support language
                low = ing.lower()
                if any(k in low for k in ("omega", "epa", "dha", "fish oil", "glucosamine", "chondroitin", "msm")):
                    g.add_edge(iid, cid, "reduces", mechanism="nutritional_support")

        ie = self.platform.ingredient_evidence()
        if not ie.empty:
            for _, row in ie.iterrows():
                ing = str(row.get("ingredient_name") or "")
                if not ing:
                    continue
                iid = g.upsert_node("ingredient", ing, ing)
                pid = _paper_id_from_row(row.to_dict())
                paper = g.upsert_node("paper", pid, str(row.get("source_name") or pid), url=row.get("source_url"))
                g.add_edge(iid, paper, "cites", paper_id=pid, year=row.get("year"))
                for flag, cond_hint in (
                    ("supports_joint", "Joint Health"),
                    ("supports_skin", "Skin Health"),
                    ("supports_gut", "Gut Health"),
                ):
                    val = str(row.get(flag) or "").strip().lower()
                    if val in ("1", "true", "yes", "y"):
                        cid = g.upsert_node("condition", cond_hint, cond_hint)
                        g.add_edge(iid, cid, "supports", from_flag=flag)

    def _add_foods(self, g: KnowledgeGraph) -> None:
        df = self.platform.natural_food_sources()
        if df.empty:
            return
        for _, row in df.iterrows():
            food = str(row.get("food_source") or row.get("food_name") or row.get("food") or "")
            ing = str(row.get("ingredient_name") or row.get("nutrient_name") or "")
            if not food:
                continue
            fid = g.upsert_node("food", food, food)
            if ing:
                iid = g.upsert_node("ingredient", ing, ing)
                g.add_edge(fid, iid, "contains")

    def _add_activities(self, g: KnowledgeGraph) -> None:
        df = self.platform.condition_activities()
        if df.empty:
            return
        for _, row in df.iterrows():
            cond = str(row.get("condition") or row.get("condition_name") or "")
            act = str(row.get("activity_name") or row.get("activity") or "")
            if not cond or not act:
                continue
            cid = g.upsert_node("condition", cond, cond)
            aid = g.upsert_node("activity", act, act)
            g.add_edge(aid, cid, "prevents")

    def _add_products(self, g: KnowledgeGraph) -> None:
        catalog = self.platform.product_catalog()
        comps = self.platform.product_components()
        if not catalog.empty:
            for _, row in catalog.iterrows():
                pid = str(row.get("product_id") or "")
                name = str(row.get("product_name") or row.get("name") or pid)
                if not pid:
                    continue
                g.upsert_node("product", pid, name, category=row.get("category"), status=row.get("status"))
        if not comps.empty:
            for _, row in comps.iterrows():
                pid = str(row.get("product_id") or "")
                comp = str(row.get("component_name") or row.get("ingredient_name") or row.get("active_name") or "")
                if not pid or not comp:
                    continue
                prod = g.upsert_node("product", pid, pid)
                iid = g.upsert_node("ingredient", comp, comp)
                g.add_edge(prod, iid, "contains", amount=row.get("amount"), unit=row.get("unit"))
