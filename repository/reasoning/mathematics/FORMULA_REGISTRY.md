# Formula Registry (Ω4)

All scientific inference equations are versioned artifacts.

## EST-001 (v1.0.0)
- Equation: `canonical_percentage(x) = x*100 when x<=1 else x`
- Description: Normalize ratio/percent-like prevalence to percentage.
- Units: percent

## EST-002 (v1.0.0)
- Equation: `contribution = canonical_percentage(value) * weight`
- Description: Deterministic contribution from direct evidence values.
- Units: percent

## EST-003 (v1.0.0)
- Equation: `contribution_from_factor = (factor - 1) * baseline_percent`
- Description: Interaction-factor delta against baseline prevalence.
- Units: percent

## EST-004 (v1.0.0)
- Equation: `estimated_prevalence = sum(contributions) / count(contributions)`
- Description: Mean contribution estimate with full traceability.
- Units: percent

## AGR-001 (v1.0.0)
- Equation: `absolute_difference = abs(observed - estimated)`
- Description: Absolute agreement gap.
- Units: percent

## AGR-002 (v1.0.0)
- Equation: `relative_difference = absolute_difference / observed`
- Description: Relative agreement gap ratio.
- Units: ratio

## AGR-003 (v1.0.0)
- Equation: `agreement_percentage = max(0, 100 - relative_difference*100)`
- Description: Agreement percentage from relative difference.
- Units: percent

## SYS-001 (v1.0.0)
- Equation: `system(condition) -> lookup(condition_systems.csv)`
- Description: Body system lookup mapping.
- Units: categorical

## MEC-001 (v1.0.0)
- Equation: `mechanisms(condition) -> lookup(condition_mechanisms.csv)`
- Description: Mechanism lookup mapping.
- Units: categorical
