# Data Architecture Review (Column-Level)

**Status:** Architecture redesign proposal — not a migration, not a refactor  
**Scope:** Every CSV under `data/` (live tree), every column, every consumer  
**Date:** 2026-07-21  
**Manifest:** `data/manifest.yaml` v2.1.0 — **45 declared tables**  
**On disk (live):** **47 CSVs** (45 manifested + `STAPLE_FOOD.csv` + `TREATS.csv` unmanifested)  
**Archive:** `archive/data/**` excluded from redesign targets (historical only)

This document is the single source of truth for the data-layer redesign. Implementation comes later.

---

## 0. Verdict

| Metric | Today | Target |
|--------|-------|--------|
| Live CSVs | 47 | **~16–18** |
| Manifest tables | 45 | **~16–18** |
| Parallel ingredient homes | 2 folders (sci + prev) | **1** |
| Trait prevalence files | 9 isomorphic CSVs | **1** |
| Alias / defaults CSVs | 3 | **0** (Python) |
| Loaded but unused tables | 4 | **0** |

**Philosophy (non-negotiable):**

| Home | Contents |
|------|----------|
| **CSV** | Facts an intern can verify in literature, guidelines, breed standards, or manufacturer specs |
| **Python** | Algorithms, weights, ladders, resolvers, aliases, display labels, heuristics, thresholds |

---

## 1. Complete file inventory

Legend: **Sci** = scientific archive · **Clin** = clinical evidence · **Prod** = commercial · **Ref** = citation · **Parse** = parser · **Algo** = algorithm · **Der** = derived · **Unused** = loaded, no runtime consumer

