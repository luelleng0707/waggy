# Data recovery report

Generated: 2026-09-03 09:15 UTC

This is a **recovery** report, not a scientific reinterpretation. Conflicting or incomplete intern rows were preserved and flagged. Nothing was deleted.

## Totals

- **TOTAL LEGACY DATASETS** (intern `a122a83` CSVs restored to `warehouse/recovery_original/`): 76
- **TOTAL LEGACY ROWS** (those intern CSVs): 896
- **TOTAL POPULATED DATASETS** (inventory STATUS starts with POPULATED): 213
- **TOTAL SCIENTIFIC ROWS** (canonical biology/prevention/reference fact tables after recovery): 871
- **TOTAL ROWS RECOVERED this run** (mapping entries): 719
- **TOTAL ROWS REQUIRING VALIDATION** (`NEEDS_VALIDATION` in mapping): 248
- **TOTAL ROWS WITH MISSING PROVENANCE** (`MISSING_PROVENANCE` in mapping): 471
- **TOTAL CONFLICT ROWS** (`CONFLICT_REQUIRES_VALIDATION` in mapping): 0
- **TOTAL ROWS NOT MAPPABLE**: see migration matrix (runtime policy / empty source / already discarded by prior migration notes, **not deleted**)
- Snapshot papers.csv rows: 199
- Canonical rows with a scientific quote (post-recovery fact tables): 336

## 1. Where the intern data was found

Intern research was **in git**, not lost.

1. **Working-tree canonical warehouse** already contained migrated intern prevalence and trait-condition facts in `warehouse/biology/` and `warehouse/prevention/`. `breeds.csv` was identity-only (9 breeds). `breed_traits.csv` was header-only. Commercial tables were header-only.
2. **Deleted intern trees** at commit `a122a83`: `data/breed_analysis/**` (biological traits, management conditions, scientific nutrition), `data/preventative_ingredients/**`, `data/product_portfolio/**`, `archive/data/legacy-parity-csv/**`.
3. **Deleted snapshot** at commit `d6384a0`: `operations/snapshots/2026.07.20-omega/warehouse/**`, including `reference/papers.csv`.
4. **On-disk leftover**: `legacy/warehouse/draft/authoring_staging/papers.csv` and `ingredient_evidence.csv` — staging/test EPA drafts, not the intern corpus.
5. **Why Health Analysis looked empty**: `app/data/loader.py` treated `warehouse/` as a native science warehouse because `CANONICAL_MANIFEST.json` contains `science_only`. `warehouse/science/` does not exist, so formula views were empty. `warehouse_biology.merge_biology_into` existed but was never called.

Read-only copies now live in `warehouse/recovery_original/`. Original git blobs were not modified.

## 2. How much was recovered

```json
{
  "breeds": {
    "added_breeds": 39,
    "added_traits": 432,
    "intern_breed_rows": 48
  },
  "observed": {
    "intern_rows": 16,
    "already_present": 16,
    "appended": 0
  },
  "traits": {
    "intern_rows": 90,
    "already_present": 90,
    "appended": 0
  },
  "ingredients": {
    "intern_rows": 12,
    "already_present": 12,
    "appended": 0
  },
  "mixed": {
    "intern_rows": 10,
    "already_present": 10,
    "appended": 0
  },
  "papers": {
    "intern_rows": 199,
    "already_present": 0,
    "appended": 199,
    "created": true
  },
  "commercial": {
    "intern_rows": 16,
    "already_present": 0,
    "appended": 16,
    "functions_appended": 10,
    "feeding_appended": 23
  }
}
```

Already-migrated intern Labrador / Golden Retriever prevalence rows in `observed_breed_conditions.csv` were **left in place** (not overwritten). Mapping entries are only for rows appended or newly created this run.

## 3. Canonical tables populated (append-only)

