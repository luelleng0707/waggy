# OPTIMIZATION_DECISION_ARCHITECTURE

## Conceptual optimization chain

`target intake -> candidate products -> coverage -> absorption -> synergy -> conflict -> calories -> constraints -> harmony -> selection`

## Current state boundary

- **Production-active owner**: app runtime (`app.agent.package_optimizer`, `app.agent.bundle_engine`, related nodes)
- **Parallel fully modeled owner**: `repository/optimization/*` (test/debug architecture path)

## Intended package-level harmony decomposition

Harmony is a **package-level** score, not a single-product rating.

Conceptual relationship:

`BASE HARMONY + COVERAGE + ABSORPTION + SYNERGY - CONFLICT - CALORIE PENALTY - CONSTRAINT PENALTY - INTERFERENCE PENALTY`

No new coefficients are defined in this phase.

## Stage architecture notes

| Stage | Current production status | Parallel repository status |
|---|---|---|
| Target intake planning | PARTIAL | IMPLEMENTED (`TGT-701`) |
| Candidate generation | IMPLEMENTED | IMPLEMENTED (`CND-702`) |
| Coverage scoring | PARTIAL | IMPLEMENTED (`COV-703/704`) |
| Absorption analysis | PARTIAL | IMPLEMENTED (`ABS-705`) |
| Synergy analysis | PARTIAL | IMPLEMENTED (`SYN-706`) |
| Conflict analysis | PARTIAL | IMPLEMENTED (`CON-707`) |
| Calorie penalty | PARTIAL | IMPLEMENTED (`CAL-708/709`) |
| Constraint checks | IMPLEMENTED | IMPLEMENTED (`CST-710`) |
| Harmony score | IMPLEMENTED (package-level) | IMPLEMENTED (`HRM-711`) |
| Selection | IMPLEMENTED | IMPLEMENTED (`OPT-712`) |

## Key constraint

Do not interpret harmony as:

- customer satisfaction score
- product star rating
- direct scientific truth metric

It is a constrained package decision metric over interacting bundle components.