| # | CSV | Folder | Rows | Cols | PK | Scientific? | Can run without? | Recommendation |
|---|-----|--------|------|------|-----|-------------|------------------|----------------|
| 1 | `BREEDS.csv` | `1_biological_traits` | 48 | 10 | `breed` | Yes | No | **KEEP** |
| 2 | `BREED_ALIASES.csv` | `1_biological_traits` | 4 | 2 | `alias` | No (parser) | Soft | **MOVE → Python** |
| 3 | `MIXED_BREED_MATRIX.csv` | `1_biological_traits` | 5 | 7 | breed_a,breed_b,condition | Yes if curated | Soft | **KEEP** (rename) |
| 4 | `MIXED_BREED_INTERACTIONS.csv` | `1_biological_traits` | 10 | 7 | trait_a,trait_b,condition | Dup of trait_interactions | **Yes (unused)** | **MERGE/DELETE** |
| 5 | `TRAIT_PURPOSES.csv` | `2_evolutionary_profiles` | 5 | 7 | category,value | Mixed (copy + cite) | Soft | **MERGE** → trait science |
| 6 | `ENVIRONMENTAL_MATRICES.csv` | `2_evolutionary_profiles` | 6 | 10 | multi | Partial | Soft | **KEEP/MERGE** |
| 7 | `TRAIT_ATTRIBUTE_EXPLANATIONS.csv` | `2_evolutionary_profiles` | 10 | 10 | category,value | Mixed | Soft | **MERGE** |
| 8 | `TRAIT_CONTRIBUTION_WEIGHTS.csv` | `3_management` | 7 | 8 | cat,value,condition | Borderline | Soft | **REVIEW → Python or KEEP** |
| 9 | `CLINICAL_RISK_TIMELINE.csv` | `3_management` | 6 | 7 | stage,trait,condition | Clin narrative | Soft | **KEEP** |
| 10 | `BREED_CONDITIONS.csv` | `3_management` | 16 | 10 | breed,condition | Yes | No | **KEEP** (rename prevalence) |
| 11–19 | `SIZE/BODYTYPE/COATTYPE/ENERGY/SKULLTYPE/CLIMATE/FUNCTIONGROUP/WEAKNESSGROUP/LIFESPAN_CONDITIONS.csv` | `3_management` | 10×9 | 10 | trait,condition | Yes | No | **MERGE → TRAIT_PREVALENCE** |
| 20 | `TRAIT_INTERACTIONS.csv` | `3_management` | 10 | 7 | a,b,condition | Yes | Soft | **KEEP** (+ benefits) |
| 21 | `TRAIT_BENEFITS.csv` | `4_preventative` | 10 | 6 | a,b,condition | Yes | Soft | **MERGE** → interactions |
| 22 | `CONDITION_ACTIVITIES.csv` | `4_preventative` | 10 | 7 | condition,activity | Yes | Soft | **KEEP/MERGE** care |
| 23 | `ACTIVITY_EVIDENCE.csv` | `4_preventative` | 10 | 5 | activity_name | Ref | **Yes (unused)** | **MERGE → EVIDENCE** |
| 24 | `ACTIVITY_PRESCRIPTION_RULES.csv` | `4_preventative` | 4 | 15 | energy,size,body,age | Clin protocol | Soft | **KEEP** |
| 25 | `GROOMING_OBSERVATION_DEFS.csv` | `4_preventative` | 10 | 8 | observation_key | Clin criteria | Soft | **KEEP** (trim display) |
| 26 | `CONDITION_INGREDIENTS.csv` (sci) | `5_scientific_nutrition` | 12 | 9 | condition,ingredient | Yes | No | **MERGE** nutrition home |
| 27 | `INGREDIENT_EVIDENCE.csv` (sci) | `5_scientific_nutrition` | 10 | 9 | ingredient,source | Ref | Soft | **KEEP** (single) |
| 28 | `INGREDIENT_MECHANISMS.csv` | `5_scientific_nutrition` | 8 | 7 | nutrient,ingredient,product | Mixed (product FK!) | Soft | **SPLIT/MERGE** |
| 29 | `NATURAL_FOOD_SOURCES.csv` | `5_scientific_nutrition` | 15 | 5 | ingredient,food | Yes | Soft | **MERGE → INGREDIENTS** |
| 30 | `NUTRIENT_PRIORITIES.csv` | `5_scientific_nutrition` | 5 | 9 | condition,nutrient | Yes | Soft | **MERGE → CONDITION_NUTRIENTS** |
| 31 | `CLINICAL_EVIDENCE_BASE.csv` | `5_scientific_nutrition` | 7 | 10 | evidence_id | Ref | Soft | **KEEP** as EVIDENCE hub |
| 32 | `INGREDIENT_ALIASES.csv` | `5_scientific_nutrition` | 6 | 4 | canonical,alias | Parser | Soft | **MOVE → Python** |
| 33 | `INGREDIENT_NUTRIENT_ESTIMATES.csv` | `5_scientific_nutrition` | 8 | 12 | ingredient,nutrient | Yes | Soft (opt-in) | **MERGE → INGREDIENTS** |
| 34 | `CONDITION_INGREDIENTS.csv` (prev) | `preventative_ingredients` | 12 | 8 | condition,ingredient | Dup of sci | Soft | **DELETE** after merge |
| 35 | `INGREDIENT_EVIDENCE.csv` (prev) | `preventative_ingredients` | 10 | 5 | ingredient,source | Dup | Soft | **DELETE** after merge |
| 36 | `CONDITION_PROTOCOLS.csv` | `preventative_ingredients` | 12 | 10 | condition,ingredient | Dup / unused | **Yes (unused)** | **MERGE or DELETE** |
| 37 | `PRODUCT_CATALOG.csv` | `product_portfolio` | 16 | 16 | product_id | Prod | No | **KEEP** |
| 38 | `PRODUCT_PRICING.csv` | `product_portfolio` | 16 | 4 | product_id | Prod | No | **KEEP** (or merge catalog) |
| 39 | `PRODUCT_COMPONENTS.csv` | `product_portfolio` | 59 | 7 | product,type,name | Prod | No | **KEEP** |
| 40 | `PRODUCT_FEEDING_RULES.csv` | `product_portfolio` | 23 | 5 | product,weight band | Prod | Soft | **KEEP** |
| 41 | `EXT_SUPPLEMENTS.csv` | `product_portfolio` | 0 | 6 | product_id | Prod | Soft | **MERGE** extensions |
| 42 | `EXT_TREATS_BAKERY.csv` | `product_portfolio` | 12 | 9 | product_id | Prod | Soft | **MERGE** extensions |
| 43 | `PRODUCT_FUNCTIONS.csv` | `product_portfolio` | 10 | 3 | product,function | Prod + algo conf | Soft | **KEEP** (drop conf→Python) |
| 44 | `PACKAGE_TIERS.csv` | `product_portfolio` | 3 | 5 | tier_id | Prod/policy | Soft | **KEEP** |
| 45 | `PRODUCT_DEFAULTS.csv` | `product_portfolio` | 5 | 2 | key | Algo/fallback | **Yes (unused)** | **MOVE → Python** |
| 46 | `STAPLE_FOOD.csv` | `product_portfolio` | 4 | 17 | product_id | Prod | Soft | **MERGE** extensions (**unmanifested**) |
| 47 | `TREATS.csv` | `product_portfolio` | 12 | 8 | product_id | Prod | Soft | **MERGE** extensions (**unmanifested**) |

### Modules / consumers (summary)

| Domain | Backend consumers | Frontend |
|--------|-------------------|----------|
| Breeds / traits / prevalence | `biological`, `health_risk`, `epidemiology`, `calculation_trace` | Via analyze / assess only |
| Narrative / timeline / evidence | `report_generator`, `clinical_report_builder` | Demo report |
| Nutrition / ingredients | `nutrition`, `ingredient_engine`, `response_assembler`, `optimization`, `package_optimizer` | Via payloads |
| Products | `package_optimizer`, `package_detail`, `bundle_engine`, `api` store/catalog | Demo shop/store |
| Aliases | `DataPlatform` indexes → `normalize_breed_name`, `ingredient_alias_groups` | None |
| Unused accessors | `mixed_breed_interactions`, `activity_evidence`, `condition_protocols`, `product_defaults` | — |

---

## 2. Column inventory (every column)

Ownership codes: **S** scientific · **C** clinical · **P** product · **R** reference · **X** parser · **A** algorithm · **D** derived · **U** UI/display · **M** meta (debug filename)

### 2.1 `BREEDS.csv`

