# PROJECT_STRUCTURE.md

```
app/                 # Runtime API + FormulaGraph + Repository loaders + demo UI
warehouse/
  reference/         # Entities
  science/           # Relationships + facts
  runtime/           # aliases, parameters, units
  repository/        # ScientificRepository
  tools/             # build_science_graph.py only
  current/           # release pointer
tests/
docs/                # ≤10 living docs
scripts/             # minimization / bootstrap helpers
authoring/           # Evidence staging (not clinical math)
curation/
ontology/
science_pipeline/    # Validate / publish science
```

Root also contains demo frontend assets (`index.html`, `*.js`, CSS) and deploy files (`Procfile`, `railway.json`, `requirements.txt`).
