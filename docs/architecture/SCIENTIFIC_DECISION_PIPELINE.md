# SCIENTIFIC_DECISION_PIPELINE

This document separates observed science, derived estimates, engineering assumptions, optimization decisions, and presentation values in the current system.

## Pipeline semantics

1. **Breed/profile intake** (`app.api.payload_adapter`, `app.agent.nodes.profile_node`)
2. **Biological trait resolution** (`app.agent.nodes.biology_node`)
3. **Condition risk inference** (`app.agent.nodes.risk_node`)
4. **Evidence attachment** (`app.agent.nodes.evidence_node`, optional `app.science.attach`)
5. **Observed prevalence fields** (from warehouse-backed observed data where available)
6. **Estimated prevalence fields** (derived calculations from runtime formulas)
7. **Agreement/confidence/uncertainty-like outputs** (derived and partially heuristic)
8. **Priority / objective-like fields** (derived planning values)
9. **Mechanism/ingredient/product planning** (engineering + optimization decisions)
10. **Package generation + economics** (optimization and business logic)
11. **Presentation projection** (`app.presentation.adapter`)

## Classification boundary

| Category | Meaning | Current examples |
|---|---|---|
| OBSERVED DATA | Direct dataset observation | observed condition prevalence values, product list prices |
| DERIVED ESTIMATE | Computed from observed + model assumptions | estimated prevalence, priority-like scores |
| ENGINEERING ASSUMPTION | Non-empirical tunable behavior | weighting/heuristic terms in confidence/priority-like and packaging logic |
| OPTIMIZATION DECISION | Candidate ranking and constrained selection | package selection, harmony/composite package scoring |
| PRESENTATION VALUE | Display-projected value in surface-specific schema | customer summary cards, business `NOT AVAILABLE` placeholders, developer trace cards |

## Critical rules

- Observed prevalence is not the same as estimated prevalence.
- Confidence-like fields are derived and not guaranteed to be formal statistical confidence intervals.
- Package-level optimization scores are decision metrics, not direct scientific observations.
- UI values can represent transformed projections and must not be mislabeled as observed epidemiological facts.