| Column | Type | Meaning | Example | Own | Intern edit? | Used by |
|--------|------|---------|---------|-----|--------------|---------|
| `breed` | str | Canonical breed name | Labrador Retriever | S | Yes | biological, health_risk, API breeds |
| `size` | enum | Size class | Large | S | Yes | traits, activity rules, risk |
| `body_type` | enum | Build | Athletic | S | Yes | same |
| `coat_type` | enum | Coat | Double | S | Yes | same |
| `energy` | enum | Energy band | High | S | Yes | same |
| `weakness_group` | enum | Predisposition group | Orthopedic | S/C | Yes | risk traits |
| `skull_type` | enum | Skull morphology | Mesocephalic | S | Yes | risk traits |
| `climate` | enum | Ancestral climate | Temperate | S | Yes | risk traits |
| `lifespan` | enum/band | Lifespan class | 10-12 | S | Yes | risk traits |
| `function_group` | enum | Historical function | Sporting | S | Yes | risk traits |

**Dup note:** trait values also appear as keys in nine `*_CONDITIONS` files — that is by design (join), not column duplication inside BREEDS.

---

### 2.2 `BREED_ALIASES.csv` → **Python**

| Column | Own | Verdict |
|--------|-----|---------|
| `alias` | X | MOVE — resolver dictionary |
| `canonical_breed` | X | MOVE — maps to `BREEDS.breed` |

Intern does not “verify” aliases in papers; they are spelling convenience.

---

### 2.3 `MIXED_BREED_MATRIX.csv`

| Column | Own | Used | Verdict |
|--------|-----|------|---------|
| `breed_a`, `breed_b` | S | health_risk, epidemiology | KEEP |
| `condition` | C | same | KEEP |
| `factor` | S/A | same | KEEP if literature-backed interaction factor; else Python |
| `source_name`, `source_quote`, `source_url` | R | sparse | KEEP with factor |

---

### 2.4 `MIXED_BREED_INTERACTIONS.csv` — **UNUSED**

| Column | Own | Verdict |
|--------|-----|---------|
| `trait_a`, `trait_b`, `condition`, `interaction`, `factor`, `reason`, `source` | S/C | Schema clones `TRAIT_INTERACTIONS`. **MERGE into TRAIT_INTERACTIONS or DELETE.** |

---

### 2.5 Trait narrative trio

#### `TRAIT_PURPOSES.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `trait_category`, `trait_value` | S | KEEP as keys |
| `biological_purpose` | S/C | KEEP |
| `advantage_summary` | U/C | KEEP if clinical; trim marketing tone |
| `source_*` | R | KEEP |

#### `TRAIT_ATTRIBUTE_EXPLANATIONS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `trait_category`, `trait_value` | S | MERGE with purposes (1 row per trait) |
| `card_title` | U | **MOVE → Layer B / Python** or drop |
| `explanation` | C/U | KEEP clinical prose |
| `related_conditions` | D/C | Prefer join to prevalence; else KEEP curated list |
| `evidence_level` | R/A | KEEP as reference enum if guideline-backed |
| `evidence_id` | R | KEEP FK → evidence hub |
| `source_csv` | M | **DELETE** — debug meta, not science |
| `source_name`, `source_url` | R | KEEP |

#### `ENVIRONMENTAL_MATRICES.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `trait_category`, `trait_value` | S | KEEP |
| `trait` | X/D | **DELETE** — duplicate of `trait_value` |
| `climate_context`, `dimension` | S | KEEP |
| `compatibility_score` | A/S | If scored heuristically → **Python**; if from published matrix → KEEP |
| `management_note` | C | KEEP |
| `source_*` | R | KEEP |

---

### 2.6 Nine isomorphic `*_CONDITIONS.csv` → one `TRAIT_PREVALENCE`

Shared schema (each file):

| Column | Own | Used | Verdict |
|--------|-----|------|---------|
| trait key (`size` / `body_type` / …) | S | health_risk, epidemiology | Become `trait_category` + `trait_value` |
| `condition` | C | same | KEEP |
| `prevalence` | S | same | KEEP (0–1 fraction) |
| `sample_population`, `sample_size` | R | report / evidence | KEEP |
| `source_name`, `source_quote`, `source_url`, `year` | R | same | KEEP |
| `confidence_level` | R | report | KEEP as evidence strength of the **study**, not algorithm confidence |

**Duplicate responsibility:** nine files, identical columns, only trait dimension differs. Code already unions them in `trait_condition_tables()`.

---

### 2.7 `BREED_CONDITIONS.csv`

Same citation columns as trait prevalence; grain is `breed × condition`. **KEEP** as `BREED_PREVALENCE` (do not fold into trait table — different grain).

---

### 2.8 Interactions / benefits / contribution

#### `TRAIT_INTERACTIONS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `trait_a`, `trait_b`, `condition` | S/C | KEEP |
| `interaction` | S | KEEP (`synergy` / `neutral` / …) |
| `factor` | S | KEEP if published interaction factor |
| `reason`, `source` | R/C | KEEP (`source` is weak — prefer `source_name`/`url`) |

#### `TRAIT_BENEFITS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `trait_a`, `trait_b`, `condition` | S/C | **MERGE** into interactions with `effect=increase|decrease` or signed factor |
| `reduction_factor` | S | Same as interaction factor with opposite semantics |
| `reason`, `source` | R | KEEP |

#### `TRAIT_CONTRIBUTION_WEIGHTS.csv`

| Column | Own | Intern verify? | Verdict |
|--------|-----|----------------|---------|
| `risk_delta` | A/S | Only if from published risk ratio | **If algorithmic Δ for UI tree → Python**; if published RR → KEEP |
| `unit` | M | — | KEEP with delta |
| `source_csv` | M | No | **DELETE** |
| `evidence_id`, `mechanism_note` | R/C | Yes | KEEP when scientific |