| Canonical table | Role |
|---|---|
| `warehouse/biology/breeds.csv` | Extra intern breed **identities** (no papers stuffed onto the entity) |
| `warehouse/biology/breed_traits.csv` | Intern phenotype columns (`size`, `body_type`, `coat_type`, …) with `MISSING_PROVENANCE` |
| `warehouse/biology/observed_breed_conditions.csv` | Intern `BREED_CONDITIONS.csv` facts not already present |
| `warehouse/biology/trait_condition_associations.csv` | Intern SIZE/BODYTYPE/COAT/ENERGY/… condition tables |
| `warehouse/prevention/condition_ingredients.csv` | Intern condition–ingredient facts not already present |
| `warehouse/biology/mixed_breed_NEEDS_VALIDATION.csv` | Intern mixed-breed interactions still lacking citations |
| `warehouse/reference/papers.csv` | Snapshot paper catalog (identity + intern quote/URL; **not** copied onto `conditions.csv`) |
| `warehouse/commercial/product_master.csv` | Intern product catalog identity |
| `warehouse/commercial/product_functions_NEEDS_VALIDATION.csv` | Intern product functions |
| `warehouse/commercial/product_feeding_guide.csv` | Intern feeding rules |

`conditions.csv` remains identity-only. Evidence stays on relationship/fact tables.

## 4. Which scientific facts remain missing

- Intern `BREEDS.csv` phenotype has **no paper/quote/URL**. Recovered as traits with `MISSING_PROVENANCE` — not turned into fake citations.
- Mixed-breed interaction rows still have no scientific quotes (flagged `MISSING_PROVENANCE` / `needs_validation`).
- Life-stage and size-risk intern notes remain in `*_NEEDS_VALIDATION.csv` without papers.
- `warehouse/science/` still does not exist; runtime now merges biology views instead of inventing a science tree.
- No intern prevalence was estimated. No DEMO_SYNTHETIC_BREED_CARE_MODEL rows were written into the warehouse.

## 5. Which rows need validation

See `warehouse/recovery_original/RECOVERY_MAPPING.csv` (719 rows). Counts: NEEDS_VALIDATION=248, MISSING_PROVENANCE=471, CONFLICT_REQUIRES_VALIDATION=0.

Existing canonical rows already marked `migrated` / `needs_validation` / `active` were not rewritten.

## 6. Files now safe to archive (NOT deleted)

Do **not** delete yet. After review, candidates to *archive in place* (copy, not destroy):

- Git history already holds intern trees; `warehouse/recovery_original/*.zip` is the portable copy.
- `legacy/warehouse/draft/authoring_staging/*` staging EPA drafts (not intern corpus).

Nothing in this list has been removed.

## 7. Files that must remain

- `warehouse/recovery_original/` (entire tree)
- `warehouse/biology/*` including `*_NEEDS_VALIDATION.csv`
- `warehouse/prevention/*`
- `warehouse/reference/papers.csv`
- `warehouse/commercial/*` recovered intern catalog rows
- git commits `a122a83`, `d6384a0` (source of intern/snapshot blobs)

## Migration matrix

| Legacy dataset | Canonical dataset | Rows available | Rows migrated before this run | Rows missing then recovered | Evidence preserved? | Recovery action |
|---|---|---:|---:|---:|---|---|
| intern BREEDS.csv | breeds.csv + breed_traits.csv | 48 | 9 identities, 0 traits | breeds +39; traits +432 | quotes were never on intern BREEDS | append identity; traits MISSING_PROVENANCE |
| intern BREED_CONDITIONS.csv | observed_breed_conditions.csv | 16 | 16 | 0 | yes (source_name/quote/url/year → paper_name/scientific_quote/paper_link/publication_year) | append only if not already present |
| intern *TYPE*_CONDITIONS.csv | trait_condition_associations.csv | 90 | 90 | 0 | yes when intern had citations | append missing; flag conflicts |
| intern CONDITION_INGREDIENTS.csv | prevention/condition_ingredients.csv | 12 | 12 | 0 | yes when intern had citations | append missing |
| intern MIXED_BREED_INTERACTIONS.csv | mixed_breed_NEEDS_VALIDATION.csv | 10 | 10 | 0 | intern had no quotes | keep flagged |
| snapshot papers.csv | reference/papers.csv | 199 | 0 | 199 | yes (title/url/quote/year) | created catalog; not copied onto conditions.csv |
| intern PRODUCT_CATALOG.csv | commercial/product_master.csv | 16 | 0 | 16 | N/A (commercial identity) | fill empty commercial table |
| intern PRODUCT_FUNCTIONS.csv | product_functions_NEEDS_VALIDATION.csv | — | 0 | 10 | N/A | fill empty |
| intern PRODUCT_FEEDING_RULES.csv | product_feeding_guide.csv | — | 0 | 23 | N/A | fill empty |
| intern CLINICAL_EVIDENCE_BASE / ACTIVITY_* / GROOMING_* | not auto-merged into identity tables | preserved in recovery_original | prior migration discarded schedules/recommendations | 0 this run | originals preserved | do not reinterpret into facts until review |
| snapshot papers (prior MIGRATION_REPORT: no paper lookup) | reference/papers.csv now exists | recovered | previously skipped as lookup | recovered this run | yes | catalog restored without stuffing conditions.csv |

