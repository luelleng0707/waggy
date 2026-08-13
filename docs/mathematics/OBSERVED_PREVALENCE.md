# OBSERVED_PREVALENCE

## 1. Formula identity
- Formula ID: `MAT-1001`
- Formula version: `v1.0`
- Formula name: Observed Aggregation
- Status: active
- Owning module: `repository/mathematics/epidemiology.py`
- Python implementation: `ObservedEpidemiologyEngine.evaluate`
- Source lines: `11-66`

## 2. Purpose
Calculates observed condition prevalence from observed evidence edges only.

## 3. Inputs
- `observed_edge_values` | type: float[] | unit: % | range: 0-100 | source: `EvidenceGraph.edges[].observed_value`

## 4. Equation
`ObservedPrevalence = mean(observed_edge_values)`

## 5. Code -> equation mapping
- `values = [canonical_percent(...)]` -> normalize observed values to percent.
- `prevalence = sum(values)/len(values)` -> arithmetic mean.

## 6. Parameter provenance
- No external coefficients consumed.
- PARAMETER_STATUS = ENGINEERING_ASSUMPTION (none).

## 7. ILLUSTRATIVE MATHEMATICAL EXAMPLE
- observed values: `[18, 20, 16]`
- mean: `(18 + 20 + 16) / 3 = 18`
- result: `18%`

## 8. Epidemiological term audit (Ω9.3)

- MAT-1001 output is treated as **observed prevalence percent** derived from evidence rows tagged `observed`.
- The current implementation does not model incidence rates, odds ratios, or time-windowed risk directly.
- In developer/publication language:
  - use "observed prevalence proxy from curated evidence rows",
  - avoid interchangeable use of prevalence/incidence/odds/risk unless separate formulas are introduced.