**Critical:** this is **not** the same as Python `CATEGORY_WEIGHTS` (optimizer/category scoring). Do not conflate.

---

### 2.9 Timeline / activities / grooming

#### `CLINICAL_RISK_TIMELINE.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `age_stage`, `trait_or_breed`, `condition` | C | KEEP |
| `risk_level` | C | KEEP (ordinal clinical) |
| `monitoring`, `prevention` | C | KEEP |
| `evidence_id` | R | KEEP |

#### `CONDITION_ACTIVITIES.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `condition`, `activity_name` | C | KEEP |
| `frequency`, `duration_minutes` | C | KEEP |
| `source_*` | R | KEEP |

#### `ACTIVITY_EVIDENCE.csv` — unused

Merge citations into evidence hub or into `CONDITION_ACTIVITIES` rows.

#### `ACTIVITY_PRESCRIPTION_RULES.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `energy`, `size`, `body_type`, `age_stage` | S keys | KEEP |
| `daily_km`, `weekly_km`, walk mins | C | KEEP if guideline-backed |
| `mental_enrichment`, `swimming`, `fetch`, `training` | C/U | KEEP protocol fields |
| `recovery_note` | C | KEEP |
| `source_name`, `source_url` | R | KEEP |

#### `GROOMING_OBSERVATION_DEFS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `observation_key` | C | KEEP |
| `label` | U | Prefer Python / Layer B |
| `normal_criteria`, `monitor_criteria`, `attention_criteria` | C | KEEP |
| `severity_scale` | C/A | KEEP if clinical scale |
| `recommendation_template` | U | Layer B |
| `source_csv` | M | **DELETE** |

---

### 2.10 Nutrition — parallel homes (biggest duplication)

#### Sci `CONDITION_INGREDIENTS` ≈ Prev `CONDITION_INGREDIENTS` ≈ `CONDITION_PROTOCOLS` ≈ overlap with `NUTRIENT_PRIORITIES`

| Column | Own | Dup? | Verdict |
|--------|-----|------|---------|
| `condition` | C | Yes across 4 files | One home |
| `ingredient_name` / `nutrient_name` | S | Naming split | One column: `nutrient_or_ingredient` + `kind` |
| `recommended_daily_dose` / `target_dose` | S | Yes | One: `daily_target` |
| `dose_unit` / `target_unit` | S | Yes | One: `unit` |
| `priority_rank` | A/C | Yes | If guideline order → KEEP; if optimizer preference → **Python** |
| `evidence_type` | R | protocols | KEEP optional |
| `source_*`, `year` | R | Yes | KEEP |
| `supports_joint/skin/gut`, `anti_inflammatory` | S flags | sci evidence only | Belong on ingredient master or evidence |

**Intern problem today:** “Where do I edit Hip Dysplasia → Glucosamine dose?” Answer is ambiguous (sci vs prev vs protocols vs priorities). **This alone justifies redesign.**

#### `INGREDIENT_EVIDENCE` (sci + prev)

| Column | Own | Verdict |
|--------|-----|---------|
| `ingredient_name` | S | Single file |
| `source_*`, `year` | R | KEEP |
| `supports_*` flags | S | Prefer mechanisms/taxonomy on INGREDIENTS |

#### `INGREDIENT_MECHANISMS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `nutrient_name`, `ingredient_name` | S | → INGREDIENTS or MECHANISMS child |
| `source_product_id` | P | **Wrong home** — product composition belongs in PRODUCT_COMPONENTS |
| `amount_per_serving`, `unit` | P/S | If product-specific → components; if food density → estimates |
| `mechanism_summary` | S | KEEP on ingredient |
| `evidence_level` | R | KEEP |

#### `NATURAL_FOOD_SOURCES.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `ingredient_name`, `food_source` | S | MERGE → ingredient food sources |
| `amount_per_100g`, `unit` | S | Same as nutrient estimates grain |
| `bioavailability_notes` | S | KEEP |

#### `INGREDIENT_NUTRIENT_ESTIMATES.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `ingredient`, `canonical_ingredient` | X/S | One canonical key; drop duplicate label col |
| `nutrient`, `amount_per_100g`, `unit` | S | KEEP |
| `confidence` | A/R | Study confidence OK; ladder → Python |
| `source`, `is_estimated`, `notes` | R/S | KEEP |
| `category`, `parent`, `property_tags` | S/X | Taxonomy on ingredient master |

#### `INGREDIENT_ALIASES.csv` → **Python**

| Column | Own | Verdict |
|--------|-----|---------|
| `canonical_key`, `alias_key` | X | resolver |
| `category`, `parent_key` | S/X | If true taxonomy → INGREDIENTS; else Python |

#### `CLINICAL_EVIDENCE_BASE.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `evidence_id` | R | Hub PK |
| `domain`, `condition`, `nutrient_or_activity`, `mechanism` | C/S | KEEP |
| `evidence_level`, `source_*`, `year` | R | KEEP |

---

### 2.11 Products

#### `PRODUCT_CATALOG.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `product_id`, `brand`, `category`, `subcategory`, `product_name`, `status` | P | KEEP |
| `image_url`, `purchase_url`, `description`, `short_description` | P/U | KEEP (commerce) |
| `featured`, `tags`, `display_order`, `inventory_status`, `rating`, `review_count` | P/U/A | Commerce OK; ratings not clinical |

