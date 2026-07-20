# Data Duplication Report

**Status:** Responsibility-level duplication analysis (not filename matching)  
**Rule:** One fact → one owner. Parallel files with the same grain are defects.

---

## 1. Responsibility duplication matrix

| Responsibility | Current homes | Grain | Verdict |
|----------------|---------------|-------|---------|
| Trait × condition prevalence | 9 × `*_CONDITIONS.csv` | trait_value × condition | **MERGE → TRAIT_PREVALENCE** |
| Breed × condition prevalence | `BREED_CONDITIONS.csv` | breed × condition | **KEEP separate** (different grain) |
| Trait × trait × condition factor (risk↑) | `TRAIT_INTERACTIONS.csv` | a×b×condition | **KEEP** |
| Trait × trait × condition factor (risk↓) | `TRAIT_BENEFITS.csv` | a×b×condition | **MERGE** into interactions (`effect` / signed factor) |
| Mixed trait interactions | `MIXED_BREED_INTERACTIONS.csv` | a×b×condition | **DELETE/MERGE** (unused; same grain as interactions) |
| Mixed breed factors | `MIXED_BREED_MATRIX.csv` | breed×breed×condition | **KEEP** (breed grain) |
| Trait narrative profile | `TRAIT_PURPOSES` + `TRAIT_ATTRIBUTE_EXPLANATIONS` | category×value | **MERGE → TRAIT_PROFILES** |
| Condition → nutrient daily dose | sci CI + prev CI + `CONDITION_PROTOCOLS` + `NUTRIENT_PRIORITIES` | condition × nutrient | **MERGE → CONDITION_NUTRIENTS** |
| Ingredient citation | sci + prev `INGREDIENT_EVIDENCE` | ingredient × source | **MERGE → one file** |
| Citation metadata | Repeated `source_*` on dozens of tables | paper | **NORMALIZE → EVIDENCE hub** |
| Ingredient density | `INGREDIENT_NUTRIENT_ESTIMATES` + parts of `NATURAL_FOOD_SOURCES` | ingredient × nutrient/food | **SPLIT cleanly** (densities vs foods) |
| Ingredient taxonomy | aliases `category`/`parent` + estimates `category`/`parent` | ingredient | **INGREDIENT_MASTER only** |
| Product extension attrs | `EXT_*` + `STAPLE_FOOD` + `TREATS` | product_id | **MERGE → PRODUCT_ATTRIBUTES** |
| Activity citations | `ACTIVITY_EVIDENCE` (unused) vs inline on activities | activity | **EVIDENCE hub** |
| Defaults / aliases | `PRODUCT_DEFAULTS`, `BREED_ALIASES`, `INGREDIENT_ALIASES` | parser | **Python** |

---

## 2. Column-name duplication

| Synonyms today | Canonical target | Why |
|----------------|------------------|-----|
| `ingredient`, `ingredient_name`, `canonical_ingredient`, `canonical_key`, `nutrient_name` (when same entity) | `ingredient_key` (+ `display_name` in Python if needed) | One identity |
| `condition`, `condition_name` | `condition_key` | One identity |
| `recommended_daily_dose`, `target_dose`, `target_daily_dose` | `daily_target` | One measure |
| `dose_unit`, `target_unit`, `unit` | `unit` | One unit column |
| `trait`, `trait_value` | `trait_value` | Drop duplicate |
| `confidence`, `confidence_level`, `evidence_level` | `evidence_level` on citations; algo confidence in Python | Avoid conflating study quality with model confidence |
| `priority_rank`, `sort_order`, `display_order` | Keep only domain-appropriate; UI order → Python | Mixed semantics |
| `source`, `source_name` | Prefer `evidence_id` | Hub |

---

## 3. Citation duplication

The same paper fields appear on:

- All prevalence tables (`source_name`, `source_quote`, `source_url`, `year`, `sample_*`, `confidence_level`)
- Nutrition / evidence / mechanisms / activities / trait narratives

**Cost:** Interns update one paper in N places; drift is inevitable.

**Fix:** `EVIDENCE.csv` + `evidence_id` FKs only.

---

## 4. Cross-domain pollution

| Pollution | Where | Fix |
|-----------|-------|-----|
| Product ID inside ingredient science | `INGREDIENT_MECHANISMS.source_product_id` | Move amounts to `PRODUCT_COMPONENTS` |
| Algo confidence on product functions | `PRODUCT_FUNCTIONS.confidence` | Python or drop |
| Debug breadcrumb | `source_csv` | Delete |
| Display title in science | `card_title`, grooming `label` | Layer B / Python |
| Unmanifested commercial sheets | `STAPLE_FOOD`, `TREATS` | Manifest or merge attributes |

---

## 5. Loader / path duplication

| Pattern | Today | Target |
|---------|-------|--------|
| `condition_ingredients()` | sci ∪ prev merge (`sci` wins) | Single table |
| `ingredient_evidence()` | sci ∪ prev concat | Single table |
| `trait_condition_tables()` | Union 9 files + inject category | One `TRAIT_PREVALENCE` |
| Alias indexes | CSV → platform index | Python dict / code module |

---

## 6. False duplicates (keep both)

| Pair | Why not duplicate |
|------|-------------------|
| `BREED_CONDITIONS` vs trait `*_CONDITIONS` | Different grain (breed vs trait class) |
| `MIXED_BREED_MATRIX` vs `TRAIT_INTERACTIONS` | Breed pair vs trait pair |
| `PRODUCT_PRICING` vs catalog | High-churn commerce vs identity (may stay split) |
| `TRAIT_CONTRIBUTION_WEIGHTS.risk_delta` vs Python `CATEGORY_WEIGHTS` | Different concepts if literature RR vs scoring weights |

---

## 7. Severity ranking

| Priority | Issue | Intern impact |
|----------|-------|---------------|
| P0 | Four homes for condition→dose | “Where do I edit Glucosamine?” |
| P0 | Nine trait prevalence files | Wrong file risk |
| P1 | Dual ingredient evidence | Citation drift |
| P1 | Repeated citation columns | Paper update hell |
| P2 | Alias CSVs in `data/` | Looks scientific, is not |
| P2 | Unused loaded tables | False confidence |
| P3 | Naming synonyms | Join bugs |

---

## Related

[DATA_NORMALIZATION.md](DATA_NORMALIZATION.md) · [DATA_DICTIONARY.md](DATA_DICTIONARY.md) · [DATA_ARCHITECTURE_V2.md](DATA_ARCHITECTURE_V2.md)
