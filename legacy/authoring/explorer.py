"""6K — Interactive scientific explorer (static HTML + embedded JSON from graph)."""

from __future__ import annotations

from app.core.paths import clinical_root_str, resolve_clinical_root

import json
from pathlib import Path

from app.data.repository import DataPlatform
from app.science.builder import KnowledgeGraphBuilder
from ontology import CONDITION_ONTOLOGY, INGREDIENT_ONTOLOGY, condition_path, ingredient_path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "authoring" / "studio" / "explorer.html"


def build_explorer_payload() -> dict:
    platform = DataPlatform(clinical_root_str(), strict=True)
    graph = KnowledgeGraphBuilder(platform).build()
    breeds = []
    bdf = platform.breeds
    if not bdf.empty:
        col = "breed" if "breed" in bdf.columns else bdf.columns[0]
        breeds = [str(x) for x in bdf[col].dropna().tolist()]

    # Precompute neighborhood for each breed via breed_conditions
    breed_map = {}
    bc = platform.breed_conditions()
    if not bc.empty:
        bcol = next((c for c in bc.columns if "breed" in c.lower()), None)
        ccol = next((c for c in bc.columns if "condition" in c.lower()), None)
        if bcol and ccol:
            for _, row in bc.iterrows():
                b = str(row.get(bcol))
                c = str(row.get(ccol))
                breed_map.setdefault(b, []).append(c)

    conditions = {}
    for n in graph.by_type("condition"):
        papers, ingredients, products = [], [], []
        for e in graph.edges:
            if e.source != n.id and e.target != n.id:
                continue
            other = graph.nodes.get(e.target if e.source == n.id else e.source)
            if not other:
                continue
            if other.type == "paper":
                papers.append(other.label)
            elif other.type == "ingredient":
                ingredients.append(other.label)
            elif other.type == "product":
                products.append(other.label)
        conditions[n.label] = {
            "ontology": condition_path(n.label),
            "papers": sorted(set(papers))[:30],
            "ingredients": sorted(set(ingredients))[:30],
            "products": sorted(set(products))[:30],
            "meta": CONDITION_ONTOLOGY.get(n.label),
        }

    ingredients = {
        n.label: {
            "ontology": ingredient_path(n.label),
            "meta": INGREDIENT_ONTOLOGY.get(n.label),
        }
        for n in graph.by_type("ingredient")
    }

    return {
        "breeds": breeds,
        "breed_conditions": breed_map,
        "conditions": conditions,
        "ingredients": ingredients,
        "summary": {"nodes": len(graph.nodes), "edges": len(graph.edges)},
    }


def write_explorer() -> Path:
    data = build_explorer_payload()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>PPIE Scientific Explorer</title>
<style>
:root {{ --bg:#10161c; --panel:#1a242e; --text:#edf2f7; --muted:#9aafc0; --accent:#6bc4b8; --line:#2a3846; }}
body {{ margin:0; font-family:"Source Sans 3",Segoe UI,sans-serif; background:linear-gradient(160deg,#10161c,#162029); color:var(--text); display:grid; grid-template-columns:280px 1fr; min-height:100vh; }}
aside {{ border-right:1px solid var(--line); padding:1.25rem; overflow:auto; }}
main {{ padding:1.5rem 2rem; }}
h1 {{ font-size:1.35rem; margin:0 0 .5rem; }}
h2 {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; color:var(--accent); }}
input, select {{ width:100%; background:#0f161c; color:var(--text); border:1px solid var(--line); border-radius:8px; padding:.5rem; margin:.35rem 0 1rem; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:1rem; margin-bottom:1rem; }}
ul {{ margin:.3rem 0; padding-left:1.1rem; color:var(--muted); }}
.pill {{ display:inline-block; background:#24343c; color:var(--accent); padding:.15rem .5rem; border-radius:999px; margin:.15rem; font-size:.8rem; }}
pathline {{ display:block; color:var(--muted); font-size:.9rem; margin-bottom:.8rem; }}
</style>
</head>
<body>
<aside>
  <h1>Scientific Explorer</h1>
  <p style="color:var(--muted);font-size:.85rem">Deterministic graph browse — not clinical advice</p>
  <h2>Breed</h2>
  <select id="breed"></select>
  <h2>Condition</h2>
  <select id="condition"></select>
  <h2>Ingredient</h2>
  <select id="ingredient"></select>
</aside>
<main>
  <div class="card" id="view"><p style="color:var(--muted)">Select a breed, condition, or ingredient.</p></div>
</main>
<script>
const DATA = {json.dumps(data)};
const breedSel = document.getElementById('breed');
const condSel = document.getElementById('condition');
const ingSel = document.getElementById('ingredient');
const view = document.getElementById('view');

breedSel.innerHTML = '<option value="">—</option>' + DATA.breeds.map(b => `<option>${{b}}</option>`).join('');
condSel.innerHTML = '<option value="">—</option>' + Object.keys(DATA.conditions).sort().map(c => `<option>${{c}}</option>`).join('');
ingSel.innerHTML = '<option value="">—</option>' + Object.keys(DATA.ingredients).sort().map(c => `<option>${{c}}</option>`).join('');

function showBreed(b) {{
  const conds = DATA.breed_conditions[b] || [];
  view.innerHTML = `<h2>Breed</h2><h1>${{b}}</h1>
    <p>Conditions linked in breed_conditions</p>
    <div>${{conds.map(c => `<span class="pill" data-c="${{c}}">${{c}}</span>`).join('') || '—'}}</div>`;
  view.querySelectorAll('[data-c]').forEach(el => el.onclick = () => {{ condSel.value = el.dataset.c; showCondition(el.dataset.c); }});
}}
function showCondition(c) {{
  const d = DATA.conditions[c] || {{}};
  view.innerHTML = `<h2>Condition</h2><h1>${{c}}</h1>
    <pathline>${{(d.ontology||[]).join(' → ')}}</pathline>
    <div class="card"><h2>Evidence / Papers</h2><ul>${{(d.papers||[]).map(x=>`<li>${{x}}</li>`).join('')||'<li>—</li>'}}</ul></div>
    <div class="card"><h2>Ingredients</h2><div>${{(d.ingredients||[]).map(x=>`<span class="pill">${{x}}</span>`).join('')||'—'}}</div></div>
    <div class="card"><h2>Products</h2><ul>${{(d.products||[]).map(x=>`<li>${{x}}</li>`).join('')||'<li>—</li>'}}</ul></div>`;
}}
function showIngredient(i) {{
  const d = DATA.ingredients[i] || {{}};
  view.innerHTML = `<h2>Ingredient</h2><h1>${{i}}</h1>
    <pathline>${{(d.ontology||[]).join(' → ')}}</pathline>
    <pre style="color:var(--muted);white-space:pre-wrap">${{JSON.stringify(d.meta||{{}},null,2)}}</pre>`;
}}
breedSel.onchange = () => breedSel.value && showBreed(breedSel.value);
condSel.onchange = () => condSel.value && showCondition(condSel.value);
ingSel.onchange = () => ingSel.value && showIngredient(ingSel.value);
</script>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    (OUT.parent / "explorer_data.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return OUT