#### `PRODUCT_PRICING.csv` — KEEP (high churn)

`list_price_rmb`, `package_units`, `unit_label`

#### `PRODUCT_COMPONENTS.csv` — KEEP

`component_type`, `component_name`, `value`, `unit`, `evidence_level`, `notes`

#### `PRODUCT_FEEDING_RULES.csv` — KEEP

Weight-banded manufacturer feeding amounts.

#### `PRODUCT_FUNCTIONS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `function` | P/C | KEEP (claimed clinical function) |
| `confidence` | A | **MOVE → Python** or drop |

#### `PACKAGE_TIERS.csv`

| Column | Own | Verdict |
|--------|-----|---------|
| `tier_id`, `title`, `staple_product_id`, `sort_order` | P | KEEP |
| `yearly_discount_factor` | A/P | Commercial policy — OK in product ops CSV **or** Python constants |

#### `PRODUCT_DEFAULTS.csv` — unused → **Python**

#### Extensions: `EXT_*`, `STAPLE_FOOD`, `TREATS`

Overlapping product_id attributes (storage, shelf life, macros, treat type). **MERGE → `PRODUCT_ATTRIBUTES.csv`** (EAV or typed columns by `attribute_group`).

---

## 3. Ownership analysis (column → one category)

| Ownership | Examples in today’s data | Action |
|-----------|--------------------------|--------|
| Scientific | prevalence, amount_per_100g, breed traits, mechanisms | Stay CSV |
| Clinical | conditions, monitoring, grooming criteria, dose targets with cites | Stay CSV |
| Product | SKU, price, feeding chart, components | Stay CSV |
| Reference | PMID/URL/quote/year/sample_size | Stay CSV (normalize column names) |
| Parser | aliases, duplicate `trait` vs `trait_value`, `source_csv` | **Python / delete** |
| Algorithm | `PRODUCT_FUNCTIONS.confidence`, package discount if heuristic, contribution Δ if not published, priority_rank if optimizer | **Python** |
| Derived | related_conditions lists that only mirror prevalence joins | Prefer compute |

---

## 4. Duplication analysis

### 4.1 Duplicate tables (same responsibility)

| Group | Files | Resolution |
|-------|-------|------------|
| Trait prevalence | 9 × `*_CONDITIONS` | **1 × `TRAIT_PREVALENCE.csv`** |
| Condition → nutrient dose | sci CI, prev CI, protocols, nutrient_priorities | **1 × `CONDITION_NUTRIENTS.csv`** |
| Ingredient evidence | sci + prev | **1 × `INGREDIENT_EVIDENCE.csv`** |
| Trait×trait factors | `TRAIT_INTERACTIONS`, `TRAIT_BENEFITS`, unused `MIXED_BREED_INTERACTIONS` | **1 × `TRAIT_INTERACTIONS.csv`** |
| Product extras | EXT_*, STAPLE, TREATS | **1 × `PRODUCT_ATTRIBUTES.csv`** |
| Trait copy | PURPOSES + EXPLANATIONS | **1 × `TRAIT_PROFILES.csv`** |

### 4.2 Duplicate / near-duplicate columns

| Pattern | Columns | Resolution |
|---------|---------|------------|
| Ingredient identity | `ingredient`, `ingredient_name`, `canonical_ingredient`, `canonical_key`, `nutrient_name` | One `ingredient_key` + optional `display_name` (display in Python) |
| Dose | `recommended_daily_dose`, `target_dose`, `target_daily_dose` | `daily_target` |
| Unit | `dose_unit`, `target_unit`, `unit` | `unit` |
| Trait identity | `trait`, `trait_value` | `trait_value` only |
| Evidence strength | `confidence`, `confidence_level`, `evidence_level` | `evidence_level` for studies; algorithm confidence only in Python |
| Meta path | `source_csv` | Delete |
| Rank | `priority_rank`, `sort_order`, `display_order` | Keep only if domain-appropriate; else Python |

### 4.3 Duplicate paths in code

```text
condition → nutrient targets
  ├─ nutrient_priorities          (preferred in assembler)
  ├─ condition_ingredients (sci∪prev)
  └─ condition_protocols          (unused accessor)
```

Target: **one lookup**.

---

## 5. Relationship diagram (current vs target)

### Current (simplified)

```text
BREEDS ──aliases──► (parser)
   │
   ├─► BREED_CONDITIONS ─────────────────────────────┐
   │                                                  │
   └─► trait attrs ─► 9× *_CONDITIONS ───────────────┼─► RISK / EPI
                      TRAIT_INTERACTIONS / BENEFITS ─┤
                      MIXED_BREED_MATRIX ────────────┘

TRAIT_PURPOSES / EXPLANATIONS / ENV / CONTRIBUTION / TIMELINE / EVIDENCE_BASE
   └─► report builders (parallel to risk path)

CONDITION_INGREDIENTS (sci) ─┐
CONDITION_INGREDIENTS (prev)─┼─► nutrition / ingredients / packages
NUTRIENT_PRIORITIES ─────────┤
CONDITION_PROTOCOLS (unused)─┘
INGREDIENT_* / NATURAL_FOOD / ALIASES / ESTIMATES

PRODUCTS ─► PRICING / COMPONENTS / FEEDING / FUNCTIONS / EXT_* / TIERS / DEFAULTS
```

### Target