## Exact intern scientific records for Labrador Retriever / Golden Retriever

These rows were already in `warehouse/biology/observed_breed_conditions.csv` (intern `BREED_CONDITIONS.csv` migrated earlier). They are the recovered facts that must drive Health Analysis once the loader merges biology views:

| breed | condition | prevalence | paper_name | paper_link | scientific_quote | status |
|---|---|---|---|---|---|---|
| Labrador Retriever | Hip Dysplasia | 0.127 | BMC Genomics | https://pmc.ncbi.nlm.nih.gov/articles/PMC7818755/ | Labrador Retrievers showed consistently elevated hip dysplasia prevalence across multi-breed genetic validation cohorts. | migrated |
| Labrador Retriever | Obesity | 0.185 | Cell Metabolism | https://pmc.ncbi.nlm.nih.gov/articles/PMC4873617/ | A POMC gene deletion was strongly associated with increased weight and obesity prevalence in Labrador Retriever dogs. | migrated |
| Golden Retriever | Hip Dysplasia | 0.149 | Animals | https://pmc.ncbi.nlm.nih.gov/articles/PMC11758603/ | Golden Retrievers had the highest risk of CHD diagnosis among guide dog breeding program cohorts. | migrated |
| Golden Retriever | Atopic Dermatitis | 0.132 | Animals | https://pmc.ncbi.nlm.nih.gov/articles/PMC12030778/ | Golden Retrievers demonstrated elevated atopic dermatitis prevalence linked to environmental allergen seropositivity. | migrated |

## Runtime wiring (so recovered facts are visible)

`load_all_tables` now merges `warehouse/biology` + `warehouse/prevention` into empty native science views. `run_package_search` uses `resolve_care_model(repo, …)` when a repository is passed, so Health Analysis reads intern warehouse rows instead of `DEMO_SYNTHETIC_BREED_CARE_MODEL`. Demo synthetic care remains a labeled fallback only when the warehouse has **no** matching breed-condition rows.

## Phase 10 verification (Labrador Retriever × Golden Retriever)

Runtime now loads intern `observed_breed_conditions.csv` via `merge_biology_into`. `resolve_care_model` returns **warehouse evidence**, not `DEMO_SYNTHETIC_BREED_CARE_MODEL`.

Verified from `DataRepository` + `resolve_care_model(['Labrador Retriever','Golden Retriever'])`:

| Health finding | Recovered intern records that produce it |
|---|---|
| Joint / Hip Dysplasia | Labrador 12.7% — BMC Genomics — PMC7818755 — “Labrador Retrievers showed consistently elevated hip dysplasia prevalence…”; Golden 14.9% — Animals — PMC11758603 — “Golden Retrievers had the highest risk of CHD diagnosis…” |
| Digestive / Obesity | Labrador 18.5% — Cell Metabolism — PMC4873617 — “A POMC gene deletion was strongly associated with increased weight and obesity prevalence…” |
| Skin / Atopic Dermatitis | Golden 13.2% — Animals — PMC12030778 — “Golden Retrievers demonstrated elevated atopic dermatitis prevalence…” |

`warehouse_evidence=True`, `demo_synthetic=False`. Estimated prevalence is **not** computed (intern phenotype has no estimation formula). Incomplete activity rows with empty `condition_id` remain in `condition_activities.csv` as `needs_validation` and still load.

For a breed with no observed warehouse rows, Health Analysis stays on the labeled warehouse-unavailable / demo-ranking-only path. No fabricated health report.

## Stop for review

Repository cleanup and documentation consolidation must wait until this report is reviewed. DATA FIRST. CLEANUP SECOND.

