# Data provider (default: CSV)

This folder is the **default scientific + catalog archive** for PPIE. Wagtopia may replace it with SQL or internal services without changing clinical formulas — see [docs/DATA.md](../docs/DATA.md).

**Philosophy:** rows must be verifiable science or manufacturer/catalog facts. Optimizer weights, confidence ladders, and scoring coefficients live in Python — not here.

## What Wagtopia edits often

| Area | Path |
|------|------|
| Product catalog | `product_portfolio/PRODUCT_CATALOG.csv` |
| Components / lab fields | `product_portfolio/PRODUCT_COMPONENTS.csv` |
| Pricing | `product_portfolio/PRODUCT_PRICING.csv` |
| Feeding rules | `product_portfolio/PRODUCT_FEEDING_RULES.csv` |
| Clinical functions | `product_portfolio/PRODUCT_FUNCTIONS.csv` |
| Package tiers | `product_portfolio/PACKAGE_TIERS.csv` |
| Defaults | `product_portfolio/PRODUCT_DEFAULTS.csv` |

Changing these should **not** require Python formula edits. Bump data version via `manifest.yaml` when shipping dataset changes.

## What clinical stewards curate

Breed matrices, trait tables, condition prevalence, nutrient science, and evidence rows under `breed_analysis/` and `preventative_ingredients/`. Edits are data changes (`data_version`); formula changes remain algorithm-versioned.

## Manifest

`manifest.yaml` declares every table, primary keys, and foreign keys. The repository (`app/data/`) loads, validates, caches, and optionally hot-reloads these files.

## Customer dog profiles

**Not stored here.** Wagtopia persists DogProfiles and passes them to the assess API at runtime.