```text
breeds/BREEDS
breeds/BREED_PREVALENCE ──────────────┐
traits/TRAIT_PREVALENCE ──────────────┼─► RISK (fewest joins)
traits/TRAIT_INTERACTIONS ────────────┤
breeds/MIXED_BREED_FACTORS ───────────┘

traits/TRAIT_PROFILES
traits/ENVIRONMENT
clinical/EVIDENCE ◄── evidence_id FKs
clinical/RISK_TIMELINE
care/ACTIVITIES
care/GROOMING

nutrition/CONDITION_NUTRIENTS
nutrition/INGREDIENTS  (densities, mechanisms, food sources, taxonomy)
nutrition/INGREDIENT_EVIDENCE

products/PRODUCTS (+ pricing columns or PRICING child)
products/PRODUCT_COMPONENTS
products/PRODUCT_FEEDING
products/PRODUCT_ATTRIBUTES
products/PRODUCT_FUNCTIONS
products/PACKAGE_TIERS

Python: resolvers (breed/ingredient aliases), defaults, SCORE_WEIGHTS, CONF ladder, display labels
```

**Remove:** circular science↔product FKs inside `INGREDIENT_MECHANISMS.source_product_id` (product amounts live under products).

---

## 6. Retrieval analysis (backend)

| Stage | Today lookups | Target |
|-------|---------------|--------|
| Breed resolve | breeds + aliases CSV | breeds + **Python alias map** |
| Trait risk | 9 condition tables + breed_conditions + interactions + benefits + mixed matrix | **4 tables**: breed prevalence, trait prevalence, interactions, mixed factors |
| Nutrition targets | priorities ∪ sci∪prev ingredients (± protocols) | **1 table** CONDITION_NUTRIENTS |
| Ingredient match | aliases CSV + components + evidence×2 | Python aliases + INGREDIENTS + 1 evidence |
| Packages | catalog, pricing, components, feeding, functions, tiers, ext×N | catalog(+price), components, feeding, attributes, functions, tiers |
| Reports | purposes, explanations, env, contribution, timeline, evidence | profiles, env, timeline, evidence (+ optional contribution) |

**Loader impact:** fewer tables → smaller `manifest.yaml`, simpler `trait_condition_tables()`, delete sci/prev merge logic.

---

## 7. Intern workflow analysis

| Intern task | Today | Target |
|-------------|-------|--------|
| Add breed trait facts | `BREEDS.csv` | Same |
| Add breed disease prevalence + paper | `BREED_CONDITIONS.csv` | `BREED_PREVALENCE.csv` |
| Add size→condition prevalence | `SIZE_CONDITIONS.csv` (must know which of 9) | `TRAIT_PREVALENCE.csv` (`trait_category=size`) |
| Add Glucosamine dose for Hip Dysplasia | sci CI **or** prev CI **or** protocols **or** priorities | **`CONDITION_NUTRIENTS.csv` only** |
| Add ingredient paper | sci **or** prev evidence | `INGREDIENT_EVIDENCE.csv` |
| Add nutrient density | estimates CSV | `INGREDIENTS` densities section / child rows |
| Add spelling alias | aliases CSV | **Tell eng to add Python alias** (or controlled alias file under `app/`, not science archive) |
| Add SKU / price | product CSVs | Same product folder |
| Change optimizer weight | (wrongly) might hunt CSV | **`app/inference/config.py` / optimizer only** |

**Success test:** every scientific edit has exactly one filename answer.

---

## 8. Resolver / parser analysis

| Asset | Role | Decision |
|-------|------|----------|
| `BREED_ALIASES.csv` | String normalize | **Python** `BREED_ALIASES` dict (or code-owned YAML under `app/`, not `data/`) |
| `INGREDIENT_ALIASES.csv` | String normalize | **Python** resolver |
| `source_csv` columns | Trace breadcrumb | Delete; debug uses table names from manifest |
| `card_title`, grooming `label`, templates | Display | Layer B / Python |
| Duplicate `trait` column | Loader convenience | Delete |

True synonyms that are **scientific nomenclature** (INN vs common nutrient name) may remain as rows on `INGREDIENTS` (`synonym` child) **only if** curated as nomenclature — still better in Python if purely matching.

---

## 9. Formula / numeric column analysis

| Column | Keep in CSV? | Why |
|--------|--------------|-----|
| `prevalence` | Yes | Published rate |
| `factor` / `reduction_factor` | Yes if cited interaction | Else Python |
| `risk_delta` | Only if published effect size | Else Python |
| `compatibility_score` | Only if published matrix | Else Python |
| `priority_rank` | Only if guideline ordering | Else Python |
| `confidence` on estimates | Study/quality label OK | Ladder → Python |
| `PRODUCT_FUNCTIONS.confidence` | No | Algorithm |
| `yearly_discount_factor` | Commercial OK | Not clinical science |
| `list_price_rmb`, macros % | Yes | Manufacturer/commerce |
| `amount_per_100g` | Yes | Nutrition tables |

---

## 10. Merge matrix (every live CSV)

