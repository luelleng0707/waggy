# TRAIT_AGGREGATION

## 1. Formula identity
- Formula ID: `MAT-1002`
- Formula version: `v1.0`
- Formula name: Trait Aggregation
- Status: active
- Owning module: `repository/mathematics/aggregation.py`
- Python implementation: `TraitAggregationEngine.estimate`
- Source lines: `14-120`

## 2. Purpose
Aggregates trait/environment/interaction evidence into one evidence prevalence using weighted log-odds.

## 3. Inputs
- `edge_prevalence` | float[] | % | 0-100 | source: evidence edges `value_number`
- `evidence_type` | str[] | categorical | known types | source: evidence edges
- `weights` | float[] | ratio | >0 | source: `repository/mathematics/weights.py`

## 4. Equation
`P_evidence = logistic( sum(weight_i * logit(p_i)) / sum(weight_i) )`

## 5. Code -> equation mapping
- `weighted_logits.append(logit(probability) * weight)`
- `aggregated_probability = logistic(sum(weighted_logits) / total_weight)`
- `evidence_percent = probability_to_percent(aggregated_probability)`

## 6. Parameter provenance
- `min_strength=0.20` from `warehouse/formulas/coefficients.csv` (`MAT-1002`, `PS_MAT1002_V1`)
- `max_strength=0.90` same source
- `strength_divisor=10.0` same source

## 7. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- trait inputs: `6%, 5%, 4%`
- weighted logit mean -> `0.055` probability
- `evidence_percent = 5.5%`
