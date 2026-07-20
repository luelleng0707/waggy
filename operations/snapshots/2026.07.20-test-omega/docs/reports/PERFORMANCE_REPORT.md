# Performance Report

Generated: `2026-07-20T21:58:06.499334+00:00`

## Runtime (from benchmark)

- Total: 25.2017s
- Avg API latency: 5040.092 ms
- P95 API latency: 5280.962 ms
- Peak memory: 2.334 MB
- CSV loading: 0.0006s
- Graph traversal: 0.0529s

## Slowest Nodes

- `export`: 4314.137 ms
- `risk`: 242.259 ms
- `epidemiology`: 152.5 ms
- `ingredient`: 41.685 ms
- `nutrition`: 24.94 ms
- `biology`: 15.943 ms
- `product`: 10.987 ms
- `grooming`: 8.29 ms
- `activity`: 4.837 ms
- `breed`: 3.948 ms
- `evidence`: 0.64 ms
- `trace`: 0.159 ms
- `validation`: 0.047 ms
- `package`: 0.046 ms
- `assessment`: 0.04 ms

## Largest Tables

| Table | Rows | Cols |
|---|---:|---:|
| `product_components` | 59 | 9 |
| `breeds` | 48 | 12 |
| `product_feeding_rules` | 23 | 7 |
| `breed_conditions` | 16 | 12 |
| `products` | 16 | 18 |
| `product_pricing` | 16 | 6 |
| `natural_food_sources` | 15 | 7 |
| `condition_ingredients_sci` | 12 | 11 |
| `condition_ingredients_prev` | 12 | 10 |
| `condition_protocols` | 12 | 12 |
| `ext_treats_bakery` | 12 | 11 |
| `mixed_breed_interactions` | 10 | 9 |
| `trait_attribute_explanations` | 10 | 12 |
| `grooming_observation_defs` | 10 | 10 |
| `size_conditions` | 10 | 12 |
| `bodytype_conditions` | 10 | 12 |
| `coattype_conditions` | 10 | 12 |
| `energy_conditions` | 10 | 12 |
| `skulltype_conditions` | 10 | 12 |
| `climate_conditions` | 10 | 12 |
| `functiongroup_conditions` | 10 | 12 |
| `weaknessgroup_conditions` | 10 | 12 |
| `lifespan_conditions` | 10 | 12 |
| `trait_interactions` | 10 | 9 |
| `trait_benefits` | 10 | 8 |

## Cache Efficiency

- DataPlatform loads CSVs once per process into `_tables` (in-memory).
- Warehouse materialize is opt-in via `backend=warehouse`.
- Knowledge graph rebuild is per Validation/Audit invocation unless cached by caller.