| Current CSV | Action | Destination |
|-------------|--------|-------------|
| `BREEDS.csv` | **KEEP** | `breeds/BREEDS.csv` |
| `BREED_ALIASES.csv` | **MOVE TO PYTHON** | `app/inference/resolver.py` (or `app/data/aliases.py`) |
| `MIXED_BREED_MATRIX.csv` | **RENAME** | `breeds/MIXED_BREED_FACTORS.csv` |
| `MIXED_BREED_INTERACTIONS.csv` | **MERGE/DELETE** | `traits/TRAIT_INTERACTIONS.csv` (or delete if empty unique) |
| `TRAIT_PURPOSES.csv` | **MERGE** | `traits/TRAIT_PROFILES.csv` |
| `TRAIT_ATTRIBUTE_EXPLANATIONS.csv` | **MERGE** | `traits/TRAIT_PROFILES.csv` |
| `ENVIRONMENTAL_MATRICES.csv` | **KEEP** | `traits/ENVIRONMENT.csv` (drop dup `trait`) |
| `TRAIT_CONTRIBUTION_WEIGHTS.csv` | **SPLIT** | Published deltas → `traits/TRAIT_EFFECT_SIZES.csv`; else Python |
| `CLINICAL_RISK_TIMELINE.csv` | **KEEP** | `clinical/RISK_TIMELINE.csv` |
| `BREED_CONDITIONS.csv` | **RENAME** | `breeds/BREED_PREVALENCE.csv` |
| `SIZE_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `BODYTYPE_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `COATTYPE_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `ENERGY_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `SKULLTYPE_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `CLIMATE_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `FUNCTIONGROUP_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `WEAKNESSGROUP_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `LIFESPAN_CONDITIONS.csv` | **MERGE** | `traits/TRAIT_PREVALENCE.csv` |
| `TRAIT_INTERACTIONS.csv` | **KEEP** | `traits/TRAIT_INTERACTIONS.csv` |
| `TRAIT_BENEFITS.csv` | **MERGE** | `traits/TRAIT_INTERACTIONS.csv` (`effect`/`signed_factor`) |
| `CONDITION_ACTIVITIES.csv` | **MERGE** | `care/ACTIVITIES.csv` |
| `ACTIVITY_EVIDENCE.csv` | **MERGE** | `clinical/EVIDENCE.csv` |
| `ACTIVITY_PRESCRIPTION_RULES.csv` | **MERGE** | `care/ACTIVITIES.csv` (or `care/ACTIVITY_PRESCRIPTIONS.csv` if too wide) |
| `GROOMING_OBSERVATION_DEFS.csv` | **KEEP** | `care/GROOMING.csv` |
| `CONDITION_INGREDIENTS.csv` (sci) | **MERGE** | `nutrition/CONDITION_NUTRIENTS.csv` |
| `CONDITION_INGREDIENTS.csv` (prev) | **DELETE** | after merge into CONDITION_NUTRIENTS |
| `CONDITION_PROTOCOLS.csv` | **MERGE/DELETE** | CONDITION_NUTRIENTS (dedupe) |
| `NUTRIENT_PRIORITIES.csv` | **MERGE** | CONDITION_NUTRIENTS |
| `INGREDIENT_EVIDENCE.csv` (sci) | **KEEP** | `nutrition/INGREDIENT_EVIDENCE.csv` |
| `INGREDIENT_EVIDENCE.csv` (prev) | **DELETE** | after merge |
| `INGREDIENT_MECHANISMS.csv` | **SPLIT** | mechanism text → INGREDIENTS; product amounts → PRODUCT_COMPONENTS |
| `NATURAL_FOOD_SOURCES.csv` | **MERGE** | `nutrition/INGREDIENTS.csv` (food_source rows) |
| `INGREDIENT_NUTRIENT_ESTIMATES.csv` | **MERGE** | INGREDIENTS nutrient density rows |
| `INGREDIENT_ALIASES.csv` | **MOVE TO PYTHON** | resolver |
| `CLINICAL_EVIDENCE_BASE.csv` | **KEEP** | `clinical/EVIDENCE.csv` |
| `PRODUCT_CATALOG.csv` | **KEEP** | `products/PRODUCTS.csv` |
| `PRODUCT_PRICING.csv` | **KEEP** | `products/PRODUCT_PRICING.csv` (or columns on PRODUCTS) |
| `PRODUCT_COMPONENTS.csv` | **KEEP** | `products/PRODUCT_COMPONENTS.csv` |
| `PRODUCT_FEEDING_RULES.csv` | **KEEP** | `products/PRODUCT_FEEDING.csv` |
| `PRODUCT_FUNCTIONS.csv` | **KEEP** | drop `confidence` → Python |
| `PACKAGE_TIERS.csv` | **KEEP** | `products/PACKAGE_TIERS.csv` |
| `PRODUCT_DEFAULTS.csv` | **MOVE TO PYTHON** | defaults dict |
| `EXT_SUPPLEMENTS.csv` | **MERGE** | `products/PRODUCT_ATTRIBUTES.csv` |
| `EXT_TREATS_BAKERY.csv` | **MERGE** | PRODUCT_ATTRIBUTES |
| `STAPLE_FOOD.csv` | **MERGE** | PRODUCT_ATTRIBUTES (+ manifest) |
| `TREATS.csv` | **MERGE** | PRODUCT_ATTRIBUTES |

**Archive:** any leftover after cutover → `archive/data/pre-redesign/`.

---

## 11. Proposed folder structure

