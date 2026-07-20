# Data Architecture V2 (Target)

**Status:** Planning only — **no migration executed**  
**Constraint:** Clinical formulas, inference, optimizer, API payloads, and tests must remain identical until an approved migration batch.  
**Companion:** [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md) (current-state audit)

---

## Purpose

Normalize the scientific archive under `data/` so that:

1. Every scientific fact exists **exactly once**  
2. Every column has **exactly one owner**  
3. Every CSV has **exactly one responsibility**  
4. Every backend lookup has **one authoritative source**  
5. Interns know **where to edit** without guessing  

This is a **data architecture** redesign, not a clinical rewrite.

---

## Philosophy

| Layer | Owns |
|-------|------|
| `data/` | Literature-backed / manufacturer-backed facts |
| Python | Algorithms, resolvers, aliases, display labels, defaults, heuristics |
| Wagtopia | Dog SoR, commerce UX, CRM |

Intern test: *Can I cite a paper, guideline, breed standard, or manufacturer sheet for this row?*  
If no → it does not belong in `data/`.

---

## Current vs target (counts)

| | Current | Target (3NF) |
|--|--------:|-------------:|
| Live CSVs | 47 | **~22–26** (normalized; not minimized for its own sake) |
| Manifest tables | 45 | Same as live |
| Trait prevalence files | 9 | 1 |
| Nutrition dose homes | 4 | 1 |
| Ingredient evidence homes | 2 | 1 |
| Alias / defaults CSVs | 3 | 0 (Python) |

Normalization quality > fewest files. Prefer separate 3NF tables over mega-tables.

---

## Target folder layout

```text
data/
  manifest.yaml

  breeds/
    BREEDS.csv                      # breed identity + trait attributes
    BREED_PREVALENCE.csv            # breed × condition prevalence + evidence_id
    MIXED_BREED_FACTORS.csv         # breed_a × breed_b × condition factor

  traits/
    TRAIT_PREVALENCE.csv            # trait_category × trait_value × condition
    TRAIT_INTERACTIONS.csv          # trait_a × trait_b × condition (± effect)
    TRAIT_PROFILES.csv              # clinical purpose + explanation
    TRAIT_ENVIRONMENT.csv           # climate compatibility notes
    TRAIT_EFFECT_SIZES.csv          # optional published effect sizes only

  clinical/
    EVIDENCE.csv                    # citation hub (evidence_id)
    RISK_TIMELINE.csv
    CONDITIONS.csv                  # optional condition registry (id, name)

  care/
    CONDITION_ACTIVITIES.csv
    ACTIVITY_PRESCRIPTIONS.csv
    GROOMING.csv

  nutrition/
    CONDITION_NUTRIENTS.csv         # condition → daily nutrient targets
    INGREDIENT_MASTER.csv           # identity + taxonomy
    INGREDIENT_NUTRIENTS.csv        # densities per 100g
    INGREDIENT_MECHANISMS.csv       # mechanism text (no product FK)
    INGREDIENT_FOOD_SOURCES.csv
    INGREDIENT_EVIDENCE.csv         # ingredient ↔ evidence_id

  products/
    PRODUCTS.csv                    # commercial identity
    PRODUCT_PRICING.csv
    PRODUCT_COMPONENTS.csv
    PRODUCT_FEEDING.csv
    PRODUCT_FUNCTIONS.csv           # claimed functions (no algo confidence)
    PRODUCT_ATTRIBUTES.csv          # ext/staple/treat attrs
    PACKAGE_TIERS.csv
```

**Removed from `data/`:** `BREED_ALIASES`, `INGREDIENT_ALIASES`, `PRODUCT_DEFAULTS`, `source_csv` columns, numbered phase folders, parallel `preventative_ingredients/`.

---

## Canonical naming

| Concept | Canonical column |
|---------|------------------|
| Ingredient identity | `ingredient_key` |
| Condition identity | `condition_key` (+ optional `condition_label`) |
| Trait value | `trait_category` + `trait_value` |
| Daily dose | `daily_target` |
| Unit | `unit` |
| Citation | `evidence_id` → `EVIDENCE` |
| Product | `product_id` |

Deprecated names (migrate then delete): `ingredient_name`, `canonical_ingredient`, `recommended_daily_dose`, `target_dose`, `dose_unit`, `target_unit`, `trait` (dup of `trait_value`).

---

## Evidence hub

All repeated `source_name` / `source_quote` / `source_url` / `year` / `sample_*` patterns consolidate into:

`clinical/EVIDENCE.csv` keyed by `evidence_id`.

Fact tables store **only** `evidence_id` (and optionally a short local note).

---

## Compatibility strategy

1. Keep **table accessor names** stable in `DataRepository` during cutover (views/adapters).  
2. Or ship **compatibility shims** that union old paths into new shapes.  
3. Golden / parity suites must stay green with **zero clinical delta**.  
4. Validation Console CSV browser follows `manifest.yaml` only.

---

## Document map (this phase)

| Doc | Role |
|-----|------|
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Every current column defined |
| [DATA_CONSUMERS.md](DATA_CONSUMERS.md) | Blast radius matrix |
| [DATA_RELATIONSHIPS.md](DATA_RELATIONSHIPS.md) | ER / joins |
| [DATA_DUPLICATION_REPORT.md](DATA_DUPLICATION_REPORT.md) | Duplicate responsibilities |
| [DATA_NORMALIZATION.md](DATA_NORMALIZATION.md) | 3NF target specs |
| [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md) | Ordered plan + rollback |
| [DATA_ARCHITECTURE_REVIEW.md](DATA_ARCHITECTURE_REVIEW.md) | Prior column-level audit |

Operating rules for the **current** runtime remain in [DATA.md](DATA.md) until migration completes.
