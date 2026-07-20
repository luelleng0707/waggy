"""Deterministic research query tools (not AI)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder
from app.science.diff_engine import ScientificDiffEngine

ROOT = Path(__file__).resolve().parents[2]


class ResearchAssistant:
    def __init__(self, platform: DataPlatform | None = None):
        self.platform = platform or DataPlatform("data", strict=True)
        self.graph = KnowledgeGraphBuilder(self.platform).build()

    def papers_by_condition(self, condition: str) -> list[dict[str, Any]]:
        q = condition.lower().strip()
        out = []
        for n in self.graph.by_type("condition"):
            if q not in (n.label or "").lower() and q not in n.id.lower():
                continue
            for e in self.graph.edges:
                if e.source != n.id and e.target != n.id:
                    continue
                other = e.target if e.source == n.id else e.source
                p = self.graph.nodes.get(other)
                if p and p.type == "paper":
                    out.append({"condition": n.label, "paper": p.label or p.id, "relation": e.relation})
        return out

    def ingredients_by_mechanism(self, mechanism: str) -> list[dict[str, Any]]:
        q = mechanism.lower().strip()
        out = []
        # Prefer CSV if available
        for attr in ("ingredient_mechanisms", "ingredient_evidence"):
            fn = getattr(self.platform, attr, None)
            if not callable(fn):
                continue
            try:
                df = fn()
            except Exception:
                continue
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
            mech_col = next((c for c in df.columns if "mech" in c.lower()), None)
            ing_col = next((c for c in df.columns if "ingred" in c.lower()), None)
            if not mech_col:
                continue
            for _, row in df.iterrows():
                m = str(row.get(mech_col) or "").lower()
                if q in m:
                    out.append(
                        {
                            "ingredient": str(row.get(ing_col) or "") if ing_col else "",
                            "mechanism": str(row.get(mech_col) or ""),
                            "source_table": attr,
                        }
                    )
        # Graph fallback
        if not out:
            for n in self.graph.by_type("ingredient"):
                meta = n.meta if hasattr(n, "meta") else {}
                blob = json.dumps(meta or {}, default=str).lower()
                if q in blob or q in (n.label or "").lower():
                    out.append({"ingredient": n.label or n.id, "mechanism": mechanism, "source_table": "graph"})
        return out

    def conditions_by_breed(self, breed: str) -> list[dict[str, Any]]:
        q = breed.lower().strip()
        bc = self.platform.breed_conditions()
        out = []
        if bc.empty:
            return out
        bcol = next((c for c in bc.columns if "breed" in c.lower()), None)
        ccol = next((c for c in bc.columns if "condition" in c.lower()), None)
        if not bcol or not ccol:
            return out
        for _, row in bc.iterrows():
            if q in str(row.get(bcol) or "").lower():
                out.append({k: row.get(k) for k in bc.columns})
        return out

    def recommendations_affected_by_paper(self, paper_id: str) -> list[dict[str, Any]]:
        q = paper_id.lower().strip()
        papers = [
            n
            for n in self.graph.by_type("paper")
            if q in n.id.lower() or q in (n.label or "").lower()
        ]
        affected = []
        pids = {p.id for p in papers}
        for e in self.graph.edges:
            if e.source in pids or e.target in pids:
                other = e.target if e.source in pids else e.source
                n = self.graph.nodes.get(other)
                if n:
                    affected.append(
                        {
                            "paper": next(iter(pids)),
                            "entity_type": n.type,
                            "entity": n.label or n.id,
                            "relation": e.relation,
                        }
                    )
        return affected

    def products_supporting_condition(self, condition: str) -> list[dict[str, Any]]:
        q = condition.lower().strip()
        out = []
        cond_ids = {
            n.id
            for n in self.graph.by_type("condition")
            if q in (n.label or "").lower() or q in n.id.lower()
        }
        # condition -> ingredient -> product paths
        ing_ids = set()
        for e in self.graph.edges:
            if e.source in cond_ids or e.target in cond_ids:
                other = e.target if e.source in cond_ids else e.source
                n = self.graph.nodes.get(other)
                if n and n.type == "ingredient":
                    ing_ids.add(n.id)
        for e in self.graph.edges:
            if e.source in ing_ids or e.target in ing_ids:
                other = e.target if e.source in ing_ids else e.source
                n = self.graph.nodes.get(other)
                if n and n.type == "product":
                    out.append({"condition": condition, "product": n.label or n.id, "via": "ingredient"})
        # direct product edges
        for e in self.graph.edges:
            if e.source in cond_ids or e.target in cond_ids:
                other = e.target if e.source in cond_ids else e.source
                n = self.graph.nodes.get(other)
                if n and n.type == "product":
                    out.append({"condition": condition, "product": n.label or n.id, "via": "direct"})
        # dedupe
        seen = set()
        uniq = []
        for row in out:
            key = (row["product"], row["via"])
            if key not in seen:
                seen.add(key)
                uniq.append(row)
        return uniq

    def compare_versions(self, left: Path | str, right: Path | str) -> dict[str, Any]:
        left, right = Path(left), Path(right)
        # Prefer DiffEngine on graphs if present; else directory file list
        result: dict[str, Any] = {"left": str(left), "right": str(right), "files": {}}
        result["diff_note"] = (
            "CSV path inventory comparison below. "
            "For graph topology diffs use ScientificDiffEngine.diff_graphs(before, after)."
        )
        result["diff_engine"] = ScientificDiffEngine.__name__

        def _csv_names(p: Path) -> set[str]:
            if not p.exists():
                return set()
            return {f.name for f in p.rglob("*.csv")}

        left_csvs = _csv_names(left)
        right_csvs = _csv_names(right)
        result["files"] = {
            "only_left": sorted(left_csvs - right_csvs),
            "only_right": sorted(right_csvs - left_csvs),
            "shared": sorted(left_csvs & right_csvs),
        }
        return result


def main_cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="PPIE research query tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("papers-by-condition")
    a.add_argument("condition")
    b = sub.add_parser("ingredients-by-mechanism")
    b.add_argument("mechanism")
    c = sub.add_parser("conditions-by-breed")
    c.add_argument("breed")
    d = sub.add_parser("recs-by-paper")
    d.add_argument("paper_id")
    e = sub.add_parser("products-by-condition")
    e.add_argument("condition")
    f = sub.add_parser("compare")
    f.add_argument("left")
    f.add_argument("right")

    args = p.parse_args()
    ra = ResearchAssistant()
    if args.cmd == "papers-by-condition":
        print(json.dumps(ra.papers_by_condition(args.condition), indent=2, default=str))
    elif args.cmd == "ingredients-by-mechanism":
        print(json.dumps(ra.ingredients_by_mechanism(args.mechanism), indent=2, default=str))
    elif args.cmd == "conditions-by-breed":
        print(json.dumps(ra.conditions_by_breed(args.breed), indent=2, default=str)[:20000])
    elif args.cmd == "recs-by-paper":
        print(json.dumps(ra.recommendations_affected_by_paper(args.paper_id), indent=2, default=str))
    elif args.cmd == "products-by-condition":
        print(json.dumps(ra.products_supporting_condition(args.condition), indent=2, default=str))
    elif args.cmd == "compare":
        print(json.dumps(ra.compare_versions(args.left, args.right), indent=2, default=str))


if __name__ == "__main__":
    main_cli()