```text
data/
  manifest.yaml

  breeds/
    BREEDS.csv
    BREED_PREVALENCE.csv
    MIXED_BREED_FACTORS.csv

  traits/
    TRAIT_PREVALENCE.csv          # trait_category, trait_value, condition, prevalence, citations
    TRAIT_INTERACTIONS.csv        # includes former benefits
    TRAIT_PROFILES.csv            # purpose + clinical explanation
    ENVIRONMENT.csv
    TRAIT_EFFECT_SIZES.csv        # optional; only published deltas

  clinical/
    EVIDENCE.csv                  # evidence_id hub
    RISK_TIMELINE.csv

  care/
    ACTIVITIES.csv                # condition activities + prescriptions (or split if needed)
    GROOMING.csv

  nutrition/
    CONDITION_NUTRIENTS.csv       # one dose home
    INGREDIENTS.csv               # master + densities + mechanisms + food sources
    INGREDIENT_EVIDENCE.csv

  products/
    PRODUCTS.csv
    PRODUCT_PRICING.csv
    PRODUCT_COMPONENTS.csv
    PRODUCT_FEEDING.csv
    PRODUCT_ATTRIBUTES.csv
    PRODUCT_FUNCTIONS.csv
    PACKAGE_TIERS.csv
```

**Gone as folders:** `1_biological_traits` numbering, `preventative_ingredients` parallel tree, numbered “phase” science paths.

**Count:** **18 files** (17 if pricing folded into PRODUCTS; 16 if activity prescriptions stay inside ACTIVITIES only and effect sizes omitted).

---

## 12. CSV reduction estimate

| | Count |
|--|------:|
| Live today | 47 |
| Manifested today | 45 |
| After redesign | **16–18** |
| Move to Python | 3+ (`BREED_ALIASES`, `INGREDIENT_ALIASES`, `PRODUCT_DEFAULTS`, plus display/meta columns) |
| Delete as pure duplicates | ~12–15 (9 trait files →1, prev trio, unused overlaps) |
| Merge into masters | ~15 |

---

## 13. Migration roadmap (when approved)

This review does **not** migrate data. Suggested phases:

### M0 — Freeze rules
- No new algorithmic CSVs.  
- No new parallel ingredient files.  
- New prevalence rows go only into future TRAIT_PREVALENCE shape (even if still split files temporarily).

### M1 — Delete dead weight (low risk)
- Stop loading unused: `mixed_breed_interactions`, `activity_evidence`, `condition_protocols`, `product_defaults` (or wire them intentionally).  
- Manifest `STAPLE_FOOD` / `TREATS` or merge into attributes.  
- Drop `source_csv` / duplicate `trait` columns.

### M2 — Unify nutrition (highest intern value)
- Build `CONDITION_NUTRIENTS` from sci∪prev∪priorities∪protocols (dedupe).  
- Single `INGREDIENT_EVIDENCE`.  
- Delete `preventative_ingredients/` tree.  
- Point `condition_ingredients()` at one table.

### M3 — Unify trait prevalence
- One `TRAIT_PREVALENCE`; rewrite `trait_condition_tables()` to read it.  
- Golden/parity must stay green.

### M4 — Ingredient master
- Merge mechanisms (non-product), natural foods, estimates into `INGREDIENTS`.  
- Move product-tied amounts to `PRODUCT_COMPONENTS`.  
- Aliases → Python.

### M5 — Product attributes + folder rename
- Merge EXT/STAPLE/TREATS.  
- Rename folders to domain layout; update manifest paths only (table names can stay stable initially).

### M6 — Python ownership pass
- Aliases, defaults, function confidence, display titles.  
- Confirm `SCORE_WEIGHTS` / CONF ladder remain code-only.

### M7 — Docs & console
- Rewrite [DATA.md](DATA.md) to match new layout.  
- Validation Console CSV browser follows manifest.

**Parity gate:** each M-step requires `tests/test_agent_pipeline.py`, inference parity, and golden suite as applicable — **no clinical math change** unless explicitly approved.

---

## 14. Success criteria checklist

| Criterion | After redesign |
|-----------|----------------|
| Every scientific fact once | Nutrition + prevalence unifications |
| Algorithms in Python | Aliases/defaults/weights/confidence |
| Parser rules in Python | Alias CSVs removed from `data/` |
| Intern knows which file | One dose file, one prevalence file per grain |
| One domain per CSV | Domain folders above |
| Duplicate columns gone | Canonical naming |
| Duplicate CSVs gone | Merge matrix |
| Fewer retrievals | §6 |
| Smaller loaders | No sci/prev merge, no 9-file trait union |
| Easier maintenance | 16–18 CSVs, clear ownership |

---

## 15. Appendix — Unused / weak tables (act first)

| Table | Status |
|-------|--------|
| `mixed_breed_interactions` | Accessor only |
| `activity_evidence` | Accessor only |
| `condition_protocols` | Accessor only (filename mentioned in report copy) |
| `product_defaults` | Indexed, never read |
| `ingredient_nutrient_estimates` | Opt-in inference only (`enabled=False`) |
| `EXT_SUPPLEMENTS` | 0 data rows |
| `STAPLE_FOOD`, `TREATS` | Unmanifested |

---

## 16. Related living docs

- [DATA.md](DATA.md) — current operating philosophy (update after migration)  
- [FORMULAS.md](FORMULAS.md) — what must stay in Python  
- [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) — consumers  
- [DEBUGGING.md](DEBUGGING.md) — Validation Console / CSV browser  

**Do not implement this redesign without an explicit approval batch.** This file is the architectural decision record.
