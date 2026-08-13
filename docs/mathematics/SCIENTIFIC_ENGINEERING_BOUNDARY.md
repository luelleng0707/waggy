# SCIENTIFIC_ENGINEERING_BOUNDARY

## SCIENTIFIC FACT RETRIEVAL
- Warehouse-backed evidence rows from canonical datasets (`biology.*`, `prevention.*`, `nutrition.*`, `mechanisms.*`, etc.).
- Citation metadata retrieval (`paper_name`, `paper_link`, `scientific_quote`).
- Evidence graph assembly from stored facts.

## SCIENTIFICALLY DERIVED
- Normalization transforms required for prevalence/probability math (percent <-> probability, logit/logistic), when used as mathematical transforms rather than biological claims.
- Observed prevalence arithmetic over observed evidence rows (MAT-1001), noting no sample-size weighting.

## EMPIRICALLY ESTIMATED
- None of MAT-1002..MAT-1008 coefficients are currently linked to explicit empirical estimation pipelines in the warehouse.
- Empirical estimation status is therefore partial and limited to direct observed prevalence inputs.

## ENGINEERING INFERENCE
- MAT-1002 evidence-type weights and bounded strength schedule.
- MAT-1003 Bayesian-style blend semantics without explicit likelihood model.
- MAT-1005 composite confidence coefficients.
- MAT-1006 emerging thresholds.
- MAT-1007 multiplicative priority architecture and agreement floor.
- MAT-1008 uncertainty-factor floor and dispersion proxy formulation.
- Pipeline climate-string matching heuristics and first-breed resolver behavior.

## COMMERCIAL OPTIMIZATION
- Optimization formulas and product bundle scoring are outside MAT-1001..MAT-1008, in `repository/optimization/*`.
- They consume upstream scientific/engineering signals but are a separate commercial optimization layer.

## Communication rule
Engineering assumptions must never be described as peer-reviewed scientific facts in scientific reports.
