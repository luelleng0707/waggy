# Identity mapping (Ω12)

These CSVs are **alias → canonical ID** tables.

They are **not** scientific fact tables. They must not contain prevalence, risk, treatment, or product efficacy.

Breed, condition, and product `canonical_id` values must already exist in:

- `warehouse/biology/breeds.csv`
- `warehouse/biology/conditions.csv`
- `warehouse/commercial/product_master.csv`

Sex IDs are the existing engine tokens `male` / `female`.

Observation IDs in `observation_aliases.csv` are Ω12 mapping vocabulary only. They are **not** warehouse biology trait facts (`coat_type` / Double Coat) and must not be treated as scientific evidence.

Do not invent breed, condition, or product IDs here.
