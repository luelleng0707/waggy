# Data Normalization (3NF Target Specs)

**Status:** Spec only — no files moved yet  
**Principles:** One responsibility per table · 3NF where practical · no mega-tables · no parser in `data/`

---

## 1. Global rules

1. **Atomic facts** — one predicate per row.  
2. **No repeating groups** — citations → `EVIDENCE`; not copied columns.  
3. **No transitive dependency** — product amounts do not live under ingredient science.  
4. **Surrogate or natural keys** — prefer stable `*_key` / `*_id` strings already used by the engine.  
5. **Python owns** aliases, defaults, display labels, score weights, confidence ladders.

---

## 2. Evidence hub

### `clinical/EVIDENCE.csv`

| Column | Type | Notes |
|--------|------|-------|
| `evidence_id` | PK | Stable id |
| `title` | str | |
| `authors` | str | nullable |
| `journal` | str | nullable |
| `year` | int | nullable |
| `doi` | str | nullable |
| `pmid` | str | nullable |
| `study_type` | enum | nullable |
| `species` | str | default canine |
| `sample_size` | int | nullable |
| `quality` / `evidence_level` | enum | high/moderate/… |
| `url` | str | |
| `quote` | str | optional canonical excerpt |

Every scientific fact table may include `evidence_id` FK. Drop inline `source_*` after backfill.

---

## 3. Breeds domain

### `BREEDS.csv`
PK: `breed`  
Columns: trait attributes only (`size`, `body_type`, …). No prevalence.

### `BREED_PREVALENCE.csv`
PK: (`breed`, `condition_key`)  
Columns: `prevalence`, `sample_population`, `sample_size`, `evidence_id`  
FK: `breed` → BREEDS

### `MIXED_BREED_FACTORS.csv`
PK: (`breed_a`, `breed_b`, `condition_key`)  
Columns: `factor`, `evidence_id`

**Python:** breed alias map (former `BREED_ALIASES`).

---

## 4. Traits domain

### `TRAIT_PREVALENCE.csv`
PK: (`trait_category`, `trait_value`, `condition_key`)  
Replaces nine `*_CONDITIONS` files.  
Columns: `prevalence`, sample fields, `evidence_id`

### `TRAIT_INTERACTIONS.csv`
PK: (`trait_a`, `trait_b`, `condition_key`, `effect`)  
`effect` ∈ {`increase`,`decrease`} or signed `factor`  
Merges `TRAIT_INTERACTIONS` + `TRAIT_BENEFITS` (+ unused mixed trait file if any unique rows)

### `TRAIT_PROFILES.csv`
PK: (`trait_category`, `trait_value`)  
Merges purposes + explanations.  
Columns: `biological_purpose`, `explanation`, `advantage_summary`, `evidence_id`  
**Drop:** `card_title`, `source_csv`

### `TRAIT_ENVIRONMENT.csv`
PK: (`trait_category`, `trait_value`, `climate_context`, `dimension`)  
**Drop:** duplicate `trait` column.  
`compatibility_score` only if literature-backed; else move to Python.

### `TRAIT_EFFECT_SIZES.csv` (optional)
Published `risk_delta` only — else delete and keep scoring in Python.

---

## 5. Care domain

### `CONDITION_ACTIVITIES.csv`
PK: (`condition_key`, `activity_key`)  
Dose-like fields + `evidence_id`

### `ACTIVITY_PRESCRIPTIONS.csv`
PK: (`energy`, `size`, `body_type`, `age_stage`)  
Protocol numbers + `evidence_id`

### `GROOMING.csv`
PK: `observation_key`  
Clinical criteria columns only.  
**Python/Layer B:** `label`, `recommendation_template`

---

## 6. Nutrition domain (no mega-table)

### `CONDITION_NUTRIENTS.csv`
PK: (`condition_key`, `ingredient_key`)  
Columns: `daily_target`, `unit`, `priority` (only if guideline order), `evidence_id`, `evidence_type`  
Replaces sci/prev CI + protocols + nutrient_priorities (deduped).

### `INGREDIENT_MASTER.csv`
PK: `ingredient_key`  
Columns: `display_name` optional, `category`, `parent_key`, flags (`supports_*` if scientific taxonomy)

### `INGREDIENT_NUTRIENTS.csv`
PK: (`ingredient_key`, `nutrient_key`)  
Columns: `amount_per_100g`, `unit`, `is_estimated`, `evidence_id`, `notes`

### `INGREDIENT_MECHANISMS.csv`
PK: (`ingredient_key`, `mechanism_key`) or (`ingredient_key`, `nutrient_key`)  
Columns: `mechanism_summary`, `evidence_id`  
**Forbidden:** `source_product_id`

### `INGREDIENT_FOOD_SOURCES.csv`
PK: (`ingredient_key`, `food_source`)  
Columns: `amount_per_100g`, `unit`, `bioavailability_notes`, `evidence_id`

### `INGREDIENT_EVIDENCE.csv`
PK: (`ingredient_key`, `evidence_id`)  
Link table only (optional extra flags)

**Python:** ingredient alias resolver (former `INGREDIENT_ALIASES`).

---

## 7. Clinical registry (optional but recommended)

### `CONDITIONS.csv`
PK: `condition_key`  
Columns: `condition_label`, `domain`  
Gives a single vocabulary for joins.

### `RISK_TIMELINE.csv`
PK: (`age_stage`, `subject_key`, `condition_key`)  
Columns: `risk_level`, `monitoring`, `prevention`, `evidence_id`

---

## 8. Products domain

### `PRODUCTS.csv`
Commercial identity + status + media URLs.  
Marketing copy may stay (commerce), not clinical math.

### `PRODUCT_PRICING.csv`
PK: `product_id` — high churn

### `PRODUCT_COMPONENTS.csv`
Composition / lab / active amounts (includes former mechanism product amounts)

### `PRODUCT_FEEDING.csv`
Weight-banded feeding rules

### `PRODUCT_FUNCTIONS.csv`
(`product_id`, `function`) — **no** `confidence` column

### `PRODUCT_ATTRIBUTES.csv`
EAV or typed groups for former EXT/STAPLE/TREATS

### `PACKAGE_TIERS.csv`
Tier config; discount factor is commercial policy (allowed) or Python constant

**Python:** `PRODUCT_DEFAULTS` map

---

## 9. Naming canonicalization checklist

| Old | New |
|-----|-----|
| `ingredient_name` | `ingredient_key` |
| `recommended_daily_dose` / `target_dose` | `daily_target` |
| `dose_unit` / `target_unit` | `unit` |
| `condition` (free text) | `condition_key` (+ label table) |
| `source_name`… on fact rows | `evidence_id` |

---

## 10. What must not be “merged to reduce count”

| Do not collapse | Why |
|-----------------|-----|
| Breed prevalence into trait prevalence | Different grain |
| Product components into ingredient nutrients | Commerce vs science |
| Evidence hub into every fact table | Reintroduces duplication |
| All nutrition into one INGREDIENTS mega-file | Violates 3NF / SRP |

---

## Related

[DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md) · [DATA_MIGRATION_V2.md](DATA_MIGRATION_V2.md) · [DATA_DUPLICATION_REPORT.md](DATA_DUPLICATION_REPORT.md)
