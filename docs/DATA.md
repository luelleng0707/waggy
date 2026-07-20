# Data

Scientific archive, manifest, and ownership rules for `data/` **as it runs today**.

**Normalization planning pack (no migration yet):**

| Doc | Role |
|-----|------|
| [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md) | Target architecture |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Every current column |
| [DATA_CONSUMERS.md](DATA_CONSUMERS.md) | Blast-radius matrix |
| [DATA_RELATIONSHIPS.md](DATA_RELATIONSHIPS.md) | ER diagrams |
| [DATA_DUPLICATION_REPORT.md](DATA_DUPLICATION_REPORT.md) | Duplicate responsibilities |
| [DATA_NORMALIZATION.md](DATA_NORMALIZATION.md) | 3NF table specs |
| [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md) | Ordered migration plan |
| [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md) | Prior column-level audit |

**Rule:** CSVs hold facts an intern can verify against literature or manufacturer documentation. Algorithms, weights, ladders, and heuristics live in Python.

---

## Philosophy

| Belongs in CSV | Belongs in Python |
|----------------|-------------------|
| Breed traits, prevalence | Optimizer weights |
| Nutrient densities (literature) | Confidence ladders |
| Ingredient evidence / mechanisms | Scoring coefficients |
| Feeding / protocol dose rules | Display labels / nutrient catalogs |
| Product composition & pricing facts | String normalization / aliases heuristics |
| True synonyms (breed / ingredient) | Package penalties, fallback heuristics |
| Climate / trait matrices | Goal ↔ condition UX maps |

**Intern test:** “Can I cite a paper or manufacturer sheet for this row?”  
If no → code or delete.  
Formatting (`EPA+DHA` vs `epa_dha`) → resolver code, not alias rows.

`data/` is **not** a configuration folder for the optimizer.

---

## Runtime model

```text
data/manifest.yaml  (version 2.1.0)
        │
        ▼
app.data.loader → DataPlatform (in-memory pandas)
        │
        ▼
DataRepository  → stages / assemblers
```

- Default provider is CSV on disk. There is no Supabase/Postgres query path in app code today.  
- Repository loads, validates, caches, hot-reloads, hashes — **no clinical math**.  
- Engines must use repository accessors, not hard-coded file paths.  
- Archive CSVs under `archive/data/` are historical and not loaded.

---

## Folder layout

```text
data/
  manifest.yaml
  breed_analysis/
    1_biological_traits/      BREEDS, aliases, mixed matrices, …
    2_evolutionary_profiles/  environmental matrices, trait purposes, …
    3_management_considerations/
    4_preventative_interventions/
    5_scientific_nutrition/   priorities, evidence, mechanisms, nutrient estimates, aliases
  preventative_ingredients/   parallel condition/ingredient tables (review for duplication)
  product_portfolio/          catalog, pricing, components, packages, tiers
```

Manifest declares every live table. Unmanifested files (e.g. some staple/treat sheets) are not part of the runtime contract until listed.

---

## What lives where (current)

### Scientific / commercial CSVs (keep)

Breeds & aliases · mixed-breed matrices · trait explanations & contribution weights · environmental matrices · condition prevalence tables · trait interactions / benefits · activity & grooming defs · condition ingredients · ingredient evidence / mechanisms · natural food sources · nutrient priorities · clinical evidence base · ingredient aliases · **ingredient nutrient estimates** · condition protocols · product catalog / pricing / components / package tiers / external supplements.

### Python (intentional — not CSV)

| Constant / map | Location |
|----------------|----------|
| `CATEGORY_WEIGHTS` | `app/inference/config.py` |
| `SCORE_WEIGHTS` | package optimizer / config |
| `NUTRIENT_CATALOG` | config (display labels) |
| `INGREDIENT_ORDER_PERCENTS` | config (F2 heuristic) |
| `GROOMER_MAP` | config |
| Wellness / goal maps | `wellness_map.py`, `condition_lookup.py` |
| Confidence ladder | `confidence.py` |

There is **no** `data/inference/` module. Algorithmic micro-CSVs were removed; do not reintroduce weights/ladders/goal maps as CSV.

---

## Lookup chains

Typical joins (names simplified):

```text
breed name
  → BREED_ALIASES → BREEDS
  → mixed matrices (if secondary)
  → trait fields → TRAIT_INTERACTIONS / TRAIT_BENEFITS / ENVIRONMENTAL_MATRICES
  → BREED_CONDITIONS / trait condition tables
  → CONDITION_INGREDIENTS / NUTRIENT_PRIORITIES
  → INGREDIENT_EVIDENCE / MECHANISMS / ALIASES
  → PRODUCT_* composition + pricing
  → PACKAGE_* / tiers + coverage matrix
```

Primary keys and foreign keys are declared in `manifest.yaml`. Trust the manifest over ad-hoc path assumptions.

---

## Ingredient resolution

1. Original string  
2. Normalize (Python resolver)  
3. Alias match (`INGREDIENT_ALIASES.csv` — true synonyms only)  
4. Canonical key  
5. Optional taxonomy / category / parent on estimates or aliases  
6. Mechanisms + evidence rows  
7. Product match / coverage  

Alias failures should be explained in debug as failed match — not invented rows.

---

## Domains

| Domain | Churn | Owner |
|--------|-------|-------|
| Clinical reference (prevalence, evidence, traits) | Slow | PPIE science |
| Commercial catalog (SKU, price, stock) | High | Wagtopia ops via product CSVs / future provider |
| Customer dog profiles | High | Wagtopia SoR only — PPIE does not persist dogs |

Future SQL / Wagtopia / lab providers should implement the same repository-facing accessors. Lab columns stay additive and degrade gracefully (usually bump data version only).

---

## Evidence & validation stewardship

- Never fabricate citations, PMIDs, or benchmarks.  
- Evidence levels: `high` | `moderate` | `emerging` | `guideline` | `pending`.  
- Validation modules expose a benchmark or explicit `unavailable` + reason.  
- Production UI must not show raw CSV filenames (debug console may).

---

## Review / known duplication

| Item | Note |
|------|------|
| `preventative_ingredients/*` vs `5_scientific_nutrition/*` | Parallel tables — merge later if redundant |
| `STAPLE_FOOD` / `TREATS` | Confirm need vs catalog; manifest before relying |
| `TRAIT_CONTRIBUTION_WEIGHTS` vs code `CATEGORY_WEIGHTS` | Different concepts — keep both |

---

## Intern / ops workflow

1. Edit or add rows only for verifiable science or catalog facts.  
2. Update `manifest.yaml` when adding a table.  
3. Run load/validate (app startup or tests).  
4. Check Validation Console CSV Lookups / Repository Browser under debug.  
5. If a change alters ranking or targets, run golden/parity — that is an algorithm+data event; bump versions per [API.md](API.md).

---

## Related

- [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) · [FORMULAS.md](FORMULAS.md) · [DEBUGGING.md](DEBUGGING.md)
