"""Extended scientific validators — evidence, biology, ingredients, products, graph."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder
from app.science.validator import DataValidator

ROOT = Path(__file__).resolve().parents[2]


def _safe_float(v: Any) -> float | None:
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return None
        s = str(v).strip().replace("%", "")
        if not s or s.lower() in {"nan", "none", ""}:
            return None
        return float(s)
    except (TypeError, ValueError):
        return None


class ExtendedScienceValidator:
    """Phase 5D validators. Additive to Phase 4 DataValidator; never mutates clinical data."""

    def __init__(self, platform: DataPlatform | None = None):
        self.platform = platform or DataPlatform("data", strict=True)
        self.base = DataValidator(self.platform)

    def validate(self) -> dict[str, Any]:
        base = self.base.validate()
        errors = list(base.get("errors") or [])
        warnings = list(base.get("warnings") or [])
        sections: dict[str, Any] = {"base": base}

        sections["evidence"] = self._validate_evidence(errors, warnings)
        sections["biology"] = self._validate_biology(errors, warnings)
        sections["ingredients"] = self._validate_ingredients(errors, warnings)
        sections["products"] = self._validate_products(errors, warnings)
        sections["graph"] = self._validate_graph(errors, warnings)

        return {
            "ok": not errors,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "errors": errors,
            "warnings": warnings,
            "sections": sections,
            "stats": base.get("stats") or {},
        }

    def _validate_evidence(self, errors: list[str], warnings: list[str]) -> dict[str, Any]:
        ceb = self.platform.clinical_evidence_base()
        missing_doi = 0
        bad_year = 0
        unsupported_type = 0
        quotes: list[str] = []
        allowed_types = {
            "rct",
            "randomized",
            "meta-analysis",
            "systematic review",
            "cohort",
            "case-control",
            "observational",
            "review",
            "guideline",
            "expert",
            "in vitro",
            "animal",
            "clinical",
            "unknown",
            "",
        }

        if not ceb.empty:
            for _, row in ceb.iterrows():
                doi = str(row.get("doi") or row.get("DOI") or "").strip()
                if not doi:
                    missing_doi += 1
                year = _safe_float(row.get("year") or row.get("publication_year"))
                if year is not None and (year < 1900 or year > datetime.now().year + 1):
                    bad_year += 1
                    errors.append(f"Invalid publication year: {year}")
                st = str(row.get("study_type") or row.get("evidence_type") or "").strip().lower()
                if st and not any(a in st for a in allowed_types if a):
                    unsupported_type += 1
                    warnings.append(f"Unsupported study type: {st[:80]}")
                q = str(row.get("quote") or row.get("excerpt") or "").strip()
                if q:
                    quotes.append(q.lower())

        dup_quotes = [q for q, c in Counter(quotes).items() if c > 1]
        if dup_quotes:
            warnings.append(f"{len(dup_quotes)} duplicate evidence quotes")

        paper_ids = []
        if not ceb.empty:
            for col in ("paper_id", "Paper_ID", "citation_id", "id"):
                if col in ceb.columns:
                    paper_ids.extend(ceb[col].astype(str).str.strip().tolist())
                    break
        dup_papers = [p for p, c in Counter([p for p in paper_ids if p and p != "nan"]).items() if c > 1]

        if missing_doi:
            warnings.append(f"{missing_doi} evidence rows missing DOI")
        if unsupported_type:
            warnings.append(f"{unsupported_type} rows with unsupported study type")

        return {
            "missing_doi": missing_doi,
            "invalid_year": bad_year,
            "unsupported_study_type": unsupported_type,
            "duplicate_quotes": len(dup_quotes),
            "duplicate_paper_ids_in_table": len(dup_papers),
        }

    def _validate_biology(self, errors: list[str], warnings: list[str]) -> dict[str, Any]:
        breeds = self.platform.breeds
        breed_ids = set()
        if not breeds.empty:
            for col in ("breed", "Breed", "breed_name", "name"):
                if col in breeds.columns:
                    breed_ids = set(breeds[col].astype(str).str.strip().str.lower())
                    break

        invalid_breeds = 0
        missing_prev = 0
        impossible_prev = 0
        bc = self.platform.breed_conditions()
        if not bc.empty and breed_ids:
            bcol = next((c for c in ("breed", "Breed", "breed_name") if c in bc.columns), None)
            pcol = next(
                (c for c in ("prevalence", "Prevalence", "risk_pct", "lifetime_risk") if c in bc.columns),
                None,
            )
            if bcol:
                for _, row in bc.iterrows():
                    b = str(row.get(bcol) or "").strip().lower()
                    if b and b not in breed_ids and b != "nan":
                        invalid_breeds += 1
            if pcol:
                for _, row in bc.iterrows():
                    p = _safe_float(row.get(pcol))
                    if p is None:
                        missing_prev += 1
                    elif p < 0 or p > 100:
                        impossible_prev += 1
                        errors.append(f"Impossible prevalence {p} for breed condition row")

        if invalid_breeds:
            warnings.append(f"{invalid_breeds} breed_condition rows reference unknown breeds")
        if missing_prev:
            warnings.append(f"{missing_prev} breed_condition rows missing prevalence")

        return {
            "invalid_breeds": invalid_breeds,
            "missing_prevalence": missing_prev,
            "impossible_prevalence": impossible_prev,
            "breed_count": len(breed_ids),
        }

    def _validate_ingredients(self, errors: list[str], warnings: list[str]) -> dict[str, Any]:
        ci = self.platform.condition_ingredients()
        neg_dose = 0
        bad_range = 0
        missing_mech = 0
        bad_bio = 0

        if not ci.empty:
            dose_cols = [c for c in ci.columns if "dose" in c.lower() and "unit" not in c.lower()]
            min_c = next((c for c in ci.columns if "min" in c.lower() and "dose" in c.lower()), None)
            max_c = next((c for c in ci.columns if "max" in c.lower() and "dose" in c.lower()), None)
            for _, row in ci.iterrows():
                for dc in dose_cols:
                    v = _safe_float(row.get(dc))
                    if v is not None and v < 0:
                        neg_dose += 1
                        errors.append(f"Negative dose in {dc}: {v}")
                if min_c and max_c:
                    mn, mx = _safe_float(row.get(min_c)), _safe_float(row.get(max_c))
                    if mn is not None and mx is not None and mx < mn:
                        bad_range += 1
                        errors.append(f"max dose < min dose: {mx} < {mn}")
                bio = _safe_float(row.get("bioavailability") or row.get("bioavailability_pct"))
                if bio is not None and (bio < 0 or bio > 100):
                    bad_bio += 1
                    errors.append(f"Invalid bioavailability: {bio}")

        ie = getattr(self.platform, "ingredient_evidence", lambda: pd.DataFrame())()
        if hasattr(self.platform, "table"):
            try:
                ie = self.platform.table("ingredient_evidence") if callable(getattr(self.platform, "table", None)) else ie
            except Exception:
                pass
        # Prefer repository helpers when present
        for name in ("ingredient_mechanisms", "ingredient_evidence"):
            fn = getattr(self.platform, name, None)
            if callable(fn):
                try:
                    df = fn()
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        if "mechanism" in df.columns or "Mechanism" in df.columns:
                            mech_col = "mechanism" if "mechanism" in df.columns else "Mechanism"
                            missing_mech += int((df[mech_col].astype(str).str.strip() == "").sum())
                except Exception:
                    continue

        if neg_dose:
            warnings.append(f"{neg_dose} negative dose values")
        if bad_range:
            warnings.append(f"{bad_range} dose ranges with max < min")
        if missing_mech:
            warnings.append(f"{missing_mech} ingredient rows missing mechanism")

        return {
            "negative_dose": neg_dose,
            "max_lt_min": bad_range,
            "missing_mechanisms": missing_mech,
            "invalid_bioavailability": bad_bio,
        }

    def _validate_products(self, errors: list[str], warnings: list[str]) -> dict[str, Any]:
        products = self.platform.products if hasattr(self.platform, "products") else pd.DataFrame()
        if callable(products):
            products = products()
        components = (
            self.platform.product_components()
            if hasattr(self.platform, "product_components")
            else pd.DataFrame()
        )
        missing_ing = 0
        bad_serving = 0
        missing_comp = 0

        if not products.empty:
            pid_col = next((c for c in ("product_id", "Product_ID", "sku", "id") if c in products.columns), None)
            if pid_col and not components.empty:
                cpid = next((c for c in ("product_id", "Product_ID", "sku") if c in components.columns), None)
                if cpid:
                    with_comp = set(components[cpid].astype(str))
                    for pid in products[pid_col].astype(str):
                        if pid not in with_comp:
                            missing_comp += 1
            for col in ("serving_size", "Serving_Size", "serve_g"):
                if col in products.columns:
                    for _, row in products.iterrows():
                        v = _safe_float(row.get(col))
                        if v is not None and v <= 0:
                            bad_serving += 1
                            errors.append(f"Impossible serving size: {v}")

        if not components.empty:
            ing_col = next((c for c in ("ingredient", "Ingredient", "ingredient_id") if c in components.columns), None)
            if ing_col:
                missing_ing = int((components[ing_col].astype(str).str.strip() == "").sum())

        if missing_comp:
            warnings.append(f"{missing_comp} products missing composition rows")
        if missing_ing:
            warnings.append(f"{missing_ing} product component rows missing ingredient")

        return {
            "missing_ingredients": missing_ing,
            "impossible_serving": bad_serving,
            "missing_composition": missing_comp,
            "product_count": 0 if products.empty else len(products),
        }

    def _validate_graph(self, errors: list[str], warnings: list[str]) -> dict[str, Any]:
        builder = KnowledgeGraphBuilder(self.platform)
        graph = builder.build()

        # Isolated nodes (degree 0)
        degree: dict[str, int] = defaultdict(int)
        for e in graph.edges:
            degree[e.source] += 1
            degree[e.target] += 1
        isolated = [nid for nid in graph.nodes if degree[nid] == 0]
        if isolated:
            warnings.append(f"{len(isolated)} isolated graph nodes")

        # Circular references (simple DFS cycle detect on directed edges)
        adj: dict[str, list[str]] = defaultdict(list)
        for e in graph.edges:
            adj[e.source].append(e.target)

        visiting: set[str] = set()
        visited: set[str] = set()
        cycles = 0

        def dfs(u: str, stack: list[str]) -> None:
            nonlocal cycles
            visiting.add(u)
            stack.append(u)
            for v in adj[u]:
                if v in visiting:
                    cycles += 1
                    if cycles <= 5:
                        # Knowledge graphs often contain intentional cycles; treat as warning.
                        warnings.append(f"Circular reference involving {u} -> {v}")
                elif v not in visited:
                    dfs(v, stack)
            stack.pop()
            visiting.discard(u)
            visited.add(u)

        for nid in list(graph.nodes.keys())[:500]:  # bound work
            if nid not in visited:
                dfs(nid, [])

        # Duplicate edges
        edge_keys = [(e.source, e.target, e.relation) for e in graph.edges]
        dup_edges = sum(1 for _, c in Counter(edge_keys).items() if c > 1)
        if dup_edges:
            warnings.append(f"{dup_edges} duplicate graph edges")

        # Conditions without path to paper
        conditions = [n for n in graph.by_type("condition")]
        missing_paths = 0
        for c in conditions:
            outs = [e for e in graph.edges if e.source == c.id]
            if not outs:
                missing_paths += 1
        if missing_paths:
            warnings.append(f"{missing_paths} conditions missing outbound evidence paths")

        return {
            "isolated_nodes": len(isolated),
            "circular_references": cycles,
            "duplicate_edges": dup_edges,
            "conditions_missing_paths": missing_paths,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
        }


def write_validation_report(result: dict[str, Any], out_path: Path | None = None) -> Path:
    out_path = out_path or (ROOT / "governance" / "validation" / "SCIENCE_VALIDATION_REPORT.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Science Validation Report",
        "",
        f"Generated: `{result.get('generated_at')}`",
        f"Status: **{'PASS' if result.get('ok') else 'FAIL'}**",
        "",
        f"- Errors: {len(result.get('errors') or [])}",
        f"- Warnings: {len(result.get('warnings') or [])}",
        "",
        "## Errors",
        "",
    ]
    errs = result.get("errors") or []
    if not errs:
        lines.append("_None_")
    else:
        for e in errs[:100]:
            lines.append(f"- {e}")
    lines += ["", "## Warnings", ""]
    warns = result.get("warnings") or []
    if not warns:
        lines.append("_None_")
    else:
        for w in warns[:150]:
            lines.append(f"- {w}")
    lines += ["", "## Sections", ""]
    for name, sec in (result.get("sections") or {}).items():
        if name == "base":
            continue
        lines.append(f"### {name}")
        lines.append("")
        if isinstance(sec, dict):
            for k, v in sec.items():
                lines.append(f"- `{k}`: {v}")
        lines.append("")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # Also JSON sidecar
    import json

    (out_path.with_suffix(".json")).write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    return out_path
